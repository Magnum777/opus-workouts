import sys, subprocess, datetime, json, os

base = r'C:\Users\compj\.openclaw\workspace\trading-bot'

print('--- PHASE 1: RESEARCH ---')
proc = subprocess.Popen(
    [r'C:\ProgramData\chocolatey\bin\python3.14.exe', '-u', os.path.join(base, '_test_signals.py')],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)
try:
    out, err = proc.communicate(timeout=25)
    print(out)
    if err: print('STDERR:', err[-1000:])
except subprocess.TimeoutExpired:
    proc.kill()
    print('RESEARCH TIMEOUT')

print()
print('--- PHASE 2: SCOUT + QUEUE ---')
proc = subprocess.Popen(
    [r'C:\ProgramData\chocolatey\bin\python3.14.exe', '-u', os.path.join(base, '_test_scout.py')],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)
try:
    out, err = proc.communicate(timeout=25)
    print(out)
    if err: print('STDERR:', err[-1000:])
except subprocess.TimeoutExpired:
    proc.kill()
    print('SCOUT TIMEOUT')

print()
print('--- PHASE 3: CURRENT QUEUE ---')
qpath = os.path.join(base, 'trading-queue.json')
if os.path.exists(qpath):
    with open(qpath) as f:
        q = json.load(f)
    pending = q.get('pending', [])
    print(f'Pending signals: {len(pending)}')
    for s in pending:
        print(f'  {s.get("action")} {s.get("token")}: {s.get("reason", "")} (conf={s.get("confidence", "?")})')
    executed = q.get('executed', [])
    print(f'Executed: {len(executed)}')
else:
    print('No trading-queue.json found')

print()
print('--- PHASE 4: PORTFOLIO ---')
ppath = os.path.join(base, 'portfolio.db.json')
if os.path.exists(ppath):
    with open(ppath) as f:
        pf = json.load(f)
    pp = pf.get('portfolio', {})
    per = pf.get('performance', {})
    usdc = pp.get('usdc_balance', 0)
    sol = pp.get('sol_balance', 0)
    total = pp.get('total_value_usd', 0)
    realized = per.get('total_realized_pnl', 0)
    print(f'USDC: ')
    print(f'SOL: {sol:.4f}')
    print(f'Total: ')
    print(f'Realized PnL: ')
    positions = pf.get('positions', [])
    open_pos = [p for p in positions if p.get('status') == 'OPEN']
    print(f'Open positions: {len(open_pos)}')
    for p in open_pos:
        tok = p.get('token', '??')
        val = p.get('current_value_usd', 0)
        cost = p.get('cost_basis_usd', p.get('buy_price_usd', 0))
        upnl = val - cost
        upnl_pct = (upnl / cost * 100) if cost > 0 else 0
        sign = '+' if upnl >= 0 else ''
        print(f'  {tok}:  (P&L: {sign} / {sign}{upnl_pct:.1f}%)')

print()
print('ALL CHECKS COMPLETE')
