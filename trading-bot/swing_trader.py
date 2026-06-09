#!/usr/bin/env python3
"""
TradeBot V2 - Momentum Swing Trader with Auto-Execution
Captures multiple 3-5% swings instead of waiting for 10% moves
"""

import json
import os
import sys
import base64
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
import portfolio_db_v2 as pdb
from momentum_trader import (
    generate_momentum_signals, 
    generate_dip_buy_signals,
    record_price,
    get_jupiter_price
)

# Solana
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

PRIVATE_KEY = bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d")
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client("https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887")

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Conservative position sizes
BUY_SIZE_SOL = 0.15  # Slightly smaller for more frequent trades
MAX_POSITIONS = 4    # Max tokens to hold at once

def execute_buy(mint, token_name, sol_amount):
    """Execute buy via Jupiter"""
    try:
        lamports = int(sol_amount * 1e9)
        
        # Get quote
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={SOL_MINT}&outputMint={mint}&amount={lamports}&slippage=10",
            timeout=15
        )
        if r.status_code != 200:
            return False, f"Quote failed: {r.status_code}"
        
        quote = r.json()
        
        # Get swap transaction
        swap_resp = requests.post(
            "https://lite-api.jup.ag/swap/v1/swap",
            json={
                "quoteResponse": quote,
                "userPublicKey": str(WALLET.pubkey()),
                "wrapAndUnwrapSol": True
            },
            timeout=15
        )
        
        if swap_resp.status_code != 200:
            return False, f"Swap request failed: {swap_resp.status_code}"
        
        swap_data = swap_resp.json()
        
        # Sign and send
        tx = VersionedTransaction.from_bytes(base64.b64decode(swap_data["swapTransaction"]))
        signed = VersionedTransaction(tx.message, [WALLET])
        result = CLIENT.send_raw_transaction(
            bytes(signed),
            opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed")
        )
        
        tx_hash = result.value if hasattr(result, "value") else str(result)
        return True, tx_hash
        
    except Exception as e:
        return False, str(e)

def execute_sell(mint, token_name, amount_raw):
    """Execute sell via Jupiter"""
    try:
        # Get quote (token -> USDC)
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount={amount_raw}&slippage=10",
            timeout=15
        )
        if r.status_code != 200:
            return False, f"Quote failed: {r.status_code}"
        
        quote = r.json()
        
        # Get swap transaction
        swap_resp = requests.post(
            "https://lite-api.jup.ag/swap/v1/swap",
            json={
                "quoteResponse": quote,
                "userPublicKey": str(WALLET.pubkey()),
                "wrapAndUnwrapSol": True
            },
            timeout=15
        )
        
        if swap_resp.status_code != 200:
            return False, f"Swap request failed: {swap_resp.status_code}"
        
        swap_data = swap_resp.json()
        
        # Sign and send
        tx = VersionedTransaction.from_bytes(base64.b64decode(swap_data["swapTransaction"]))
        signed = VersionedTransaction(tx.message, [WALLET])
        result = CLIENT.send_raw_transaction(
            bytes(signed),
            opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed")
        )
        
        tx_hash = result.value if hasattr(result, "value") else str(result)
        return True, tx_hash
        
    except Exception as e:
        return False, str(e)

