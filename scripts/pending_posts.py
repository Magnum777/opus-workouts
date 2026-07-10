import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from vault_helper import get_credential

import requests, base64

EVE_URL = get_credential('wordpress', 'eveonion_url')
EVE_USER = get_credential('wordpress', 'eveonion_user')
EVE_PASS = get_credential('wordpress', 'eveonion_pass')

auth = base64.b64encode(f'{EVE_USER}:{EVE_PASS}'.encode()).decode()
r = requests.get(
    f'{EVE_URL}/wp-json/wp/v2/posts?per_page=20&orderby=date&order=desc',
    headers={'Authorization': f'Basic {auth}', 'User-Agent': 'Mozilla/5.0'},
    timeout=10
)
posts = r.json()
print('All posts with featured images:')
for p in posts:
    fm = p.get('featured_media', 'none')
    title = p['title']['rendered']
    print(f'ID {p["id"]} | featured_media={fm} | {title[:70]}')
