import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console_ip = "192.241.248.242"
username = "nova.cofounder@gmail.com"
password = "Fr34k3r!123123"

session = requests.Session()

print("=== UniFi Console Login ===")
print(f"Console: https://{console_ip}")
print(f"Username: {username}")
print()

try:
    resp = session.post(
        f"https://{console_ip}/api/auth/login",
        json={"username": username, "password": password, "remember": True},
        timeout=15,
        verify=False
    )
    print(f"Login response: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"SUCCESS!")
        print(f"Token: {data.get('csrfToken', 'N/A')[:20]}...")
        print(f"Role: {data.get('role', 'N/A')}")
        print(f"Is Admin: {data.get('isAdmin', False)}")
        
        # Now get devices
        print("\n=== Fetching Devices ===")
        devices_resp = session.get(
            f"https://{console_ip}/proxy/network/api/s/default/stat/device",
            timeout=15,
            verify=False
        )
        if devices_resp.status_code == 200:
            devices = devices_resp.json().get('data', [])
            print(f"Found {len(devices)} devices")
            for dev in devices:
                print(f"  {dev.get('name', 'Unknown')} ({dev.get('model', 'Unknown')})")
                print(f"    MAC: {dev.get('mac', 'N/A')}")
                print(f"    IP: {dev.get('ip', 'N/A')}")
                print(f"    Status: {'Online' if dev.get('adopted') and not dev.get('disconnected') else 'Issue'}")
                print(f"    Clients: {dev.get('num_sta', 0)}")
                print(f"    Channel: {dev.get('radio_table', [{}])[0].get('channel', 'N/A') if dev.get('radio_table') else 'N/A'}")
                print(f"    Channel Width: {dev.get('radio_table', [{}])[0].get('ht', 'N/A') if dev.get('radio_table') else 'N/A'}")
                print(f"    Tx Retries: {dev.get('stat', {}).get('tx_retries', 0)}")
                print()
        else:
            print(f"Failed to get devices: {devices_resp.status_code}")
            print(devices_resp.text[:500])
    else:
        print(f"Login failed: {resp.status_code}")
        print(resp.text[:500])
except Exception as e:
    print(f"Error: {e}")
