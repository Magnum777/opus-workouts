import json
from collections import defaultdict, Counter

with open(r'C:\Users\compj\.openclaw\workspace\trading-bot\trade-history.json') as f:
    trades = json.load(f)

# Count by action
c = Counter(t.get('action') for t in trades)
print('Action counts:', dict(c))

# BUY analysis
buys = [t for t in trades if t.get('action') == 'BUY']
print(f'\nTotal BUY trades: {len(buys)}')

sol_per_token = defaultdict(float)
for t in buys:
    token = t.get('token', 'UNKNOWN')
    sol = t.get('amount_sol', 0) or 0
    sol_per_token[token] += sol

print('\nSOL spent per token:')
total_sol = 0
for token, sol in sorted(sol_per_token.items(), key=lambda x: -x[1]):
    print(f'  {token}: {sol:.2f} SOL (${sol * 93:.2f})')
    total_sol += sol
print(f'\nTotal SOL spent on buys: {total_sol:.2f}')
print(f'Total USD at $93/SOL: ${total_sol * 93:.2f}')
print(f'Total USD at $88/SOL (current): ${total_sol * 88:.2f}')

# SELL analysis
sells = [t for t in trades if t.get('action') == 'SELL']
print(f'\nTotal SELL trades: {len(sells)}')
total_proceeds = sum(t.get('proceeds', t.get('amount_usd', 0) or 0) for t in sells)
total_pnl = sum(t.get('pnl_usd', 0) or 0 for t in sells)
print(f'Total proceeds from sells: ${total_proceeds:.2f}')
print(f'Total realized PnL: ${total_pnl:.2f}')

# Last BUY trade
buys_sorted = sorted(buys, key=lambda x: x.get('timestamp', ''))
print(f'\nFirst buy: {buys_sorted[0].get("timestamp", "?")}')
print(f'Last buy: {buys_sorted[-1].get("timestamp", "?")}')

# Show sells
print('\n=== ALL SELLS ===')
for t in sells:
    print(f'  {t.get("timestamp","?")[:19]} | {t.get("token","?")} | {t.get("reason","?")} | proceeds=${t.get("proceeds",0)} | pnl=${t.get("pnl_usd",0)}')

# Check if any trades happened after the May 6th crash
may6 = [t for t in trades if '2026-05-06' in t.get('timestamp','') or '2026-05-07' in t.get('timestamp','') or '2026-05-08' in t.get('timestamp','') or '2026-05-09' in t.get('timestamp','') or '2026-05-10' in t.get('timestamp','')]
print(f'\nTrades after May 6: {len(may6)}')
for t in may6:
    print(f'  {t.get("timestamp","?")[:19]} | {t.get("token","?")} | {t.get("action","?")} | {t.get("reason","?")}')
