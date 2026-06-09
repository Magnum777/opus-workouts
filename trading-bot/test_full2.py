import sys, os, traceback
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = open('tradebot_full.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

try:
    import research_v2 as research
    import scout_v2 as scout
    import portfolio_db_v2 as pdb
    import json, risk_manager as risk

    # Step 0: Research
    print("--- RESEARCH ---")
    research_result = research.research_portfolio()
    print(f"Research complete: {len(research_result.get('analyses', []))} tokens analyzed")
    buy_signals = research.get_buy_signals(min_confidence=80)
    sell_signals = research.get_sell_signals()
    print(f"Buy opportunities (conf>=80): {len(buy_signals)}")
    print(f"Sell signals: {len(sell_signals)}")
    for bs in buy_signals:
        print(f"  BUY {bs['token']}: conf={bs['confidence']} rec={bs['recommendation']} price=${bs.get('current_price', 0):.8f}")
    for ss in sell_signals:
        print(f"  SELL {ss['token']}: rec={ss['recommendation']} pnl={ss.get('pnl_pct', 0):.1f}%")

    # Step 1: Scout
    print("--- SCOUT ---")
    sol_balance = scout.get_sol_balance()
    sol_price = scout.get_jupiter_price(scout.SOL_MINT) or 84
    holdings = scout.get_all_holdings()
    usdc_balance = scout.get_usdc_balance()
    print(f"SOL: {sol_balance:.4f} | USDC: ${usdc_balance:.2f}")
    print(f"Holdings tokens: {list(holdings.keys())}")

    # Step 2: Risk summary
    print("--- RISK ---")
    risk_summary = risk.get_risk_summary()
    print(f"Risk summary: {json.dumps(risk_summary, indent=2)}")
    
    # Step 3: Portfolio
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
        for pos in open_positions:
            pos_token = pos['token']
            # Check stop loss / take profit
            sltp = risk.check_stop_loss_take_profit(pos)
            print(f"  {pos_token}: SL/TP check = {sltp}")
    elif usdc < 25:
        print(f"USDC too low (${usdc:.2f} < $25) to trade")
    elif buy_signals:
        print(f"{len(buy_signals)} buy signals to evaluate")
        for bs in buy_signals:
            allowed, reason = risk.check_trade_allowed(
                bs['token'], 'BUY', total_value, 0, mint=bs.get('mint', '')
            )
            print(f"  {bs['token']}: allowed={allowed} reason={reason}")
    else:
        print("No buy signals (conf>=80), no positions - idle")

    print("--- END ---")

except Exception as e:
    traceback.print_exc()
    print(f'Error: {e}')
