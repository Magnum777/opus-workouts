import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
with open('tmp/unifi_authenticated.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

# Get self data including csrf token
r = session.get('https://192.241.248.242/proxy/network/api/s/default/self', verify=False, timeout=30)
if r.status_code == 200:
    self_data = r.json()['data'][0]
    print(f"Name: {self_data.get('name')}")
    print(f"Is Super: {self_data.get('is_super')}")
    print(f"Is Owner: {self_data.get('is_owner')}")
    print(f"Email: {self_data.get('email')}")
    # Check for csrf token
    csrf = self_data.get('csrf_token', '')
    print(f"CSRF Token: {csrf[:50] if csrf else 'none'}...")
    
    # Save full self data for inspection
    with open('tmp/unifi_self.json', 'w') as f:
        json.dump(self_data, f, indent=2)
    print("Saved full self data to tmp/unifi_self.json")
