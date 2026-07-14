"""
Swap USDC to SOL via lite-api.jup.ag - Fixed signing
"""
import os
import requests, base64, json
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed

PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client(os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"))

USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"

usdc_amount = 5155701
print(f"Swapping {usdc_amount} lamports USDC -> SOL")

# Get quote
quote_url = "https://lite-api.jup.ag/swap/v1/quote"
params = {"inputMint": USDC_MINT, "outputMint": SOL_MINT, "amount": usdc_amount, "slippage": 5}
resp = requests.get(quote_url, params=params, timeout=15)
quote = resp.json()
print(f"Output: {quote.get('outAmount')} lamports SOL")

# Get swap transaction
swap_url = "https://lite-api.jup.ag/swap/v1/swap"
swap_data = {"quoteResponse": quote, "userPublicKey": str(WALLET.pubkey()), "wrapAndUnwrapSol": True}
swap_resp = requests.post(swap_url, json=swap_data, timeout=15)
swap_result = swap_resp.json()
tx_base64 = swap_result.get("swapTransaction")

# Sign and send - try different methods
try:
    # Method 1: VersionedTransaction with sign
    tx = VersionedTransaction.from_bytes(base64.b64decode(tx_base64))
    # Use compile() method to get the signed transaction
    signed_tx = tx.compile()
    # Actually we need to use .sign() but it returns a new tx
    from solders.transaction import Transaction
    # Try creating a new VersionedTransaction with the signed message
    from solders.pubkey import Pubkey
    
    # Get the message and sign it manually
    msg = tx.message
    # Sign the message
    from solders import message
    msg_bytes = message.to_bytes_versioned(msg)
    signature = WALLET.sign_message(msg_bytes)
    
    # Create signed transaction
    signed = VersionedTransaction(msg, [signature])
    
    result = CLIENT.send_raw_transaction(bytes(signed), opts=Confirmed)
    print(f"SUCCESS! Signature: {result.value}")
except Exception as e:
    print(f"Method 1 failed: {e}")
    
    # Try Method 2: Simple RPC call
    try:
        import subprocess
        # Serialize to base64
        tx_b64 = tx_base64
        # Use solana CLI or direct RPC
        cmd = f'''
        curl -s -X POST {os.environ.get('HELIUS_RPC_URL', 'https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE')} -H "Content-Type: application/json" -d '{{"jsonrpc":"2.0","id":1,"method":"sendTransaction","params":["{tx_b64}",{{"encoding":"base64","skipPreflight":true}}]}}'
        '''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        print(f"CLI result: {result.stdout}")
    except Exception as e2:
        print(f"Method 2 also failed: {e2}")
