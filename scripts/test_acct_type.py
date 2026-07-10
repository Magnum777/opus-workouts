import json
import plaid
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest

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
acct = resp['accounts'][0]
print(f'Type: {repr(acct["type"])}')
print(f'Type value: {acct["type"].value}')
print(f'Subtype: {repr(acct.get("subtype"))}')
