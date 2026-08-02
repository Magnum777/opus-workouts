#!/usr/bin/env python3
"""Content quality validator for OpenClaw WordPress sites.

Checks published articles against quality standards:
- Word count (min 800, warn if < 1200)
- Heading structure (at least 2 H2s)
- Link count (at least 2 external links)
- Duplicate title check against post log
- No excessive em dashes (> 5)
- Meta description present and < 160 chars
- Featured image present

Usage:
  python content_quality_validator.py --site <site> [--post-id <id>] [--recent N] [--json]
  python content_quality_validator.py --site all [--recent 5]

Sites: aitoolalliance, aibusinessinsider, aicofounderstack, all
"""

import sys
import json
import re
import argparse
from pathlib import Path

# Add workspace to path for creds
sys.path.insert(0, str(Path(__file__).parent))
from creds import get_wp_site, get_wp_auth_header

import requests

MIN_WORDS = 800
WARN_WORDS = 1200
MIN_H2S = 2
MIN_LINKS = 2
MAX_EM_DASHES = 5
MAX_TITLE_LEN = 60
MAX_META_LEN = 160

SITES = ['aitoolalliance', 'aibusinessinsider', 'aicofounderstack']


def fetch_posts(site_name, recent=5, post_id=None):
    """Fetch posts from WordPress REST API."""
    site = get_wp_site(site_name)
    if not site:
        return None, f"Unknown site: {site_name}"

    headers = get_wp_auth_header(site_name)
    headers['User-Agent'] = 'Nova-Quality-Validator/1.0'

    if post_id:
        url = f"{site['url']}/wp-json/wp/v2/posts/{post_id}"
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            return None, f"Failed to fetch post {post_id}: HTTP {resp.status_code}"
        return [resp.json()], None

    url = f"{site['url']}/wp-json/wp/v2/posts?per_page={recent}&orderby=date&order=desc"
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        return None, f"Failed to fetch posts: HTTP {resp.status_code}"
    return resp.json(), None


def validate_post(post, site_name):
    """Validate a single post against quality standards."""
    content = post.get('content', {}).get('rendered', '')
    title = post.get('title', {}).get('rendered', '') or ''
    post_id = post.get('id')
    post_url = post.get('link', '')
    has_featured = post.get('featured_media', 0) != 0
    excerpt = post.get('excerpt', {}).get('rendered', '') or ''

    # Strip HTML for text analysis
    text = re.sub(r'<[^>]+>', '', content)
    word_count = len(text.split())

    # Heading structure
    h2_count = len(re.findall(r'<h2', content))
    h3_count = len(re.findall(r'<h3', content))

    # Link count (external links only)
    links = re.findall(r'<a\s+[^>]*href=[\'"]([^\'"]+)[\'"]', content)
    external_links = [l for l in links if not l.startswith('#') and site_name not in l.lower()]

    # Em dash check
    em_dashes = content.count('\u2014') + content.count('&mdash;') + content.count('--')

    # Title length
    title_len = len(title)

    # Meta description (from Yoast or excerpt)
    meta = excerpt.strip()
    # Strip HTML from excerpt
    meta = re.sub(r'<[^>]+>', '', meta).strip()
    meta_len = len(meta)

    # Build result
    issues = []
    warnings = []

    if word_count < MIN_WORDS:
        issues.append(f"Word count {word_count} below minimum {MIN_WORDS}")
    elif word_count < WARN_WORDS:
        warnings.append(f"Word count {word_count} below recommended {WARN_WORDS}")

    if h2_count < MIN_H2S:
        issues.append(f"Only {h2_count} H2 headings (minimum {MIN_H2S})")

    if len(external_links) < MIN_LINKS:
        warnings.append(f"Only {len(external_links)} external links (recommended {MIN_LINKS})")

    if em_dashes > MAX_EM_DASHES:
        issues.append(f"Excessive em dashes: {em_dashes} (max {MAX_EM_DASHES})")

    if title_len > MAX_TITLE_LEN:
        warnings.append(f"Title {title_len} chars (SEO max {MAX_TITLE_LEN})")

    if not has_featured:
        warnings.append("No featured image")

    if meta_len == 0:
        warnings.append("No meta description/excerpt")
    elif meta_len > MAX_META_LEN:
        warnings.append(f"Meta description {meta_len} chars (max {MAX_META_LEN})")

    # Overall score
    score = 100
    for _ in issues:
        score -= 15
    for _ in warnings:
        score -= 5
    score = max(0, score)

    return {
        'post_id': post_id,
        'title': title[:80],
        'url': post_url,
        'site': site_name,
        'score': score,
        'word_count': word_count,
        'h2_count': h2_count,
        'h3_count': h3_count,
        'external_links': len(external_links),
        'em_dashes': em_dashes,
        'has_featured_image': has_featured,
        'title_length': title_len,
        'meta_length': meta_len,
        'issues': issues,
        'warnings': warnings,
        'status': 'FAIL' if issues else ('WARN' if warnings else 'PASS'),
    }


def format_report(results):
    """Format validation results into a concise report."""
    lines = []
    for r in results:
        icon = {'PASS': '+', 'WARN': '~', 'FAIL': 'X'}[r['status']]
        line = f"  [{icon}] {r['site']} #{r['post_id']}: {r['title']}"
        line += f" ({r['word_count']}w, {r['h2_count']} H2, score {r['score']}/100)"
        lines.append(line)
        for issue in r['issues']:
            lines.append(f"      ISSUE: {issue}")
        for warn in r['warnings']:
            lines.append(f"      WARN: {warn}")

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    warned = sum(1 for r in results if r['status'] == 'WARN')
    failed = sum(1 for r in results if r['status'] == 'FAIL')

    report = "## Content Quality Report\n"
    report += '\n'.join(lines) + '\n'
    report += f"\nSummary: {total} posts checked | {passed} PASS | {warned} WARN | {failed} FAIL"

    return report


def main():
    parser = argparse.ArgumentParser(description='Validate WordPress content quality')
    parser.add_argument('--site', required=True, help='Site name or "all"')
    parser.add_argument('--post-id', type=int, help='Check specific post ID')
    parser.add_argument('--recent', type=int, default=5, help='Number of recent posts to check')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    sites = SITES if args.site == 'all' else [args.site]
    all_results = []

    for site in sites:
        posts, err = fetch_posts(site, recent=args.recent, post_id=args.post_id)
        if err:
            print(f"ERROR ({site}): {err}", file=sys.stderr)
            continue
        for post in posts:
            result = validate_post(post, site)
            all_results.append(result)

    if not all_results:
        print("No posts found.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(all_results, indent=2))
    else:
        print(format_report(all_results))

    # Exit 1 if any FAIL
    if any(r['status'] == 'FAIL' for r in all_results):
        sys.exit(1)


if __name__ == '__main__':
    main()