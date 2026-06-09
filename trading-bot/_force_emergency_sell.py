"""Emergency forced sell of TRUMP and ORCA"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from executor_v2 import execute_sell_live
import portfolio_db_v2 as pdb

# TRUMP and ORCA mints + raw amounts we want to dump
TOKENS = {
    "TRUMP": {"mint": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN"},
    "ORCA": {"mint": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE"},
}

def main():
    db = pdb.load_db()
    results = []
    for token, info in TOKENS.items():
        mint = info["mint"]
        # Find open position
        pos = None
        for p in db["positions"]:
            if p["mint"] == mint and p.get("status") == "OPEN":
                pos = p
                break

        if not pos:
            print(f"{token}: No open position found, skipping")
            continue

        amount_raw = pos.get("amount_raw", 0)
        value = pos.get("current_value_usd", 0)
        cost = pos.get("cost_basis_usd", 0)

        if amount_raw <= 0:
            print(f"{token}: Zero balance, skipping")
            continue

        cost_basis = pos.get("cost_basis_usd", 0)
        pnl_pct = ((value - cost_basis) / cost_basis * 100) if cost_basis > 0 else 0

        print(f"Selling {token} ({mint[:8]}...): {amount_raw} raw units, ~${value:.2f}, P&L: {pnl_pct:+.1f}%")
        success, msg = execute_sell_live(mint, token, amount_raw)

        if success:
            pnl_usd = value - cost
            pnl_pct = (pnl_usd / cost * 100) if cost > 0 else 0
            trade = {
                "token": token,
                "action": "SELL",
                "reason": "EMERGENCY_FORCE",
                "amount_raw": amount_raw,
                "amount_usd": value,
                "pnl_usd": pnl_usd,
                "pnl_pct": pnl_pct,
                "tx_hash": str(msg),
                "mint": mint
            }
            pdb.add_trade(trade)
            pdb.close_position(token, {
                "close_price_usd": value,
                "close_value_usd": value,
                "tx_hash": str(msg)
            })
            print(f"  ✅ SOLD! TX: {str(msg)[:20]}...")
        else:
            print(f"  ❌ Sell failed: {msg}")

        results.append({"token": token, "success": success, "msg": msg})

    print("\n=== RESULTS ===")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['token']}: {r['msg'][:80] if r['success'] else r['msg']}")

if __name__ == "__main__":
    main()