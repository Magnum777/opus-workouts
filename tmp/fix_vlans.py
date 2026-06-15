import json, requests, urllib3
urllib3.disable_warnings()

session = requests.Session()
with open('tmp/unifi_local_working.json', 'r') as f:
    cookies = json.load(f)
for name, value in cookies.items():
    session.cookies.set(name, value)

BASE_URL = 'https://192.241.248.242/proxy/network/api/s/default'

# Step 1: Unassign SSIDs from VLAN networks back to Default
print("Step 1: Unassigning SSIDs from VLAN networks...")
ssid_fixes = [
    {"_id": "63753939922fab0fb76769a8", "name": "sojourn", "networkconf_id": "63753641922fab0fb7676948"},
    {"_id": "63753955922fab0fb76769a9", "name": "sojourn-office", "networkconf_id": "63753641922fab0fb7676948"},
    {"_id": "63753978922fab0fb76769ab", "name": "sojourn-guest", "networkconf_id": "63753641922fab0fb7676948"}
]

for ssid in ssid_fixes:
    r = session.put(f'{BASE_URL}/rest/wlanconf/{ssid["_id"]}', json=ssid, verify=False, timeout=15)
    print(f'  {ssid["name"]}: {r.status_code}')

# Step 2: Delete existing VLAN-only networks
print("\nStep 2: Deleting existing VLAN networks...")
vlan_ids = [
    "6a2f7984d638bc9db7aa7871",  # sojourn-office
    "6a2f79d0d638bc9db7aa7874",  # sojourn
    "6a2f79d3d638bc9db7aa7877",  # sojourn-guest
]

for vid in vlan_ids:
    r = session.delete(f'{BASE_URL}/rest/networkconf/{vid}', verify=False, timeout=15)
    print(f'  Delete {vid}: {r.status_code}')

# Step 3: Try creating corporate networks with networkgroup explicitly set
print("\nStep 3: Creating corporate VLAN networks...")
networks = [
    {"name": "sojourn-office", "vlan": 10, "purpose": "corporate", "networkgroup": "LAN", 
     "ip_subnet": "192.168.10.1/24", "dhcpd_start": "192.168.10.10", "dhcpd_stop": "192.168.10.250", 
     "dhcpd_enabled": True, "vlan_enabled": True, "site_id": "63753636922fab0fb7676937"},
    {"name": "sojourn", "vlan": 20, "purpose": "corporate", "networkgroup": "LAN", 
     "ip_subnet": "192.168.20.1/24", "dhcpd_start": "192.168.20.10", "dhcpd_stop": "192.168.20.250", 
     "dhcpd_enabled": True, "vlan_enabled": True, "site_id": "63753636922fab0fb7676937"},
    {"name": "sojourn-guest", "vlan": 30, "purpose": "corporate", "networkgroup": "LAN", 
     "ip_subnet": "192.168.30.1/24", "dhcpd_start": "192.168.30.10", "dhcpd_stop": "192.168.30.250", 
     "dhcpd_enabled": True, "vlan_enabled": True, "site_id": "63753636922fab0fb7676937"}
]

new_ids = {}
for net in networks:
    r = session.post(f'{BASE_URL}/rest/networkconf', json=net, verify=False, timeout=15)
    print(f'  Create {net["name"]} (VLAN {net["vlan"]}): {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        if 'data' in data and len(data['data']) > 0:
            new_ids[net["name"]] = data['data'][0]['_id']
            print(f'    -> ID: {data["data"][0]["_id"]}')
    else:
        print(f'    -> Error: {r.text[:200]}')

# Step 4: Assign SSIDs to new networks
if new_ids:
    print("\nStep 4: Assigning SSIDs to new networks...")
    ssid_assignments = [
        {"_id": "63753939922fab0fb76769a8", "name": "sojourn", "networkconf_id": new_ids.get("sojourn")},
        {"_id": "63753955922fab0fb76769a9", "name": "sojourn-office", "networkconf_id": new_ids.get("sojourn-office")},
        {"_id": "63753978922fab0fb76769ab", "name": "sojourn-guest", "networkconf_id": new_ids.get("sojourn-guest")}
    ]
    
    for ssid in ssid_assignments:
        if ssid["networkconf_id"]:
            r = session.put(f'{BASE_URL}/rest/wlanconf/{ssid["_id"]}', json=ssid, verify=False, timeout=15)
            print(f'  {ssid["name"]}: {r.status_code}')

print("\nDone!")
