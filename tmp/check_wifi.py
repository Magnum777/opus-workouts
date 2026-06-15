import json, requests, urllib3
urllib3.disable_warnings()

session = requests.Session()
with open('tmp/unifi_local_working.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

BASE_URL = 'https://192.241.248.242/proxy/network/api/s/default'

# Check WLANs
r = session.get(f'{BASE_URL}/rest/wlanconf', verify=False, timeout=15)
print(f'WLAN Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    for item in data.get('data', []):
        print(f'  {item["name"]}: enabled={item["enabled"]}, security={item["security"]}, is_guest={item.get("is_guest", False)}, network_id={item["networkconf_id"]}')

# Check health
r2 = session.get(f'{BASE_URL}/stat/health', verify=False, timeout=15)
if r2.status_code == 200:
    print('\nHealth:')
    for item in r2.json().get('data', []):
        print(f'  {item["subsystem"]}: {item["status"]} (users: {item.get("num_user", "N/A")}, aps: {item.get("num_adopted", "N/A")})')
