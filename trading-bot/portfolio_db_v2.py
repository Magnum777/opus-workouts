"""
Unified Portfolio Database Module V2
Research-driven, risk-aware, performance-tracked
"""

import json
import os
from datetime import datetime, timezone

DB_PATH = "portfolio.db.json"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDC_MINTS = {"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"}


def is_stablecoin_mint(mint):
    """Check if mint is a known stablecoin"""
    return mint in USDC_MINTS


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
        "wallet": {
            "address": "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA",
            "chain": "solana"
        },
        "portfolio": {
            "sol_balance": 0.0,
            "sol_price_usd": 0.0,
            "usdc_balance": 0.0,
            "total_value_usd": 0.0,
            "positions_count": 0,
            "cost_basis_total": 0.0
        },
        "positions": [],
        "trades": [],
        "signals": [],
        "risk_metrics": {
            "daily_trade_count": 0,
            "daily_trade_reset": datetime.now(timezone.utc).isoformat()[:10],
            "last_trade_time": None,
            "consecutive_losses": 0
        },
        "performance": {
            "daily_pnl": {},
            "win_rate": 0.0,
            "avg_profit_per_trade": 0.0,
            "total_realized_pnl": 0.0,
            "total_unrealized_pnl": 0.0,
            "daily_avg": 0.0,
            "projected_days_to_1000": 999
        },
        "tax_summary": {}
    }

def get_position(token):
    """Get position by token"""
    db = load_db()
    for pos in db["positions"]:
        if pos["token"] == token and pos["status"] == "OPEN":
            return pos
    return None

def add_position(position):
    """Add new position"""
    db = load_db()
    position["opened_at"] = datetime.now(timezone.utc).isoformat()
    db["positions"].append(position)
    db["portfolio"]["positions_count"] = len([p for p in db["positions"] if p["status"] == "OPEN"])
    save_db(db)
    return position

def partial_close_position(token, close_data, remaining_fraction):
    """Sell part of a position, update remaining amount and cost basis.
    remaining_fraction: what fraction of the position stays open (e.g. 0.5 = half stays)"""
    db = load_db()
    for i, pos in enumerate(db["positions"]):
        if pos["token"] == token and pos["status"] == "OPEN":
            # Record trade for the portion sold
            original_amount_raw = pos.get("amount_raw", 0)
            original_cost = pos.get("cost_basis_usd", 0)
            proceeds = close_data.get("close_value_usd", 0)
            
            # PnL on the sold portion
            sold_cost = original_cost * (1 - remaining_fraction)
            sold_pnl = proceeds - sold_cost
            
            pos["amount_raw"] = int(original_amount_raw * remaining_fraction)
            pos["cost_basis_usd"] = original_cost * remaining_fraction
            pos["partial_trims"] = pos.get("partial_trims", 0) + 1
            
            db["positions"][i] = pos
            save_db(db)
            return {
                "pnl_usd": sold_pnl,
                "proceeds": proceeds,
                "remaining_amount": pos["amount_raw"],
                "remaining_cost": pos["cost_basis_usd"]
            }
    return None

