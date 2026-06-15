"""
UniFi Auth + Phase 1 -- Full SSO MFA flow in one script
"""
import requests
import json
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EMAIL = "nova.cofounder@gmail.com"
PASSWORD = "Fr34k3r!123123"
BASE_URL = "https://192.241.248.242"

mfa_code = sys.argv[1] if len(sys.argv) > 1 else sys.exit("Usage: python unifi_full.py <MFA_CODE>")

session = requests.Session()

print("="*60)
print("UNIFI PHASE 1 -- REMOTE EXECUTION")
print("="*60)

# Step 1: Initial login to trigger MFA and get cookies
print("\n[1/3] Initial login (trigger MFA)...")
r1 = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": EMAIL, "password": PASSWORD, "remember": True},
    verify=False,
    timeout=30
)
print(f"Initial login status: {r1.status_code}")

if r1.status_code != 499:
    print(f"Unexpected response: {r1.text[:300]}")
    sys.exit(1)

print("MFA triggered. Got session cookies.")
print(f"Cookies after step 1: {dict(session.cookies)}")

# Step 2: Submit MFA code WITH the session cookies
print(f"\n[2/3] Submitting MFA code {mfa_code} with session...")
r2 = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": EMAIL, "password": PASSWORD, "token": mfa_code, "remember": True},
    verify=False,
    timeout=30
)
print(f"MFA submission status: {r2.status_code}")

if r2.status_code == 200:
    print("[OK] Authenticated!")
    print(f"Final cookies: {dict(session.cookies)}")
elif r2.status_code == 499:
    print("Still needs MFA -- code may have expired or already used")
    print(f"Response: {r2.text[:300]}")
    sys.exit(1)
else:
    print(f"Auth failed: {r2.text[:500]}")
    sys.exit(1)

# Step 3: Make changes
print("\n" + "="*60)
print("MAKING PHASE 1 CHANGES")
print("="*60)

changes = []

# Get WLANs
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan", verify=False, timeout=30)
wlans = r.json().get('data', []) if r.status_code == 200 else []
print(f"Found {len(wlans)} WLANs")

# 1. Band steering
print("\n[1/5] Band steering...")
for wlan in wlans:
    wlan_id = wlan['_id']
    r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan/{wlan_id}", 
                   json={"bandsteering_mode": "balanced"}, verify=False, timeout=30)
    if r.status_code == 200:
        print(f"  [OK] {wlan.get('name', 'unknown')}")
        changes.append(f"band_steering:{wlan.get('name')}")
    else:
        print(f"  [FAIL] {wlan.get('name')} ({r.status_code})")

# 2. Min RSSI
print("\n[2/5] Min RSSI -70...")
for wlan in wlans:
    wlan_id = wlan['_id']
    r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan/{wlan_id}", 
                   json={"min_rssi_enabled": True, "min_rssi": -70}, verify=False, timeout=30)
    if r.status_code == 200:
        print(f"  [OK] {wlan.get('name', 'unknown')}")
        changes.append(f"min_rssi:{wlan.get('name')}")
    else:
        print(f"  [FAIL] {wlan.get('name')} ({r.status_code})")

# 3. SAP 5GHz
print("\n[3/5] SAP 5GHz...")
r = session.get(f"{BASE_URL}/proxy/network/api/s/default/stat/device", verify=False, timeout=30)
if r.status_code == 200:
    devices = r.json().get('data', [])
    sap_found = False
    for d in devices:
        if d.get('name', '').upper() == 'SAP':
            sap_found = True
            device_id = d['_id']
            radio_table = d.get('radio_table', [{}, {}])
            if len(radio_table) > 1:
                radio_table[1]['channel'] = 149
                radio_table[1]['ht'] = 40
            r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/device/{device_id}", 
                          json={"radio_table": radio_table}, verify=False, timeout=30)
            if r.status_code == 200:
                print("  [OK] SAP: Ch 149 / 40MHz")
                changes.append("sap_5ghz:ch149_40mhz")
            else:
                print(f"  [FAIL] SAP failed ({r.status_code})")
            break
    if not sap_found:
        print("  ! SAP not found by name, trying model...")
        for d in devices:
            if 'UAP6MP' in str(d.get('model', '')):
                device_id = d['_id']
                radio_table = d.get('radio_table', [{}, {}])
                if len(radio_table) > 1:
                    radio_table[1]['channel'] = 149
                    radio_table[1]['ht'] = 40
                r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/device/{device_id}", 
                              json={"radio_table": radio_table}, verify=False, timeout=30)
                if r.status_code == 200:
                    print(f"  [OK] {d.get('name', 'UAP6MP')}: Ch 149 / 40MHz")
                    changes.append("sap_5ghz:ch149_40mhz")
                break

# 4. DPI
print("\n[4/5] DPI...")
r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/setting", 
               json={"dpi_enabled": True}, verify=False, timeout=30)
if r.status_code == 200:
    print("  [OK] DPI enabled")
    changes.append("dpi:enabled")
else:
    print(f"  [FAIL] DPI failed ({r.status_code})")

# 5. Multicast
print("\n[5/5] Multicast...")
for wlan in wlans:
    wlan_id = wlan['_id']
    r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan/{wlan_id}", 
                   json={"mcastenhance_enabled": True}, verify=False, timeout=30)
    if r.status_code == 200:
        print(f"  [OK] {wlan.get('name', 'unknown')}")
        changes.append(f"multicast:{wlan.get('name')}")
    else:
        print(f"  [FAIL] {wlan.get('name')} ({r.status_code})")

print("\n" + "="*60)
print(f"COMPLETE: {len(changes)} changes made")
print("="*60)
for c in changes:
    print(f"  [OK] {c}")
