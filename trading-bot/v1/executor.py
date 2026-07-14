#!/usr/bin/env python3
"""
TradeBot-Nova Executor Module - LIVE TRADING
5-minute trade execution with Jupiter API, tax logging
"""

import json
import os
import base64
import requests
from datetime import datetime, timezone
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# Import unified portfolio database
import portfolio_db as pdb

# Wallet configuration
PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client(os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"))

# Token constants
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"
TOKEN2022_PROGRAM = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"

# Trading parameters (from old system)
TAKE_PROFIT_PCT = 1.0    # 1% take profit
STOP_LOSS_PCT = -1.0     # 1% stop loss
MAX_POSITIONS = 6
BUY_SIZE_SOL = 0.20
COOLDOWN_SCANS = 6       # Scans before re-buying sold token

# Known tokens
KNOWN_TOKENS = {
    "PUMP": "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn",
    "FART": "9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump",
    "PENGU": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv",
    "TRUMP": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
    "GIGA": "63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoaggixuT4Byifb9T8qbtPas",
    "WIF": "85VBFQZC9TZkfaptBWqv14ALD9fJNUKtWA41kh69teRP",
    "POPCAT": "7xKXtg2CW87d97TXJSDpbD5jBkheotQbM2MyWGkErQgB",
    "MOODENG": "Moodeng5zS4Zs2Dq3bFJBjtFAY4xqKc9w1EqR4XP2S3Dq",
    "GOAT": "CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump",
    "HONK": "3ag1M9QJK91mXJtVvHaKq7hWwWQzw6q4oVZunLLAoqNZ",
    "PIPPIN": "GScX7cE5PxLkGrSjK3xwRJrYwKpV7MEmFgH2yFrhQGqm",
}

# File paths
QUEUE_FILE = "trading-queue.json"
TRADE_LOG = "trade-history.json"
TAX_LOG = "tax-log.json"
POSITIONS_FILE = "positions.json"
COOLDOWN_FILE = "trade-cooldowns.json"

def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r') as f:
            return json.load(f)
    return {"pending": [], "executed": [], "rejected": []}

def save_queue(queue):
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

def load_positions():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, 'r') as f:
            return json.load(f)
    return {"positions": []}

def save_positions(positions):
    with open(POSITIONS_FILE, 'w') as f:
        json.dump(positions, f, indent=2)

def load_cooldowns():
    if os.path.exists(COOLDOWN_FILE):
        with open(COOLDOWN_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cooldowns(cooldowns):
    with open(COOLDOWN_FILE, 'w') as f:
        json.dump(cooldowns, f, indent=2)

def log_trade(trade):
    """Log trade to trade-history.json AND unified portfolio DB"""
    # Legacy logging
    trades = []
    if os.path.exists(TRADE_LOG):
        with open(TRADE_LOG, 'r') as f:
            try:
                trades = json.load(f)
            except:
                trades = []
    trades.append(trade)
    with open(TRADE_LOG, 'w') as f:
        json.dump(trades, f, indent=2)
    
    # New: Unified portfolio DB logging
    pdb.add_trade(trade)

def log_tax_event(trade):
    """DEPRECATED: Tax logging now handled in portfolio_db.add_trade()"""
    # Tax events are automatically logged when trades are added to portfolio DB
    pass

def get_token_price(mint):
    """Get token price in USDC via Jupiter"""
    try:
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount=1000000&slippage=1",
            timeout=8
        )
        if r.status_code == 200:
            return float(r.json()["outAmount"]) / 1e6
        return 0
    except:
        return 0

def execute_sell_live(mint, token_name, amount_raw):
    """Execute real sell via Jupiter"""
    try:
        # Get Jupiter quote
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={SOL_MINT}&amount={amount_raw}&slippage=15",
            timeout=15
        )
        if r.status_code != 200:
            return False, "Quote failed"
        
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
            return False, "Swap request failed"
        
        swap_data = swap_resp.json()
        
        # Sign and send transaction
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

def execute_buy_live(mint, token_name, sol_amount):
    """Execute real buy via Jupiter"""
    try:
        lamports = int(sol_amount * 1e9)
        
        # Get Jupiter quote
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={SOL_MINT}&outputMint={mint}&amount={lamports}&slippage=10",
            timeout=15
        )
        if r.status_code != 200:
            return False, "Quote failed"
        
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
            return False, "Swap request failed"
        
        swap_data = swap_resp.json()
        
        # Sign and send transaction
        tx = VersionedTransaction.from_bytes(base64.b64decode(swap_data["swapTransaction"]))
        signed = VersionedTransaction(tx.message, [WALLET])
        result = CLIENT.send_raw_transaction(
            bytes(signed),
            opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed")
        )
        
        tx_hash = result.value if hasattr(result, "value") else str(result)
        return True, str(tx_hash)
        
    except Exception as e:
        return False, str(e)

