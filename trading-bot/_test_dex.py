"""Quick test of DexScreener API"""
import json, requests

r = requests.get("https://api.dexscreener.com/token-boosts/top/v1", timeout=10)
data = r.json()
print(f"Status: {r.status_code}, results: {len(data)}")
solana = [d for d in data if d.get("chainId") == "solana"]
print(f"Solana tokens: {len(solana)}")
for d in solana[:5]:
    url = d.get("url", "")
    token_id = url.split("/")[-1][:15] if url else "?"
    print(f"  {token_id}: score={d.get('score','?')}")