"""
Solana DEX Trading via Jupiter
"""
import requests, json, time
from solders.keypair import Keypair
from solders.pubkey import Pubkey

# Wallet
PRIVATE_KEY = bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d")
WALLET = Keypair.from_bytes(PRIVATE_KEY)
print("Wallet:", str(WALLET.pubkey()))

# Jupiter API
JUPITER_API = "https://api.jup.ag"

def get_token_mint(token_symbol):
    """Get token mint address from symbol"""
    # Common tokens
    tokens = {
        "SOL": "So11111111111111111111111111111111111111112",
        "GORK": "GorkRgj6K4K449QA4eF1nawc5CNlQtmsVeiKhPg7FC",  # Example - need to verify
        "USDC": "EPjFWdd5AufqSSQhM9fgxG8LgiJZ94NsAA7L2YnLrFe",
    }
    return tokens.get(token_symbol.upper())

def get_price(input_mint, output_mint):
    """Get price from Jupiter"""
    url = f"{JUPITER_API}/price?inputMint={input_mint}&outputMint={output_mint}"
    resp = requests.get(url, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        return data.get('data', {}).get(input_mint, {}).get('price')
    return None

def get_quote(input_mint, output_mint, amount):
    """Get swap quote from Jupiter"""
    url = f"{JUPITER_API}/quote"
    params = {
        "inputMint": input_mint,
        "outputMint": output_mint,
        "amount": amount,
        "slippage": 5  # 5% max slippage
    }
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    return None

def execute_swap(quote):
    """Execute swap (placeholder - needs solana web3.py + signing)"""
    print("Swap quote received:")
    print(json.dumps(quote, indent=2)[:500])
    print("\n[Would execute swap here - need additional setup]")
    return quote

# Test
print("\n=== Testing Jupiter API ===")
sol_mint = get_token_mint("SOL")
usdc_mint = get_token_mint("USDC")
print(f"SOL mint: {sol_mint}")
print(f"USDC mint: {usdc_mint}")

# Get price (1 SOL in USDC)
price = get_price(sol_mint, usdc_mint)
print(f"\n1 SOL = ${price}" if price else "Price fetch failed")

# Get quote for 0.1 SOL
quote = get_quote(sol_mint, usdc_mint, int(0.1 * 1e9))
if quote:
    print(f"\nQuote for 0.1 SOL:")
    print(f"  Output: {quote.get('outAmount', 0)[:10]}... USDC")
    execute_swap(quote)
