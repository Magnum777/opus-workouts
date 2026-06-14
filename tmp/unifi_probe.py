import requests
import json

headers = {'X-Api-Key': 'M_9VaI2JRSa4gWtFHzlA-rXK0r55m_KA'}
site_id = '63753636922fab0fb7676937'

def api_get(path):
    url = f'https://api.ui.com/ea/sites/{site_id}{path}'
    resp = requests.get(url, headers=headers, timeout=20)
    if resp.status_code == 200:
        return resp.json()
    print(f'  ERROR {resp.status_code}: {resp.text[:150]}')
    return None

# Try different device endpoints
for endpoint in ['/devices', '/stat/device', '/rest/device']:
    print(f'Testing endpoint: {endpoint}')
    result = api_get(endpoint)
    if result and result.get('data'):
        print(f'  SUCCESS: {len(result["data"])} items')
        break

# Try client endpoints  
for endpoint in ['/clients', '/stat/sta']:
    print(f'Testing endpoint: {endpoint}')
    result = api_get(endpoint)
    if result and result.get('data'):
        print(f'  SUCCESS: {len(result["data"])} items')
        break

# Try wlan endpoints
for endpoint in ['/wlans', '/rest/wlanconf', '/stat/wlanconf']:
    print(f'Testing endpoint: {endpoint}')
    result = api_get(endpoint)
    if result and result.get('data'):
        print(f'  SUCCESS: {len(result["data"])} items')
        break

# Try health
print(f'Testing endpoint: /health')
result = api_get('/health')
if result:
    print(f'  SUCCESS: {len(result.get("data", []))} items')
