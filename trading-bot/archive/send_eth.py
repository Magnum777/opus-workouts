from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

private_key = '297fbd842e76349299847b3f8d6d688b0403ebdea14ac3c289654c182d796d1d'
from_addr = '0x4d2049F1e4a1d34FF458944c13E4720d2BAbc6A8'
to_addr = '0x706afBE8675e4748F75b4bF80326Be33a22a01F0'

balance_wei = w3.eth.get_balance(from_addr)
# Use a fixed lower gas price to ensure it goes through
# Base network is cheap, let's try 10 Gwei
gas_price = 10 * 10**9  # 10 Gwei

# Use standard gas limit for ETH transfer
gas_limit = 21000

print(f"Balance: {w3.from_wei(balance_wei, 'ether'):.6f} ETH")
print(f"Gas price: {gas_price} wei")
print(f"Gas limit: {gas_limit}")

# Send a safe amount - leave 0.0005 ETH for gas
safe_amount = balance_wei - int(0.0005 * 1e18)
max_value = safe_amount

if max_value <= 0:
    print("ERROR: Not enough balance for gas!")
else:
    print(f"Sending: {w3.from_wei(max_value, 'ether'):.6f} ETH")
    
    tx = {
        'to': to_addr,
        'value': max_value,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': w3.eth.get_transaction_count(from_addr),
        'chainId': 8453  # Base mainnet
    }
    
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    
    print(f"\nSUCCESS!")
    print(f"TX: https://basescan.org/tx/{tx_hash.hex()}")
