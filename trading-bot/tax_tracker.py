"""
Trading Journal & Tax Tracker
Tracks all trades for tax purposes
"""
import json
from datetime import datetime

JOURNAL_PATH = "trading-bot/trade_journal.json"

def load_journal():
    import os
    if not os.path.exists(JOURNAL_PATH):
        return {"trades": [], "summary": {"total_trades": 0, "realized_pnl": 0, "fees_paid": 0}}
    with open(JOURNAL_PATH, "r") as f:
        return json.load(f)

def add_trade(trade):
    journal = load_journal()
    trade["timestamp"] = datetime.now().isoformat()
    journal["trades"].append(trade)
    
    # Update summary
    if trade.get("pnl"):
        journal["summary"]["realized_pnl"] += trade["pnl"]
    if trade.get("fee"):
        journal["summary"]["fees_paid"] += trade["fee"]
    journal["summary"]["total_trades"] += 1
    
    with open(JOURNAL_PATH, "w") as f:
        json.dump(journal, f, indent=2)
    
    return journal

def get_tax_report():
    journal = load_journal()
    trades = journal["trades"]
    
    # Group by year
    by_year = {}
    for t in trades:
        year = t.get("timestamp", "")[:4]
        if year not in by_year:
            by_year[year] = {"trades": 0, "pnl": 0, "fees": 0}
        by_year[year]["trades"] += 1
        by_year[year]["pnl"] += t.get("pnl", 0)
        by_year[year]["fees"] += t.get("fee", 0)
    
    return {
        "total_trades": journal["summary"]["total_trades"],
        "realized_pnl": journal["summary"]["realized_pnl"],
        "fees_paid": journal["summary"]["fees_paid"],
        "by_year": by_year
    }

# Test
if __name__ == "__main__":
    # Add sample trade
    add_trade({
        "type": "SWAP",
        "pair": "SOL-USDC",
        "sent_amount": 0.01,
        "sent_token": "SOL",
        "received_amount": 0.85,
        "received_token": "USDC",
        "fee": 0.0005,
        "tx_hash": "44EmeKBY1XjQ2csjFAmypLcqog7ApdmMEoLmZkcrGv7BCdEkvPeZy2TS29Q21G8AahWFmKX72jCLHS4spmdnQJvz"
    })
    
    print(json.dumps(get_tax_report(), indent=2))
