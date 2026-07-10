#!/usr/bin/env python3
"""Fix duplicate titles on 2 published aicofounderstack articles."""
import requests, base64, re, os

from vault_helper import get_credential

SITE = {
    "url": "https://www.aicofounderstack.com",
    "user": get_credential("wordpress", "aicofounderstack_user"),
    "pass": get_credential("wordpress", "aicofounderstack_pass")
}

# Post IDs from URLs
POSTS = [
    ("how-i-built-a-49-ai-product-in-48-hours-step-by-step", 31),  # adjust ID if wrong
    ("ai-agents-vs-traditional-saas-why-the-future-is-autonomous", 30)
]

auth = base64.b64encode(f"{SITE['user']}:{SITE['pass']}".encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Get actual post IDs from slugs
base = f"{SITE['url']}/wp-json/wp/v2/posts"

for slug, _ in POSTS:
    # Find post ID by slug
    r = requests.get(f"{base}?slug={slug}", headers=headers, timeout=30)
    if r.status_code == 200 and r.json():
        post = r.json()[0]
        post_id = post['id']
        content = post['content']['rendered']
        # Strip first h1 if it's duplicate of title
        title = post['title']['rendered']
        # Simple regex to remove first h1 matching title
        new_content = re.sub(
            f'^\s*<h[12][^>]*>.*?(?:{re.escape(title)}).*?</h[12]>\s*',
            '',
            content,
            count=1,
            flags=re.IGNORECASE | re.DOTALL
        )
        if new_content != content:
            update = requests.post(f"{base}/{post_id}", json={'content': new_content}, headers=headers, timeout=30)
            if update.status_code == 200:
                print(f"Fixed: {slug}")
            else:
                print(f"FAIL {slug}: HTTP {update.status_code}")
        else:
            print(f"No fix needed (or couldn't match): {slug}")
    else:
        print(f"Could not find: {slug}")
