#!/usr/bin/env python3
"""List all portfolio assets - live from chain + DB."""
import json, requests, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from solders.keypair import Keypair
from solana.rpc.api import Client

WALLET = Keypair.from_bytes(bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d"))
H = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
C = Client(H)
WS = str(WALLET.pubkey())
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_PRICE = 170

sol_raw = C.get_balance(WALLET.pubkey()).value
sol = sol_raw / 1e9
sol_usd = sol * SOL_PRICE

all_mints = {}
for prog_id in ["TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"]:
    r = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getTokenAccountsByOwner","params":[WS,{"programId":prog_id},{"encoding":"jsonParsed"}]}, timeout=10).json()
    for a in r.get("result", {}).get("value", []):
        info = a["account"]["data"]["parsed"]["info"]
        mint = info.get("mint", "")
        amt = float(info.get("tokenAmount", {}).get("uiAmount", 0) or 0)
        all_mints[mint] = amt

# Print
print("=== Portfolio ===")
print("Wallet:", WS)
print()

print("Native SOL:", f"{sol:.6f}", "($" + str(round(sol_usd, 2)) + ")")
print()

# Known tokens
known_labels = {
    USDC_MINT: "USDC",
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": "USDT",
    "So11111111111111111111111111111111111111112": "wSOL",
    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN": "JUP",
    "or": "ORCA",
    "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R": "RAY",
    "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv": "PENGU",
    "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn": "PUMP",
    "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN": "TRUMP",
    "2tXpgu2DLTsPUf9zFmuZmA4xrYxXKBTpVq9wAM7hzs9y": "HANTA",
}

usdc_amt = all_mints.get(USDC_MINT, 0)
print("USDC: $" + str(round(usdc_amt, 2)))
print()

other_sum = 0
for mint, amt in sorted(all_mints.items()):
    if mint == USDC_MINT:
        continue
    label = known_labels.get(mint, mint[:15])
    
    # Try to price it
    try:
        p = requests.get("https://lite-api.jup.ag/swap/v1/quote?inputMint=" + mint + "&outputMint=" + USDC_MINT + "&amount=1000000&slippage=50", timeout=10).json()
        if "outAmount" in p:
            price_per = float(p["outAmount"]) / 1e6
            val = price_per * amt / 1_000_000
            other_sum += val
            print("  " + label + ": " + f"{amt:,.2f}" + " (~$" + str(round(val, 2)) + ")")
        else:
            print("  " + label + ": " + f"{amt:,.2f}" + " (no price)")
    except:
        print("  " + label + ": " + f"{amt:,.2f}" + " (no price)")

# DB stats
print()
with open(os.path.join(os.path.dirname(__file__), "portfolio.db.json")) as f:
    db = json.load(f)

pf = db["performance"]
print("Performance:")
print("  Realized PnL: $" + str(round(pf.get("total_realized_pnl", 0), 2)))
print("  Win/Loss: " + str(pf.get("win_count", 0)) + "W / " + str(pf.get("loss_count", 0)) + "L")
print("  Consecutive losses: " + str(db.get("risk_metrics", {}).get("consecutive_losses", 0)))

print()
print("Open positions: 0")
print()

total = sol_usd + usdc_amt + other_sum
print("=" * 40)
print("NET WORTH: $" + str(round(total, 2)))
print("  SOL: $" + str(round(sol_usd, 2)))
print("  USDC: $" + str(round(usdc_amt, 2)))
print("  Other: $" + str(round(other_sum, 2)))