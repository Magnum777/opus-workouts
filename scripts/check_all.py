import json
import plaid
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.liabilities_get_request import LiabilitiesGetRequest

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
    print(f"\n=== {name} ===")
    
    resp = client.accounts_get(AccountsGetRequest(access_token=token))
    for acct in resp['accounts']:
        bal = acct['balances']
        cur = bal.get('current') or 0
        avail = bal.get('available')
        t = str(acct['type'])
        print(f"  {acct['name']:30} | {t:12} | mask={acct.get('mask', '****')} | current=${cur:,.2f}", end="")
        if avail is not None:
            print(f" | avail=${avail:,.2f}")
        else:
            print()
    
    try:
        liab = client.liabilities_get(LiabilitiesGetRequest(access_token=token))
        credit = liab['liabilities'].get('credit', [])
        if credit:
            print(f"\n  Credit Details ({len(credit)} cards):")
            for c in credit:
                last_pmt = c.get('last_payment_amount') or 0
                min_pmt = c.get('minimum_payment_amount') or 0
                due = c.get('next_payment_due_date', 'N/A')
                print(f"    {c.get('name', 'Unknown'):30} | last_payment=${last_pmt:,.2f} | min_payment=${min_pmt:,.2f} | next_due={due}")
    except Exception as e:
        print(f"\n  No liability details: {e}")
