import json, requests, urllib3
urllib3.disable_warnings()

session = requests.Session()
with open('tmp/unifi_local_working.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

BASE_URL = 'https://192.241.248.242/proxy/network/api/s/default'

# Try to get network list
r = session.get(f'{BASE_URL}/rest/networkconf', verify=False, timeout=15)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    for item in data.get('data', []):
        print(f'  {item["name"]} (ID: {item["_id"]}, Purpose: {item["purpose"]})')
else:
    print(f'Error: {r.text[:500]}')
