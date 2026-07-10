import json
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
import plaid
from datetime import datetime, timedelta

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

print("=" * 80)
print("ALL MONEY COMING IN (Last 90 Days)")
print("=" * 80)
print(f"{'Date':12} {'Amount':>12} {'Bank':15} {'Name':45}")
print("-" * 80)

total_in = 0.0

for bank_name, token in tokens.items():
    resp = client.transactions_get(TransactionsGetRequest(
        access_token=token,
        start_date=start,
        end_date=end,
        options=TransactionsGetRequestOptions(count=500),
    ))
    
    for tx in resp['transactions']:
        amt = tx['amount']
        if amt < 0:  # Inflow
            date_str = str(tx['date'])
            name = tx['name'][:45]
            total_in += abs(amt)
            print(f"{date_str:12} ${abs(amt):>10,.2f} {bank_name[:14]:15} {name:45}")

print("-" * 80)
print(f"{'TOTAL':12} ${total_in:>10,.2f}")
