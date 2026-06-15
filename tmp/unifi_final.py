"""
UniFi Phase 1 -- SSO auth + immediate changes
"""
import requests
import json
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EMAIL = "nova.cofounder@gmail.com"
PASSWORD = "Fr34k3r!123123"
BASE_URL = "https://192.241.248.242"

session = requests.Session()

print("="*60)
print("UNIFI PHASE 1 -- SSO LOGIN + CHANGES")
print("="*60)

# Step 1: Login (may need MFA)
print("\n[1/3] Logging in...")
r = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": EMAIL, "password": PASSWORD, "remember": True},
    verify=False,
    timeout=30
)

print(f"Status: {r.status_code}")

if r.status_code == 499:
    print("MFA required. Give me the code NOW.")
    sys.exit(1)
elif r.status_code == 200:
    print("[OK] Logged in!")
else:
    print(f"Failed: {r.text[:200]}")
    sys.exit(1)

# Step 2: Get WLANs
print("\n[2/3] Getting WLAN config...")
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf", verify=False, timeout=30)
if r.status_code == 200:
    wlans = r.json().get('data', [])
    print(f"Found {len(wlans)} WLANs")
    for wlan in wlans:
        print(f"  - {wlan.get('name')} (ID: {wlan['_id'][:8]}...)")
else:
    print(f"Failed: {r.status_code}")
    wlans = []

# Step 3: Make all changes
print("\n[3/3] Making changes...")
changes = []

for wlan in wlans:
    wlan_id = wlan['_id']
    name = wlan.get('name', 'unknown')
    
    # Band steering
    r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}",
                   json={"bandsteering_mode": "balanced"}, verify=False, timeout=30)
    if r.status_code == 200:
        changes.append(f"band_steering:{name}")
        print(f"  [OK] {name}: band steering")
    else:
        print(f"  [FAIL] {name}: band steering ({r.status_code})")
    
    # Min RSSI
    r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}",
                   json={"min_rssi_enabled": True, "min_rssi": -70}, verify=False, timeout=30)
    if r.status_code == 200:
        changes.append(f"min_rssi:{name}")
        print(f"  [OK] {name}: min RSSI")
    else:
        print(f"  [FAIL] {name}: min RSSI ({r.status_code})")
    
    # Multicast
    r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}",
                   json={"mcastenhance_enabled": True}, verify=False, timeout=30)
    if r.status_code == 200:
        changes.append(f"multicast:{name}")
        print(f"  [OK] {name}: multicast")
    else:
        print(f"  [FAIL] {name}: multicast ({r.status_code})")

# SAP 5GHz
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/stat/device", verify=False, timeout=30)
if r.status_code == 200:
    devices = r.json().get('data', [])
    for d in devices:
        if d.get('name', '').upper() == 'SAP':
            mac = d.get('mac', '')
            radio_table = d.get('radio_table', [{}, {}])
            if len(radio_table) > 1:
                radio_table[1]['channel'] = 149
                radio_table[1]['ht'] = 40
            r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/device/{d['_id']}",
                          json={"radio_table": radio_table}, verify=False, timeout=30)
            if r.status_code == 200:
                changes.append("sap_5ghz:ch149_40mhz")
                print(f"  [OK] SAP: Ch 149 / 40MHz")
            else:
                print(f"  [FAIL] SAP ({r.status_code})")
            break

# DPI
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/setting", verify=False, timeout=30)
if r.status_code == 200:
    settings = r.json().get('data', [])
    for s in settings:
        if s.get('key') == 'dpi':
            r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/setting/{s['_id']}",
                           json={"enabled": True}, verify=False, timeout=30)
            if r.status_code == 200:
                changes.append("dpi:enabled")
                print(f"  [OK] DPI enabled")
            else:
                print(f"  [FAIL] DPI ({r.status_code})")
            break

print("\n" + "="*60)
print(f"COMPLETE: {len(changes)} changes")
print("="*60)
for c in changes:
    print(f"  [OK] {c}")
