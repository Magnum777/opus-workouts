"""
Unified Portfolio Database Module
Single source of truth for all trading data
"""

import json
import os
from datetime import datetime, timezone

DB_PATH = "trading-bot/portfolio.db.json"
HISTORY_PATH = "trading-bot/trade-history.json"

def load_db():
    """Load central portfolio database"""
    if not os.path.exists(DB_PATH):
        return create_default_db()
    with open(DB_PATH, "r") as f:
        return json.load(f)

def save_db(db):
    """Save central portfolio database"""
    db["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)
    return db

def create_default_db():
    """Create default database structure"""
    return {
        "schema_version": "1.0",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "wallet": {
            "address": "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA",
            "chain": "solana",
            "rpc": "https://mainnet.helius-rpc.com"
        },
        "portfolio": {
            "sol_balance": 0.0,
            "sol_price_usd": 0.0,
            "total_value_usd": 0.0,
            "positions_count": 0
        },
        "positions": [],
        "trades": [],
        "signals": [],
        "tax_summary": {}
    }

def get_position(token):
    """Get position by token symbol"""
    db = load_db()
    for pos in db["positions"]:
        if pos["token"] == token:
            return pos
    return None

def update_position(token, updates):
    """Update position with new data"""
    db = load_db()
    for i, pos in enumerate(db["positions"]):
        if pos["token"] == token:
            db["positions"][i].update(updates)
            save_db(db)
            return db["positions"][i]
    return None

def add_position(position):
    """Add new position"""
    db = load_db()
    position["opened_at"] = datetime.now(timezone.utc).isoformat()
    db["positions"].append(position)
    db["portfolio"]["positions_count"] = len(db["positions"])
    save_db(db)
    return position

def close_position(token, close_data):
    """Close position and calculate P&L"""
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
            
            # Add to trades history
            trade = {
                "timestamp": pos["closed_at"],
                "token": token,
                "action": "SELL",
                "mint": pos.get("mint"),
                "amount_raw": pos.get("amount_raw"),
                "cost_basis_usd": cost_basis,
                "proceeds_usd": proceeds,
                "pnl_usd": pos["realized_pnl_usd"],
                "pnl_pct": pos["realized_pnl_pct"],
                "tx_hash": close_data.get("tx_hash")
            }
            db["trades"].append(trade)
            
            # Update tax summary
            year = pos["closed_at"][:4]
            if year not in db["tax_summary"]:
                db["tax_summary"][year] = {
                    "total_trades": 0,
                    "realized_pnl": 0.0,
                    "fees_paid": 0.0
                }
            db["tax_summary"][year]["total_trades"] += 1
            db["tax_summary"][year]["realized_pnl"] += pos["realized_pnl_usd"]
            
            db["positions"][i] = pos
            db["portfolio"]["positions_count"] = len([p for p in db["positions"] if p["status"] == "OPEN"])
            save_db(db)
            return pos
    return None

def add_trade(trade_data):
    """Add trade to history and update tax records"""
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
    if trade.get("fee_sol"):
        # Approximate fee in USD (rough calc)
        fee_usd = trade["fee_sol"] * db["portfolio"].get("sol_price_usd", 150)
        db["tax_summary"][year]["fees_paid"] += fee_usd
    
    save_db(db)
    return trade

def get_tax_report(year=None):
    """Generate tax report for year"""
    db = load_db()
    if year is None:
        year = str(datetime.now().year)
    
    summary = db["tax_summary"].get(year, {
        "total_trades": 0,
        "realized_pnl": 0.0,
        "fees_paid": 0.0
    })
    
    trades = [t for t in db["trades"] if t["timestamp"][:4] == year]
    
    return {
        "year": year,
        "summary": summary,
        "trades": trades
    }

def update_portfolio_summary(updates):
    """Update portfolio summary values"""
    db = load_db()
    db["portfolio"].update(updates)
    save_db(db)
    return db["portfolio"]

def sync_from_blockchain(holdings, sol_balance, sol_price):
    """Sync positions from actual blockchain data
    
    holdings: list of dicts with keys: token, mint, amount, value_usd, value_sol
    """
    db = load_db()
    db["portfolio"]["sol_balance"] = sol_balance
    db["portfolio"]["sol_price_usd"] = sol_price
    
    # Update positions with current values
    total_value = sol_balance * sol_price
    for holding in holdings:
        token = holding["token"]
        found = False
        for i, pos in enumerate(db["positions"]):
            if pos["token"] == token and pos["status"] == "OPEN":
                pos["current_value_usd"] = holding["value_usd"]
                pos["current_value_sol"] = holding["value_sol"]
                pos["amount_raw"] = holding["amount"]
                db["positions"][i] = pos
                total_value += holding["value_usd"]
                found = True
                break
        
        # If position not found, add it
        if not found:
            new_pos = {
                "token": token,
                "mint": holding["mint"],
                "amount_raw": holding["amount"],
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
    
    # Remove closed positions that are no longer in holdings
    db["positions"] = [p for p in db["positions"] if p["status"] == "OPEN" and any(h["token"] == p["token"] for h in holdings)]
    
    db["portfolio"]["total_value_usd"] = total_value
    save_db(db)
    return db

if __name__ == "__main__":
    # Test
    db = load_db()
    print(f"Portfolio DB loaded: {db['portfolio']['total_value_usd']} USD")
    print(f"Positions: {len(db['positions'])}")
    print(f"Trades: {len(db['trades'])}")
