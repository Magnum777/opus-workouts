import json
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
import plaid

from vault_helper import get_credential

PLAID_CLIENT_ID = get_credential('plaid', 'client_id')
PLAID_SANDBOX_SECRET = get_credential('plaid', 'sandbox_secret')

config = plaid.Configuration(
    host='https://sandbox.plaid.com',
    api_key={'clientId': PLAID_CLIENT_ID, 'secret': PLAID_SANDBOX_SECRET}
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))
tokens = json.load(open('credentials/.plaid_tokens.json'))
token = tokens.get('chase-sandbox', list(tokens.values())[0])
resp = client.accounts_get(AccountsGetRequest(access_token=token))

nw = 0
assets = 0
liabilities = 0
for a in resp['accounts']:
    cur = a['balances']['current'] or 0
    t = str(a['type'])
    print(f'{a["name"]:30} type={t:15} current=${cur:,.2f}')
    if t in ('depository', 'investment'):
        nw += cur
        assets += cur
    elif t in ('credit', 'loan'):
        nw -= cur
        liabilities += abs(cur)

print(f'\nAssets: ${assets:,.2f}')
print(f'Liabilities: ${liabilities:,.2f}')
print(f'Net Worth: ${nw:,.2f}')
