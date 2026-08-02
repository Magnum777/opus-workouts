#!/usr/bin/env python3
"""Internal link builder for OpenClaw WordPress sites.

Scans published posts across all 3 sites and adds internal links
between related articles. Boosts SEO cross-traffic.

Usage:
  python internal_link_builder.py [--site <site|all>] [--dry-run] [--max-links 3]

Logic:
1. Fetch recent posts from each site (last 30 days)
2. For each post, find related posts on other sites by keyword matching
3. Insert 2-3 internal links per post (to other sites in our network)
4. Update the post via WordPress REST API
5. Log changes to post log
"""

import sys
import json
import argparse
import re
from pathlib import Path
from datetime import datetime, timedelta

import requests

sys.path.insert(0, str(Path(__file__).parent))
from creds import get_wp_site, get_wp_auth_header

SITES = {
    'aitoolalliance': 'https://www.aitoolalliance.com',
    'aibusinessinsider': 'https://www.aibusinessinsider.org',
    'aicofounderstack': 'https://www.aicofounderstack.com',
}

# Keywords that signal related content
LINK_KEYWORDS = {
    'aitoolalliance': ['ai tool', 'ai software', 'automation', 'productivity', 'ai app',
                       'free ai', 'ai platform', 'chatgpt alternative', 'ai writing',
                       'ai image', 'ai video', 'ai code', 'ai assistant'],
    'aibusinessinsider': ['business strategy', 'enterprise ai', 'ai adoption', 'startup',
                          'funding', 'revenue', 'saas', 'b2b', 'ai market', 'industry',
                          'corporate', 'leadership', 'scaling', 'growth'],
    'aicofounderstack': ['solo founder', 'startup', 'no-code', 'low-code', 'bootstrapper',
                         'founder', 'indie hacker', 'side project', 'mvp', 'business model',
                         'launch', 'productivity', 'automation'],
}

MAX_LINKS_PER_POST = 3
DAYS_BACK = 30


def fetch_posts(site_name, days=DAYS_BACK):
    """Fetch recent posts from a site."""
    site = get_wp_site(site_name)
    if not site:
        print(f"Unknown site: {site_name}")
        return []

    headers = get_wp_auth_header(site_name)
    headers['User-Agent'] = 'Nova-LinkBuilder/1.0'

    after = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%dT00:00:00')
    url = f"{site['url']}/wp-json/wp/v2/posts?per_page=50&after={after}&status=publish"

    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f"ERROR: {site_name} returned HTTP {resp.status_code}")
            return []
        return resp.json()
    except Exception as e:
        print(f"ERROR fetching {site_name}: {e}")
        return []


def extract_keywords(text, site_name):
    """Extract matching keywords from post content."""
    text_lower = text.lower()
    found = []
    for kw in LINK_KEYWORDS.get(site_name, []):
        if kw in text_lower:
            found.append(kw)
    return found


def find_related_posts(post, all_posts_by_site, source_site, max_links=MAX_LINKS_PER_POST):
    """Find related posts from other sites for internal linking."""
    title = (post.get('title', {}).get('rendered', '') or '').lower()
    content = (post.get('content', {}).get('rendered', '') or '').lower()
    source_keywords = extract_keywords(title + ' ' + content, source_site)

    if not source_keywords:
        return []

    candidates = []
    for site_name, posts in all_posts_by_site.items():
        if site_name == source_site:
            continue  # Only cross-site links
        for candidate in posts:
            c_title = (candidate.get('title', {}).get('rendered', '') or '').lower()
            c_content = (candidate.get('content', {}).get('rendered', '') or '').lower()
            c_keywords = extract_keywords(c_title + ' ' + c_content, site_name)

            # Score: how many keywords overlap
            overlap = len(set(source_keywords) & set(c_keywords))
            if overlap > 0:
                candidates.append({
                    'site': site_name,
                    'post_id': candidate['id'],
                    'title': candidate.get('title', {}).get('rendered', ''),
                    'url': candidate.get('link', ''),
                    'score': overlap,
                })

    # Sort by relevance, take top max_links
    candidates.sort(key=lambda x: x['score'], reverse=True)
    return candidates[:max_links]


