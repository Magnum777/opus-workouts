#!/usr/bin/env python3
"""Live wallet balance check"""
import requests, json, sys
from solders.keypair import Keypair

MINT_TO_NAME = {
    'So11111111111111111111111111111111111111112': 'SOL',
    '6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN': 'TRUMP',
    '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R': 'RAY',
    '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump': 'FARTCOIN',
    'orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE': 'ORCA',
    '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv': 'PENGU',
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263': 'BONK',
    'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN': 'JUP',
    'pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn': 'PUMP',
    '2tXpgu2DLTsPUf9zFmuZmA4xrYxXKBTpVq9wAM7hzs9y': 'HANTA',
    'EKpQGSJtjfaX4B7qfz2aWJ2wSrnKZUEJkE4B6gFuy1r': 'WIF',
}

USDC_MINT = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
HELIUS = 'https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887'
PK = bytes.fromhex('edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d')
WALLET = Keypair.from_bytes(PK)

def jup_price(mint, decimals):
    q = requests.get(f'https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC_MINT}&amount={10**decimals}&slippage=1', timeout=10)
    if q.status_code == 200:
        return float(q.json()['outAmount']) / 1e6
    return 0

# SOL price
sol_price = jup_price('So11111111111111111111111111111111111111112', 9)

# SOL balance
sb = requests.post(HELIUS, json={'jsonrpc':'2.0','id':1,'method':'getBalance','params':[str(WALLET.pubkey())]}, timeout=10).json()
sol_bal = sb['result']['value'] / 1e9

# USDC balance
ur = requests.post(HELIUS, json={'jsonrpc':'2.0','id':1,'method':'getTokenAccountsByOwner','params':[str(WALLET.pubkey()), {'mint': USDC_MINT}, {'encoding':'jsonParsed'}]}, timeout=10).json()
usdc_bal = 0
if ur.get('result',{}).get('value'):
    usdc_bal = float(ur['result']['value'][0]['account']['data']['parsed']['info']['tokenAmount']['uiAmount'] or 0)

# Token holdings (standard token program)
th = requests.post(HELIUS, json={'jsonrpc':'2.0','id':1,'method':'getTokenAccountsByOwner','params':[str(WALLET.pubkey()), {'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'}, {'encoding':'jsonParsed'}]}, timeout=10).json()

# Token holdings (token-2022 program)
th2 = requests.post(HELIUS, json={'jsonrpc':'2.0','id':1,'method':'getTokenAccountsByOwner','params':[str(WALLET.pubkey()), {'programId': 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'}, {'encoding':'jsonParsed'}]}, timeout=10).json()

total = sol_bal * sol_price + usdc_bal
tokens = []

for acc in th.get('result',{}).get('value',[]):
    info = acc['account']['data']['parsed']['info']
    mint = info['mint']
    if mint == USDC_MINT: continue
    amt = float(info['tokenAmount'].get('uiAmount') or 0)
    if amt <= 0: continue
    dec = int(info['tokenAmount'].get('decimals',6))
    name = MINT_TO_NAME.get(mint, mint[:10])
    price = jup_price(mint, dec)
    val = amt * price
    total += val
    tokens.append((name, f'{amt:.6f}', f'${price:.8f}', f'${val:.4f}'))

for acc in th2.get('result',{}).get('value',[]):
    info = acc['account']['data']['parsed']['info']
    mint = info['mint']
    if mint == USDC_MINT: continue
    amt = float(info['tokenAmount'].get('uiAmount') or 0)
    if amt <= 0: continue
    dec = int(info['tokenAmount'].get('decimals',6))
    name = MINT_TO_NAME.get(mint, mint[:10])
    price = jup_price(mint, dec)
    val = amt * price
    total += val
    tokens.append((name, f'{amt:.6f}', f'${price:.8f}', f'${val:.4f}'))

print('=== LIVE PORTFOLIO SNAPSHOT ===')
print(f'SOL: {sol_bal:.6f} @ ${sol_price:.2f} = ${sol_bal*sol_price:.2f}')
print(f'USDC: ${usdc_bal:.4f}')
for n, a, p, v in tokens:
    print(f'{n}: {a} * {p} = {v}')
print(f'---')
print(f'TOTAL: ${total:.2f}')
