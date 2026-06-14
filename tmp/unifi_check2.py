import requests

headers = {'X-Api-Key': 'M_9VaI2JRSa4gWtFHzlA-rXK0r55m_KA'}
resp = requests.get('https://api.ui.com/ea/sites', headers=headers, timeout=15)
print(f'X-Api-Key response: {resp.status_code}')
if resp.status_code == 200:
    print(f'Sites: {len(resp.json().get("data", []))}')
else:
    print(resp.text[:300])
