"""
Content-Nova WordPress Publisher v2
REST API publisher for Layered Media LLC WordPress sites.
Supports: aitoolalliance.com | aibusinessinsider.org | aicofounderstack.com
"""

import requests, base64, json, sys, os
from pathlib import Path

# Site configs -- TODO: move to env vars or 1Password
SITES = {
    'aitoolalliance.com': {
        'url': 'https://aitoolalliance.com/wp-json/wp/v2',
        'user': 'aitoolalliance_u6cbhe',
        'pass': 'PXop SzVQ b6wX IAyr FSig 8ZfL',
        'focus': 'AI tools, productivity software, automation'
    },
    'aibusinessinsider.org': {
        'url': 'https://aibusinessinsider.org/wp-json/wp/v2',
        'user': 'nova.cofounder@gmail.com',
        'pass': 'sDLx Ja22 YxcI QAok gu8u xRXI',
        'focus': 'AI business strategy, enterprise AI, market analysis'
    },
    'aicofounderstack.com': {
        'url': 'https://aicofounderstack.com/wp-json/wp/v2',
        'user': 'nova',
        'pass': 'DUau yrXK 1X8k O6eH YL5v qKID',
        'focus': 'AI cofounders, startup tools, solopreneur resources'
    }
}

def _auth(user, password):
    creds = f"{user}:{password}".encode()
    token = base64.b64encode(creds).decode()
    return {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'ContentNovaBot/2.0'
    }

def list_posts(site_key, per_page=5, status='publish'):
    site = SITES.get(site_key)
    if not site:
        return {'error': f'Unknown site: {site_key}'}
    headers = _auth(site['user'], site['pass'])
    url = f"{site['url']}/posts"
    r = requests.get(url, headers=headers, params={'per_page': per_page, 'status': status}, timeout=30)
    if r.status_code == 200:
        return r.json()
    return {'error': f'HTTP {r.status_code}', 'detail': r.text[:200]}

def create_post(site_key, title, content, status='draft', excerpt=None, categories=None, tags=None):
    """Publish a post. Returns dict with 'id', 'link', or 'error'."""
    site = SITES.get(site_key)
    if not site:
        return {'error': f'Unknown site: {site_key}'}
    headers = _auth(site['user'], site['pass'])
    url = f"{site['url']}/posts"
    data = {
        'title': title,
        'content': content,
        'status': status,
        'excerpt': excerpt or ''
    }
    if categories:
        data['categories'] = categories
    if tags:
        data['tags'] = tags
    r = requests.post(url, headers=headers, json=data, timeout=60)
    if r.status_code in (200, 201):
        res = r.json()
        return {'ok': True, 'id': res.get('id'), 'link': res.get('link')}
    return {'error': f'HTTP {r.status_code}', 'detail': r.text[:500]}

def update_post(site_key, post_id, title=None, content=None, status=None):
    site = SITES.get(site_key)
    if not site:
        return {'error': f'Unknown site: {site_key}'}
    headers = _auth(site['user'], site['pass'])
    url = f"{site['url']}/posts/{post_id}"
    data = {}
    if title: data['title'] = title
    if content: data['content'] = content
    if status: data['status'] = status
    r = requests.post(url, headers=headers, json=data, timeout=30)
    if r.status_code in (200, 201):
        res = r.json()
        return {'ok': True, 'id': res.get('id'), 'link': res.get('link')}
    return {'error': f'HTTP {r.status_code}', 'detail': r.text[:500]}

def get_latest_post_date(site_key):
    """Returns ISO date string of most recent published post."""
    posts = list_posts(site_key, per_page=1)
    if isinstance(posts, list) and len(posts) > 0:
        return posts[0].get('date')
    return None

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('site', choices=list(SITES.keys()))
    parser.add_argument('action', choices=['list','create','update','latest'])
    parser.add_argument('--title')
    parser.add_argument('--content')
    parser.add_argument('--status', default='draft')
    parser.add_argument('--post-id', type=int)
    args = parser.parse_args()

    if args.action == 'list':
        for p in list_posts(args.site):
            print(f"ID:{p['id']} | {p['title']['rendered'][:60]} | {p['status']}")
    elif args.action == 'latest':
        print(get_latest_post_date(args.site))
    elif args.action == 'create':
        if not args.title or not args.content:
            print('--title and --content required')
            sys.exit(1)
        res = create_post(args.site, args.title, args.content, args.status)
        print(json.dumps(res, indent=2))
    elif args.action == 'update':
        if not args.post_id:
            print('--post-id required')
            sys.exit(1)
        res = update_post(args.site, args.post_id, args.title, args.content, args.status)
        print(json.dumps(res, indent=2))
