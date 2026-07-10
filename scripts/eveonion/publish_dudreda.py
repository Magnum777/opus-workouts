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

with open('eveonion/articles/2026-07-04-strait-of-dudreda-propaganda-war.md') as f:
    content = f.read()

lines = content.split('\n')
html_parts = []
for line in lines:
    if line.startswith('**') and '—' in line:
        html_parts.append(f'<p><strong>{line.replace("**","")} — </p>')
        continue
    if line.startswith('#') or line.startswith('---') or line.startswith('*EVE Onion'):
        continue
    if line.startswith('*'):
        html_parts.append(f'<p><em>{line[1:].strip()}</em></p>')
        continue
    if line.strip() == '':
        continue
    html_parts.append(f'<p>{line}</p>')

title = "Propaganda War Escalates in Strait of Dudreda as Both Sides Claim Victory in 7v1 Gank"

data = {
    'title': title,
    'content': '\n'.join(html_parts),
    'status': 'publish',
    'slug': 'strait-of-dudreda-propaganda-war',
}

r = requests.post(url, headers=headers, json=data, timeout=30)
print(f'Create: {r.status_code}')
if r.status_code in (200, 201):
    print(f'Post ID: {r.json().get("id")}')
else:
    print(r.text[:300])
