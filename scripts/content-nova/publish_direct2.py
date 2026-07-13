"""Direct publish to aicofounderstack.com via REST API."""
import sys, json, base64, requests
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts')
from vault_helper import get_credential

user = get_credential('wordpress', 'aicofounderstack_user')
pwd = get_credential('wordpress', 'aicofounderstack_pass')

with open(r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\article-draft.md', 'r') as f:
    content = f.read()

lines = content.strip().split('\n', 1)
title = lines[0].replace('# ', '').strip()
body = lines[1].strip()

url = 'https://www.aicofounderstack.com'
creds = f'{user}:{pwd}'.encode()
token = base64.b64encode(creds).decode()
headers = {
    'Authorization': f'Basic {token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

data = {
    'title': title,
    'content': body,
    'status': 'publish',
    'excerpt': 'Solo founders are using AI cofounder tools to build million-dollar businesses without human cofounders. Here are the best platforms in 2026 and how they work.'
}

r = requests.post(f'{url}/wp-json/wp/v2/posts', headers=headers, json=data, timeout=60)
print(f'Status: {r.status_code}')
if r.status_code in (200, 201):
    res = r.json()
    post_id = res['id']
    link = res['link']
    print(f'SUCCESS! Post ID: {post_id}')
    print(f'Link: {link}')
    with open(r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\last_post_id.txt', 'w') as f:
        f.write(str(post_id))
else:
    print(f'Error: {r.text[:1000]}')
