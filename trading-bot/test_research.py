import sys, io, os, dotenv, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(r'C:\Users\compj\.openclaw\workspace\trading-bot')
dotenv.load_dotenv(override=True)
sys.path.insert(0, os.getcwd())
import research_v2 as research
import research_context as rctx
print('modules loaded')

t0 = time.time()
rc = rctx.load_research_context()
print(f'research_context: {time.time()-t0:.1f}s')

t0 = time.time()
print('calling research.research_portfolio()...')
result = research.research_portfolio()
print(f'research_portfolio: {time.time()-t0:.1f}s')
print('analyses:', len(result.get('analyses',[])))

t0 = time.time()
buys = research.get_buy_signals(min_confidence=75)
print(f'get_buy_signals: {time.time()-t0:.1f}s, {len(buys)} signals')

t0 = time.time()
sells = research.get_sell_signals()
print(f'get_sell_signals: {time.time()-t0:.1f}s, {len(sells)} signals')

for b in buys[:5]:
    print(f'  BUY {b["token"]}: conf={b["confidence"]} price=')
for s in sells[:5]:
    print(f'  SELL {s["token"]}: rec={s["recommendation"]}')
