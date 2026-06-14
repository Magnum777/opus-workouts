import requests
import json

headers = {
    'Authorization': 'Bearer M_9VaI2JRSa4gWtFHzlA-rXK0r55m_KA',
    'Content-Type': 'application/json'
}

print("Testing UniFi Site Manager API...")

# Get sites
try:
    resp = requests.get('https://api.ui.com/ea/sites', headers=headers, timeout=15)
    print(f'Response code: {resp.status_code}')
    if resp.status_code == 200:
        sites = resp.json()
        data = sites.get('data', [])
        print(f'Found {len(data)} sites:')
        for site in data:
            print(f'  Name: {site.get("name", "N/A")}')
            print(f'  Host: {site.get("host_name", "N/A")}')
            print(f'  Type: {site.get("type", "N/A")}')
            print(f'  ID: {site.get("_id", "N/A")[:8]}...')
            print('---')
    else:
        print(f'Error: {resp.status_code} - {resp.text[:500]}')
except Exception as e:
    print(f'Error: {e}')
