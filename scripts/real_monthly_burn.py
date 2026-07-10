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

# Look at 3 months for clearer pattern
end = datetime.now().date()
start = end - timedelta(days=90)

# Track by month
month_data = defaultdict(lambda: {
    'real_income': 0,      # Direct deposits, payroll
    'transfers_in': 0,   # Internal transfers, CC payments back
    'real_spending': 0,  # Money gone to merchants
    'cc_payments': 0,    # Paying down cards
    'transfers_out': 0,  # Moving to savings/other
    'big_items': [],
})

for bank_name, token in tokens.items():
    resp = client.transactions_get(TransactionsGetRequest(
        access_token=token,
        start_date=start,
        end_date=end,
        options=TransactionsGetRequestOptions(count=500),
    ))
    
    for tx in resp['transactions']:
        amt = tx['amount']
        date = str(tx['date'])[:7]  # YYYY-MM
        name = tx['name'].upper()
        
        # Categorize the transaction
        is_payroll = any(k in name for k in ['CREDENCE MANAGEM', 'PAYROLL', 'HOUSTON COUNTY'])
        is_tax_refund = any(k in name for k in ['IRS TREAS', 'TAX REF', 'GASTTAXRFD'])
        is_cc_payment = any(k in name for k in ['PAYMENT TO CHASE', 'AMEX EPAYMENT', 'AMERICAN EXPRESS ACH', 'PAYMENT THANK YOU', 'MOBILE PAYMENT'])
        is_internal_xfer = any(k in name for k in ['TRANSFER', 'EB TO SAVINGS', 'EB TO CHECKING', 'EB FROM', 'WIRE TO', 'WIRE TRANSFER'])
        is_interest = 'INTEREST' in name
        is_refund = any(k in name for k in ['AMAZON MKTPLACE PMTS', 'REFUND', 'CREDIT'])
        
        if amt < 0:  # Inflow
            if is_payroll or is_tax_refund:
                month_data[date]['real_income'] += abs(amt)
            elif is_cc_payment or is_internal_xfer or is_refund or is_interest:
                month_data[date]['transfers_in'] += abs(amt)
            else:
                # Other inflows
                month_data[date]['transfers_in'] += abs(amt)
        
        else:  # Outflow
            if is_cc_payment:
                month_data[date]['cc_payments'] += amt
            elif is_internal_xfer:
                month_data[date]['transfers_out'] += amt
            elif 'MILLEDGEVILLE' in name and 'WIRE' in name:
                month_data[date]['big_items'].append({'name': tx['name'], 'amount': amt})
            elif 'FOUNDATION ACADEMY' in name and amt > 500:
                month_data[date]['big_items'].append({'name': tx['name'], 'amount': amt})
            else:
                month_data[date]['real_spending'] += amt

print("=" * 80)
print("REAL MONTHLY BURN RATE (Last 3 Months)")
print("=" * 80)

for month in sorted(month_data.keys()):
    d = month_data[month]
    print(f"\n--- {month} ---")
    print(f"  Real Income (payroll + tax):      ${d['real_income']:,>10,.2f}")
    print(f"  Internal/Transfer Inflows:        ${d['transfers_in']:,>10,.2f}")
    print(f"  Real Spending (merchants, etc.):  ${d['real_spending']:,>10,.2f}")
    print(f"  Credit Card Payments:               ${d['cc_payments']:,>10,.2f}")
    print(f"  Internal Transfers Out:           ${d['transfers_out']:,>10,.2f}")
    
    if d['big_items']:
        print(f"  Big One-Time Items:")
        for item in d['big_items']:
            print(f"    {item['name'][:45]:45} ${item['amount']:>10,.2f}")
    
    net = d['real_income'] - d['real_spending'] - d['cc_payments']
    print(f"  NET (income - spend - cc pay):    ${net:,>10,.2f}")

# Averages
print("\n" + "=" * 80)
print("3-MONTH AVERAGES")
print("=" * 80)
total_income = sum(d['real_income'] for d in month_data.values())
total_spend = sum(d['real_spending'] for d in month_data.values())
total_cc = sum(d['cc_payments'] for d in month_data.values())
total_xfer_out = sum(d['transfers_out'] for d in month_data.values())
n = len(month_data)

print(f"Monthly Real Income:   ${total_income/n:,.2f}")
print(f"Monthly Real Spending: ${total_spend/n:,.2f}")
print(f"Monthly CC Payments:   ${total_cc/n:,.2f}")
print(f"Monthly Xfers Out:     ${total_xfer_out/n:,.2f}")
print(f"Net Flow:              ${(total_income - total_spend - total_cc)/n:,.2f}")
