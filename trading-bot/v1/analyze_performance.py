import json
from datetime import datetime, timedelta

# Load data
trades = json.load(open('trade-history.json'))
db = json.load(open('portfolio.db.json'))

print("=" * 50)
print("TRADING PERFORMANCE ANALYSIS")
print("=" * 50)

# Current portfolio
print("\n[CURRENT PORTFOLIO]")
print(f"  Total Value: ${db['portfolio']['total_value_usd']:.2f}")
print(f"  SOL Balance: {db['portfolio']['sol_balance']:.4f} SOL")
print(f"  Positions: {db['portfolio']['positions_count']}")
print(f"  Last Update: {db['last_updated'][:10]}")

# Realized P&L from sells
realized_pnl = sum(t.get('pnl_usd', 0) for t in trades if t.get('pnl_usd'))
sells = [t for t in trades if t['action'] == 'SELL']
buys = [t for t in trades if t['action'] == 'BUY']

print(f"\n[REALIZED P&L from sells]")
print(f"  Total Profit: ${realized_pnl:.2f}")
print(f"  Total Sells: {len(sells)}")
print(f"  Total Buys: {len(buys)}")

if sells:
    print(f"\n  Recent Sells:")
    for t in sells[-5:]:
        print(f"    {t['timestamp'][:10]} | {t['token']}: ${t.get('pnl_usd', 0):+.2f}")

# Unrealized P&L from open positions
print(f"\n[OPEN POSITIONS - Unrealized P&L]")
unrealized_pnl = 0
for pos in db['positions']:
    if pos['status'] == 'OPEN':
        pnl = pos.get('unrealized_pnl_usd', 0)
        unrealized_pnl += pnl
        print(f"  {pos['token']}: ${pos['current_value_usd']:.2f} (PnL: ${pnl:+.2f})")

print(f"\n  Total Unrealized P&L: ${unrealized_pnl:+.2f}")

# Total profit
total_pnl = realized_pnl + unrealized_pnl
print(f"\n[TOTAL PROFIT - Realized + Unrealized]: ${total_pnl:+.2f}")

# Time analysis
if trades:
    first_trade = min(t['timestamp'] for t in trades)
    last_trade = max(t['timestamp'] for t in trades)
    print(f"\n[TRADING PERIOD]")
    print(f"  First Trade: {first_trade[:10]}")
    print(f"  Last Trade: {last_trade[:10]}")
    
    # Calculate days trading
    try:
        start = datetime.fromisoformat(first_trade.replace('Z', '+00:00'))
        end = datetime.fromisoformat(last_trade.replace('Z', '+00:00'))
        days = (end - start).days
        if days < 1:
            days = 1
        print(f"  Days Trading: {days}")
        
        # Daily rate
        daily_pnl = total_pnl / days
        print(f"\n[DAILY PERFORMANCE]")
        print(f"  Daily Average: ${daily_pnl:+.2f}/day")
        
        # Projection to $1000
        if daily_pnl > 0:
            remaining = 1000 - total_pnl
            days_to_1000 = remaining / daily_pnl
            print(f"\n[PROJECTION TO $1000]")
            print(f"  Current Profit: ${total_pnl:.2f}")
            print(f"  Remaining to $1000: ${remaining:.2f}")
            print(f"  Est. Days to $1000: {days_to_1000:.1f} days ({days_to_1000/30:.1f} months)")
        else:
            print(f"\n[!] Currently not profitable - projection not possible")
            
    except Exception as e:
        print(f"  Error calculating dates: {e}")

print("\n" + "=" * 50)
