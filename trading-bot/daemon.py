#!/usr/bin/env python3
"""
TradeBot Daemon — consolidated scout + research + executor in one pass.
NOW with active BUY signal generation from research module.
Reports only when trades actually execute or signals are generated.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from datetime import datetime, timezone
import copy

from risk_manager import is_on_cooldown, load_cooldowns, MAX_OPEN_POSITIONS

# Fix Windows console encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Tee stdout: keep output for logs but suppress empty cycles from Discord.
_stdout = sys.stdout
_output = io.StringIO()
sys.stdout = _output

def _flush_output():
    """Emit buffered output to real stdout and restore direct output."""
    _stdout.write(_output.getvalue())
    _stdout.flush()
    sys.stdout = _stdout


_restore_count = 0
def _restore_output():
    """Restore raw stdout without flushing (for final Discord report lines)."""
    sys.stdout = _stdout

def _discard_output():
    """Silently discard buffer (quiet cycle)."""
    _output.truncate(0)
    _output.seek(0)

import scout_v2 as scout
import executor_v2 as execmod
import portfolio_db_v2 as pdb
import research_v2 as research
import token_safety_check as safety
import risk_manager as risk

# ── Cycle-level 429 cooldown check ──
_429_COOLDOWN = os.path.join(os.path.dirname(__file__), ".jupiter_429_cooldown.json")
def _is_jupiter_cooled():
    """True if we're in a 429 penalty window. If so, skip everything Jupiter-related."""
    try:
        import json as _j
        with open(_429_COOLDOWN) as _f:
            _d = _j.load(_f)
        _rem = _d.get("expires_at", 0) - time.time()
        if _rem > 0:
            print(f"[429 COOLDOWN] {_rem:.0f}s remaining — skipping research + executor")
            return False
    except:
        pass
    return True

def _mark_429_hit():
    """Persist 429 hit so next cycle also knows."""
    try:
        import json as _j
        with open(_429_COOLDOWN, "w") as _f:
            _j.dump({"expires_at": time.time() + 600}, _f)
    except:
        pass

print(f"[{datetime.now(timezone.utc).isoformat()}] TradeBot Daemon")

# Early exit: if Jupiter is rate-limited, just sync chain state and skip execution
import time as _daemon_time
if not _is_jupiter_cooled():
    # Still do scout (Helius RPC is fine, different endpoint)
    sol_balance = scout.get_sol_balance()
    sol_price = scout.get_jupiter_price(scout.SOL_MINT) or 84
    holdings = scout.get_all_holdings()
    usdc_balance = scout.get_usdc_balance()
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
            "token": token, "mint": mint, "amount": h['amount'],
            "amount_raw": h['raw'], "decimals": h['decimals'],
            "value_usd": value_usd, "value_sol": value_usd / sol_price if sol_price > 0 else 0
        })
    pdb.sync_from_blockchain(holdings_list, sol_balance, sol_price)
    db = pdb.load_db()
    perf = db.get("performance", {})
    portfolio = db.get("portfolio", {})
    usdc = portfolio.get('usdc_balance', 0)
    print(f"\nUSDC: ${usdc:.2f}")
    print(f"SOL: {portfolio.get('sol_balance', 0):.4f}")
    print(f"Total: ${portfolio.get('total_value_usd', 0):.2f}")
    print(f"[CYCLE END] 429 cooldown — reporting only. No trades possible.")
    _discard_output()
    sys.exit(0)

# ── Step 0: Build signal queue from research before anything ──
# Research needs to analyze tracked tokens for buy opportunities
print("--- RESEARCH ---")
try:
    research_result = research.research_portfolio()
    print(f"Research complete: {len(research_result.get('analyses', []))} tokens analyzed")
    buy_signals = research.get_buy_signals(min_confidence=75)
    sell_signals = research.get_sell_signals()
    print(f"Buy opportunities: {len(buy_signals)}")
    print(f"Sell signals: {len(sell_signals)}")
    for bs in buy_signals:
        print(f"  BUY {bs['token']}: conf={bs['confidence']} rec={bs['recommendation']} price=${bs['current_price']:.8f}")
    for ss in sell_signals:
        print(f"  SELL {ss['token']}: rec={ss['recommendation']} pnl={ss.get('pnl_pct', 0):.1f}%")
except Exception as e:
    print(f"Research failed: {e}")
    buy_signals = []
    sell_signals = []

