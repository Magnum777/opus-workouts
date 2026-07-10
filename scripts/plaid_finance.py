#!/usr/bin/env python3
"""
Plaid Finance Bridge - balances, transactions, accounts
Usage:
  python scripts/plaid_finance.py balances
  python scripts/plaid_finance.py transactions --days 30
  python scripts/plaid_finance.py accounts
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# --- Config ---
CRED_DIR = Path(__file__).parent.parent / "credentials"
ENV_FILE = CRED_DIR / "plaid.env"
TOKENS_FILE = CRED_DIR / ".plaid_tokens.json"

HOSTS = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com",
}


def load_env():
    if not ENV_FILE.exists():
        print(f"Missing {ENV_FILE}")
        print("Create it with:")
        print("  PLAID_CLIENT_ID=xxx")
        print("  PLAID_SECRET=xxx")
        print("  PLAID_ENV=sandbox|development|production")
        sys.exit(1)

    vals = {}
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            vals[k] = v.strip()
    return vals


def get_secret(env_vals, env_name):
    if env_name == "production":
        return env_vals.get("PLAID_PROD_SECRET", env_vals.get("PLAID_SECRET", ""))
    elif env_name == "sandbox":
        return env_vals.get("PLAID_SANDBOX_SECRET", env_vals.get("PLAID_SECRET", ""))
    return env_vals.get("PLAID_SECRET", env_vals.get("PLAID_PROD_SECRET", env_vals.get("PLAID_SANDBOX_SECRET", "")))


def get_plaid_client():
    import plaid
    from plaid.api import plaid_api

    env_vals = load_env()
    env_name = env_vals.get("PLAID_ENV", "development").lower()
    host = HOSTS.get(env_name, HOSTS["development"])
    secret = get_secret(env_vals, env_name)

    configuration = plaid.Configuration(
        host=host,
        api_key={
            "clientId": env_vals["PLAID_CLIENT_ID"],
            "secret": secret,
        },
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def load_tokens():
    if not TOKENS_FILE.exists():
        return {}
    with open(TOKENS_FILE) as f:
        return json.load(f)


def save_tokens(tokens):
    CRED_DIR.mkdir(parents=True, exist_ok=True)
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)


def cmd_balances(args):
    from plaid.model.accounts_get_request import AccountsGetRequest
    client = get_plaid_client()
    tokens = load_tokens()
    if not tokens:
        print("No linked accounts. Run the link flow first.")
        return

    for name, token in tokens.items():
        try:
            req = AccountsGetRequest(access_token=token)
            resp = client.accounts_get(req)
            print(f"\n=== {name.upper()} ===")
            for acct in resp["accounts"]:
                bal = acct["balances"]
                print(f"  {acct['name']} ({acct['subtype']})")
                if bal.get("current") is not None:
                    print(f"    Current: ${bal['current']:,.2f}")
                if bal.get("available") is not None:
                    print(f"    Available: ${bal['available']:,.2f}")
        except Exception as e:
            print(f"  ERROR for {name}: {e}")


def cmd_transactions(args):
    from plaid.model.transactions_get_request import TransactionsGetRequest
    from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
    client = get_plaid_client()
    tokens = load_tokens()
    if not tokens:
        print("No linked accounts. Run the link flow first.")
        return

    end = datetime.now().date()
    start = end - timedelta(days=args.days)

    for name, token in tokens.items():
        try:
            req = TransactionsGetRequest(
                access_token=token,
                start_date=start,
                end_date=end,
                options=TransactionsGetRequestOptions(count=100),
            )
            resp = client.transactions_get(req)
            print(f"\n=== {name.upper()} - {resp['total_transactions']} tx ===")
            for tx in resp["transactions"]:
                amt = tx["amount"]
                sign = "-" if amt > 0 else "+"
                print(f"  {tx['date']} {sign}${abs(amt):,.2f} - {tx['name']}")
        except Exception as e:
            print(f"  ERROR for {name}: {e}")


def cmd_accounts(args):
    from plaid.model.accounts_get_request import AccountsGetRequest
    client = get_plaid_client()
    tokens = load_tokens()
    if not tokens:
        print("No linked accounts.")
        return
    for name, token in tokens.items():
        try:
            req = AccountsGetRequest(access_token=token)
            resp = client.accounts_get(req)
            print(f"\n=== {name.upper()} ===")
            for acct in resp["accounts"]:
                print(f"  {acct['name']} | {acct.get('official_name', 'N/A')} | {acct.get('mask', '****')}")
        except Exception as e:
            print(f"  ERROR for {name}: {e}")


def cmd_init():
    print("""Plaid Setup:

1. Go to https://dashboard.plaid.com and sign up.
2. Switch to Development environment.
3. Copy Client ID + Secret.
4. Create credentials/plaid.env:

PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret
PLAID_ENV=development

5. To link accounts, run:
   python scripts/plaid_link_server.py
   Then open http://localhost:3000 in your browser.
""")


def cmd_add_token(args):
    tokens = load_tokens()
    tokens[args.name] = args.token
    save_tokens(tokens)
    print(f"Saved token for '{args.name}'")


def cmd_refresh(args):
    from plaid.model.accounts_get_request import AccountsGetRequest
    from plaid.model.transactions_refresh_request import TransactionsRefreshRequest
    client = get_plaid_client()
    tokens = load_tokens()
    if not tokens:
        print("No linked accounts. Run the link flow first.")
        return

    for name, token in tokens.items():
        try:
            req = TransactionsRefreshRequest(access_token=token)
            resp = client.transactions_refresh(req)
            print(f"  {name}: refresh triggered (status: {resp.get('status', 'unknown')})")
        except Exception as e:
            print(f"  ERROR refreshing {name}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Plaid Finance Bridge")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Show setup instructions")
    sub.add_parser("balances", help="Show balances")
    sub.add_parser("accounts", help="Show account details")

    tx = sub.add_parser("transactions", help="Show recent transactions")
    tx.add_argument("--days", type=int, default=30)

    sub.add_parser("refresh", help="Force refresh account data from bank")

    add = sub.add_parser("add-token", help="Store an access token")
    add.add_argument("--name", required=True)
    add.add_argument("--token", required=True)

    args = parser.parse_args()

    if args.cmd == "init":
        cmd_init()
        return

    if args.cmd == "balances":
        cmd_balances(args)
    elif args.cmd == "transactions":
        cmd_transactions(args)
    elif args.cmd == "accounts":
        cmd_accounts(args)
    elif args.cmd == "refresh":
        cmd_refresh(args)
    elif args.cmd == "add-token":
        cmd_add_token(args)


if __name__ == "__main__":
    main()