def process_sell_signal(signal):
    """Process sell signal with live execution using ACTUAL blockchain amount"""
    token = signal["token"]
    mint = signal.get("mint", KNOWN_TOKENS.get(token, ""))
    
    # Get amount from signal (which came from actual blockchain holdings in scout)
    amount_raw = signal.get("amount_raw", 0)
    if amount_raw == 0:
        return False, "No amount to sell (not in wallet?)"
    
    # Execute sell
    success, result = execute_sell_live(mint, token, amount_raw)
    
    if success:
        # Calculate P&L from signal data
        buy_price = signal.get("buy_price_sol", 0)
        current_value = signal.get("current_value_sol", 0)
        pnl_pct = signal.get("pnl_pct", 0)
        
        trade = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "token": token,
            "action": "SELL",
            "reason": signal.get("reason", "SIGNAL"),
            "amount_raw": amount_raw,
            "pnl_pct": pnl_pct,
            "tx_hash": str(result),
            "mint": mint
        }
        
        log_trade(trade)
        log_tax_event(trade)
        
        # CLOSE POSITION IN UNIFIED DB
        close_data = {
            "close_price_usd": signal.get("current_value_usd", 0),
            "close_value_usd": signal.get("current_value_usd", 0),
            "tx_hash": str(result)
        }
        pdb.close_position(token, close_data)
        
        # Add to cooldown
        cooldowns = load_cooldowns()
        cooldowns[token] = COOLDOWN_SCANS
        save_cooldowns(cooldowns)
        
        return True, f"SOLD {token} | P&L: {pnl_pct:+.2f}% | TX: {str(result)[:20]}..."
    else:
        return False, f"Sell failed: {result}"

def process_buy_signal(signal):
    """Process buy signal with live execution"""
    token = signal["token"]
    mint = signal.get("mint", KNOWN_TOKENS.get(token, ""))
    
    if not mint:
        return False, "No mint address for token"
    
    # Execute buy via Jupiter
    success, result = execute_buy_live(mint, token, BUY_SIZE_SOL)
    
    if success:
        trade = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "token": token,
            "action": "BUY",
            "amount_sol": BUY_SIZE_SOL,
            "tx_hash": str(result),
            "mint": mint
        }
        
        log_trade(trade)
        
        # Add to unified portfolio database
        pdb.add_position({
            "token": token,
            "mint": mint,
            "amount_raw": 0,  # Will be updated by scout
            "current_price_usd": 0,  # Will be updated
            "current_value_usd": 0,
            "current_value_sol": BUY_SIZE_SOL,
            "buy_price_usd": 0,  # Will be updated
            "buy_price_sol": BUY_SIZE_SOL,
            "cost_basis_usd": 0,  # Will be updated
            "unrealized_pnl_usd": 0,
            "unrealized_pnl_pct": 0,
            "status": "OPEN",
            "tx_hash": str(result)
        })
        
        # Add to positions (will be updated with actual values on next scout scan)
        positions_data = load_positions()
        positions = positions_data.get("positions", [])
        
        new_position = {
            "token": token,
            "mint": mint,
            "buy_price_sol": BUY_SIZE_SOL,
            "buy_tx": str(result),
            "status": "OPEN",
            "bought_at": datetime.now(timezone.utc).isoformat()
        }
        
        positions.append(new_position)
        save_positions({"positions": positions})
        
        return True, f"BOUGHT {token} | {BUY_SIZE_SOL} SOL | TX: {str(result)[:20]}..."
    else:
        return False, f"Buy failed: {result}"


def main():
    """Main executor routine"""
    print(f"[{datetime.now(timezone.utc).isoformat()}] === TRADEBOT EXECUTOR ===")
    print(f"Wallet: {WALLET.pubkey()}")
    
    queue = load_queue()
    pending = queue.get("pending", [])
    
    if not pending:
        print("Status: No pending trades")
        print("=" * 40)
        return
    
    print(f"Pending Signals: {len(pending)}")
    
    executed = []
    rejected = []
    
    for signal in pending:
        action = signal.get("action", "UNKNOWN")
        token = signal.get("token", "UNKNOWN")
        print(f"Processing: {action} {token}")
        
        if action == "SELL":
            success, msg = process_sell_signal(signal)
            if success:
                executed.append(signal)
                print(f"  [EXECUTED] {msg}")
            else:
                rejected.append({**signal, "error": msg})
                print(f"  [FAILED] {msg}")
        else:
            # Buy signals - execute buy
            success, msg = process_buy_signal(signal)
            if success:
                executed.append(signal)
                print(f"  [EXECUTED] {msg}")
            else:
                rejected.append({**signal, "error": msg})
                print(f"  [FAILED] {msg}")
    
    # Update queue
    queue["pending"] = []
    queue["executed"].extend(executed)
    queue["rejected"].extend(rejected)
    save_queue(queue)
    
    print(f"Results: {len(executed)} executed, {len(rejected)} rejected")
    print("=" * 40)

if __name__ == "__main__":
    main()
