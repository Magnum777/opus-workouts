import requests, base64, sys
sys.stdout.reconfigure(encoding='utf-8')

site = {
    'url': 'https://aicofounderstack.com/wp-json/wp/v2',
    'user': 'nova',
    'pass': 'DUau yrXK 1X8k O6eH YL5v qKID'
}
creds = f"{site['user']}:{site['pass']}".encode()
token = base64.b64encode(creds).decode()
headers = {
    'Authorization': f'Basic {token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Nova/1.0'
}

# Update default comment settings
r = requests.post(f"{site['url']}/settings", headers=headers,
                json={'default_comment_status': 'closed', 'default_ping_status': 'closed'},
                timeout=30)
print(f'Settings update: HTTP {r.status_code}')
if r.status_code in (200, 201):
    print('Default comment status set to closed')
    print('Default ping status set to closed')
else:
    print(f'Response: {r.text[:200]}')
