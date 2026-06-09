import requests, base64

auth = base64.b64encode('nova:EVEONION_APP_PASSWORD_REDACTED'.encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# List recent media
r = requests.get('https://eveonion.com/wp-json/wp/v2/media?per_page=20&orderby=date&order=desc', headers=headers)
print(f'Status: {r.status_code}')
if r.status_code == 200:
    items = r.json()
    for item in items:
        print(f"  ID {item['id']} | {item['source_url'].split('/')[-1][:40]} | post={item.get('post', 'none')}")
else:
    print(f'Error: {r.text[:200]}')