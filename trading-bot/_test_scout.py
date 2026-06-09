import sys, datetime
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\trading-bot')

import scout_v2 as scout
import json

print(f'[{datetime.datetime.now(datetime.UTC).isoformat()}] Scout loaded')

# Try just getting SOL balance
print('Getting SOL balance...')
sol = scout.get_sol_balance()
print(f'SOL: {sol}')

print('Getting USDC balance...')
usdc = scout.get_usdc_balance()
print(f'USDC: {usdc}')

print('Getting holdings...')
holdings = scout.get_all_holdings()
print(f'Holdings: {len(holdings)} tokens')
for m, h in list(holdings.items())[:3]:
    print(f'  {m[:10]}: {h["amount"]}')

print('SCOUT COMPLETE')
