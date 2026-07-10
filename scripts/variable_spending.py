#!/usr/bin/env python3
"""
Variable spending analysis — where does the rest of the money go?
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
start = end - timedelta(days=90)

# Known recurring merchants (from previous analysis)
RECURRING_MERCHANTS = {
    'TRUIST MORTG', 'TRUIST LN', 'FLINT ELECTRIC', 'VERIZON WIRELESS',
    'FOUNDATION ACADEMY', 'DEPT EDUCATION STUDENT LN', 'WHITNEY ONDIKE',
    'SOJOURN CHURCH', 'MARGARITASMEXICABONAIRE', 'GOOGLE GOOGL', 'COX GEORGIA',
    'TIDAL WAVE', 'SHELL', 'HETZNER', 'STRAIGHT TALK', 'HULU', 'H P LIQUORS',
    'UBIQUITI', 'NETFLIX', 'ANCESTRY.COM', 'HOODBUSTERS', 'RESTREAM',
    'KAFFIBRENNSLAN', 'AUDIBLE', 'GOOGLE YOUTU', 'PUNCHBOWL.COM', 'BOOST',
    'PEACOCK', 'MICROSOFT*XBOX', 'TWITCH-TIER', 'FACEBOOKTEC', 'ELASTICMAIL',
    'SUNOCO', 'RED OWL COFFEE', 'MONTHLY FEE', 'AMAZON PRIME', 'PRIME VIDEO',
    'MEDIUM MONTHLY', 'AMEX EPAYMENT', 'PAYMENT TO CHASE', 'WIRE TRANSFER',
    'EB TO SAVINGS', 'EB TO CHECKING', 'PAYMENT THANK YOU', 'MOBILE PAYMENT',
}

variable_by_category = defaultdict(float)
variable_by_merchant = defaultdict(float)
recurring_total = 0
variable_total = 0

for bank_name, token in tokens.items():
    resp = client.transactions_get(TransactionsGetRequest(
        access_token=token,
        start_date=start,
        end_date=end,
        options=TransactionsGetRequestOptions(count=500),
    ))
    
    for tx in resp['transactions']:
        if tx['amount'] > 0:  # Outflow
            name = tx['name'].upper()
            is_recurring = any(r in name for r in RECURRING_MERCHANTS)
            is_internal = any(k in name for k in ['TRANSFER', 'WIRE TO', 'EB TO', 'ZELLE', 'VENMO'])
            is_cc_payment = any(k in name for k in ['PAYMENT TO CHASE', 'AMEX EPAYMENT', 'AMERICAN EXPRESS ACH', 'PAYMENT THANK YOU', 'MOBILE PAYMENT'])
            
            cat = tx.get('category', ['Uncategorized'])[0] if tx.get('category') else 'Uncategorized'
            
            if is_recurring or is_internal or is_cc_payment:
                recurring_total += tx['amount']
            else:
                variable_total += tx['amount']
                variable_by_category[cat] += tx['amount']
                variable_by_merchant[tx['name']] += tx['amount']

print("=" * 70)
print("VARIABLE SPENDING (90 Days) — Money You Actually Spent")
print("=" * 70)
print(f"Total Variable Spending: ${variable_total:,.2f}")
print(f"Monthly Average:         ${variable_total/3:,.2f}")
print(f"Recurring + Internal:    ${recurring_total:,.2f}")
print()

print("--- BY CATEGORY ---")
for cat, amt in sorted(variable_by_category.items(), key=lambda x: x[1], reverse=True):
    monthly = amt / 3
    print(f"  {cat:35} ${amt:>10,.2f} (${monthly:>8,.2f}/mo)")

print("\n--- TOP MERCHANTS (Variable Only) ---")
for merch, amt in sorted(variable_by_merchant.items(), key=lambda x: x[1], reverse=True)[:30]:
    monthly = amt / 3
    print(f"  {merch[:40]:40} ${amt:>10,.2f} (${monthly:>8,.2f}/mo)")

print("\n" + "=" * 70)
print("MONTHLY BUDGET PICTURE")
print("=" * 70)
print(f"Household Income:        ~$15,654")
print(f"Fixed Recurring Bills:   ~$4,351")
print(f"Variable Spending:       ~${variable_total/3:,.2f}")
print(f"Total Outflows:          ~${(recurring_total + variable_total)/3:,.2f}")
print(f"Remaining:               ~${15654 - (recurring_total + variable_total)/3:,.2f}")
