import requests
import json

headers = {'X-Api-Key': 'M_9VaI2JRSa4gWtFHzlA-rXK0r55m_KA'}

# Get hosts
resp = requests.get('https://api.ui.com/ea/hosts', headers=headers, timeout=15)
hosts = resp.json().get('data', [])

for host in hosts:
    hid = host.get('id')
    htype = host.get('type', 'unknown')
    state = host.get('reportedState', {}).get('state', 'unknown')
    name = host.get('reportedState', {}).get('name', 'unknown')
    fw = host.get('reportedState', {}).get('firmware_version', 'unknown')
    version = host.get('reportedState', {}).get('version', 'unknown')
    ip = host.get('ipAddress', 'unknown')
    
    print(f'\n=== HOST: {name} ===')
    print(f'  ID: {hid}')
    print(f'  Type: {htype}')
    print(f'  State: {state}')
    print(f'  IP: {ip}')
    print(f'  Firmware: {fw}')
    print(f'  Version: {version}')
    print(f'  Hostname: {host.get("reportedState", {}).get("hostname", "N/A")}')
    print(f'  Inform Port: {host.get("reportedState", {}).get("inform_port", "N/A")}')
    print(f'  Mgmt Port: {host.get("reportedState", {}).get("mgmt_port", "N/A")}')
    print(f'  IP Addrs: {host.get("reportedState", {}).get("ipAddrs", [])}')
    
    # Try getting devices for this host
    print(f'\n  Trying device endpoints...')
    for endpoint in [f'/hosts/{hid}/devices', f'/hosts/{hid}/sites/default/devices']:
        url = f'https://api.ui.com/ea{endpoint}'
        r = requests.get(url, headers=headers, timeout=15)
        print(f'    {endpoint}: {r.status_code}')
        if r.status_code == 200:
            data = r.json().get('data', [])
            print(f'      SUCCESS: {len(data)} devices')
            for dev in data[:5]:
                print(f'        {dev.get("name", "N/A")} ({dev.get("model", "N/A")}) - {dev.get("mac", "N/A")}')
            break
