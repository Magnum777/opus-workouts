#!/usr/bin/env python3
import json
d = json.load(open('portfolio.db.json'))
print('=== PORTFOLIO STATUS ===')
print(f'Total: ${d["portfolio"]["total_value_usd"]:.2f}')
print(f'USDC: ${d["portfolio"].get("usdc_balance",0):.2f}')
print(f'SOL: {d["portfolio"].get("sol_balance",0):.4f}')
print()
for p in d.get('positions', []):
    if p.get('status') == 'OPEN':
        print(f'{p["token"]}: ${p.get("current_value_usd",0):.2f} | PnL {p.get("unrealized_pnl_pct",0):+.1f}% | {p.get("opened_at","?")[:10]}')
print()
print(f'Closed positions: {len([p for p in d.get("positions",[]) if p.get("status")=="CLOSED"])}')
