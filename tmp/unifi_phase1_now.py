"""
UniFi Phase 1 -- Single script, single session
Usage: python unifi_phase1_now.py
Then enter MFA code when prompted
"""
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EMAIL = "nova.cofounder@gmail.com"
PASSWORD = "Fr34k3r!123123"
BASE_URL = "https://192.241.248.242"

session = requests.Session()

print("="*60)
print("UNIFI PHASE 1")
print("="*60)

# Step 1: Trigger MFA
print("\n[1/3] Triggering MFA...")
r1 = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": EMAIL, "password": PASSWORD, "remember": True},
    verify=False,
    timeout=30
)

if r1.status_code == 499:
    print("MFA email sent. Enter code below:")
elif r1.status_code == 200:
    print("Already logged in!")
else:
    print(f"Error: {r1.status_code} - {r1.text[:200]}")
    exit(1)

# Step 2: Get MFA code from user
mfa_code = input("MFA code: ").strip()

# Step 3: Login with MFA (SAME session)
print(f"\n[2/3] Authenticating with {mfa_code}...")
r2 = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": EMAIL, "password": PASSWORD, "token": mfa_code, "remember": True},
    verify=False,
    timeout=30
)

if r2.status_code == 200:
    print("[OK] Authenticated!")
else:
    print(f"[FAIL] Auth failed: {r2.status_code} - {r2.text[:200]}")
    exit(1)

# Step 4: Make changes
print("\n[3/3] Making changes...")
changes = []

# Get WLANs
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf", verify=False, timeout=30)
if r.status_code == 200:
    wlans = r.json().get('data', [])
    print(f"Found {len(wlans)} WLANs")
    
    for wlan in wlans:
        wlan_id = wlan['_id']
        name = wlan.get('name', 'unknown')
        
        # Band steering
        r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}",
                       json={"bandsteering_mode": "balanced"}, verify=False, timeout=30)
        if r.status_code == 200:
            print(f"  [OK] {name}: band steering")
            changes.append(f"band_steering:{name}")
        else:
            print(f"  [FAIL] {name}: band steering ({r.status_code})")
        
        # Min RSSI
        r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}",
                       json={"min_rssi_enabled": True, "min_rssi": -70}, verify=False, timeout=30)
        if r.status_code == 200:
            print(f"  [OK] {name}: min RSSI -70")
            changes.append(f"min_rssi:{name}")
        else:
            print(f"  [FAIL] {name}: min RSSI ({r.status_code})")
        
        # Multicast
        r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}",
                       json={"mcastenhance_enabled": True}, verify=False, timeout=30)
        if r.status_code == 200:
            print(f"  [OK] {name}: multicast")
            changes.append(f"multicast:{name}")
        else:
            print(f"  [FAIL] {name}: multicast ({r.status_code})")

# SAP 5GHz
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/stat/device", verify=False, timeout=30)
if r.status_code == 200:
    devices = r.json().get('data', [])
    for d in devices:
        if d.get('name', '').upper() == 'SAP':
            radio_table = d.get('radio_table', [{}, {}])
            if len(radio_table) > 1:
                radio_table[1]['channel'] = 149
                radio_table[1]['ht'] = 40
            r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/device/{d['_id']}",
                          json={"radio_table": radio_table}, verify=False, timeout=30)
            if r.status_code == 200:
                print(f"  [OK] SAP: Ch 149 / 40MHz")
                changes.append("sap_5ghz:ch149_40mhz")
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
                print(f"  [OK] DPI enabled")
                changes.append("dpi:enabled")
            else:
                print(f"  [FAIL] DPI ({r.status_code})")
            break

print(f"\n{'='*60}")
print(f"COMPLETE: {len(changes)} changes made")
print(f"{'='*60}")
for c in changes:
    print(f"  [OK] {c}")
