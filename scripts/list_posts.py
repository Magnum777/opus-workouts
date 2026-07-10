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
r = requests.get(
    f'{EVE_URL}/wp-json/wp/v2/posts?per_page=10&orderby=date&order=desc',
    headers={
        'Authorization': f'Basic {auth}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    },
    timeout=10
)
posts = r.json()
print(f'Found {len(posts)} posts:')
for p in posts:
    fm = p.get('featured_media', 0)
    print(f'ID {p["id"]} | {"HAS" if fm else "NO "} IMG | {p["date"][:10]} | {p["title"]["rendered"][:55]}')