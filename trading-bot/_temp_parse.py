import sys, json

data = json.load(sys.stdin)
latest_key = sorted(data.keys())[-1]
latest = data[latest_key]
if isinstance(latest, dict):
    for k, v in latest.items():
        if k == 'positions' and isinstance(v, list):
            print('positions (%d):' % len(v))
            for p in v:
                token = p.get('token', '?')
                val = p.get('current_value_usd', p.get('value_usd', '?'))
                pnl = p.get('unrealized_pnl_usd', p.get('pnl', '?'))
                pnl_pct = p.get('pnl_pct', '?')
                print('  %s: value=\$%s, pnl=\$%s (%s%%%%)' % (token, val, pnl, pnl_pct))
                print('    entry=%s, current=%s, amount=%s' % (p.get('entry_price','?'), p.get('current_price','?'), p.get('amount','?')))
        elif k == 'summary' and isinstance(v, dict):
            print('summary:', json.dumps(v, default=str))
        elif k == 'performance' and isinstance(v, dict):
            print('performance:', json.dumps(v, default=str))
        elif k == 'risk_metrics' and isinstance(v, dict):
            print('risk_metrics:', json.dumps(v, default=str))
        elif k not in ('tokens_analyzed',):
            val_str = json.dumps(v, default=str)
            if len(val_str) > 500:
                val_str = val_str[:500] + '...'
            print('%s: %s' % (k, val_str))

