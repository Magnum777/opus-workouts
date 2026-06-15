"""
UniFi Authentication v3 — SSO MFA flow with challenge
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

# Step 1: Initial login to trigger MFA and get challenge
print("Step 1: Initial login...")
r = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": EMAIL, "password": PASSWORD, "remember": True},
    verify=False,
    timeout=30
)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    print("Login successful! No MFA needed.")
    print(json.dumps(r.json(), indent=2)[:500])
    sys.exit(0)

if r.status_code == 499:
    data = r.json()
    print(f"MFA required. Authenticators: {data}")
    
    # Get MFA code
    mfa_code = sys.argv[1] if len(sys.argv) > 1 else input("Enter MFA code: ")
    
    # Try SSO MFA endpoint
    print(f"\nStep 2: SSO MFA verification with code {mfa_code}...")
    
    # The SSO MFA endpoint
    mfa_payload = {
        "username": EMAIL,
        "password": PASSWORD,
        "token": mfa_code,
        "rememberMe": True
    }
    
    r2 = session.post(
        f"{BASE_URL}/api/auth/sso-login",
        json=mfa_payload,
        verify=False,
        timeout=30
    )
    print(f"SSO Login status: {r2.status_code}")
    print(f"Response: {r2.text[:500]}")
    
    if r2.status_code == 200:
        print("\n✓ SSO Login successful!")
        # Now try device API
        r3 = session.get(
            f"{BASE_URL}/proxy/network/api/s/default/stat/device",
            verify=False,
            timeout=30
        )
        print(f"Device API: {r3.status_code}")
        if r3.status_code == 200:
            devices = r3.json().get('data', [])
            print(f"Found {len(devices)} devices")
    else:
        # Try alternative endpoint
        print("\nTrying alternative MFA endpoint...")
        r3 = session.post(
            f"{BASE_URL}/api/auth/verify-mfa",
            json={"token": mfa_code},
            verify=False,
            timeout=30
        )
        print(f"Verify MFA status: {r3.status_code}")
        print(f"Response: {r3.text[:500]}")
        
        if r3.status_code == 200:
            print("\n✓ MFA verified!")
            # Test device API
            r4 = session.get(
                f"{BASE_URL}/proxy/network/api/s/default/stat/device",
                verify=False,
                timeout=30
            )
            print(f"Device API: {r4.status_code}")
else:
    print(f"Unexpected: {r.text[:500]}")
