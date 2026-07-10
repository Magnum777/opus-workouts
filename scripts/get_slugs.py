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
headers = {'Authorization': f'Basic {auth}', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

post_ids = [25005, 25004, 25003, 24999, 24998, 24997, 24996, 24993]
for pid in post_ids:
    r = requests.get(f'{EVE_URL}/wp-json/wp/v2/posts/{pid}', headers=headers)
    if r.status_code == 200:
        d = r.json()
        slug = d.get('slug', 'N/A')
        link = d.get('link', 'N/A')
        print(f'ID {pid}: {slug}')
        print(f'  Link: {link}')
    else:
        print(f'ID {pid}: ERROR {r.status_code}')