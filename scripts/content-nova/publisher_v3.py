"""
WordPress Publisher v3 — wordpress-api-pro Integration
Replaces publisher.py with production-grade REST API.
Supports: aitoolalliance.com | aibusinessinsider.org | aicofounderstack.com
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# WordPress API Pro skill path
WP_PRO_DIR = Path(r'C:\Users\compj\.openclaw\workspace\skills\wordpress-api-pro')
SCRIPTS_DIR = WP_PRO_DIR / 'scripts'

# Site configs using application passwords (safer than basic auth)
SITES = {
    'aitoolalliance.com': {
        'url': 'https://aitoolalliance.com',
        'user': 'aitoolalliance_u6cbhe',
        'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>,
    },
    'aibusinessinsider.org': {
        'url': 'https://aibusinessinsider.org',
        'user': 'nova.cofounder@gmail.com',
        'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>,
    },
    'aicofounderstack.com': {
        'url': 'https://aicofounderstack.com',
        'user': 'nova',
        'pass': 'DUau yrXK 1X8k O6eH YL5v qKID',
    }
}

def _setup_env(site_key):
    """Set environment variables for wordpress-api-pro scripts."""
    site = SITES.get(site_key)
    if not site:
        raise ValueError(f"Unknown site: {site_key}")
    
    env = os.environ.copy()
    env['WP_URL'] = site['url']
    env['WP_USERNAME'] = site['user']
    env['WP_APP_PASSWORD'] = site['pass']
    return env

def _run_script(script_name, args, site_key=None):
    """Run a wordpress-api-pro script with proper env."""
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return {'error': f'Script not found: {script_path}'}
    
    env = None
    if site_key:
        env = _setup_env(site_key)
    
    cmd = [sys.executable, str(script_path)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {'ok': True, 'output': result.stdout}
    else:
        return {'error': f'Script failed', 'stderr': result.stderr[:500], 'stdout': result.stdout[:500]}


# === ContentNova API ===

def list_posts(site_key, per_page=5, status='publish'):
    """List recent posts. Returns list of post dicts."""
    result = _run_script('list_posts.py', [
        '--per-page', str(per_page),
        '--status', status
    ], site_key)
    
    if 'error' in result:
        return result
    
    # Parse output (list_posts.py prints formatted text)
    # Fall back to API call if script output is text-based
    import requests
    import base64
    
    site = SITES.get(site_key)
    creds = f"{site['user']}:{site['pass']}".encode()
    token = base64.b64encode(creds).decode()
    headers = {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
    }
    url = f"{site['url']}/wp-json/wp/v2/posts"
    r = requests.get(url, headers=headers, params={'per_page': per_page, 'status': status}, timeout=30)
    if r.status_code == 200:
        return r.json()
    return {'error': f'HTTP {r.status_code}', 'detail': r.text[:200]}

def create_post(site_key, title, content, status='draft', excerpt=None, categories=None, tags=None):
    """Create a new post. Returns dict with 'id', 'link', or 'error'."""
    import requests
    import base64
    
    site = SITES.get(site_key)
    if not site:
        return {'error': f'Unknown site: {site_key}'}
    
    creds = f"{site['user']}:{site['pass']}".encode()
    token = base64.b64encode(creds).decode()
    headers = {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    url = f"{site['url']}/wp-json/wp/v2/posts"
    
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
    """Update an existing post."""
    import requests
    import base64
    
    site = SITES.get(site_key)
    if not site:
        return {'error': f'Unknown site: {site_key}'}
    
    creds = f"{site['user']}:{site['pass']}".encode()
    token = base64.b64encode(creds).decode()
    headers = {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    url = f"{site['url']}/wp-json/wp/v2/posts/{post_id}"
    
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


# === New Features from wordpress-api-pro ===

def set_seo_meta(site_key, post_id, title=None, description=None, keywords=None):
    """Set SEO meta using wordpress-api-pro seo_meta.py."""
    args = ['--post-id', str(post_id)]
    if title:
        args.extend(['--meta-title', title])
    if description:
        args.extend(['--meta-description', description])
    if keywords:
        args.extend(['--meta-keywords', keywords])
    
    return _run_script('seo_meta.py', args, site_key)

def upload_media(site_key, file_path):
    """Upload media to WordPress."""
    args = ['--file', str(file_path)]
    return _run_script('upload_media.py', args, site_key)

def site_audit(site_key):
    """Run no-auth site audit (PageSpeed, SSL, security headers)."""
    return _run_script('site_audit.py', [], site_key)

def detect_plugins(site_key):
    """Detect installed plugins and SEO stack."""
    return _run_script('detect_plugins.py', [], site_key)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='WordPress Publisher v3')
    parser.add_argument('site', choices=list(SITES.keys()))
    parser.add_argument('action', choices=['list','create','update','latest','audit','plugins'])
    parser.add_argument('--title')
    parser.add_argument('--content')
    parser.add_argument('--status', default='draft')
    parser.add_argument('--post-id', type=int)
    parser.add_argument('--file')
    args = parser.parse_args()

    if args.action == 'list':
        for p in list_posts(args.site):
            if isinstance(p, dict):
                print(f"ID:{p['id']} | {p['title']['rendered'][:60]} | {p['status']}")
            else:
                print(p)
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
    elif args.action == 'audit':
        res = site_audit(args.site)
        print(json.dumps(res, indent=2))
    elif args.action == 'plugins':
        res = detect_plugins(args.site)
        print(json.dumps(res, indent=2))
