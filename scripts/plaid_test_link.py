#!/usr/bin/env python3
"""Test Plaid Link token creation directly — no server needed."""

import json
from pathlib import Path

CRED_DIR = Path(__file__).parent.parent / "credentials"
ENV_FILE = CRED_DIR / "plaid.env"


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
env_name = env.get("PLAID_ENV", "sandbox").lower()

if env_name == "production":
    secret = env.get("PLAID_PROD_SECRET", env.get("PLAID_SECRET", ""))
    host = "https://production.plaid.com"
elif env_name == "sandbox":
    secret = env.get("PLAID_SANDBOX_SECRET", env.get("PLAID_SECRET", ""))
    host = "https://sandbox.plaid.com"
else:
    secret = env.get("PLAID_SECRET", env.get("PLAID_PROD_SECRET", env.get("PLAID_SANDBOX_SECRET", "")))
    host = "https://development.plaid.com"

print(f"Env: {env_name}")
print(f"Host: {host}")
print(f"Client ID: {client_id[:8]}...")
print(f"Secret: {secret[:8]}...")

import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

config = plaid.Configuration(
    host=host,
    api_key={"clientId": client_id, "secret": secret},
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))

try:
    req = LinkTokenCreateRequest(
        products=[Products("auth"), Products("transactions")],
        client_name="Nova Finance",
        country_codes=[CountryCode("US")],
        language="en",
        user=LinkTokenCreateRequestUser(client_user_id="opus-nova-001"),
    )
    resp = client.link_token_create(req)
    print(f"\nSUCCESS! Link token: {resp['link_token'][:40]}...")
    print("Paste this into the Plaid Link sandbox tester to simulate bank connection.")
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
