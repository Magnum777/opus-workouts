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

# Load secrets from .env (never commit secrets)
def _load_env_file(path):
    """Parse KEY=VALUE lines from a .env file into os.environ."""
    if not os.path.exists(path):
        return
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

_load_env_file(os.path.join(os.path.dirname(__file__), '.env'))

# Import V2 modules
sys.path.insert(0, os.path.dirname(__file__))
import portfolio_db_v2 as pdb
from risk_manager import check_trade_allowed, record_trade, record_sell_cooldown
from risk_manager import STOP_LOSS_PCT, TAKE_PROFIT_PCT, TRIM_PCT, TRIM_FRACTION
from risk_manager import TRAILING_ACTIVATE_PCT, TRAILING_DISTANCE_PCT
from risk_manager import update_trailing_stop, get_trailing_stop_info
from research_v2 import TOKENS

# Solana imports
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# Wallet
PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
HELIUS_RPC = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")
CLIENT = Client(HELIUS_RPC)

# Constants
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# SOL gas: self-sustaining reserve
#   Target = 3% of portfolio in SOL (up from 2% for safety margin)
#   Floor = 0.015 SOL (never go below this)
#   Ceiling = 0.05 SOL (never hoard more)
#   Refill triggers at 60% of target (earlier than 50%)
#   Refill capped at 8% of USDC per cycle (up from 5%)
#   Daily hard cap: 0.015 SOL max on fees (up from 0.01)
#   Gas tax: 2% of every profitable trade goes to gas reserve
SOL_TARGET_PCT = 0.03           # 3% of portfolio in SOL for gas
SOL_TARGET_FLOOR = 0.015        # minimum 0.015 SOL
SOL_TARGET_CEILING = 0.05       # never hold more than 0.05 SOL
SOL_REFILL_TRIGGER = 0.60       # refill when below 60% of target
SOL_REFILL_CAP_PCT = 0.08       # max 8% of USDC per refill
SOL_DAILY_BUDGET = 0.015        # max 0.015 SOL/day on fees (~$1)
SOL_MIN_SAFE = 0.005            # below this, emergency pause
SOL_GAS_TAX_PCT = 0.02          # 2% of every profitable trade -> gas reserve

GAS_LOG = os.path.join(os.path.dirname(__file__), "gas_tracker.json")
GAS_RESERVE_FILE = os.path.join(os.path.dirname(__file__), ".gas_reserve.json")

# Trading params - used by daemon and executor
BUY_SIZES = [4.0, 8.0, 12.0]  # Legacy, unused - sizing now in determine_buy_size()
# Strategy: %-based sizing scaled to current capital
#   Survival ($0-$15):    60% on one target
#   Dig-out ($15-$30):    45%
#   Rebuild ($30-$60):    40% strong / 25% medium / 15% base
#   Standard ($60+):      flat caps ($15/$12/$10)
# SINGLE POSITION: Max 1 open position at a time


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
                # Rate limited - wait 2s and retry
                time.sleep(2)
                continue
        except:
            pass
        break
    return 0


def get_sol_balance():
    """Get SOL balance from blockchain"""
    try:
        result = CLIENT.get_balance(WALLET.pubkey())
        if hasattr(result, "value"):
            return result.value / 1e9
    except:
        pass
    return 0


# ── Cycle-level 429 cooldown ──
_429_COOLDOWN_FILE = os.path.join(os.path.dirname(__file__), ".jupiter_429_cooldown.json")

def _load_429_cooldown():
    """Check if we're in a 429 cooldown window. Returns remaining seconds."""
    try:
        with open(_429_COOLDOWN_FILE) as f:
            data = json.load(f)
        expires = data.get("expires_at", 0)
        remaining = expires - time.time()
        if remaining > 0:
            return remaining
    except:
        pass
    return 0

def _mark_429_hit():
    """Store a 10-min cooldown so next cycles also know to back off."""
    try:
        with open(_429_COOLDOWN_FILE, "w") as f:
            json.dump({"expires_at": time.time() + 600}, f)
    except:
        pass

def _respectful_quote(input_mint, output_mint, amount, slippage_bps=1500, label="quote"):
    """Jupiter quote with cycle-aware backoff. Returns (quote_json, error_str) or (None, reason)."""
    cd = _load_429_cooldown()
    if cd > 0:
        return None, f"429 cooldown active ({cd:.0f}s remaining)"
    
    cooldown_gate = _load_429_cooldown()
    if cooldown_gate > 0:
        return None, f"Cycle 429 cooldown ({cooldown_gate:.0f}s)"
    
    for attempt in range(3):
        try:
            resp = requests.get(
                f"https://lite-api.jup.ag/swap/v1/quote?inputMint={input_mint}&outputMint={output_mint}&amount={amount}&slippage={slippage_bps/100}",
                timeout=15
            )
            if resp.status_code == 200:
                return resp.json(), None
            elif resp.status_code == 429:
                _mark_429_hit()
                wait = 5 + (5 * attempt)
                print(f"Rate limited (429) on {label}, retry {attempt+1}/3 in {wait}s")
                time.sleep(wait)
                continue
            else:
                return None, f"Quote HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            if attempt < 2:
                print(f"Quote exception on {label} ({attempt+1}/3): {e}, retrying in 5s...")
                time.sleep(5)
                continue
            return None, f"Quote exception: {e}"
    return None, "Quote failed after 3 retries"