# ── Step 1: Scout — sync holdings, check prices ──
print("--- SCOUT ---")
sol_balance = scout.get_sol_balance()
sol_price = scout.get_jupiter_price(scout.SOL_MINT) or 84
holdings = scout.get_all_holdings()
usdc_balance = scout.get_usdc_balance()

print(f"SOL: {sol_balance:.4f} | USDC: ${usdc_balance:.2f}")
print(f"Tokens on chain: {len(holdings)}")

# Skip sub-penny dust
relevant = {m: h for m, h in holdings.items() if h['amount'] * (scout.get_jupiter_price(m, h['decimals']) or 0) >= 0.01}
print(f"Valuable tokens: {len(relevant)}")

holdings_list = []
for mint, h in holdings.items():
    token = scout.MINT_TO_NAME.get(mint, mint[:10])
    price = scout.get_jupiter_price(mint, decimals=h['decimals'])
    # USDC can't price itself via Jupiter — force $1
    if mint == scout.USDC:
        price = 1.0
    value_usd = h['amount'] * price if price > 0 else 0
    if value_usd < 0.01:
        continue
    holdings_list.append({
        "token": token, "mint": mint, "amount": h['amount'],
        "amount_raw": h['raw'], "decimals": h['decimals'],
        "value_usd": value_usd, "value_sol": value_usd / sol_price if sol_price > 0 else 0
    })
    print(f"  {token}: {h['amount']:.4f} (${value_usd:.2f})")

pdb.sync_from_blockchain(holdings_list, sol_balance, sol_price)

# ── Step 2: Build trade queue from TP/SL signals + research buy signals ──
# 2a: Scout TP/SL signals (from open positions)
scout_signals = scout.scan_for_signals()
print(f"\nScout signals: {len(scout_signals)}")

# 2b: Convert research buy signals to trade queue format
research_buy_queue = []
for bs in buy_signals:
    mint = bs.get("mint", "")
    conf = bs.get("confidence", 50)
    rec = bs.get("recommendation", "BUY")
    # Convert research signals into executor-compatible format
    research_buy_queue.append({
        "token": bs["token"],
        "mint": mint,
        "action": "BUY",
        "reason": f"RESEARCH_{rec}",
        "recommendation": rec,
        "confidence": conf,
        "price": bs.get("current_price", 0),
        "momentum": bs.get("momentum", {})
    })
    print(f"  [BUY SIGNAL] {bs['token']}: {rec} (conf: {conf})")

# 2c: Convert research sell signals to trade queue format
research_sell_queue = []
for ss in sell_signals:
    mint = ss.get("mint", "")
    research_sell_queue.append({
        "token": ss["token"],
        "mint": mint,
        "action": "SELL",
        "reason": f"RESEARCH_{ss.get('recommendation', 'SELL')}",
        "recommendation": ss.get("recommendation", "SELL"),
        "confidence": ss.get("confidence", 50),
        "pnl_pct": ss.get("pnl_pct", 0),
        "current_value_usd": ss.get("current_price", 0)  # approximate
    })
    print(f"  [SELL SIGNAL] {ss['token']}: {ss.get('recommendation')} (pnl: {ss.get('pnl_pct', 0):.1f}%)")

# 2d: Merge all signals into queue
# Priority: scout TP/SL > research sell > research buy
all_pending = []
seen_tokens = set()

# First, scout signals (highest priority - they're from actual positions)
for sig in scout_signals:
    token = sig["token"]
    all_pending.append(sig)
    seen_tokens.add(token)

# Then research sell signals (don't duplicate)
for sig in research_sell_queue:
    token = sig["token"]
    if token not in seen_tokens:
        all_pending.append(sig)
        seen_tokens.add(token)

# Then research buy signals — but check cooldowns and max positions
# Load cooldowns once for efficiency
cooldowns = load_cooldowns()
now_utc = datetime.now(timezone.utc).isoformat()
# Count current open positions for max-positions cap
db = pdb.load_db()
current_open_ct = len([p for p in db.get("positions", []) if p.get("status") == "OPEN"])

