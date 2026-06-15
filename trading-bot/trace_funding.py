#!/usr/bin/env python3
"""Trace every cent that ever entered this wallet from the blockchain."""
import requests, json, sys, os, time

H = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
WS = "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

print("Fetching ALL transactions...")
all_sigs = []
before = None
for page in range(50):
    params = {"limit": 100}
    if before:
        params["before"] = before
    r = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getSignaturesForAddress","params":[WS,params]}, timeout=10).json()
    batch = r.get("result", [])
    if not batch:
        break
    all_sigs.extend(batch)
    before = batch[-1]["signature"]
    print(f"  Page {page+1}: {len(batch)} tx (total {len(all_sigs)})")
    if page >= 4:
        break  # 500 tx is enough

print(f"\n{len(all_sigs)} total transactions\n")

# Track: SOL deposits from external, SOL spent on fees, USDC deposits from external
external_sol_funding = 0.0  # SOL sent TO this wallet from outside
total_fees = 0
external_usdc_funding = 0.0

# Track the very first deposit
first_deposit_found = False

for idx, sig_info in enumerate(all_sigs):
    sig = sig_info["signature"]
    if idx % 100 == 0:
        print(f"Processing {idx}/{len(all_sigs)}...")
    
    tx = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getTransaction","params":[sig,{"encoding":"jsonParsed","maxSupportedTransactionVersion":0}]}, timeout=10).json()
    if not tx.get("result"):
        continue
    
    meta = tx["result"].get("meta", {})
    msg = tx["result"].get("transaction", {}).get("message", {})
    accts = msg.get("accountKeys", [])
    pre = meta.get("preBalances", [])
    post = meta.get("postBalances", [])
    fee = meta.get("fee", 0)
    total_fees += fee
    
    # Our wallet balance change (index 0)
    our_pre = pre[0] if len(pre) > 0 else 0
    our_post = post[0] if len(post) > 0 else 0
    our_sol_change = (our_post - our_pre) / 1e9
    
    # Check if external account sent us SOL
    for i in range(min(len(pre), len(post))):
        change = post[i] - pre[i]
        if i == 0:
            continue  # our wallet
        if change > 500000:  # > 0.0005 SOL gained by another account
            addr = str(accts[i])[:25] if i < len(accts) else "?"
            if change < -500000 and i < len(accts):
                addr_from = str(accts[i])[:25]
                # They lost SOL, we gained it
                if our_sol_change > 0:
                    external_sol_funding += our_sol_change
                    if not first_deposit_found:
                        print(f"FIRST DEPOSIT: {our_sol_change:.4f} SOL from {addr_from} slot={sig_info['slot']}")
                        first_deposit_found = True
    
    # USDC changes
    pre_usdc = 0
    post_usdc = 0
    for b in meta.get("preTokenBalances", []):
        if b.get("mint") == USDC_MINT:
            pre_usdc = float(b.get("uiTokenAmount",{}).get("uiAmount",0) or 0)
    for b in meta.get("postTokenBalances", []):
        if b.get("mint") == USDC_MINT:
            post_usdc = float(b.get("uiTokenAmount",{}).get("uiAmount",0) or 0)
    
    usdc_change = post_usdc - pre_usdc
    
    # If USDC appeared from nowhere (not a token sale, not a swap)
    # This means an external deposit
    if usdc_change > 5 and abs(our_sol_change) < 0.001:
        external_usdc_funding += usdc_change
        if not first_deposit_found:
            print(f"FIRST DEPOSIT: ${usdc_change:.2f} USDC slot={sig_info['slot']}")
            first_deposit_found = True

print(f"\n=== WHAT ENTERED THE WALLET ===")
print(f"SOL deposits from external: {external_sol_funding:.4f} SOL (${external_sol_funding*170:.2f})")
print(f"Fees paid: {total_fees} lamports ({total_fees/1e9:.4f} SOL)")
print(f"USDC from external deposits: ${external_usdc_funding:.2f}")
print(f"Total $ in: ${external_sol_funding*170 + external_usdc_funding:.2f}")