"""
Real Cash Flow Analyzer (90 days)

Fetches transactions via Plaid, separates real spending from transfers
and credit card payments, and prints a formatted cash flow report.

Uses vault_helper for Plaid credentials (P0 fix applied 2026-07-10).
"""

import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
import plaid

from vault_helper import get_credential

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load Plaid credentials from vault
PLAID_CLIENT_ID = get_credential('plaid', 'client_id') or os.environ.get('PLAID_CLIENT_ID', '')
PLAID_SECRET = get_credential('plaid', 'secret') or os.environ.get('PLAID_SECRET', '')

if not PLAID_CLIENT_ID or not PLAID_SECRET:
    logger.error("PLAID_CLIENT_ID and PLAID_SECRET must be set as environment variables or in vault")
    raise ValueError("Missing Plaid credentials")

config = plaid.Configuration(
    host='https://production.plaid.com',
    api_key={'clientId': PLAID_CLIENT_ID, 'secret': PLAID_SECRET}
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))


def load_tokens(path: str = 'credentials/.plaid_tokens.json') -> dict[str, str]:
    """Load Plaid access tokens from JSON file."""
    token_path = Path(path)
    if not token_path.exists():
        logger.error("Tokens file not found: %s", token_path)
        raise FileNotFoundError(f"Tokens file not found: {token_path}")
    with open(token_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def is_income(tx: dict) -> tuple[bool, float]:
    """Check if transaction is income. Returns (is_income, amount)."""
    amt = tx['amount']
    name = tx['name'].upper()
    if amt >= 0:
        return False, 0.0
    is_direct_deposit = any(k in name for k in ['DIRECT DEPOSIT', 'PAYROLL', 'SALARY', 'WAGE', 'ACH DEPOSIT'])
    return is_direct_deposit, abs(amt)


def is_transfer(tx: dict) -> tuple[bool, float]:
    """Check if transaction is a transfer between accounts."""
    amt = tx['amount']
    name = tx['name'].upper()
    is_transfer_in = any(k in name for k in ['TRANSFER', 'WIRE', 'EB TO', 'ZELLE', 'VENMO'])
    is_transfer_out = any(k in name for k in ['TRANSFER', 'WIRE TO', 'EB TO SAVINGS', 'EB TO CHECKING', 'ZELLE', 'VENMO'])
    if is_transfer_in and amt < 0:
        return True, abs(amt)
    if is_transfer_out and amt > 0:
        return True, amt
    return False, 0.0


def is_cc_payment(tx: dict) -> tuple[bool, float]:
    """Check if transaction is a credit card payment."""
    amt = tx['amount']
    name = tx['name'].upper()
    is_cc = any(k in name for k in ['PAYMENT TO CHASE', 'AMEX EPAYMENT', 'AMERICAN EXPRESS ACH', 'PAYMENT TO CARD'])
    return is_cc and amt > 0, amt if is_cc and amt > 0 else 0.0


def is_one_time_big(tx: dict) -> tuple[bool, dict]:
    """Check if transaction is a known one-time large purchase."""
    name = tx['name'].upper()
    if 'WIRE TRANSFER MILLEDGEVILLE' in name or ('WIRE' in name and 'MILLEDGEVILLE' in name):
        return True, {'name': tx['name'], 'amount': tx['amount'], 'date': str(tx['date'])}
    return False, {}


def fetch_transactions(token: str, start: datetime.date, end: datetime.date) -> list[dict]:
    """Fetch transactions from Plaid for a given token and date range."""
    try:
        resp = client.transactions_get(TransactionsGetRequest(
            access_token=token,
            start_date=start,
            end_date=end,
            options=TransactionsGetRequestOptions(count=500),
        ))
        return resp.get('transactions', [])
    except Exception as e:
        logger.warning("Failed to fetch transactions: %s", e)
        return []


def analyze_cashflow(days: int = 90) -> dict:
    """Analyze real cash flow over the last N days. Returns results dict."""
    end = datetime.now().date()
    start = end - timedelta(days=days)
    tokens = load_tokens()

    real_spending: defaultdict[str, float] = defaultdict(float)
    income_total = 0.0
    transfers_between_accounts = 0.0
    cc_payments = 0.0
    one_time_big_items = []

    for bank_name, token in tokens.items():
        logger.info("Fetching transactions for %s", bank_name)
        transactions = fetch_transactions(token, start, end)
        logger.info("  %d transactions fetched", len(transactions))

        for tx in transactions:
            try:
                amt = tx['amount']
                cat = tx.get('category', [])
                cat_label = cat[0] if cat else 'Uncategorized'

                # Income
                is_inc, inc_amt = is_income(tx)
                if is_inc:
                    income_total += inc_amt
                    continue

                # Transfers
                is_xfer, xfer_amt = is_transfer(tx)
                if is_xfer:
                    transfers_between_accounts += xfer_amt
                    continue

                # CC payments
                is_cc, cc_amt = is_cc_payment(tx)
                if is_cc:
                    cc_payments += cc_amt
                    continue

                # One-time big items
                is_big, big_item = is_one_time_big(tx)
                if is_big:
                    one_time_big_items.append(big_item)
                    continue

                # Real spending (positive amount going out)
                if amt > 0:
                    real_spending[cat_label] += amt

            except Exception as e:
                logger.warning("Error processing transaction: %s", e)
                continue

    return {
        'start': start,
        'end': end,
        'income_total': income_total,
        'transfers': transfers_between_accounts,
        'cc_payments': cc_payments,
        'one_time_items': one_time_big_items,
        'real_spending': dict(real_spending),
        'real_total': sum(real_spending.values()),
    }


def print_report(results: dict) -> None:
    """Print formatted cash flow report to stdout."""
    start = results['start']
    end = results['end']
    income_total = results['income_total']
    transfers = results['transfers']
    cc_payments = results['cc_payments']
    one_time_items = results['one_time_items']
    real_spending = results['real_spending']
    real_total = results['real_total']

    print("=" * 70)
    print("REAL CASH FLOW (90 Days)")
    print(f"Period: {start} to {end}")
    print("=" * 70)

    print(f"\n--- INCOME (Direct Deposits Only) ---")
    print(f"  Total Income:            ${income_total:>12,.2f}")

    print(f"\n--- INTERNAL MOVEMENTS (Not Spending) ---")
    print(f"  Transfers Between Accts: ${transfers:>12,.2f}")
    print(f"  Credit Card Payments:    ${cc_payments:>12,.2f}")

    if one_time_items:
        print(f"\n--- ONE-TIME ITEMS ---")
        for item in one_time_items:
            print(f"  {item['date']} {item['name'][:45]:45} ${item['amount']:>10,.2f}")

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


def main() -> None:
    """Main entry point."""
    results = analyze_cashflow(days=90)
    print_report(results)


if __name__ == "__main__":
    main()
