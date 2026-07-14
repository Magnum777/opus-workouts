#!/usr/bin/env python3
"""
TradeBot V2 Executor
Research-driven execution with risk management
"""

import json
import os
import sys
import base64
import time
import requests
from datetime import datetime, timezone

# Import V2 modules
sys.path.insert(0, os.path.dirname(__file__))
import portfolio_db_v2 as pdb
from risk_manager import check_trade_allowed, record_trade, MAX_OPEN_POSITIONS, MAX_POSITION_PCT
from research_v2 import TOKENS

# Solana imports
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# RPC
from rpc_config import get_rpc

# Wallet
PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client(get_rpc())

# Constants
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


def get_jupiter_price(mint, decimals=None):
    """Get token price via Jupiter. Returns price per 1 full token in USD."""
    for attempt in range(3):
        try:
            if decimals is None:
                decimals = 9 if mint == SOL_MINT else 6
            amount = 10 ** decimals  # 1 full token in smallest units
            r = requests.get(
                f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount={amount}&slippage=1",
                timeout=8
            )
            if r.status_code == 200:
                return float(r.json()["outAmount"]) / 1e6  # USDC has 6 decimals
            elif r.status_code == 429:
                time.sleep(2)
                continue
        except:
            pass
        break
    return 0

# Trading params
BUY_SIZE_SOL = 0.2  # Conservative buy size

def dynamic_buy_size(portfolio_value, confidence):
    """Scale buy size: more confident = bigger bet, up to 0.5 SOL.
    
    - 50+ conf: 0.3 SOL (core plays)
    - 70+ conf: 0.4 SOL (high conviction)
    - 85+ conf: 0.5 SOL (max conviction)
    - Below 50: 0.15 SOL (exploratory)
    Also caps at MAX_POSITION_PCT of portfolio.
    """
    if confidence >= 85:
        size = 0.5
    elif confidence >= 70:
        size = 0.4
    elif confidence >= 50:
        size = 0.3
    else:
        size = 0.15
    
    # Respect max position size as % of portfolio
    sol_price = get_jupiter_price(SOL_MINT) or 75
    proposed_usd = size * sol_price
    max_position_usd = portfolio_value * MAX_POSITION_PCT
    if proposed_usd > max_position_usd:
        size = max_position_usd / sol_price
    
    return round(size, 2)


    """Get token price via Jupiter. Returns price per 1 full token in USD."""
    try:
        if decimals is None:
            decimals = 9 if mint == SOL_MINT else 6
        amount = 10 ** decimals  # 1 full token in smallest units
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount={amount}&slippage=1",
            timeout=8
        )
        if r.status_code == 200:
            return float(r.json()["outAmount"]) / 1e6  # USDC has 6 decimals
    except:
        pass
    return 0


def execute_buy_live(mint, token_name, sol_amount):
    """Execute buy via Jupiter"""
    try:
        lamports = int(sol_amount * 1e9)
        
        # Get quote with retry and detailed logging
        def fetch_quote(slippage_bps=1500):
            try:
                resp = requests.get(
                    f"https://lite-api.jup.ag/swap/v1/quote?inputMint={SOL_MINT}&outputMint={mint}&amount={lamports}&slippage={slippage_bps/100}",
                    timeout=15
                )
                if resp.status_code == 200:
                    return resp.json(), None
                else:
                    return None, f"Quote HTTP {resp.status_code}: {resp.text[:200]}"
            except Exception as e:
                return None, f"Quote exception: {e}"
        
        quote, err = fetch_quote()
        if err:
            # Try with higher slippage as fallback
            print(f"Initial quote failed: {err}. Retrying with 20% slippage.")
            quote, err = fetch_quote(slippage_bps=2000)
            if err:
                print(f"Fallback quote also failed: {err}")
                return False, "Quote failed"
        
        # Debug output: show received quote summary
        print(f"Quote received: inAmount={quote.get('inAmount')} outAmount={quote.get('outAmount')} slippageBps={quote.get('slippageBps')}")        
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