def _respectful_swap(quote, user_pk_str, wrap_sol=False, label="swap"):
    """Jupiter swap with cycle-aware backoff."""
    cd = _load_429_cooldown()
    if cd > 0:
        return None, f"429 cooldown active ({cd:.0f}s)"
    
    for attempt in range(3):
        try:
            resp = requests.post(
                "https://lite-api.jup.ag/swap/v1/swap",
                json={
                    "quoteResponse": quote,
                    "userPublicKey": user_pk_str,
                    "wrapAndUnwrapSol": wrap_sol,
                    "prioritizationFeeLamports": 10000,
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json(), None
            elif resp.status_code == 429:
                _mark_429_hit()
                wait = 5 + (5 * attempt)
                print(f"Swap rate limited (429) on {label}, retry {attempt+1}/3 in {wait}s")
                time.sleep(wait)
                continue
            else:
                return None, f"Swap HTTP {resp.status_code} {resp.text[:150]}"
        except Exception as e:
            if attempt < 2:
                print(f"Swap POST error ({attempt+1}/3): {e}, retrying in 5s...")
                time.sleep(5)
                continue
            return None, f"Swap error: {e}"
    return None, "Swap failed after 3 retries"

def get_gas_reserve():
    """Get the tracked gas reserve balance (separate from wallet SOL).
    This is a virtual tracker — the actual SOL is in the wallet.
    """
    try:
        if os.path.exists(GAS_RESERVE_FILE):
            with open(GAS_RESERVE_FILE) as f:
                data = json.load(f)
            return data.get("reserve_sol", 0)
    except:
        pass
    return 0

def add_to_gas_reserve(amount_sol):
    """Add SOL to the gas reserve from trade profits."""
    if amount_sol <= 0:
        return
    try:
        reserve = get_gas_reserve()
        reserve += amount_sol
        with open(GAS_RESERVE_FILE, "w") as f:
            json.dump({"reserve_sol": reserve, "updated": time.time()}, f, indent=2)
        print(f"[GAS RESERVE] +{amount_sol:.6f} SOL (total: {reserve:.6f})")
    except:
        pass

def get_daily_gas_spent():
    """Get total SOL spent on fees today."""
    try:
        if os.path.exists(GAS_LOG):
            with open(GAS_LOG) as f:
                log = json.load(f)
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            return log.get(today, 0)
    except:
        pass
    return 0

def log_gas_spent(cycle_start_sol, cycle_end_sol):
    """Track SOL spent this cycle."""
    spent = cycle_start_sol - cycle_end_sol
    if spent > 0.000001:  # ignore dust
        try:
            log = {}
            if os.path.exists(GAS_LOG):
                with open(GAS_LOG) as f:
                    log = json.load(f)
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            log[today] = log.get(today, 0) + spent
            with open(GAS_LOG, "w") as f:
                json.dump(log, f, indent=2)
            if spent > 0.001:
                print(f"[GAS WARNING] Cycle burned {spent:.6f} SOL — high!")
        except:
            pass

def ensure_sol_for_gas():
    """
    Self-sustaining SOL gas reserve.
    Refills from USDC when below trigger.
    Daily hard cap prevents runaway fee drain.
    Gas reserve tracks virtual SOL set aside from profits.
    """
    sol_bal = get_sol_balance()
    sol_price = get_jupiter_price(SOL_MINT)
    if sol_price <= 0:
        sol_price = 170
    usdc_bal = get_usdc_balance()
    total_value = usdc_bal + (sol_bal * sol_price)
    gas_reserve = get_gas_reserve()

    # Calculate target: 3% of portfolio, bounded
    target_sol = max(SOL_TARGET_FLOOR, min(SOL_TARGET_CEILING, total_value * SOL_TARGET_PCT / sol_price))

    # Emergency check: if SOL is below MIN_SAFE, pause everything
    if sol_bal < SOL_MIN_SAFE:
        print(f"[GAS EMERGENCY] SOL at {sol_bal:.6f} — below MIN_SAFE ({SOL_MIN_SAFE})!")
        print(f"[GAS EMERGENCY] Attempting emergency refill...")
        # Try a bigger refill (20% of USDC) to get back to safe
        if usdc_bal > 2.0:
            refill = min(usdc_bal * 0.20, 5.0)  # up to 20% of USDC or $5
            success, msg = execute_buy_live(SOL_MINT, "SOL", refill)
            if success:
                new_sol = get_sol_balance()
                print(f"[GAS EMERGENCY] Refilled! {sol_bal:.6f} → {new_sol:.6f} SOL")
                return True
            else:
                print(f"[GAS EMERGENCY] Refill failed: {msg}")
        print(f"[GAS EMERGENCY] Cannot refill — wallet stuck until SOL is sent")
        return False

    # Check if we need refill
    if sol_bal >= target_sol * SOL_REFILL_TRIGGER:
        return False  # plenty of gas

    # Check daily budget
    daily_spent = get_daily_gas_spent()
    if daily_spent >= SOL_DAILY_BUDGET:
        print(f"[GAS] Daily budget reached ({daily_spent:.6f}/{SOL_DAILY_BUDGET} SOL) — pausing refills until tomorrow")
        return False

    # Calculate refill amount
    deficit_sol = target_sol - sol_bal
    deficit_usd = deficit_sol * sol_price
    max_refill = usdc_bal * SOL_REFILL_CAP_PCT
    refill_amount = min(deficit_usd, max_refill)

    if refill_amount < 0.50:  # skip if less than $0.50
        return False

    print(f"[SOL GAS] {sol_bal:.6f} SOL (target {target_sol:.4f}, reserve {gas_reserve:.6f}). Refilling ${refill_amount:.2f} USDC → SOL...")

    success, msg = execute_buy_live(SOL_MINT, "SOL", refill_amount)
    if success:
        new_sol = get_sol_balance()
        print(f"[SOL GAS] Refilled! {sol_bal:.6f} → {new_sol:.6f} SOL")
    else:
        print(f"[SOL GAS] Refill failed: {msg}")
    return True


def refill_usdc_from_sol():
    """REMOVED — selling gas for trading capital creates a death spiral.
    If USDC is low, the bot waits for a trade to close instead.
    """
    return False


def get_usdc_balance():
    """Get USDC balance from blockchain"""
    try:
        helius_url = HELIUS_RPC
        data = {
            "jsonrpc": "2.0", "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                str(WALLET.pubkey()),
                {"mint": USDC},
                {"encoding": "jsonParsed"}
            ]
        }
        resp = requests.post(helius_url, json=data, headers={"Content-Type": "application/json"}, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            accounts = result.get("result", {}).get("value", [])
            if accounts:
                amount = float(accounts[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"] or 0)
                return amount
    except Exception as e:
        print(f"Failed to get USDC balance: {e}")
    return 0


def execute_buy_live(mint, token_name, usdc_amount):
    """Execute buy via Jupiter v2 API (handles Token-2022)"""
    usdc_units = int(usdc_amount * 1e6)

    # Use Jupiter v2 API
    try:
        resp = requests.get(
            f"https://api.jup.ag/swap/v2/order?inputMint={USDC}&outputMint={mint}&amount={usdc_units}&slippageBps=5000&taker={str(WALLET.pubkey())}&dynamicBlockhash=true",
            timeout=15
        )
        if resp.status_code != 200:
            return False, f"v2 order failed: HTTP {resp.status_code}"
        data = resp.json()
        if data.get("errorCode"):
            return False, f"v2 order error: {data.get('errorMessage', 'unknown')}"
        tx_b64 = data.get("transaction")
        if not tx_b64:
            return False, "No transaction in v2 response"
        out_amount = data.get("outAmount", "?")
        print(f"v2 order: inAmount={data.get('inAmount')} outAmount={out_amount} slippageBps={data.get('slippageBps')}")
    except Exception as e:
        return False, f"v2 order exception: {e}"

    tx = VersionedTransaction.from_bytes(base64.b64decode(tx_b64))
    signed = VersionedTransaction(tx.message, [WALLET])

    _PENDING_TX_FILE = os.path.join(os.path.dirname(__file__), ".pending_buy_tx.json")

    for send_attempt in range(3):
        try:
            result = CLIENT.send_raw_transaction(
                bytes(signed),
                opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed", max_retries=5)
            )
            tx_hash = result.value if hasattr(result, "value") else str(result)
            time.sleep(3)
            confirmed = False
            for verify_attempt in range(30):
                try:
                    confirm = CLIENT.get_signature_statuses([str(tx_hash)])
                    if confirm and confirm.value and confirm.value[0]:
                        status = confirm.value[0]
                        if status.confirmation_status:
                            confirmed = True
                            print(f"TX confirmed: {str(tx_hash)[:20]}... status={status.confirmation_status}")
                            break
                        elif status.err:
                            print(f"TX failed on-chain: {status.err}")
                            return False, f"TX failed on-chain: {status.err}"
                except:
                    pass
                time.sleep(1)

            if not confirmed:
                # Fallback: check if balance actually changed
                print(f"TX {str(tx_hash)[:20]}... not confirmed via status API - checking balance...")
                try:
                    from scout_v2 import get_usdc_balance
                    time.sleep(2)
                    post_usdc = get_usdc_balance()
                    if post_usdc < usdc_amount - 0.50:  # USDC decreased = buy went through
                        confirmed = True
                        print(f"TX confirmed via balance change: USDC {usdc_amount:.2f} -> {post_usdc:.2f}")
                except:
                    pass
                if send_attempt < 2:
                    print(f"TX {str(tx_hash)[:20]}... did not confirm after ~35s - retrying once in 10s")
                    time.sleep(10)
                    continue
                print(f"TX {str(tx_hash)[:20]}... did not confirm after 2 attempts - storing for next-cycle check")
                try:
                    pending = {}
                    if os.path.exists(_PENDING_TX_FILE):
                        with open(_PENDING_TX_FILE) as f:
                            pending = json.load(f)
                    pending[str(tx_hash)] = {
                        "mint": mint,
                        "token": token_name,
                        "sent_at": time.time(),
                        "attempts": send_attempt + 1
                    }
                    with open(_PENDING_TX_FILE, "w") as f:
                        json.dump(pending, f, indent=2)
                except Exception as e:
                    print(f"Failed to store pending TX: {e}")
                return False, f"TX not confirmed - likely failed"

            return True, tx_hash
        except Exception as e:
            err = str(e)
            if "429" in err or "too many requests" in err.lower():
                _mark_429_hit()
                wait = 5 + (5 * send_attempt)
                print(f"RPC rate limited, retry in {wait}s")
                time.sleep(wait)
                continue
            elif send_attempt < 2:
                print(f"Send TX error ({send_attempt+1}/3): {err}, retrying...")
                time.sleep(2)
                continue
            return False, f"Send TX failed: {err[:150]}"

def execute_sell_live(mint, token_name, amount_raw):
    """Execute sell via Jupiter v2 API (handles Token-2022).
    Chunks large amounts if v2 API rejects the full position.
    """
    # Try full amount first
    chunks = [amount_raw]
    
    for chunk in chunks:
        try:
            resp = requests.get(
                f"https://api.jup.ag/swap/v2/order?inputMint={mint}&outputMint={USDC}&amount={chunk}&slippageBps=5000&taker={str(WALLET.pubkey())}&dynamicBlockhash=true",
                timeout=15
            )
            if resp.status_code != 200:
                return False, f"v2 order failed: HTTP {resp.status_code}"
            data = resp.json()
            if data.get("errorCode"):
                # If full amount fails, try half
                if chunk == amount_raw:
                    half = amount_raw // 2
                    if half > 1000:
                        print(f"Full sell failed ({data.get('errorMessage')}), trying half ({half})...")
                        chunks.append(half)
                        continue
                return False, f"v2 order error: {data.get('errorMessage', 'unknown')}"
            tx_b64 = data.get("transaction")
            if not tx_b64:
                return False, "No transaction in v2 response"
        except Exception as e:
            return False, f"v2 order exception: {e}"

        tx = VersionedTransaction.from_bytes(base64.b64decode(tx_b64))
        signed = VersionedTransaction(tx.message, [WALLET])

        for send_attempt in range(3):
            try:
                result = CLIENT.send_raw_transaction(
                    bytes(signed),
                    opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed", max_retries=5)
                )
                tx_hash = result.value if hasattr(result, "value") else str(result)
                time.sleep(3)
                confirmed = False
                for verify_attempt in range(60):
                    try:
                        confirm = CLIENT.get_signature_statuses([str(tx_hash)])
                        if confirm and confirm.value and confirm.value[0]:
                            status = confirm.value[0]
                            if status.confirmation_status:
                                confirmed = True
                                print(f"Sell TX confirmed: {str(tx_hash)[:20]}... status={status.confirmation_status}")
                                return True, tx_hash
                            elif status.err:
                                print(f"Sell TX failed on-chain: {status.err}")
                                return False, f"Sell TX failed on-chain: {status.err}"
                    except:
                        pass
                    time.sleep(1)

                if not confirmed:
                    print(f"Sell TX {str(tx_hash)[:20]}... did not confirm after ~65s - FAILING")
                    if send_attempt < 2:
                        print("Retrying...")
                        time.sleep(10)
                        continue
                    return False, f"Sell TX not confirmed after 3 attempts"

                return True, tx_hash
            except Exception as e:
                err = str(e)
                if "429" in err or "too many requests" in err.lower():
                    _mark_429_hit()
                    wait = 5 + (5 * send_attempt)
                    print(f"RPC rate limited (sell), retry in {wait}s")
                    time.sleep(wait)
                    continue
                elif send_attempt < 2:
                    print(f"Send TX error ({send_attempt+1}/3): {err}, retrying...")
                    time.sleep(2)
                    continue
                return False, f"Send TX failed: {err[:150]}"

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

    # Quick routability check — skip if Jupiter can't route it
    if mint:
        try:
            test_amt = min(amount_raw, 1000000)
            r = requests.get(
                f"https://api.jup.ag/swap/v2/order?inputMint={mint}&outputMint={USDC}&amount={test_amt}&slippageBps=5000&taker={str(WALLET.pubkey())}&dynamicBlockhash=true",
                timeout=8
            )
            d = r.json()
            if d.get("errorCode"):
                print(f"  [SKIP] {token} — not routable ({d.get('errorMessage', 'unknown')})")
                return False, f"Token not routable: {d.get('errorMessage', 'unknown')}"
            out_amount = float(d.get("outAmount", 0))
            if out_amount < 1000:  # less than $0.001
                print(f"  [SKIP] {token} — estimated value $0 (outAmount={out_amount})")
                return False, "Token has no value"
        except Exception as e:
            print(f"  [SKIP] {token} — routability check failed: {e}")
            return False, f"Routability check failed: {e}"

    # Check risk
    portfolio_value = pdb.load_db()["portfolio"]["total_value_usd"]
    position_value = position.get("current_value_usd", 0)

    allowed, reason = check_trade_allowed(token, "SELL", portfolio_value, position_value, mint=mint)
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

        # Record cooldown on EVERY sell - no same-cycle re-buys, ever
        record_sell_cooldown(token, mint)
        record_trade(token, 'SELL', pnl_usd, trade_value=current_value)

        # Gas tax: 2% of profitable trades go to gas reserve
        if pnl_usd > 0 and sol_price > 0:
            gas_tax_usd = pnl_usd * SOL_GAS_TAX_PCT
            gas_tax_sol = gas_tax_usd / sol_price
            if gas_tax_sol > 0.0001:
                add_to_gas_reserve(gas_tax_sol)
                print(f"  [GAS TAX] {gas_tax_sol:.6f} SOL (${gas_tax_usd:.2f}) added to reserve")

        return True, f"SOLD {token} | P&L: ${pnl_usd:+.2f} ({pnl_pct:+.1f}%) | TX: {str(result)[:20]}..."
    else:
        return False, f"Sell failed: {result}"


def process_trim_signal(signal):
    """Sell TRIM_FRACTION of a position to free capital, let rest ride."""
    token = signal["token"]
    mint = signal.get("mint", "")

    position = pdb.get_position(token)
    if not position:
        return False, "No position found"

    amount_raw = position.get("amount_raw", 0)
    if amount_raw == 0:
        return False, "No amount to sell"

    sell_amount = int(amount_raw * (1 - TRIM_FRACTION))
    if sell_amount < 1:
        return False, f"Trim amount too small ({sell_amount})"

    success, result = execute_sell_live(mint, token, sell_amount)
    if not success:
        return False, f"Trim sell failed: {result}"

    cost = position.get("cost_basis_usd", 0)
    current_value = position.get("current_value_usd", 0)
    proceeds = current_value * (1 - TRIM_FRACTION)
    pnl_pct = ((current_value - cost) / cost * 100) if cost > 0 else 0

    partial = pdb.partial_close_position(token, {"close_value_usd": proceeds}, TRIM_FRACTION)
    if not partial:
        return False, "Partial close failed"

    trade = {
        "token": token,
        "action": "TRIM",
        "reason": "PARTIAL_TRIM",
        "amount_raw": sell_amount,
        "amount_usd": proceeds,
        "pnl_usd": partial["pnl_usd"],
        "pnl_pct": pnl_pct,
        "tx_hash": str(result),
        "mint": mint
    }
    pdb.add_trade(trade)
    record_trade(token, "TRIM", partial["pnl_usd"], trade_value=proceeds)

    return True, f"TRIM {token} | Sold {1-TRIM_FRACTION:.0%} at +{pnl_pct:.1f}% | Freed ${proceeds:.2f} | TX: {str(result)[:20]}..."


def determine_buy_size(signal):
    """Buy sizing scaled to current capital - %-based for rebuild, flat for standard+"""
    recommendation = signal.get("recommendation", "BUY")
    confidence = signal.get("confidence", 50)
    momentum = signal.get("momentum", {})
    usdc_balance = get_usdc_balance()

    # Rebuild phase ($0-$150): %-based sizing
    if usdc_balance < 150.0:
        if usdc_balance < 2.0:
            return 0  # too small to trade
        elif usdc_balance < 15.0:
            pcts = (0.60, 0.45, 0.30)  # survival
        elif usdc_balance < 30.0:
            pcts = (0.45, 0.30, 0.20)  # dig-out
        else:
            pcts = (0.40, 0.25, 0.15)  # rebuild ($30-$150)

        if recommendation == "STRONG_BUY" or confidence >= 65:
            size = usdc_balance * pcts[0]
        elif confidence >= 55:
            size = usdc_balance * pcts[1]
        else:
            size = usdc_balance * pcts[2]

        # Upgrade if clear upward momentum
        if momentum and momentum.get('trend') == 'up' and momentum.get('momentum_pct', 0) > 0.02:
            size = max(size, usdc_balance * pcts[2])  # at least base tier

        size = min(size, usdc_balance * 0.85)  # leave buffer
        size = round(size, 2)

        MIN_BUY = max(1.0, usdc_balance * 0.10)
        if size < MIN_BUY:
            return 0
        return size

    # Standard ($150+): flat caps
    if recommendation == "STRONG_BUY" or confidence >= 65:
        size = min(15.0, usdc_balance * 0.30)
    elif confidence >= 55:
        size = min(12.0, usdc_balance * 0.20)
    else:
        size = min(10.0, usdc_balance * 0.15)

    if momentum and momentum.get('trend') == 'up' and momentum.get('momentum_pct', 0) > 0.02:
        size = max(size, 10.0)

    size = min(size, usdc_balance * 0.85)
    size = round(size, 2)

    if usdc_balance < 20.0:
        MIN_BUY = 4.0
    elif usdc_balance < 50.0:
        MIN_BUY = 6.0
    else:
        MIN_BUY = 8.0
    if size < MIN_BUY:
        return 0
    return size


def determine_buy_size_recovery(usdc_balance):
    """Legacy recovery sizing - keep for back-compat, superseded by unified sizing above"""
    if usdc_balance < 15.0:
        return round(usdc_balance * 0.60, 2)
    elif usdc_balance < 30.0:
        return round(usdc_balance * 0.45, 2)
    else:
        return round(usdc_balance * 0.30, 2)


def process_buy_signal(signal):
    """Process buy with risk checks - buys with USDC"""
    token = signal["token"]
    mint = signal.get("mint", "")

    if not mint:
        return False, "No mint address"

    # Patch 3: Check for pending (unconfirmed) TX from previous cycle
    _PENDING_TX_FILE = os.path.join(os.path.dirname(__file__), ".pending_buy_tx.json")
    try:
        if os.path.exists(_PENDING_TX_FILE):
            with open(_PENDING_TX_FILE) as f:
                pending_txs = json.load(f)
            still_pending = {}
            for tx_hash_str, info in pending_txs.items():
                # Check if this TX confirmed since last cycle
                try:
                    confirm = CLIENT.get_signature_statuses([tx_hash_str])
                    if confirm and confirm.value and confirm.value[0]:
                        status = confirm.value[0]
                        if status.confirmation_status:
                            print(f"[PENDING TX RECOVERED] TX {tx_hash_str[:20]}... confirmed! status={status.confirmation_status}")
                            # TX went through! Record the position
                            trade = {
                                "token": info.get("token", token),
                                "action": "BUY",
                                "amount_usdc": 0,
                                "tx_hash": tx_hash_str,
                                "mint": info.get("mint", mint)
                            }
                            pdb.add_trade(trade)
                            pdb.add_position({
                                "token": info.get("token", token),
                                "mint": info.get("mint", mint),
                                "amount_raw": 0,
                                "amount": 0,
                                "decimals": 6,
                                "buy_price_usd": 0,
                                "buy_price_sol": 0,
                                "cost_basis_usd": 0,
                                "current_value_usd": 0,
                                "status": "OPEN"
                            })
                            pdb.save_db()
                            continue  # don't carry forward
                        elif status.err:
                            print(f"[PENDING TX FAILED] TX {tx_hash_str[:20]}... failed on-chain: {status.err}")
                            continue  # don't carry forward
                except:
                    pass
                # Still unconfirmed after a full cycle — keep for next check
                still_pending[tx_hash_str] = info
            if still_pending:
                with open(_PENDING_TX_FILE, "w") as f:
                    json.dump(still_pending, f, indent=2)
            else:
                if os.path.exists(_PENDING_TX_FILE):
                    os.remove(_PENDING_TX_FILE)
    except Exception as e:
        print(f"[PENDING TX CHECK] Error: {e}")

    # Auto-refill USDC from SOL if USDC is low
    if get_usdc_balance() < 15.0:
        refill_usdc_from_sol()

    # Check risk
    db = pdb.load_db()
    portfolio_value = db["portfolio"]["total_value_usd"]
    current_position = pdb.get_position(token)
    position_value = current_position.get("current_value_usd", 0) if current_position else 0

    allowed, reason = check_trade_allowed(token, "BUY", portfolio_value, position_value, mint=mint)
    if not allowed:
        return False, f"Risk check failed: {reason}"

    # Determine buy size from signal type
    usdc_balance = get_usdc_balance()
    if usdc_balance <= 0:
        return False, "No USDC balance available"

    buy_size = signal.get("max_usdc")
    if buy_size is None:
        buy_size = determine_buy_size(signal)

    # Handle skip signal (size=0 from determine_buy_size)
    if buy_size == 0:
        return False, "Buy size too small - skipping"

    print(f"Available USDC: ${usdc_balance:.2f} | Buying with: ${buy_size:.2f} ({buy_size/usdc_balance*100:.0f}%)")
    success, result = execute_buy_live(mint, token, buy_size)

    if success:
        # Add to DB
        trade = {
            "token": token,
            "action": "BUY",
            "amount_usdc": buy_size,
            "tx_hash": str(result),
            "mint": mint
        }

        pdb.add_trade(trade)

        # Record the buy with cost basis; scout sync will fill on-chain amounts next cycle
        pdb.add_position({
            "token": token,
            "mint": mint,
            "amount_raw": 0,
            "current_price_usd": 0,
            "current_value_usd": 0,
            "current_value_sol": 0,
            "cost_basis_usd": buy_size,
            "buy_price_usd": 0,
            "buy_price_sol": 0,
            "unrealized_pnl_usd": 0,
            "unrealized_pnl_pct": 0,
            "status": "OPEN",
            "tx_hash": str(result)
        })

        record_trade(token, "BUY", trade_value=buy_size)

        return True, f"BOUGHT {token} | ${buy_size:.2f} USDC | TX: {str(result)[:20]}..."
    else:
        return False, f"Buy failed: {result}"

def main():
    """Main executor routine"""
    print(f"[{datetime.now(timezone.utc).isoformat()}] === V2 EXECUTOR ===")
    print(f"Wallet: {WALLET.pubkey()}")

    # Track gas at start of cycle
    cycle_start_sol = get_sol_balance()
    daily_gas = get_daily_gas_spent()
    gas_reserve = get_gas_reserve()
    print(f"[GAS] SOL: {cycle_start_sol:.6f} | Today: {daily_gas:.6f}/{SOL_DAILY_BUDGET} SOL | Reserve: {gas_reserve:.6f}")

    # Check daily gas budget before doing anything
    if daily_gas >= SOL_DAILY_BUDGET:
        print(f"[GAS] Daily budget exhausted — pausing until tomorrow")
        print("=" * 50)
        return

    # Emergency check: if SOL is critically low, warn and skip trading
    if cycle_start_sol < SOL_MIN_SAFE:
        print(f"[GAS CRITICAL] SOL at {cycle_start_sol:.6f} — below MIN_SAFE ({SOL_MIN_SAFE}). Attempting emergency refill...")
        ensure_sol_for_gas()
        cycle_start_sol = get_sol_balance()
        if cycle_start_sol < SOL_MIN_SAFE:
            print(f"[GAS CRITICAL] Cannot refill — skipping all trading this cycle")
            print("=" * 50)
            return

    # Auto-refill SOL gas before any trade operations
    ensure_sol_for_gas()

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
        elif action == "TRIM":
            mint = signal.get("mint", "")
            success, msg = process_trim_signal(signal)
            print(msg)
            if success:
                queue["pending"].remove(signal)
                queue.setdefault("executed", []).append(signal)
        elif action == "BUY":
            mint = signal.get("mint") or TOKENS.get(token, {}).get("mint")
            if not mint:
                print(f"No mint found for {token}, skipping")
                continue
            # Re-check USDC balance before buying - ensure we still have funds
            current_usdc = get_usdc_balance()
            if current_usdc < 3.0:
                print(f"  [SKIP {token}] USDC too low after previous buys (${current_usdc:.2f}) - need >= $3 for min buy")
                continue
            sig = {"token": token, "mint": mint}
            success, msg = process_buy_signal(sig)
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

    # Track threshold-triggered actions for reporting (written after threshold check)
    threshold_actions = list(queue.get("threshold_actions", []))
    queue["threshold_actions"] = threshold_actions

    # Load DB for status reporting and auto-threshold checks
    db = pdb.load_db()
    risk = db.get("risk_metrics", {})

    today = datetime.now(timezone.utc).isoformat()[:10]
    daily_count = risk.get("daily_trade_count", 0) if risk.get("daily_trade_reset") == today else 0

    print(f"Daily Trades: {daily_count}")
    print(f"Status: {'PAUSED' if risk.get('consecutive_losses', 0) >= 3 else 'ACTIVE'}")

    # Auto-check open positions for TP/SL/trailing-stop thresholds (belt + suspenders)
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
            tp_threshold = TAKE_PROFIT_PCT * 100  # e.g. 25.0
            trim_threshold = TRIM_PCT * 100       # e.g. 12.0
            sl_threshold = STOP_LOSS_PCT * 100     # e.g. -8.0
            live_pnl_pct = ((live_value - cost) / cost) * 100 if cost > 0 else 0

            # Update trailing stop high watermark
            pos["current_price_usd"] = live_price
            update_trailing_stop(pos, live_price)

            # Check trailing stop first (overrides hard stop loss when active)
            trail_info = get_trailing_stop_info(pos)
            trailing_hit = False
            if trail_info and trail_info.get("active"):
                trail_stop = trail_info["trail_stop_price"]
                if live_price <= trail_stop:
                    trailing_hit = True
                    print(f"  {token}: ${live_value:.2f} (PnL: {live_pnl_pct:+.1f}%) | Trailing: locked +{trail_info['locked_pnl_pct']:.1f}%")
                    print(f"  >> TRAILING STOP at ${trail_stop:.8f} (current ${live_price:.8f}) — locking in +{trail_info['locked_pnl_pct']:.1f}%")
                    sig = {"token": token, "mint": mint, "current_value_usd": live_value, "reason": "TRAILING_STOP"}
                    success, msg = process_sell_signal(sig)
                    print(f"  {msg}")
                    executed_tokens.add(token)
                    threshold_actions.append({"token": token, "action": "SELL", "reason": "TRAILING_STOP", "pnl_pct": live_pnl_pct})
                    continue

            print(f"  {token}: ${live_value:.2f} (PnL: {live_pnl_pct:+.1f}%)", end="")
            if trail_info and trail_info.get("active"):
                print(f" | trail: +{trail_info['locked_pnl_pct']:.1f}% locked, {trail_info['distance_to_stop_pct']:.1f}% to stop")
            else:
                print()

            # Routability check — if Jupiter can't route it, close in DB and move on
            if live_price > 0 and live_value < 0.50:
                print(f"  >> Worthless (${live_value:.2f}) — closing in DB")
                pdb.close_position(token, {"close_price_usd": live_price, "close_value_usd": live_value, "reason": "WORTHLESS"})
                continue

            already_trimmed = pos.get("partial_trims", 0) > 0

            if live_pnl_pct >= tp_threshold:
                print(f"  >> TAKE PROFIT triggered at +{live_pnl_pct:.1f}% (threshold: +{tp_threshold:.0f}%)")
                sig = {"token": token, "mint": mint, "current_value_usd": live_value, "reason": "TAKE_PROFIT"}
                success, msg = process_sell_signal(sig)
                print(f"  {msg}")
                executed_tokens.add(token)
                threshold_actions.append({"token": token, "action": "SELL", "reason": "TAKE_PROFIT", "pnl_pct": live_pnl_pct})
            elif live_pnl_pct <= sl_threshold:
                print(f"  >> STOP LOSS triggered at {live_pnl_pct:.1f}% (threshold: {sl_threshold:.0f}%)")
                sig = {"token": token, "mint": mint, "current_value_usd": live_value, "reason": "STOP_LOSS"}
                success, msg = process_sell_signal(sig)
                print(f"  {msg}")
                executed_tokens.add(token)
                threshold_actions.append({"token": token, "action": "SELL", "reason": "STOP_LOSS", "pnl_pct": live_pnl_pct})
            elif live_pnl_pct >= trim_threshold and not already_trimmed:
                print(f"  >> TRIM THRESHOLD at +{live_pnl_pct:.1f}% - selling half")
                sig = {"token": token, "mint": mint, "current_value_usd": live_value, "reason": "TRIM_THRESHOLD"}
                success, msg = process_trim_signal(sig)
                print(f"  {msg}")
                threshold_actions.append({"token": token, "action": "TRIM", "reason": "TRIM_THRESHOLD", "pnl_pct": live_pnl_pct})
            else:
                if already_trimmed:
                    print(f"  >> Held (already trimmed, trailing stop active, waiting for full TP/trail)")
                else:
                    print(f"  >> Held (within threshold bounds)")
        else:
            print(f"  {token}: no price data — skipping (likely dead/rugged)")
            # Remove from DB so we don't keep trying
            pdb.close_position(token, {"close_price_usd": 0, "close_value_usd": 0, "reason": "NO_PRICE_DATA"})
            print(f"  >> Closed {token} in DB (no price data)")

    # Write threshold actions back to queue so post-run checks can see them
    # Threshold-triggered trades (TP/SL/trim/trailing) aren't in queue["executed"]
    # because they come from the THRESHOLD CHECK section, not from pending signals.
    # Without this, reports that only check queue["executed"] miss threshold actions.
    try:
        with open(pending_path, "r") as f:
            queue2 = json.load(f)
        queue2["threshold_actions"] = threshold_actions
        with open(pending_path, "w") as f:
            json.dump(queue2, f, indent=2)
        action_count = len(threshold_actions)
        print(f"[QUEUE] Threshold actions written: {action_count}")
    except Exception as e:
        print(f"[QUEUE] Failed to write threshold actions: {e}")

    # Track gas at end of cycle
    cycle_end_sol = get_sol_balance()
    log_gas_spent(cycle_start_sol, cycle_end_sol)
    gas_reserve = get_gas_reserve()
    spent_this = cycle_start_sol - cycle_end_sol
    print(f"[GAS] End: {cycle_end_sol:.6f} SOL | Spent: {spent_this:.6f} | Reserve: {gas_reserve:.6f}")

    # Warn if gas is getting low
    if cycle_end_sol < SOL_TARGET_FLOOR:
        print(f"[GAS WARNING] SOL below target floor ({SOL_TARGET_FLOOR})! Reserve: {gas_reserve:.6f}")
    if spent_this > 0.002:
        print(f"[GAS WARNING] High cycle spend ({spent_this:.6f} SOL) — check for runaway fees")
    if daily_gas + spent_this > SOL_DAILY_BUDGET * 0.8:
        print(f"[GAS WARNING] Approaching daily budget ({(daily_gas + spent_this):.6f}/{SOL_DAILY_BUDGET})")

    print("=" * 50)

if __name__ == "__main__":
    main()
