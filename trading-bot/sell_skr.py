"""
Sell SKR
"""
import requests, base64
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

PRIVATE_KEY = bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d")
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client("https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887")

SKR = "SKRbvo6Gf7GondiT3BbTfuRDPqLWei4j2Qy2NPGZhW3"
SOL = "So11111111111111111111111111111111111111112"

# Sell SKR (424 tokens = 424112724 lamports)
amount = 424112724
print(f"Selling {amount} lamports SKR -> SOL")

r = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={SKR}&outputMint={SOL}&amount={amount}&slippage=20", timeout=15)
quote = r.json()
print(f"Quote: {quote.get('outAmount')} lamports SOL")

swap = requests.post("https://lite-api.jup.ag/swap/v1/swap", json={"quoteResponse": quote, "userPublicKey": str(WALLET.pubkey()), "wrapAndUnwrapSol": True}, timeout=15).json()

tx = VersionedTransaction.from_bytes(base64.b64decode(swap["swapTransaction"]))
signed = VersionedTransaction(tx.message, [WALLET])

result = CLIENT.send_raw_transaction(bytes(signed), opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed"))
print(f"Result: {result.value if hasattr(result, 'value') else result}")
