import json, requests, urllib3
urllib3.disable_warnings()

session = requests.Session()
with open('tmp/unifi_local_working.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

BASE_URL = 'https://192.241.248.242'
r = session.get(f'{BASE_URL}/proxy/network/api/s/default/rest/setting/guest_access', verify=False, timeout=10)
if r.status_code == 200:
    data = r.json()['data'][0]
    print('Current portal settings:')
    print(f'  portal_customized: {data.get("portal_customized", False)}')
    print(f'  title: {data.get("portal_customized_title", "NOT SET")}')
    print(f'  welcome_text: {data.get("portal_customized_welcome_text", "NOT SET")}')
    print(f'  button_text: {data.get("portal_customized_button_text", "NOT SET")}')
    print(f'  tos_enabled: {data.get("portal_customized_tos_enabled", False)}')
    print(f'  logo_enabled: {data.get("portal_customized_logo_enabled", False)}')
    print(f'  logo_filename: {data.get("portal_customized_logo_filename", "none")}')
    print(f'  bg_color: {data.get("portal_customized_bg_color", "NOT SET")}')
    print(f'  box_color: {data.get("portal_customized_box_color", "NOT SET")}')
    print(f'  text_color: {data.get("portal_customized_text_color", "NOT SET")}')
    print(f'  button_color: {data.get("portal_customized_button_color", "NOT SET")}')
    print(f'  template_engine: {data.get("template_engine", "NOT SET")}')
    print(f'  portal_enabled: {data.get("portal_enabled", False)}')
    print(f'  auth: {data.get("auth", "NOT SET")}')
else:
    print(f'Failed: {r.status_code}')
