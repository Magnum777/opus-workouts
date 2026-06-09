import requests, base64, re, sys
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

r = requests.get(f"{site['url']}/posts/34", headers=headers, timeout=30)
p = r.json()
content = p.get('content', {}).get('rendered', '')

print('POST 34 content (first 3000 chars):')
print(content[:3000])
print('\n---')
print('Contains <ul>:', '<ul>' in content)
print('Contains <li>:', '<li>' in content)
print('Contains p+en-dash:', '<p>\u2013' in content)
