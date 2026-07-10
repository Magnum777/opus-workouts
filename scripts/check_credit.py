import json
import plaid
from plaid.api import plaid_api
from plaid.model.liabilities_get_request import LiabilitiesGetRequest
from plaid.model.accounts_get_request import AccountsGetRequest

from vault_helper import get_credential

PLAID_CLIENT_ID = get_credential('plaid', 'client_id')
PLAID_SECRET = get_credential('plaid', 'secret')

config = plaid.Configuration(
    host='https://production.plaid.com',
    api_key={'clientId': PLAID_CLIENT_ID, 'secret': PLAID_SECRET}
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))
tokens = json.load(open('credentials/.plaid_tokens.json'))

for name, token in tokens.items():
    print(f"=== {name} ===")
    # Try liabilities endpoint
    try:
        resp = client.liabilities_get(LiabilitiesGetRequest(access_token=token))
        if resp.get('liabilities'):
            credit = resp['liabilities'].get('credit', [])
            print(f"Credit liabilities: {len(credit)}")
            for c in credit:
                print(f"  {c.get('name', 'Unknown')}: ${c.get('last_payment_amount', 0)}")
        else:
            print("No liabilities data")
    except Exception as e:
        print(f"Liabilities error: {e}")
    
    # Check accounts again
    try:
        resp = client.accounts_get(AccountsGetRequest(access_token=token))
        for acct in resp['accounts']:
            t = str(acct['type'])
            if t == 'credit':
                print(f"  CREDIT FOUND: {acct['name']} mask={acct.get('mask', '****')}")
    except Exception as e:
        print(f"Accounts error: {e}")
