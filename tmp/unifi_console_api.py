import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {'X-Api-Key': 'M_9VaI2JRSa4gWtFHzlA-rXK0r55m_KA'}
host_id = '192bddb3-1b82-4096-82df-1c71631154a3'

# Try console's API through site manager
for endpoint in [
    f'https://api.ui.com/ea/hosts/{host_id}/api/s/default/stat/device',
    f'https://api.ui.com/ea/hosts/{host_id}/api/s/default/rest/device',
    f'https://api.ui.com/ea/hosts/{host_id}/api/s/default/stat/sta',
    f'https://api.ui.com/ea/hosts/{host_id}/api/s/default/stat/health',
]:
    resp = requests.get(endpoint, headers=headers, timeout=15)
    print(f'{endpoint.split("/")[-4:]}: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json().get('data', [])
        print(f'  SUCCESS: {len(data)} items')
        # Show first few
        for item in data[:3]:
            print(f'    {item.get("name", item.get("model", "N/A"))} - {item.get("mac", "N/A")}')
    print()

# Try direct console
print('--- Trying direct console ---')
resp = requests.get('https://192.241.248.242/proxy/network/api/s/default/stat/device', 
                    headers=headers, timeout=15, verify=False)
print(f'Direct console: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json().get('data', [])
    print(f'  SUCCESS: {len(data)} devices')
