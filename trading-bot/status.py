#!/usr/bin/env python3
import json, requests
from solders.keypair import Keypair
from solana.rpc.api import Client

WALLET = Keypair.from_bytes(bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d"))
H = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
C = Client(H)

sol_raw = C.get_balance(WALLET.pubkey()).value
sol = sol_raw / 1e9
sol_price = 170
sol_usd = sol * sol_price

r = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getTokenAccountsByOwner","params":[str(WALLET.pubkey()),{"mint":"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"},{"encoding":"jsonParsed"}]}, timeout=10).json()
accts = r.get("result",{}).get("value",[])
usdc = float(accts[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]) if accts else 0

total = usdc + sol_usd
status = "GREEN" if sol >= 0.003 else "RED - BELOW RENT THRESHOLD!"

print(f">**TradeBot** | SOL: {sol:.4f} (${sol_usd:.2f}) | USDC: ${usdc:.2f} | Total: ${total:.2f}")
print(f">Gas status: {status}")
print(f">Safe above 0.003 SOL | Refill triggers at 0.003 | Target: 0.01+")