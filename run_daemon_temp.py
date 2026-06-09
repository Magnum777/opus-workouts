import traceback, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(r'C:\Users\compj\.openclaw\workspace\trading-bot'))

from datetime import datetime, timezone
print(f'[{datetime.now(timezone.utc).isoformat()}] TradeBot Daemon')

import scout_v2 as scout
import executor_v2 as execmod
import portfolio_db_v2 as pdb
import research_v2 as research
import token_safety_check as safety
import risk_manager as risk

# Step 0: Research
print('--- RESEARCH ---')
try:
    research_result = research.research_portfolio()
    print(f'Research complete: {len(research_result.get("analyses", []))} tokens analyzed')
    buy_signals = research.get_buy_signals(min_confidence=80)
    sell_signals = research.get_sell_signals()
    print(f'Buy opportunities: {len(buy_signals)}')
    print(f'Sell signals: {len(sell_signals)}')
    for bs in buy_signals:
        print(f'  BUY {bs["token"]}: conf={bs["confidence"]} rec={bs["recommendation"]} price=')
    for ss in sell_signals:
        print(f'  SELL {ss["token"]}: rec={ss["recommendation"]} pnl={ss.get("pnl_pct", 0):.1f}%')
except Exception as e:
    traceback.print_exc()
    buy_signals = []
    sell_signals = []

# Step 1: Scout
print('--- SCOUT ---')
sol_balance = scout.get_sol_balance()
sol_price = scout.get_jupiter_price(scout.SOL_MINT) or 84
holdings = scout.get_all_holdings()
usdc_balance = scout.get_usdc_balance()

print(f'SOL: {sol_balance:.4f} | USDC: ')
print(f'Tokens on chain: {len(holdings)}')

# Step 2 onwards
relevant = {m: h for m, h in holdings.items() if h['amount'] * (scout.get_jupiter_price(m, h['decimals']) or 0) >= 0.01}
print(f'Valuable tokens: {len(relevant)}')

holdings_list = []
for mint, h in holdings.items():
    token = scout.MINT_TO_NAME.get(mint, mint[:10])
    price = scout.get_jupiter_price(mint, decimals=h['decimals'])
    if mint == scout.USDC:
        price = 1.0
    value_usd = h['amount'] * price if price and price > 0 else 0
    if value_usd < 0.01:
        continue
    holdings_list.append({
        'token': token, 'mint': mint, 'amount': h['amount'],
        'amount_raw': h['raw'], 'decimals': h['decimals'],
        'value_usd': value_usd, 'value_sol': value_usd / sol_price if sol_price > 0 else 0
    })
    print(f'  {token}: {h["amount"]:.4f} ()')

pdb.sync_from_blockchain(holdings_list, sol_balance, sol_price)

# Scout signals
scout_signals = scout.scan_for_signals()
print(f'\nScout signals: {len(scout_signals)}')

# Research buy queue
research_buy_queue = []
for bs in buy_signals:
    mint = bs.get('mint', '')
    conf = bs.get('confidence', 50)
    rec = bs.get('recommendation', 'BUY')
    research_buy_queue.append({
        'token': bs['token'],
        'mint': mint,
        'action': 'BUY',
        'reason': f'RESEARCH_{rec}',
        'recommendation': rec,
        'confidence': conf,
        'price': bs.get('current_price', 0),
        'momentum': bs.get('momentum', {})
    })
    print(f'  [BUY SIGNAL] {bs["token"]}: {rec} (conf: {conf})')

research_sell_queue = []
for ss in sell_signals:
    mint = ss.get('mint', '')
    research_sell_queue.append({
        'token': ss['token'],
        'mint': mint,
        'action': 'SELL',
        'reason': f"RESEARCH_{ss.get('recommendation', 'SELL')}",
        'recommendation': ss.get('recommendation', 'SELL'),
        'confidence': ss.get('confidence', 50),
        'pnl_pct': ss.get('pnl_pct', 0),
        'current_value_usd': ss.get('current_price', 0)
    })
    print(f'  [SELL SIGNAL] {ss["token"]}: {ss.get("recommendation")} (pnl: {ss.get("pnl_pct", 0):.1f}%)')

# Merge signals
all_pending = []
seen_tokens = set()

for sig in scout_signals:
    token = sig['token']
    all_pending.append(sig)
    seen_tokens.add(token)

for sig in research_sell_queue:
    token = sig['token']
    if token not in seen_tokens:
        all_pending.append(sig)
        seen_tokens.add(token)

for sig in research_buy_queue:
    token = sig['token']
    if token not in seen_tokens:
        all_pending.append(sig)
        seen_tokens.add(token)

