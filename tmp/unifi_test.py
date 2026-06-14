import requests

token = 'M_9VaI2JRSa4gWtFHzlA-rXK0r55m_KA'

# Test multiple header formats
headers_list = [
    ('Bearer auth', {'Authorization': f'Bearer {token}'}),
    ('X-Api-Key', {'X-Api-Key': token}),
    ('X-API-KEY', {'X-API-KEY': token}),
    ('api-key', {'api-key': token}),
]

for name, headers in headers_list:
    for endpoint in ['https://api.ui.com/ea/sites', 'https://api.ui.com/v2/sites', 'https://api.ui.com/sites']:
        try:
            resp = requests.get(endpoint, headers=headers, timeout=10)
            print(f'{name} -> {endpoint.split("/")[-2:]}: {resp.status_code}')
            if resp.status_code == 200:
                print(f'  SUCCESS: {len(resp.json().get("data", []))} sites')
        except Exception as e:
            print(f'{name} -> {endpoint}: ERROR {e}')

print('\n--- Testing with no trailing slash variations ---')

# Also try the direct console approach if it's a local controller
# Site Manager tokens usually start with M_ for member tokens
# Let's also try the unifi.local approach if applicable
