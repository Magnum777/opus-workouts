"""
Risk Manager V3
Enforces trading limits and risk rules with re-buy cooldown and proper loss tracking
"""

import json
import os
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db.json")
DAILY_LIMIT = 999          # Effectively unlimited — other guardrails handle discipline
MIN_HOLD_HOURS = 1         # Minimum hold time in hours
MAX_POSITION_PCT = 0.40    # Max 40% of portfolio in one position
MAX_OPEN_POSITIONS = 6     # Up to 6 concurrent positions — diversified, not degenerate
MAX_TOTAL_EXPOSURE_PCT = 0.70  # Never have more than 70% of portfolio in positions
STOP_LOSS_PCT = -0.08      # -8% stop loss (gave the 1-pos tightness; let runners breathe)
TRIM_PCT = 99.0            # Disabled — trim never triggers at this level
TRIM_FRACTION = 0.5        # Kept for import compatibility, never used
TAKE_PROFIT_PCT = 0.20     # +20% full take profit — quick flips, small account

# Trailing stop — locks in gains as price rises
TRAILING_ACTIVATE_PCT = 0.12   # Trailing stop activates after +12% profit
TRAILING_DISTANCE_PCT = 0.04   # Trail 4% below the highest price seen
# Once active, the effective stop loss becomes: max(original -8%, highest_price - 5%)
# So if a position goes up 67%, the stop is at ~62% profit — you keep most of the gain.
REBUY_COOLDOWN_HOURS = 48  # 48h cooldown — no rebuying tokens you just sold
MIN_TRADE_VALUE = 1.0      # Trades under $1 don't count for consecutive loss tracking
CONSECUTIVE_LOSS_DECAY_HOURS = 6  # Decay 1 loss every 6h without new losses
COOLDOWN_FILE = os.path.join(os.path.dirname(__file__), "rebuy_cooldowns.json")

# Blocklist — tokens the bot must never buy
BLOCKED_TOKENS = {
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
}

