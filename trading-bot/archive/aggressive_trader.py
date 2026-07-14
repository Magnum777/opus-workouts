"""
Aggressive Solana Trading Bot v2
With proper logging
"""
import os
import requests, base64, json
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from datetime import datetime

# Config
PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY", "")
JUPITER_API_KEY = "9d47a5ee-ff57-479e-9a0a-ac322715a012"
CLIENT = Client(f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}")

# Known tokens
TOKENS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
}

LOG_FILE = "trading-bot/trade_journal.json"

def log_trade(trade):
    """Log trade to file"""
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {"trades": [], "summary": {"total_trades": 0, "realized_pnl": 0}}
    
    trade["timestamp"] = datetime.now().isoformat()
    data["trades"].append(trade)
    data["summary"]["total_trades"] += 1
    
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Trade logged: {trade}")

def get_balance():
    resp = CLIENT.get_balance(WALLET.pubkey())
    return resp.value / 1e9

def get_price(input_mint, output_mint, amount_lamports=1000000):
    headers = {"x-api-key": JUPITER_API_KEY} if JUPITER_API_KEY else {}
    url = "https://api.jup.ag/swap/v1/quote"
    params = {"inputMint": input_mint, "outputMint": output_mint, "amount": str(amount_lamports), "slippage": "1"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    # Fallback to lite
    url = "https://lite-api.jup.ag/swap/v1/quote"
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return None

def execute_swap(input_mint, output_mint, amount_lamports):
    """Execute a swap"""
    headers = {"x-api-key": JUPITER_API_KEY} if JUPITER_API_KEY else {}
    
    # Get quote
    url = "https://api.jup.ag/swap/v1/quote"
    params = {"inputMint": input_mint, "outputMint": output_mint, "amount": str(amount_lamports), "slippage": "5"}
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    if resp.status_code != 200:
        # Fallback to lite
        url = "https://lite-api.jup.ag/swap/v1/quote"
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            print(f"Quote failed: {resp.text}")
            return None
    
    quote = resp.json()
    
    # Get swap tx
    swap_url = "https://api.jup.ag/swap/v1/swap"
    swap_params = {"quoteResponse": quote, "userPublicKey": str(WALLET.pubkey()), "wrapAndUnwrapSol": True}
    resp2 = requests.post(swap_url, json=swap_params, headers=headers, timeout=15)
    if resp2.status_code != 200:
        swap_url = "https://lite-api.jup.ag/swap/v1/swap"
        resp2 = requests.post(swap_url, json=swap_params, headers=headers, timeout=15)
        if resp2.status_code != 200:
            print(f"Swap tx failed: {resp2.text}")
            return None
    
    swap_data = resp2.json()
    
    # Sign and send
    swap_tx_b64 = swap_data["swapTransaction"]
    swap_tx_bytes = base64.b64decode(swap_tx_b64)
    signed_tx = VersionedTransaction.from_bytes(swap_tx_bytes)
    tx = VersionedTransaction(signed_tx.message, [WALLET])
    signed_bytes = bytes(tx)
    
    result = CLIENT.send_raw_transaction(signed_bytes)
    
    # Log the trade
    trade = {
        "type": "SWAP",
        "input_token": input_mint[:20] + "...",
        "output_token": output_mint[:20] + "...",
        "input_amount": amount_lamports / 1e9,
        "quote_output": quote.get("outAmount", "0"),
        "tx_hash": str(result),
        "status": "executed"
    }
    log_trade(trade)
    
    return result

def run():
    balance = get_balance()
    print(f"=== Solana Trader ===")
    print(f"Wallet: {str(WALLET.pubkey())[:20]}...")
    print(f"Balance: {balance:.4f} SOL")
    
    # Check SOL -> USDC price
    price_data = get_price(TOKENS["SOL"], TOKENS["USDC"], 1000000)  # 1 SOL
    if price_data:
        usd_price = int(price_data.get("outAmount", 0)) / 1e6
        print(f"SOL price: ${usd_price:.2f}")
        
        # If SOL is high, maybe swap some to USDC for safety
        # For now, just report
        print(f"Price check complete - no trade executed")
    else:
        print("Could not get price")
    
    return {"balance": balance}

if __name__ == "__main__":
    result = run()
    print(json.dumps(result, indent=2))
