"""
Trading Bot - AUTO BUY & SELL
Fast mode (--fast): Skip dip scanning, only check positions.
Normal mode: Full scan + execute.
"""
import os
import requests
import json
import base64
import random
import sys
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client(os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"))

USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"
TOKEN2022_PROGRAM = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"

FAST_MODE = "--fast" in sys.argv

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

RECENTLY_SOLD = {}
STOP_LOSS_COOLDOWN = {}

TAKE_PROFIT_PCT = 1
STOP_LOSS_PCT = 1
MAX_POSITIONS = 6
BUY_SIZE_SOL = 0.20
COOLDOWN_STOPS = 2
COOLDOWN_SCANS = 6

STATE_FILE = "positions_enforced.json"

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_state(s):
    with open(STATE_FILE, "w") as f:
        json.dump(s, f, indent=2)

def get_balance():
    return CLIENT.get_balance(WALLET.pubkey()).value / 1e9

def get_all_holdings():
    """Get ALL token holdings from BOTH Token programs"""
    holdings = {}
    for prog in ["TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", TOKEN2022_PROGRAM]:
        try:
            url = "https://api.mainnet-beta.solana.com"
            data = {
                "jsonrpc": "2.0", "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [str(WALLET.pubkey()), {"programId": prog}, {"encoding": "jsonParsed"}]
            }
            resp = requests.post(url, json=data, headers={"Content-Type": "application/json"}, timeout=15)
            if resp.status_code == 200:
                result = resp.json()
                if "result" in result and result["result"]:
                    for account in result["result"]["value"]:
                        mint = account["account"]["data"]["parsed"]["info"]["mint"]
                        amount = int(account["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])
                        if amount > 0 and mint != SOL_MINT:
                            holdings[mint] = amount
        except:
            continue
    return holdings

def get_price_fast(mint):
    """Fast price check - single token, short timeout"""
    try:
        r = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount=1000000&slippage=1", timeout=8)
        return float(r.json()["outAmount"]) / 1e6 if r.status_code == 200 else 0
    except:
        return 0

def get_sol_price():
    try:
        r = requests.get("https://lite-api.jup.ag/swap/v1/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=1000000000&slippage=1", timeout=8)
        return float(r.json()["outAmount"]) / 1e6 if r.status_code == 200 else 84
    except:
        return 84

def scan_for_dips():
    """Scan for buying opportunities"""
    dips = []
    for name, mint in KNOWN_TOKENS.items():
        try:
            price = get_price_fast(mint)
            if price > 0:
                priority = 1
                if name in ["POPCAT", "WIF", "BONK", "PENGU", "PUMP"]:
                    priority = 3
                elif name in ["TRUMP", "GOAT", "MOODENG", "GIGA", "FART"]:
                    priority = 2
                dips.append({"name": name, "mint": mint, "price": price, "priority": priority, "liquidity": 50000})
        except:
            continue
    dips.sort(key=lambda x: x["priority"], reverse=True)
    return dips

def execute_buy(mint, amount_sol):
    try:
        lamports = int(amount_sol * 1e9)
        r = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={SOL_MINT}&outputMint={mint}&amount={lamports}&slippage=10", timeout=15)
        if r.status_code != 200:
            return False, "Quote failed"
        quote = r.json()
        swap = requests.post("https://lite-api.jup.ag/swap/v1/swap", json={
            "quoteResponse": quote,
            "userPublicKey": str(WALLET.pubkey()),
            "wrapAndUnwrapSol": True
        }, timeout=15).json()
        tx = VersionedTransaction.from_bytes(base64.b64decode(swap["swapTransaction"]))
        signed = VersionedTransaction(tx.message, [WALLET])
        result = CLIENT.send_raw_transaction(bytes(signed), opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed"))
        return True, result.value if hasattr(result, "value") else "sent"
    except Exception as e:
        return False, str(e)

def execute_sell(mint, amount, name):
    try:
        r = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={SOL_MINT}&amount={amount}&slippage=15", timeout=15)
        quote = r.json()
        swap = requests.post("https://lite-api.jup.ag/swap/v1/swap", json={
            "quoteResponse": quote,
            "userPublicKey": str(WALLET.pubkey()),
            "wrapAndUnwrapSol": True
        }, timeout=15).json()
        tx = VersionedTransaction.from_bytes(base64.b64decode(swap["swapTransaction"]))
        signed = VersionedTransaction(tx.message, [WALLET])
        result = CLIENT.send_raw_transaction(bytes(signed), opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed"))
        return True, result.value if hasattr(result, "value") else "sent"
    except Exception as e:
        return False, str(e)

# === MAIN ===
state = load_state()
sol = get_balance()
sol_price = get_sol_price()
mode_tag = "[FAST]" if FAST_MODE else "[FULL]"
print(f"=== AUTO TRADING BOT {mode_tag} ===")
print(f"SOL: {sol:.4f} (${sol * sol_price:.2f})")

trades = []
total_value = sol * sol_price

# FAST MODE: Only check existing positions from state, skip full holdings scan + dip scan
if FAST_MODE:
    # Load positions from state file (mints we have buy_price for)
    position_mints = {mint.replace("_buy_price", ""): buy_price for mint, buy_price in state.items() if mint.endswith("_buy_price") and not state.get(mint.replace("_buy_price", "") + "_sold", False)}
    if not position_mints:
        print("No active positions in state. Skipping fast scan.")
        print(f"Total Portfolio: ${total_value:.2f}")
    else:
        print(f"Checking {len(position_mints)} position(s) from state...")
        for mint_buy_key in position_mints:
            mint = mint_buy_key.replace("_buy_price", "")
            buy_price = state[mint_buy_key + "_buy_price"]
            try:
                price = get_price_fast(mint)
                if price > 0:
                    value_sol = price / 1e6
                    pct = ((value_sol - buy_price) / buy_price) * 100
                    print(f"  {KNOWN_TOKENS.get(mint, mint[:10])}: {pct:+.1f}% (vs buy @ {buy_price:.4f} SOL)")
                    if pct >= TAKE_PROFIT_PCT:
                        print(f"  → TP hit on {mint[:10]}, would sell (full scan needed)")
                    elif pct <= -STOP_LOSS_PCT:
                        print(f"  → SL hit on {mint[:10]}, would sell (full scan needed)")
            except:
                continue
        print(f"Total Portfolio: ${total_value:.2f}")
        print("[FAST] No buys/sells in fast mode. Full scan needed for execution.")
else:
    # FULL MODE: Full holdings scan + dip scanning + execution
    holdings = get_all_holdings()
    print(f"Positions: {len(holdings)}")

    # SELL LOGIC
    for mint, amount in holdings.items():
        price = get_price_fast(mint)
        if price == 0:
            continue
        token_name = mint[:10]
        for name, m in KNOWN_TOKENS.items():
            if m == mint:
                token_name = name
                break
        value_usd = amount * price / 1e6
        total_value += value_usd
        buy_price = state.get(f"{mint}_buy_price", 0)
        if buy_price > 0:
            value_sol = value_usd / sol_price
            pct = ((value_sol - buy_price) / buy_price) * 100
            print(f"{token_name}: ${value_usd:.2f} ({pct:+.1f}%)")
            if pct >= TAKE_PROFIT_PCT:
                success, result = execute_sell(mint, amount, token_name)
                if success:
                    state[f"{mint}_sold"] = True
                    trades.append(f"SOLD {token_name}: {result}")
                    RECENTLY_SOLD[token_name] = {"cooldown_remaining": 3}
                    print(f"[BLOCKED] {token_name} marked as recently sold")
            elif pct <= -STOP_LOSS_PCT:
                success, result = execute_sell(mint, amount, token_name)
                if success:
                    state[f"{mint}_sold"] = True
                    trades.append(f"STOP LOSS {token_name}: {result}")
                    if token_name not in STOP_LOSS_COOLDOWN:
                        STOP_LOSS_COOLDOWN[token_name] = {"count": 0, "cooldown_remaining": 0}
                    STOP_LOSS_COOLDOWN[token_name]["count"] += 1
                    if STOP_LOSS_COOLDOWN[token_name]["count"] >= COOLDOWN_STOPS:
                        STOP_LOSS_COOLDOWN[token_name]["cooldown_remaining"] = COOLDOWN_SCANS
                        print(f"[PAUSED] {token_name} entered COOLDOWN")
                    RECENTLY_SOLD[token_name] = {"cooldown_remaining": 3}
        else:
            print(f"{token_name}: ${value_usd:.2f} (new)")

    print(f"\nTotal Portfolio: ${total_value:.2f}")

    # BUY LOGIC
    if len(holdings) < MAX_POSITIONS and sol >= BUY_SIZE_SOL * 2:
        dips = scan_for_dips()
        available_dips = []
        for pick in dips:
            token = pick["name"]
            cooldown_info = STOP_LOSS_COOLDOWN.get(token, {})
            if cooldown_info.get("cooldown_remaining", 0) > 0:
                STOP_LOSS_COOLDOWN[token]["cooldown_remaining"] -= 1
                continue
            sold_info = RECENTLY_SOLD.get(token, {})
            if sold_info.get("cooldown_remaining", 0) > 0:
                RECENTLY_SOLD[token]["cooldown_remaining"] -= 1
                continue
            available_dips.append(pick)
        if not available_dips:
            available_dips = dips
        random.shuffle(available_dips)
        available_dips.sort(key=lambda x: x.get("priority", 1), reverse=True)
        if available_dips:
            pick = available_dips[0]
            if pick["mint"] not in holdings:
                liq = pick.get("liquidity", 0)
                print(f"\n--- Buying {pick['name']} (liq: ${liq:,.0f}) with {BUY_SIZE_SOL} SOL ---")
                success, result = execute_buy(pick["mint"], BUY_SIZE_SOL)
                if success:
                    state[f"{pick['mint']}_buy_price"] = BUY_SIZE_SOL
                    trades.append(f"BUY {pick['name']}: {result}")
                else:
                    trades.append(f"BUY FAILED: {result}")

    save_state(state)
    if trades:
        print(f"\nTrades: {trades}")
