import sys, os, time, signal
sys.path.insert(0, os.path.dirname(__file__))
print(f'[{time.time():.0f}] Starting research_portfolio test...', flush=True)
import research_v2 as research
print(f'[{time.time():.0f}] Running research_portfolio()...', flush=True)
try:
    result = research.research_portfolio()
    print(f'[{time.time():.0f}] DONE: {len(result.get(\"analyses\", []))} tokens', flush=True)
except Exception as e:
    print(f'[{time.time():.0f}] ERROR: {e}', flush=True)
    import traceback
    traceback.print_exc()