for sig in research_buy_queue:
    token = sig["token"]
    mint = sig.get("mint", "")
    if token in seen_tokens:
        continue
    
    # COOLDOWN CHECK: No rebuying tokens sold recently
    cd_token, cd_mint = None, None
    if token:
        on_cd, remaining = is_on_cooldown(token, "")
        if on_cd:
            print(f"  [COOLDOWN SKIP] {token}: rebuy cooldown {remaining:.1f}h remaining")
            cd_token = True
    if mint and not cd_token:
        on_cd, remaining = is_on_cooldown(mint, mint)
        if on_cd:
            print(f"  [COOLDOWN SKIP] {token}: mint cooldown {remaining:.1f}h remaining")
            cd_mint = True
    if cd_token or cd_mint:
        continue
    
    # MAX POSITIONS CHECK: Can we afford to buy?
    if current_open_ct >= MAX_OPEN_POSITIONS:
        print(f"  [MAX POSITIONS] Skipping buy {token}: {current_open_ct} positions open, max {MAX_OPEN_POSITIONS}")
        continue
    
    all_pending.append(sig)
    seen_tokens.add(token)

# Also add pure TP/SL threshold sell signals from existing positions
db = pdb.load_db()
for pos in db.get("positions", []):
    if pos.get("status") != "OPEN":
        continue
    t = pos["token"]
    if t in seen_tokens:
        continue
    mint = pos.get("mint", "")
    cost = pos.get("cost_basis_usd", pos.get("buy_price_usd", 0))
    raw = pos.get("amount_raw", 0)
    if cost <= 0 or raw == 0:
        continue
    decimals = pos.get("decimals", 6)
    live_price = execmod.get_jupiter_price(mint, decimals=decimals)
    if live_price <= 0:
        continue
    live_value = live_price * raw / 1e6
    live_pnl_pct = ((live_value - cost) / cost) * 100 if cost > 0 else 0
    tp_threshold = risk.TAKE_PROFIT_PCT * 100  # e.g. 15.0
    trim_threshold = risk.TRIM_PCT * 100       # e.g. 8.0
    sl_threshold = risk.STOP_LOSS_PCT * 100     # e.g. -8.0
    already_trimmed = pos.get("partial_trims", 0) > 0
    # Momentum override for TP: skip if still surging (>3% in last 15min)
    mom = pos.get("momentum", {})
    surging = mom.get('trend') == 'up' and mom.get('momentum_pct', 0) > 0.03

    if live_pnl_pct >= tp_threshold:
        if surging:
            print(f"  [MOMENTUM HOLD] {t}: +{live_pnl_pct:.1f}% but still surging ({mom.get('momentum_pct',0)*100:.1f}%) — let it ride")
        else:
            all_pending.append({
                "token": t, "mint": mint, "action": "SELL",
                "reason": "TAKE_PROFIT", "current_value_usd": live_value,
                "pnl_pct": live_pnl_pct
            })
            seen_tokens.add(t)
            print(f"  [THRESHOLD SELL] {t}: TAKE_PROFIT (+{live_pnl_pct:.1f}%)")
    elif live_pnl_pct <= sl_threshold:
        all_pending.append({
            "token": t, "mint": mint, "action": "SELL",
            "reason": "STOP_LOSS", "current_value_usd": live_value,
            "pnl_pct": live_pnl_pct
        })
        seen_tokens.add(t)
        print(f"  [THRESHOLD SELL] {t}: STOP_LOSS ({live_pnl_pct:.1f}%)")
    elif live_pnl_pct >= trim_threshold and not already_trimmed:
        all_pending.append({
            "token": t, "mint": mint, "action": "SELL",
            "reason": "TRIM_THRESHOLD", "current_value_usd": live_value,
            "pnl_pct": live_pnl_pct
        })
        seen_tokens.add(t)
        print(f"  [THRESHOLD SELL] {t}: TRIM_THRESHOLD (+{live_pnl_pct:.1f}%) — selling all")

# Write consolidated queue
queue_path = os.path.join(os.path.dirname(__file__), "trading-queue.json")
with open(queue_path, "w") as f:
    json.dump({"pending": all_pending, "executed": []}, f, indent=2)
print(f"[QUEUE] {len(all_pending)} signal(s) written ({len([s for s in all_pending if s['action']=='BUY'])} buys, {len([s for s in all_pending if s['action']=='SELL'])} sells)")

# ── Step 3: Executor — process signals, ONE AT A TIME, stop on 429 ──
print("\n--- EXECUTOR ---")

import time as _exec_time

# Auto-refill SOL if critically low (< 0.001 SOL) - but only if no 429 cooldown
_429_FILE = os.path.join(os.path.dirname(__file__), ".jupiter_429_cooldown.json")
try:
    import json as _je
    with open(_429_FILE) as _jf:
        _jd = _je.load(_jf)
    _429_active = _jd.get("expires_at", 0) > _exec_time.time()
