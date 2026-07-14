"""
Force Sell All - Try multiple DEXs
"""
import os
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
import requests, json, sys

# Setup
PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client("https://api.mainnet-beta.solana.com")

# Token mints
SOL_MINT = "So11111111111111111111111111111111111111112"
BIRB_MINT = "G7vQWurMkMMm2dU3iZpXYFTHT9Biio4F4gZCrwFpKNwG"
PUMP_MINT = "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn"

def get_token_balance(mint):
    """Get token balance for a specific mint"""
    try:
        # Get all token accounts for this mint
        url = "https://api.mainnet-beta.solana.com"
        headers = {"Content-Type": "application/json"}
        
        # First get the token account
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                str(WALLET.pubkey()),
                {"mint": mint},
                {"encoding": "jsonParsed"}
            ]
        }
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            if "result" in result and result["result"]["value"]:
                account = result["result"]["value"][0]
                amount = account["account"]["data"]["parsed"]["info"]["amount"]
                return int(amount), account["pubkey"]
    except Exception as e:
        print(f"Error getting balance for {mint}: {e}")
    return 0, None

def get_orca_quote(input_mint, output_mint, amount):
    """Try Orca for quote"""
    try:
        url = "https://api.orca.ai/v1/quote"
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount,
            "slippage": 5
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Orca quote error: {e}")
    return None

def sell_via_jupiter(token_mint, token_amount):
    """Try selling via Jupiter"""
    try:
        # Get quote from Jupiter
        url = "https://quote-api.jup.ag/v6/quote"
        params = {
            "inputMint": token_mint,
            "outputMint": SOL_MINT,
            "amount": token_amount,
            "slippage": 10
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            quotes = resp.json()
            if quotes and len(quotes) > 0:
                quote = quotes[0]
                print(f"Jupiter quote: {quote.get('outAmount')} lamports SOL for {token_amount} lamports token")
                
                # Try to execute swap
                return execute_jupiter_swap(quote)
    except Exception as e:
        print(f"Jupiter error: {e}")
    return None

def execute_jupiter_swap(quote):
    """Execute Jupiter swap"""
    try:
        # Get swap instructions
        url = "https://quote-api.jup.ag/v6/swap"
        data = {
            "quoteResponse": quote,
            "userPublicKey": str(WALLET.pubkey()),
            "wrapAndUnwrapSol": True
        }
        resp = requests.post(url, json=data, timeout=10)
        if resp.status_code == 200:
            swap_data = resp.json()
            # Would need to execute this via solana-py
            print("Got swap instructions, but execution requires more setup")
            return swap_data
    except Exception as e:
        print(f"Swap execution error: {e}")
    return None

# Main execution
print("=== FORCE SELL ALL TOKENS ===\n")

# Check BIRB
print("Checking BIRB...")
birb_amount, birb_account = get_token_balance(BIRB_MINT)
print(f"  BIRB balance: {birb_amount}")
if birb_amount > 0:
    print(f"  Account: {birb_account}")
    # Try Jupiter
    result = sell_via_jupiter(BIRB_MINT, birb_amount)
    if result:
        print(f"  Swap data: {result}")

# Check PUMP
print("\nChecking PUMP...")
pump_amount, pump_account = get_token_balance(PUMP_MINT)
print(f"  PUMP balance: {pump_amount}")
if pump_amount > 0:
    print(f"  Account: {pump_account}")
    result = sell_via_jupiter(PUMP_MINT, pump_amount)
    if result:
        print(f"  Swap data: {result}")

print("\nDone - manual execution required")
