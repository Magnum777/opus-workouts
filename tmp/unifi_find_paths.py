"""
Find correct API paths for this UniFi controller version
"""
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://192.241.248.242"

# Load authenticated session
session = requests.Session()
with open('tmp/unifi_authenticated.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

# Test various paths
paths = [
    "/proxy/network/api/s/default/stat/sysinfo",
    "/proxy/network/api/s/default/stat/wlan",
    "/proxy/network/api/s/default/rest/wlanconf",
    "/proxy/network/api/s/default/rest/wlan",
    "/proxy/network/api/s/default/rest/device",
    "/proxy/network/api/s/default/rest/setting",
    "/proxy/network/api/s/default/rest/networkconf",
]

print("Testing API paths:")
for path in paths:
    r = session.get(f"{BASE_URL}{path}", verify=False, timeout=30)
    print(f"  {path}: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if 'data' in data:
            items = data['data']
            if isinstance(items, list) and len(items) > 0:
                print(f"    Found {len(items)} items")
                if len(items) > 0:
                    print(f"    First item keys: {list(items[0].keys())[:10]}")
            else:
                print(f"    Response: {str(data)[:200]}")
