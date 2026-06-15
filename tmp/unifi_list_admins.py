"""
Check admin accounts with SSO session
"""
import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://192.241.248.242"

session = requests.Session()
with open('tmp/unifi_authenticated.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

# List admins
print("Checking admin accounts...")
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/admin", verify=False, timeout=30)
print(f"Admin list status: {r.status_code}")
if r.status_code == 200:
    admins = r.json().get('data', [])
    print(f"Found {len(admins)} admins:")
    for admin in admins:
        print(f"  - {admin.get('name', 'unknown')} ({admin.get('email', 'no email')}) - Super: {admin.get('is_super', False)}")
else:
    print(f"Failed: {r.text[:200]}")

# Also check user accounts
print("\nChecking user accounts...")
r2 = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/user", verify=False, timeout=30)
print(f"User list status: {r2.status_code}")
if r2.status_code == 200:
    users = r2.json().get('data', [])
    print(f"Found {len(users)} users")
    for user in users[:10]:
        print(f"  - {user.get('name', 'unknown')}: {user.get('note', 'no note')}")
