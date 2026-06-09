#!/usr/bin/env python3
"""Emergency sell: dump BONK open position and TRUMP if needed"""
import json, sys, os, base64, time, requests
sys.path.insert(0, os.path.dirname(__file__))

import portfolio_db_v2 as pdb
from risk_manager import BLOCKED_TOKENS

from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# Wallet
PRIVATE_KEY = bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d")
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client("https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887")

USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

def sell_token(mint, amount_raw, token_name):
    """Execute sell via Jupiter, token -> USDC"""
    for attempt in range(3):
        try:
            r = requests.get(
                f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount={amount_raw}&slippage=15",
                timeout=15
            )
            if r.status_code == 200:
                break
            time.sleep(2)
        except:
            time.sleep(2)
    else:
        print(f"FAILED: Could not get quote for {token_name}")
        return False
    
    quote = r.json()
    
    for swap_attempt in range(3):
        try:
            swap_resp = requests.post(
                "https://lite-api.jup.ag/swap/v1/swap",
                json={
                    "quoteResponse": quote,
                    "userPublicKey": str(WALLET.pubkey()),
                    "wrapAndUnwrapSol": True,
                    "prioritizationFeeLamports": 5000
                },
                timeout=30
            )
            if swap_resp.status_code == 200:
                break
            time.sleep(3)
        except:
            time.sleep(3)
    else:
        print(f"FAILED: Swap request for {token_name}")
        return False
    
    swap_data = swap_resp.json()
    tx = VersionedTransaction.from_bytes(base64.b64decode(swap_data["swapTransaction"]))
    signed = VersionedTransaction(tx.message, [WALLET])
    
    for send_attempt in range(3):
        try:
            result = CLIENT.send_raw_transaction(
                bytes(signed),
                opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed")
            )
            tx_hash = result.value if hasattr(result, "value") else str(result)
            time.sleep(2)
            print(f"SOLD {token_name}: TX {str(tx_hash)[:20]}...")
            return tx_hash
        except Exception as e:
            err = str(e)
            if "429" in err:
                time.sleep(3)
                continue
            print(f"Sell error for {token_name}: {str(e)[:100]}")
            return False
    return False

# Load portfolio
db = pdb.load_db()
usdc_balance = 0  # Will sync after sells

# Find open BONK positions
bonk_mint = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
for pos in db.get("positions", []):
    if pos.get("status") == "OPEN" and pos.get("mint") == bonk_mint:
        amount_raw = pos.get("amount_raw", 0)
        value = pos.get("current_value_usd", 0)
        pnl = pos.get("unrealized_pnl_pct", 0)
        print(f"SELLING BONK: {value:.2f} USD | PnL {pnl:+.1f}%")
        tx = sell_token(bonk_mint, amount_raw, "BONK")
        if tx:
            pdb.close_position("BONK", {
                "close_price_usd": value,
                "close_value_usd": value,
                "tx_hash": str(tx)
            })
            trade = {
                "token": "BONK",
                "action": "SELL",
                "reason": "FORCED_SELL (blocklist)",
                "amount_usd": value,
                "pnl_usd": value - pos.get("cost_basis_usd", 0),
                "pnl_pct": pnl,
                "tx_hash": str(tx),
                "mint": bonk_mint
            }
            pdb.add_trade(trade)

# Check remaining open positions
print("\n=== REMAINING OPEN POSITIONS ===")
for pos in db.get("positions", []):
    if pos.get("status") == "OPEN":
        print(f"  {pos['token']}: ${pos.get('current_value_usd',0):.2f} | PnL {pos.get('unrealized_pnl_pct',0):+.1f}%")
