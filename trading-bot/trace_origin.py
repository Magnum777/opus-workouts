#!/usr/bin/env python3
"""Trace all deposits into this wallet from the blockchain."""
import requests, json, sys, os

H = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
WS = "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA"

print("Fetching oldest transactions...")
r = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getSignaturesForAddress","params":[WS,{"limit":1000}]}, timeout=10).json()
sigs = r.get("result", [])
print(f"Total: {len(sigs)} tx")

# Get the oldest 20
oldest_20 = sigs[-20:]

print("\n=== OLDEST TRANSACTIONS (the very first activity) ===\n")
for sig_info in reversed(oldest_20):
    sig = sig_info["signature"]
    slot = sig_info["slot"]
    tx = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getTransaction","params":[sig,{"encoding":"jsonParsed","maxSupportedTransactionVersion":0}]}, timeout=10).json()
    result_data = tx.get("result") or tx.get("error", {})
    if not tx.get("result"):
        print(f"  {sig[:25]}.. NO RESULT (tx likely expired from Helius cache)")
        continue
    
    meta = tx["result"].get("meta", {})
    msg = tx["result"].get("transaction", {}).get("message", {})
    accts = msg.get("accountKeys", [])
    pre = meta.get("preBalances", [0])
    post = meta.get("postBalances", [0])
    fee = meta.get("fee", 0)
    
    # Our wallet SOL change
    wallet_sol = (post[0] - pre[0]) / 1e9 if len(pre) > 0 else 0
    
    # Raw display of ALL balance changes for this tx
    bal_changes = []
    for i in range(min(len(pre), len(post))):
        bal_change = post[i] - pre[i]
        if abs(bal_change) > 1000 and i < len(accts):
            addr = str(accts[i])[:30]
            bal_changes.append(f"{addr}: {bal_change/1e9:+.4f}")
    
    # USDC change
    pre_usdc = 0
    post_usdc = 0
    for b in meta.get("preTokenBalances", []):
        if b.get("mint") == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v":
            pre_usdc = float(b.get("uiTokenAmount",{}).get("uiAmount",0) or 0)
    for b in meta.get("postTokenBalances", []):
        if b.get("mint") == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v":
            post_usdc = float(b.get("uiTokenAmount",{}).get("uiAmount",0) or 0)
    
    usdc_change = post_usdc - pre_usdc
    
    # Always print for oldest 20
    bal_str = " | ".join(bal_changes)
    print(f"  slot={slot} | USDC=${usdc_change:+.2f} | {bal_str}")

print("=== ACCOUNTING ===")
print("The first transaction that shows MONEY coming IN is the truth.")
print("Everything else is trades, swaps, fees.")