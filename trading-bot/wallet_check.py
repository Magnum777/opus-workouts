import requests, json
from solana.rpc.api import Client
from solders.keypair import Keypair

PRIVATE_KEY = bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d")
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client("https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887")

sol = CLIENT.get_balance(WALLET.pubkey()).value / 1e9

try:
    sol_price_data = requests.get("https://price.jup.ag/v6/price?ids=So11111111111111111111111111111111111111112", timeout=10).json()
    sol_usd = sol_price_data["data"]["So11111111111111111111111111111111111111112"]["price"]
except:
    sol_usd = 140  # fallback

TOKENS = {"BIRB": "G7vQWurMkMMm2dU3iZpXYFTHT9Biio4F4gZCrwFpKNwG", "PUMP": "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn", "SKR": "SKRbvo6Gf7GondiT3BbTfuRDPqLWei4j2Qy2NPGZhW3"}
HOLDINGS = {"BIRB": 124035784, "PUMP": 1974473658, "SKR": 1200000000}
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

print("=== WALLET SNAPSHOT ===")
print("Address: " + str(WALLET.pubkey()))
print("SOL: " + str(round(sol, 4)) + " ($" + str(round(sol * sol_usd, 2)) + ")")
print()

total_usd = sol * sol_usd
for name, mint in TOKENS.items():
    try:
        r = requests.get("https://lite-api.jup.ag/swap/v1/quote?inputMint=" + mint + "&outputMint=" + USDC + "&amount=1000000&slippage=1", timeout=10)
        price = float(r.json()["outAmount"]) / 1e6
        value = HOLDINGS[name] * price / 1e6
        total_usd += value
        print(name + ": " + f"{HOLDINGS[name]:,}" + " tokens @ $" + str(round(price, 6)) + " = $" + str(round(value, 2)))
    except Exception as e:
        print(name + ": error - " + str(e))

print()
print("Total Portfolio: $" + str(round(total_usd, 2)))
print("Total Spent:     ~$92 (1.07 SOL)")
print("PnL:             $" + str(round(total_usd - 92, 2)))
