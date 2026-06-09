#!/usr/bin/env python3
"""Audit the portfolio DB — find and fix bogus PnL numbers"""
import json

d = json.load(open('portfolio.db.json'))

print("=== CORRUPTED FIELDS ===")

# Tax summary is clearly bogus
print(f"\ntax_summary: {json.dumps(d.get('tax_summary', {}), indent=2)}")

# Performance
perf = d.get('performance', {})
print(f"\nperformance:")
print(f"  total_realized_pnl: ${perf.get('total_realized_pnl', 0):.2f}")
print(f"  win_rate: {perf.get('win_rate', 0)}")

# Walk through every trade and compute real PnL
print("\n=== REAL PnL AUDIT ===")
trades = d.get('trades', [])
total_in = 0  # USDC spent on buys
total_out = 0  # USDC recovered on sells

for t in trades:
    if t['action'] == 'BUY':
        total_in += t.get('amount_usdc', 0)
        print(f"BUY  {t['token']}: -${t.get('amount_usdc', 0):.2f}")
    elif t['action'] == 'SELL':
        # The SELL pnl_usd for FARTCOIN is 6360% which is insane - that's a 25-cent buy reported as $25
        pnl = t.get('pnl_usd', 0)
        amt = t.get('amount_usd', 0)
        total_out += pnl  # pnl_usd = amount returned - cost basis... no wait
        print(f"SELL {t['token']}: pnl_usd=${pnl:.2f} amount_usd=${amt:.2f} reason={t.get('reason','?')}")

# Actually compute correctly
print("\n=== RE-CALCULATED ===")
buys = {}  # token -> running total of USDC spent
real_pnl = 0
for t in trades:
    tok = t['token']
    if t['action'] == 'BUY':
        if tok not in buys:
            buys[tok] = []
        buys[tok].append(t.get('amount_usdc', 0))
        all_in = sum(buys[tok])
        print(f"BUY  {tok}: ${t.get('amount_usdc',0):.2f} (total spent=${all_in:.2f})")
    elif t['action'] == 'SELL':
        all_in = sum(buys.get(tok, [0]))
        # For sell: amount_usd is what we got back (if available), otherwise pnl_usd + cost basis
        amt_back = t.get('amount_usd', 0)
        if amt_back == 0 and all_in > 0:
            amt_back = t.get('pnl_usd', 0) + all_in
        elif all_in == 0 and t.get('pnl_pct', 0) == 0 or t.get('pnl_usd', 0) == t.get('amount_usd', 0):
            # This is a bogus sell - pnl == amount_usd means cost basis was 0
            # Real cost basis from BONK stop-loss: $30 buy, got $2.75 back, so pnl = -27.25
            # But DB says pnl = +2.75 which is wrong
            pass
        
        if all_in > 0:
            actual_pnl = amt_back - all_in
        else:
            actual_pnl = t.get('pnl_usd', 0)
            amt_back = actual_pnl  # can't separate cost from return
            
        print(f"SELL {tok}: got back=${amt_back:.2f} spent=${all_in:.2f} actual_pnl=${actual_pnl:.2f} (DB says ${t.get('pnl_usd',0):.2f})")

# Summary
print(f"\nTotal BUYS: ${total_in:.2f}")
print(f"Total SELL returns: ${total_out:.2f}")
