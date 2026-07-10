#!/usr/bin/env python3
"""Quick Plaid API test - verify credentials and list sandbox institutions."""

import os
import sys
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
sandbox_secret = env.get("PLAID_SANDBOX_SECRET", "")

print(f"Client ID: {client_id[:8]}...")
print(f"Sandbox Secret: {sandbox_secret[:8]}...")

import plaid
from plaid.api import plaid_api
from plaid.model.institutions_get_request import InstitutionsGetRequest
from plaid.model.country_code import CountryCode

config = plaid.Configuration(
    host="https://sandbox.plaid.com",
    api_key={"clientId": client_id, "secret": sandbox_secret},
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))

try:
    req = InstitutionsGetRequest(count=3, offset=0, country_codes=[CountryCode("US")])
    resp = client.institutions_get(req)
    print(f"\nAPI OK! Found {len(resp['institutions'])} institutions:")
    for inst in resp["institutions"]:
        print(f"  - {inst['name']} ({inst['institution_id']})")
except Exception as e:
    print(f"\nAPI ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
