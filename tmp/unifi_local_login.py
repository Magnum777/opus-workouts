import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console_ip = "192.241.248.242"
password = "n20CQ9aRcvQdKCFf"

# Try different username formats
usernames = [
    "nova.cofounder@gmail.com",
    "nova.cofounder",
    "nova",
    "cofounder",
    "admin",
    "sojournchurchtech@gmail.com",
    "sojournchurchtech",
    "sojourn",
    "church",
]

session = requests.Session()

print("=== Testing Local Console Login ===")
print(f"Console: https://{console_ip}")
print(f"Password: {password[:4]}****")
print()

for username in usernames:
    try:
        resp = session.post(
            f"https://{console_ip}/api/auth/login",
            json={"username": username, "password": password, "remember": True},
            timeout=15,
            verify=False
        )
        status = "SUCCESS" if resp.status_code == 200 else f"{resp.status_code}"
        print(f"  {username:30s} -> {status}")
        if resp.status_code == 200:
            print(f"    Token: {resp.json().get('csrfToken', 'N/A')[:20]}...")
            # Try to get devices
            devices_resp = session.get(
                f"https://{console_ip}/proxy/network/api/s/default/stat/device",
                timeout=15,
                verify=False
            )
            if devices_resp.status_code == 200:
                devices = devices_resp.json().get('data', [])
                print(f"    DEVICES: {len(devices)}")
                for dev in devices[:3]:
                    print(f"      {dev.get('name', 'N/A')} ({dev.get('model', 'N/A')})")
            break
    except Exception as e:
        print(f"  {username:30s} -> ERROR: {str(e)[:50]}")
