import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from vault_helper import get_credential

import requests, base64

EVE_URL = get_credential('wordpress', 'eveonion_url')
EVE_USER = get_credential('wordpress', 'eveonion_user')
EVE_PASS = get_credential('wordpress', 'eveonion_pass')

auth = base64.b64encode(f'{EVE_USER}:{EVE_PASS}'.encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, */*',
    'Content-Type': 'application/json'
}

DEFAULT_IMAGE_ID = 25043

# Posts that need fixing
post_ids = [25079, 25080, 25081, 25082, 25083]

for pid in post_ids:
    r = requests.post(f'{EVE_URL}/wp-json/wp/v2/posts/{pid}',
                      json={'featured_media': DEFAULT_IMAGE_ID}, headers=headers, timeout=15)
    status = 'OK' if r.status_code in (200, 201) else r.text[:100]
    print(f'Post {pid}: {r.status_code} {status}')
