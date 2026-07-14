import json
import urllib.request
import datetime
import sys
import os

helius_key = os.environ.get('HELIUS_API_KEY', '')
wallet = os.environ.get('TRADING_BOT_WALLET', '7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA')
base = 'https://mainnet.helius-rpc.com/?api-key=' + helius_key

def rpc_call(method, params):
    payload = json.dumps({
        'jsonrpc': '2.0', 'id': 1,
        'method': method,
        'params': params
    }).encode()
    req = urllib.request.Request(base, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

# 1. SOL Balance
bal = rpc_call('getBalance', [wallet])
sol = bal['result']['value'] / 1e9
print('=== WALLET: ' + wallet + ' ===')
print('')

# 2. Current SOL price
print('--- SOL BALANCE ---')
try:
    req_p = urllib.request.Request('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd', headers={'Accept': 'application/json'})
    with urllib.request.urlopen(req_p, timeout=10) as resp_p:
        prices = json.loads(resp_p.read())
        sol_price = prices.get('solana', {}).get('usd', 0)
except:
    sol_price = 88

total_sol_usd = sol * sol_price
print('SOL: %.6f SOL = $%.2f (at $%.2f/SOL)' % (sol, total_sol_usd, sol_price))

# 3. All token accounts (legacy)
print('\n--- TOKEN ACCOUNTS (Legacy Program) ---')
tokens = rpc_call('getTokenAccountsByOwner', [
    wallet,
    {'programId': 'TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA'},
    {'encoding': 'jsonParsed'}
])

KNOWN_MINTS = {
    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v': 'USDC',
    'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263': 'BONK',
    '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv': 'PENGU',
    '63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9': 'AURA',
    '2tXpgu2DLTsPUf9zFmuZmA4xrYxXKBTpVq9wAM7hzs9y': 'UNKNOWN-45TOKENS',
}

holding_tokens = []
for acc in tokens['result']['value']:
    info = acc['account']['data']['parsed']['info']
    mint = info['mint']
    amt = info['tokenAmount']['uiAmount']
    sym = KNOWN_MINTS.get(mint, mint[:20])
    print('  %20s | %s' % (sym, str(amt)))
    if amt is not None and amt > 0:
        holding_tokens.append({'mint': mint, 'amount': amt, 'symbol': sym})

# 4. Token Extensions
print('\n--- TOKEN ACCOUNTS (Extensions Program) ---')
tokens_ext = rpc_call('getTokenAccountsByOwner', [
    wallet,
    {'programId': 'TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb'},
    {'encoding': 'jsonParsed'}
])
for acc in tokens_ext['result']['value']:
    info = acc['account']['data']['parsed']['info']
    mint = info['mint']
    amt = info['tokenAmount']['uiAmount']
    print('  %20s | %s' % (mint[:20], str(amt)))
    if amt is not None and amt > 0:
        holding_tokens.append({'mint': mint, 'amount': amt, 'symbol': mint[:15]})

print('\n=== NON-ZERO HOLDINGS ===')
for t in holding_tokens:
    print('  %20s | amount: %s | mint: %s' % (t['symbol'], str(t['amount']), t['mint']))

# 5. Last 30 TXs
print('\n=== LAST 30 TRANSACTIONS ===')
sigs = rpc_call('getSignaturesForAddress', [wallet, {'limit': 30}])

for s in sigs['result']:
    bt = s.get('blockTime', 0)
    ts = datetime.datetime.fromtimestamp(bt, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC') if bt else '?'
    sig_short = s['signature'][:30]
    print('  %s...  %s  %s' % (sig_short, ts, s.get('confirmationStatus','?')))

# 6. TX details since May 6
cutoff = datetime.datetime(2026, 5, 6, tzinfo=datetime.timezone.utc)
print('\n=== TX DETAILS (Since May 6) ===')
for s in sigs['result']:
    bt = s.get('blockTime', 0)
    if not bt:
        continue
    ts_dt = datetime.datetime.fromtimestamp(bt, tz=datetime.timezone.utc)
    if ts_dt < cutoff:
        continue
    
    sig = s['signature']
    tx = rpc_call('getTransaction', [sig, {'encoding': 'jsonParsed', 'maxSupportedTransactionVersion': 0}])
    result = tx.get('result', {})
    if not result:
        continue
    meta = result.get('meta', {})
    ts = ts_dt.strftime('%Y-%m-%d %H:%M UTC')
    
    err = meta.get('err')
    status = 'SUCCESS' if err is None else 'FAILED: ' + str(err)
    fee = meta.get('fee', 0) / 1e9
    
    print('\n  [%s] Sig: %s...' % (ts, sig[:40]))
    print('  Status: %s | Fee: %.6f SOL' % (status, fee))
    
    pre_tokens = meta.get('preTokenBalances', [])
    post_tokens = meta.get('postTokenBalances', [])
    
    for pt in pre_tokens:
        if pt.get('owner') == wallet:
            amt = pt.get('uiTokenAmount', {}).get('uiAmountString', '?')
            mint = pt.get('mint', '?')[:30]
            print('  Pre-Token:  %s  mint=%s' % (amt, mint))
    for pt in post_tokens:
        if pt.get('owner') == wallet:
            amt = pt.get('uiTokenAmount', {}).get('uiAmountString', '?')
            mint = pt.get('mint', '?')[:30]
            print('  Post-Token: %s  mint=%s' % (amt, mint))
    
    acct_keys = result.get('transaction', {}).get('message', {}).get('accountKeys', [])
    pre_bals = meta.get('preBalances', [])
    post_bals = meta.get('postBalances', [])
    for i, key in enumerate(acct_keys):
        if key == wallet and i < len(pre_bals) and i < len(post_bals):
            delta = (post_bals[i] - pre_bals[i]) / 1e9
            print('  SOL: %.6f -> %.6f (delta: %+.6f)' % (pre_bals[i]/1e9, post_bals[i]/1e9, delta))
            break
    
    instrs = result.get('transaction', {}).get('message', {}).get('instructions', [])
    for instr in instrs:
        prog = instr.get('programId', '')[:20]
        parsed = instr.get('parsed', {})
        if parsed:
            ptype = parsed.get('type', '')
            pinfo = json.dumps(parsed.get('info', {}))
            print('  %s: %s' % (ptype, pinfo[:120]))
        else:
            d = str(instr.get('data', ''))[:40]
            print('  Program: %s | data=%s' % (prog, d))

print('\n=== AUDIT COMPLETE ===')
total_value = total_sol_usd
for t in holding_tokens:
    print('  Holding: %s %s (mint: %s)' % (str(t['amount']), t['symbol'], t['mint']))
print('Total SOL value: $%.2f' % total_sol_usd)