def load_db():
    """Load V2 database"""
    if not os.path.exists(DB_PATH):
        return create_default_db()
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(db):
    """Save V2 database"""
    db["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)
    return db

def create_default_db():
    """Create default V2 database"""
    return {
        "schema_version": "2.0",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "wallet": {"address": "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA", "chain": "solana"},
        "portfolio": {
            "sol_balance": 0.0, "sol_price_usd": 0.0,
            "total_value_usd": 0.0, "positions_count": 0
        },
        "positions": [], "trades": [], "signals": [],
        "risk_metrics": {
            "daily_trade_count": 0,
            "daily_trade_reset": datetime.now(timezone.utc).isoformat()[:10],
            "last_trade_time": None,
            "consecutive_losses": 0
        },
        "performance": {
            "daily_pnl": {}, "win_rate": 0.0, "avg_profit_per_trade": 0.0
        }
    }

# --- Re-buy Cooldown System ---

def load_cooldowns():
    """Load sell cooldowns"""
    if not os.path.exists(COOLDOWN_FILE):
        return {}
    with open(COOLDOWN_FILE, "r") as f:
        return json.load(f)

def save_cooldowns(cooldowns):
    """Save sell cooldowns"""
    with open(COOLDOWN_FILE, "w") as f:
        json.dump(cooldowns, f, indent=2)

def record_sell_cooldown(token, mint):
    """Record that we sold a token, so it can't be re-bought for REBUY_COOLDOWN_HOURS"""
    cooldowns = load_cooldowns()
    cooldowns[mint] = {
        "token": token,
        "sold_at": datetime.now(timezone.utc).isoformat(),
        "cooldown_until": (datetime.now(timezone.utc) + timedelta(hours=REBUY_COOLDOWN_HOURS)).isoformat()
    }
    save_cooldowns(cooldowns)

def is_on_cooldown(token, mint):
    """Check if a token is on re-buy cooldown"""
    cooldowns = load_cooldowns()
    entry = cooldowns.get(mint)
    if not entry:
        return False, 0
    cooldown_until = datetime.fromisoformat(entry["cooldown_until"].replace('Z', '+00:00'))
    if datetime.now(timezone.utc) < cooldown_until:
        remaining = (cooldown_until - datetime.now(timezone.utc)).total_seconds() / 3600
        return True, remaining
    return False, 0

# --- Core Risk Checks ---

def check_trade_allowed(token, action, portfolio_value, current_position_value, mint=""):
    """Check if trade is allowed by risk rules"""
    db = load_db()
    metrics = db.get("risk_metrics", {})
    
    # Check 0: Blocklist (for buys)
    if action == "BUY":
        if token in BLOCKED_TOKENS or mint in BLOCKED_TOKENS.values():
            return False, f"{token} is blocked — no buys allowed"

    # Check 1: Re-buy cooldown (for buys)
    if action == "BUY" and mint:
        on_cd, remaining = is_on_cooldown(token, mint)
        if on_cd:
            return False, f"Re-buy cooldown active ({remaining:.1f}h remaining for {token})"
    
    # Check 1: Daily trade limit
    today = datetime.now(timezone.utc).isoformat()[:10]
    daily_reset = metrics.get("daily_trade_reset", "")
    
    if daily_reset != today:
        metrics["daily_trade_count"] = 0
        metrics["daily_trade_reset"] = today
    
    if metrics["daily_trade_count"] >= DAILY_LIMIT:
        return False, f"Daily trade limit reached ({DAILY_LIMIT})"
    
    # Check 2: Minimum hold time (for sells)
    if action == "SELL":
        position = get_position(token)
        if position:
            opened_at = position.get("opened_at") or position.get("timestamp")
            if opened_at:
                try:
                    opened = datetime.fromisoformat(opened_at.replace('Z', '+00:00'))
                    hold_time = datetime.now(timezone.utc) - opened
                    if hold_time < timedelta(hours=MIN_HOLD_HOURS):
                        hrs = hold_time.total_seconds() / 3600
                        return False, f"Hold time too short ({hrs:.1f}h < {MIN_HOLD_HOURS}h)"
                except:
                    pass  # If we can't parse, don't block the trade
    
    # Check 3: Max position size (for buys)
    if action == "BUY":
        position_size = current_position_value  # passed as proposed size for buys
        if position_size > portfolio_value * MAX_POSITION_PCT:
            return False, f"Position too large (${position_size:.2f} > {MAX_POSITION_PCT*100}% of ${portfolio_value:.2f})"
    
    # Check 4: Consecutive losses with time-based decay
    # Only blocks RE-BUYS of the same token, not all trading
    consecutive_losses = metrics.get("consecutive_losses", 0)
    if consecutive_losses >= 3:
        # Check if enough time has passed to decay the counter
        last_loss_time = metrics.get("last_loss_time")
        if last_loss_time:
            elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(last_loss_time.replace('Z', '+00:00'))).total_seconds() / 3600
            if elapsed >= CONSECUTIVE_LOSS_DECAY_HOURS:
                # Decay 1 loss count
                decay_amount = int(elapsed / CONSECUTIVE_LOSS_DECAY_HOURS)
                metrics["consecutive_losses"] = max(0, consecutive_losses - decay_amount)
                db["risk_metrics"] = metrics
                save_db(db)
                consecutive_losses = metrics["consecutive_losses"]
    
    if action == "BUY" and consecutive_losses >= 3:
        # Check if this is a re-buy of a recently lost token
        # Look up the last 5 closed positions for this token
        recent_closed = [p for p in db.get("positions", [])
                        if p.get("token") == token and p.get("status") == "CLOSED"
                        and p.get("realized_pnl_usd", 0) < 0
                        and p.get("closed_at")]
        if recent_closed:
            # Sort by most recent close
            recent_closed.sort(key=lambda p: p.get("closed_at", ""), reverse=True)
            last_close = recent_closed[0].get("closed_at", "")
            if last_close:
                try:
                    closed = datetime.fromisoformat(last_close.replace('Z', '+00:00'))
                    hours_since = (datetime.now(timezone.utc) - closed).total_seconds() / 3600
                    if hours_since < REBUY_COOLDOWN_HOURS:
                        return False, f"Re-buy blocked - {token} lost ${abs(recent_closed[0].get('realized_pnl_usd', 0)):.2f} {hours_since:.0f}h ago (cooldown {REBUY_COOLDOWN_HOURS}h)"
                except:
                    pass
        # If it's a new token (not a re-buy), allow the trade
        # The consecutive loss counter is informational only for new tokens
    
    # Check 5: Total exposure cap (don't go all-in)
    if action == "BUY":
        open_count = len([p for p in db.get("positions", []) if p.get("status") == "OPEN"])
        if open_count >= MAX_OPEN_POSITIONS:
            return False, f"Max open positions ({MAX_OPEN_POSITIONS}) reached — currently holding {open_count}"
        
        # Also check total exposure cap
        if portfolio_value > 0:
            total_in_positions = sum(
                p.get("current_value_usd", 0) for p in db.get("positions", [])
                if p.get("status") == "OPEN"
            )
            exposure_pct = total_in_positions / portfolio_value
            if exposure_pct >= MAX_TOTAL_EXPOSURE_PCT:
                return False, f"Total exposure cap reached ({exposure_pct*100:.0f}% >= {MAX_TOTAL_EXPOSURE_PCT*100:.0f}%) — need to free up capital first"
    
    return True, "Trade allowed"

