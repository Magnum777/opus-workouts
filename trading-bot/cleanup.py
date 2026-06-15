#!/usr/bin/env python3
"""
TradeBot Full Cleanup & Sync
1. Close ALL dead token ATAs (non-USDC with no Jupiter liquidity)
2. Sync portfolio.db.json from live chain state
3. Clean up old redundant db/json files
4. Remove stale log cruft
"""
import json, os, sys, requests, time, glob, shutil
sys.path.insert(0, os.path.dirname(__file__))
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.message import Message
from solders.transaction import Transaction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from datetime import datetime, timezone

DIR = os.path.dirname(__file__)
WALLET = Keypair.from_bytes(bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d"))
H = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
C = Client(H)
WS = str(WALLET.pubkey())

USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
TOKEN_PROG = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
TOKENZ_PROG = Pubkey.from_string("TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb")

# ═══════════════════════════════════════════
# STEP 1: Check chain state
# ═══════════════════════════════════════════
print("=== STEP 1: Check chain state ===")
sol_raw = C.get_balance(WALLET.pubkey()).value
sol = sol_raw / 1e9
print(f"SOL: {sol:.6f} ({sol_raw} lamports)")

# Get all token accounts
all_token_accts = {}
for prog_id, prog_label in [(str(TOKEN_PROG), "Tokenkeg"), (str(TOKENZ_PROG), "TokenzQd")]:
    r = requests.post(H, json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [WS, {"programId": prog_id}, {"encoding": "jsonParsed"}]
    }, timeout=10).json()
    for a in r.get("result", {}).get("value", []):
        pk = a.get("pubkey", "")
        info = a["account"]["data"]["parsed"]["info"]
        mint = info.get("mint", "")
        amt = float(info.get("tokenAmount", {}).get("uiAmount", 0) or 0)
        lamports = a["account"]["lamports"]
        all_token_accts[pk] = {"mint": mint, "amount": amt, "lamports": lamports, "program": prog_label}

print(f"Total token accounts: {len(all_token_accts)}")

# Categorize
usdc_acct = None
dust_accts = []
empty_accts = []
for pk, info in all_token_accts.items():
    if info["mint"] == USDC_MINT and info["amount"] > 0:
        usdc_acct = pk
        print(f"  USDC ATA: {pk[:20]}.. ${info['amount']:.2f} (rent: {info['lamports']})")
    elif info["amount"] > 0:
        dust_accts.append({"pk": pk, **info})
        print(f"  DUST: {pk[:20]}.. {info['mint'][:20]} = {info['amount']} (rent: {info['lamports']})")
    elif info["amount"] == 0:
        empty_accts.append({"pk": pk, **info})
        print(f"  EMPTY: {pk[:20]}.. {info['mint'][:20]} (rent: {info['lamports']})")

# ═══════════════════════════════════════════
# STEP 2: Check if dust has any Jupiter liquidity
# ═══════════════════════════════════════════
print(f"\n=== STEP 2: Check dust liquidity ===")
worthwhile_dust = []
worthless_dust = []
for d in dust_accts:
    try:
        p = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={d['mint']}&outputMint={USDC_MINT}&amount=1000000&slippage=50", timeout=10).json()
        if "outAmount" in p:
            val = float(p["outAmount"]) / 1e6
        else:
            p2 = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={USDC_MINT}&outputMint={d['mint']}&amount=1000000&slippage=50", timeout=10).json()
            val = float(p2.get("outAmount", 0)) / 1e6 if "outAmount" in p2 else 0
        
        total_val = val * d['amount'] / 1_000_000
        if total_val > 0.05:
            worthwhile_dust.append(d)
            print(f"  {d['mint'][:20]}.. = ${total_val:.4f} — worth selling")
        else:
            worthless_dust.append(d)
            print(f"  {d['mint'][:20]}.. = ${total_val:.4f} — worthless, close for rent")
    except:
        worthless_dust.append(d)
        print(f"  {d['mint'][:20]}.. = $0 — no price, close for rent")

# ═══════════════════════════════════════════
# STEP 3: Close worthless dust + empty ATAs
# ═══════════════════════════════════════════
print(f"\n=== STEP 3: Close {len(worthless_dust)} dust + {len(empty_accts)} empty ATAs ===")
close_targets = []
for d in worthless_dust:
    close_targets.append(d)
for e in empty_accts:
    close_targets.append(e)

total_reclaim = sum(t["lamports"] for t in close_targets)
print(f"Would reclaim {total_reclaim} lamports ({total_reclaim/1e9:.4f} SOL ~=${total_reclaim/1e9*170:.2f})")

