"""
Complete cleanup: audit trade-history against on-chain, rebuild portfolio DB from truth.
"""

import json, urllib.request, datetime, sys, os

helius_key = '2e3fb808-0c5f-4101-8c2b-82b4c4aa0887'
wallet = '7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA'
base = 'https://mainnet.helius-rpc.com/?api-key=' + helius_key

def rpc(method, params):
    payload = json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode()
    req = urllib.request.Request(base, data=payload, headers={'Content-Type':'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

def verify_tx(tx_hash):
    """Check if a tx_hash exists on-chain"""
    try:
        tx = rpc('getTransaction', [tx_hash, {'encoding':'jsonParsed','maxSupportedTransactionVersion':0}])
        return tx.get('result') is not None
    except:
        return False

print('=== STEP 1: VERIFY EACH TRADE IN trade-history.json ===')

with open(r'C:\Users\compj\.openclaw\workspace\trading-bot\trade-history.json') as f:
    old_trades = json.load(f)

# Get all real on-chain TX signatures for this wallet
sigs_result = rpc('getSignaturesForAddress', [wallet, {'limit': 100}])
real_sigs = set(s['signature'] for s in sigs_result['result'])
print('  Known real on-chain TX signatures: %d' % len(real_sigs))

# Also verify the two BIRB/PUMP sells which are from Apr 26 (older than 100 sigs)
# We already know these work from previous audit
real_sigs.add('3ZTvsXd3aXrgE38jcrjxuQwvSuiNeLaY7Hu9iFygKuycCSGhS89NmWUfYTs3JT4dD3YhTpi4yufjQYAnZeXhz69Z')
real_sigs.add('4qJuKqxb8KrGDYDRiRzDtgsNA7QVuaszeohFYvRTpEquqPvqFNUw4yfYyzZGTitDjTSUHr8ZVQgrKhhsKeUgYvYb')

# Check old PENGU/PUMP buys too (Apr 26 - before our 100-tx window)
earlies = ['Me2uVUsKMeTPV9Jk9dT7CWVxeCU45hXtBDPLXbF1xZxx3UWYn5RoP3wvpUt9zdjB62nxTdSDukLugMwKSpGpStD',
           '4CV8fTpANBpJrDjCb17QigtBjEDVf9oZHo7Wbi1QKATXerXgDH76rjXc7jTgCdgTVhdMvgD5SCUQsxFsZffB3FgB']
for h in earlies:
    if verify_tx(h):
        real_sigs.add(h)

real_trades = []
fake_count = 0
total_sol_spent_on_real = 0

for t in old_trades:
    h = t.get('tx_hash', '')
    if isinstance(h, str) and h in real_sigs:
        real_trades.append(t)
        if t.get('action') == 'BUY':
            total_sol_spent_on_real += float(t.get('amount_sol', 0) or 0)
    else:
        fake_count += 1

print('  Real trades: %d' % len(real_trades))
print('  Fake/backtest trades removed: %d' % fake_count)
print('  Total SOL in real buys: %.2f SOL' % total_sol_spent_on_real)

# Write clean history
clean_path = r'C:\Users\compj\.openclaw\workspace\trading-bot\trade-history.json'
backup_path = r'C:\Users\compj\.openclaw\workspace\trading-bot\trade-history.backup.json'
with open(backup_path, 'w') as f:
    json.dump(old_trades, f, indent=2)
print('  Backup written to trade-history.backup.json')
with open(clean_path, 'w') as f:
    json.dump(real_trades, f, indent=2)
print('  Clean trade-history.json written (%d trades)' % len(real_trades))

print('')
print('=== STEP 2: CURRENT ON-CHAIN BALANCES ===')

# SOL
bal = rpc('getBalance', [wallet])
sol = bal['result']['value'] / 1e9

# SOL price
try:
    req_p = urllib.request.Request('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd', headers={'Accept':'application/json'})
    with urllib.request.urlopen(req_p, timeout=10) as resp:
        p = json.loads(resp.read())
        sol_price = p.get('solana', {}).get('usd', 90)
except:
    sol_price = 90

# Token accounts from BOTH programs
USDC_MINT = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
USDC_MINTS = {USDC_MINT, 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'}
SOL_MINT = 'So11111111111111111111111111111111111111112'
KNOWN_TOKENS = {
    '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv': 'PENGU',
    'pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn': 'PUMP', 
    '6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN': 'TRUMP',
    '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump': 'FARTCOIN',
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263': 'BONK',
    'JUPyiwrYJFskUPiHu7LboG7Chgk8KddY9nKNt6cWPnWE': 'JUP',
    'orcaEKTdLwJKMwsSMbKsKzkD5MjycGk5Zn3KdG5fK8VJ': 'ORCA',
    '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R': 'RAY',
    '2tXpgu2DLTsPUf9zFmuZmA4xrYxXKBTpVq9wAM7hzs9y': 'HANTA',
    '8GxLxKA8tf3h8JUkXFfP4dNyn6D2vvwyGif5wanRpump': 'AURA',
}

holdings_list = []
total_usdc = 0

for prog in ['TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA', 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb']:
    tokens = rpc('getTokenAccountsByOwner', [wallet, {'programId': prog}, {'encoding': 'jsonParsed'}])
    for acc in tokens['result']['value']:
        info = acc['account']['data']['parsed']['info']
        mint = info['mint']
        ta = info['tokenAmount']
        raw = int(ta['amount'])
        ui = float(ta.get('uiAmount') or 0)
        dec = int(ta.get('decimals') or 0)
        
        if raw <= 0 or mint == SOL_MINT:
            continue
        
        if mint in USDC_MINTS:
            total_usdc += ui
            continue
        
        token_name = KNOWN_TOKENS.get(mint, mint[:12])
        
        # Price via Jupiter
        try:
            amt = 10 ** dec
            q = urllib.request.Request(
                f'https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC_MINT}&amount={amt}&slippage=1',
                headers={'Accept':'application/json'}
            )
            with urllib.request.urlopen(q, timeout=8) as qr:
                qj = json.loads(qr.read())
                price = float(qj['outAmount']) / 1e6
        except:
            price = 0
        
        value_usd = ui * price if price > 0 else 0
        holdings_list.append({
            'token': token_name, 'mint': mint, 'amount': ui,
            'amount_raw': raw, 'decimals': dec,
            'value_usd': value_usd, 'value_sol': value_usd / sol_price if sol_price > 0 else 0
        })
        print('  %s: %s tokens ($%.4f)' % (token_name, ui, value_usd))

print('')
print('  SOL: %.6f ($%.2f @ $%.2f/SOL)' % (sol, sol*sol_price, sol_price))
print('  USDC: $%.2f' % total_usdc)

print('')
print('=== STEP 3: REBUILD portfolio.db.json ===')

import sys
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\trading-bot')
import portfolio_db_v2 as pdb

db = pdb.create_default_db()
db['portfolio']['sol_balance'] = sol
db['portfolio']['sol_price_usd'] = sol_price
db['portfolio']['usdc_balance'] = total_usdc
db['portfolio']['total_value_usd'] = sol * sol_price + total_usdc + sum(h['value_usd'] for h in holdings_list)
db['portfolio']['cost_basis_total'] = total_usdc + sum(h['value_usd'] for h in holdings_list)

for h in holdings_list:
    pos = {
        'token': h['token'], 'mint': h['mint'],
        'amount_raw': h['amount_raw'], 'amount': h['amount'], 'decimals': h['decimals'],
        'current_value_usd': h['value_usd'], 'current_value_sol': h['value_sol'],
        'cost_basis_usd': h['value_usd'], 'buy_price_usd': h['value_usd'], 'buy_price_sol': h['value_sol'],
        'unrealized_pnl_usd': 0, 'unrealized_pnl_pct': 0, 'status': 'OPEN'
    }
    db['positions'].append(pos)

# Copy real trade history and recalculate performance
db['trades'] = real_trades
sells = [t for t in real_trades if t.get('action') == 'SELL']
if sells:
    total_pnl = sum(t.get('pnl_usd', 0) or 0 for t in sells)
    wins = sum(1 for t in sells if (t.get('pnl_usd', 0) or 0) > 0)
    db['performance']['total_realized_pnl'] = total_pnl
    db['performance']['win_rate'] = (wins / len(sells)) * 100
    db['performance']['avg_profit_per_trade'] = total_pnl / len(sells) if sells else 0

    # Tax summary
    year = '2026'
    db['tax_summary'][year] = {
        'total_trades': len(real_trades),
        'realized_pnl': total_pnl,
        'fees_paid': 0
    }

pdb.save_db(db)

print('')
print('=== FINAL STATE ===')
print('  SOL: %.6f ($%.2f)' % (sol, sol*sol_price))
print('  USDC: $%.2f' % total_usdc)
print('  Positions: %d' % len(holdings_list))
print('  Total: $%.2f' % db['portfolio']['total_value_usd'])
print('  Real trade count: %d' % len(real_trades))
print('')
print('=== CLEANUP COMPLETE ===')
