import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timezone
import collections

# ---- Source 1: Health log ----
hl = json.load(open('health_log.json'))
daily_health = {}
for h in hl:
    d = h['timestamp'][:10]
    pv = h.get('portfolio_value')
    if pv is not None:
        dt = datetime.strptime(d, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        if d not in daily_health:
            daily_health[d] = {'date': dt, 'values': [], 'first': pv, 'last': pv}
        daily_health[d]['values'].append(pv)
        daily_health[d]['last'] = pv

# ---- Source 2: Scout log portfolio_usd ----
sl = json.load(open('scout-log.json'))
daily_scout = {}
for s in sl:
    if s.get('type') == 'SCAN_COMPLETE':
        d = s['timestamp'][:10]
        pv = s.get('data', {}).get('portfolio_usd')
        if pv is not None:
            dt = datetime.strptime(d, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            if d not in daily_scout:
                daily_scout[d] = {'date': dt, 'values': []}
            daily_scout[d]['values'].append(pv)

# ---- Source 3: Latest portfolio.db snapshot ----
pd = json.load(open('portfolio.db.json'))
current_total = pd.get('portfolio', {}).get('total_value_usd', 0)
current_ts = pd.get('last_updated', '')
if current_ts:
    current_date = current_ts[:10]

# ---- Source 4: Reconstruct from trades where possible ----
# We know:
# May 6: $74.53 (scout)
# May 28: first buys = $100 deployed (need opening value estimate)
# Let's estimate from available trades

# Build daily points with explicit dates
# Scout data gives us per-minute precision, so average per day
daily_points = {}

# Health log: take last value of each day
for d, info in sorted(daily_health.items()):
    daily_points[d] = info['last']

# Scout log: take average per day
for d, info in daily_scout.items():
    if d in daily_points:
        # Overwrite with scout data if available (more precise)
        daily_points[d] = info['values'][-1]  # last scan of the day
    else:
        daily_points[d] = info['values'][-1]

# Add current portfolio value
if current_ts:
    cd = current_ts[:10]
    # Only add if not May 1 (Jun 1 gap)
    daily_points[cd] = current_total

# Now generate the chart with all available data points
dates = sorted(daily_points.keys())
values = [daily_points[d] for d in dates]

fig, ax = plt.subplots(figsize=(14, 7))

# Plot as line with markers
ax.plot(dates, values, color='#00d4aa', linewidth=2, marker='o', markersize=8, 
        markerfacecolor='#00d4aa', markeredgecolor='#0a1628', markeredgewidth=2, zorder=5)

# Highlight current value
if current_ts:
    cd = current_ts[:10]
    if cd in daily_points:
        ax.scatter([cd], [daily_points[cd]], color='#ff6b35', s=200, zorder=10,
                   edgecolors='white', linewidth=2, label=f'Current: ${daily_points[cd]:.2f}')

# Add value labels on each point
for i, (d, v) in enumerate(zip(dates, values)):
    offset = 15 if i % 2 == 0 else -25
    va = 'bottom' if i % 2 == 0 else 'top'
    ax.annotate(f'${v:.2f}', (d, v), textcoords="offset points", 
                xytext=(0, offset), ha='center', va=va,
                fontsize=9, fontweight='bold', color='#e0e0e0',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a2a44', edgecolor='#00d4aa', alpha=0.8))

# Format date labels
ax.set_xticks(range(len(dates)))
ax.set_xticklabels(dates, rotation=35, ha='right', fontsize=10)

# Styling
fig.patch.set_facecolor('#0a1628')
ax.set_facecolor('#0a1628')
ax.set_title('Daily Portfolio Value — Last 30 Days', fontsize=18, fontweight='bold', color='#e0e0e0', pad=20)
ax.set_ylabel('Portfolio Value (USD)', fontsize=13, color='#a0b0c0')
ax.grid(True, alpha=0.2, linestyle='--', color='#3a5a7a')
ax.tick_params(colors='#a0b0c0')

# Style spines
for spine in ax.spines.values():
    spine.set_color('#2a4a6a')
    spine.set_linewidth(0.5)

# Add reference line at $100
ax.axhline(y=100, color='#ff6b35', linestyle='--', alpha=0.5, linewidth=1)
ax.text(len(dates)-0.5, 100, '$100', color='#ff6b35', fontsize=9, alpha=0.7, va='bottom')

# Portfolio summary stats box
min_v = min(values) if values else 0
max_v = max(values) if values else 0
start_v = values[0] if values else 0
end_v = values[-1] if values else 0
change_v = end_v - start_v
change_pct = (change_v / start_v * 100) if start_v else 0

change_color = '#00d4aa' if change_v >= 0 else '#ff4444'
change_sign = '+' if change_v >= 0 else ''

stats_text = (
    f'Start: ${start_v:.2f}\n'
    f'Current: ${end_v:.2f}\n'
    f'Change: {change_sign}${change_v:.2f} ({change_sign}{change_pct:.1f}%)\n'
    f'High: ${max_v:.2f}\n'
    f'Low: ${min_v:.2f}'
)

props = dict(boxstyle='round', facecolor='#1a2a44', edgecolor='#00d4aa', alpha=0.9)
ax.text(0.02, 0.97, stats_text, transform=ax.transAxes, fontsize=11, 
        verticalalignment='top', color='#e0e0e0', bbox=props, fontfamily='monospace')

plt.tight_layout()
plt.savefig('trading-bot/portfolio_30day.png', dpi=150, bbox_inches='tight',
            facecolor='#0a1628', edgecolor='none')
print(f'Chart saved. Data points: {len(dates)}')
print(f'Dates: {dates}')
print(f'Values: {values}')
print(f'Current: ${current_total:.2f}')