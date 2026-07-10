import json
from datetime import datetime
from collections import defaultdict

with open('C:/Users/compj/.openclaw/workspace/finance/full_tx_dump.json', 'r') as f:
    data = json.load(f)

# Find the Chase account key
chase_key = None
for key in data.keys():
    if 'zwq' in key.lower():
        chase_key = key
        break

print(f"Chase account key: {chase_key}")

chase_txs = data[chase_key]

# Show ALL fields from first transaction to see if we have account_id
print("\nFirst transaction fields:")
first_tx = chase_txs[0]
for k, v in first_tx.items():
    print(f"  {k}: {v}")

# Group by account_id if available
accounts = defaultdict(list)
for tx in chase_txs:
    acct_id = tx.get('account_id', 'unknown')
    accounts[acct_id].append(tx)

print(f"\nTransactions grouped by account_id:")
for acct_id, txs in accounts.items():
    print(f"  {acct_id}: {len(txs)} transactions")
