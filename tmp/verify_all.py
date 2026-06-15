"""
Rate-limit-aware UniFi verification script.
Logs in once, reuses cookies, batches API calls with delays.
"""
import json, requests, urllib3, time
urllib3.disable_warnings()

# Config
HOST = '192.241.248.242'
USERNAME = 'Nova'
PASSWORD = 'N0v4!123N0v4!12'
BASE = f'https://{HOST}/proxy/network/api/s/default'

def login_and_save_session():
    """Login and save cookie jar to file"""
    session = requests.Session()
    r = session.post(f'https://{HOST}/api/auth/login', 
                     json={'username': USERNAME, 'password': PASSWORD}, 
                     verify=False, timeout=15)
    if r.status_code != 200:
        print(f'Login failed: {r.status_code} - {r.text[:200]}')
        return None
    cookies = {c.name: c.value for c in session.cookies}
    with open('tmp/unifi_session.json', 'w') as f:
        json.dump(cookies, f)
    print('[OK] Logged in, session saved.')
    return session

def load_session():
    """Load existing session, check if valid"""
    try:
        with open('tmp/unifi_session.json', 'r') as f:
            cookies = json.load(f)
        session = requests.Session()
        for name, value in cookies.items():
            session.cookies.set(name, value)
        r = session.get(f'{BASE}/stat/health', verify=False, timeout=10)
        if r.status_code == 200:
            return session
        else:
            print(f'Expired session (status {r.status_code}), re-logging in...')
            return login_and_save_session()
    except (FileNotFoundError, json.JSONDecodeError):
        print('No saved session, logging in...')
        return login_and_save_session()

def api_get(session, path, label):
    """GET with retry on 401"""
    r = session.get(f'{BASE}{path}', verify=False, timeout=15)
    if r.status_code == 401:
        print(f'  [{label}] Session expired, re-logging in...')
        session = login_and_save_session()
        if session:
            r = session.get(f'{BASE}{path}', verify=False, timeout=15)
    return r

# Main
print('='*60)
print('SOJOURN CHURCH NETWORK VERIFICATION')
print('='*60)

session = load_session()
if not session:
    print('Failed to authenticate.')
    exit(1)

# 1. Health
print('\n=== HEALTH ===')
r = api_get(session, '/stat/health', 'health')
if r.status_code == 200:
    for item in r.json().get('data', []):
        print(f'  {item["subsystem"]:8} | {item["status"]}')
else:
    print(f'  Failed: {r.status_code}')
time.sleep(1)

# 2. DPI
print('\n=== DPI ===')
r = api_get(session, '/rest/setting/dpi', 'dpi')
if r.status_code == 200:
    data = r.json().get('data', [{}])[0]
    print(f'  enabled: {data.get("enabled", "?")}')
else:
    print(f'  Failed: {r.status_code}')
time.sleep(1)

# 3. Networks
print('\n=== NETWORKS ===')
r = api_get(session, '/rest/networkconf', 'networks')
if r.status_code == 200:
    for item in r.json().get('data', []):
        vlan_info = f'VLAN {item.get("vlan", "N/A")}' if item.get('vlan_enabled') else 'native'
        print(f'  {item["name"]:15} | {item["purpose"]:10} | {item.get("ip_subnet", "N/A"):18} | {vlan_info}')
else:
    print(f'  Failed: {r.status_code}')
time.sleep(1)

# 4. SSIDs
print('\n=== SSIDs ===')
r = api_get(session, '/rest/wlanconf', 'ssids')
if r.status_code == 200:
    for item in r.json().get('data', []):
        print(f'  {item["name"]:15} | sec={item["security"]:8} | guest={item.get("is_guest", False)} | isolate={item.get("l2_isolation", False)} | mcast={item.get("mcastenhance_enabled", False)} | enabled={item["enabled"]}')
else:
    print(f'  Failed: {r.status_code}')
time.sleep(1)

# 5. Guest Portal Detail
print('\n=== GUEST PORTAL ===')
r = api_get(session, '/rest/setting/guest_access', 'portal')
if r.status_code == 200:
    d = r.json().get('data', [{}])[0]
    print(f'  portal_enabled:    {d.get("portal_enabled", "?")}')
    print(f'  portal_customized: {d.get("portal_customized", "?")}')
    print(f'  title:             {d.get("portal_customized_title", "?")}')
    print(f'  welcome:           {d.get("portal_customized_welcome_text", "?")}')
    print(f'  button:            {d.get("portal_customized_button_text", "?")}')
    print(f'  tos_enabled:       {d.get("portal_customized_tos_enabled", "?")}')
    print(f'  tos_preview:       {d.get("portal_customized_tos", "")[:60]}...')
    print(f'  expire:            {d.get("expire", "?")} min = {d.get("expire", 0)//60} hrs')
    dl = d.get('download_limit')
    ul = d.get('upload_limit')
    print(f'  download_limit:    {dl if dl is not None else "?"} Kbps')
    print(f'  upload_limit:      {ul if ul is not None else "?"} Kbps')
    print(f'  logo_enabled:      {d.get("portal_customized_logo_enabled", "?")}')
    print(f'  bg_color:          {d.get("portal_customized_bg_color", "?")}')
    print(f'  button_color:      {d.get("portal_customized_button_color", "?")}')
    print(f'  text_color:        {d.get("portal_customized_text_color", "?")}')
    print(f'  success_msg:       {d.get("portal_customized_success_text", "?")}')
else:
    print(f'  Failed: {r.status_code}')
time.sleep(1)

# 6. AP Channels
print('\n=== ACCESS POINTS ===')
r = api_get(session, '/stat/device', 'devices')
if r.status_code == 200:
    for dev in r.json().get('data', []):
        if dev.get('type') == 'uap':
            ch2 = '?'; ht2 = '?'; ch5 = '?'; ht5 = '?'
            for radio in dev.get('radio_table', []):
                name = radio.get('name', '')
                if name in ('wifi0', 'ra0'):
                    ch2 = radio.get('channel', '?')
                    ht2 = radio.get('ht', '?')
                elif name in ('wifi1', 'rai0', 'wifi1ap6', 'wifi1ap5', 'wifi1ap4'):
                    ch5 = radio.get('channel', '?')
                    ht5 = radio.get('ht', '?')
            print(f'  {dev["name"]:6} | {dev.get("model", "?"):6} | 2.4: ch{ch2}/{ht2} | 5: ch{ch5}/{ht5} | adopted={dev.get("adopted", "?")} | state={dev.get("state", "?")}')
else:
    print(f'  Failed: {r.status_code}')
time.sleep(1)

# 7. USG & Switches
print('\n=== GATEWAY & SWITCHES ===')
r = api_get(session, '/stat/device', 'gateway')
if r.status_code == 200:
    for dev in r.json().get('data', []):
        t = dev.get('type', '?')
        if t in ('ugw', 'usw'):
            print(f'  {dev["name"]:15} | {dev.get("model", "?"):8} | type={t} | adopted={dev.get("adopted", "?")} | state={dev.get("state", "?")}')
else:
    print(f'  Failed: {r.status_code}')

print('\n' + '='*60)
print('VERIFICATION COMPLETE')
print('='*60)
