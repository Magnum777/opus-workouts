import sys, os, traceback
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = open('tradebot_full.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

def log(msg):
    print(msg)
    print(msg, file=open('tradebot_console.txt', 'a', encoding='utf-8'))

try:
    import research_v2 as research
    import scout_v2 as scout
    import executor_v2 as execmod
    import portfolio_db_v2 as pdb
    import token_safety_check as safety
    import risk_manager as risk

    # Step 0: Research
    print("--- RESEARCH ---")
    research_result = research.research_portfolio()
    print(f"Research complete: {len(research_result.get('analyses', []))} tokens analyzed")
    buy_signals = research.get_buy_signals(min_confidence=80)
    sell_signals = research.get_sell_signals()
    print(f"Buy opportunities: {len(buy_signals)}")
    print(f"Sell signals: {len(sell_signals)}")
    for bs in buy_signals:
        print(f"  BUY {bs['token']}: conf={bs['confidence']} rec={bs['recommendation']} price=${bs['current_price']:.8f}")
    for ss in sell_signals:
        print(f"  SELL {ss['token']}: rec={ss['recommendation']} pnl={ss.get('pnl_pct', 0):.1f}%")

    # Step 1: Scout
    print("--- SCOUT ---")
    sol_balance = scout.get_sol_balance()
    sol_price = scout.get_jupiter_price(scout.SOL_MINT) or 84
    holdings = scout.get_all_holdings()
    usdc_balance = scout.get_usdc_balance()
    print(f"SOL: {sol_balance:.4f} | USDC: ${usdc_balance:.2f}")
    print(f"Holdings: {len(holdings)} tokens")

    # Step 2: Risk manager
    print("--- RISK ---")
    risk_state = risk.get_state()
    risk_check = risk.can_trade()
    print(f"Risk state: {risk_state}")
    print(f"Can trade: {risk_check}")

    # Step 3: Portfolio valuation
    print("--- PORTFOLIO ---")
    total_value = scout.get_total_portfolio_value_usd()
    print(f"Total portfolio value: ${total_value:.2f}")
    
    open_positions = pdb.get_open_positions()
    print(f"Open positions: {len(open_positions)}")
    for op in open_positions:
        print(f"  {op['token']}: entry=${op.get('entry_price', 0):.6f} size=${op.get('size_usd', 0):.2f}")
    
    usdc = scout.get_usdc_balance()
    print(f"USDC available: ${usdc:.2f}")
    
    # Step 4: Trade decisions
    print("--- TRADE DECISIONS ---")
    if open_positions:
        print("Open position exists - checking sell signals")
        # ... sell logic
    elif usdc < 25:
        print("USDC too low (< $25) to trade")
    elif not risk_check.get('allowed', True):
        print(f"Risk manager blocks trade: {risk_check.get('reason', 'unknown')}")
    elif buy_signals:
        print(f"{len(buy_signals)} buy signals to evaluate")
        for bs in buy_signals:
            print(f"  Signal: {bs['token']} conf={bs['confidence']}")
    else:
        print("No buy signals, no positions - idle")

except Exception as e:
    traceback.print_exc()
    print(f'Error: {e}')