except:
    _429_active = False

if not _429_active:
    try:
        execmod.ensure_sol_for_gas()
    except Exception as e:
        print(f"[SOL GAS CHECK] Failed: {e}")

# Load queue
queue_path = os.path.join(os.path.dirname(__file__), "trading-queue.json")
try:
    with open(queue_path, "r") as f:
        queue = json.load(f)
except:
    queue = {"pending": []}

# Prioritize: sells first (critical), then best buy
pending = list(queue.get("pending", []))
sells = [s for s in pending if s.get("action") == "SELL"]
buys = sorted([s for s in pending if s.get("action") == "BUY"], key=lambda s: s.get("confidence", 0), reverse=True)
ordered_signals = sells + buys[:1]  # ALL sells + only the BEST buy

# Also clear any extra buy signals from queue so they don't re-appear next cycle
queue["pending"] = [s for s in queue.get("pending", []) if s.get("action") != "BUY"] + buys[1:] if len(buys) > 1 else []

if ordered_signals:
    print(f"[QUEUE] {len(pending)} pending → prioritizing {len(sells)} sells + 1 best buy (skipped {len(buys)-1 if len(buys)>1 else 0} other buys)")

hit_429_this_cycle = False
executed_tokens = set()
execution_results = []
failures = []

for signal in ordered_signals:
    if hit_429_this_cycle:
        print(f"  [SKIP {signal.get('token')}] Stopped early — previous signal hit 429")
        break
    
    action = signal.get("action")
    token = signal.get("token")

    if action == "SELL":
        if token in executed_tokens:
            continue
        success, msg = execmod.process_sell_signal(signal)
        if success:
            executed_tokens.add(token)
            reason = signal.get("reason", "")
            if "TP" in reason or "TAKE_PROFIT" in reason:
                emoji = "🎯"
            elif "SL" in reason or "STOP_LOSS" in reason:
                emoji = "🚨"
            else:
                emoji = "💰"
            execution_results.append(f"{emoji} SELL {token} {reason}: P&L ${msg.split('P&L: ')[-1].split(' |')[0] if 'P&L: ' in msg else msg}")
        else:
            fail_reason = msg.split("FAILED:")[-1].strip() if "FAILED:" in msg else msg
            if "429" in fail_reason or "cooldown" in fail_reason.lower():
                hit_429_this_cycle = True
                _mark_429_hit()
            failures.append(f"**{action} {token} FAILED**: {fail_reason}")
        # Remove from queue regardless
        queue["pending"] = [s for s in queue.get("pending", []) if s.get("token") != token or s.get("action") != action]

    elif action == "BUY":
        mint = signal.get("mint", "")
        if not mint:
            continue

        # SAFETY CHECK
        print(f"  [SAFETY] Checking {token} before buy...")
        safety_result = safety.check_token_safety(mint, token)
        if not safety_result["safe"]:
            print(f"  [SAFETY BLOCKED] {token}: score={safety_result['score']}/100")
            for note in safety_result.get("notes", []):
                print(f"    {note}")
            failures.append(f"**BUY {token} BLOCKED**: Safety score {safety_result['score']}/100")
            queue["pending"] = [s for s in queue.get("pending", []) if s.get("mint") != mint]
            continue
        else:
            print(f"  [SAFETY OK] {token}: score={safety_result['score']}/100")

        live_usdc = execmod.get_usdc_balance()
        if live_usdc < 3.0:
            print(f"  [SKIP {token}] USDC too low (${live_usdc:.2f})")
            queue["pending"] = [s for s in queue.get("pending", []) if s.get("mint") != mint]
            continue

        sig = {"token": token, "mint": mint}
        sig["recommendation"] = signal.get("recommendation", "BUY")
        sig["confidence"] = signal.get("confidence", 50)

        print(f"  [BALANCE CHECK] USDC before BUY {token}: ${live_usdc:.2f}")
        success, msg = execmod.process_buy_signal(sig)
        if success:
            execution_results.append(f"💎 BUY {token}: ${msg.split('|')[1].strip() if '|' in msg else msg}")
            queue["pending"] = [s for s in queue.get("pending", []) if s.get("mint") != mint]
        else:
            fail_reason = msg.split("failed:")[-1].strip() if "failed:" in msg else msg
            if "429" in fail_reason or "cooldown" in fail_reason.lower():
                hit_429_this_cycle = True
                _mark_429_hit()
            else:
                # Remove failed buy from queue so it doesn't retry forever
                queue["pending"] = [s for s in queue.get("pending", []) if s.get("mint") != mint]
            failures.append(f"**BUY {token} FAILED**: {fail_reason}")

