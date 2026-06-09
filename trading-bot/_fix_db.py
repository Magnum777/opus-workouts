#!/usr/bin/env python3
"""Fix corrupted PnL in portfolio DB, nuke bogus tax_summary"""
import json

d = json.load(open('portfolio.db.json'))

# 1. Nuke bogus tax_summary
d['tax_summary'] = {"2026": {"total_trades": 0, "realized_pnl": 0, "fees_paid": 0}}
print("Nuked bogus tax_summary (was $88,566)")

# 2. Correct FARTCOIN SELL: $25 buy, $25.59 return = $0.59 profit
for t in d['trades']:
    if t['token'] == 'FARTCOIN' and t['action'] == 'SELL' and t.get('pnl_pct', 0) > 100:
        # This is the first FARTCOIN sell that recorded 6360% profit
        # Find corresponding buys before this sell
        pre_buys = [x for x in d['trades'] if x['token'] == 'FARTCOIN' and x['action'] == 'BUY' and x['timestamp'] < t['timestamp']]
        cost_basis = sum(x.get('amount_usdc', 0) for x in pre_buys)
        if cost_basis > 0:
            real_pnl = t.get('amount_usd', 0) - cost_basis
            print(f"FARTCOIN: cost_basis=${cost_basis:.2f} return=${t.get('amount_usd',0):.2f} real_pnl=${real_pnl:.2f}")
            t['pnl_usd'] = round(real_pnl, 2)
            t['pnl_pct'] = round(real_pnl / cost_basis * 100, 2) if cost_basis > 0 else 0

# 3. Correct BONK STOP_LOSS: $30 buy, $2.75 return = -$27.25 loss
for t in d['trades']:
    if t['token'] == 'BONK' and t.get('reason') == 'STOP_LOSS':
        # First BONK SELL - got $2.75 back on $30 buy
        pre_buys = [x for x in d['trades'] if x['token'] == 'BONK' and x['action'] == 'BUY' and x['timestamp'] < t['timestamp']]
        cost_basis = sum(x.get('amount_usdc', 0) for x in pre_buys[:1])  # Only first buy
        if cost_basis > 0 and t.get('amount_usd', 0) > 0:
            real_pnl = t.get('amount_usd', 0) - cost_basis
            print(f"BONK STOP-LOSS: cost_basis=${cost_basis:.2f} return=${t.get('amount_usd',0):.2f} real_pnl=${real_pnl:.2f}")
            t['pnl_usd'] = round(real_pnl, 2)
            t['pnl_pct'] = round(real_pnl / cost_basis * 100, 2)

# 4. Correct BONK FORCED_SELL: combines both legs
# First buy $30 (lost -$27.25), second buy $30 (sold $27.51 = -$2.49)
# Total on BONK: -$29.74
for t in d['trades']:
    if t['token'] == 'BONK' and t.get('reason') == 'FORCED_SELL (blocklist)':
        # All BONK buys before this sell
        pre_buys = [x for x in d['trades'] if x['token'] == 'BONK' and x['action'] == 'BUY' and x['timestamp'] < t['timestamp']]
        cost_basis = sum(x.get('amount_usdc', 0) for x in pre_buys)
        if cost_basis > 0 and t.get('amount_usd', 0) > 0:
            real_pnl = t.get('amount_usd', 0) - cost_basis
            print(f"BONK FORCED_SELL: cost_basis=${cost_basis:.2f} return=${t.get('amount_usd',0):.2f} real_pnl=${real_pnl:.2f}")
            t['pnl_usd'] = round(real_pnl, 2)
            t['pnl_pct'] = round(real_pnl / cost_basis * 100, 2)

# 5. Recalculate performance
trades = d['trades']
sell_trades = [t for t in trades if t['action'] == 'SELL' and isinstance(t.get('pnl_usd'), (int, float))]
realized_pnl = sum(t['pnl_usd'] for t in sell_trades)
winners = sum(1 for t in sell_trades if t['pnl_usd'] > 0)
losers = sum(1 for t in sell_trades if t['pnl_usd'] < 0)
total_trades = winners + losers
win_rate = (winners / total_trades * 100) if total_trades > 0 else 0
avg_profit = (realized_pnl / total_trades) if total_trades > 0 else 0

d['performance']['total_realized_pnl'] = round(realized_pnl, 2)
d['performance']['win_rate'] = round(win_rate, 1)
d['performance']['avg_profit_per_trade'] = round(avg_profit, 2)
d['performance']['total_unrealized_pnl'] = round(d['performance'].get('total_unrealized_pnl', 0), 2)

# 6. Recalculate portfolio total from open positions
open_pos = [p for p in d.get('positions', []) if p.get('status') == 'OPEN']
pos_value = sum(p.get('current_value_usd', 0) for p in open_pos)
usdc = d['portfolio'].get('usdc_balance', 0)
sol = d['portfolio'].get('sol_balance', 0)
sol_price = d['portfolio'].get('sol_price_usd', 84)
total = pos_value + usdc + (sol * sol_price)

d['portfolio']['total_value_usd'] = round(total, 2)
d['portfolio']['positions_count'] = len(open_pos)

json.dump(d, open('portfolio.db.json', 'w'), indent=2)

print(f"\n=== FIXED ===")
print(f"Realized PnL: ${realized_pnl:.2f}")
print(f"Win rate: {win_rate:.1f}% ({winners}W / {losers}L)")
print(f"Avg profit: ${avg_profit:.2f}")
print(f"Portfolio total: ${total:.2f}")
print(f"Open positions: {len(open_pos)}")
for p in open_pos:
    print(f"  {p['token']}: ${p.get('current_value_usd',0):.2f} | PnL {p.get('unrealized_pnl_pct',0):+.1f}%")
