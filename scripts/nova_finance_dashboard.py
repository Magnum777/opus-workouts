#!/usr/bin/env python3
"""
Nova Finance Dashboard - comprehensive financial wellness report.
Usage: python scripts/nova_finance_dashboard.py
Output: finance-dashboard/index.html
"""

import os
import json
import sys
from datetime import datetime, timedelta, date
from pathlib import Path
from collections import defaultdict

CRED_DIR = Path(__file__).parent.parent / "credentials"
ENV_FILE = CRED_DIR / "plaid.env"
TOKENS_FILE = CRED_DIR / ".plaid_tokens.json"
OUT_DIR = Path(__file__).parent.parent / "finance-dashboard"

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


def get_plaid_client():
    import plaid
    from plaid.api import plaid_api
    env_vals = load_env()
    env_name = env_vals.get("PLAID_ENV", "sandbox").lower()
    host = HOSTS.get(env_name, HOSTS["sandbox"])
    if env_name == "production":
        secret = env_vals.get("PLAID_PROD_SECRET", env_vals.get("PLAID_SECRET", ""))
    elif env_name == "sandbox":
        secret = env_vals.get("PLAID_SANDBOX_SECRET", env_vals.get("PLAID_SECRET", ""))
    else:
        secret = env_vals.get("PLAID_SECRET", env_vals.get("PLAID_PROD_SECRET", env_vals.get("PLAID_SANDBOX_SECRET", "")))

    config = plaid.Configuration(
        host=host,
        api_key={"clientId": env_vals["PLAID_CLIENT_ID"], "secret": secret},
    )
    return plaid_api.PlaidApi(plaid.ApiClient(config))


def load_tokens():
    if not TOKENS_FILE.exists():
        return {}
    with open(TOKENS_FILE) as f:
        return json.load(f)


def fetch_data():
    from plaid.model.accounts_get_request import AccountsGetRequest
    from plaid.model.transactions_get_request import TransactionsGetRequest
    from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
    from plaid.model.liabilities_get_request import LiabilitiesGetRequest

    client = get_plaid_client()
    tokens = load_tokens()
    if not tokens:
        print("No linked accounts.")
        sys.exit(1)

    data = {"banks": [], "net_worth": 0, "transactions": [], "credit_cards": []}

    for bank_name, token in tokens.items():
        # Accounts
        acct_resp = client.accounts_get(AccountsGetRequest(access_token=token))
        bank_data = {"name": bank_name, "accounts": []}
        for acct in acct_resp["accounts"]:
            bal = acct["balances"]
            current = bal.get("current") or 0
            acct_type = str(acct["type"])
            acct_data = {
                "name": acct["name"],
                "type": acct_type,
                "subtype": str(acct.get("subtype", "")),
                "mask": acct.get("mask", "****"),
                "current": current,
                "available": bal.get("available"),
            }
            bank_data["accounts"].append(acct_data)
            # Net worth calculation
            if acct_type in ("depository", "investment"):
                data["net_worth"] += current
            elif acct_type == "credit":
                data["net_worth"] -= current
            elif acct_type == "loan":
                data["net_worth"] -= current

        # Liabilities (credit cards)
        try:
            liab_resp = client.liabilities_get(LiabilitiesGetRequest(access_token=token))
            if liab_resp.get("liabilities"):
                for cc in liab_resp["liabilities"].get("credit", []):
                    data["credit_cards"].append({
                        "bank": bank_name,
                        "name": cc.get("name", "Unknown"),
                        "last_payment": cc.get("last_payment_amount") or 0,
                        "min_payment": cc.get("minimum_payment_amount") or 0,
                        "next_due": str(cc.get("next_payment_due_date", "N/A")),
                    })
        except:
            pass

        # Transactions (last 90 days)
        end = datetime.now().date()
        start = end - timedelta(days=90)
        tx_resp = client.transactions_get(TransactionsGetRequest(
            access_token=token,
            start_date=start,
            end_date=end,
            options=TransactionsGetRequestOptions(count=500),
        ))
        for tx in tx_resp["transactions"]:
            data["transactions"].append({
                "date": tx["date"],
                "name": tx["name"],
                "amount": tx["amount"],
                "category": tx.get("category", []),
                "bank": bank_name,
            })

        data["banks"].append(bank_data)

    return data


