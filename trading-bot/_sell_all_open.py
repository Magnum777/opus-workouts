"""Emergency sell of all open positions - we jumped back in too fast"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))
from executor_v2 import execute_sell_live
import portfolio_db_v2 as pdb

TO_SELL = [
    # position label    mint
    ("PENGU", "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv", 3137747097),
    ("JUP",   "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN", 125591281),
    ("ORCA",  "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE", 19245108),
    ("RAY",   "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R", 35111837),
]

def main():
    results = []
    for token, mint, raw_amt in TO_SELL:
        print(f"\nSelling {token} ({mint[:8]}...) - {raw_amt} raw units...")
        success, msg = execute_sell_live(mint, token, raw_amt)
        if success:
            tx = str(msg)[:25]
            print(f"  ✅ SOLD {token} | TX: {tx}...")
            # Close position in DB
            pdb.close_position(token, {
                "close_price_usd": 0,
                "close_value_usd": 0,
                "tx_hash": str(msg)
            })
        else:
            print(f"  ❌ SELL FAILED: {msg}")
        results.append({"token": token, "success": success, "msg": msg})
        time.sleep(2)

    print("\n=== RESULTS ===")
    for r in results:
        s = "🟢" if r["success"] else "🔴"
        print(f"  {s} {r['token']}: {r['msg'][:80]}")

    # After sell, show wallet
    from executor_v2 import get_usdc_balance
    usdc = get_usdc_balance()
    print(f"\nUSDC after sell: ${usdc:.2f}")

if __name__ == "__main__":
    main()