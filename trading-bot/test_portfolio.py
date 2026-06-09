import sys, os, traceback, json
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = open('tradebot_full.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

try:
    import scout_v2 as scout
    import portfolio_db_v2 as pdb
    import risk_manager as risk

    # Portfolio DB
    db = pdb.load_db()
    positions = db.get("positions", [])
    open_positions = [p for p in positions if p.get("status") == "OPEN"]
    trades = db.get("trades", [])
    
    print("--- PORTFOLIO DB ---")
    print(f"Open positions: {len(open_positions)}")
    for p in open_positions:
        print(f"  {p.get('token','?')}: entry={p.get('buy_price_usd','?')} size={p.get('size_usd','?')} sl={p.get('stop_loss','?')} tp={p.get('take_profit','?')}")
    print(f"Recent trades: {len(trades)}")
    for t in trades[-3:]:
        print(f"  {t.get('token','?')}: {t.get('action','?')} pnl={t.get('pnl','?')}")

    # Scout holdings
    print("\n--- HOLDINGS ---")
    holdings = scout.get_all_holdings()
    total_usd = 0
    for mint, data in holdings.items():
        print(f"  {mint}: {data.get('amount',0)}")
    
    usdc = scout.get_usdc_balance()
    sol = scout.get_sol_balance()
    print(f"\nUSDC: ${usdc:.2f}")
    print(f"SOL: {sol:.4f}")
    print(f"SOL price: ${scout.get_jupiter_price(scout.SOL_MINT):.2f}")
    
    # Check if daemon would report
    print("\n--- DAEMON DECISION ---")
    if open_positions:
        print(f"Open position exists: {open_positions[0].get('token','?')}")
    elif usdc < 25:
        print(f"USDC too low (${usdc:.2f} < $25) - NO BUY")
    else:
        print(f"USDC sufficient (${usdc:.2f} >= $25) - checking signals")
    
    # Check stop loss / take profit for any open positions
    for p in open_positions:
        sltp = risk.check_stop_loss_take_profit(p)
        print(f"  {p.get('token','?')} SL/TP: {sltp}")
    
    print("\n--- FULL OUTPUT END ---")
    
except Exception as e:
    traceback.print_exc()
    print(f'Error: {e}')
