import re
from datetime import datetime
from collections import defaultdict

# Read the transaction dump
with open('C:/Users/compj/.openclaw/workspace/finance/tx_dump.txt', 'r', encoding='utf-8') as f:
    data = f.read()

# Parse transactions
tx_pattern = r'(\d{4}-\d{2}-\d{2})\s+([+-])\$?([\d,]+\.\d{2})\s+-\s+(.*)'

accounts = {}
current_account = None

for line in data.split('\n'):
    if line.startswith('=== '):
        current_account = line.replace('=== ', '').replace(' ===', '').strip()
        accounts[current_account] = []
    elif line.strip().startswith('2026'):
        match = re.match(tx_pattern, line.strip())
        if match:
            date_str, sign, amount, desc = match.groups()
            amount = float(amount.replace(',', ''))
            if sign == '-':
                amount = -amount
            accounts[current_account].append({
                'date': datetime.strptime(date_str, '%Y-%m-%d'),
                'amount': amount,
                'desc': desc.strip()
            })

# Analyze each account
for account, txs in accounts.items():
    print(f"\n{'='*60}")
    print(f"Account: {account[:20]}...")
    
    # Find all CC payments
    payments = [tx for tx in txs if any(kw in tx['desc'].upper() for kw in 
        ['PAYMENT', 'EPAYMENT', 'EPAY', 'AUTOPAY', 'CREDIT CRD'])]
    
    # Find all interest charges
    interest = [tx for tx in txs if 'INTEREST' in tx['desc'].upper()]
    
    # Monthly totals
    monthly = defaultdict(float)
    monthly_income = defaultdict(float)
    
    for tx in txs:
        month_key = tx['date'].strftime('%Y-%m')
        if tx['amount'] > 0:
            monthly_income[month_key] += tx['amount']
        else:
            monthly[month_key] += tx['amount']
    
    print(f"\nTotal transactions: {len(txs)}")
    print(f"Payments to CCs: {len(payments)}")
    for p in payments:
        print(f"  {p['date'].strftime('%Y-%m-%d')}: ${p['amount']:,.2f} - {p['desc'][:50]}")
    
    print(f"\nInterest charges: {len(interest)}")
    for i in interest:
        print(f"  {i['date'].strftime('%Y-%m-%d')}: ${i['amount']:,.2f} - {i['desc']}")
    
    print(f"\nMonthly spending (last 6 months):")
    for month in sorted(monthly.keys())[-6:]:
        income = monthly_income.get(month, 0)
        spend = monthly[month]
        print(f"  {month}: Income=${income:>10,.2f}  Spend=${spend:>10,.2f}  Net=${income+spend:>10,.2f}")