def execute_sell_live(mint, token_name, amount_raw):
    """Execute sell via Jupiter"""
    try:
        # Get quote (token -> USDC)
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount={amount_raw}&slippage=15",
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

def process_sell_signal(signal):
    """Process sell with risk checks"""
    token = signal["token"]
    mint = signal.get("mint", "")
    
    # Get position
    position = pdb.get_position(token)
    if not position:
        return False, "No position found"
    
    amount_raw = position.get("amount_raw", 0)
    if amount_raw == 0:
        return False, "No amount to sell"
    
    # Check risk
    portfolio_value = pdb.load_db()["portfolio"]["total_value_usd"]
    position_value = position.get("current_value_usd", 0)
    
    allowed, reason = check_trade_allowed(token, "SELL", portfolio_value, position_value)
    if not allowed:
        return False, f"Risk check failed: {reason}"
    
    # Execute sell
    success, result = execute_sell_live(mint, token, amount_raw)
    
    if success:
        # Calculate P&L
        buy_price = position.get("buy_price_usd", 0)
        current_value = signal.get("current_value_usd", position_value)
        pnl_usd = current_value - buy_price
        pnl_pct = (pnl_usd / buy_price * 100) if buy_price > 0 else 0
        
        # Record trade
        trade = {
            "token": token,
            "action": "SELL",
            "reason": signal.get("reason", "SIGNAL"),
            "amount_raw": amount_raw,
            "amount_usd": current_value,
            "pnl_usd": pnl_usd,
            "pnl_pct": pnl_pct,
            "tx_hash": str(result),
            "mint": mint
        }
        
        pdb.add_trade(trade)
        
        # Close position in DB
        pdb.close_position(token, {
            "close_price_usd": current_value,
            "close_value_usd": current_value,
            "tx_hash": str(result)
        })
        
        # Record for risk tracking
        record_trade(token, "SELL", pnl_usd)
        
        return True, f"SOLD {token} | P&L: ${pnl_usd:+.2f} ({pnl_pct:+.1f}%) | TX: {str(result)[:20]}..."
    else:
        return False, f"Sell failed: {result}"

def process_buy_signal(signal):
    """Process buy with risk checks"""
    token = signal["token"]
    mint = signal.get("mint", "")
    
    if not mint:
        return False, "No mint address"
    
    # Check risk
    db = pdb.load_db()
    portfolio_value = db["portfolio"]["total_value_usd"]
    current_position = pdb.get_position(token)
    position_value = current_position.get("current_value_usd", 0) if current_position else 0
    
    allowed, reason = check_trade_allowed(token, "BUY", portfolio_value, position_value)
    if not allowed:
        return False, f"Risk check failed: {reason}"
    
    # Execute buy — scale size by confidence
    confidence = signal.get("confidence", 70)
    buy_amount = dynamic_buy_size(portfolio_value, confidence)
    success, result = execute_buy_live(mint, token, buy_amount)
    
    if success:
        # Add to DB
        trade = {
            "token": token,
            "action": "BUY",
            "amount_sol": buy_amount,
            "tx_hash": str(result),
            "mint": mint
        }
        
        pdb.add_trade(trade)
        
        # Add position (will be updated with actual values on next scout)
        pdb.add_position({
            "token": token,
            "mint": mint,
            "amount_raw": 0,
            "current_price_usd": 0,
            "current_value_usd": 0,
            "current_value_sol": BUY_SIZE_SOL,
            "buy_price_usd": 0,
            "buy_price_sol": BUY_SIZE_SOL,
            "cost_basis_usd": 0,
            "unrealized_pnl_usd": 0,
            "unrealized_pnl_pct": 0,
            "status": "OPEN",
            "tx_hash": str(result)
        })
        
        record_trade(token, "BUY")
        
        return True, f"BOUGHT {token} | {buy_amount} SOL | conf {confidence} | TX: {str(result)[:20]}..."
    else:
        return False, f"Buy failed: {result}"

