import json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

os.chdir("C:/Users/compj/.openclaw/workspace/trading-bot")

# Read latest portfolio
d = json.load(open("portfolio.db.json"))

# Get current on-chain state
import scout_v2 as scout
usdc = scout.get_usdc_balance()
sol = scout.get_sol_balance()
holdings = scout.get_all_holdings()

result_lines = []
result_lines.append(f">**TradeBot** | 3:16 PM scan")
result_lines.append(f">USDC: ${usdc:.2f} | SOL: {sol:.4f}")

positions_chain = []
for mint, h in holdings.items():
    token = scout.MINT_TO_NAME.get(mint, mint[:10])
    price = scout.get_jupiter_price(mint, h.get("decimals",6))
    if mint == scout.USDC:
        price = 1.0
    value = h["amount"] * price if price else 0
    if value >= 0.01 and mint != scout.USDC:
        positions_chain.append(f"{token}: ${value:.2f}")

if positions_chain:
    result_lines.append(f">Holdings: {' | '.join(positions_chain)}")
else:
    result_lines.append(f">No open token positions")

# Check signals
for s in d.get("signals", []):
    if s.get("confidence", 0) >= 75:
        result_lines.append(f">Watching: {s.get('token','?')} ({s.get('recommendation','?')}, conf {s.get('confidence',0)})")

rm = d.get("risk_metrics", {})
if rm.get("consecutive_losses", 0) >= 3:
    result_lines.insert(1, ">Trading paused - 3+ consecutive losses")

if usdc < 30:
    result_lines.insert(1, f">LOW CAPITAL: ${usdc:.2f} USDC")

result_lines.append(f">Total value: ${d['portfolio'].get('total_value_usd',0):.2f}")

print("[DISCORD_REPORT]")
for line in result_lines:
    print(line)
print("==================================================")
