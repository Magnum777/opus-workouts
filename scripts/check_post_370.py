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

# Check post 370 (the TradeBot monthly review)
r = requests.get(f"{site['url']}/posts/370", headers=headers, timeout=30)
p = r.json()
content = p.get('content', {}).get('rendered', '')

print('POST 370 - TradeBot Monthly Review:')
print(content[:4000])
print('\n---')
print('Has byline:', '<strong>Author:' in content)
