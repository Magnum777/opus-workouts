"""
UniFi Phase 1 -- Push changes with local admin session
"""
import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://192.241.248.242"

session = requests.Session()
with open('tmp/unifi_local_working.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

print("="*60)
print("UNIFI PHASE 1 -- PUSHING CHANGES")
print("="*60)

changes = []

# Get WLANs
print("\nGetting WLAN config...")
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf", verify=False, timeout=30)
if r.status_code == 200:
    wlans = r.json().get('data', [])
    print(f"Found {len(wlans)} WLANs: {[w.get('name') for w in wlans]}")
else:
    print(f"Failed to get WLANs: {r.status_code}")
    wlans = []

# 1. Band steering
print("\n[1/5] Band steering...")
for wlan in wlans:
    wlan_id = wlan['_id']
    name = wlan.get('name', 'unknown')
    r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}", 
                   json={"bandsteering_mode": "balanced"}, verify=False, timeout=30)
    if r.status_code == 200:
        print(f"  [OK] {name}: band steering ON")
        changes.append(f"band_steering:{name}")
    else:
        print(f"  [FAIL] {name} ({r.status_code}): {r.text[:100]}")

# 2. Min RSSI
print("\n[2/5] Min RSSI -70...")
for wlan in wlans:
    wlan_id = wlan['_id']
    name = wlan.get('name', 'unknown')
    r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}", 
                   json={"min_rssi_enabled": True, "min_rssi": -70}, verify=False, timeout=30)
    if r.status_code == 200:
        print(f"  [OK] {name}: min RSSI -70")
        changes.append(f"min_rssi:{name}")
    else:
        print(f"  [FAIL] {name} ({r.status_code}): {r.text[:100]}")

# 3. SAP 5GHz
print("\n[3/5] SAP 5GHz...")
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/stat/device", verify=False, timeout=30)
if r.status_code == 200:
    devices = r.json().get('data', [])
    for d in devices:
        if d.get('name', '').upper() == 'SAP':
            device_id = d['_id']
            mac = d.get('mac', '')
            radio_table = d.get('radio_table', [{}, {}])
            if len(radio_table) > 1:
                radio_table[1]['channel'] = 149
                radio_table[1]['ht'] = 40
            r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/device/{device_id}", 
                          json={"radio_table": radio_table}, verify=False, timeout=30)
            if r.status_code == 200:
                print(f"  [OK] SAP ({mac}): Ch 149 / 40MHz")
                changes.append("sap_5ghz:ch149_40mhz")
            else:
                print(f"  [FAIL] SAP ({r.status_code}): {r.text[:100]}")
            break
    else:
        print("  ! SAP not found")
else:
    print(f"  Failed to get devices: {r.status_code}")

# 4. DPI
print("\n[4/5] DPI...")
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/setting", verify=False, timeout=30)
if r.status_code == 200:
    settings = r.json().get('data', [])
    for s in settings:
        if s.get('key') == 'dpi':
            setting_id = s['_id']
            r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/setting/{setting_id}", 
                           json={"enabled": True}, verify=False, timeout=30)
            if r.status_code == 200:
                print("  [OK] DPI enabled")
                changes.append("dpi:enabled")
            else:
                print(f"  [FAIL] DPI ({r.status_code}): {r.text[:100]}")
            break
    else:
        print("  ! DPI setting not found")
else:
    print(f"  Failed to get settings: {r.status_code}")

# 5. Multicast
print("\n[5/5] Multicast...")
for wlan in wlans:
    wlan_id = wlan['_id']
    name = wlan.get('name', 'unknown')
    r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}", 
                   json={"mcastenhance_enabled": True}, verify=False, timeout=30)
    if r.status_code == 200:
        print(f"  [OK] {name}: multicast ON")
        changes.append(f"multicast:{name}")
    else:
        print(f"  [FAIL] {name} ({r.status_code}): {r.text[:100]}")

print("\n" + "="*60)
print(f"COMPLETE: {len(changes)} changes made")
print("="*60)
for c in changes:
    print(f"  [OK] {c}")

# Save result
with open('tmp/unifi_phase1_result.json', 'w') as f:
    json.dump(changes, f, indent=2)
print(f"\nResult saved to tmp/unifi_phase1_result.json")
