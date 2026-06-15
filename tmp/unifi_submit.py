"""
Submit MFA code with saved session
"""
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EMAIL = "nova.cofounder@gmail.com"
PASSWORD = "Fr34k3r!123123"
BASE_URL = "https://192.241.248.242"
MFA_CODE = "993375"

# Load saved session cookies
with open('tmp/unifi_session_cookies.json', 'r') as f:
    cookies = json.load(f)

session = requests.Session()
for name, value in cookies.items():
    session.cookies.set(name, value)

print(f"Loaded session cookies: {dict(session.cookies)}")

# Submit MFA with existing session
print(f"\nSubmitting MFA code {MFA_CODE}...")
r = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": EMAIL, "password": PASSWORD, "token": MFA_CODE, "remember": True},
    verify=False,
    timeout=30
)

print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

if r.status_code == 200:
    print("\n[OK] AUTHENTICATED!")
    print(f"Final cookies: {dict(session.cookies)}")
    # Save final authenticated session
    with open('tmp/unifi_authenticated.json', 'w') as f:
        json.dump(dict(session.cookies), f)
    print("Saved authenticated session")
    
    # Now make Phase 1 changes
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
else:
    print("\n[FAIL] Authentication failed")
    print("The code may have expired during the delay.")
    print("Check your console - you may already be logged in.")
