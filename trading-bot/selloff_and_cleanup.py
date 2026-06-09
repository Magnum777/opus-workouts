#!/usr/bin/env python3
"""
Phase 2 Launch Script
1. Clean DB (reset fake PnL from JUP corruption)
2. Sell ALL open positions to free capital
3. Clear buy watch list / trading queue
4. Report results
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datetime import datetime, timezone
from executor_v2 import execute_sell_live, get_usdc_balance
import portfolio_db_v2 as pdb

print("=" * 60)
print("PHASE 2 LAUNCH - %s" % datetime.now(timezone.utc).strftime('%b %d %I:%M %p ET'))
print("=" * 60)

# -- STEP 1: Clean DB --
print("\n--- STEP 1: Cleaning Database ---")
db = pdb.load_db()

# Reset the fake realized PnL from JUP corruption
db["performance"]["total_realized_pnl"] = 0
db["performance"]["win_rate"] = 0
db["performance"]["avg_profit_per_trade"] = 0
db["performance"]["daily_avg"] = 0
db["performance"]["projected_days_to_1000"] = 999

# Reset tax summary 
db["tax_summary"] = {
    "2026": {"total_trades": 0, "realized_pnl": 0, "fees_paid": 0}
}

# Keep only OPEN positions - remove closed ones with fake PnL
closed_positions = [p for p in db["positions"] if p.get("status") == "CLOSED"]
print("Removing %d CLOSED positions from DB (fake PnL)" % len(closed_positions))
db["positions"] = [p for p in db["positions"] if p.get("status") == "OPEN"]

# Clean trades list too - remove the fake ones
trade_count_before = len(db.get("trades", []))
db["trades"] = []
print("Cleared %d stale trades from history" % trade_count_before)

pdb.save_db(db)
print("Database cleaned [OK]")

# -- STEP 2: Sell All Open Positions --
print("\n--- STEP 2: Selling All Open Positions ---")

db = pdb.load_db()
positions = [p for p in db["positions"] if p.get("status") == "OPEN"]
print("Open positions to sell: %d" % len(positions))

results = []
for pos in positions:
    token = pos.get("token", "???")
    mint = pos.get("mint", "")
    amount_raw = pos.get("amount_raw", 0)
    value = pos.get("current_value_usd", 0)
    cost = pos.get("cost_basis_usd", 0)
    pnl_pct = ((value - cost) / cost * 100) if cost > 0 else 0
    
    print("\n  Selling %s..." % token)
    print("    Value: $%.2f | Cost: $%.2f | PnL: %+.2f%%" % (value, cost, pnl_pct))
    print("    Amount raw: %s" % amount_raw)
    
    if amount_raw <= 0:
        print("    [FAIL] No tokens to sell (amount_raw=0)")
        continue
    
    success, msg = execute_sell_live(mint, token, amount_raw)
    
    if success:
        proceeds = value
        pnl_usd = value - cost
        
        # Close position in DB
        pdb.close_position(token, {
            "close_price_usd": value,
            "close_value_usd": value,
            "tx_hash": str(msg)
        })
        
        results.append("[OK] SOLD %s: $%.2f | PnL %+.2f%% | TX: %s..." % (token, value, pnl_pct, str(msg)[:20]))
        print("    [OK] Sold! TX: %s..." % str(msg)[:30])
    else:
        results.append("[FAIL] SELL %s FAILED: %s" % (token, msg))
        print("    [FAIL] Failed: %s" % msg)

# -- STEP 3: Clear Trading Queue --
print("\n--- STEP 3: Clearing Trading Queue ---")
queue_path = os.path.join(os.path.dirname(__file__), "trading-queue.json")
if os.path.exists(queue_path):
    queue = {"pending": [], "executed": []}
    with open(queue_path, "w") as f:
        json.dump(queue, f, indent=2)
    print("Trading queue cleared [OK]")

# Clear rebuy cooldowns too (fresh start)
cooldown_path = os.path.join(os.path.dirname(__file__), "rebuy_cooldowns.json")
if os.path.exists(cooldown_path):
    os.remove(cooldown_path)
    print("Rebuy cooldowns cleared [OK]")

# -- STEP 4: Report --
print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
for r in results:
    print("  %s" % r)

# Wait a moment for chain state to settle, then check balance
print("\n--- Checking final USDC balance ---")
time.sleep(5)
final_usdc = get_usdc_balance()

# Also sync from blockchain to update DB
import scout_v2 as scout
try:
    sol_balance = scout.get_sol_balance()
    sol_price = scout.get_jupiter_price(scout.SOL_MINT) or 80
    holdings = scout.get_all_holdings()
    
    holdings_list = []
    for mint, h in holdings.items():
        token = scout.MINT_TO_NAME.get(mint, mint[:10])
        price = scout.get_jupiter_price(mint, decimals=h['decimals'])
        if mint == scout.USDC:
            price = 1.0
        value_usd = h['amount'] * price if price > 0 else 0
        if value_usd < 0.01:
            continue
        holdings_list.append({
            "token": token, "mint": mint, "amount": h['amount'],
            "amount_raw": h['raw'], "decimals": h['decimals'],
            "value_usd": value_usd, "value_sol": value_usd / sol_price if sol_price > 0 else 0
        })
    
    pdb.sync_from_blockchain(holdings_list, sol_balance, sol_price)
    print("Blockchain sync complete [OK]")
except Exception as e:
    print("Blockchain sync error: %s" % e)

db = pdb.load_db()
total = db["portfolio"]["total_value_usd"]
print("\n[PORTFOLIO] FINAL TOTAL: $%.2f" % total)
print("   USDC: $%.2f" % db["portfolio"]["usdc_balance"])
print("   SOL: %.4f @ $%.2f" % (db["portfolio"]["sol_balance"], db["portfolio"]["sol_price_usd"]))

if final_usdc:
    print("[CASH] Free USDC to deploy: $%.2f" % final_usdc)

print("\nPhase 2 ready. Run daemon cycle for fresh analysis + buys.")
print("=" * 60)