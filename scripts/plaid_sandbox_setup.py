#!/usr/bin/env python3
"""
Plaid Sandbox Setup - create a test bank connection for development.
Uses Plaid's sandbox institutions (fake data, no real banks).
"""

import json
from pathlib import Path

CRED_DIR = Path(__file__).parent.parent / "credentials"
ENV_FILE = CRED_DIR / "plaid.env"
TOKENS_FILE = CRED_DIR / ".plaid_tokens.json"


def load_env():
    vals = {}
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            vals[k] = v.strip()
    return vals


env = load_env()
client_id = env.get("PLAID_CLIENT_ID", "")
sandbox_secret = env.get("PLAID_SANDBOX_SECRET", env.get("PLAID_SECRET", ""))

import plaid
from plaid.api import plaid_api
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products

config = plaid.Configuration(
    host="https://sandbox.plaid.com",
    api_key={"clientId": client_id, "secret": sandbox_secret},
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))

# Create a sandbox public token for a test institution (Chase-like)
print("Creating sandbox test account...")
request = SandboxPublicTokenCreateRequest(
    institution_id="ins_109508",  # Chase sandbox institution
    initial_products=[Products("auth"), Products("transactions")],
)
response = client.sandbox_public_token_create(request)
public_token = response["public_token"]
print(f"Public token: {public_token[:40]}...")

# Exchange for access token
exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
exchange_response = client.item_public_token_exchange(exchange_request)
access_token = exchange_response["access_token"]
item_id = exchange_response["item_id"]
print(f"Access token: {access_token[:40]}...")
print(f"Item ID: {item_id}")

# Save it
TOKENS_FILE.parent.mkdir(parents=True, exist_ok=True)
tokens = {}
if TOKENS_FILE.exists():
    with open(TOKENS_FILE) as f:
        tokens = json.load(f)

tokens["chase-sandbox"] = access_token
with open(TOKENS_FILE, "w") as f:
    json.dump(tokens, f, indent=2)

print(f"\nSaved to {TOKENS_FILE}")

# Test: get balances
from plaid.model.accounts_get_request import AccountsGetRequest

req = AccountsGetRequest(access_token=access_token)
resp = client.accounts_get(req)
print(f"\n=== Sandbox Chase Accounts ===")
for acct in resp["accounts"]:
    bal = acct["balances"]
    print(f"  {acct['name']} ({acct['subtype']})")
    print(f"    Current: ${bal['current']:,.2f}")
    if bal.get("available") is not None:
        print(f"    Available: ${bal['available']:,.2f}")
