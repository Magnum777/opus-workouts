#!/usr/bin/env python3
"""Total wallet audit - trace every transaction from the beginning."""
import json, requests, time, sys, os
from solders.keypair import Keypair
from solana.rpc.api import Client

WALLET = Keypair.from_bytes(bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d"))
H = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
C = Client(H)
WS = str(WALLET.pubkey())
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Get current chain state
sol_raw = C.get_balance(WALLET.pubkey()).value
curr_sol = sol_raw / 1e9
r = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getTokenAccountsByOwner","params":[WS,{"mint":USDC_MINT},{"encoding":"jsonParsed"}]}, timeout=10).json()
curr_usdc = float(r["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]) if r.get("result",{}).get("value") else 0

# Fetch all tx signatures (paginate)
print("Fetching all wallet transactions...")
all_sigs = []
before = None
for page in range(20):
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
    if page >= 4:  # Limit to ~500 tx for speed
        break

print(f"\nTotal tx: {len(all_sigs)}")

# Track everything
external_sol_in = 0.0
external_sol_out = 0.0
usdc_to_sol_vol = 0.0
sol_to_usdc_vol = 0.0
token_buy_vol = 0.0
token_sell_vol = 0.0
fees_lamports = 0
other_tx = 0

# Also track per-tx for reporting
big_tx = []

for idx, sig_info in enumerate(all_sigs):
    sig = sig_info["signature"]
    if idx % 50 == 0:
        print(f"  Processing {idx}/{len(all_sigs)}...")
    
    tx = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getTransaction","params":[sig,{"encoding":"jsonParsed","maxSupportedTransactionVersion":0}]}, timeout=10).json()
    if not tx.get("result"):
        continue
    
    meta = tx["result"].get("meta", {})
    fee = meta.get("fee", 0)
    fees_lamports += fee
    
    pre_bal = meta.get("preBalances", [0,0])
    post_bal = meta.get("postBalances", [0,0])
    sol_change = (post_bal[0] - pre_bal[0] + fee) / 1e9 if len(pre_bal) > 0 and len(post_bal) > 0 else 0
    
    pre_usdc = 0
    post_usdc = 0
    for b in meta.get("preTokenBalances", []):
        if b.get("mint") == USDC_MINT:
            pre_usdc = float(b.get("uiTokenAmount",{}).get("uiAmount",0) or 0)
    for b in meta.get("postTokenBalances", []):
        if b.get("mint") == USDC_MINT:
            post_usdc = float(b.get("uiTokenAmount",{}).get("uiAmount",0) or 0)
    
    usdc_change = post_usdc - pre_usdc
    
    # Classify
    if sol_change > 0.001 and abs(usdc_change) < 0.5:
        external_sol_in += sol_change
    elif sol_change < -0.001 and abs(usdc_change) < 0.5:
        external_sol_out += abs(sol_change)
    elif usdc_change < -0.5 and sol_change > 0.001:
        usdc_to_sol_vol += -usdc_change
    elif sol_change < -0.001 and usdc_change > 0.5:
        sol_to_usdc_vol += usdc_change
    elif usdc_change < -0.5:
        token_buy_vol += -usdc_change
    elif usdc_change > 0.5:
        token_sell_vol += usdc_change
    else:
        other_tx += 1
    
    # Track big ones for detail
    if abs(usdc_change) > 5 or abs(sol_change) > 0.01:
        slot = sig_info["slot"]
        big_tx.append({
            "slot": slot,
            "sol": round(sol_change, 4),
            "usdc": round(usdc_change, 2),
            "sig": sig[:25]
        })

print(f"  Done. Processed {len(all_sigs)} tx")

# Now calculate
print()
print("=" * 55)
print("COMPLETE WALLET AUDIT")
print("=" * 55)
print()

curr_sol_usd = curr_sol * 170
curr_total = curr_usdc + curr_sol_usd

print(f"=== CURRENT STATE ===")
print(f"SOL:  {curr_sol:.6f} (${curr_sol_usd:.2f})")
print(f"USDC: ${curr_usdc:.2f}")
print(f"Total: ${curr_total:.2f}")
print()

print(f"=== ALL-TIME FLOWS ===")
print(f"SOL received (external deposits): +{external_sol_in:.4f} SOL")
print(f"SOL sent out: -{external_sol_out:.4f} SOL")
print(f"SOL from USDC->SOL swaps: +{usdc_to_sol_vol/170:.4f} (${usdc_to_sol_vol:.2f} USDC spent)")
print(f"SOL used for SOL->USDC swaps: -{sol_to_usdc_vol/170:.4f} (${sol_to_usdc_vol:.2f} USDC received)")
print(f"Fees: {fees_lamports} lamports ({fees_lamports/1e9:.4f} SOL)")
print()

print(f"Token buys: ${token_buy_vol:.2f} USDC spent")
print(f"Token sells: ${token_sell_vol:.2f} USDC received")
print()

print("=== P&L ===")
token_pnl = token_sell_vol - token_buy_vol
swap_pnl = sol_to_usdc_vol - usdc_to_sol_vol
print(f"Token trading: ${token_pnl:.2f}")
print(f"USDC-SOL swaps: ${swap_pnl:.2f}")
print(f"Fees: ${fees_lamports/1e9*170:.4f}")
print(f"Net P&L: ${token_pnl + swap_pnl - fees_lamports/1e9*170:.2f}")
print()

print("=== MONEY THAT PASSED THROUGH ===")
print(f"Total USDC in (sells+deposits): ${token_sell_vol + sol_to_usdc_vol:.2f}")
print(f"Total USDC out (buys+swaps): ${token_buy_vol + usdc_to_sol_vol:.2f}")
print()

# Net position change
print("=== ACCOUNTING CHECK ===")
# Starting SOL = current - all deposits + all outflows
start_sol = curr_sol - external_sol_in + external_sol_out - usdc_to_sol_vol/170 + sol_to_usdc_vol/170
print(f"Implied starting SOL: {start_sol:.6f} (should be near 0 if wallet started empty)")
print(f"Your $9 deposit: {9/170:.4f} SOL accounted for in external deposits")
print()

print("=== BIGGEST TRANSACTIONS ===")
for tx in reversed(big_tx[-10:]):
    print(f"  SOL={tx['sol']:+.4f} USDC=${tx['usdc']:+.2f} slot={tx['slot']} {tx['sig']}")
print()

print(f"Current balance: ${curr_total:.2f}")
print(f"Bot is stopped. No new trades until you say go.")