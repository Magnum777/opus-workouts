import json
from datetime import datetime

with open('C:/Users/compj/.openclaw/workspace/finance/full_tx_dump.json', 'r') as f:
    data = json.load(f)

# Analyze Chase account
chase_txs = data.get('ZWQ1YK4PX5COQQPVJRKRI86BJ9V0DGF4V8KZG', [])

print(f"Total Chase transactions: {len(chase_txs)}")
print("\nFirst 20 transactions:")
for tx in chase_txs[:20]:
    print(f"  {tx['date']} | ${tx['amount']:>8,.2f} | {tx['name'][:60]}")

# Show all transactions by month
from collections import defaultdict
monthly = defaultdict(list)
for tx in chase_txs:
    monthly[tx['date'][:7]].append(tx)

print("\n\nTransactions by month:")
for month in sorted(monthly.keys()):
    txs = monthly[month]
    print(f"\n{month} ({len(txs)} transactions):")
    for tx in txs[:5]:  # Show first 5
        print(f"  {tx['date']} | ${tx['amount']:>8,.2f} | {tx['name'][:60]}")
    if len(txs) > 5:
        print(f"  ... and {len(txs)-5} more")
