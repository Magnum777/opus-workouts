import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
with open('tmp/unifi_authenticated.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

# Check current user
r = session.get('https://192.241.248.242/proxy/network/api/s/default/stat/sysinfo', verify=False, timeout=30)
if r.status_code == 200:
    data = r.json()['data'][0]
    print(f"Role: {data.get('role', 'unknown')}")
    print(f"Version: {data.get('version', 'unknown')}")
    print(f"Build: {data.get('build', 'unknown')}")

# Check admin status
r2 = session.get('https://192.241.248.242/proxy/network/api/s/default/self', verify=False, timeout=30)
print(f"Self endpoint: {r2.status_code}")
if r2.status_code == 200:
    print(r2.text[:500])