def analyze(data):
    analysis = {
        "net_worth": data["net_worth"],
        "total_assets": 0,
        "total_liabilities": 0,
        "liquid_assets": 0,
        "investments": 0,
        "credit_limit_total": 0,
        "credit_used_total": 0,
        "monthly_spend": defaultdict(float),
        "category_spend": defaultdict(float),
        "largest_transactions": [],
        "recommendations": [],
        "upcoming_payments": [],
        "account_breakdown": [],
    }

    # Asset/liability/credit breakdown
    for bank in data["banks"]:
        for acct in bank["accounts"]:
            t = acct["type"]
            cur = acct["current"]
            avail = acct.get("available") or 0
            
            if t in ("depository", "investment"):
                analysis["total_assets"] += cur
                if t == "depository":
                    analysis["liquid_assets"] += cur
                else:
                    analysis["investments"] += cur
            elif t == "credit":
                analysis["total_liabilities"] += abs(cur)
                # Calculate credit limit from available
                limit = cur + avail if avail else cur
                analysis["credit_limit_total"] += limit
                analysis["credit_used_total"] += cur
            elif t == "loan":
                analysis["total_liabilities"] += abs(cur)

    # Spending analysis
    for tx in data["transactions"]:
        if tx["amount"] > 0:
            tx_date = tx["date"]
            if hasattr(tx_date, 'isoformat'):
                month = tx_date.isoformat()[:7]
            else:
                month = str(tx_date)[:7]
            analysis["monthly_spend"][month] += tx["amount"]
            cat = tx["category"][0] if tx["category"] else "Uncategorized"
            analysis["category_spend"][cat] += tx["amount"]

    sorted_tx = sorted([t for t in data["transactions"] if t["amount"] > 0], key=lambda x: x["amount"], reverse=True)[:10]
    analysis["largest_transactions"] = sorted_tx

    # Credit utilization
    if analysis["credit_limit_total"] > 0:
        analysis["credit_utilization"] = (analysis["credit_used_total"] / analysis["credit_limit_total"]) * 100
    else:
        analysis["credit_utilization"] = 0

    # Upcoming payments
    today = date.today()
    for cc in data["credit_cards"]:
        if cc.get("next_due") and cc["next_due"] != "None":
            try:
                due = datetime.strptime(cc["next_due"], "%Y-%m-%d").date()
                days_until = (due - today).days
                analysis["upcoming_payments"].append({
                    "card": cc["name"],
                    "min_payment": cc["min_payment"],
                    "due_date": cc["next_due"],
                    "days_until": days_until,
                    "urgent": days_until <= 3,
                })
            except:
                pass

    # Sort upcoming by urgency
    analysis["upcoming_payments"].sort(key=lambda x: x["days_until"])

    # Recommendations
    recs = []
    if analysis["credit_utilization"] > 30:
        recs.append(f"Credit utilization is {analysis['credit_utilization']:.1f}%. Pay down to under 30% to improve credit score.")
    
    if analysis["monthly_spend"]:
        avg_monthly = sum(analysis["monthly_spend"].values()) / len(analysis["monthly_spend"])
        if avg_monthly > analysis["liquid_assets"] * 0.5:
            recs.append("Monthly spend exceeds 50% of liquid assets. Build emergency fund to 3-6 months expenses.")
        elif avg_monthly > analysis["liquid_assets"] * 0.2:
            recs.append("Monthly spend is high relative to liquid assets. Consider increasing savings rate.")
    
    if analysis["liquid_assets"] < 1000:
        recs.append("Liquid assets below $1,000. Prioritize building emergency fund before investing.")
    
    for payment in analysis["upcoming_payments"]:
        if payment["days_until"] <= 1:
            recs.append(f"URGENT: {payment['card']} minimum payment of ${payment['min_payment']:,.2f} due in {payment['days_until']} days!")
        elif payment["days_until"] <= 7:
            recs.append(f"{payment['card']} minimum payment of ${payment['min_payment']:,.2f} due in {payment['days_until']} days.")
    
    if analysis["category_spend"].get("Food and Drink", 0) > sum(analysis["category_spend"].values()) * 0.25:
        recs.append("Dining out is >25% of spending. Meal prepping could save $200-400/month.")
    
    if analysis["investments"] == 0 and analysis["liquid_assets"] > 5000:
        recs.append("You have liquid assets but no tracked investments. Consider opening IRA/brokerage account.")
    
    if not recs:
        recs.append("Financial health looks solid. Continue tracking and consider increasing retirement contributions.")
    
    analysis["recommendations"] = recs
    return analysis


