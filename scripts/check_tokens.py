import json
import plaid
from plaid.api import plaid_api
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
print(f"Tokens found: {list(tokens.keys())}")

for name, token in tokens.items():
    try:
        resp = client.accounts_get(AccountsGetRequest(access_token=token))
        print(f"\n=== {name} ===")
        for acct in resp['accounts']:
            print(f"  {acct['name']} | type={acct['type']} | subtype={acct.get('subtype', 'N/A')}")
    except Exception as e:
        print(f"Error for {name}: {e}")
