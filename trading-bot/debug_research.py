import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
print(f'[{time.time():.0f}] Starting research test...')
import research_v2 as research
print(f'[{time.time():.0f}] research_v2 imported')

print(f'[{time.time():.0f}] Running research_portfolio...')
result = research.research_portfolio()
print(f'[{time.time():.0f}] Research complete: {len(result.get("analyses", []))} tokens')

print(f'[{time.time():.0f}] Getting buy signals...')
buys = research.get_buy_signals(min_confidence=75)
print(f'[{time.time():.0f}] Buy signals: {len(buys)}')

print(f'[{time.time():.0f}] Getting sell signals...')
sells = research.get_sell_signals()
print(f'[{time.time():.0f}] Sell signals: {len(sells)}')

print(f'[{time.time():.0f}] DONE')
