"""Inspect DexScreener API structure"""
import json, requests

r = requests.get("https://api.dexscreener.com/token-boosts/top/v1", timeout=10)
data = r.json()
print(f"Total: {len(data)}")
print(f"First item keys: {list(data[0].keys())}")
print(f"\nFirst 3 items:")
for d in data[:3]:
    print(f"  {json.dumps(d, indent=2)}")
print(f"\n---\nAll solana token addresses:")
for d in data:
    if d.get("chainId") == "solana":
        print(f"  {d.get('url','?')}")