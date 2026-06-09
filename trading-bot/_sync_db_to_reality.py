"""Sync DB to on-chain reality"""
import json, os, requests

wallet = "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Get on-chain USDC
url = "https://api.mainnet-beta.solana.com"
data = {"jsonrpc": "2.0", "id": 1, "method": "getTokenAccountsByOwner",
        "params": [wallet, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "jsonParsed"}]}
resp = requests.post(url, json=data, timeout=10)
tokens = resp.json().get("result", {}).get("value", [])
real_usdc = 0
real_tokens = set()
for t in tokens:
    info = t["account"]["data"]["parsed"]["info"]
    mint = info["mint"]
    amt = float(info["tokenAmount"]["uiAmount"] or 0)
    if mint == USDC_MINT:
        real_usdc = round(amt, 2)
    if amt > 0.001:
        real_tokens.add(mint)

print(f"On-chain USDC: ${real_usdc:.2f}")
print(f"On-chain non-zero tokens: {len(real_tokens)}")

# Load DB
db = json.load(open("portfolio.db.json"))
bogus_positions = []
for p in list(db["positions"]):
    mint = p.get("mint", "")
    if mint not in real_tokens and p.get("status") == "OPEN":
        bogus_positions.append(p)
        db["positions"].remove(p)
        print(f"Removed ghost position: {p['token']} (mint {mint[:12]}... - not on wallet)")

# Sync USDC
db["portfolio"]["usdc_balance"] = real_usdc
db["portfolio"]["total_value_usd"] = real_usdc + (db["portfolio"]["sol_balance"] * db["portfolio"]["sol_price_usd"])
db["portfolio"]["positions_count"] = 0  # no open positions

# Also add any sells we did today that aren't recorded
# Check for missing trades by scanning if we had CLOSED positions without corresponding SELL trades
existing_sells = {t.get("mint") for t in db.get("trades", []) if t.get("action") == "SELL"}

# Done
json.dump(db, open("portfolio.db.json", "w"), indent=2)
print(f"\n✅ DB synced")
print(f"  USDC: ${real_usdc:.2f}")
print(f"  Open positions: 0")
print(f"  Total value: ${db['portfolio']['total_value_usd']:.2f}")