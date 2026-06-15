#!/usr/bin/env python3
"""Deep audit: scan all wallet transactions, trace every dollar."""
import json, requests, sys, os, time

H = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
WS = "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

print("Fetching 200 recent transactions...")
r = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getSignaturesForAddress","params":[WS,{"limit":200}]}, timeout=10).json()
sigs = r.get("result", [])
print(f"Total: {len(sigs)} tx")

# Categories
deposits = []    # SOL in (external sends, ATA closes)
swaps_buy = []   # USDC -> SOL
swaps_sell = []  # SOL -> USDC
token_buys = []  # USDC -> token
token_sells = [] # token -> USDC
fees_total = 0
unexplained = []

for sig_info in sigs:
    sig = sig_info["signature"]
    tx = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getTransaction","params":[sig,{"encoding":"jsonParsed","maxSupportedTransactionVersion":0}]}, timeout=10).json()
    if not tx.get("result"):
        continue
    meta = tx["result"].get("meta", {})
    
    fee = meta.get("fee", 0)
    fees_total += fee
    
    pre_sol = meta.get("preBalances", [0])[0]
    post_sol = meta.get("postBalances", [0])[0]
    sol_change = (post_sol - pre_sol + fee) / 1e9
    
    pre_usdc = 0
    post_usdc = 0
    pre_other = {}
    post_other = {}
    
    for b in meta.get("preTokenBalances", []):
        mint = b.get("mint", "")
        amt = float(b.get("uiTokenAmount", {}).get("uiAmount", 0) or 0)
        if mint == USDC_MINT:
            pre_usdc = amt
        elif amt > 0:
            pre_other[mint] = amt
    
    for b in meta.get("postTokenBalances", []):
        mint = b.get("mint", "")
        amt = float(b.get("uiTokenAmount", {}).get("uiAmount", 0) or 0)
        if mint == USDC_MINT:
            post_usdc = amt
        elif amt > 0:
            post_other[mint] = amt
    
    usdc_change = post_usdc - pre_usdc
    slot = sig_info["slot"]
    
    # Classify the transaction
    if abs(sol_change) > 0.01 and abs(usdc_change) < 0.5 and sol_change > 0:
        deposits.append({"slot": slot, "sol": round(sol_change, 4), "sig": sig[:25]})
    elif usdc_change < -5 and sol_change > 0.01:
        swaps_buy.append({"slot": slot, "usdc": round(-usdc_change, 2), "sol": round(sol_change, 4), "sig": sig[:25]})
    elif sol_change < -0.01 and usdc_change > 5:
        swaps_sell.append({"slot": slot, "sol": round(-sol_change, 4), "usdc": round(usdc_change, 2), "sig": sig[:25]})
    elif usdc_change < -5 and len(post_other) > 0:
        token_buys.append({"slot": slot, "usdc": round(-usdc_change, 2), "tokens": dict((k[:15], round(v, 0)) for k,v in post_other.items()), "sig": sig[:25]})
    elif usdc_change > 0 and abs(sol_change) < 0.01:
        token_sells.append({"slot": slot, "usdc": round(usdc_change, 2), "pre_tokens": dict((k[:15], round(v, 0)) for k,v in pre_other.items()), "sig": sig[:25]})
    else:
        unexplained.append({"slot": slot, "sol": round(sol_change, 4), "usdc": round(usdc_change, 2), "sig": sig[:25]})

print()
print("=== DEPOSITS (SOL in - external sends, ATA closes) ===")
total_dep = sum(d["sol"] for d in deposits)
print(f"Total: {total_dep:.4f} SOL")
for d in deposits:
    print(f"  +{d['sol']:.4f} slot={d['slot']} {d['sig']}")

print()
print("=== USDC -> SOL SWAPS ===")
total_buy_usdc = sum(s["usdc"] for s in swaps_buy)
total_buy_sol = sum(s["sol"] for s in swaps_buy)
print(f"Total: ${total_buy_usdc:.2f} USDC -> {total_buy_sol:.4f} SOL")
for s in swaps_buy:
    rate = s["sol"] * 170 / s["usdc"] if s["usdc"] > 0 else 0
    print(f"  -${s['usdc']:.2f} +{s['sol']:.4f} ({rate:.0f}% of market) slot={s['slot']} {s['sig']}")

print()
print("=== SOL -> USDC SWAPS ===")
total_sell_sol = sum(s["sol"] for s in swaps_sell)
total_sell_usdc = sum(s["usdc"] for s in swaps_sell)
print(f"Total: {total_sell_sol:.4f} SOL -> ${total_sell_usdc:.2f} USDC")
for s in swaps_sell:
    rate = s["usdc"] / (s["sol"] * 1.7) if s["sol"] > 0 else 0
    print(f"  -{s['sol']:.4f} +${s['usdc']:.2f} ({rate:.0f}% of market) slot={s['slot']} {s['sig']}")

print()
print("=== TOKEN BUYS (USDC -> tokens) ===")
total_buy_usdc_tokens = sum(b["usdc"] for b in token_buys)
print(f"Total: ${total_buy_usdc_tokens:.2f} USDC spent on tokens")
for b in token_buys:
    print(f"  -${b['usdc']:.2f} for {b['tokens']} slot={b['slot']} {b['sig']}")

print()
print("=== TOKEN SELLS (tokens -> USDC) ===")
total_sell_usdc_tokens = sum(s["usdc"] for s in token_sells)
print(f"Total: ${total_sell_usdc_tokens:.2f} USDC from sells")
for s in token_sells:
    print(f"  +${s['usdc']:.2f} from {s['pre_tokens']} slot={s['slot']} {s['sig']}")

print()
print("=== UNEXPLAINED ===")
for u in unexplained:
    print(f"  SOL={u['sol']:+.4f} USDC=${u['usdc']:+.2f} slot={u['slot']} {u['sig']}")

print()
print("=== GRAND SUMMARY ===")
print(f"Fees paid: {fees_total} lamports ({round(fees_total/1e9, 6)} SOL)")
print(f"SOL deposits (external + ATA): {total_dep:.4f} SOL")
print(f"USDC -> SOL swaps: ${total_buy_usdc:.2f} USDC")
print(f"SOL -> USDC swaps: ${total_sell_usdc:.2f} USDC")
print(f"Token buys: ${total_buy_usdc_tokens:.2f} USDC")
print(f"Token sells: ${total_sell_usdc_tokens:.2f} USDC")
net_flow = total_sell_usdc + total_sell_usdc_tokens - total_buy_usdc - total_buy_usdc_tokens
print(f"Net USDC flow (positive = money in): ${net_flow:.2f}")
print(f"Current USDC: check chain")
print(f"Current SOL: check chain")