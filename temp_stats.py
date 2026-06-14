import json
with open(r'C:\Users\compj\.openclaw\workspace\portfolio.db.json', 'r') as f:
    data = json.load(f)

perf = data.get('performance', {})
portfolio = data.get('portfolio', {})
print(f'Total trades: {perf.get(\"total_trades\", \"N/A\")}')
print(f'Realized PnL: ')
print(f'Win rate: {perf.get(\"win_rate\", 0):.1f}%')
print(f'Portfolio value: ')

wins = 0
losses = 0
for p in data.get('positions', []):
    if p.get('status') == 'CLOSED':
        pnl = p.get('realized_pnl_usd', 0)
        if pnl > 0:
            wins += 1
        else:
            losses += 1

print(f'Wins: {wins}, Losses: {losses}')
print(f'Win rate calc: {wins/(wins+losses)*100 if wins+losses > 0 else 0:.1f}%')