# Close in batches of 4 to avoid TX size issues
for i in range(0, len(close_targets), 4):
    batch = close_targets[i:i+4]
    print(f"  Batch {i//4+1} ({len(batch)} accounts)...")
    
    instructions = []
    for t in batch:
        prog = TOKENZ_PROG if t.get("program") == "TokenzQd" else TOKEN_PROG
        close_ix = Instruction(
            program_id=prog,
            accounts=[
                AccountMeta(Pubkey.from_string(t["pk"]), False, True),
                AccountMeta(WALLET.pubkey(), False, True),
                AccountMeta(WALLET.pubkey(), True, False),
            ],
            data=bytes([9])
        )
        instructions.append(close_ix)
    
    try:
        bh = C.get_latest_blockhash(commitment="finalized").value
        msg = Message(instructions, WALLET.pubkey())
        tx = Transaction([WALLET], msg, bh)
        result = C.send_transaction(tx, opts=TxOpts(skip_preflight=False, max_retries=3))
        print(f"    TX: {result.value}")
        time.sleep(3)
        
        for _ in range(5):
            time.sleep(1)
            c = C.get_signature_statuses([result.value])
            if c and c.value and c.value[0]:
                s = c.value[0]
                if s.confirmation_status:
                    print(f"    Confirmed!")
                    break
                elif s.err:
                    print(f"    Failed: {s.err}")
                    break
    except Exception as e:
        print(f"    Error: {str(e)[:100]}")
        if "429" in str(e):
            time.sleep(10)

# ═══════════════════════════════════════════
# STEP 4: Sell worthwhile dust if any
# ═══════════════════════════════════════════
print(f"\n=== STEP 4: Sell worthwhile dust ===")
for d in worthwhile_dust:
    # Sell via Jupiter
    raw_amt = int(d["amount"] * (10**9))  # assume 9 decimals
    q = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={d['mint']}&outputMint={USDC_MINT}&amount={raw_amt}&slippage=5", timeout=10).json()
    if "routePlan" in q:
        sw = requests.post("https://lite-api.jup.ag/swap/v1/swap", json={
            "quoteResponse": q, "userPublicKey": WS, "wrapAndUnwrapSol": False,
        }, timeout=30).json()
        from solders.transaction import VersionedTransaction
        tx = VersionedTransaction.from_bytes(__import__('base64').b64decode(sw["swapTransaction"]))
        signed = VersionedTransaction(tx.message, [WALLET])
        result = C.send_raw_transaction(bytes(signed), opts=TxOpts(skip_preflight=True, max_retries=3))
        print(f"  Sold {d['mint'][:20]}.. TX: {result.value}")
        time.sleep(10)

# ═══════════════════════════════════════════
# STEP 5: Sync DB
# ═══════════════════════════════════════════
print(f"\n=== STEP 5: Sync DB ===")
time.sleep(3)
sol_raw = C.get_balance(WALLET.pubkey()).value
sol = sol_raw / 1e9

r = requests.post(H, json={
    "jsonrpc": "2.0", "id": 1,
    "method": "getTokenAccountsByOwner",
    "params": [WS, {"mint": USDC_MINT}, {"encoding": "jsonParsed"}]
}, timeout=10).json()
accts = r.get("result", {}).get("value", [])
usdc = float(accts[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]) if accts else 0

db_path = os.path.join(DIR, "portfolio.db.json")
with open(db_path) as f:
    db = json.load(f)

# Fix corrupted HfMbPyDdZH entry
for t in db.get("trades", []):
    if t.get("token") == "HfMbPyDdZH" and abs(t.get("pnl_usd", 0)) > 100:
        t["pnl_usd"] = 0.0
        t["pnl_pct"] = 0.0

# Update portfolio
db["portfolio"]["sol_balance"] = sol
db["portfolio"]["sol_price_usd"] = 170
db["portfolio"]["usdc_balance"] = usdc
db["portfolio"]["total_value_usd"] = usdc + (sol * 170)
db["portfolio"]["positions_count"] = 0

# Recalculate realized PnL
total_pnl = sum(t.get("pnl_usd", 0) for t in db.get("trades", []))
db["performance"]["total_realized_pnl"] = total_pnl
db["performance"]["win_count"] = len([t for t in db.get("trades", []) if t.get("pnl_usd", 0) > 0])
db["performance"]["loss_count"] = len([t for t in db.get("trades", []) if t.get("pnl_usd", 0) < 0])
db["last_updated"] = datetime.now(timezone.utc).isoformat()

with open(db_path, "w") as f:
    json.dump(db, f, indent=2)

