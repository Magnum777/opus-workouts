import json
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.liabilities_get_request import LiabilitiesGetRequest
import plaid

from vault_helper import get_credential

PLAID_CLIENT_ID = get_credential('plaid', 'client_id')
PLAID_SECRET = get_credential('plaid', 'secret')

config = plaid.Configuration(
    host='https://production.plaid.com',
    api_key={'clientId': PLAID_CLIENT_ID, 'secret': PLAID_SECRET}
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))
tokens = json.load(open('credentials/.plaid_tokens.json'))

total_credit_used = 0
total_credit_limit = 0
liquid = 0
investments = 0
upcoming = []

print("=== ALL ACCOUNTS ===\n")

for name, token in tokens.items():
    print(f"--- {name[:20]} ---")
    acct_resp = client.accounts_get(AccountsGetRequest(access_token=token))
    for a in acct_resp['accounts']:
        t = str(a['type'])
        cur = a['balances'].get('current') or 0
        avail = a['balances'].get('available') or 0
        mask = a.get('mask', '****')
        
        if t == 'credit':
            limit = cur + avail
            total_credit_used += cur
            total_credit_limit += limit
            print(f"  CREDIT: {a['name']:35} ****{mask} | balance=${cur:>10,.2f} | limit=${limit:>10,.2f}")
        elif t == 'depository':
            liquid += cur
            print(f"  CASH:   {a['name']:35} ****{mask} | balance=${cur:>10,.2f}")
        elif t == 'investment':
            investments += cur
            print(f"  INVEST: {a['name']:35} ****{mask} | balance=${cur:>10,.2f}")
        else:
            print(f"  OTHER:  {a['name']:35} ****{mask} | type={t:12} | balance=${cur:>10,.2f}")
    
    try:
        liab = client.liabilities_get(LiabilitiesGetRequest(access_token=token))
        for cc in liab['liabilities'].get('credit', []):
            upcoming.append({
                'card': cc.get('name', 'Unknown'),
                'min': cc.get('minimum_payment_amount') or 0,
                'due': str(cc.get('next_payment_due_date', 'N/A')),
                'last_pmt': cc.get('last_payment_amount') or 0,
            })
    except:
        pass

print("\n" + "="*60)
print("DEBT SNAPSHOT")
print("="*60)
print(f"Total Credit Card Debt:      ${total_credit_used:>12,.2f}")
print(f"Total Credit Limit:          ${total_credit_limit:>12,.2f}")
print(f"Utilization Rate:            {total_credit_used/total_credit_limit*100 if total_credit_limit else 0:>12.1f}%")
print(f"Available Credit:            ${total_credit_limit - total_credit_used:>12,.2f}")

print("\n" + "="*60)
print("CASH SNAPSHOT")
print("="*60)
print(f"Total Liquid Cash:           ${liquid:>12,.2f}")
print(f"Investments:                 ${investments:>12,.2f}")
print(f"Total Assets:                ${liquid + investments:>12,.2f}")

print("\n" + "="*60)
print("NET POSITION")
print("="*60)
net = liquid + investments - total_credit_used
print(f"Cash minus CC debt:          ${net:>12,.2f}")
print(f"If you paid off ALL CCs today: ${liquid - total_credit_used:>12,.2f} left")

print("\n" + "="*60)
print("UPCOMING MINIMUM PAYMENTS")
print("="*60)
for p in upcoming:
    print(f"  {p['card']:40} min=${p['min']:>8,.2f}  due={p['due']:12}  last_paid=${p['last_pmt']:>10,.2f}")
