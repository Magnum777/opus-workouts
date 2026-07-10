#!/usr/bin/env python3
"""
Extract recurring monthly expenses from transaction history.

Looks for same merchants, similar amounts, monthly patterns across
6 months of Plaid transaction history.
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


def clean_merchant_name(name: str) -> str:
    """Clean merchant name by removing common suffixes/prefixes."""
    name = name.upper()
    for suffix in [' ACH DEBIT', ' ACH PMT', ' AUTOMATIC PAYMENT', ' RECURRING', ' SUBSCRIPTION']:
        name = name.replace(suffix, '')
    return name


def find_recurring_expenses(all_tx: list[dict]) -> list[dict]:
    """Find recurring expenses from transaction list."""
    by_merchant: defaultdict[str, list[dict]] = defaultdict(list)
    for tx in all_tx:
        if tx['amount'] <= 0:
            continue  # Skip inflows
        name = clean_merchant_name(tx['name'])
        by_merchant[name].append(tx)

    recurring = []
    for merchant, txs in by_merchant.items():
        if len(txs) < 2:
            continue
        amounts = [t['amount'] for t in txs]
        avg = sum(amounts) / len(amounts)
        variance = max(amounts) - min(amounts)

        # Check if amounts are similar (within 10% or $5)
        if variance > max(avg * 0.1, 5):
            continue

        # Check monthly pattern
        dates = sorted([datetime.strptime(t['date'], '%Y-%m-%d') for t in txs])
        if len(dates) < 2:
            continue
        gaps = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        avg_gap = sum(gaps) / len(gaps)

        if 20 <= avg_gap <= 40:
            frequency = 'Monthly'
        elif 5 <= avg_gap <= 9:
            frequency = 'Weekly'
        else:
            continue  # Skip irregular patterns

        recurring.append({
            'merchant': merchant[:50],
            'avg_amount': avg,
            'frequency': frequency,
            'count': len(txs),
            'last_date': dates[-1].strftime('%Y-%m-%d'),
            'bank': txs[0]['bank'][:10],
            'category': txs[0]['category'],
        })

    return recurring


def analyze_expenses(days: int = 180) -> dict:
    """Analyze recurring expenses over the last N days. Returns results dict."""
    end = datetime.now().date()
    start = end - timedelta(days=days)
    tokens = load_tokens()

    all_tx = []
    for bank_name, token in tokens.items():
        logger.info("Fetching transactions for %s", bank_name)
        transactions = fetch_transactions(token, start, end)
        logger.info("  %d transactions fetched", len(transactions))

        for tx in transactions:
            try:
                if tx['amount'] > 0:  # Outflows only
                    all_tx.append({
                        'date': str(tx['date']),
                        'name': tx['name'],
                        'amount': tx['amount'],
                        'category': tx.get('category', ['Uncategorized'])[0] if tx.get('category') else 'Uncategorized',
                        'bank': bank_name,
                    })
            except Exception as e:
                logger.warning("Error processing transaction: %s", e)
                continue

    # Find recurring
    recurring = find_recurring_expenses(all_tx)

    # Big one-off expenses
    big_expenses = [tx for tx in all_tx if tx['amount'] >= 500]

    # Housing/mortgage specifically
    housing = [t for t in all_tx if any(k in t['name'].upper() for k in ['MORTGAGE', 'RENT', 'TRUIST', 'MILLEDGEVILLE', 'WIRE'])]

    return {
        'total_tx': len(all_tx),
        'recurring': recurring,
        'big_expenses': big_expenses,
        'housing': housing,
        'total_monthly': sum(r['avg_amount'] for r in recurring if r['frequency'] == 'Monthly') +
                         sum(r['avg_amount'] * 4.3 for r in recurring if r['frequency'] == 'Weekly'),
    }


def print_report(results: dict) -> None:
    """Print formatted expense report to stdout."""
    total_tx = results['total_tx']
    recurring = results['recurring']
    big_expenses = results['big_expenses']
    housing = results['housing']
    total_monthly = results['total_monthly']

    print("=" * 80)
    print("MONTHLY EXPENSES EXTRACTED FROM 6-MONTH HISTORY")
    print("=" * 80)

    print("\n--- RECURRING MONTHLY EXPENSES ---")
    print(f"{'Merchant':40} {'Avg':>10} {'Freq':10} {'Count':6} {'Last':12} {'Category':20}")
    print("-" * 80)

    for r in sorted(recurring, key=lambda x: x['avg_amount'], reverse=True):
        print(f"{r['merchant']:40} ${r['avg_amount']:>9,.2f} {r['frequency']:10} {r['count']:>5}x   {r['last_date']:12} {r['category']:20}")

    print(f"\nEstimated monthly recurring: ${total_monthly:,.2f}")

    print("\n--- HOUSING / BIG FIXED COSTS ---")
    for h in housing[-10:]:
        print(f"  {h['date']} {h['name'][:50]:50} ${h['amount']:>10,.2f}")

    print("\n--- BIG ONE-OFF EXPENSES (>$500 in 6 months) ---")
    for b in sorted(big_expenses, key=lambda x: x['amount'], reverse=True)[:15]:
        print(f"  {b['date']} {b['name'][:50]:50} ${b['amount']:>10,.2f}")

    # Calculate true monthly burn rate
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total transactions analyzed: {total_tx}")
    print(f"Recurring monthly expenses: ${total_monthly:,.2f}")
    print(f"Estimated true monthly spend: ${total_monthly:,.2f} (recurring) + variable")


def main() -> None:
    """Main entry point."""
    results = analyze_expenses(days=180)
    print_report(results)


if __name__ == "__main__":
    main()
