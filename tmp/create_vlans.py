import json, requests, urllib3
urllib3.disable_warnings()

session = requests.Session()
with open('tmp/unifi_local_working.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

BASE_URL = 'https://192.241.248.242/proxy/network/api/s/default'

# Create VLAN-only networks first (works), then update with IP config
vlans = [
    {"name": "sojourn", "vlan": 20},
    {"name": "sojourn-guest", "vlan": 30}
]

for v in vlans:
    payload = {
        "name": v["name"],
        "vlan": v["vlan"],
        "purpose": "vlan-only",
        "vlan_enabled": True
    }
    r = session.post(f'{BASE_URL}/rest/networkconf', json=payload, verify=False, timeout=15)
    print(f'{v["name"]} (VLAN {v["vlan"]}): {r.status_code}')
    if r.status_code == 200:
        print(f'  Created: {r.json()["data"][0]["_id"]}')
    else:
        print(f'  Error: {r.text[:200]}')
    print()
