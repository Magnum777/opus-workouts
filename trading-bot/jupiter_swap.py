"""
Jupiter Solana Swap - Test Trade
"""
import os
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
import requests, json, base64

# Setup
PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client("https://api.mainnet-beta.solana.com")

# Token mints
SOL_MINT = Pubkey.from_string("So11111111111111111111111111111111111111112")
USDC_MINT = Pubkey.from_string("EPjFWdd5AufqSSQhM9fgxG8LgiJZ94NsAA7L2YnLrFe")

print("Wallet:", str(WALLET.pubkey()))

# Check balance
def get_balance():
    resp = CLIENT.get_balance(WALLET.pubkey())
    lamports = resp.value
    return lamports / 1e9

print(f"Balance: {get_balance()} SOL")

# Get Jupiter quote
def get_quote():
    # Swap 0.01 SOL to USDC
    amount_lamports = int(0.01 * 1e9)
    
    url = "https://quote-api.jup.ag/v6/quote"
    params = {
        "inputMint": str(SOL_MINT),
        "outputMint": str(USDC_MINT),
        "amount": amount_lamports,
        "slippage": 5,
        "restrictIntermediateTokens": True
    }
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if data:
            return data[0]
    return None

quote = get_quote()
if quote:
    print(f"\nQuote received:")
    print(f"  Input: {quote.get('inAmount', 0)} lamports SOL")
    print(f"  Output: {quote.get('outAmount', 0)} lamports USDC")
    print(f"  Price: {quote.get('priceImpactPct', 0)}% impact")
else:
    print("Failed to get quote")
