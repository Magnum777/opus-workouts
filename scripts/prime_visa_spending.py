import re
from datetime import datetime
from collections import defaultdict

# Read the transaction dump
with open('C:/Users/compj/.openclaw/workspace/finance/tx_dump.txt', 'r', encoding='utf-8') as f:
    data = f.read()

# Parse Chase account transactions
tx_pattern = r'(\d{4}-\d{2}-\d{2})\s+([+-])\$?([\d,]+\.\d{2})\s+-\s+(.*)'

chase_txs = []
in_chase = False

for line in data.split('\n'):
    if '=== ZWQ1YK4PX5COQQPVJRKRI86BJ9V0DGF4V8KZG' in line:
        in_chase = True
        continue
    if line.startswith('===') and in_chase:
        in_chase = False
        continue
    if in_chase and line.strip().startswith('2026'):
        match = re.match(tx_pattern, line.strip())
        if match:
            date_str, sign, amount, desc = match.groups()
            amount = float(amount.replace(',', ''))
            if sign == '-':
                amount = -amount
            chase_txs.append({
                'date': datetime.strptime(date_str, '%Y-%m-%d'),
                'amount': amount,
                'desc': desc.strip()
            })

# Filter out non-spending transactions
excluded_keywords = [
    'TRANSFER', 'PAYMENT', 'EPAYMENT', 'EPAY', 'AUTOPAY', 
    'AMERICAN EXPRESS', 'AMEX', 'INTEREST CHARGE',
    'ONLINE TRANSFER', 'EB FROM', 'EB TO'
]

prime_visa_spending = []
for tx in chase_txs:
    desc_upper = tx['desc'].upper()
    if any(kw in desc_upper for kw in excluded_keywords):
        continue
    if tx['amount'] > 0:
        continue  # Skip income/returns
    prime_visa_spending.append(tx)

# Calculate monthly totals (excluding June 2026)
monthly_totals = defaultdict(float)
monthly_counts = defaultdict(int)

for tx in prime_visa_spending:
    month_key = tx['date'].strftime('%Y-%m')
    if month_key == '2026-06':
        continue
    monthly_totals[month_key] += abs(tx['amount'])
    monthly_counts[month_key] += 1

print("Prime Visa Monthly Spending (excluding June 2026):")
print("=" * 60)
for month in sorted(monthly_totals.keys()):
    total = monthly_totals[month]
    count = monthly_counts[month]
    print(f"{month}: ${total:>10,.2f}  ({count} transactions)")

if monthly_totals:
    avg = sum(monthly_totals.values()) / len(monthly_totals)
    print(f"\nAverage monthly spending: ${avg:,.2f}")
    print(f"Months averaged: {len(monthly_totals)}")

# Show all transactions for verification
print("\n\nAll Prime Visa transactions (excluding June):")
print("=" * 60)
for tx in prime_visa_spending:
    if tx['date'].strftime('%Y-%m') != '2026-06':
        print(f"{tx['date'].strftime('%Y-%m-%d')}: ${abs(tx['amount']):>8,.2f} - {tx['desc'][:55]}")
