"""
UniFi local admin authentication and Phase 1 changes
"""
import requests
import json
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERNAME = "nova"
PASSWORD = "N0v4!123N0v4!123"
BASE_URL = "https://192.241.248.242"

session = requests.Session()

print("="*60)
print("UNIFI PHASE 1 -- LOCAL ADMIN AUTH")
print("="*60)

# Step 1: Login with local credentials (no MFA needed)
print("\n[1/2] Logging in with local admin...")
r = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": USERNAME, "password": PASSWORD},
    verify=False,
    timeout=30
)

print(f"Login status: {r.status_code}")

if r.status_code != 200:
    print(f"Login failed: {r.text[:500]}")
    sys.exit(1)

print("[OK] Authenticated as local admin!")
print(f"Cookies: {dict(session.cookies)}")

# Save authenticated session
with open('tmp/unifi_local_authenticated.json', 'w') as f:
    json.dump(dict(session.cookies), f)
print("Session saved")

# Try with the SSO token we already have, but for a UDM/cloud controller
# the API path might be different

# First try to re-authenticate with the working SSO but use the correct API endpoint
print("\nTrying SSO auth with correct paths...")

EMAIL = "nova.cofounder@gmail.com"
PASSWORD = "Fr34k3r!123123"

# Trigger MFA again to get a fresh session
r = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": EMAIL, "password": PASSWORD, "remember": True},
    verify=False,
    timeout=30
)

if r.status_code == 499:
    print("MFA required. Need fresh code.")
elif r.status_code == 200:
    print("SSO logged in!")
    
    # Now try changes with this session
    print("\nTrying band steering...")
    r = session.get(f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf", verify=False, timeout=30)
    print(f"WLAN list: {r.status_code}")
    if r.status_code == 200:
        wlans = r.json().get('data', [])
        print(f"Found {len(wlans)} WLANs")
        for wlan in wlans:
            print(f"  - {wlan.get('name')} (ID: {wlan['_id'][:8]}...)")
        
        # Try update with session cookies
        if wlans:
            wlan_id = wlans[0]['_id']
            r2 = session.put(
                f"{BASE_URL}/proxy/network/api/s/default/rest/wlanconf/{wlan_id}",
                json={"bandsteering_mode": "balanced"},
                verify=False,
                timeout=30
            )
            print(f"\nBand steering update: {r2.status_code}")
            print(f"Response: {r2.text[:200]}")
else:
    print(f"Unexpected: {r.status_code} - {r.text[:200]}")
