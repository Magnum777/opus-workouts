"""
UniFi Authentication v4 — Full SSO MFA with cookie
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

# Step 1: Initial login to trigger MFA
print("Step 1: Initial login...")
r = session.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": EMAIL, "password": PASSWORD, "remember": True},
    verify=False,
    timeout=30
)
print(f"Status: {r.status_code}")

if r.status_code == 200:
    print("Login successful!")
    sys.exit(0)

if r.status_code == 499:
    data = r.json()
    print("MFA required")
    
    # Get MFA code
    mfa_code = sys.argv[1] if len(sys.argv) > 1 else input("MFA code: ")
    
    # Extract the mfaCookie from response
    mfa_cookie = data.get('data', {}).get('mfaCookie', '')
    if mfa_cookie:
        # Parse and set cookie
        cookie_parts = mfa_cookie.split(';')
        cookie_name_value = cookie_parts[0].strip()
        print(f"Setting MFA cookie: {cookie_name_value[:50]}...")
        session.cookies.set('UBIC_2FA', cookie_name_value.split('=', 1)[1] if '=' in cookie_name_value else '')
    
    # Now verify MFA with the cookie
    print(f"\nStep 2: Verifying MFA with code {mfa_code}...")
    
    # The proper SSO MFA endpoint
    r2 = session.post(
        f"{BASE_URL}/api/auth/sso/verify-mfa",
        json={
            "token": mfa_code,
            "rememberMe": True
        },
        verify=False,
        timeout=30
    )
    print(f"Status: {r2.status_code}")
    print(f"Response: {r2.text[:500]}")
    
    if r2.status_code == 200:
        print("\n✓ MFA verified!")
        # Now login again with verified MFA
        print("\nStep 3: Final login...")
        r3 = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": EMAIL, "password": PASSWORD, "remember": True},
            verify=False,
            timeout=30
        )
        print(f"Login status: {r3.status_code}")
        
        if r3.status_code == 200:
            print("✓ LOGGED IN!")
            # Test device API
            r4 = session.get(
                f"{BASE_URL}/proxy/network/api/s/default/stat/device",
                verify=False,
                timeout=30
            )
            print(f"Device API: {r4.status_code}")
            if r4.status_code == 200:
                devices = r4.json().get('data', [])
                print(f"Found {len(devices)} devices")
                # Save session cookies for later use
                cookies = dict(session.cookies)
                print(f"\nSession cookies saved for API calls")
                with open('tmp/unifi_session.json', 'w') as f:
                    json.dump(cookies, f)
                print("Session saved to tmp/unifi_session.json")
    else:
        print(f"MFA verification failed: {r2.text[:500]}")
        
        # Try one more time with the raw mfaCookie header
        print("\nTrying with cookie header...")
        headers = {'Cookie': mfa_cookie} if mfa_cookie else {}
        r3 = session.post(
            f"{BASE_URL}/api/auth/verify-mfa",
            json={"token": mfa_code},
            headers=headers,
            verify=False,
            timeout=30
        )
        print(f"Alternative status: {r3.status_code}")
        print(f"Response: {r3.text[:500]}")
