import sys, os
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\trading-bot')
sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from datetime import datetime, timezone
print(f"[{datetime.now(timezone.utc).isoformat()}] TradeBot Daemon (cron run)")

import scout_v2 as scout, executor_v2 as execmod, portfolio_db_v2 as pdb, research_v2 as research, token_safety_check as safety, risk_manager as risk

sol_bal = scout.get_sol_balance()
sol_price = scout.get_jupiter_price(scout.SOL_MINT) or 84
usdc_bal = scout.get_usdc_balance()
print(f"SOL: {sol_bal:.4f} | USDC: ")

positions = pdb.load_positions()
open_positions = [p for p in positions if p.get('status') == 'open']
print(f"Open positions: {len(open_positions)}")
for p in open_positions:
    print(f"  {p.get('mint','?')[:12]}: entry=")

try:
    research.research_portfolio()
    buys = research.get_buy_signals(75)
    sells = research.get_sell_signals()
    print(f"Buy signals: {len(buys)}, Sell signals: {len(sells)}")
    for b in buys:
        print(f"  BUY {b['token']}: conf={b['confidence']} rec={b['recommendation']}")
except Exception as e:
    print(f"Research fail: {e}")
    buys = []

disco = []
if len(open_positions) == 0 and len(buys) > 0:
    for b in buys[:2]:
        try:
            ok, reason = safety.check_token(b['token'])
            if ok:
                disco.append(f"Ready to buy {b['token']} (conf {b['confidence']}) -  USDC")
            else:
                disco.append(f"SAFETY FAIL {b['token']}: {reason}")
        except Exception as e:
            disco.append(f"Safety check error on {b['token']}: {e}")
elif len(open_positions) > 0:
    for p in open_positions:
        mint = p.get('mint','')
        entry = float(p.get('entry_price',0))
        try:
            price = scout.get_jupiter_price(mint, p.get('decimals', 6)) or entry
        except:
            price = entry
        pnl_pct = ((price - entry) / entry * 100) if entry else 0
        disco.append(f"{mint[:12]}:  (+{pnl_pct:.1f}%)" if pnl_pct >= 0 else f"{mint[:12]}:  ({pnl_pct:.1f}%)")
else:
    disco.append(f"No positions. USDC:  | Watching for signals")

if disco:
    print("\n[DISCORD_REPORT]")
    for l in disco:
        print(f">{l}")
    print(f">USDC:  | SOL: {sol_bal:.4f}")

print("=== DONE ===")