with open(queue_path, "w") as f:
    json.dump(queue, f, indent=2)

# ── Step 4: Report ──
db = pdb.load_db()
perf = db.get("performance", {})
portfolio = db.get("portfolio", {})

print("\n--- SUMMARY ---")
print(f"USDC: ${portfolio.get('usdc_balance', 0):.2f}")
print(f"SOL: {portfolio.get('sol_balance', 0):.4f}")
print(f"Total: ${portfolio.get('total_value_usd', 0):.2f}")
print(f"Realized PnL: ${perf.get('total_realized_pnl', 0):.2f}")
print(f"Open positions: {portfolio.get('positions_count', 0)}")
if execution_results:
    print(f"Trades just executed: {len(execution_results)}")
    for r in execution_results:
        print(f"  {r}")
else:
    print("No trades executed this cycle")

# Build open positions PnL string
positions_pnl = ""
positions_data = db.get("positions", [])
open_positions = [p for p in positions_data if p.get("status") == "OPEN"]
if open_positions:
    pnl_parts = []
    for p in open_positions:
        tok = p.get("token", "??")
        val = p.get("current_value_usd", 0)
        cost = p.get("cost_basis_usd", 0)
        upnl = p.get("unrealized_pnl_usd", val - cost)
        upnl_pct = p.get("unrealized_pnl_pct", ((val - cost) / cost * 100) if cost > 0 else 0)
        sign = "+" if upnl >= 0 else ""
        pnl_parts.append(f"{tok}: ${sign}{upnl:.2f} ({sign}{upnl_pct:.1f}%)")
    positions_pnl = " | ".join(pnl_parts)

# Build audit warnings: flag DB/chain desync
open_ct_db = portfolio.get('positions_count', 0)
# Count actual tokens on chain (non-stable worth >= $0.01)
on_chain_positions = [h for h in holdings_list if h.get('value_usd', 0) >= 0.01 and not pdb.is_stablecoin_mint(h.get('mint', ''))]
on_chain_ct = len(on_chain_positions)
audit_warnings = []
if open_ct_db != on_chain_ct:
    audit_warnings.append(f"AUDIT: DB shows {open_ct_db} open positions but chain has {on_chain_ct}")

# Consecutive losses warning
consecutive_losses = db.get('risk_metrics', {}).get('consecutive_losses', 0)
if consecutive_losses >= 3:
    audit_warnings.append(f"Trading paused - {consecutive_losses} consecutive losses")
elif consecutive_losses >= 2:
    audit_warnings.append(f"WARNING: {consecutive_losses} consecutive losses")

# USDC low warning
usdc = portfolio.get('usdc_balance', 0)
if usdc < 10:
    audit_warnings.append(f"LOW CAPITAL: ${usdc:.2f} USDC")

# ── Discord report: only on actual events ──
has_news = bool(execution_results or failures or audit_warnings)
if not has_news:
    # Quiet cycle - nothing happened, nothing to report
    _discard_output()
    sys.exit(0)

# Flush accumulated research/scout/executor output to real stdout
_flush_output()

# From here, output goes directly to real stdout (no buffer)
print("\n[DISCORD_REPORT]")
if execution_results:
    print(f">**TradeBot** | {len(execution_results)} trade(s) executed")
    for r in execution_results:
        print(f">{r}")

if failures:
    for f in failures:
        print(f">{f}")

if audit_warnings:
    lines = []
    for w in audit_warnings:
        lines.append(w + " | ")
    print(f">" + "".join(lines)[:-3])

if positions_pnl:
    print(f">Positions: {positions_pnl}")
print(f">USDC: ${usdc:.2f} | Total: ${portfolio.get('total_value_usd', 0):.2f}")

# Show best pending buy signal
if buy_signals and not execution_results:
    best_buy = buy_signals[0]
    print(f">Watching: {best_buy['token']} ({best_buy['recommendation']}, conf {best_buy['confidence']})")

print("=" * 50)
print(f"[CYCLE END]")


