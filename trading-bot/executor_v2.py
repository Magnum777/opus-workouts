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
from risk_manager import check_trade_allowed, record_trade, record_sell_cooldown
from risk_manager import STOP_LOSS_PCT, TAKE_PROFIT_PCT, TRIM_PCT, TRIM_FRACTION
from research_v2 import TOKENS

# Solana imports
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# Wallet
PRIVATE_KEY = bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d")
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client("https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887")

# Constants
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# SOL gas: %-based reserve, auto-refills from USDC when low
#   Target = max(0.01 SOL, portfolio_value * SOL_RESERVE_PCT / sol_price)
#   Refill capped at MAX_REFILL_PCT of current USDC per cycle
SOL_TARGET_FLOOR = 0.01       # 0.01 SOL absolute minimum
SOL_RESERVE_PCT = 0.01        # 1% of portfolio as gas reserve
MAX_REFILL_PCT = 0.15          # max 15% of USDC per cycle for refill
MIN_REFILL_FLOOR = 5.0          # minimum SOL refill in USD
SOL_MIN_SAFE = 0.003          # below this swaps fail due to ATA rent

SOL_MIN_HYSTERIA = 0.01       # above this, bot runs normally

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

def ensure_sol_for_gas():
    """
    Proportional SOL gas reserve. Refills from USDC when below target.
    Silently skips if SOL > 0.001 — we rarely need more for ~200 txns.
    """
    sol_bal = get_sol_balance()
    
    # Absolute floor: 0.001 SOL (~200 txns) — no point burning API calls below that
    if sol_bal >= 0.001:
        return False
    
    sol_price = get_jupiter_price(SOL_MINT)
    if sol_price <= 0:
        sol_price = 170
    
    usdc_bal = get_usdc_balance()
    total_value = usdc_bal + (sol_bal * sol_price)
    target_sol = max(0.01, (total_value * SOL_RESERVE_PCT) / sol_price)
    
    if sol_bal >= target_sol:
        return False
    
    deficit_sol = target_sol - sol_bal
    deficit_usd = deficit_sol * sol_price
    max_refill = usdc_bal * MAX_REFILL_PCT
    refill_amount = min(max(deficit_usd, MIN_REFILL_FLOOR), max_refill)
    
    print(f"[SOL GAS] Very low: {sol_bal:.6f}. Refilling ${refill_amount:.2f} USDC → SOL...")
    
    success, msg = execute_buy_live(SOL_MINT, "SOL", refill_amount)
    if success:
        new_sol = get_sol_balance()
        print(f"[SOL GAS] Refilled! {sol_bal:.6f} → {new_sol:.6f} SOL")
    else:
        print(f"[SOL GAS] Refill failed: {msg}")
    return True

