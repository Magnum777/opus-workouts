import sys, os, json, datetime
sys.path.insert(0, os.path.dirname(__file__))
from datetime import datetime, timezone
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import scout_v2 as scout
import portfolio_db_v2 as pdb
import research_v2 as research
import token_safety_check as safety
import risk_manager as risk

print(f"[{datetime.now(timezone.utc).isoformat()}] TradeBot Lite")

# --- RESEARCH ---
print("--- RESEARCH ---")
try:
    research_result = research.research_portfolio()
    print(f"Research complete: {len(research_result.get('analyses', []))} tokens analyzed")
    buy_signals = research.get_buy_signals(min_confidence=80)
    sell_signals = research.get_sell_signals()
    print(f"Buy opportunities: {len(buy_signals)}")
    print(f"Sell signals: {len(sell_signals)}")
    for bs in buy_signals:
        print(f"  BUY {bs['token']}: conf={bs['confidence']} rec={bs['recommendation']} price=")
    for ss in sell_signals:
        print(f"  SELL {ss['token']}: rec={ss['recommendation']} pnl={ss.get('pnl_pct', 0):.1f}%")
except Exception as e:
    print(f"Research failed: {e}")
    buy_signals = []
    sell_signals = []

# --- SCOUT ---
print("--- SCOUT ---")
sol_balance = scout.get_sol_balance()
sol_price = scout.get_jupiter_price(scout.SOL_MINT) or 84
holdings = scout.get_all_holdings()
usdc_balance = scout.get_usdc_balance()
print(f"SOL: {sol_balance:.4f} | USDC: ")
print(f"Tokens on chain: {len(holdings)}")

scout_signals = scout.scan_for_signals()
print(f"Scout signals: {len(scout_signals)}")
for s in scout_signals:
    print(f"  {s['action']} {s['token']}: {s.get('reason', '')}")

# Portfolio
db = pdb.load_db()
portfolio = db.get('portfolio', {})
perf = db.get('performance', {})
positions = db.get('positions', [])
open_pos = [p for p in positions if p.get('status') == 'OPEN']

print(f"USDC: ")
print(f"SOL: {sol_balance:.4f}")
print(f"Total: ")
print(f"Realized PnL: ")
print(f"Open positions: {len(open_pos)}")

for p in open_pos:
    tok = p.get('token', '??')
    val = p.get('current_value_usd', 0)
    cost = p.get('cost_basis_usd', p.get('buy_price_usd', 0))
    upnl = val - cost
    upnl_pct = (upnl / cost * 100) if cost > 0 else 0
    sign = '+' if upnl >= 0 else ''
    print(f"  {tok}:  (P&L: {sign} / {sign}{upnl_pct:.1f}%)")

# Build report
report_lines = []
if buy_signals:
    for bs in buy_signals:
        if bs.get('confidence', 0) >= 80:
            report_lines.append(f"BUY {bs['token']}: {bs.get('recommendation')} (conf: {bs['confidence']}, price: )")

pnl_parts = []
for p in open_pos:
    tok = p.get('token', '??')
    val = p.get('current_value_usd', 0)
    cost = p.get('cost_basis_usd', p.get('buy_price_usd', 0))
    upnl = val - cost
    upnl_pct = (upnl / cost * 100) if cost > 0 else 0
    sign = '+' if upnl >= 0 else ''
    pnl_parts.append(f"{tok}: {sign} ({sign}{upnl_pct:.1f}%)")

if pnl_parts:
    report_lines.append(f"Positions: {' | '.join(pnl_parts)}")

report_lines.append(f"USDC:  | SOL: {sol_balance:.4f}")

if report_lines:
    print()
    print("[DISCORD_REPORT]")
    for line in report_lines:
        print(line)

print()
print("=== LITE DAEMON COMPLETE ===")
