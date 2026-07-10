import requests, base64, sys

from vault_helper import get_credential
sys.stdout.reconfigure(encoding='utf-8')

site = {
    'url': get_credential('wordpress', 'aicofounderstack_url') + '/wp-json/wp/v2',
    'user': get_credential('wordpress', 'aicofounderstack_user'),
    'pass': get_credential('wordpress', 'aicofounderstack_pass')
}
creds = f"{site['user']}:{site['pass']}".encode()
token = base64.b64encode(creds).decode()
headers = {
    'Authorization': f'Basic {token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Nova/1.0'
}

# Find the "Automation Marketplace" post
all_posts = []
page = 1
while True:
    r = requests.get(f"{site['url']}/posts", headers=headers,
                     params={'per_page': 100, 'status': 'publish', 'page': page}, timeout=30)
    if r.status_code != 200:
        break
    posts = r.json()
    if not posts:
        break
    all_posts.extend(posts)
    if len(posts) < 100:
        break
    page += 1

for p in all_posts:
    title = p['title']['rendered'].lower()
    if 'marketplace' in title or 'automation marketplace' in title:
        print(f"POST {p['id']}: {p['title']['rendered']}")
        content = p.get('content', {}).get('rendered', '')
        print(content[:3000])
        print('\n---')
