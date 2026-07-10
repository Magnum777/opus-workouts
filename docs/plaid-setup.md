# Plaid Finance Setup

## 1. Get Plaid Credentials

- Go to https://dashboard.plaid.com
- Sign up (free, personal use)
- Switch to **Development** environment (top-left dropdown)
- Copy:
  - **Client ID**
  - **Secret** (Development, NOT Sandbox)

## 2. Save Credentials

Create `credentials/plaid.env`:

```
PLAID_CLIENT_ID=xxx
PLAID_SECRET=xxx
PLAID_ENV=development
```

## 3. Link Your Banks

Plaid requires OAuth (Chase) and a Link flow. Two options:

**Option A: Plaid Quickstart (recommended)**
- Clone https://github.com/plaid/plaid-python-quickstart
- Run it locally, go through Link UI
- It prints an `access_token` — save it via:
  ```bash
  python scripts/plaid_finance.py add-token --name chase --token us_access_xxx
  ```

**Option B: Manual (I can build a mini Link page)**
- I create a tiny local HTML page with Plaid Link
- You open it in browser, auth Chase + AMEX
- Tokens get saved automatically

## 4. Daily Usage

```bash
python scripts/plaid_finance.py balances
python scripts/plaid_finance.py transactions --days 30
python scripts/plaid_finance.py accounts
```

## Notes

- Development env supports up to 100 live accounts, no cost
- Access tokens are permanent unless you revoke them
- Tokens stored in `credentials/.plaid_tokens.json`
