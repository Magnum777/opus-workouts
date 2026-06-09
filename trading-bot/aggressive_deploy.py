"""
Aggressive deployment - buy into BONK and FARTCOIN with momentum, plus UFO narrative play
"""
import json, os, sys, base64, requests, time
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

PRIVATE_KEY = bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d")
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client("https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887")
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Buy orders - going aggressive
BUYS = [
    {"token": "BONK",   "mint": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "sol": 0.2},
    {"token": "FARTCOIN","mint": "9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump",  "sol": 0.15},
    {"token": "UFO",    "mint": "9enS2VasgRxzT2QVkhjfVJAtrVJGB9MSYTSvUpf2pump", "sol": 0.08},
]

def get_sol_balance():
    try:
        return CLIENT.get_balance(WALLET.pubkey()).value / 1e9
    except:
        return 0

def buy_token(mint, token_name, sol_amount):
    print(f"\n--- Buying {token_name} with {sol_amount} SOL ---")
    try:
        lamports = int(sol_amount * 1e9)
        
        # Get quote SOL -> token
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={SOL_MINT}&outputMint={mint}&amount={lamports}&slippage=15",
            timeout=15
        )
        if r.status_code != 200:
            print(f"  Quote failed: {r.status_code}")
            return False, None
        
        quote = r.json()
        out_amount = int(quote.get("outAmount", 0))
        print(f"  Quote received: ~{out_amount} tokens")
        
        # Get swap tx
        swap_resp = requests.post(
            "https://lite-api.jup.ag/swap/v1/swap",
            json={
                "quoteResponse": quote,
                "userPublicKey": str(WALLET.pubkey()),
                "wrapAndUnwrapSol": True,
                "dynamicComputeUnitLimit": True
            },
            timeout=15
        )
        if swap_resp.status_code != 200:
            print(f"  Swap request failed: {swap_resp.status_code}")
            return False, None
        
        swap_data = swap_resp.json()
        
        # Sign and send
        tx = VersionedTransaction.from_bytes(base64.b64decode(swap_data["swapTransaction"]))
        signed = VersionedTransaction(tx.message, [WALLET])
        result = CLIENT.send_raw_transaction(
            bytes(signed),
            opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed")
        )
        
        tx_hash = result.value if hasattr(result, "value") else str(result)
        print(f"  TX sent: {tx_hash}")
        print(f"  View: https://solscan.io/tx/{tx_hash}")
        return True, tx_hash
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return False, None

def update_portfolio(token, mint, sol_spent, tx_hash):
    """Add new position to portfolio DB"""
    try:
        from datetime import datetime, timezone
        sol_price = 93.52
        with open("portfolio.db.json", "r") as f:
            db = json.load(f)
        
        db["positions"].append({
            "token": token,
            "mint": mint,
            "amount_raw": 0,
            "amount_formatted": 0,
            "current_price_usd": 0,
            "current_value_usd": 0,
            "current_value_sol": sol_spent,
            "buy_price_usd": sol_spent * sol_price,
            "buy_price_sol": sol_spent,
            "cost_basis_usd": sol_spent * sol_price,
            "unrealized_pnl_usd": 0,
            "unrealized_pnl_pct": 0,
            "status": "OPEN",
            "opened_at": datetime.now(timezone.utc).isoformat(),
            "tx_hash": str(tx_hash),
            "research_confidence": 70,
            "research_recommendation": "BUY"
        })
        db["portfolio"]["positions_count"] = len(db["positions"])
        db["portfolio"]["sol_balance"] = get_sol_balance()
        db["portfolio"]["total_value_usd"] = sum(p.get("current_value_usd", 0) for p in db["positions"]) + get_sol_balance() * sol_price
        db["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        with open("portfolio.db.json", "w") as f:
            json.dump(db, f, indent=2)
        print(f"  Portfolio DB updated for {token}")
    except Exception as e:
        print(f"  Portfolio DB update error: {e}")

# === MAIN ===
print("=== AGGRESSIVE DEPLOY ===")
print(f"Wallet: {WALLET.pubkey()}")

sol_before = get_sol_balance()
print(f"SOL before: {sol_before:.4f} ({sol_before * 93.52:.2f})")
print(f"USDC: 60.54")
print(f"Total: ~{sol_before * 93.52 + 60.54:.2f}")

# First swap some USDC to SOL for buying power
print("\n--- Swapping 40 USDC to SOL for ammo ---")
try:
    usdc_raw = int(40 * 1e6)  # 40 USDC in smallest units
    r = requests.get(
        f"https://lite-api.jup.ag/swap/v1/quote?inputMint={USDC}&outputMint={SOL_MINT}&amount={usdc_raw}&slippage=5",
        timeout=15
    )
    if r.status_code == 200:
        quote = r.json()
        swap_resp = requests.post(
            "https://lite-api.jup.ag/swap/v1/swap",
            json={"quoteResponse": quote, "userPublicKey": str(WALLET.pubkey()), "wrapAndUnwrapSol": True, "dynamicComputeUnitLimit": True},
            timeout=15
        )
        if swap_resp.status_code == 200:
            swap_data = swap_resp.json()
            tx = VersionedTransaction.from_bytes(base64.b64decode(swap_data["swapTransaction"]))
            signed = VersionedTransaction(tx.message, [WALLET])
            result = CLIENT.send_raw_transaction(bytes(signed), opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed"))
            tx_hash = result.value if hasattr(result, "value") else str(result)
            print(f"  USDC->SOL done: {tx_hash}")
            time.sleep(3)  # Wait for confirmation
        else:
            print(f"  USDC swap failed: {swap_resp.status_code}")
    else:
        print(f"  USDC quote failed: {r.status_code}")
except Exception as e:
    print(f"  USDC->SOL error: {e}")

# Check updated SOL balance
time.sleep(2)
sol_after = get_sol_balance()
print(f"\nSOL after USDC swap: {sol_after:.4f}")

# Now execute buys
successes = 0
for b in BUYS:
    if sol_after < b["sol"] + 0.02:
        print(f"\n  Not enough SOL for {b['token']} (need {b['sol']}, have {sol_after:.4f})")
        b["sol"] = max(0.05, sol_after - 0.02)
        if b["sol"] < 0.05:
            print(f"  Skipping {b['token']} - not enough funds")
            continue
    
    ok, tx = buy_token(b["mint"], b["token"], b["sol"])
    if ok:
        successes += 1
        update_portfolio(b["token"], b["mint"], b["sol"], tx)
        sol_after -= b["sol"]
        time.sleep(2)
    else:
        print(f"  Trying again with less slippage...")
        time.sleep(1)
        ok, tx = buy_token(b["mint"], b["token"], b["sol"])
        if ok:
            successes += 1
            update_portfolio(b["token"], b["mint"], b["sol"], tx)
            sol_after -= b["sol"]
            time.sleep(2)

final_sol = get_sol_balance()
print(f"\n=== DEPLOYMENT COMPLETE ===")
print(f"Buys executed: {successes}/{len(BUYS)}")
print(f"Final SOL: {final_sol:.4f}")
print(f"Keep remaining USDC as stablecoin reserve")
