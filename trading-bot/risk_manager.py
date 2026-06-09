"""
Risk Manager V3
Enforces trading limits and risk rules with re-buy cooldown and proper loss tracking
"""

import json
import os
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db.json")
DAILY_LIMIT = 999        # Effectively unlimited — other guardrails handle discipline
MIN_HOLD_HOURS = 1       # Minimum hold time in hours
MAX_POSITION_PCT = 0.40  # Max 40% of portfolio in one position
MAX_OPEN_POSITIONS = 1   # HARD CAP — only ever hold 1 position at a time
STOP_LOSS_PCT = -0.06    # -6% stop loss (keep tight — limit damage)
TRIM_PCT = 0.12         # +12% partial trim — let rebuild runners breathe
TRIM_FRACTION = 0.5     # Sell half at trim threshold
TAKE_PROFIT_PCT = 0.15   # +15% full take profit (was 8% — too tight for memes)
REBUY_COOLDOWN_HOURS = 48  # 48h cooldown — no rebuying tokens you just sold
MIN_TRADE_VALUE = 1.0    # Trades under $1 don't count for consecutive loss tracking
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
    consecutive_losses = metrics.get("consecutive_losses", 0)
    if consecutive_losses >= 3:
        # Check if enough time has passed to decay the counter
        last_loss_time = metrics.get("last_loss_time")
        if last_loss_time:
            elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(last_loss_time.replace('Z', '+00:00'))).total_seconds() / 3600
            if elapsed >= CONSECUTIVE_LOSS_DECAY_HOURS:
                # Decay 1 loss count, unfreeze if we're at 3
                decay_amount = int(elapsed / CONSECUTIVE_LOSS_DECAY_HOURS)
                metrics["consecutive_losses"] = max(0, consecutive_losses - decay_amount)
                db["risk_metrics"] = metrics
                save_db(db)
                consecutive_losses = metrics["consecutive_losses"]
    
    if action == "BUY" and consecutive_losses >= 3:
        return False, f"Trading paused - {consecutive_losses} consecutive real losses (>$1 each)"
    
    # Check 5: Max open positions
    if action == "BUY":
        open_count = len([p for p in db.get("positions", []) if p.get("status") == "OPEN"])
        if open_count >= MAX_OPEN_POSITIONS:
            return False, f"Max open positions ({MAX_OPEN_POSITIONS}) reached — currently holding {open_count}"
    
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
    """Check if position hit stop loss or take profit"""
    if not position:
        return None
    
    buy_price = position.get("buy_price_usd", 0)
    current_price = position.get("current_price_usd", 0)
    
    if buy_price <= 0:
        return None
    
    pnl_pct = (current_price - buy_price) / buy_price
    
    if pnl_pct <= STOP_LOSS_PCT:
        return "STOP_LOSS", pnl_pct
    if pnl_pct >= TAKE_PROFIT_PCT:
        return "TAKE_PROFIT", pnl_pct
    
    return None, pnl_pct

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
        "min_hold_hours": MIN_HOLD_HOURS,
        "stop_loss_pct": STOP_LOSS_PCT,
        "take_profit_pct": TAKE_PROFIT_PCT,
        "rebuy_cooldown_hours": REBUY_COOLDOWN_HOURS
    }

if __name__ == "__main__":
    summary = get_risk_summary()
    print("Risk Summary:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
