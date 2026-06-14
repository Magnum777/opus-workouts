import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

email = "nova.cofounder@gmail.com"
password = "n20CQ9aRcvQdKCFf"

session = requests.Session()

# Step 1: Login to UniFi Cloud (account.ui.com)
print("=== Step 1: UniFi Cloud Login ===")
login_resp = session.post(
    "https://sso.ui.com/api/users/login",
    json={"email": email, "password": password},
    headers={"Content-Type": "application/json"},
    timeout=15
)
print(f"  Login response: {login_resp.status_code}")
print(f"  Headers: {dict(login_resp.headers)}")
if login_resp.status_code == 200:
    print(f"  Body: {login_resp.text[:500]}")
    
    # Step 2: Get CSRF token for console access
    print("\n=== Step 2: Get Console Access Token ===")
    
    # Try to get a session for the Sojourn Church console
    console_id = "192bddb3-1b82-4096-82df-1c71631154a3"
    
    # Method: Use the cloud API to get a proxy token
    for endpoint in [
        f"https://api.ui.com/ea/hosts/{console_id}/api/auth",
        f"https://api.ui.com/ea/consoles/{console_id}/auth",
        f"https://unifi.ui.com/api/users/{email}/consoles",
    ]:
        try:
            resp = session.get(endpoint, timeout=15)
            print(f"  {endpoint.split('/')[-2:]}: {resp.status_code}")
            if resp.status_code == 200:
                print(f"  SUCCESS: {resp.text[:500]}")
        except Exception as e:
            print(f"  Error: {e}")

    # Step 3: Try direct console proxy through cloud
    print("\n=== Step 3: Cloud-Proxied Console Access ===")
    proxy_url = f"https://{console_id}.unifi-hosting.ui.com/proxy/network/api/s/default/stat/device"
    try:
        resp = session.get(proxy_url, timeout=20, verify=False)
        print(f"  Proxy status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  DEVICES FOUND: {len(resp.json().get('data', []))}")
    except Exception as e:
        print(f"  Error: {e}")

else:
    print(f"  Login failed: {login_resp.text[:500]}")

# Step 4: Try with the API key combined with cloud auth
print("\n=== Step 4: API Key + Cloud Session ===")
api_headers = {
    'X-Api-Key': 'M_9VaI2JRSa4gWtFHzlA-rXK0r55m_KA',
    'Content-Type': 'application/json'
}
# Try getting detailed host info
resp = requests.get(
    'https://api.ui.com/ea/hosts/192bddb3-1b82-4096-82df-1c71631154a3',
    headers=api_headers,
    timeout=15
)
if resp.status_code == 200:
    host = resp.json().get('data', {})
    print(f"  Console access info:")
    print(f"    Name: {host.get('reportedState', {}).get('name', 'N/A')}")
    print(f"    Version: {host.get('reportedState', {}).get('version', 'N/A')}")
    print(f"    Mgmt Port: {host.get('reportedState', {}).get('mgmt_port', 'N/A')}")
    print(f"    IP: {host.get('ipAddress', 'N/A')}")
    # Check if there's a direct access URL
    print(f"    Has IP Addrs: {host.get('reportedState', {}).get('ipAddrs', [])}")
    print(f"    Hostname: {host.get('reportedState', {}).get('hostname', 'N/A')}")
