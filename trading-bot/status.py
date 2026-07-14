#!/usr/bin/env python3
import os
import json, requests
from solders.keypair import Keypair
from solana.rpc.api import Client

WALLET = Keypair.from_bytes(bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", "")))
H = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")
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