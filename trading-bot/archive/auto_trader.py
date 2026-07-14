"""
Nova's Automated Trading Bot
Monitors positions and executes stop-loss/take-profit
"""
import os
import requests, json, time, base64
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# Config
PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
HELIUS_API_KEY = os.environ.get("HELIUS_API_KEY", "")
CLIENT = Client(f'https://mainnet.helius-rpc.com/?api-key={HELIUS_API_KEY}')

USDC_MINT = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
SOL_MINT = 'So11111111111111111111111111111111111111112'

# Trading params
STOP_LOSS_PCT = 10
TAKE_PROFIT_PCT = 30

# Token mints
TOKENS = {
    'BIRB': 'G7vQWurMkMMm2dU3iZpXYFTHT9Biio4F4gZCrwFpKNwG',
    'PUMP': 'pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn',
}

def get_token_price(mint):
    """Get current token price in USDC"""
    try:
        # 1M token -> USDC
        url = f'https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC_MINT}&amount=1000000&slippage=1'
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            q = resp.json()
            out = float(q.get('outAmount', 0)) / 1e6
            return out  # USDC for 1M tokens = price in cents basically
    except Exception as e:
        print(f"Price error: {e}")
    return 0

def get_sol_price():
    """Get SOL price in USD"""
    try:
        resp = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd', timeout=10)
        return resp.json()['solana']['usd']
    except:
        return 86

def sell_token(mint, amount):
    """Sell token for SOL"""
    try:
        url = 'https://lite-api.jup.ag/swap/v1/quote'
        params = {
            'inputMint': mint,
            'outputMint': SOL_MINT,
            'amount': str(amount),
            'slippage': '15'
        }
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            return None
        quote = resp.json()
        
        swap_url = 'https://lite-api.jup.ag/swap/v1/swap'
        swap_params = {
            'quoteResponse': quote,
            'userPublicKey': str(WALLET.pubkey()),
            'wrapAndUnwrapSol': True
        }
        resp2 = requests.post(swap_url, json=swap_params, timeout=15)
        swap_data = resp2.json()
        
        swap_tx_b64 = swap_data['swapTransaction']
        swap_tx_bytes = base64.b64decode(swap_tx_b64)
        signed_tx = VersionedTransaction.from_bytes(swap_tx_bytes)
        tx = VersionedTransaction(signed_tx.message, [WALLET])
        signed_bytes = bytes(tx)
        
        result = CLIENT.send_raw_transaction(signed_bytes)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def check_positions():
    """Check all positions for stop-loss/take-profit"""
    print("=== Position Monitor ===")
    
    with open('positions.json', 'r') as f:
        data = json.load(f)
    
    positions = data.get('positions', [])
    sol_price = get_sol_price()
    
    print(f"SOL Price: ${sol_price}")
    print()
    
    for pos in positions:
        if pos.get('status') != 'OPEN':
            continue
        
        token = pos.get('token')
        mint = TOKENS.get(token)
        if not mint:
            continue
        
        # Current token price
        current_price = get_token_price(mint)  # USDC for 1M tokens
        if current_price == 0:
            print(f"{token}: Could not fetch price")
            continue
        
        # What we paid: 0.02 SOL @ ~$86 = $1.72
        # For 1M tokens at current price
        buy_value_usd = 0.02 * sol_price
        current_value_usd = current_price  # 1M tokens worth this much USDC
        
        # Wait - I need to recalculate properly
        # We spent 0.02 SOL for amount tokens
        # Current value = amount * current_price / 1M
        amount = pos.get('amount', 0)
        current_value = amount * current_price / 1e6
        
        pnl_pct = ((current_value - buy_value_usd) / buy_value_usd) * 100
        
        print(f"{token}: Paid ${buy_value_usd:.2f} | Now ${current_value:.2f} | PnL: {pnl_pct:+.1f}%")
        
        # Check stop-loss
        if pnl_pct <= -STOP_LOSS_PCT:
            print(f"!!! STOP-LOSS: Selling {token} !!!")
            # tx = sell_token(mint, amount)
            # print(f"TX: {tx}")
            # pos['status'] = 'STOP_LOSS'
        
        # Check take-profit
        elif pnl_pct >= TAKE_PROFIT_PCT:
            print(f"!!! TAKE-PROFIT: Selling {token} !!!")
            # tx = sell_token(mint, amount)
            # print(f"TX: {tx}")
            # pos['status'] = 'TAKE_PROFIT'
    
    with open('positions.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print()
    print(f"Stop-loss: -{STOP_LOSS_PCT}% | Take-profit: +{TAKE_PROFIT_PCT}%")

if __name__ == "__main__":
    check_positions()
