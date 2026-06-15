"""
UniFi Phase 1 — Make changes with correct API paths
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

print("Authenticated session loaded")
changes = []

# 1. Get WLANs and update band steering
print("\n[1/5] Band steering...")
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf", verify=False, timeout=30)
if r.status_code == 200:
    wlans = r.json().get('data', [])
    print(f"Found {len(wlans)} WLANs")
    for wlan in wlans:
        wlan_id = wlan['_id']
        name = wlan.get('name', 'unknown')
        # Update band steering
        r2 = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}", 
                        json={"bandsteering_mode": "balanced"}, verify=False, timeout=30)
        if r2.status_code == 200:
            print(f"  [OK] {name}: band steering ON")
            changes.append(f"band_steering:{name}")
        else:
            print(f"  [FAIL] {name} ({r2.status_code}): {r2.text[:100]}")

# 2. Min RSSI
print("\n[2/5] Min RSSI -70...")
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf", verify=False, timeout=30)
if r.status_code == 200:
    wlans = r.json().get('data', [])
    for wlan in wlans:
        wlan_id = wlan['_id']
        name = wlan.get('name', 'unknown')
        r2 = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}", 
                        json={"min_rssi_enabled": True, "min_rssi": -70}, verify=False, timeout=30)
        if r2.status_code == 200:
            print(f"  [OK] {name}: min RSSI -70")
            changes.append(f"min_rssi:{name}")
        else:
            print(f"  [FAIL] {name} ({r2.status_code}): {r2.text[:100]}")

# 3. SAP 5GHz channel
print("\n[3/5] SAP 5GHz...")
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/stat/device", verify=False, timeout=30)
if r.status_code == 200:
    devices = r.json().get('data', [])
    for d in devices:
        if d.get('name', '').upper() == 'SAP':
            device_id = d['_id']
            mac = d.get('mac', '')
            print(f"Found SAP: {d.get('name')} ({mac})")
            
            # Use cmd/devmgr to set channel
            r2 = session.post(f"{BASE_URL}/proxy/network/api/s/default/cmd/devmgr", 
                            json={
                                "cmd": "set-config",
                                "mac": mac,
                                "radio_table": [
                                    {},
                                    {"channel": 149, "ht": 40}
                                ]
                            }, verify=False, timeout=30)
            if r2.status_code == 200:
                print("  [OK] SAP: Ch 149 / 40MHz")
                changes.append("sap_5ghz:ch149_40mhz")
            else:
                print(f"  [FAIL] SAP ({r2.status_code}): {r2.text[:100]}")
            break
    else:
        print("  ! SAP not found")

# 4. DPI - Try to find the setting
print("\n[4/5] DPI...")
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/setting", verify=False, timeout=30)
if r.status_code == 200:
    settings = r.json().get('data', [])
    dpi_setting = None
    for s in settings:
        if s.get('key') == 'dpi':
            dpi_setting = s
            break
    
    if dpi_setting:
        setting_id = dpi_setting['_id']
        r2 = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/setting/{setting_id}", 
                        json={"enabled": True}, verify=False, timeout=30)
        if r2.status_code == 200:
            print("  [OK] DPI enabled")
            changes.append("dpi:enabled")
        else:
            print(f"  [FAIL] DPI ({r2.status_code}): {r2.text[:100]}")
    else:
        print("  ! DPI setting not found")

# 5. Multicast enhancement
print("\n[5/5] Multicast...")
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf", verify=False, timeout=30)
if r.status_code == 200:
    wlans = r.json().get('data', [])
    for wlan in wlans:
        wlan_id = wlan['_id']
        name = wlan.get('name', 'unknown')
        r2 = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}", 
                        json={"mcastenhance_enabled": True}, verify=False, timeout=30)
        if r2.status_code == 200:
            print(f"  [OK] {name}: multicast ON")
            changes.append(f"multicast:{name}")
        else:
            print(f"  [FAIL] {name} ({r2.status_code}): {r2.text[:100]}")

print("\n" + "="*60)
print(f"COMPLETE: {len(changes)} changes made")
print("="*60)
for c in changes:
    print(f"  [OK] {c}")
