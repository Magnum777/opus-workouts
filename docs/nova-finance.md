# Nova Finance Dashboard

## Overview
Real-time financial dashboard connected to your bank accounts via Plaid. Generates spending analysis, net worth tracking, and personalized recommendations.

## Files
- `scripts/plaid_finance.py` - CLI: balances, transactions, accounts
- `scripts/plaid_link_server.py` - Local web server for bank auth via Plaid Link
- `scripts/nova_finance_dashboard.py` - Generates HTML dashboard
- `credentials/plaid.env` - API credentials (local only)
- `credentials/.plaid_tokens.json` - Bank access tokens (local only)
- `finance-dashboard/index.html` - Generated report (open in browser)

## Usage

### View Dashboard
```bash
# Regenerate and open
python scripts/nova_finance_dashboard.py
# Then open finance-dashboard/index.html in browser
```

### Quick CLI Commands
```bash
python scripts/plaid_finance.py balances
python scripts/plaid_finance.py transactions --days 30
python scripts/plaid_finance.py accounts
```

### Connect a New Bank
```bash
# Start the Link server
python scripts/plaid_link_server.py
# Open http://localhost:3000 in browser
# Follow Plaid Link flow, tokens auto-save
```

## Current Status
- **Sandbox mode** (test data)
- Chase test account connected with fake transactions
- Dashboard shows: net worth, spending by category, monthly trends, top transactions, recommendations

## Next Steps (for real data)
1. Request Development environment at https://dashboard.plaid.com
2. Switch `PLAID_ENV=development` in `credentials/plaid.env`
3. Re-run Link server and auth real Chase + AMEX accounts
4. Set up daily cron to regenerate dashboard

## Security
- Credentials stored locally in `credentials/` (not in git)
- Plaid access tokens are permanent until revoked
- All API calls are read-only (no transfers, no changes)
