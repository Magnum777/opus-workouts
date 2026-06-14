import sys, os, time
sys.path.insert(0, r"C:\Users\compj\.openclaw\workspace\trading-bot")
os.chdir(r"C:\Users\compj\.openclaw\workspace\trading-bot")

print("Testing research...", flush=True)
import research_v2 as research
print("1. research imported", flush=True)

print("Calling research_portfolio()...", flush=True)
try:
    start = time.time()
    rr = research.research_portfolio()
    elapsed = time.time() - start
    print(f"2. Research done in {elapsed:.1f}s: {len(rr.get('analyses', []))} tokens", flush=True)
except Exception as e:
    print(f"2. Research FAILED: {e}", flush=True)
    import traceback
    traceback.print_exc()