def record_trade(token, action, pnl=None, trade_value=0):
    """Record trade for risk tracking"""
    db = load_db()
    metrics = db.get("risk_metrics", {})
    
    # Update daily count
    today = datetime.now(timezone.utc).isoformat()[:10]
    if metrics.get("daily_trade_reset") != today:
        metrics["daily_trade_count"] = 0
        metrics["daily_trade_reset"] = today
    
    metrics["daily_trade_count"] = metrics.get("daily_trade_count", 0) + 1
    metrics["last_trade_time"] = datetime.now(timezone.utc).isoformat()
    
    # Track consecutive losses - ONLY for real trades over MIN_TRADE_VALUE
    if pnl is not None and action == "SELL" and trade_value >= MIN_TRADE_VALUE:
        if pnl < 0:
            metrics["consecutive_losses"] = metrics.get("consecutive_losses", 0) + 1
            metrics["last_loss_time"] = datetime.now(timezone.utc).isoformat()
        else:
            metrics["consecutive_losses"] = 0
            metrics["last_loss_time"] = None
    
    db["risk_metrics"] = metrics
    save_db(db)

def get_position(token):
    """Get position from V2 DB"""
    db = load_db()
    for pos in db["positions"]:
        if pos["token"] == token and pos.get("status") == "OPEN":
            return pos
    return None

def check_stop_loss_take_profit(position):
    """Check if position hit stop loss, take profit, or trailing stop"""
    if not position:
        return None
    
    buy_price = position.get("buy_price_usd", 0)
    current_price = position.get("current_price_usd", 0)
    
    if buy_price <= 0:
        return None
    
    pnl_pct = (current_price - buy_price) / buy_price
    
    # Hard stop loss (always active)
    if pnl_pct <= STOP_LOSS_PCT:
        return "STOP_LOSS", pnl_pct
    
    # Take profit (always active)
    if pnl_pct >= TAKE_PROFIT_PCT:
        return "TAKE_PROFIT", pnl_pct
    
    # Trailing stop check — only if position has enough data
    trailing_high = position.get("trailing_high_price", 0)
    if trailing_high > 0:
        trailing_pnl = (trailing_high - buy_price) / buy_price
        # Only activate trailing stop if we've been above the activation threshold
        if trailing_pnl >= TRAILING_ACTIVATE_PCT:
            trail_stop_price = trailing_high * (1 - TRAILING_DISTANCE_PCT)
            if current_price <= trail_stop_price:
                return "TRAILING_STOP", pnl_pct
    
    return None, pnl_pct


def update_trailing_stop(position, current_price):
    """Update the trailing high watermark for a position.
    Returns True if the high was updated, False otherwise.
    Call this every cycle to track the highest price seen."""
    if not position:
        return False
    
    buy_price = position.get("buy_price_usd", 0)
    if buy_price <= 0 or current_price <= 0:
        return False
    
    trailing_high = position.get("trailing_high_price", 0)
    
    # Initialize trailing high to buy price if not set
    if trailing_high <= 0:
        position["trailing_high_price"] = buy_price
        return True
    
    # Update if we hit a new high
    if current_price > trailing_high:
        position["trailing_high_price"] = current_price
        return True
    
    return False


