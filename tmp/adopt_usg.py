import json, requests, urllib3
urllib3.disable_warnings()

session = requests.Session()
with open('tmp/unifi_local_working.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

BASE_URL = 'https://192.241.248.242/proxy/network/api/s/default'

# Find the USG
r = session.get(f'{BASE_URL}/rest/device', verify=False, timeout=10)
if r.status_code == 200:
    data = r.json().get('data', [])
    print('Looking for USG...')
    for dev in data:
        if dev.get('type') == 'ugw':
            print(f'Found USG:')
            print(f'  Name: {dev.get("name", "?")}')
            print(f'  MAC: {dev.get("mac", "?")}')
            print(f'  State: {dev.get("state", "?")}')  
            print(f'  Adopted: {dev.get("adopted", "?")}')
            print(f'  IP: {dev.get("ip", "?")}')
            print(f'  Model: {dev.get("model", "?")}')
            print(f'  Version: {dev.get("version", "?")}')
            print(f'  Adoption error: {dev.get("adoption_error", "none")}')
            print(f'  Provisioned at: {dev.get("provisioned_at", "never")}')
            
            # Try to adopt
            if not dev.get('adopted', False):
                print('\nAttempting adoption...')
                adopt_payload = {
                    "cmd": "adopt",
                    "mac": dev.get("mac")
                }
                a = session.post(f'{BASE_URL}/cmd/sitemgr', json=adopt_payload, verify=False, timeout=10)
                print(f'  Adoption cmd status: {a.status_code}')
                if a.status_code == 200:
                    print(f'  Response: {json.dumps(a.json(), indent=2)[:500]}')
                else:
                    print(f'  Error: {a.text[:500]}')
            else:
                print('\nAlready adopted!')
                # Try forcing provision
                print('Forcing provision...')
                prov_payload = {
                    "cmd": "force-provision",
                    "mac": dev.get("mac")
                }
                p = session.post(f'{BASE_URL}/cmd/devmgr', json=prov_payload, verify=False, timeout=10)
                print(f'  Force provision status: {p.status_code}')
                if p.status_code == 200:
                    print(f'  Response: {json.dumps(p.json(), indent=2)[:500]}')
                else:
                    print(f'  Error: {p.text[:500]}')
        elif 'gateway' in str(dev.get('model','')).lower() or 'usg' in str(dev.get('model','')).lower():
            print(f'Found gateway-like device: {dev.get("name","?")} ({dev.get("model","?")}), adopted={dev.get("adopted","?")}')
else:
    print(f'Failed to get devices: {r.status_code}')
    print(r.text[:500])
