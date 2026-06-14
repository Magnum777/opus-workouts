import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
print(f'[{time.time():.0f}] Starting daemon test...')
import scout_v2 as scout

print(f'[{time.time():.0f}] Getting SOL balance...')
sol = scout.get_sol_balance()
print(f'[{time.time():.0f}] SOL: {sol}')

print(f'[{time.time():.0f}] Getting USDC...')
usdc = scout.get_usdc_balance()
print(f'[{time.time():.0f}] USDC: {usdc}')

print(f'[{time.time():.0f}] Getting holdings...')
holdings = scout.get_all_holdings()
print(f'[{time.time():.0f}] Holdings: {len(holdings)} tokens')

print(f'[{time.time():.0f}] Getting Jupiter price...')
sol_price = scout.get_jupiter_price(scout.SOL_MINT) or 84
print(f'[{time.time():.0f}] SOL price: $ {sol_price}')

print(f'[{time.time():.0f}] DONE')
