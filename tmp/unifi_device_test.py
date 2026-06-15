"""
Test device API paths
"""
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://192.241.248.242"

session = requests.Session()
with open('tmp/unifi_authenticated.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

# Test device paths
device_paths = [
    "/proxy/network/api/s/default/stat/device",
    "/proxy/network/api/s/default/rest/device",
    "/proxy/network/api/s/default/stat/ap",
    "/proxy/network/api/s/default/rest/ap",
    "/api/s/default/stat/device",
]

print("Testing device paths:")
for path in device_paths:
    r = session.get(f"{BASE_URL}{path}", verify=False, timeout=30)
    print(f"  {path}: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if 'data' in data:
            items = data['data']
            print(f"    Found {len(items)} items")
            if len(items) > 0:
                print(f"    First: {items[0].get('name', 'unnamed')} ({items[0].get('model', 'unknown')})")
