#!/usr/bin/env python3
"""Live sync from blockchain"""
import json, requests

wallet = '7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA'
url = 'https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887'

# SOL
r = requests.post(url, json={'jsonrpc':'2.0','id':1,'method':'getBalance','params':[wallet]}, timeout=10)
sol = r.json()['result']['value'] / 1e9
print(f"SOL: {sol:.4f}")

# Get SOL price
r = requests.get("https://lite-api.jup.ag/swap/v1/quote?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=1000000000&slippage=1", timeout=8)
sol_price = float(r.json()['outAmount']) / 1e6
print(f"SOL price: ${sol_price:.2f}")
print(f"SOL value: ${sol * sol_price:.2f}")

# USDC
r = requests.post(url, json={'jsonrpc':'2.0','id':1,'method':'getTokenAccountsByOwner','params':[wallet,{'mint':'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'},{'encoding':'jsonParsed'}]}, timeout=10)
usdc = 0
try:
    accounts = r.json()['result']['value']
    if accounts:
        usdc = float(accounts[0]['account']['data']['parsed']['info']['tokenAmount']['uiAmount'] or 0)
except:
    pass
print(f"USDC: ${usdc:.2f}")

# All token holdings
known = {
    'So11111111111111111111111111111111111111112': 'SOL',
    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v': 'USDC',
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263': 'BONK',
    '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv': 'PENGU',
    'pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn': 'PUMP',
    '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump': 'FARTCOIN',
    '6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN': 'TRUMP',
    'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN': 'JUP',
    'orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE': 'ORCA',
    '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R': 'RAY',
}

print("\n=== TOKEN HOLDINGS ===")
r = requests.post(url, json={'jsonrpc':'2.0','id':1,'method':'getTokenAccountsByOwner','params':[wallet,{'programId':'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'},{'encoding':'jsonParsed'}]}, timeout=10)
for acct in r.json()['result']['value']:
    info = acct['account']['data']['parsed']['info']
    mint = info['mint']
    amt = float(info['tokenAmount']['uiAmount'] or 0)
    if amt > 0 and mint != 'So11111111111111111111111111111111111111112':
        name = known.get(mint, mint[:10])
        print(f"  {name}: {amt:.6f}")

# Also check Token-2022 (for BONK)
r = requests.post(url, json={'jsonrpc':'2.0','id':1,'method':'getTokenAccountsByOwner','params':[wallet,{'programId':'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'},{'encoding':'jsonParsed'}]}, timeout=10)
try:
    for acct in r.json()['result']['value']:
        info = acct['account']['data']['parsed']['info']
        mint = info['mint']
        amt = float(info['tokenAmount']['uiAmount'] or 0)
        if amt > 0:
            name = known.get(mint, mint[:10])
            print(f"  {name} (Token2022): {amt:.6f}")
except:
    pass

total = sol * sol_price + usdc
print(f"\nTotal: ${total:.2f}")
