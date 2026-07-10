#!/usr/bin/env python3
"""
6-month spending overview — month by month, category by category
"""

import json
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
import plaid
from datetime import datetime, timedelta
from collections import defaultdict

from vault_helper import get_credential

PLAID_CLIENT_ID = get_credential('plaid', 'client_id')
PLAID_SECRET = get_credential('plaid', 'secret')

config = plaid.Configuration(
    host='https://production.plaid.com',
    api_key={'clientId': PLAID_CLIENT_ID, 'secret': PLAID_SECRET}
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))
tokens = json.load(open('credentials/.plaid_tokens.json'))

end = datetime.now().date()
start = end - timedelta(days=180)

# Structure: month -> category -> amount
months = defaultdict(lambda: defaultdict(float))
month_totals = defaultdict(float)
month_income = defaultdict(float)

for bank_name, token in tokens.items():
    resp = client.transactions_get(TransactionsGetRequest(
        access_token=token,
        start_date=start,
        end_date=end,
        options=TransactionsGetRequestOptions(count=500),
    ))
    
    for tx in resp['transactions']:
        amt = tx['amount']
        date = tx['date']
        if hasattr(date, 'isoformat'):
            month = date.isoformat()[:7]
        else:
            month = str(date)[:7]
        
        cat = tx.get('category', ['Uncategorized'])[0] if tx.get('category') else 'Uncategorized'
        
        if amt > 0:  # Outflow
            months[month][cat] += amt
            month_totals[month] += amt
        else:  # Inflow
            month_income[month] += abs(amt)

# Print month by month
print("=" * 80)
print("6-MONTH SPENDING OVERVIEW")
print(f"Period: {start} to {end}")
print("=" * 80)

all_categories = set()
for cats in months.values():
    all_categories.update(cats.keys())

# Sort months
sorted_months = sorted(months.keys())

print("\n--- MONTHLY TOTALS ---")
print(f"{'Month':10} {'Spent':>12} {'Income':>12} {'Net':>12}")
print("-" * 50)
for m in sorted_months:
    spent = month_totals[m]
    income = month_income[m]
    net = income - spent
    print(f"{m:10} ${spent:>10,.2f} ${income:>10,.2f} ${net:>10,.2f}")

# Show all categories across all months
print("\n--- SPENDING BY CATEGORY (per month) ---")
cat_list = sorted(all_categories)
header = f"{'Category':25} " + " ".join([f"{m[5:7]:>10}" for m in sorted_months]) + f" {'Total':>12}"
print(header)
print("-" * len(header))

for cat in cat_list:
    row = f"{cat:25}"
    total = 0
    for m in sorted_months:
        amt = months[m].get(cat, 0)
        row += f" ${amt:>9,.2f}"
        total += amt
    row += f" ${total:>10,.2f}"
    print(row)

# 6-month averages
print("\n--- 6-MONTH AVERAGES ---")
total_spent = sum(month_totals.values())
total_income = sum(month_income.values())
avg_monthly = total_spent / len(sorted_months) if sorted_months else 0
avg_income = total_income / len(sorted_months) if sorted_months else 0
print(f"Average Monthly Spend:   ${avg_monthly:,.2f}")
print(f"Average Monthly Income:  ${avg_income:,.2f}")
print(f"Average Net:             ${avg_income - avg_monthly:,.2f}")
print(f"Total Spent (6mo):       ${total_spent:,.2f}")
print(f"Total Income (6mo):      ${total_income:,.2f}")
