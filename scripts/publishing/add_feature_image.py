import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from vault_helper import get_credential

import requests, base64, json

# WordPress credentials from vault
EVE_URL = get_credential('wordpress', 'eveonion_url')
EVE_USER = get_credential('wordpress', 'eveonion_user')
EVE_PASS = get_credential('wordpress', 'eveonion_pass')
WP_URL = f"{EVE_URL}/wp-json/wp/v2"
WP_AUTH = base64.b64encode(f"{EVE_USER}:{EVE_PASS}".encode()).decode()
WP_HEADERS = {
    "Authorization": f"Basic {WP_AUTH}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

# Upload image as media
image_path = r"C:\Users\compj\.openclaw\workspace\scripts\publishing\eveonion_feature_fenris.jpg"
with open(image_path, "rb") as f:
    image_data = f.read()

files = {
    "file": ("fenris-ai-capsuleers.jpg", image_data, "image/jpeg")
}

media_r = requests.post(f"{WP_URL}/media", headers={"Authorization": f"Basic {WP_AUTH}", "User-Agent": "Mozilla/5.0"}, files=files, timeout=30)
print(f"Upload: {media_r.status_code}")
if media_r.status_code in (200, 201):
    media_id = media_r.json().get("id")
    print(f"Media ID: {media_id}")

    # Assign to post
    post_r = requests.post(f"{WP_URL}/posts/24988", json={"featured_media": media_id}, headers=WP_HEADERS, timeout=15)
    print(f"Post update: {post_r.status_code}")
else:
    print(media_r.text[:200])
