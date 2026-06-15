"""
UniFi Phase 1 — Fixed API paths for v5 controller
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

print("Loaded authenticated session")
print(f"Cookies: {dict(session.cookies)}")

# Try different API paths to find what works
paths_to_test = [
    "/api/s/default/stat/sysinfo",
    "/api/s/default/stat/device",
    "/proxy/network/api/s/default/stat/sysinfo",
    "/proxy/network/api/s/default/stat/device",
]

print("\nTesting API paths...")
working_base = None
for path in paths_to_test:
    r = session.get(f"{BASE_URL}{path}", verify=False, timeout=30)
    print(f"  {path}: {r.status_code}")
    if r.status_code == 200:
        print(f"    [OK] Found working path!")
        working_base = path.rsplit('/', 1)[0]
        break

if not working_base:
    print("\n[FAIL] No working API path found")
    sys.exit(1)

print(f"\nWorking base: {working_base}")

# Now make changes with correct paths
changes = []

# Get WLANs (try both wlan and wlanconf)
print("\n[1/5] Band steering...")
for wlan_path in ["/rest/wlan", "/rest/wlanconf"]:
    r = session.get(f"{BASE_URL}{working_base}{wlan_path}", verify=False, timeout=30)
    print(f"  Trying {wlan_path}: {r.status_code}")
    if r.status_code == 200:
        wlans = r.json().get('data', [])
        print(f"  Found {len(wlans)} WLANs")
        for wlan in wlans:
            wlan_id = wlan['_id']
            r2 = session.put(f"{BASE_URL}{working_base}{wlan_path}/{wlan_id}", 
                           json={"bandsteering_mode": "balanced"}, verify=False, timeout=30)
            if r2.status_code == 200:
                print(f"  [OK] {wlan.get('name', 'unknown')}: band steering ON")
                changes.append(f"band_steering:{wlan.get('name')}")
            else:
                print(f"  [FAIL] {wlan.get('name')} ({r2.status_code})")
        break

# Min RSSI
print("\n[2/5] Min RSSI -70...")
for wlan_path in ["/rest/wlan", "/rest/wlanconf"]:
    r = session.get(f"{BASE_URL}{working_base}{wlan_path}", verify=False, timeout=30)
    if r.status_code == 200:
        wlans = r.json().get('data', [])
        for wlan in wlans:
            wlan_id = wlan['_id']
            r2 = session.put(f"{BASE_URL}{working_base}{wlan_path}/{wlan_id}", 
                           json={"min_rssi_enabled": True, "min_rssi": -70}, verify=False, timeout=30)
            if r2.status_code == 200:
                print(f"  [OK] {wlan.get('name', 'unknown')}: min RSSI -70")
                changes.append(f"min_rssi:{wlan.get('name')}")
            else:
                print(f"  [FAIL] {wlan.get('name')} ({r2.status_code})")
        break

# SAP 5GHz
print("\n[3/5] SAP 5GHz...")
r = session.get(f"{BASE_URL}{working_base}/stat/device", verify=False, timeout=30)
if r.status_code == 200:
    devices = r.json().get('data', [])
    for d in devices:
        if d.get('name', '').upper() == 'SAP':
            device_id = d['_id']
            radio_table = d.get('radio_table', [{}, {}])
            if len(radio_table) > 1:
                radio_table[1]['channel'] = 149
                radio_table[1]['ht'] = 40
            r2 = session.put(f"{BASE_URL}{working_base}/rest/device/{device_id}", 
                          json={"radio_table": radio_table}, verify=False, timeout=30)
            if r2.status_code == 200:
                print("  [OK] SAP: Ch 149 / 40MHz")
                changes.append("sap_5ghz:ch149_40mhz")
            else:
                print(f"  [FAIL] SAP ({r2.status_code})")
            break

# DPI
print("\n[4/5] DPI...")
r = session.put(f"{BASE_URL}{working_base}/rest/setting", 
               json={"dpi_enabled": True}, verify=False, timeout=30)
if r.status_code == 200:
    print("  [OK] DPI enabled")
    changes.append("dpi:enabled")
else:
    print(f"  [FAIL] DPI ({r.status_code})")

# Multicast
print("\n[5/5] Multicast...")
for wlan_path in ["/rest/wlan", "/rest/wlanconf"]:
    r = session.get(f"{BASE_URL}{working_base}{wlan_path}", verify=False, timeout=30)
    if r.status_code == 200:
        wlans = r.json().get('data', [])
        for wlan in wlans:
            wlan_id = wlan['_id']
            r2 = session.put(f"{BASE_URL}{working_base}{wlan_path}/{wlan_id}", 
                           json={"mcastenhance_enabled": True}, verify=False, timeout=30)
            if r2.status_code == 200:
                print(f"  [OK] {wlan.get('name', 'unknown')}: multicast ON")
                changes.append(f"multicast:{wlan.get('name')}")
            else:
                print(f"  [FAIL] {wlan.get('name')} ({r2.status_code})")
        break

print("\n" + "="*60)
print(f"COMPLETE: {len(changes)} changes made")
print("="*60)
for c in changes:
    print(f"  [OK] {c}")
