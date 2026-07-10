#!/usr/bin/env python3
"""
Extract recurring monthly expenses from transaction history.
Looks for same merchants, similar amounts, monthly patterns.
"""

import os
import json
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
import plaid
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Plaid credentials from environment
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID', '')
PLAID_SECRET = os.environ.get('PLAID_SECRET', '')

if not PLAID_CLIENT_ID or not PLAID_SECRET:
    logger.error("PLAID_CLIENT_ID and PLAID_SECRET must be set as environment variables")
    raise ValueError("Missing Plaid credentials")

config = plaid.Configuration(
    host='https://production.plaid.com',
    api_key={'clientId': PLAID_CLIENT_ID, 'secret': PLAID_SECRET}
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))
tokens = json.load(open('credentials/.plaid_tokens.json'))

end = datetime.now().date()
start = end - timedelta(days=180)  # 6 months for pattern detection

# Collect all transactions
all_tx = []
for bank_name, token in tokens.items():
    resp = client.transactions_get(TransactionsGetRequest(
        access_token=token,
        start_date=start,
        end_date=end,
        options=TransactionsGetRequestOptions(count=500),
    ))
    for tx in resp['transactions']:
        if tx['amount'] > 0:  # Outflows only
            all_tx.append({
                'date': str(tx['date']),
                'name': tx['name'],
                'amount': tx['amount'],
                'category': tx.get('category', ['Uncategorized'])[0] if tx.get('category') else 'Uncategorized',
                'bank': bank_name,
            })

# Group by merchant name (cleaned)
by_merchant = defaultdict(list)
for tx in all_tx:
    # Clean merchant name for grouping
    name = tx['name'].upper()
    # Remove common suffixes/prefixes
    for suffix in [' ACH DEBIT', ' ACH PMT', ' AUTOMATIC PAYMENT', ' RECURRING', ' SUBSCRIPTION']:
        name = name.replace(suffix, '')
    by_merchant[name].append(tx)

# Find recurring expenses (same merchant, multiple times, similar amounts)
recurring = []
for merchant, txs in by_merchant.items():
    if len(txs) >= 2:  # At least 2 occurrences
        amounts = [t['amount'] for t in txs]
        avg = sum(amounts) / len(amounts)
        variance = max(amounts) - min(amounts)
        
        # Check if amounts are similar (within 10% or $5)
        if variance <= max(avg * 0.1, 5):
            # Check monthly pattern
            dates = sorted([datetime.strptime(t['date'], '%Y-%m-%d') for t in txs])
            if len(dates) >= 2:
                gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                avg_gap = sum(gaps) / len(gaps)
                
                # Recurring if gap is roughly 28-35 days or weekly-ish
                if 20 <= avg_gap <= 40:
                    frequency = 'Monthly'
                elif 5 <= avg_gap <= 9:
                    frequency = 'Weekly'
                else:
                    frequency = 'Irregular'
                
                if frequency in ['Monthly', 'Weekly']:
                    recurring.append({
                        'merchant': merchant[:50],
                        'avg_amount': avg,
                        'frequency': frequency,
                        'count': len(txs),
                        'last_date': dates[-1].strftime('%Y-%m-%d'),
                        'bank': txs[0]['bank'][:10],
                        'category': txs[0]['category'],
                    })

# Also find big one-off expenses
big_expenses = []
for tx in all_tx:
    if tx['amount'] >= 500:
        big_expenses.append(tx)

# Housing/mortgage specifically
housing = [t for t in all_tx if any(k in t['name'].upper() for k in ['MORTGAGE', 'RENT', 'TRUIST', 'MILLEDGEVILLE', 'WIRE'])]

print("=" * 80)
print("MONTHLY EXPENSES EXTRACTED FROM 6-MONTH HISTORY")
print("=" * 80)

print("\n--- RECURRING MONTHLY EXPENSES ---")
print(f"{'Merchant':40} {'Avg':>10} {'Freq':10} {'Count':6} {'Last':12} {'Category':20}")
print("-" * 80)

total_monthly = 0
for r in sorted(recurring, key=lambda x: x['avg_amount'], reverse=True):
    print(f"{r['merchant']:40} ${r['avg_amount']:>9,.2f} {r['frequency']:10} {r['count']:>5}x   {r['last_date']:12} {r['category']:20}")
    if r['frequency'] == 'Monthly':
        total_monthly += r['avg_amount']
    elif r['frequency'] == 'Weekly':
        total_monthly += r['avg_amount'] * 4.3

print(f"\nEstimated monthly recurring: ${total_monthly:,.2f}")

print("\n--- HOUSING / BIG FIXED COSTS ---")
for h in housing[-10:]:
    print(f"  {h['date']} {h['name'][:50]:50} ${h['amount']:>10,.2f}")

print("\n--- BIG ONE-OFF EXPENSES (>$500 in 6 months) ---")
for b in sorted(big_expenses, key=lambda x: x['amount'], reverse=True)[:15]:
    print(f"  {b['date']} {b['name'][:50]:50} ${b['amount']:>10,.2f}")

# Calculate true monthly burn rate
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total transactions analyzed: {len(all_tx)}")
print(f"Recurring monthly expenses: ${total_monthly:,.2f}")
print(f"Estimated true monthly spend: ${total_monthly:,.2f} (recurring) + variable")
