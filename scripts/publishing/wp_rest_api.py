#!/usr/bin/env python3
"""WordPress REST API helper for publishing.
Plain text output (no emojis) to avoid Unicode errors on Windows.
"""

import argparse, requests, base64, json, sys, subprocess, urllib.parse

# Site configs (application passwords)
SITES = {
    'aitoolalliance.com': {
        'url': 'https://aitoolalliance.com/wp-json/wp/v2',
        'user': 'aitoolalliance_u6cbhe',
        'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>
    },
    'aibusinessinsider.org': {
        'url': 'https://aibusinessinsider.org/wp-json/wp/v2',
        'user': 'nova.cofounder@gmail.com',
        'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>
    },
    'aicofounderstack.com': {
        'url': 'https://aicofounderstack.com/wp-json/wp/v2',
        'user': 'nova',
        'pass': 'DUau yrXK 1X8k O6eH YL5v qKID'
    },
    'eveonion.com': {
        'url': 'https://eveonion.com/wp-json/wp/v2',
        'user': 'nova',
        'pass': 'EVEONION_APP_PASSWORD_REDACTED'
    }
}

def _auth(user, password):
    creds = f"{user}:{password}".encode()
    token = base64.b64encode(creds).decode()
    return {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

def list_posts(site_key, search=None, status=None, per_page=10):
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
        print(f"Error: {r.status_code} - {r.text}")
        return []

def update_post(site_key, post_id, title=None, content=None, status=None):
    site = SITES.get(site_key)
    if not site:
        print(f"Unknown site: {site_key}")
        return None
    headers = _auth(site['user'], site['pass'])
    url = f"{site['url']}/posts/{post_id}"
    data = {}
    if title: data['title'] = title
    if content: data['content'] = content
    if status: data['status'] = status
    r = requests.post(url, headers=headers, json=data)
    if r.status_code in (200, 201):
        res = r.json()
        print(f"[OK] Updated: {res.get('link')}")
        return res
    else:
        print(f"[ERROR] {r.status_code} - {r.text}")
        return None

def _run_research(site_key):
    """Research step for AI sites.
    - Pulls latest topics from Reddit's r/ArtificialIntelligence.
    - For each topic, prints a Brave search URL (placeholder for further processing).
    Returns True on success, False on failure.
    """
    ai_sites = {'aitoolalliance.com', 'aibusinessinsider.org'}
    if site_key not in ai_sites:
        return True  # skip non‑AI sites
    # Fetch recent Reddit posts
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get('https://www.reddit.com/r/ArtificialIntelligence/new.json?limit=5', headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        posts = data.get('data', {}).get('children', [])
        if not posts:
            print(f"[RESEARCH] No Reddit posts found for {site_key}")
            return True
        print(f"[RESEARCH] Latest Reddit AI topics for {site_key}:")
        for p in posts:
            title = p.get('data', {}).get('title', '(no title)')
            print(f"  - {title}")
            query = urllib.parse.quote_plus(title)
            search_url = f"https://search.brave.com/search?q={query}"
            print(f"    [SEARCH] Brave results: {search_url}")
        return True
    except Exception as e:
        print(f"[RESEARCH ERROR] Failed to fetch Reddit topics for {site_key}: {e}")
        return False

def create_post(site_key, title, content, status='publish'):
    # Run research first; abort if it fails.
    if not _run_research(site_key):
        print(f"[ABORT] Research failed for {site_key}, not publishing.")
        return None
    site = SITES.get(site_key)
    if not site:
        print(f"Unknown site: {site_key}")
        return None
    headers = _auth(site['user'], site['pass'])
    url = f"{site['url']}/posts"
    data = {'title': title, 'content': content, 'status': status}
    r = requests.post(url, headers=headers, json=data)
    if r.status_code == 201:
        res = r.json()
        print(f"[OK] Created: {res.get('link')}")
        return res
    else:
        print(f"[ERROR] {r.status_code} - {r.text}")
        return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WP REST helper')
    parser.add_argument('site', choices=SITES.keys())
    parser.add_argument('action', choices=['list','update','create'])
    parser.add_argument('--search')
    parser.add_argument('--post-id', type=int)
    parser.add_argument('--title')
    parser.add_argument('--content')
    parser.add_argument('--status', choices=['publish','draft','private'])
    args = parser.parse_args()
    if args.action == 'list':
        posts = list_posts(args.site, args.search)
        for p in posts:
            print(f"ID:{p['id']} | {p['title']['rendered'][:50]}... | {p['status']}")
    elif args.action == 'update':
        if not args.post_id:
            print('--post-id required')
            sys.exit(1)
        update_post(args.site, args.post_id, args.title, args.content, args.status)
    elif args.action == 'create':
        if not args.title or not args.content:
            print('--title and --content required')
            sys.exit(1)
        create_post(args.site, args.title, args.content, args.status or 'publish')