def get_trailing_stop_info(position):
    """Get human-readable trailing stop status for a position.
    Returns dict with: active, current_stop_price, highest_seen, locked_pnl"""
    if not position:
        return None
    
    buy_price = position.get("buy_price_usd", 0)
    trailing_high = position.get("trailing_high_price", 0)
    current_price = position.get("current_price_usd", 0)
    
    if buy_price <= 0 or trailing_high <= 0:
        return {"active": False, "reason": "no trailing data yet"}
    
    trailing_pnl = (trailing_high - buy_price) / buy_price
    
    if trailing_pnl < TRAILING_ACTIVATE_PCT:
        return {
            "active": False,
            "reason": f"not yet activated (need +{TRAILING_ACTIVATE_PCT*100:.0f}%, currently at +{trailing_pnl*100:.1f}%)",
            "highest_seen": trailing_high,
            "highest_pnl_pct": trailing_pnl * 100
        }
    
    trail_stop_price = trailing_high * (1 - TRAILING_DISTANCE_PCT)
    locked_pnl = (trail_stop_price - buy_price) / buy_price * 100
    distance_to_stop = ((current_price - trail_stop_price) / trail_stop_price * 100) if trail_stop_price > 0 else 0
    
    return {
        "active": True,
        "trail_stop_price": trail_stop_price,
        "highest_seen": trailing_high,
        "highest_pnl_pct": trailing_pnl * 100,
        "locked_pnl_pct": locked_pnl,
        "distance_to_stop_pct": distance_to_stop,
        "current_price": current_price
    }

def get_risk_summary():
    """Get current risk status (auto-decays consecutive losses)"""
    db = load_db()
    metrics = db.get("risk_metrics", {})
    
    # Apply time-based decay to consecutive_losses
    consecutive_losses = metrics.get("consecutive_losses", 0)
    last_loss_time = metrics.get("last_loss_time")
    if consecutive_losses > 0 and last_loss_time:
        elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(last_loss_time.replace('Z', '+00:00'))).total_seconds() / 3600
        if elapsed >= CONSECUTIVE_LOSS_DECAY_HOURS:
            decay_amount = int(elapsed / CONSECUTIVE_LOSS_DECAY_HOURS)
            new_losses = max(0, consecutive_losses - decay_amount)
            if new_losses != consecutive_losses:
                metrics["consecutive_losses"] = new_losses
                db["risk_metrics"] = metrics
                save_db(db)
                consecutive_losses = new_losses
    
    today = datetime.now(timezone.utc).isoformat()[:10]
    daily_count = metrics.get("daily_trade_count", 0) if metrics.get("daily_trade_reset") == today else 0
    
    cooldowns = load_cooldowns()
    active_cooldowns = []
    for mint, entry in list(cooldowns.items()):
        until = datetime.fromisoformat(entry["cooldown_until"].replace('Z', '+00:00'))
        if datetime.now(timezone.utc) < until:
            remaining = (until - datetime.now(timezone.utc)).total_seconds() / 3600
            active_cooldowns.append(f"{entry['token']} ({remaining:.0f}h)")
        else:
            cooldowns.pop(mint, None)
    save_cooldowns(cooldowns)
    
    return {
        "daily_trades_used": daily_count,
        "daily_trades_remaining": DAILY_LIMIT - daily_count,
        "consecutive_losses": metrics.get("consecutive_losses", 0),
        "trading_paused": metrics.get("consecutive_losses", 0) >= 3,
        "cooldowns": active_cooldowns,
        "max_open_positions": MAX_OPEN_POSITIONS,
        "max_exposure_pct": MAX_TOTAL_EXPOSURE_PCT,
        "min_hold_hours": MIN_HOLD_HOURS,
        "stop_loss_pct": STOP_LOSS_PCT,
        "take_profit_pct": TAKE_PROFIT_PCT,
        "trailing_activate_pct": TRAILING_ACTIVATE_PCT,
        "trailing_distance_pct": TRAILING_DISTANCE_PCT,
        "rebuy_cooldown_hours": REBUY_COOLDOWN_HOURS
    }

if __name__ == "__main__":
    summary = get_risk_summary()
    print("Risk Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
