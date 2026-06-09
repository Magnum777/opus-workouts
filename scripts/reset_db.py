"""
Hard reset portfolio.db.json to reflect actual on-chain balances.
Call this once to wipe stale positions.
"""

import json, urllib.request, datetime, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'trading-bot'))
import portfolio_db_v2 as pdb

helius_key = '2e3fb808-0c5f-4101-8c2b-82b4c4aa0887'
base = 'https://mainnet.helius-rpc.com/?api-key=' + helius_key
wallet = '7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA'
USDC_MINT = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
SOL_MINT = 'So11111111111111111111111111111111111111112'
TOKEN_LEGACY = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'
TOKEN_EXT = 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'

KNOWN_TOKENS = {
    'pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn': 'PUMP',
    '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump': 'FARTCOIN',
    '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv': 'PENGU',
    '6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN': 'TRUMP',
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263': 'BONK',
    'JUPyiwrYJFskUPiHu7LboG7Chgk8KddY9nKNt6cWPnWE': 'JUP',
    'orcaEKTdLwJKMwsSMbKsKzkD5MjycGk5Zn3KdG5fK8VJ': 'ORCA',
    '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R': 'RAY',
    '2tXpgu2DLTsPUf9zFmuZmA4xrYxXKBTpVq9wAM7hzs9y': 'HANTA',
}

def rpc(method, params):
    payload = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}).encode()
    req = urllib.request.Request(base, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

# 1. Get SOL balance
sol_bal = rpc('getBalance', [wallet])
sol = sol_bal['result']['value'] / 1e9

# Get SOL price
try:
    req_p = urllib.request.Request('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd', headers={'Accept': 'application/json'})
    with urllib.request.urlopen(req_p, timeout=10) as resp_p:
        prices = json.loads(resp_p.read())
        sol_price = prices.get('solana', {}).get('usd', 90)
except:
    sol_price = 90

# 2. Get all token accounts from both programs
holdings_list = []
total_usdc = 0
USDC_MINTS = {'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'}

for prog in [TOKEN_LEGACY, TOKEN_EXT]:
    tokens = rpc('getTokenAccountsByOwner', [wallet, {'programId': prog}, {'encoding': 'jsonParsed'}])
    for acc in tokens['result']['value']:
        info = acc['account']['data']['parsed']['info']
        mint = info['mint']
        ta = info['tokenAmount']
        raw = int(ta['amount'])
        ui = float(ta.get('uiAmount') or 0)
        decimals = int(ta.get('decimals') or 0)
        
        if raw <= 0 or mint == SOL_MINT:
            continue
        
        token_name = KNOWN_TOKENS.get(mint, mint[:12])
        
        # Get price via Jupiter
        try:
            amt_for_quote = 10 ** decimals
            q = urllib.request.Request(
                f'https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC_MINT}&amount={amt_for_quote}&slippage=1',
                headers={'Accept': 'application/json'}
            )
            with urllib.request.urlopen(q, timeout=8) as qr:
                qj = json.loads(qr.read())
                price = float(qj['outAmount']) / 1e6
        except:
            price = 0
        
        value_usd = ui * price if price > 0 else 0
        value_sol = value_usd / sol_price if sol_price > 0 else 0
        
        # Check if stablecoin
        if mint in USDC_MINTS:
            total_usdc += ui
            continue
        
        holdings_list.append({
            'token': token_name,
            'mint': mint,
            'amount': ui,
            'amount_raw': raw,
            'decimals': decimals,
            'value_usd': value_usd,
            'value_sol': value_sol
        })
        
        print('  %s: %s tokens, $%.2f (mint: %s...)' % (token_name, ui, value_usd, mint[:16]))

print('')
print('Real on-chain balances:')
print('  SOL: %.6f ($%.2f @ $%.2f/SOL)' % (sol, sol*sol_price, sol_price))
print('  USDC: $%.2f' % total_usdc)
for h in holdings_list:
    print('  %s: %.4f tokens ($%.4f)' % (h['token'], h['amount'], h['value_usd']))

# 3. Create fresh DB
db = pdb.create_default_db()
db['portfolio']['sol_balance'] = sol
db['portfolio']['sol_price_usd'] = sol_price
db['portfolio']['usdc_balance'] = total_usdc
db['portfolio']['total_value_usd'] = sol * sol_price + total_usdc + sum(h['value_usd'] for h in holdings_list)
db['portfolio']['positions_count'] = len(holdings_list)
db['portfolio']['cost_basis_total'] = total_usdc + sum(h['value_usd'] for h in holdings_list)

# Add positions for non-stable holdings
for h in holdings_list:
    pos = {
        'token': h['token'],
        'mint': h['mint'],
        'amount_raw': h['amount_raw'],
        'amount': h['amount'],
        'decimals': h['decimals'],
        'current_value_usd': h['value_usd'],
        'current_value_sol': h['value_sol'],
        'cost_basis_usd': h['value_usd'],
        'buy_price_usd': h['value_usd'],
        'buy_price_sol': h['value_sol'],
        'unrealized_pnl_usd': 0,
        'unrealized_pnl_pct': 0,
        'status': 'OPEN'
    }
    db['positions'].append(pos)

# Preserve existing trade history from old DB
old_db = pdb.load_db()
if old_db.get('trades'):
    db['trades'] = old_db['trades']
    # Recalculate performance metrics
    sells = [t for t in old_db['trades'] if t.get('action') == 'SELL']
    if sells:
        total_pnl = sum(t.get('pnl_usd', 0) for t in sells)
        wins = len([t for t in sells if t.get('pnl_usd', 0) > 0])
        db['performance']['total_realized_pnl'] = total_pnl
        db['performance']['win_rate'] = (wins / len(sells)) * 100 if sells else 0
        db['performance']['avg_profit_per_trade'] = total_pnl / len(sells) if sells else 0

pdb.save_db(db)
print('')
print('DB saved!')
print('Total value: $%.2f' % db['portfolio']['total_value_usd'])
print('  SOL: $%.2f' % (sol * sol_price))
print('  USDC: $%.2f' % total_usdc)
print('  Positions: %d' % len(holdings_list))
for h in holdings_list:
    print('    %s: $%.2f' % (h['token'], h['value_usd']))