print(f"DB synced: SOL={sol:.4f} USDC=${usdc:.2f} Total=${db['portfolio']['total_value_usd']:.2f}")
print(f"Realized PnL: ${total_pnl:.2f} ({db['performance']['win_count']}W / {db['performance']['loss_count']}L)")

# ═══════════════════════════════════════════
# STEP 6: Clean up old duplicate files
# ═══════════════════════════════════════════
print(f"\n=== STEP 6: Clean up old files ===")
# Remove duplicates of the same data in old formats
to_delete = [
    "positions.json", "positions_enforced.json", "trading_state.json",
    "trades.json", "state.json", "latest_decision.json",
    "daemon_out.json", "daemon_output.json", "solana_balance.json",
    "solana_trades.json", "solana_wallet.json", "tax-log.json",
    "trade_journal.json", "portfolio_state.json",
    "portfolio_tracker.json", "scout-log.json",
    "health_log.json", "api_usage.json",
]
deleted = 0
for f in to_delete:
    fp = os.path.join(DIR, f)
    if os.path.exists(fp):
        os.remove(fp)
        deleted += 1
        print(f"  Removed: {f}")

# Old .db files that are duplicates
old_db = ["portfolio.db", "portfolio_check.db", "portfolio_history.db", 
          "portfolio_tracker.db", "portfolio_tracking.db",
          "trades.db", "tradebot.db", "trading.db", "trading_bot.db", "snapshots.db"]
for f in old_db:
    fp = os.path.join(DIR, f)
    if os.path.exists(fp) and os.path.getsize(fp) == 0:
        os.remove(fp)
        deleted += 1
        print(f"  Removed empty: {f}")

# Clean old log files
log_dir = os.path.join(DIR, "logs")
if os.path.exists(log_dir):
    for f in os.listdir(log_dir):
        fp = os.path.join(log_dir, f)
        age = time.time() - os.path.getmtime(fp)
        if age > 86400 * 7:  # older than 7 days
            os.remove(fp)
            deleted += 1
    print(f"  Cleaned old log files")

# Also clean up old .txt and .log in root (older than 3 days)
for ext in ['*.txt', '*.log']:
    for f in glob.glob(os.path.join(DIR, ext)):
        base = os.path.basename(f)
        if base in ['trading-queue.json']:
            continue
        age = time.time() - os.path.getmtime(f)
        if age > 86400 * 3:  # older than 3 days
            try:
                os.remove(f)
                deleted += 1
                print(f"  Removed old: {base}")
            except:
                pass

print(f"\nRemoved {deleted} old files")

# ═══════════════════════════════════════════
# FINAL REPORT
# ═══════════════════════════════════════════
time.sleep(3)
sol_raw = C.get_balance(WALLET.pubkey()).value
sol = sol_raw / 1e9

r = requests.post(H, json={
    "jsonrpc": "2.0", "id": 1,
    "method": "getTokenAccountsByOwner",
    "params": [WS, {"mint": USDC_MINT}, {"encoding": "jsonParsed"}]
}, timeout=10).json()
accts = r.get("result", {}).get("value", [])
usdc = float(accts[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]) if accts else 0

# Count remaining token accounts
remaining_progs = {}
for prog_id, prog_label in [(str(TOKEN_PROG), "Tokenkeg"), (str(TOKENZ_PROG), "TokenzQd")]:
    r = requests.post(H, json={
        "jsonrpc": "2.0", "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [WS, {"programId": prog_id}, {"encoding": "jsonParsed"}]
    }, timeout=10).json()
    remaining_progs[prog_label] = len(r.get("result", {}).get("value", []))

# Also check the empty {} method
r3 = requests.post(H, json={
    "jsonrpc": "2.0", "id": 1,
    "method": "getTokenAccountsByOwner",
    "params": [WS, {}, {"encoding": "jsonParsed"}]
}, timeout=10).json()

print(f"\n{'='*50}")
print(f"CLEANUP COMPLETE")
print(f"{'='*50}")
print(f"SOL:  {sol:.4f} (${sol*170:.2f})")
print(f"USDC: ${usdc:.2f}")
print(f"Total: ${usdc + sol*170:.2f}")
print(f"Tokenkeg accounts: {remaining_progs.get('Tokenkeg', 0)}")
print(f"TokenzQd accounts: {remaining_progs.get('TokenzQd', 0)}")
print(f"(empty-query method returned {len(r3.get('result',{}).get('value',[]))} — Helius quirk still there)")
print(f"Gas status: {'GREEN' if sol >= 0.003 else 'CRITICAL'}")
print(f"Realized PnL: ${total_pnl:.2f}")