import json
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

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
    print(f"Creating update token for {name}...")
    try:
        # Create an update mode link token
        req = LinkTokenCreateRequest(
            access_token=token,
            products=[Products("liabilities")],
            client_name="Nova Finance",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id="opus-nova-001"),
        )
        resp = client.link_token_create(req)
        update_token = resp['link_token']
        print(f"Update token: {update_token}")
        print("\nUse this token to launch Plaid Link in UPDATE mode:")
        print(f"  Token: {update_token}")
    except Exception as e:
        print(f"Error: {e}")
