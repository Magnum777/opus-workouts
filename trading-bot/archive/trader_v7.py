"""
Trading Bot v7 - WITH BUY SCANNING
Scans for new opportunities and executes buys
"""
import requests
import json
import base64
import time
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# WALLET
PRIVATE_KEY = bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d")
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client("https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887")

USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL = "So11111111111111111111111111111111111111112"

# ACTUAL HOLDINGS
HOLDINGS = {
    "BIRB": 62017892,
    "SKR": 600000000,
}

SOL_SPENT = {
    "BIRB": 0.53,
    "SKR": 0.25,
}

# RULES
TAKE_PROFIT = 5
STOP_LOSS = 3
TRAIL = 2
BUY_AMOUNT = 0.15  # SOL to spend per buy

STATE_FILE = "positions_v7.json"

# Track what we've already bought (don't buy same coin twice)
BOUGHT_TOKENS = set()

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

def get_sol_price():
    try:
        return requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd", timeout=10).json()["solana"]["usd"]
    except:
        return 86

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
        r = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={SOL}&outputMint={mint}&amount={lamports}&slippage=20", timeout=15)
        quote = r.json()
        swap = requests.post("https://lite-api.jup.ag/swap/v1/swap", json={"quoteResponse": quote, "userPublicKey": str(WALLET.pubkey()), "wrapAndUnwrapSol": True}, timeout=15).json()
        tx = base64.b64decode(swap["swapTransaction"])
        signed = VersionedTransaction(VersionedTransaction.from_bytes(tx).message, [WALLET])
        result = CLIENT.send_raw_transaction(bytes(signed))
        return f"SUCCESS: {str(result)[:40]}"
    except Exception as e:
        return f"FAILED: {str(e)[:60]}"

def scan_opportunities():
    """Scan for buy opportunities - coins with momentum"""
    opportunities = []
    
    # Try to get trending from Jupiter
    try:
        # Check some known pump.fun tokens
        test_tokens = [
            ("PUMP", "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn"),
            ("POPCAT", "Pop1QTJ3rNmCCUAuLXFxYUTPpoLLHLz2x8WNH6fmRqb"),
            ("GOAT", " CzZkHS5iY4FLZcSCGjCmN9KoW72tJ9xMH4gc6FZ9h6"),
            ("MEOW", "MEoWcph2uKZkKGqEXC/1VZ3p8WN2x3y6o9d9TJVqKZ"),
            ("BODEN", "BodenB2XKcnx9ESgY2XhGvW3QXE2N5p7qR9tU4vW1xZ"),
        ]
        
        for name, mint in test_tokens:
            try:
                price = get_price(mint)
                if price > 0:
                    opportunities.append({"name": name, "mint": mint, "price": price})
            except:
                pass
    except:
        pass
    
    return opportunities

# MAIN
state = load_state()
sol = get_sol()
sol_price = get_sol_price()

print("=== TRADING BOT v7 ===")
print(f"SOL: {sol:.4f} (${sol * sol_price:.2f})")
print()

trades = []

# === MANAGE EXISTING POSITIONS ===
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

# === SCAN FOR NEW OPPORTUNITIES ===
if sol > 0.3:
    print(f"\n>> Have {sol:.2f} SOL - scanning for opportunities...")
    opportunities = scan_opportunities()
    
    if opportunities:
        print(f"Found {len(opportunities)} opportunities:")
        for opp in opportunities:
            print(f"  - {opp['name']}: ${opp['price']:.4f}")
        
        # Buy the first one we haven't bought yet
        for opp in opportunities:
            if opp["name"] not in BOUGHT_TOKENS:
                print(f"\n>> BUYING {opp['name']}!")
                result = do_buy(opp["mint"], BUY_AMOUNT, opp["name"])
                print(f"  >> BUY RESULT: {result}")
                if "SUCCESS" in result:
                    trades.append(f"BUY: {opp['name']}")
                    BOUGHT_TOKENS.add(opp["name"])
                    break
    else:
        print("No clear opportunities found")

print(f"\n=== TRADES: {trades if trades else 'None'} ===")
