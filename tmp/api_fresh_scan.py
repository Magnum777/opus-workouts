import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Try REST API with API key
console_ip = "192.241.248.242"
api_key = "M_9VaI2JRSa4gWtFHzlA-rXK0r55m_KA"

headers = {
    "Accept": "application/json",
    "X-API-KEY": api_key,
}

endpoints = [
    ("Sites", "/proxy/network/api/self/sites"),
    ("Devices", "/proxy/network/api/s/default/stat/device"),
    ("Clients", "/proxy/network/api/s/default/stat/sta"),
    ("WLAN Config", "/proxy/network/api/s/default/rest/wlanconf"),
    ("Rogue APs", "/proxy/network/api/s/default/stat/rogueap"),
]

for name, path in endpoints:
    url = f"https://{console_ip}{path}"
    print(f"\n=== {name} ===")
    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            print(f"Records: {len(data)}")
            if name == "Sites":
                for s in data:
                    print(f"  Site: {s.get('name', 'N/A')} ({s.get('desc', 'N/A')})")
                    print(f"    Health: {s.get('health', 'N/A')}")
                    print(f"    Guests: {s.get('num_guest', 0)}")
                    print(f"    Adopted: {s.get('num_adopted', 0)}")
            elif name == "Devices":
                for dev in data:
                    print(f"  {dev.get('name', 'N/A')}: {dev.get('num_sta', 0)} clients, Ch 2.4:{dev.get('channel', 'N/A')}/{dev.get('ht', 'N/A')}, 5:{dev.get('channel', 'N/A')}/{dev.get('ht', 'N/A')}, FW:{dev.get('version', 'N/A')}")
            elif name == "Clients":
                print(f"  Total: {len(data)}")
                ap_counts = {}
                for c in data:
                    ap = c.get('ap_mac', 'Unknown')
                    ap_counts[ap] = ap_counts.get(ap, 0) + 1
                for ap, count in sorted(ap_counts.items(), key=lambda x: -x[1]):
                    print(f"  {ap}: {count} clients")
        else:
            print(f"Error: {resp.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")
