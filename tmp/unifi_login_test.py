import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test direct console login with the Gmail credentials
# UniFi local controllers typically use these endpoints

console_ip = "192.241.248.242"
email = "nova.cofounder@gmail.com"
password = "n20CQ9aRcvQdKCFf"

session = requests.Session()

# Try 1: Direct login endpoint
print("=== Attempt 1: Direct console login ===")
for endpoint in [
    f"https://{console_ip}/api/auth/login",
    f"https://{console_ip}:8443/api/auth/login",
]:
    try:
        resp = session.post(endpoint, json={
            "username": email,
            "password": password,
            "remember": True
        }, timeout=15, verify=False)
        print(f"  {endpoint}: {resp.status_code}")
        if resp.status_code == 200:
            print(f"  SUCCESS! Token: {resp.json().get('csrfToken', 'N/A')[:20]}...")
            break
        else:
            print(f"  Response: {resp.text[:300]}")
    except Exception as e:
        print(f"  Error: {e}")

# Try 2: UniFi Cloud (Site Manager) login
print("\n=== Attempt 2: UniFi Cloud Site Manager ===")
# UniFi Site Manager uses OAuth, but let's try basic auth or check if there's a direct API
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0'
}

# Try getting login page
for url in [
    "https://unifi.ui.com/login",
    "https://account.ui.com/api/users/me",
]:
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"  {url}: {resp.status_code}")
    except Exception as e:
        print(f"  Error: {e}")

# Try 3: Check if the email is linked to the console via the existing API key
print("\n=== Attempt 3: Verify console ownership via Site Manager API ===")
api_headers = {'X-Api-Key': 'M_9VaI2JRSa4gWtFHzlA-rXK0r55m_KA'}
resp = requests.get('https://api.ui.com/ea/hosts/192bddb3-1b82-4096-82df-1c71631154a3', 
                     headers=api_headers, timeout=15)
if resp.status_code == 200:
    host = resp.json().get('data', {})
    print(f"  Console email: {host.get('userData', {}).get('email', 'N/A')}")
    print(f"  Console name: {host.get('userData', {}).get('fullName', 'N/A')}")
    print(f"  Match: {email.lower() in str(host).lower()}")
