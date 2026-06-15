import json, requests, urllib3
urllib3.disable_warnings()

session = requests.Session()
with open('tmp/unifi_local_working.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

BASE_URL = 'https://192.241.248.242/proxy/network/api/s/default'

# Try POST directly with cookie auth
payload = {
    "name": "sojourn-office",
    "vlan": 10,
    "purpose": "corporate",
    "networkgroup": "LAN",
    "ip_subnet": "192.168.10.1/24",
    "dhcpd_start": "192.168.10.10",
    "dhcpd_stop": "192.168.10.250",
    "dhcpd_enabled": True,
    "vlan_enabled": True,
    "site_id": "63753636922fab0fb7676937"
}

r = session.post(f'{BASE_URL}/rest/networkconf', json=payload, verify=False, timeout=15)
print(f'POST /rest/networkconf: {r.status_code}')
if r.status_code == 200:
    print(f'Success: {json.dumps(r.json(), indent=2)[:500]}')
else:
    print(f'Error: {r.text[:500]}')
