#!/usr/bin/env python3
"""
Plaid Link Local Server - serve the Link UI and exchange public_token for access_token.
Run: python scripts/plaid_link_server.py
Then open http://localhost:3000 in your browser.
"""

import os
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

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


env = load_env()
CLIENT_ID = env.get("PLAID_CLIENT_ID", "")
LINK_ENV = env.get("PLAID_ENV", "sandbox").lower()

# Pick correct secret
if LINK_ENV == "production":
    SECRET = env.get("PLAID_PROD_SECRET", env.get("PLAID_SECRET", ""))
elif LINK_ENV == "sandbox":
    SECRET = env.get("PLAID_SANDBOX_SECRET", env.get("PLAID_SECRET", ""))
else:
    SECRET = env.get("PLAID_SECRET", env.get("PLAID_PROD_SECRET", env.get("PLAID_SANDBOX_SECRET", "")))

API_HOST = HOSTS.get(LINK_ENV, HOSTS["sandbox"])

HTML_PAGE = f"""<!DOCTYPE html>
<html>
<head>
<title>Plaid Link - Nova Finance</title>
<script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background: #0a0a0a; color: #e0e0e0; }}
h1 {{ color: #00d4ff; }}
button {{ padding: 14px 28px; font-size: 16px; background: #00d4ff; color: #000; border: none; border-radius: 6px; cursor: pointer; }}
button:hover {{ background: #00b8e0; }}
#status {{ margin-top: 20px; padding: 12px; background: #1a1a1a; border-radius: 6px; min-height: 60px; }}
.token {{ font-family: monospace; font-size: 12px; color: #00ff88; word-break: break-all; }}
</style>
</head>
<body>
<h1>Link Your Banks</h1>
<p>Click below to connect Chase and American Express via Plaid.</p>
<p><small>Mode: {LINK_ENV}</small></p>
<button id="linkBtn">Connect Bank Account</button>
<div id="status">Waiting...</div>
<script>
async function initLink() {{
  const resp = await fetch('/create_link_token', {{method: 'POST'}});
  const data = await resp.json();
  if (!data.link_token) {{
    document.getElementById('status').innerText = 'Error: ' + JSON.stringify(data);
    return;
  }}
  console.log('Link token:', data.link_token);
  const handler = Plaid.create({{
    token: data.link_token,
    onSuccess: async (public_token, metadata) => {{
      console.log('onSuccess metadata:', JSON.stringify(metadata, null, 2));
      const accounts = metadata.accounts || [];
      const accountList = accounts.map(a => a.name || a.mask || 'unknown').join(', ');
      document.getElementById('status').innerHTML =
        '<b>Public token received.</b><br>Exchanging...<br>Accounts selected: ' + accountList;
      const r2 = await fetch('/exchange_token', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{public_token}})
      }});
      const data2 = await r2.json();
      if (data2.access_token) {{
        document.getElementById('status').innerHTML =
          '<b style="color:#00ff88">Linked!</b><br>Account: ' + (metadata.institution ? metadata.institution.name : 'Unknown') +
          '<br>Access token saved locally.<br>Selected accounts: ' + accountList;
      }} else {{
        document.getElementById('status').innerHTML =
          '<b style="color:#ff4444">Error:</b> ' + JSON.stringify(data2);
      }}
    }},
    onEvent: (eventName, metadata) => {{
      console.log('Plaid event:', eventName, metadata);
      if (eventName === 'SELECT_INSTITUTION') {{
        console.log('Institution selected:', metadata.institution ? metadata.institution.name : 'none');
      }}
      if (eventName === 'SUBMIT_CREDENTIALS') {{
        console.log('Credentials submitted, accounts:', metadata.accounts);
      }}
    }},
    onExit: (err, metadata) => {{
      if (err) console.log('Link exit error:', err);
      console.log('Exit metadata:', metadata);
    }}
  }});
  handler.open();
}}
document.getElementById('linkBtn').addEventListener('click', initLink);
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        elif self.path == "/update":
            self.serve_update_page()
        else:
            self.send_response(404)
            self.end_headers()

    def serve_update_page(self):
        # Create a fresh update token
        import plaid
        from plaid.model.link_token_create_request import LinkTokenCreateRequest
        from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
        from plaid.model.products import Products
        from plaid.model.country_code import CountryCode

        tokens = {}
        if TOKENS_FILE.exists():
            with open(TOKENS_FILE) as f:
                tokens = json.load(f)

        # Get first token to update
        if not tokens:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No existing tokens to update")
            return

        token = list(tokens.values())[0]
        client = self._plaid_client()

        req = LinkTokenCreateRequest(
            access_token=token,
            products=[Products("liabilities")],
            client_name="Nova Finance",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id="opus-nova-001"),
        )
        resp = client.link_token_create(req)
        update_token = resp['link_token']

        update_html = f"""<!DOCTYPE html>
