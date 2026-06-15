#!/usr/bin/env python3
"""Swap $40 SOL -> USDC to get trading capital back."""
import base64, json, requests, time, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

WALLET = Keypair.from_bytes(bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d"))
H = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
C = Client(H)
WS = str(WALLET.pubkey())
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Swap $40 of SOL -> USDC
sol_amount = int(40 * 1e9 / 170)  # ~0.235 SOL
print(f"Swapping {sol_amount/1e9:.4f} SOL ($40) -> USDC")

r = requests.get(f"https://lite-api.jup.ag/swap/v1/quote?inputMint={SOL_MINT}&outputMint={USDC_MINT}&amount={sol_amount}&slippage=1.5", timeout=10).json()
print(f"Quote: {float(r['inAmount'])/1e9:.4f} SOL -> ${float(r['outAmount'])/1e6:.2f} USDC")

sw = requests.post("https://lite-api.jup.ag/swap/v1/swap", json={
    "quoteResponse": r, "userPublicKey": WS, "wrapAndUnwrapSol": True
}, timeout=30).json()

tx = VersionedTransaction.from_bytes(base64.b64decode(sw["swapTransaction"]))
signed = VersionedTransaction(tx.message, [WALLET])
result = C.send_raw_transaction(bytes(signed), opts=TxOpts(skip_preflight=True, max_retries=5))
tx_hash = result.value if hasattr(result, "value") else str(result)
print(f"TX: {tx_hash}")

confirmed = False
for i in range(30):
    time.sleep(1)
    c = C.get_signature_statuses([tx_hash])
    if c and c.value and c.value[0]:
        s = c.value[0]
        if s.confirmation_status:
            print(f"CONFIRMED! {s.confirmation_status}")
            confirmed = True
            break
        elif s.err:
            print(f"FAILED: {s.err}")
            break

if not confirmed:
    print("Waiting extra...")
    time.sleep(15)

time.sleep(5)
sol = C.get_balance(WALLET.pubkey()).value / 1e9
r2 = requests.post(H, json={"jsonrpc":"2.0","id":1,"method":"getTokenAccountsByOwner","params":[WS,{"mint":USDC_MINT},{"encoding":"jsonParsed"}]}, timeout=10).json()
usdc = float(r2["result"]["value"][0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"]) if r2.get("result",{}).get("value") else 0

print(f"\nAfter: SOL={sol:.4f} USDC=${usdc:.2f} Total=${sol*170+usdc:.2f}")

# Sync DB
db_path = os.path.join(os.path.dirname(__file__), "portfolio.db.json")
with open(db_path) as f:
    db = json.load(f)
db["portfolio"]["sol_balance"] = sol
db["portfolio"]["sol_price_usd"] = 170
db["portfolio"]["usdc_balance"] = usdc
db["portfolio"]["total_value_usd"] = usdc + (sol * 170)
from datetime import datetime, timezone
db["last_updated"] = datetime.now(timezone.utc).isoformat()
with open(db_path, "w") as f:
    json.dump(db, f, indent=2)

print("DB synced")
print(f"\nReady to trade! ${usdc:.2f} USDC available for buys")