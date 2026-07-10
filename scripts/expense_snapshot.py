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
start = end - timedelta(days=90)

spending_by_category = defaultdict(float)
spending_by_merchant = defaultdict(float)
monthly_totals = defaultdict(float)
daily_average = 0
total_outflows = 0
total_inflows = 0

all_tx = []

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
        name = tx['name']
        cat = tx.get('category', ['Uncategorized'])[0] if tx.get('category') else 'Uncategorized'
        
        if hasattr(date, 'isoformat'):
            month = date.isoformat()[:7]
        else:
            month = str(date)[:7]
        
        if amt > 0:  # Outflow (spending)
            spending_by_category[cat] += amt
            spending_by_merchant[name] += amt
            monthly_totals[month] += amt
            total_outflows += amt
        else:  # Inflow (income/refund)
            total_inflows += abs(amt)
        
        all_tx.append({'date': str(date), 'name': name, 'amount': amt, 'cat': cat, 'bank': bank_name})

print("="*70)
print("90-DAY EXPENSE SNAPSHOT")
print(f"Period: {start} to {end}")
print("="*70)

print(f"\nTotal Money Out:  ${total_outflows:,.2f}")
print(f"Total Money In:   ${total_inflows:,.2f}")
print(f"Net Flow:          ${total_inflows - total_outflows:,.2f}")

if monthly_totals:
    avg_monthly = sum(monthly_totals.values()) / len(monthly_totals)
    print(f"Avg Monthly Spend: ${avg_monthly:,.2f}")
    print(f"Daily Average:     ${avg_monthly/30:,.2f}")

print("\n" + "="*70)
print("SPENDING BY CATEGORY (Top 15)")
print("="*70)
for cat, amt in sorted(spending_by_category.items(), key=lambda x: x[1], reverse=True)[:15]:
    pct = (amt / total_outflows * 100) if total_outflows else 0
    print(f"  {cat:40} ${amt:>10,.2f}  ({pct:>5.1f}%)")

print("\n" + "="*70)
print("TOP MERCHANTS (Top 20)")
print("="*70)
for merch, amt in sorted(spending_by_merchant.items(), key=lambda x: x[1], reverse=True)[:20]:
    pct = (amt / total_outflows * 100) if total_outflows else 0
    print(f"  {merch:40} ${amt:>10,.2f}  ({pct:>5.1f}%)")

print("\n" + "="*70)
print("MONTHLY TOTALS")
print("="*70)
for month in sorted(monthly_totals.keys()):
    print(f"  {month}: ${monthly_totals[month]:,.2f}")
