import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from vault_helper import get_credential

import requests, base64

EVE_URL = get_credential('wordpress', 'eveonion_url')
EVE_USER = get_credential('wordpress', 'eveonion_user')
EVE_PASS = get_credential('wordpress', 'eveonion_pass')

url = f'{EVE_URL}/wp-json/wp/v2/posts'
auth = base64.b64encode(f'{EVE_USER}:{EVE_PASS}'.encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json'
}

title = 'Ganker Posts Killmail Expecting Tears; Victim Responds With 45-Minute Tutorial on Emotional Maturity'

with open('scripts/eveonion/latest_article.html') as f:
    content = f.read()

post_data = {'title': title, 'content': content, 'status': 'publish', 'featured_media': 25043}
r = requests.post(url, json=post_data, headers=headers, timeout=15)
print(f'Status: {r.status_code}')
if r.status_code == 201:
    data = r.json()
    print(f'Post ID: {data.get("id")}')
    print(f'Link: {data.get("link")}')
else:
    print(f'Error: {r.text[:300]}')
