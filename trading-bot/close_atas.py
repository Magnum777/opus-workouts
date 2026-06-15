#!/usr/bin/env python3
"""Close all EMPTY token accounts to reclaim rent. Keep USDC ATA.
Corrections: track program ownership per-account, use correct close ix."""
import json, requests, time, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.message import Message
from solders.transaction import Transaction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

WALLET = Keypair.from_bytes(bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d"))
H = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
C = Client(H)
WS = str(WALLET.pubkey())

USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
PROGRAMS = {
    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA": "Token",
    "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb": "Token-2022",
}

print("=== Checking all token accounts ===")
closeable = []
kept = []

for prog_id_str, prog_name in PROGRAMS.items():
    prog_pk = Pubkey.from_string(prog_id_str)
    r = requests.post(H, json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [WS, {"programId": prog_id_str}, {"encoding": "jsonParsed"}]
    }, timeout=10).json()
    for a in r.get("result", {}).get("value", []):
        pk = a.get("pubkey", "")
        info = a["account"]["data"]["parsed"]["info"]
        mint = info.get("mint", "")
        amt = float(info.get("tokenAmount", {}).get("uiAmount", 0) or 0)
        lamports = a["account"]["lamports"]
        
        if amt > 0 and mint == USDC_MINT:
            kept.append((pk, mint, amt, lamports, prog_id_str))
            print(f"  KEEP: {pk[:20]}.. USDC balance={amt} rent={lamports}")
        elif amt > 0:
            kept.append((pk, mint, amt, lamports, prog_id_str))
            print(f"  DUST: {pk[:20]}.. mint={mint[:15]}.. balance={amt} rent={lamports} [{prog_name}] — SKIPPED (non-zero)")
        else:
            closeable.append((pk, mint, lamports, prog_pk))
            print(f"  CLOSE: {pk[:20]}.. mint={mint[:15]}.. rent={lamports} [{prog_name}]")

total_reclaimable = sum(l for _, _, l, _ in closeable)
print(f"\nCloseable: {len(closeable)} accounts")
print(f"Total reclaimable: {total_reclaimable} lamports ({total_reclaimable/1e9:.4f} SOL)")
if total_reclaimable == 0:
    print("No accounts to close. Nothing to do.")
    print("\n=== Final ===")
    print(f"Nothing changed.")
    sys.exit(0)

# Batch close in groups of 5
batches = [closeable[i:i+5] for i in range(0, len(closeable), 5)]
print(f"Batches: {len(batches)}\n")

closed_count = 0
for i, batch in enumerate(batches):
    print(f"Batch {i+1}/{len(batches)} ({len(batch)} accounts)...")
    
    instructions = []
    for pk, mint, _, prog_pk in batch:
        close_ix = Instruction(
            program_id=prog_pk,
            accounts=[
                AccountMeta(Pubkey.from_string(pk), False, True),
                AccountMeta(WALLET.pubkey(), False, True),
                AccountMeta(WALLET.pubkey(), True, False),
            ],
            data=bytes([9])
        )
        instructions.append(close_ix)
    
    for attempt in range(4):
        try:
            bh = C.get_latest_blockhash(commitment="processed").value.blockhash
            msg = Message(instructions, WALLET.pubkey())
            tx = Transaction([WALLET], msg, bh)
            result = C.send_transaction(tx, opts=TxOpts(skip_preflight=True, max_retries=5))
            print(f"  TX: {result.value}")
            closed_count += len(batch)
            break
        except Exception as e:
            err = str(e)
            if "429" in err:
                print(f"  Rate limited (attempt {attempt+1}), waiting 10s...")
                time.sleep(10)
                continue
            if "Blockhash not found" in err:
                print(f"  Blockhash expired, retry {attempt+1}...")
                time.sleep(1)
                continue
            if "invalid account data" in err:
                print(f"  Skipping: {err[:120]}")
                break
            if "custom program error: 0xb" in err:
                print(f"  Skipping (token still has balance?): {err[:120]}")
                break
            if attempt < 3:
                print(f"  Err (attempt {attempt+1}): {err[:120]}")
                time.sleep(3)
            else:
                print(f"  Give up: {err[:120]}")
    time.sleep(2)

time.sleep(2)

# Get accurate starting balance from chain
print("\n=== Getting final balance ===")
final_resp = C.get_balance(WALLET.pubkey())
final_bal = final_resp.value if hasattr(final_resp, 'value') else final_resp
final_sol = final_bal / 1e9

print(f"\n=== Results ===")
print(f"Accounts closed (attempted): {closed_count}")
print(f"Final SOL balance: {final_sol:.6f}")
print(f"Done")