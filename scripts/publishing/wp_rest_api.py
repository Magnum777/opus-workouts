#!/usr/bin/env python3
"""WordPress REST API helper for publishing.
Plain text output (no emojis) to avoid Unicode errors on Windows.

Usage:
    python wp_rest_api.py <site> create --title "..." --content "..."
    python wp_rest_api.py <site> update <post_id> --status publish
"""

import argparse
import base64
import json
import requests
import subprocess
import sys
import urllib.parse
from pathlib import Path

# Add scripts/ to path so vault_helper is importable when run from workspace root
sys.path.insert(0, str(Path(__file__).parent.parent))
from vault_helper import get_credential

# Site configs loaded from vault (P0 fix applied 2026-07-10)
SITES = {
    'aitoolalliance.com': {
        'url': get_credential('wordpress', 'aitoolalliance_url') + '/wp-json/wp/v2',
        'user': get_credential('wordpress', 'aitoolalliance_user'),
        'pass': get_credential('wordpress', 'aitoolalliance_pass')
    },
    'aibusinessinsider.org': {
        'url': get_credential('wordpress', 'aibusinessinsider_url') + '/wp-json/wp/v2',
        'user': get_credential('wordpress', 'aibusinessinsider_user'),
        'pass': get_credential('wordpress', 'aibusinessinsider_pass')
    },
    'aicofounderstack.com': {
        'url': get_credential('wordpress', 'aicofounderstack_url') + '/wp-json/wp/v2',
        'user': get_credential('wordpress', 'aicofounderstack_user'),
        'pass': get_credential('wordpress', 'aicofounderstack_pass')
    },
    'eveonion.com': {
        'url': get_credential('wordpress', 'eveonion_url') + '/wp-json/wp/v2',
        'user': get_credential('wordpress', 'eveonion_user'),
        'pass': get_credential('wordpress', 'eveonion_pass')
    }
}

def _auth(user: str, password: str) -> dict[str, str]:
    creds = f"{user}:{password}".encode()
    token = base64.b64encode(creds).decode()
    return {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

def list_posts(site_key: str, search: str = None, status: str = None, per_page: int = 10) -> list:
    site = SITES.get(site_key)
    if not site:
        print(f"Unknown site: {site_key}")
        return []
    headers = _auth(site['user'], site['pass'])
    url = f"{site['url']}/posts"
    params = {'per_page': per_page}
    if search:
        params['search'] = search
    if status:
        params['status'] = status
    r = requests.get(url, headers=headers, params=params)
    if r.status_code == 200:
        return r.json()
    else:
        print(f"Error listing posts: {r.status_code} {r.text[:200]}")
        return []

def create_post(site_key: str, title: str, content: str, status: str = 'publish', slug: str = None) -> int:
    site = SITES.get(site_key)
    if not site:
        print(f"Unknown site: {site_key}")
        return 0
    headers = _auth(site['user'], site['pass'])
    url = f"{site['url']}/posts"
    data = {'title': title, 'content': content, 'status': status}
    if slug:
        data['slug'] = slug
    r = requests.post(url, headers=headers, json=data)
    if r.status_code in (200, 201):
        return r.json().get('id', 0)
    else:
        print(f"Error creating post: {r.status_code} {r.text[:200]}")
        return 0

def update_post(site_key: str, post_id: int, status: str = None, featured_media: int = None) -> bool:
    site = SITES.get(site_key)
    if not site:
        print(f"Unknown site: {site_key}")
        return False
    headers = _auth(site['user'], site['pass'])
    url = f"{site['url']}/posts/{post_id}"
    data = {}
    if status:
        data['status'] = status
    if featured_media is not None:
        data['featured_media'] = featured_media
    r = requests.post(url, headers=headers, json=data)
    if r.status_code in (200, 201):
        return True
    else:
        print(f"Error updating post: {r.status_code} {r.text[:200]}")
        return False

def upload_media(site_key: str, file_path: str, alt: str = '') -> int:
    site = SITES.get(site_key)
    if not site:
        print(f"Unknown site: {site_key}")
        return 0
    headers = _auth(site['user'], site['pass'])
    url = f"{site['url']}/media"
    headers.pop('Content-Type', None)
    with open(file_path, 'rb') as f:
        files = {'file': (Path(file_path).name, f)}
        r = requests.post(url, headers=headers, files=files, data={'alt_text': alt})
    if r.status_code in (200, 201):
        return r.json().get('id', 0)
    else:
        print(f"Error uploading media: {r.status_code} {r.text[:200]}")
        return 0

if __name__ == '__main__':
    from pathlib import Path
    parser = argparse.ArgumentParser(description='WordPress REST API helper')
    parser.add_argument('site', choices=list(SITES.keys()), help='Site to target')
    parser.add_argument('action', choices=['list', 'create', 'update', 'upload'], help='Action to perform')
    parser.add_argument('--title', help='Post title')
    parser.add_argument('--content', help='Post content')
    parser.add_argument('--status', default='publish', help='Post status')
    parser.add_argument('--post-id', type=int, help='Post ID to update')
    parser.add_argument('--file', help='File path for upload')
    parser.add_argument('--alt', default='', help='Alt text for media')
    parser.add_argument('--search', help='Search term for listing')
    parser.add_argument('--per-page', type=int, default=10, help='Posts per page')
    args = parser.parse_args()

    if args.action == 'list':
        posts = list_posts(args.site, search=args.search, per_page=args.per_page)
        for p in posts:
            print(f"{p['id']}: {p['title']['rendered']} ({p['status']})")
    elif args.action == 'create':
        pid = create_post(args.site, args.title, args.content, args.status)
        print(f"Created post ID: {pid}")
    elif args.action == 'update':
        ok = update_post(args.site, args.post_id, args.status)
        print(f"Update {'OK' if ok else 'FAILED'}")
    elif args.action == 'upload':
        mid = upload_media(args.site, args.file, args.alt)
        print(f"Media ID: {mid}")
