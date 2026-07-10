import plaid
from plaid.api import plaid_api
from plaid.model.institutions_get_request import InstitutionsGetRequest
from plaid.model.country_code import CountryCode

from vault_helper import get_credential

PLAID_CLIENT_ID = get_credential('plaid', 'client_id')
PLAID_SECRET = get_credential('plaid', 'secret')

config = plaid.Configuration(
    host="https://production.plaid.com",
    api_key={"clientId": PLAID_CLIENT_ID, "secret": PLAID_SECRET}
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))

try:
    req = InstitutionsGetRequest(count=3, offset=0, country_codes=[CountryCode("US")])
    resp = client.institutions_get(req)
    print(f"Production API OK! Found {len(resp['institutions'])} institutions")
    for inst in resp["institutions"]:
        print(f"  - {inst['name']} ({inst['institution_id']})")
except Exception as e:
    print(f"Production API Error: {e}")
