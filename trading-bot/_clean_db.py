#!/usr/bin/env python3
"""Clean up stale CLOSED positions from DB, recalculate totals"""
import json
import os
from datetime import datetime, timezone

d = json.load(open('portfolio.db.json'))

# Remove old CLOSED positions (keep only OPEN)
closed_before = sum(1 for p in d['positions'] if p.get('status') == 'CLOSED')
d['positions'] = [p for p in d['positions'] if p.get('status') != 'CLOSED']

# Recalc portfolio total from open positions + USDC + SOL
open_positions = [p for p in d['positions'] if p.get('status') == 'OPEN']
total_from_positions = sum(p.get('current_value_usd', 0) for p in open_positions)
usdc = d['portfolio'].get('usdc_balance', 0)
sol = d['portfolio'].get('sol_balance', 0)
sol_price = d['portfolio'].get('sol_price_usd', 84)
total = total_from_positions + usdc + (sol * sol_price)

d['portfolio']['total_value_usd'] = total
d['portfolio']['positions_count'] = len(open_positions)

json.dump(d, open('portfolio.db.json', 'w'), indent=2)
print(f"Cleaned {closed_before} stale CLOSED positions")
print(f"Open: {len(open_positions)} positions")
print(f"USDC: ${usdc:.2f}")
print(f"SOLD: {sol:.4f} SOL (${sol * sol_price:.2f})")
print(f"Total: ${total:.2f}")

# Show remaining open
for p in open_positions:
    print(f"  {p['token']}: ${p.get('current_value_usd',0):.2f} | {p.get('unrealized_pnl_pct',0):+.1f}%")
