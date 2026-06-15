import json, requests, urllib3
urllib3.disable_warnings()

session = requests.Session()
with open('tmp/unifi_local_working.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

BASE = 'https://192.241.248.242/proxy/network/api/s/default'

# 1. Health
print("=== HEALTH ===")
r = session.get(f'{BASE}/stat/health', verify=False, timeout=10)
if r.status_code == 200:
    for item in r.json().get('data', []):
        print(f'  {item["subsystem"]}: {item["status"]}')
else:
    print(f'  Failed: {r.status_code}')

# 2. DPI
print("\n=== DPI ===")
r = session.get(f'{BASE}/rest/setting/dpi', verify=False, timeout=10)
if r.status_code == 200:
    data = r.json().get('data', [{}])[0]
    print(f'  enabled: {data.get("enabled", "?")}')
    print(f'  key: {data.get("key", "?")}')
else:
    print(f'  Failed: {r.status_code}')

# 3. Guest Portal Full Text
print("\n=== GUEST PORTAL ===")
r = session.get(f'{BASE}/rest/setting/guest_access', verify=False, timeout=10)
if r.status_code == 200:
    data = r.json().get('data', [{}])[0]
    print(f'  portal_enabled: {data.get("portal_enabled", "?")}')
    print(f'  portal_customized: {data.get("portal_customized", "?")}')
    print(f'  title: {data.get("portal_customized_title", "?")}')
    print(f'  welcome: {data.get("portal_customized_welcome_text", "?")}')
    print(f'  button: {data.get("portal_customized_button_text", "?")}')
    print(f'  tos_enabled: {data.get("portal_customized_tos_enabled", "?")}')
    print(f'  tos: {data.get("portal_customized_tos", "")[:80]}...')
    print(f'  success: {data.get("portal_customized_success_text", "?")}')
    print(f'  expire: {data.get("expire", "?")} minutes ({data.get("expire", 0)//60} hours)')
    print(f'  download_limit: {data.get("download_limit", "?")} Kbps')
    print(f'  upload_limit: {data.get("upload_limit", "?")} Kbps')
    print(f'  logo_enabled: {data.get("portal_customized_logo_enabled", "?")}')
    print(f'  bg_color: {data.get("portal_customized_bg_color", "?")}')
    print(f'  box_color: {data.get("portal_customized_box_color", "?")}')
    print(f'  button_color: {data.get("portal_customized_button_color", "?")}')
    print(f'  text_color: {data.get("portal_customized_text_color", "?")}')
else:
    print(f'  Failed: {r.status_code}')

# 4. Switches
print("\n=== SWITCHES ===")
r = session.get(f'{BASE}/stat/device', verify=False, timeout=10)
if r.status_code == 200:
    for dev in r.json().get('data', []):
        if dev.get('type') == 'usw':
            print(f'  {dev.get("name", "?")} ({dev.get("model", "?")}): adopted={dev.get("adopted", "?")}, state={dev.get("state", "?")}')
else:
    print(f'  Failed: {r.status_code}')

# 5. USG
print("\n=== USG ===")
r = session.get(f'{BASE}/stat/device', verify=False, timeout=10)
if r.status_code == 200:
    for dev in r.json().get('data', []):
        if dev.get('type') == 'ugw' or 'usg' in str(dev.get('model', '')).lower():
            print(f'  {dev.get("name", "?")}: adopted={dev.get("adopted", "?")}, state={dev.get("state", "?")}')
else:
    print(f'  Failed: {r.status_code}')

print("\nDone.")