def close_position(token, close_data):
    """Close position with realized P&L"""
    db = load_db()
    for i, pos in enumerate(db["positions"]):
        if pos["token"] == token and pos["status"] == "OPEN":
            pos["status"] = "CLOSED"
            pos["closed_at"] = datetime.now(timezone.utc).isoformat()
            pos["close_price_usd"] = close_data.get("close_price_usd", 0)
            pos["close_value_usd"] = close_data.get("close_value_usd", 0)
            
            # Calculate realized P&L
            cost_basis = pos.get("cost_basis_usd", 0)
            proceeds = close_data.get("close_value_usd", 0)
            pos["realized_pnl_usd"] = proceeds - cost_basis
            pos["realized_pnl_pct"] = ((proceeds - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
            
            # Add to performance
            db["performance"]["total_realized_pnl"] = db["performance"].get("total_realized_pnl", 0) + pos["realized_pnl_usd"]
            
            # Update portfolio
            db["portfolio"]["positions_count"] = len([p for p in db["positions"] if p["status"] == "OPEN"])
            
            db["positions"][i] = pos
            save_db(db)
            return pos
    return None

def add_trade(trade_data):
    """Add trade and update performance"""
    db = load_db()
    trade = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **trade_data
    }
    db["trades"].append(trade)
    
    # Update tax summary
    year = trade["timestamp"][:4]
    if year not in db["tax_summary"]:
        db["tax_summary"][year] = {
            "total_trades": 0,
            "realized_pnl": 0.0,
            "fees_paid": 0.0
        }
    
    db["tax_summary"][year]["total_trades"] += 1
    if trade.get("pnl_usd"):
        db["tax_summary"][year]["realized_pnl"] += trade["pnl_usd"]
    
    # Update performance metrics
    update_performance_metrics(db)
    
    save_db(db)
    return trade

def update_performance_metrics(db):
    """Update performance calculations"""
    trades = db.get("trades", [])
    sells = [t for t in trades if t.get("action") == "SELL"]
    
    if sells:
        total_pnl = sum(t.get("pnl_usd", 0) for t in sells)
        wins = len([t for t in sells if t.get("pnl_usd", 0) > 0])
        
        db["performance"]["win_rate"] = (wins / len(sells)) * 100
        db["performance"]["avg_profit_per_trade"] = total_pnl / len(sells)
    
    # Calculate unrealized P&L
    unrealized = sum(p.get("unrealized_pnl_usd", 0) for p in db["positions"] if p["status"] == "OPEN")
    db["performance"]["total_unrealized_pnl"] = unrealized
    
    # Project to $1000
    total_pnl = db["performance"].get("total_realized_pnl", 0) + db["performance"].get("total_unrealized_pnl", 0)
    daily_avg = db["performance"].get("daily_avg", 0)
    
    if daily_avg > 0:
        db["performance"]["projected_days_to_1000"] = (1000 - total_pnl) / daily_avg
    
    return db

def sync_from_blockchain(holdings, sol_balance, sol_price):
    """Sync portfolio from blockchain data"""
    db = load_db()
    db["portfolio"]["sol_balance"] = sol_balance
    db["portfolio"]["sol_price_usd"] = sol_price
    
    total_value = sol_balance * sol_price
    
    # Purge stale positions: tokens with $0 current_value_usd (dusted/closed)
    # that are not found in on-chain holdings with positive balance
    on_chain_with_value = set(h.get("mint", "") for h in holdings if h.get("value_usd", 0) >= 0.01)
    db["positions"] = [
        p for p in db["positions"]
        if p.get("status") != "OPEN"  # keep closed positions
        or p.get("current_value_usd", 0) >= 0.01  # keep if has real value
        or p.get("mint", "") in on_chain_with_value  # keep if actually worth something on-chain
    ]
    
    for holding in holdings:
        token = holding["token"]
        mint = holding.get("mint", "")
        
        # Skip stablecoins - they're cash, not trade positions
        if is_stablecoin_mint(mint):
            # Use the raw amount as USD value (1 USDC = $1)
            usdc_val = holding["amount"]
            db["portfolio"]["usdc_balance"] = usdc_val
            total_value += usdc_val
            print(f"  USDC cash: ${usdc_val:.2f}")
            # Remove any stale position for stablecoin
            db["positions"] = [p for p in db["positions"] if p.get("mint") != mint]
            continue
        
        found = False
        
        # Skip sub-penny dust tokens - not worth tracking or trading
        if holding.get("value_usd", 0) < 0.01:
            print(f"  Skipping dust token: {holding['token']} (${holding['value_usd']:.6f})")
            continue
        
        for i, pos in enumerate(db["positions"]):
            # Match by mint FIRST (stable), fall back to token name (legacy)
            pos_mint = pos.get("mint", "")
            match = False
            if pos_mint and mint and pos_mint == mint:
                match = True
            elif not pos_mint and pos["token"] == token:
                match = True
            if match and pos["status"] == "OPEN":
                pos["current_value_usd"] = holding["value_usd"]
                pos["current_value_sol"] = holding["value_sol"]
                pos["amount_raw"] = holding.get("amount_raw", holding["amount"])
                pos["decimals"] = holding.get("decimals", 6)
                
                # Calculate unrealized P&L
                cost_basis = pos.get("cost_basis_usd", 0)
                current = holding["value_usd"]
                pos["unrealized_pnl_usd"] = current - cost_basis
                pos["unrealized_pnl_pct"] = ((current - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0
                
                db["positions"][i] = pos
                total_value += holding["value_usd"]
                found = True
                break
        
        if not found:
            # New position from blockchain (skip if stablecoin - already handled above)
            new_pos = {
                "token": token,
                "mint": mint,
                "amount_raw": holding.get("amount_raw", holding["amount"]),
                "amount": holding.get("amount", 0),
                "decimals": holding.get("decimals", 6),
                "current_value_usd": holding["value_usd"],
                "current_value_sol": holding["value_sol"],
                "buy_price_usd": holding["value_usd"],
                "buy_price_sol": holding["value_sol"],
                "cost_basis_usd": holding["value_usd"],
                "unrealized_pnl_usd": 0,
                "unrealized_pnl_pct": 0,
                "status": "OPEN"
            }
            db["positions"].append(new_pos)
            total_value += holding["value_usd"]
    
    # Remove stale positions - tokens that are no longer held on-chain
    on_chain_mints = set(h["mint"] for h in holdings)
    db["positions"] = [
        p for p in db["positions"]
        if p.get("status") != "OPEN"
        or p.get("mint", "") in on_chain_mints
        or p.get("token") == "USDC"
    ]
    db["portfolio"]["positions_count"] = len([p for p in db["positions"] if p["status"] == "OPEN"])
    
    db["portfolio"]["total_value_usd"] = total_value
    save_db(db)
    return db

def get_tax_report(year=None):
    """Generate tax report"""
    db = load_db()
    if not year:
        year = datetime.now(timezone.utc).year
    
    return db["tax_summary"].get(str(year), {
        "total_trades": 0,
        "realized_pnl": 0.0,
        "fees_paid": 0.0
    })

if __name__ == "__main__":
    db = load_db()
    print(f"V2 DB loaded: ${db['portfolio']['total_value_usd']:.2f}")
    print(f"Projected days to $1000: {db['performance'].get('projected_days_to_1000', 999):.1f}")
