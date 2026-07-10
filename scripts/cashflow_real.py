import os
import json
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
import plaid
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Plaid credentials from environment
PLAID_CLIENT_ID = os.environ.get('PLAID_CLIENT_ID', '')
PLAID_SECRET = os.environ.get('PLAID_SECRET', '')

if not PLAID_CLIENT_ID or not PLAID_SECRET:
    logger.error("PLAID_CLIENT_ID and PLAID_SECRET must be set as environment variables")
    raise ValueError("Missing Plaid credentials")

config = plaid.Configuration(
    host='https://production.plaid.com',
    api_key={'clientId': PLAID_CLIENT_ID, 'secret': PLAID_SECRET}
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))
tokens = json.load(open('credentials/.plaid_tokens.json'))

end = datetime.now().date()
start = end - timedelta(days=90)

# Track only REAL spending and REAL income
real_spending = defaultdict(float)
income_total = 0.0
transfers_between_accounts = 0.0
cc_payments = 0.0
one_time_big_items = []

for bank_name, token in tokens.items():
    resp = client.transactions_get(TransactionsGetRequest(
        access_token=token,
        start_date=start,
        end_date=end,
        options=TransactionsGetRequestOptions(count=500),
    ))
    
    for tx in resp['transactions']:
        amt = tx['amount']
        name = tx['name'].upper()
        cat = tx.get('category', [])
        cat_list = [c.upper() for c in cat] if cat else []
        
        # INCOME: Money coming IN (negative amount in Plaid)
        if amt < 0:
            # Only count direct deposits as income
            is_direct_deposit = any(k in name for k in ['DIRECT DEPOSIT', 'PAYROLL', 'SALARY', 'WAGE', 'ACH DEPOSIT'])
            is_transfer_in = any(k in name for k in ['TRANSFER', 'WIRE', 'EB TO', 'ZELLE', 'VENMO'])
            
            if is_direct_deposit:
                income_total += abs(amt)
            elif is_transfer_in:
                transfers_between_accounts += abs(amt)  # Money moving between his accounts
            # else: ignore other inflows
        
        # SPENDING: Money going OUT (positive amount in Plaid)
        elif amt > 0:
            # Credit card payments = paying down debt, not new spending
            is_cc_payment = any(k in name for k in ['PAYMENT TO CHASE', 'AMEX EPAYMENT', 'AMERICAN EXPRESS ACH', 'PAYMENT TO CARD'])
            is_transfer_out = any(k in name for k in ['TRANSFER', 'WIRE TO', 'EB TO SAVINGS', 'EB TO CHECKING', 'ZELLE', 'VENMO'])
            
            if is_cc_payment:
                cc_payments += amt
            elif is_transfer_out:
                transfers_between_accounts += amt  # Moving to savings/other accounts
            elif 'WIRE TRANSFER MILLEDGEVILLE' in name or ('WIRE' in name and 'MILLEDGEVILLE' in name):
                # Car down payment - one time
                one_time_big_items.append({'name': tx['name'], 'amount': amt, 'date': str(tx['date'])})
            else:
                # REAL SPENDING
                cat_label = cat[0] if cat else 'Uncategorized'
                real_spending[cat_label] += amt

print("=" * 70)
print("REAL CASH FLOW (90 Days)")
print(f"Period: {start} to {end}")
print("=" * 70)

print(f"\n--- INCOME (Direct Deposits Only) ---")
print(f"  Total Income:            ${income_total:>12,.2f}")

print(f"\n--- INTERNAL MOVEMENTS (Not Spending) ---")
print(f"  Transfers Between Accts: ${transfers_between_accounts:>12,.2f}")
print(f"  Credit Card Payments:    ${cc_payments:>12,.2f}")

if one_time_big_items:
    print(f"\n--- ONE-TIME ITEMS ---")
    for item in one_time_big_items:
        print(f"  {item['date']} {item['name'][:45]:45} ${item['amount']:>10,.2f}")

real_total = sum(real_spending.values())

print(f"\n--- REAL SPENDING (Money Actually Spent) ---")
print(f"  Total Real Spending:     ${real_total:>12,.2f}")

for cat, amt in sorted(real_spending.items(), key=lambda x: x[1], reverse=True):
    pct = (amt / real_total * 100) if real_total else 0
    print(f"    {cat:40} ${amt:>10,.2f}  ({pct:>5.1f}%)")

monthly_income = income_total / 3
monthly_spending = real_total / 3

print(f"\n--- MONTHLY AVERAGES ---")
print(f"  Monthly Income:          ${monthly_income:>12,.2f}")
print(f"  Monthly Real Spending:   ${monthly_spending:>12,.2f}")
print(f"  Surplus/Deficit:         ${monthly_income - monthly_spending:>12,.2f}")

print(f"\n--- DEBT PAYOFF MATH ---")
cc_debt = 16801.84
cash = 8664.74
print(f"  CC Debt:                 ${cc_debt:>12,.2f}")
print(f"  Cash on Hand:            ${cash:>12,.2f}")
print(f"  Cash - Debt:             ${cash - cc_debt:>12,.2f}")
print(f"  Monthly Surplus:         ${monthly_income - monthly_spending:>12,.2f}")

if monthly_income > monthly_spending:
    months_to_payoff = cc_debt / (monthly_income - monthly_spending)
    print(f"  Months to pay off debt:  {months_to_payoff:>12.1f}")
else:
    print(f"  Months to pay off:       INFINITE (spending exceeds income)")