def main():
    """Main executor routine"""
    print(f"[{datetime.now(timezone.utc).isoformat()}] === V2 EXECUTOR ===")
    print(f"Wallet: {WALLET.pubkey()}")

    # Load pending signals from queue
    pending_path = os.path.join(os.path.dirname(__file__), "trading-queue.json")
    try:
        with open(pending_path, "r") as f:
            queue = json.load(f)
    except Exception as e:
        print(f"Failed to load pending queue: {e}")
        queue = {"pending": []}

    # Process ALL pending signals (BUY + SELL)
    executed_tokens = set()
    for signal in list(queue.get("pending", [])):
        action = signal.get("action")
        token = signal.get("token")
        
        if action == "SELL":
            if token in executed_tokens:
                continue  # already sold in this run
            success, msg = process_sell_signal(signal)
            print(msg)
            if success:
                executed_tokens.add(token)
                queue["pending"].remove(signal)
                queue.setdefault("executed", []).append(signal)
        elif action == "BUY":
            mint = signal.get("mint") or TOKENS.get(token, {}).get("mint")
            if not mint:
                print(f"No mint found for {token}, skipping")
                continue
            success, msg = process_buy_signal(signal)
            print(msg)
            if success:
                queue["pending"].remove(signal)
                queue.setdefault("executed", []).append(signal)

    # Write back updated queue
    try:
        with open(pending_path, "w") as f:
            json.dump(queue, f, indent=2)
        print(f"[QUEUE] Updated: {len(queue.get('pending', []))} pending / {len(queue.get('executed', []))} executed")
    except Exception as e:
        print(f"Failed to write updated queue: {e}")

    # Load DB for status reporting and auto-threshold checks
    db = pdb.load_db()
    risk = db.get("risk_metrics", {})

    today = datetime.now(timezone.utc).isoformat()[:10]
    daily_count = risk.get("daily_trade_count", 0) if risk.get("daily_trade_reset") == today else 0

    print(f"Daily Trades: {daily_count}/10")
    print(f"Status: {'PAUSED' if risk.get('consecutive_losses', 0) >= 3 else 'ACTIVE'}")

    # Auto-check open positions for TP/SL thresholds (belt + suspenders)
    sol_price = get_jupiter_price(SOL_MINT) or 92
    print(f"\n[THRESHOLD CHECK] Checking open positions for auto-exits...")
    for pos in db.get("positions", []):
        if pos.get("status") != "OPEN":
            continue
        token = pos["token"]
        mint = pos.get("mint", "")
        cost = pos.get("cost_basis_usd", pos.get("buy_price_usd", 0))
        current_value = pos.get("current_value_usd", 0)
        raw = pos.get("amount_raw", 0)
        
        if cost <= 0 or raw == 0 or token in executed_tokens:
            print(f"  {token}: ${current_value:.2f} (skipped)")
            continue
        
        pnl_pct = ((current_value - cost) / cost) * 100 if cost > 0 else 0
        
        # Live refresh price
        decimals = pos.get("decimals", 6)
        live_price = get_jupiter_price(mint, decimals=decimals)
        if live_price > 0:
            live_value = live_price * raw / 1e6
            live_pnl_pct = ((live_value - cost) / cost) * 100 if cost > 0 else 0
            print(f"  {token}: ${live_value:.2f} (PnL: {live_pnl_pct:+.1f}%)")
            
            if live_pnl_pct >= 25.0:
                print(f"  >> TAKE PROFIT triggered at +{live_pnl_pct:.1f}% (threshold: +25%)")
                sig = {"token": token, "mint": mint, "current_value_usd": live_value, "reason": "TAKE_PROFIT"}
                success, msg = process_sell_signal(sig)
                print(f"  {msg}")
                executed_tokens.add(token)
            elif live_pnl_pct <= -8.0:
                print(f"  >> STOP LOSS triggered at {live_pnl_pct:.1f}% (threshold: -8%)")
                sig = {"token": token, "mint": mint, "current_value_usd": live_value, "reason": "STOP_LOSS"}
                success, msg = process_sell_signal(sig)
                print(f"  {msg}")
                executed_tokens.add(token)
            else:
                print(f"  >> Held (within threshold bounds)")
        else:
            print(f"  {token}: no price data, using DB value ${current_value:.2f}")

    print("=" * 50)

if __name__ == "__main__":
    main()
