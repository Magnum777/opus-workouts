"""
Sell USDC (Token-2022)
"""
import os
import requests, base64
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client(os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"))

USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL = "So11111111111111111111111111111111111111112"

# Sell USDC (4.16 USDC = 4155701 lamports)
amount = 4155701
print(f"Selling {amount} lamports USDC -> SOL")

r = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={USDC}&outputMint={SOL}&amount={amount}&slippage=15", timeout=15)
quote = r.json()
print(f"Quote: {quote.get('outAmount')} lamports SOL")

swap = requests.post("https://lite-api.jup.ag/swap/v1/swap", json={"quoteResponse": quote, "userPublicKey": str(WALLET.pubkey()), "wrapAndUnwrapSol": True}, timeout=15).json()

tx = VersionedTransaction.from_bytes(base64.b64decode(swap["swapTransaction"]))
signed = VersionedTransaction(tx.message, [WALLET])

result = CLIENT.send_raw_transaction(bytes(signed), opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed"))
print(f"Result: {result.value if hasattr(result, 'value') else result}")
