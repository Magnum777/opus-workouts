"""Sell BULL and reset to USDC"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from executor_v2 import execute_sell_live
import portfolio_db_v2 as pdb

mint = "3TYgKwkE2Y3rxdw9osLRSpxpXmSC1C1oo19W9KHspump"
raw_amt = 146755555753  # 14675.555753 * 1e6

print(f"Selling BULL ({mint[:12]}...) - {raw_amt} raw...")
success, msg = execute_sell_live(mint, "BULL", raw_amt)
if success:
    print(f"  SOLD! TX: {str(msg)[:25]}...")
else:
    print(f"  FAILED: {msg}")

# Sync DB
import json, requests
wallet = "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
url = "https://api.mainnet-beta.solana.com"
data = {"jsonrpc": "2.0", "id": 1, "method": "getTokenAccountsByOwner",
        "params": [wallet, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "jsonParsed"}]}
resp = requests.post(url, json=data, timeout=10)
tokens = resp.json().get("result", {}).get("value", [])
real_usdc = 0
for t in tokens:
    info = t["account"]["data"]["parsed"]["info"]
    if info["mint"] == USDC_MINT:
        real_usdc = float(info["tokenAmount"]["uiAmount"] or 0)

db = json.load(open("portfolio.db.json"))
db["portfolio"]["usdc_balance"] = round(real_usdc, 2)
db["portfolio"]["total_value_usd"] = real_usdc
db["portfolio"]["positions_count"] = 0
db["positions"] = [p for p in db["positions"] if p.get("status") == "CLOSED"]
db["signals"] = []
db["risk_metrics"]["consecutive_losses"] = 0
db["risk_metrics"]["daily_trade_count"] = 0
json.dump(db, open("portfolio.db.json", "w"), indent=2)

# Clear cooldowns for BULL
cooldowns = json.load(open("rebuy_cooldowns.json"))
cooldowns.pop(mint.upper(), None)
cooldowns.pop(mint.lower(), None)
json.dump(cooldowns, open("rebuy_cooldowns.json", "w"), indent=2)

print(f"\nDB synced. USDC: ${real_usdc:.2f}")