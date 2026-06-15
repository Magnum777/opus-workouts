"""
UniFi Auth + Phase 1 — One-shot execution
Triggers MFA, waits for code, authenticates, makes changes
"""
import requests
import json
import sys
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EMAIL = "nova.cofounder@gmail.com"
PASSWORD = "Fr34k3r!123123"
BASE_URL = "https://192.241.248.242"

session = requests.Session()

print("="*60)
print("UNIFI PHASE 1 — REMOTE EXECUTION")
print("="*60)

# Step 1: Trigger MFA
print("\n[1/3] Triggering MFA...")
r = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": EMAIL, "password": PASSWORD, "remember": True},
    verify=False,
    timeout=30
)

if r.status_code == 200:
    print("Already authenticated!")
elif r.status_code == 499:
    print("MFA email sent to nova.cofounder@gmail.com")
    
    # Step 2: Get MFA code from user
    print("\n[2/3] Waiting for MFA code...")
    mfa_code = input("Enter MFA code from email: ").strip()
    
    # Step 3: Verify MFA
    print(f"\n[3/3] Verifying code {mfa_code}...")
    
    # Try multiple endpoints
    endpoints = [
        ("/api/auth/sso/verify-mfa", {"token": mfa_code, "rememberMe": True}),
        ("/api/auth/verify-mfa", {"token": mfa_code}),
        ("/api/auth/login", {"username": EMAIL, "password": PASSWORD, "token": mfa_code, "remember": True}),
    ]
    
    authenticated = False
    for endpoint, payload in endpoints:
        r2 = session.post(f"{BASE_URL}{endpoint}", json=payload, verify=False, timeout=30)
        print(f"  {endpoint}: {r2.status_code}")
        
        if r2.status_code == 200:
            print("  ✓ Authenticated!")
            authenticated = True
            break
    
    if not authenticated:
        print("\n✗ Authentication failed. Code may have expired.")
        print("Try again with a fresh code.")
        sys.exit(1)
    
    # Step 4: Make changes
    print("\n" + "="*60)
    print("MAKING PHASE 1 CHANGES")
    print("="*60)
    
    changes = []
    
    # Get WLANs
    r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan", verify=False, timeout=30)
    wlans = r.json().get('data', []) if r.status_code == 200 else []
    
    # 1. Band steering
    print("\n[1/5] Band steering...")
    for wlan in wlans:
        wlan_id = wlan['_id']
        r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan/{wlan_id}", 
                       json={"bandsteering_mode": "balanced"}, verify=False, timeout=30)
        if r.status_code == 200:
            print(f"  ✓ {wlan.get('name', 'unknown')}")
            changes.append(f"band_steering:{wlan.get('name')}")
    
    # 2. Min RSSI
    print("\n[2/5] Min RSSI -70...")
    for wlan in wlans:
        wlan_id = wlan['_id']
        r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan/{wlan_id}", 
                       json={"min_rssi_enabled": True, "min_rssi": -70}, verify=False, timeout=30)
        if r.status_code == 200:
            print(f"  ✓ {wlan.get('name', 'unknown')}")
            changes.append(f"min_rssi:{wlan.get('name')}")
    
    # 3. SAP 5GHz
    print("\n[3/5] SAP 5GHz...")
    r = session.get(f"{BASE_URL}/proxy/network/api/s/default/stat/device", verify=False, timeout=30)
    if r.status_code == 200:
        devices = r.json().get('data', [])
        for d in devices:
            if d.get('name', '').upper() == 'SAP':
                device_id = d['_id']
                # Get current radio config
                radio_table = d.get('radio_table', [{}, {}])
                radio_table[1]['channel'] = 149
                radio_table[1]['ht'] = 40
                r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/device/{device_id}", 
                              json={"radio_table": radio_table}, verify=False, timeout=30)
                if r.status_code == 200:
                    print("  ✓ SAP: Ch 149 / 40MHz")
                    changes.append("sap_5ghz:ch149_40mhz")
                break
    
    # 4. DPI
    print("\n[4/5] DPI...")
    r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/setting", 
                   json={"dpi_enabled": True}, verify=False, timeout=30)
    if r.status_code == 200:
        print("  ✓ DPI enabled")
        changes.append("dpi:enabled")
    
    # 5. Multicast
    print("\n[5/5] Multicast...")
    for wlan in wlans:
        wlan_id = wlan['_id']
        r = session.put(f"{BASE_URL}/proxy/network/api/s/default/rest/wlan/{wlan_id}", 
                       json={"mcastenhance_enabled": True}, verify=False, timeout=30)
        if r.status_code == 200:
            print(f"  ✓ {wlan.get('name', 'unknown')}")
            changes.append(f"multicast:{wlan.get('name')}")
    
    print("\n" + "="*60)
    print(f"COMPLETE: {len(changes)} changes made")
    print("="*60)
    for c in changes:
        print(f"  ✓ {c}")

else:
    print(f"Unexpected response: {r.status_code}")
    print(r.text[:500])
