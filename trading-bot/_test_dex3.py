"""Test DexScreener pairs API for price + liquidity data"""
import json, requests

# Check a trending token's pairs
mint = "EhHyfjRwj2jhmSE7GW5uJfizaLcNDa5C4HWPiSqjpump"
r = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{mint}", timeout=10)
data = r.json()
pairs = data.get("pairs", [])
print(f"Pairs for {mint[:15]}...: {len(pairs)}")
if pairs:
    p = pairs[0]
    print(f"  Price USD: {p.get('priceUsd','?')}")
    print(f"  Liquidity USD: {p.get('liquidity',{}).get('usd','?')}")
    print(f"  Volume 24h: {p.get('volume',{}).get('h24','?')}")
    print(f"  Symbol: {p.get('baseToken',{}).get('symbol','?')}")
    print(f"  Chain: {p.get('chainId','?')}")
    print(f"  Fdv: {p.get('fdv','?')}")
else:
    print("No pairs data")
    # Check what DexScreener boosted response looks like  
    r2 = requests.get("https://api.dexscreener.com/token-boosts/top/v1", timeout=10)
    print(f"Boosted item keys: {list(r2.json()[0].keys())}")
    print(f"Boosted sample: {json.dumps(r2.json()[0], indent=2)}")