"""
UniFi local admin -- try variations
"""
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://192.241.248.242"

# Try different password variations
attempts = [
    ("nova", "N0v4!123N0v4!123"),
    ("nova", "N0v4!123N0v4!"),
    ("nova", "N0v4!123"),
    ("nova", "N0v4!123123"),
    ("Nova", "N0v4!123N0v4!123"),
    ("nova.cofounder@gmail.com", "N0v4!123N0v4!123"),
]

for username, password in attempts:
    print(f"Trying {username} / {password[:10]}...")
    session = requests.Session()
    r = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password},
        verify=False,
        timeout=30
    )
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        print("  [OK] SUCCESS!")
        print(f"  Working creds: {username} / {password}")
        break
    else:
        print(f"  Failed: {r.text[:100]}")
