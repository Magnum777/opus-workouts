"""
Trading Bot v6 - ACTUAL EXECUTION MODE
With correct holdings and enforcement
"""
import os
import requests
import json
import base64
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# WALLET
PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client(os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"))

USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL = "So11111111111111111111111111111111111111112"

# ACTUAL HOLDINGS - what we actually have
# Update these from on-chain data
HOLDINGS = {
    "BIRB": 62017892,   # After selling half
    "SKR": 600000000,   # Still holding
}

# SOL spent on each (for P/L)
SOL_SPENT = {
    "BIRB": 0.53,
    "SKR": 0.25,
}

# RULES - LOW RISK
TAKE_PROFIT = 5   # Sell 50% at +5%
STOP_LOSS = 3       # Sell all at -3%
TRAIL = 2           # Trail stop

STATE_FILE = "positions_v6.json"

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_state(s):
    with open(STATE_FILE, "w") as f:
        json.dump(s, f)

def get_sol():
    return CLIENT.get_balance(WALLET.pubkey()).value / 1e9

def get_price(mint):
    try:
        r = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount=1000000&slippage=1", timeout=10)
        return float(r.json()["outAmount"]) / 1e6 if r.status_code == 200 else 0
    except:
        return 0

def do_sell(mint, amount, name):
    try:
        print(f"  >>> SELLING {name}: {amount}")
        r = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={SOL}&amount={amount}&slippage=15", timeout=15)
        quote = r.json()
        swap = requests.post("https://lite-api.jup.ag/swap/v1/swap", json={"quoteResponse": quote, "userPublicKey": str(WALLET.pubkey()), "wrapAndUnwrapSol": True}, timeout=15).json()
        tx = base64.b64decode(swap["swapTransaction"])
        signed = VersionedTransaction(VersionedTransaction.from_bytes(tx).message, [WALLET])
        result = CLIENT.send_raw_transaction(bytes(signed))
        return f"SUCCESS: {str(result)[:40]}"
    except Exception as e:
        return f"FAILED: {str(e)[:60]}"

def do_buy(mint, sol_amount, name):
    try:
        lamports = int(sol_amount * 1e9)
        print(f"  >>> BUYING {name} with {sol_amount} SOL")
        r = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={SOL}&outputMint={mint}&amount={lamports}&slippage=15", timeout=15)
        quote = r.json()
        swap = requests.post("https://lite-api.jup.ag/swap/v1/swap", json={"quoteResponse": quote, "userPublicKey": str(WALLET.pubkey()), "wrapAndUnwrapSol": True}, timeout=15).json()
        tx = base64.b64decode(swap["swapTransaction"])
        signed = VersionedTransaction(VersionedTransaction.from_bytes(tx).message, [WALLET])
        result = CLIENT.send_raw_transaction(bytes(signed))
        return f"SUCCESS: {str(result)[:40]}"
    except Exception as e:
        return f"FAILED: {str(e)[:60]}"

# MAIN
state = load_state()
sol = get_sol()

# Get SOL price
try:
    sol_price = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd", timeout=10).json()["solana"]["usd"]
except:
    sol_price = 86

print("=== TRADING BOT v6 ===")
print(f"SOL: {sol:.4f} (${sol * sol_price:.2f})")
print()

trades = []

TOKENS = {
    "BIRB": "G7vQWurMkMMm2dU3iZpXYFTHT9Biio4F4gZCrwFpKNwG",
    "SKR": "SKRbvo6Gf7GondiT3BbTfuRDPqLWei4j2Qy2NPGZhW3",
}

for name, mint in TOKENS.items():
    price = get_price(mint)
    if price == 0:
        continue
    
    amount = HOLDINGS.get(name, 0)
    spent_sol = SOL_SPENT.get(name, 0)
    
    invested = spent_sol * sol_price
    value = amount * price / 1e6
    pnl = value - invested
    pct = (pnl / invested) * 100 if invested > 0 else 0
    
    print(f"{name}: ${value:.2f} ({pct:+.1f}%)")
    
    # Track peak
    peak = state.get(f"{name}_peak", 0)
    if pct > peak:
        state[f"{name}_peak"] = pct
        save_state(state)
        peak = pct
    
    # RULES
    if pct >= TAKE_PROFIT:
        sell_amt = int(amount * 0.5)
        result = do_sell(mint, sell_amt, name)
        print(f"  >> TAKE PROFIT: {result}")
        trades.append(f"TP: {name}")
    
    elif pct <= -STOP_LOSS:
        result = do_sell(mint, amount, name)
        print(f"  >> STOP LOSS: {result}")
        trades.append(f"SL: {name}")
    
    elif peak >= TAKE_PROFIT and (peak - pct) >= TRAIL:
        result = do_sell(mint, amount, name)
        print(f"  >> TRAIL STOP: {result}")
        trades.append(f"TR: {name}")

# BUY RULE: If SOL > 0.4, look for opportunities
if sol > 0.4:
    print(f"\n>> Have {sol:.2f} SOL - ready to buy")

print(f"\n=== TRADES: {trades if trades else 'None'} ===")
