#!/usr/bin/env python3
"""Sync portfolio DB to live blockchain holdings"""
import os
import requests, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import portfolio_db_v2 as pdb
from solders.keypair import Keypair

PK = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PK)
H = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")
USDC = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'

MINT_TO_NAME = {
    '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv': 'PENGU',
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263': 'BONK',
    'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN': 'JUP',
    'orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE': 'ORCA',
    '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R': 'RAY',
    '6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN': 'TRUMP',
    '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump': 'FARTCOIN',
    'pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn': 'PUMP',
    '2tXpgu2DLTsPUf9zFmuZmA4xrYxXKBTpVq9wAM7hzs9y': 'HANTA',
    'EKpQGSJtjfaX4B7qfz2aWJ2wSrnKZUEJkE4B6gFuy1r': 'WIF',
}

# SOL price
r = requests.get('https://lite-api.jup.ag/swap/v1/quote?inputMint=So11111111111111111111111111111111111111112&outputMint='+USDC+'&amount=1000000000&slippage=1', timeout=10)
sol_price = float(r.json()['outAmount']) / 1e6

# SOL balance
sb = requests.post(H, json={'jsonrpc':'2.0','id':1,'method':'getBalance','params':[str(WALLET.pubkey())]}, timeout=10).json()
sol_bal = sb['result']['value'] / 1e9

# USDC balance
ur = requests.post(H, json={'jsonrpc':'2.0','id':1,'method':'getTokenAccountsByOwner','params':[str(WALLET.pubkey()), {'mint': USDC}, {'encoding':'jsonParsed'}]}, timeout=10).json()
usdc = 0
if ur.get('result',{}).get('value'):
    usdc = float(ur['result']['value'][0]['account']['data']['parsed']['info']['tokenAmount']['uiAmount'] or 0)

total_val = sol_bal * sol_price + usdc
new_positions = []

# Get token holdings for all programs
for prog in ['TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb']:
    ar = requests.post(H, json={'jsonrpc':'2.0','id':1,'method':'getTokenAccountsByOwner','params':[str(WALLET.pubkey()), {'programId': prog}, {'encoding':'jsonParsed'}]}, timeout=10).json()
    for acc in ar.get('result',{}).get('value',[]):
        info = acc['account']['data']['parsed']['info']
        mint = info['mint']
        if mint == USDC: 
            continue
        amt = float(info['tokenAmount'].get('uiAmount') or 0)
        if amt <= 0: 
            continue
        dec = int(info['tokenAmount'].get('decimals', 6))
        raw = int(info['tokenAmount']['amount'])
        name = MINT_TO_NAME.get(mint, mint[:10])
        
        q = requests.get('https://lite-api.jup.ag/swap/v1/quote?inputMint='+mint+'&outputMint='+USDC+'&amount='+str(10**dec)+'&slippage=1', timeout=8)
        if q.status_code == 200:
            price = float(q.json()['outAmount']) / 1e6
        else:
            price = 0
        val = amt * price
        total_val += val
        
        new_positions.append({
            'token': name,
            'mint': mint,
            'status': 'OPEN',
            'amount_raw': raw,
            'amount': amt,
            'decimals': dec,
            'current_price_usd': price,
            'current_value_usd': val,
            'current_value_sol': val / sol_price if sol_price > 0 else 0,
            'cost_basis_usd': val,
            'buy_price_usd': price,
            'buy_price_sol': price / sol_price if sol_price > 0 else 0,
            'unrealized_pnl_usd': 0,
            'unrealized_pnl_pct': 0,
        })

# Reset DB
db = pdb.load_db()
db['portfolio']['sol_balance'] = sol_bal
db['portfolio']['sol_price_usd'] = sol_price
db['portfolio']['usdc_balance'] = usdc
db['portfolio']['total_value_usd'] = total_val
db['portfolio']['positions_count'] = len(new_positions)
db['positions'] = new_positions
db['trades'] = []
db['signals'] = []
db['performance'] = {
    'daily_pnl': {}, 'win_rate': 0, 'avg_profit_per_trade': 0,
    'total_realized_pnl': 0, 'total_unrealized_pnl': 0,
    'daily_avg': 0, 'projected_days_to_1000': 999
}
db['risk_metrics']['daily_trade_count'] = 0
db['risk_metrics']['consecutive_losses'] = 0
db['risk_metrics']['last_trade_time'] = None
pdb.save_db(db)

print('=== DB SYNCED TO ACTUAL HOLDINGS ===')
print('SOL: {:.6f} @ ${:.2f}'.format(sol_bal, sol_price))
print('USDC: ${:.2f}'.format(usdc))
print('Open positions: {}'.format(len(new_positions)))
for p in new_positions:
    print('  {}: {:.4f} (${:.2f})'.format(p['token'], p['amount'], p['current_value_usd']))
print('TOTAL: ${:.2f}'.format(total_val))