def generate_html(data, analysis):
    nw_color = "green" if analysis["net_worth"] >= 0 else "red"
    nw_formatted = f"{analysis['net_worth']:,.2f}"
    assets_formatted = f"{analysis['total_assets']:,.2f}"
    liabilities_formatted = f"{analysis['total_liabilities']:,.2f}"
    liquid_formatted = f"{analysis['liquid_assets']:,.2f}"
    invest_formatted = f"{analysis['investments']:,.2f}"
    util_formatted = f"{analysis['credit_utilization']:.1f}"
    total_accounts = sum(len(b["accounts"]) for b in data["banks"])
    total_banks = len(data["banks"])
    total_tx = len(data["transactions"])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build bank cards
    banks_html = ""
    for bank in data["banks"]:
        accounts_html = ""
        for a in bank["accounts"]:
            t = a["type"]
            color = "#00ff88" if t in ("depository", "investment") else "#ff4444" if t == "credit" else "#ffaa00"
            accounts_html += '<div class="account"><b style="color:%s">%s</b> (****%s) | %s<br>$%s</div>' % (
                color, a["name"], a["mask"], t, f"{a['current']:,.2f}"
            )
        banks_html += '<div class="bank"><h3>%s</h3>%s</div>' % (bank["name"], accounts_html)

    # Upcoming payments
    payments_html = ""
    for p in analysis["upcoming_payments"]:
        urgent_class = "urgent" if p["urgent"] else ""
        payments_html += '<tr class="%s"><td>%s</td><td>$%s</td><td>%s</td><td>%d days</td></tr>' % (
            urgent_class, p["card"], f"{p['min_payment']:,.2f}", p["due_date"], p["days_until"]
        )
    if not payments_html:
        payments_html = '<tr><td colspan="4" style="color:#8b949e">No upcoming payments detected</td></tr>'

    # Category chart
    cats = sorted(analysis["category_spend"].items(), key=lambda x: x[1], reverse=True)[:8]
    cat_labels = json.dumps([c[0] for c in cats])
    cat_values = json.dumps([c[1] for c in cats])

    # Monthly spend
    months = sorted(analysis["monthly_spend"].keys())
    month_labels = json.dumps(months)
    month_values = json.dumps([analysis["monthly_spend"][m] for m in months])

    # Transaction rows
    tx_rows = ""
    for t in analysis["largest_transactions"]:
        date_str = t["date"].isoformat() if hasattr(t["date"], "isoformat") else str(t["date"])
        tx_rows += '<tr><td>%s</td><td>%s</td><td>$%s</td><td>%s</td></tr>' % (
            date_str, t["name"], f"{t['amount']:,.2f}", t["bank"]
        )

    # Recommendations
    recs_html = ""
    for r in analysis["recommendations"]:
        urgent = "urgent" if "URGENT" in r else ""
        recs_html += '<li class="%s">%s</li>' % (urgent, r)

    return '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Nova Finance Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root { --bg: #0d1117; --card: #161b22; --border: #30363d; --text: #c9d1d9; --accent: #00d4ff; --green: #00ff88; --red: #ff4444; --yellow: #ffaa00; }
