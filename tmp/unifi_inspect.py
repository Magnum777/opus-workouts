import requests
import json

headers = {'X-Api-Key': 'M_9VaI2JRSa4gWtFHzlA-rXK0r55m_KA'}

resp = requests.get('https://api.ui.com/ea/sites', headers=headers, timeout=15)
if resp.status_code == 200:
    sites = resp.json()
    print(f'Keys in response: {list(sites.keys())}')
    data = sites.get('data', [])
    print(f'\nSites: {len(data)}')
    for i, site in enumerate(data):
        print(f'\n--- Site {i+1} ---')
        print(f'Keys: {list(site.keys())}')
        print(json.dumps(site, indent=2)[:1500])