def get_usdc_balance():
    """Get USDC balance from blockchain"""
    try:
        helius_url = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
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
    """Execute buy via Jupiter using USDC as input"""
    usdc_units = int(usdc_amount * 1e6)

    # Quote with cycle-aware backoff (2 attempts instead of 6)
    quote, err = _respectful_quote(USDC, mint, usdc_units, slippage_bps=1500, label=f"buy_{token_name}")
    if err:
        print(f"Initial quote failed: {err}. Trying 20% slippage once.")
        quote, err = _respectful_quote(USDC, mint, usdc_units, slippage_bps=2000, label=f"buy_{token_name}_fallback")
        if err:
            print(f"Fallback quote also failed: {err}")
            return False, "Quote failed"

    print(f"Quote: inAmount={quote.get('inAmount')} outAmount={quote.get('outAmount')} slippageBps={quote.get('slippageBps')}")

    # Swap with cycle-aware backoff
    swap_data, err = _respectful_swap(quote, str(WALLET.pubkey()), wrap_sol=(mint == SOL_MINT), label=f"swap_{token_name}")
    if err:
        return False, f"Swap failed: {err}"

    # Sign and send with retry
    tx = VersionedTransaction.from_bytes(base64.b64decode(swap_data["swapTransaction"]))
    signed = VersionedTransaction(tx.message, [WALLET])

    for send_attempt in range(3):
        try:
            result = CLIENT.send_raw_transaction(
                bytes(signed),
                opts=TxOpts(skip_preflight=True, max_retries=5)
            )
            tx_hash = result.value if hasattr(result, "value") else str(result)
            # Extended wait — Jupiter swaps on low-cap tokens can take 10-20s
            time.sleep(5)
            # Verify tx confirmed (up to ~20s total)
            confirmed = False
            for verify_attempt in range(15):
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
                print(f"TX {str(tx_hash)[:20]}... did not confirm after ~20s - treating as failed")
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
    """Execute sell via Jupiter"""
    quote, err = _respectful_quote(mint, USDC, amount_raw, slippage_bps=1500, label=f"sell_{token_name}")
    if err:
        return False, f"Sell quote failed: {err}"

    swap_data, err = _respectful_swap(quote, str(WALLET.pubkey()), wrap_sol=True, label=f"sell_{token_name}")
    if err:
        return False, f"Sell swap failed: {err}"
    # Sign and send with retry
    tx = VersionedTransaction.from_bytes(base64.b64decode(swap_data["swapTransaction"]))
    signed = VersionedTransaction(tx.message, [WALLET])

    for send_attempt in range(3):
        try:
            result = CLIENT.send_raw_transaction(
                bytes(signed),
                opts=TxOpts(skip_preflight=True, max_retries=5)
            )
            tx_hash = result.value if hasattr(result, "value") else str(result)
            # Extended verification for sell TX
            time.sleep(5)
            confirmed = False
            for verify_attempt in range(15):
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
                print(f"Sell TX {str(tx_hash)[:20]}... did not confirm after ~20s - returning anyway")
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
        if usdc_balance < 8.0:
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

        MIN_BUY = max(3.0, usdc_balance * 0.10)
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
            if current_usdc < 15.0:
                print(f"  [SKIP {token}] USDC too low after previous buys (${current_usdc:.2f}) - need >= $15 for min $20 buy")
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

    # Load DB for status reporting and auto-threshold checks
    db = pdb.load_db()
    risk = db.get("risk_metrics", {})

    today = datetime.now(timezone.utc).isoformat()[:10]
    daily_count = risk.get("daily_trade_count", 0) if risk.get("daily_trade_reset") == today else 0

    print(f"Daily Trades: {daily_count}")
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
            tp_threshold = TAKE_PROFIT_PCT * 100  # e.g. 15.0
            trim_threshold = TRIM_PCT * 100       # e.g. 8.0
            sl_threshold = STOP_LOSS_PCT * 100     # e.g. -8.0
            live_pnl_pct = ((live_value - cost) / cost) * 100 if cost > 0 else 0
            print(f"  {token}: ${live_value:.2f} (PnL: {live_pnl_pct:+.1f}%)")

            already_trimmed = pos.get("partial_trims", 0) > 0

            if live_pnl_pct >= tp_threshold:
                print(f"  >> TAKE PROFIT triggered at +{live_pnl_pct:.1f}% (threshold: +{tp_threshold:.0f}%)")
                sig = {"token": token, "mint": mint, "current_value_usd": live_value, "reason": "TAKE_PROFIT"}
                success, msg = process_sell_signal(sig)
                print(f"  {msg}")
                executed_tokens.add(token)
            elif live_pnl_pct <= sl_threshold:
                print(f"  >> STOP LOSS triggered at {live_pnl_pct:.1f}% (threshold: {sl_threshold:.0f}%)")
                sig = {"token": token, "mint": mint, "current_value_usd": live_value, "reason": "STOP_LOSS"}
                success, msg = process_sell_signal(sig)
                print(f"  {msg}")
                executed_tokens.add(token)
            elif live_pnl_pct >= trim_threshold and not already_trimmed:
                print(f"  >> TRIM THRESHOLD at +{live_pnl_pct:.1f}% - selling all")
                sig = {"token": token, "mint": mint, "current_value_usd": live_value, "reason": "TRIM_THRESHOLD"}
                success, msg = process_sell_signal(sig)
                print(f"  {msg}")
                executed_tokens.add(token)
            else:
                if already_trimmed:
                    print(f"  >> Held (already trimmed, waiting for full TP/SL)")
                else:
                    print(f"  >> Held (within threshold bounds)")
        else:
            print(f"  {token}: no price data, using DB value ${current_value:.2f}")

    print("=" * 50)

if __name__ == "__main__":
    main()
