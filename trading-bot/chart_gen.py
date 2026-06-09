import json, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Load data
hl = json.load(open('health_log.json'))
daily_health = {}
for h in hl:
    d = h['timestamp'][:10]
    pv = h.get('portfolio_value')
    if pv is not None:
        daily_health[d] = pv

sl = json.load(open('scout-log.json'))
daily_scout = {}
for s in sl:
    if s.get('type') == 'SCAN_COMPLETE':
        d = s['timestamp'][:10]
        pv = s.get('data', {}).get('portfolio_usd')
        if pv is not None:
            daily_scout[d] = pv

pd = json.load(open('portfolio.db.json'))
current_val = pd.get('portfolio', {}).get('total_value_usd', 0)
current_ts = pd.get('last_updated', '')

# Build daily points (scout overrides health, current overrides all)
daily_points = {}
for d, v in daily_health.items():
    daily_points[d] = v
for d, v in daily_scout.items():
    daily_points[d] = v
if current_ts:
    daily_points[current_ts[:10]] = current_val

dates = sorted(daily_points.keys())
values = [daily_points[d] for d in dates]

print('Dates:', dates)
print('Values:', values)
print('Current:', current_val)

# Chart
fig, ax = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor('#0a1628')
ax.set_facecolor('#0a1628')

ax.plot(range(len(dates)), values, color='#00d4aa', linewidth=2, marker='o', markersize=8,
        markerfacecolor='#00d4aa', markeredgecolor='#0a1628', markeredgewidth=2, zorder=5)

ax.set_xticks(range(len(dates)))
ax.set_xticklabels(dates, rotation=35, ha='right', fontsize=10, color='#a0b0c0')

for i, v in enumerate(values):
    offset = 15 if i % 2 == 0 else -25
    va = 'bottom' if i % 2 == 0 else 'top'
    label = '${:.2f}'.format(v)
    ax.annotate(label, (i, v), textcoords='offset points',
                xytext=(0, offset), ha='center', va=va,
                fontsize=9, fontweight='bold', color='#e0e0e0',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a2a44', edgecolor='#00d4aa', alpha=0.8))

ax.set_title('Daily Portfolio Value - Last 30 Days', fontsize=18, fontweight='bold', color='#e0e0e0', pad=20)
ax.set_ylabel('Portfolio Value (USD)', fontsize=13, color='#a0b0c0')
ax.grid(True, alpha=0.2, linestyle='--', color='#3a5a7a')
ax.tick_params(colors='#a0b0c0')
for spine in ax.spines.values():
    spine.set_color('#2a4a6a')

ax.axhline(y=100, color='#ff6b35', linestyle='--', alpha=0.5, linewidth=1)
ax.text(len(dates)-0.5, 100, '$100', color='#ff6b35', fontsize=9, alpha=0.7, va='bottom')

start_v, end_v = values[0], values[-1]
change_v = end_v - start_v
change_pct = (change_v / start_v * 100) if start_v else 0
change_sign = '+' if change_v >= 0 else ''

stats = ('Start: ${:.2f}\nCurrent: ${:.2f}\nChange: {}{:.2f} ({}{:.1f}%)\nHigh: ${:.2f}\nLow: ${:.2f}'.format(
    start_v, end_v, change_sign, change_v, change_sign, change_pct, max(values), min(values)))

props = dict(boxstyle='round', facecolor='#1a2a44', edgecolor='#00d4aa', alpha=0.9)
ax.text(0.02, 0.97, stats, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', color='#e0e0e0', bbox=props, fontfamily='monospace')

plt.tight_layout()
path = 'portfolio_30day.png'
fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='#0a1628', edgecolor='none')
print('Saved to', os.path.abspath(path))
print('File exists:', os.path.exists(path))
print('File size:', os.path.getsize(path))