<html>
<head>
<title>Update Chase Permissions</title>
<script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background: #0a0a0a; color: #e0e0e0; }}
h1 {{ color: #00d4ff; }}
button {{ padding: 14px 28px; font-size: 16px; background: #00d4ff; color: #000; border: none; border-radius: 6px; cursor: pointer; }}
button:hover {{ background: #00b8e0; }}
#status {{ margin-top: 20px; padding: 12px; background: #1a1a1a; border-radius: 6px; }}
</style>
</head>
<body>
<h1>Update Chase Permissions</h1>
<p>Click below to grant Nova Finance access to your Chase credit card data.</p>
<button id="updateBtn">Update Permissions</button>
<div id="status">Click the button to start...</div>
<script>
const UPDATE_TOKEN = '{update_token}';
console.log('Update token:', UPDATE_TOKEN);

document.getElementById('updateBtn').addEventListener('click', function() {{
  document.getElementById('status').innerText = 'Opening Plaid Link...';
  const handler = Plaid.create({{
    token: UPDATE_TOKEN,
    onSuccess: function(public_token, metadata) {{
      console.log('Success:', metadata);
      const accounts = metadata.accounts || [];
      const names = accounts.map(a => a.name || a.mask).join(', ');
      document.getElementById('status').innerHTML =
        '<b style="color:#00ff88">Success!</b><br>Updated accounts: ' + names +
        '<br>Reload the dashboard to see credit cards.';
    }},
    onEvent: function(eventName, metadata) {{
      console.log('Event:', eventName, metadata);
    }},
    onExit: function(err, metadata) {{
      if (err) {{
        console.log('Error:', err);
        document.getElementById('status').innerHTML =
          '<b style="color:#ff4444">Error:</b> ' + (err.display_message || err.error_message || 'Unknown error');
      }} else {{
        document.getElementById('status').innerText = 'Update cancelled or completed.';
      }}
    }}
  }});
  handler.open();
}});
</script>
</body>
</html>"""

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(update_html.encode())

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len else b"{}"

        if self.path == "/create_link_token":
            self.create_link_token()
        elif self.path == "/exchange_token":
            self.exchange_token(json.loads(body.decode()))
        else:
            self.send_response(404)
            self.end_headers()

    def _plaid_client(self):
        import plaid
        from plaid.api import plaid_api
        config = plaid.Configuration(
            host=API_HOST,
            api_key={"clientId": CLIENT_ID, "secret": SECRET},
        )
        return plaid_api.PlaidApi(plaid.ApiClient(config))

    def create_link_token(self):
        from plaid.model.link_token_create_request import LinkTokenCreateRequest
        from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
        from plaid.model.products import Products
        from plaid.model.country_code import CountryCode

        client = self._plaid_client()
        req = LinkTokenCreateRequest(
            products=[Products("auth"), Products("transactions"), Products("liabilities")],
            client_name="Nova Finance",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id="opus-nova-001"),
        )
        resp = client.link_token_create(req)
        token = resp["link_token"]

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"link_token": token}).encode())

    def exchange_token(self, data):
        from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

        client = self._plaid_client()
        req = ItemPublicTokenExchangeRequest(public_token=data["public_token"])
        resp = client.item_public_token_exchange(req)
        access_token = resp["access_token"]
        item_id = resp["item_id"]

        # Save token
        tokens = {}
        if TOKENS_FILE.exists():
            with open(TOKENS_FILE) as f:
                tokens = json.load(f)
        tokens[item_id] = access_token
        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f, indent=2)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps({"access_token": access_token, "item_id": item_id}).encode())


if __name__ == "__main__":
    port = 3000
    server = HTTPServer(("", port), Handler)
    print(f"Plaid Link server running at http://localhost:{port}")
    print(f"Mode: {LINK_ENV}")
    print("Open that URL in your browser and click 'Connect Bank Account'")
    print("Press Ctrl+C when done.\n")
    webbrowser.open(f"http://localhost:{port}")
    server.serve_forever()
