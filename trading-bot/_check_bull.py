"""Check BULL position and value"""
import json, requests

mint = "3TYgKwkE2Y3rxdw9osLRSpxpXmSC1C1oo19W9KHspump"
r = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{mint}", timeout=10)
pairs = r.json().get("pairs", [])
print("=== BULL POSITION ===")
if pairs:
    p = pairs[0]
    price = float(p.get("priceUsd", 0))
    liq = p.get("liquidity", {}).get("usd", 0)
    print(f"Price: ${price:.6f}")
    print(f"Liquidity: ${float(liq):.2f}" if liq else "Liquidity: N/A")
else:
    price = 0

# We have 14675.555753 tokens on-chain
token_amt = 14675.555753
value = token_amt * price
print(f"Tokens: {token_amt:.4f}")
print(f"Value: ${value:.2f} @ ${price:.6f}")
print(f"Cost guess: ~$60 (USDC went from $84 to $25)")
print(f"Unrealized PnL: ~{((value/60)-1)*100:.1f}%" if price > 0 else "Price not available")

# Get USDC
wallet = "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA"
url = "https://api.mainnet-beta.solana.com"
data = {"jsonrpc": "2.0", "id": 1, "method": "getTokenAccountsByOwner",
        "params": [wallet, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "jsonParsed"}]}
resp = requests.post(url, json=data, timeout=10)
tokens = resp.json().get("result", {}).get("value", [])
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
for t in tokens:
    info = t["account"]["data"]["parsed"]["info"]
    if info["mint"] == USDC_MINT:
        usdc = float(info["tokenAmount"]["uiAmount"] or 0)
        print(f"\nUSDC: ${usdc:.2f}")
        print(f"Total portfolio: ${value + usdc:.2f}")
        break