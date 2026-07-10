import re
import json
from datetime import datetime, timedelta
from pathlib import Path

# Load Plaid credentials
CRED_DIR = Path(__file__).parent.parent / "credentials"
ENV_FILE = CRED_DIR / "plaid.env"
TOKENS_FILE = CRED_DIR / ".plaid_tokens.json"

HOSTS = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com",
}

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

# Pull ALL transactions (paginated)
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions

client = get_plaid_client()
tokens = load_tokens()

all_txs = {}

for name, token in tokens.items():
    try:
        all_transactions = []
        offset = 0
        total = None
        
        while total is None or offset < total:
            req = TransactionsGetRequest(
                access_token=token,
                start_date=(datetime.now().date() - timedelta(days=180)),
                end_date=datetime.now().date(),
                options=TransactionsGetRequestOptions(count=500, offset=offset),
            )
            resp = client.transactions_get(req)
            
            if total is None:
                total = resp['total_transactions']
                print(f"=== {name.upper()} - {total} tx ===")
            
            all_transactions.extend(resp['transactions'])
            offset += len(resp['transactions'])
            
            if len(resp['transactions']) == 0:
                break
        
        all_txs[name] = all_transactions
        print(f"Fetched {len(all_transactions)} transactions")
        
    except Exception as e:
        print(f"ERROR for {name}: {e}")

# Save full dump for analysis
with open('C:/Users/compj/.openclaw/workspace/finance/full_tx_dump.json', 'w') as f:
    serializable = {}
    for name, txs in all_txs.items():
        serializable[name] = []
        for tx in txs:
            serializable[name].append({
                'date': str(tx['date']),
                'amount': float(tx['amount']),
                'name': tx['name'],
                'category': tx.get('category', []),
                'merchant_name': tx.get('merchant_name', ''),
            })
    json.dump(serializable, f, indent=2)

print(f"\nSaved {sum(len(txs) for txs in all_txs.values())} transactions to full_tx_dump.json")