def process_momentum_trade(signal):
    """Execute a momentum-based trade"""
    token = signal["token"]
    mint = signal.get("mint", "")
    action = signal["action"]
    reason = signal.get("reason", "UNKNOWN")
    
    print(f"\n[EXECUTING] {action} {token}")
    print(f"  Reason: {reason}")
    
    if action == "BUY":
        # Check position limits
        db = pdb.load_db()
        open_positions = sum(1 for p in db.get("positions", []) if p.get("status") == "OPEN")
        
        if open_positions >= MAX_POSITIONS:
            print(f"  SKIP: Max positions ({MAX_POSITIONS}) reached")
            return False, "Max positions reached"
        
        # Check SOL balance
        sol_balance = CLIENT.get_balance(WALLET.pubkey()).value / 1e9
        if sol_balance < BUY_SIZE_SOL + 0.01:  # Leave 0.01 for fees
            print(f"  SKIP: Insufficient SOL ({sol_balance:.4f} < {BUY_SIZE_SOL + 0.01:.4f})")
            return False, "Insufficient SOL"
        
        # Execute buy
        success, result = execute_buy(mint, token, BUY_SIZE_SOL)
        
        if success:
            print(f"  SUCCESS: TX {result[:20]}...")
            # Record in portfolio DB
            pdb.add_position(token, mint, BUY_SIZE_SOL, signal.get("current_price", 0))
            return True, result
        else:
            print(f"  FAILED: {result}")
            return False, result
    
    elif action == "SELL":
        # Get position
        position = pdb.get_position(token)
        if not position:
            print(f"  SKIP: No position found for {token}")
            return False, "No position"
        
        amount_raw = position.get("amount_raw", 0)
        if amount_raw == 0:
            print(f"  SKIP: No amount to sell")
            return False, "No amount"
        
        # Execute sell
        success, result = execute_sell(mint, token, amount_raw)
        
        if success:
            print(f"  SUCCESS: TX {result[:20]}...")
            # Update position in DB
            pdb.close_position(token, signal.get("current_price", 0), signal.get("pnl_pct", 0))
            return True, result
        else:
            print(f"  FAILED: {result}")
            return False, result
    
    return False, "Unknown action"

def main():
    """Main swing trader routine"""
    print(f"[{datetime.now(timezone.utc).isoformat()}] === MOMENTUM SWING TRADER ===")
    print(f"Wallet: {WALLET.pubkey()}")
    print(f"Strategy: Capture 3-5% swings, tight stops")
    print()
    
    # Get current portfolio state
    db = pdb.load_db()
    sol_balance = CLIENT.get_balance(WALLET.pubkey()).value / 1e9
    sol_price = get_jupiter_price(SOL_MINT) or 84
    
    print(f"SOL Balance: {sol_balance:.4f} SOL (${sol_balance * sol_price:.2f})")
    print(f"Open Positions: {len([p for p in db.get('positions', []) if p.get('status') == 'OPEN'])}")
    print()
    
    # Generate signals
    print("[SCANNING] Generating momentum signals...")
    sell_signals = generate_momentum_signals()
    buy_signals = generate_dip_buy_signals()
    all_signals = sell_signals + buy_signals
    
    if not all_signals:
        print("[RESULT] No momentum signals detected")
        return
    
    print(f"[SIGNALS] {len(all_signals)} signals found:\n")
    for sig in all_signals:
        print(f"  {sig['action']} {sig['token']}: {sig['reason']}")
        if 'pnl_pct' in sig:
            print(f"    P&L: {sig['pnl_pct']:+.2f}%")
        if 'current_price' in sig:
            print(f"    Price: ${sig['current_price']:.6f}")
        print()
    
    # Execute trades
    print("[EXECUTING] Processing trades...")
    executed = []
    failed = []
    
    for signal in all_signals:
        success, result = process_momentum_trade(signal)
        if success:
            executed.append({
                "token": signal["token"],
                "action": signal["action"],
                "reason": signal["reason"],
                "tx_hash": result
            })
        else:
            failed.append({
                "token": signal["token"],
                "action": signal["action"],
                "reason": result
            })
    
    # Summary
    print(f"\n[SUMMARY]")
    print(f"  Executed: {len(executed)}")
    print(f"  Failed: {len(failed)}")
    
    if executed:
        print(f"\n  Successful trades:")
        for trade in executed:
            print(f"    {trade['action']} {trade['token']} - {trade['tx_hash'][:16]}...")
    
    if failed:
        print(f"\n  Failed trades:")
        for trade in failed:
            print(f"    {trade['action']} {trade['token']} - {trade['reason']}")
    
    # Save summary
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signals_found": len(all_signals),
        "executed": len(executed),
        "failed": len(failed),
        "trades": executed + failed
    }
    
    summary_file = os.path.join(os.path.dirname(__file__), "swing_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n[LOG] Summary saved to swing_summary.json")

if __name__ == "__main__":
    main()
