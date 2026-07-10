import json
from datetime import datetime
from collections import defaultdict

with open('C:/Users/compj/.openclaw/workspace/finance/full_tx_dump.json', 'r') as f:
    data = json.load(f)

# Find the Chase account key (case-insensitive)
chase_key = None
for key in data.keys():
    if 'zwq' in key.lower():
        chase_key = key
        break

print(f"Chase account key: {chase_key}")
print(f"Total transactions: {len(data[chase_key])}")

chase_txs = data[chase_key]

# Show sample transactions
print("\nFirst 10 transactions:")
for tx in chase_txs[:10]:
    print(f"  {tx['date']} | ${tx['amount']:>8,.2f} | {tx['name'][:60]}")

# Filter to spending only (exclude transfers, payments, income)
excluded_keywords = [
    'PAYMENT', 'EPAYMENT', 'EPAY', 'AUTOPAY', 'CREDIT CRD',
    'ONLINE TRANSFER', 'EB FROM', 'EB TO', 'INTEREST',
    'AMERICAN EXPRESS', 'AMEX', 'PAYROLL'
]

spending_txs = []
for tx in chase_txs:
    desc_upper = tx['name'].upper()
    if any(kw in desc_upper for kw in excluded_keywords):
        continue
    if tx['amount'] < 0:  # Income is negative in Plaid, spending is positive
        continue
    spending_txs.append(tx)

print(f"\nSpending transactions: {len(spending_txs)}")

# Calculate monthly spending
monthly_totals = defaultdict(float)
monthly_counts = defaultdict(int)

for tx in spending_txs:
    month_key = tx['date'][:7]
    monthly_totals[month_key] += tx['amount']
    monthly_counts[month_key] += 1

print("\nPrime Visa Monthly Spending:")
print("=" * 60)
for month in sorted(monthly_totals.keys()):
    total = monthly_totals[month]
    count = monthly_counts[month]
    print(f"{month}: ${total:>10,.2f}  ({count} transactions)")

# Average excluding June 2026
non_june_months = {k: v for k, v in monthly_totals.items() if k != '2026-06'}
if non_june_months:
    avg = sum(non_june_months.values()) / len(non_june_months)
    print(f"\nAverage monthly spending (excluding June): ${avg:,.2f}")
    print(f"Months averaged: {len(non_june_months)}")
    print(f"Lowest month: ${min(non_june_months.values()):,.2f}")
    print(f"Highest month: ${max(non_june_months.values()):,.2f}")
