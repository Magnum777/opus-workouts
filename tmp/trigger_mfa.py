import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Just trigger a login attempt to send fresh MFA code
console_ip = "192.241.248.242"
username = "nova.cofounder@gmail.com"
password = "Fr34k3r!123123"

session = requests.Session()

# Try login WITHOUT token — this should trigger MFA email
resp = session.post(
    f"https://{console_ip}/api/auth/login",
    json={"username": username, "password": password, "remember": True},
    timeout=15, verify=False
)

print(f"Status: {resp.status_code}")
print(f"Body: {resp.text[:500]}")

# If we got a 403 or 401, MFA was triggered
if resp.status_code == 401:
    print("\n✅ MFA code should be sent to nova.cofounder@gmail.com")
    print("Check your email for a 6-digit code from UniFi/SSO")
