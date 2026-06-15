"""
UniFi Authentication v2 — Proper SSO + MFA flow
"""
import requests
import json
import sys

EMAIL = "nova.cofounder@gmail.com"
PASSWORD = "Fr34k3r!123123"
BASE_URL = "https://192.241.248.242"

session = requests.Session()

# Step 1: Initial login to trigger MFA
print("Step 1: Initial login...")
login_data = {
    "username": EMAIL,
    "password": PASSWORD,
    "remember": True
}

r = session.post(
    f"{BASE_URL}/api/auth/login",
    json=login_data,
    verify=False,
    timeout=30
)
print(f"Status: {r.status_code}")
print(f"Headers: {dict(r.headers)}")

if r.status_code == 200:
    print("Login successful (no MFA needed?)")
    print(r.json())
elif r.status_code == 499 or "MFA" in r.text.upper():
    print("MFA required. Need to submit MFA code.")
    
    # Try submitting MFA
    mfa_code = sys.argv[1] if len(sys.argv) > 1 else input("MFA code: ")
    
    mfa_data = {
        "username": EMAIL,
        "password": PASSWORD,
        "token": mfa_code,
        "remember": True
    }
    
    print(f"\nStep 2: Submitting MFA code {mfa_code}...")
    r2 = session.post(
        f"{BASE_URL}/api/auth/login",
        json=mfa_data,
        verify=False,
        timeout=30
    )
    print(f"Status: {r2.status_code}")
    print(f"Response: {r2.text[:500]}")
    
    if r2.status_code == 200:
        print("\nLogin successful!")
        print(f"Session cookies: {dict(session.cookies)}")
        
        # Test with a simple API call
        print("\nTesting API access...")
        r3 = session.get(
            f"{BASE_URL}/proxy/network/api/s/default/stat/device",
            verify=False,
            timeout=30
        )
        print(f"Devices API status: {r3.status_code}")
        if r3.status_code == 200:
            print("SUCCESS! API authenticated.")
        else:
            print(f"Failed: {r3.text[:200]}")
    else:
        print(f"MFA submission failed: {r2.text[:500]}")
else:
    print(f"Unexpected response: {r.text[:500]}")
