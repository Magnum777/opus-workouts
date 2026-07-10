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
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# Check working vs non-working posts for theme-specific meta
posts = {
    25006: 'WORKING',
    25000: 'WORKING', 
    25005: 'NOT WORKING',
    25004: 'NOT WORKING',
    24999: 'NOT WORKING',
    24998: 'NOT WORKING',
    24997: 'NOT WORKING',
    24996: 'NOT WORKING',
    24993: 'NOT WORKING',
}
for pid, status in posts.items():
    r = requests.get(f'{EVE_URL}/wp-json/wp/v2/posts/{pid}', headers=headers)
    d = r.json()
    meta = d.get('meta', {})
    print(f'Post {pid} [{status}]:')
    print(f'  featured_media: {d.get("featured_media")}')
    print(f'  tdm_status: {meta.get("tdm_status")}')
    print(f'  tdm_grid_status: {meta.get("tdm_grid_status")}')
    print()