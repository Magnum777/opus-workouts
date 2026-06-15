import json, requests, urllib3
urllib3.disable_warnings()

session = requests.Session()
with open('tmp/unifi_local_working.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

BASE_URL = 'https://192.241.248.242/proxy/network/api/s/default'

# Check for WAN2
r = session.get(f'{BASE_URL}/rest/networkconf', verify=False, timeout=15)
if r.status_code == 200:
    for item in r.json().get('data', []):
        if item.get('wan_networkgroup') == 'WAN2' or 'Internet 2' in item.get('name', ''):
            print(f'WAN2: {item["name"]}, enabled={item.get("enabled", "?")}, type={item.get("wan_type", "?")}')

# Also check USG directly
r2 = session.get(f'{BASE_URL}/stat/device', verify=False, timeout=15)
if r2.status_code == 200:
    for item in r2.json().get('data', []):
        if item.get('model') == 'USG3':
            print(f'\nUSG: {item.get("name", "USG")}, state={item.get("state", "?")}')
            for port in item.get('port_table', []):
                print(f'  Port {port.get("name", "?")}: {port.get("up", "?")}')
