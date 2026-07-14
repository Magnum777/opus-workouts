"""
Sell JEET tokens -> SOL via Jupiter
"""
import os
import requests, base64, json
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client(os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"))

JEET = "HPHau8yipXRgJShyhFxBpeaAfCc5rzkb3KduuRErzZPh"
SOL = "So11111111111111111111111111111111111111112"

# Get actual balance first
print("Checking JEET balance...")
data = {
    "jsonrpc": "2.0", "id": 1, "method": "getTokenAccountsByOwner",
    "params": [
        str(WALLET.pubkey()),
        {"mint": JEET},
        {"encoding": "jsonParsed"}
    ]
}
resp = requests.post("https://api.mainnet-beta.solana.com", json=data, headers={"Content-Type": "application/json"}, timeout=10)
result = resp.json()
if "result" in result and result["result"]["value"]:
    account = result["result"]["value"][0]
    amount = int(account["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])
    decimals = account["account"]["data"]["parsed"]["info"]["tokenAmount"]["decimals"]
    print(f"Balance: {amount} raw ({amount / 10**decimals:.6f} JEET)")
else:
    print("No JEET balance found")
    print(json.dumps(result, indent=2)[:500])
    exit()

if amount == 0:
    print("No JEET to sell")
    exit()

print(f"\nSelling {amount} raw JEET -> SOL via Jupiter...")
r = requests.get(
    f"https://lite-api.jup.ag/swap/v1/quote?inputMint={JEET}&outputMint={SOL}&amount={amount}&slippage=50",
    timeout=15
)
quote = r.json()
print(f"Quote outAmount: {quote.get('outAmount')} lamports SOL")
print(f"Quote: {json.dumps(quote, indent=2)[:500]}")

if "outAmount" not in quote or int(quote.get("outAmount", 0)) == 0:
    print("No viable quote - trying higher slippage or different route")
    exit()

print("\nExecuting swap...")
swap = requests.post(
    "https://lite-api.jup.ag/swap/v1/swap",
    json={
        "quoteResponse": quote,
        "userPublicKey": str(WALLET.pubkey()),
        "wrapAndUnwrapSol": True,
        "dynamicComputeUnitLimit": True
    },
    timeout=15
).json()

if "swapTransaction" not in swap:
    print(f"Swap failed: {json.dumps(swap, indent=2)[:500]}")
    exit()

tx = VersionedTransaction.from_bytes(base64.b64decode(swap["swapTransaction"]))
signed = VersionedTransaction(tx.message, [WALLET])

result = CLIENT.send_raw_transaction(bytes(signed), opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed"))
print(f"Result: {result}")