# Also TP/SL from DB positions
db = pdb.load_db()
for pos in db.get('positions', []):
    if pos.get('status') != 'OPEN':
        continue
    t = pos['token']
    if t in seen_tokens:
        continue
    mint = pos.get('mint', '')
    cost = pos.get('cost_basis_usd', pos.get('buy_price_usd', 0))
    raw = pos.get('amount_raw', 0)
    if cost <= 0 or raw == 0:
        continue
    decimals = pos.get('decimals', 6)
    live_price = execmod.get_jupiter_price(mint, decimals=decimals)
    if live_price <= 0:
        continue
    live_value = live_price * raw / 1e6
    live_pnl_pct = ((live_value - cost) / cost) * 100 if cost > 0 else 0
    tp_threshold = risk.TAKE_PROFIT_PCT * 100
    trim_threshold = risk.TRIM_PCT * 100
    sl_threshold = risk.STOP_LOSS_PCT * 100
    already_trimmed = pos.get('partial_trims', 0) > 0
    if live_pnl_pct >= tp_threshold:
        all_pending.append({'token': t, 'mint': mint, 'action': 'SELL', 'reason': 'TAKE_PROFIT', 'current_value_usd': live_value, 'pnl_pct': live_pnl_pct})
        seen_tokens.add(t)
        print(f'  [THRESHOLD SELL] {t}: TAKE_PROFIT (+{live_pnl_pct:.1f}%)')
    elif live_pnl_pct <= sl_threshold:
        all_pending.append({'token': t, 'mint': mint, 'action': 'SELL', 'reason': 'STOP_LOSS', 'current_value_usd': live_value, 'pnl_pct': live_pnl_pct})
        seen_tokens.add(t)
        print(f'  [THRESHOLD SELL] {t}: STOP_LOSS ({live_pnl_pct:.1f}%)')
    elif live_pnl_pct >= trim_threshold and not already_trimmed:
        all_pending.append({'token': t, 'mint': mint, 'action': 'TRIM', 'reason': 'PARTIAL_TRIM', 'current_value_usd': live_value, 'pnl_pct': live_pnl_pct})
        print(f'  [PARTIAL TRIM] {t}: +{live_pnl_pct:.1f}% - selling {1-risk.TRIM_FRACTION:.0%}, letting rest ride')

# Write queue
import json
queue_path = os.path.join(os.path.dirname(r'C:\Users\compj\.openclaw\workspace\trading-bot'), 'trading-queue.json')
with open(queue_path, 'w') as f:
    json.dump({'pending': all_pending, 'executed': []}, f, indent=2)
print(f'[QUEUE] {len(all_pending)} signal(s) written ({len([s for s in all_pending if s["action"]=="BUY"])} buys, {len([s for s in all_pending if s["action"]=="SELL"])} sells)')

print('\n--- EXECUTOR ---')
try:
    with open(queue_path, 'r') as f:
        queue = json.load(f)
except:
    queue = {'pending': []}

executed_tokens_set = set()
execution_results = []
failures = []

for signal in list(queue.get('pending', [])):
    action = signal.get('action')
    token = signal.get('token')

    if action == 'SELL':
        if token in executed_tokens_set:
            continue
        success, msg = execmod.process_sell_signal(signal)
        if success:
            executed_tokens_set.add(token)
            queue['pending'].remove(signal)
            queue.setdefault('executed', []).append(signal)
            reason = signal.get('reason', '')
            if 'TP' in reason or 'TAKE_PROFIT' in reason:
                emoji = 'TP'
            elif 'SL' in reason or 'STOP_LOSS' in reason:
                emoji = 'SL'
            else:
                emoji = 'SELL'
            execution_results.append(f'{emoji} SELL {token} {reason}: P&L ')
        else:
            fail_reason = msg.split('FAILED:')[-1].strip() if 'FAILED:' in msg else msg
            failures.append(f'**{action} {token} FAILED**: {fail_reason}')

    elif action == 'BUY':
        mint = signal.get('mint', '')
        if not mint:
            continue
        print(f'  [SAFETY] Checking {token} before buy...')
        safety_result = safety.check_token_safety(mint, token)
        if not safety_result['safe']:
            print(f'  [SAFETY BLOCKED] {token}: score={safety_result["score"]}/100')
            for note in safety_result.get('notes', []):
                print(f'    {note}')
            failures.append(f'**BUY {token} BLOCKED**: Safety score {safety_result["score"]}/100')
            queue['pending'].remove(signal)
            continue
        else:
            print(f'  [SAFETY OK] {token}: score={safety_result["score"]}/100')

        sig = {'token': token, 'mint': mint}
        sig['recommendation'] = signal.get('recommendation', 'BUY')
        sig['confidence'] = signal.get('confidence', 50)
        sig['max_usdc'] = signal.get('max_usdc')
        success, msg = execmod.process_buy_signal(sig)
        if success:
            queue['pending'].remove(signal)
            queue.setdefault('executed', []).append(signal)
            execution_results.append(f'BUY {token}: ')
        else:
            fail_reason = msg.split('failed:')[-1].strip() if 'failed:' in msg else msg
            failures.append(f'**BUY {token} FAILED**: {fail_reason}')

with open(queue_path, 'w') as f:
    json.dump(queue, f, indent=2)

db = pdb.load_db()
perf = db.get('performance', {})
portfolio = db.get('portfolio', {})

print('\n--- SUMMARY ---')
print(f'USDC: ')
print(f'SOL: {portfolio.get("sol_balance", 0):.4f}')
print(f'Total: ')
print(f'Realized PnL: ')
print(f'Open positions: {portfolio.get("positions_count", 0)}')
if execution_results:
    print(f'Trades just executed: {len(execution_results)}')
    for r in execution_results:
        print(f'  {r}')
else:
    print('No trades executed this cycle')

report_lines = []
if execution_results:
    report_lines.append(f'**TradeBot** | {len(execution_results)} trade(s) executed')
    for r in execution_results:
        report_lines.append(r)
    report_lines.append(f'USDC:  | Positions: {portfolio.get("positions_count", 0)}')

if report_lines:
    print('\n[DISCORD_REPORT]')
    for line in report_lines:
        print(line)

if failures:
    if not report_lines:
        print('\n[DISCORD_REPORT]')
    for f in failures:
        print(f'>{f}')
    for r in execution_results:
        print(f'>{r}')
    print(f'>USDC:  | Positions: {portfolio.get("positions_count", 0)}')
    if buy_signals and not any('BUY' in r for r in execution_results):
        best_buy = buy_signals[0]
        print(f'>**Watching:** {best_buy["token"]} ({best_buy["recommendation"]}, conf {best_buy["confidence"]}) - waiting on capital / price')

print("=" * 50)
