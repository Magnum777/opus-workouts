import requests
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from vault_helper import get_credential

EVE_URL = get_credential('wordpress', 'eveonion_url')
EVE_USER = get_credential('wordpress', 'eveonion_user')
EVE_PASS = get_credential('wordpress', 'eveonion_pass')

import base64
auth = base64.b64encode(f'{EVE_USER}:{EVE_PASS}'.encode()).decode()
headers = {'Authorization': f'Basic {auth}', 'User-Agent': 'Mozilla/5.0'}
r = requests.get(f'{EVE_URL}/wp-json/wp/v2/media?per_page=30&orderby=date&order=desc', headers=headers)
items = r.json()
orphaned = []
attached = []
for item in items:
    post = item.get('post')
    fname = item['source_url'].split('/')[-1][:35]
    entry = f'ID {item["id"]} | post={post} | {fname}'
    if post is None:
        orphaned.append(entry)
    else:
        attached.append(entry)

print('ATTACHED:')
for a in attached:
    print(f'  {a}')
print()
print('ORPHANED:')
for o in orphaned:
    print(f'  {o}')