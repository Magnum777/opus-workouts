import sys, os, traceback
sys.path.insert(0, os.path.dirname(__file__))
sys.stdout = open('tradebot_debug.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

try:
    import research_v2 as research
    print('Research imported OK')
    result = research.research_portfolio()
    print(f'Research result keys: {list(result.keys())}')
    print(f'Analyses count: {len(result.get("analyses", []))}')
    
    buy = research.get_buy_signals(min_confidence=80)
    sell = research.get_sell_signals()
    print(f'Buy signals: {len(buy)}')
    print(f'Sell signals: {len(sell)}')
    for b in buy:
        print(f'  BUY {b["token"]}: conf={b["confidence"]}')
    for s in sell:
        print(f'  SELL {s["token"]}: rec={s["recommendation"]}')
except Exception as e:
    traceback.print_exc()
    print(f'Error: {e}')
