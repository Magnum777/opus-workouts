"""
Final truth build: rebuild trade-history.json and portfolio.db.json from verified on-chain data.
"""
import json, urllib.request, datetime, sys, os

helius_key = os.environ.get('HELIUS_API_KEY', '')
wallet = os.environ.get('TRADING_BOT_WALLET', '7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA')
base = 'https://mainnet.helius-rpc.com/?api-key=' + helius_key
USDC_MINT = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'

def rpc(method, params):
    payload = json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode()
    req = urllib.request.Request(base, data=payload, headers={'Content-Type':'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

# Get all TXs for this wallet
sigs = rpc('getSignaturesForAddress', [wallet, {'limit': 100}])
print('Real on-chain TXs: %d' % len(sigs['result']))

# Known mints
KNOWN = {
    'pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn': 'PUMP',
    '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv': 'PENGU',
    '6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN': 'TRUMP',
    '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump': 'FARTCOIN',
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263': 'BONK',
    '8GxLxKA8tf3h8JUkXFfP4dNyn6D2vvwyGif5wanRpump': 'AURA',
    '2tXpgu2DLTsPUf9zFmuZmA4xrYxXKBTpVq9wAM7hzs9y': 'HANTA',
}
TOKEN_LEGACY = 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'

# Build complete trade history from on-chain
trades = []
# Track USDC balance to infer BUY/SELL
usdc_balance = 0

for s in reversed(sigs['result']):
    sig = s['signature']
    bt = s.get('blockTime', 0)
    ts = datetime.datetime.fromtimestamp(bt, tz=datetime.timezone.utc).isoformat() if bt else '?'
    
    tx = rpc('getTransaction', [sig, {'encoding': 'jsonParsed', 'maxSupportedTransactionVersion': 0}])
    result = tx.get('result', {})
    if not result:
        continue
    meta = result.get('meta', {})
    err = meta.get('err')
    if err is not None:
        # Record failed TXs for fee accounting
        trades.append({
            'timestamp': ts,
            'action': 'FAILED',
            'tx_hash': sig,
            'error': str(err),
            'fee_sol': meta.get('fee', 0) / 1e9
        })
        continue
    
    fee = meta.get('fee', 0) / 1e9
    
    # Find our wallet's token changes
    pre_tokens = meta.get('preTokenBalances', [])
    post_tokens = meta.get('postTokenBalances', [])
    
    # Find USDC change
    usdc_pre = 0
    usdc_post = 0
    for pt in pre_tokens:
        if pt.get('owner') == wallet and pt.get('mint') == USDC_MINT:
            usdc_pre = float(pt.get('uiTokenAmount', {}).get('uiAmountString', '0') or '0')
    for pt in post_tokens:
        if pt.get('owner') == wallet and pt.get('mint') == USDC_MINT:
            usdc_post = float(pt.get('uiTokenAmount', {}).get('uiAmountString', '0') or '0')
    
    usdc_delta = round(usdc_post - usdc_pre, 6)
    
    # Find non-USDC, non-SOL token changes
    for mint in set(pt.get('mint','') for pt in pre_tokens + post_tokens):
        if mint == USDC_MINT or mint == 'So11111111111111111111111111111111111111112':
            continue
        pre_amt = 0
        post_amt = 0
        for pt in pre_tokens:
            if pt.get('owner') == wallet and pt.get('mint') == mint:
                pre_amt = float(pt.get('uiTokenAmount', {}).get('uiAmountString', '0') or '0')
        for pt in post_tokens:
            if pt.get('owner') == wallet and pt.get('mint') == mint:
                post_amt = float(pt.get('uiTokenAmount', {}).get('uiAmountString', '0') or '0')
        
        delta = post_amt - pre_amt
        if abs(delta) < 0.000001:
            continue
        
        token_name = KNOWN.get(mint, 'TOKEN')
        
        if delta > 0:
            # Bought this token (USDC went down)
            trades.append({
                'timestamp': ts,
                'token': token_name,
                'mint': mint,
                'action': 'BUY',
                'amount': delta,
                'usdc_spent': abs(usdc_delta) if usdc_delta < 0 else 0,
                'tx_hash': sig,
                'fee_sol': fee
            })
        elif delta < 0:
            # Sold this token (USDC went up)
            proceeds = usdc_delta if usdc_delta > 0 else 0
            trades.append({
                'timestamp': ts,
                'token': token_name,
                'mint': mint,
                'action': 'SELL',
                'amount': abs(delta),
                'usdc_proceeds': proceeds,
                'tx_hash': sig,
                'fee_sol': fee
            })

print('\nFull on-chain trade history:')
for t in trades:
    if t['action'] == 'FAILED':
        print('  [%s] FAILED | fee=%.6f SOL | %s' % (t['timestamp'][:16], t['fee_sol'], t.get('error','')[:50]))
    elif t['action'] == 'BUY':
        print('  [%s] BUY  %s | %.4f tokens | USDC -$%.2f' % (t['timestamp'][:16], t['token'], t['amount'], t['usdc_spent']))
    else:
        print('  [%s] SELL %s | %.4f tokens | USDC +$%.2f' % (t['timestamp'][:16], t['token'], t['amount'], t['usdc_proceeds']))

# Write clean trade history  
with open(r'C:\Users\compj\.openclaw\workspace\trading-bot\trade-history.json', 'w') as f:
    json.dump(trades, f, indent=2)
print('\nWritten to trade-history.json (%d trades)' % len(trades))

# Current balances
print('\n--- Current wallet ---')
bal = rpc('getBalance', [wallet])
sol = bal['result']['value'] / 1e9
try:
    req_p = urllib.request.Request('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd', headers={'Accept':'application/json'})
    with urllib.request.urlopen(req_p, timeout=10) as resp:
        p = json.loads(resp.read())
        sol_price = p.get('solana', {}).get('usd', 90)
except:
    sol_price = 90

holdings_list = []
total_usdc = 0
USDC_MINTS = {USDC_MINT, 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'}

for prog in [TOKEN_LEGACY, 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb']:
    tokens = rpc('getTokenAccountsByOwner', [wallet, {'programId': prog}, {'encoding': 'jsonParsed'}])
    for acc in tokens['result']['value']:
        info = acc['account']['data']['parsed']['info']
        mint = info['mint']
        ta = info['tokenAmount']
        raw = int(ta['amount'])
        ui = float(ta.get('uiAmount') or 0)
        dec = int(ta.get('decimals') or 0)
        if raw <= 0 or mint == 'So11111111111111111111111111111111111111112':
            continue
        if mint in USDC_MINTS:
            total_usdc += ui
            continue
        token_name = KNOWN.get(mint, mint[:12])
        try:
            amt = 10 ** dec
            q = urllib.request.Request(f'https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC_MINT}&amount={amt}&slippage=1', headers={'Accept':'application/json'})
            with urllib.request.urlopen(q, timeout=8) as qr:
                price = float(json.loads(qr.read())['outAmount']) / 1e6
        except:
            price = 0
        value_usd = ui * price if price > 0 else 0
        holdings_list.append({
            'token': token_name, 'mint': mint, 'amount': ui, 'amount_raw': raw, 'decimals': dec,
            'value_usd': value_usd, 'value_sol': value_usd / sol_price if sol_price > 0 else 0
        })
        print('  %s: %s tokens ($%.4f)' % (token_name, ui, value_usd))

print('  SOL: %.6f ($%.2f @ $%.2f)' % (sol, sol*sol_price, sol_price))
print('  USDC: $%.2f' % total_usdc)

sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\trading-bot')
import portfolio_db_v2 as pdb
db = pdb.create_default_db()
db['portfolio']['sol_balance'] = sol
db['portfolio']['sol_price_usd'] = sol_price
db['portfolio']['usdc_balance'] = total_usdc
db['portfolio']['total_value_usd'] = sol * sol_price + total_usdc + sum(h['value_usd'] for h in holdings_list)
db['portfolio']['cost_basis_total'] = total_usdc + sum(h['value_usd'] for h in holdings_list)

for h in holdings_list:
    db['positions'].append({
        'token': h['token'], 'mint': h['mint'], 'amount_raw': h['amount_raw'],
        'amount': h['amount'], 'decimals': h['decimals'],
        'current_value_usd': h['value_usd'], 'current_value_sol': h['value_sol'],
        'cost_basis_usd': h['value_usd'], 'buy_price_usd': h['value_usd'], 'buy_price_sol': h['value_sol'],
        'unrealized_pnl_usd': 0, 'unrealized_pnl_pct': 0, 'status': 'OPEN'
    })

db['trades'] = trades

# Calculate realized PNL from SELL trades
sells = [t for t in trades if t['action'] == 'SELL']
total_proceeds = sum(t.get('usdc_proceeds', 0) for t in sells)
# Can't calculate PnL without knowing buy price, but we can report proceeds
db['performance']['total_realized_pnl'] = 0  # Can't track reliably without buy prices
db['performance']['win_rate'] = 0
db['performance']['avg_profit_per_trade'] = 0

pdb.save_db(db)
print('\nFinal state saved to portfolio.db.json!')
print('  Total: $%.2f' % db['portfolio']['total_value_usd'])
print('  Trades: %d (%d successes, %d fails)' % (
    len(trades),
    len([t for t in trades if t['action'] in ('BUY','SELL')]),
    len([t for t in trades if t['action'] == 'FAILED'])
))