def insert_links(content, related_posts):
    """Insert internal links into post content HTML.

    Strategy: Add a "Related Reading" section at the end with links.
    This is less intrusive than modifying existing content.
    """
    if not related_posts:
        return content, []

    # Check if "Related Reading" section already exists
    if 'related reading' in content.lower() or 'related articles' in content.lower():
        return content, []  # Don't duplicate

    links_html = []
    added = []
    for rp in related_posts:
        clean_title = re.sub(r'<[^>]+>', '', rp['title']).strip()
        link = f'<li><a href="{rp["url"]}">{clean_title}</a> ({rp["site"].replace("aitoolalliance", "AI Tool Alliance").replace("aibusinessinsider", "AI Business Insider").replace("aicofounderstack", "AI Cofounder Stack")})</li>'
        links_html.append(link)
        added.append(rp)

    if not links_html:
        return content, []

    related_section = f'\n\n<h2>Related Reading</h2>\n<ul>\n' + '\n'.join(links_html) + '\n</ul>'
    return content + related_section, added


def update_post(site_name, post_id, content, headers):
    """Update a post via WordPress REST API."""
    site = get_wp_site(site_name)
    url = f"{site['url']}/wp-json/wp/v2/posts/{post_id}"

    resp = requests.post(url, headers=headers, json={'content': content}, timeout=30)
    if resp.status_code == 200:
        return True
    else:
        print(f"  ERROR updating {site_name} post {post_id}: HTTP {resp.status_code}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Build internal links across WordPress sites')
    parser.add_argument('--site', default='all', help='Site name or "all"')
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without updating')
    parser.add_argument('--max-links', type=int, default=MAX_LINKS_PER_POST, help='Max links per post')
    parser.add_argument('--days', type=int, default=DAYS_BACK, help='How many days back to fetch')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    sites = list(SITES.keys()) if args.site == 'all' else [args.site]

    # Fetch all posts
    all_posts = {}
    for site in sites:
        print(f"Fetching {site}...")
        all_posts[site] = fetch_posts(site, days=args.days)
        print(f"  {len(all_posts[site])} posts found")

    # Also fetch from sites not in --site for cross-linking
    for site in SITES:
        if site not in all_posts:
            all_posts[site] = fetch_posts(site, days=args.days)

    # Find and insert links
    results = []
    total_added = 0

    for site in sites:
        headers = get_wp_auth_header(site)
        headers['User-Agent'] = 'Nova-LinkBuilder/1.0'
        headers['Content-Type'] = 'application/json'

        for post in all_posts[site]:
            related = find_related_posts(post, all_posts, site, max_links=args.max_links)
            if not related:
                continue

            content = post.get('content', {}).get('rendered', '')
            new_content, added = insert_links(content, related)

            if not added:
                continue

            title = re.sub(r'<[^>]+>', '', post.get('title', {}).get('rendered', '')).strip()
            result = {
                'site': site,
                'post_id': post['id'],
                'title': title,
                'links_added': len(added),
                'linked_to': [{'site': r['site'], 'title': re.sub(r'<[^>]+>', '', r['title']).strip(), 'url': r['url']} for r in added],
            }
            results.append(result)
            total_added += len(added)

            if args.dry_run:
                print(f"  [DRY] {site} #{post['id']}: {title[:60]} -> {len(added)} links")
                for r in added:
                    print(f"    -> {r['site']}: {re.sub(r'<[^>]+>', '', r['title']).strip()[:50]}")
            else:
                success = update_post(site, post['id'], new_content, headers)
                status = "OK" if success else "FAIL"
                print(f"  [{status}] {site} #{post['id']}: {title[:60]} -> {len(added)} links")

    print(f"\nTotal: {total_added} links added across {len(results)} posts")

    if args.json:
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()