"""Test trending scanner and buy sizing"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

# Test 1: DexScreener trending
import requests
r = requests.get("https://api.dexscreener.com/token-boosts/top/v1", timeout=10)
data = r.json()
solana = [d for d in data if isinstance(d, dict) and d.get("chainId") == "solana"]
print(f"=== DEXSCREENER ===")
print(f"Total: {len(data)}, Solana: {len(solana)}")
print(f"Sample fields: {list(solana[0].keys())}")
print(f"Sample: tokenAddress={solana[0].get('tokenAddress','?')[:15]}... url={solana[0].get('url','?')}")

# Test 2: Research module import
sys.path.insert(0, r"C:\Users\compj\.openclaw\workspace\trading-bot")
try:
    import research_v2
    print(f"\n=== RESEARCH V2 IMPORT ===")
    candidates = research_v2.fetch_trending_solana_candidates(count=3)
    print(f"Trending candidates: {len(candidates)}")
    for c in candidates:
        print(f"  {c['token']}: mint={c['mint'][:12]}... price=${c.get('current_price',0):.6f}")
except Exception as e:
    print(f"\nRESEARCH IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test 3: executor_v2 import (no daemon)
try:
    import executor_v2
    print(f"\n=== EXECUTOR V2 IMPORT ===")
    # Test determine_buy_size
    test_signal = {"recommendation": "BUY", "confidence": 55, "momentum": {"trend": "flat", "momentum_pct": 0}}
    size = executor_v2.determine_buy_size(test_signal)
    print(f"determine_buy_size(BUY, conf=55, flat): ${size:.2f}")
    test_signal2 = {"recommendation": "STRONG_BUY", "confidence": 70, "momentum": {"trend": "up", "momentum_pct": 0.03}}
    size2 = executor_v2.determine_buy_size(test_signal2)
    print(f"determine_buy_size(STRONG_BUY, conf=70, up): ${size2:.2f}"  )
except Exception as e:
    print(f"\nEXECUTOR IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()