body { font-family: -apple-system, system-ui, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h1 { color: var(--accent); margin: 0; }
.timestamp { color: #8b949e; font-size: 14px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 24px; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
.card h2 { margin-top: 0; font-size: 18px; color: var(--accent); }
.big-number { font-size: 36px; font-weight: bold; margin: 8px 0; }
.net-worth { color: var(''' + nw_color + '''); }
.metric-label { color: #8b949e; font-size: 14px; margin-top: 4px; }
.account { padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 14px; }
.account:last-child { border-bottom: none; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { padding: 10px; text-align: left; border-bottom: 1px solid var(--border); }
th { color: #8b949e; font-weight: 500; }
.recommendations { background: #1a2332; border-left: 4px solid var(--yellow); }
.recommendations li { margin: 8px 0; }
.recommendations li.urgent { color: var(--red); font-weight: bold; }
.urgent { color: var(--red); font-weight: bold; }
.score { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; }
.score-good { background: rgba(0,255,136,0.2); color: var(--green); }
.score-warn { background: rgba(255,170,0,0.2); color: var(--yellow); }
.score-bad { background: rgba(255,68,68,0.2); color: var(--red); }
</style>
</head>
<body>
<div class="header">
  <h1>Nova Finance Dashboard</h1>
  <span class="timestamp">Generated: ''' + timestamp + '''</span>
</div>

<div class="grid">
  <div class="card">
    <h2>Net Worth</h2>
    <div class="big-number net-worth">$''' + nw_formatted + '''</div>
    <div class="metric-label">Assets: $''' + assets_formatted + ''' | Liabilities: $''' + liabilities_formatted + '''</div>
  </div>
  <div class="card">
    <h2>Liquid Assets</h2>
    <div class="big-number" style="color: var(--green)">$''' + liquid_formatted + '''</div>
    <div class="metric-label">Checking + Savings</div>
  </div>
  <div class="card">
    <h2>Investments</h2>
    <div class="big-number" style="color: var(--accent)">$''' + invest_formatted + '''</div>
    <div class="metric-label">Tracked retirement/brokerage</div>
  </div>
  <div class="card">
    <h2>Credit Utilization</h2>
    <div class="big-number" style="color: var(''' + ("green" if analysis["credit_utilization"] < 30 else "yellow" if analysis["credit_utilization"] < 50 else "red") + ''')">''' + util_formatted + '''%</div>
    <div class="metric-label">$''' + f"{analysis['credit_used_total']:,.2f}" + ''' used / $''' + f"{analysis['credit_limit_total']:,.2f}" + ''' limit</div>
  </div>
  <div class="card">
    <h2>Total Accounts</h2>
    <div class="big-number">''' + str(total_accounts) + '''</div>
    <div class="metric-label">''' + str(total_banks) + ''' connected banks</div>
  </div>
  <div class="card">
    <h2>90-Day Transactions</h2>
    <div class="big-number">''' + str(total_tx) + '''</div>
    <div class="metric-label">Analyzed</div>
  </div>
</div>

<div class="grid">
  <div class="card" style="grid-column: span 2;">
    <h2>Monthly Spending Trend</h2>
    <canvas id="monthChart" height="120"></canvas>
  </div>
  <div class="card">
    <h2>By Category</h2>
    <canvas id="catChart"></canvas>
  </div>
</div>

<div class="grid">
  <div class="card" style="grid-column: span 2;">
    <h2>Upcoming Payments</h2>
    <table>
      <tr><th>Card</th><th>Min Payment</th><th>Due Date</th><th>Days Left</th></tr>
      ''' + payments_html + '''
    </table>
  </div>
</div>

<div class="grid">
  <div class="card" style="grid-column: span 2;">
    <h2>Account Details</h2>
    ''' + banks_html + '''
  </div>
</div>

<div class="grid">
  <div class="card recommendations" style="grid-column: span 2;">
    <h2>Recommendations & Alerts</h2>
    <ul>''' + recs_html + '''</ul>
  </div>
</div>

<div class="grid">
  <div class="card" style="grid-column: span 2;">
    <h2>Top Transactions (90 Days)</h2>
    <table>
      <tr><th>Date</th><th>Merchant</th><th>Amount</th><th>Bank</th></tr>
      ''' + tx_rows + '''
    </table>
  </div>
</div>

<script>
const monthCtx = document.getElementById('monthChart').getContext('2d');
new Chart(monthCtx, {
  type: 'line',
  data: {
    labels: ''' + month_labels + ''',
    datasets: [{
      label: 'Spending ($)',
      data: ''' + month_values + ''',
      borderColor: '#00d4ff',
      backgroundColor: 'rgba(0,212,255,0.1)',
      fill: true,
      tension: 0.3
    }]
  },
  options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
});

const catCtx = document.getElementById('catChart').getContext('2d');
new Chart(catCtx, {
  type: 'doughnut',
  data: {
    labels: ''' + cat_labels + ''',
    datasets: [{
      data: ''' + cat_values + ''',
      backgroundColor: ['#00d4ff', '#00ff88', '#ffaa00', '#ff4444', '#a855f7', '#ec4899', '#14b8a6', '#f97316']
    }]
  },
  options: { responsive: true, plugins: { legend: { position: 'right' } } }
});
</script>
</body>
</html>'''


def main():
    print("Fetching data from Plaid...")
    data = fetch_data()
    print(f"Got {len(data['transactions'])} transactions across {len(data['banks'])} banks")
    print(f"Credit cards tracked: {len(data['credit_cards'])}")

    print("Analyzing...")
    analysis = analyze(data)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUT_DIR / "index.html"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(generate_html(data, analysis))

    print(f"\nDashboard saved to: {out_file}")
    print(f"Net Worth: ${analysis['net_worth']:,.2f}")
    print(f"Liquid Assets: ${analysis['liquid_assets']:,.2f}")
    print(f"Credit Utilization: {analysis['credit_utilization']:.1f}%")
    print(f"Recommendations ({len(analysis['recommendations'])}):")
    for r in analysis["recommendations"]:
        print(f"  - {r}")


if __name__ == "__main__":
    main()
