import json
with open('portfolio.db.json') as f:
    data = json.load(f)

print('=== PORTFOLIO ===')
print('Last Updated:', data.get('last_updated', '?'))
sol = str(round(data['portfolio']['sol_balance'], 6))
sv = str(round(data['portfolio']['sol_price_usd'], 2))
usdc = str(round(data['portfolio']['usdc_balance'], 2))
tv = str(round(data['portfolio']['total_value_usd'], 4))
print('SOL:', sol, '@ $' + sv)
print('USDC: $' + usdc)
print('Total Value: $' + tv)
print('Positions:', data['portfolio']['positions_count'])

if data['positions']:
    print()
    print('=== OPEN POSITIONS ===')
    for p in data['positions']:
        pnl = f"{p['unrealized_pnl_pct']:+.2f}%"
        val = str(round(p['current_value_usd'], 4))
        print(' ', p['token'], ': $' + val, '(' + pnl + ')')

signals = data.get('signals', [])
buys = [s for s in signals if s.get('recommendation') in ('BUY', 'STRONG_BUY')]
sells = [s for s in signals if s.get('recommendation') in ('SELL', 'STRONG_SELL')]
holds = [s for s in signals if s.get('recommendation') == 'HOLD']

print()
print('=== SIGNALS ===')
print('Total:', len(signals), '| BUY:', len(buys), '| SELL:', len(sells), '| HOLD:', len(holds))
if buys:
    for b in buys:
        print(' BUY', b['token'], '(' + b['category'] + ')', 'Conf:', b['confidence'], '% @ $' + str(b['current_price']))
if sells:
    for s in sells:
        print(' SELL', s['token'], 'Conf:', s['confidence'], '%')
