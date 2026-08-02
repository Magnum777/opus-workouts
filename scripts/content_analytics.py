#!/usr/bin/env python3
"""
Content Analytics Dashboard
Pulls data from WordPress sites and (optionally) Google Analytics/Search Console.
Provides visibility into what content performs, traffic trends, and affiliate conversion.

Usage:
    python scripts/content_analytics.py                    # Full dashboard
    python scripts/content_analytics.py --site aitoolalliance  # Single site
    python scripts/content_analytics.py --top 10           # Top 10 posts
    python scripts/content_analytics.py --recent 7          # Posts from last 7 days
    python scripts/content_analytics.py --json             # JSON output for cron
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE / "scripts"))

from creds import get_wp_site, get_wp_auth_header

SITES = ["aitoolalliance", "aibusinessinsider", "aicofounderstack"]
SITE_URLS = {
    "aitoolalliance": "https://aitoolalliance.com",
    "aibusinessinsider": "https://aibusinessinsider.org",
    "aicofounderstack": "https://aicofounderstack.com",
}


def fetch_posts(site_key, per_page=100, page=1):
    """Fetch posts from WordPress REST API."""
    import requests
    headers = get_wp_auth_header(site_key)
    url = f"{SITE_URLS[site_key]}/wp-json/wp/v2/posts"
    params = {
        "per_page": per_page,
        "page": page,
        "orderby": "date",
        "order": "desc",
        "_fields": "id,date,title,link,status,comment_count",
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=30)
        if r.status_code != 200:
            return [], f"HTTP {r.status_code}"
        total = int(r.headers.get("X-WP-Total", 0))
        total_pages = int(r.headers.get("X-WP-TotalPages", 0))
        posts = r.json()
        return posts, None
    except Exception as e:
        return [], str(e)


def fetch_post_detail(site_key, post_id):
    """Fetch full post detail including content length."""
    import requests
    headers = get_wp_auth_header(site_key)
    url = f"{SITE_URLS[site_key]}/wp-json/wp/v2/posts/{post_id}"
    params = {"_fields": "id,date,title,link,content,modified"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def get_post_log_stats():
    """Read post log for publishing history."""
    log_path = WORKSPACE / "memory" / "post-log" / "posts.jsonl"
    if not log_path.exists():
        return []
    entries = []
    for line in log_path.read_text(encoding='utf-8').strip().split('\n'):
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def format_date(date_str):
    """Parse ISO date to readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except (ValueError, AttributeError):
        return date_str[:10] if date_str else '?'


def days_ago(date_str):
    """Calculate days since a date string."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return (datetime.now(dt.tzinfo) - dt).days
    except (ValueError, AttributeError):
        return 999


def run_dashboard(sites=None, top_n=20, recent_days=None, json_output=False):
    """Main dashboard function."""
    if sites is None:
        sites = SITES
    
    all_posts = []
    errors = []
    
    for site in sites:
        posts, err = fetch_posts(site, per_page=100)
        if err:
            errors.append(f"{site}: {err}")
            continue
        for post in posts:
            post['site'] = site
        all_posts.extend(posts)
    
    # Get post log data
    post_log = get_post_log_stats()
    log_by_title = {}
    for entry in post_log:
        title = entry.get('title', '').lower()
        log_by_title[title] = entry
    
    # Filter by recent if requested
    if recent_days is not None:
        all_posts = [p for p in all_posts if days_ago(p.get('date', '')) <= recent_days]
    
    # Sort by date
    all_posts.sort(key=lambda p: p.get('date', ''), reverse=True)
    
    if json_output:
        output = {
            "generated_at": datetime.now().isoformat(),
            "total_posts": len(all_posts),
            "sites": {},
            "errors": errors,
        }
        for site in sites:
            site_posts = [p for p in all_posts if p['site'] == site]
            output["sites"][site] = {
                "post_count": len(site_posts),
                "posts": [
                    {
                        "id": p.get("id"),
                        "title": p.get("title", {}).get("rendered", "?")[:80],
                        "date": p.get("date", "")[:10],
                        "link": p.get("link", ""),
                        "in_post_log": any(
                            p.get("title", {}).get("rendered", "").lower() in lt
                            for lt in log_by_title
                        ),
                    }
                    for p in site_posts[:top_n]
                ],
            }
        print(json.dumps(output, indent=2))
        return output
    
    # Human-readable dashboard
    print(f"=== Content Analytics Dashboard ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    if errors:
        print("Errors:")
        for e in errors:
            print(f"  - {e}")
        print()
    
    print(f"Total posts across {len(sites)} site(s): {len(all_posts)}")
    for site in sites:
        site_posts = [p for p in all_posts if p['site'] == site]
        print(f"  {site}: {len(site_posts)} posts")
    print()
    
    # Recent posts
    print(f"--- Most Recent Posts (top {min(top_n, len(all_posts))}) ---")
    for i, post in enumerate(all_posts[:top_n], 1):
        title = post.get('title', {}).get('rendered', '?')
        if len(title) > 65:
            title = title[:62] + "..."
        date = format_date(post.get('date', ''))
        age = days_ago(post.get('date', ''))
        age_str = f"{age}d ago" if age < 365 else f"{age // 30}mo ago"
        print(f"  {i:2d}. [{post['site'][:3].upper()}] {title}")
        print(f"      {date} ({age_str}) | {post.get('link', '')}")
    
    # Post log coverage
    print(f"\n--- Post Log Coverage ---")
    log_count = len(post_log)
    print(f"  {log_count} entries in post log")
    if log_count > 0:
        recent_log = sorted(post_log, key=lambda e: e.get('timestamp', ''), reverse=True)[:5]
        print(f"  Last 5 logged:")
        for entry in recent_log:
            ts = entry.get('timestamp', '?')[:16]
            project = entry.get('project', '?')
            title = entry.get('title', '?')[:50]
            status = entry.get('status', '?')
            print(f"    {ts} [{project}] {title} ({status})")
    
    # Content gaps: posts not in post log
    unlogged = []
    for post in all_posts[:50]:
        title = post.get('title', {}).get('rendered', '').lower()
        if not any(title[:20] in lt for lt in log_by_title):
            unlogged.append(post)
    if unlogged:
        print(f"\n--- Potential Content Gaps (not in post log) ---")
        for post in unlogged[:10]:
            title = post.get('title', {}).get('rendered', '?')[:65]
            print(f"  [{post['site'][:3].upper()}] {title}")
    
    return all_posts


def main():
    parser = argparse.ArgumentParser(description="Content analytics dashboard")
    parser.add_argument("--site", type=str, help="Single site to analyze")
    parser.add_argument("--top", type=int, default=20, help="Number of top posts to show")
    parser.add_argument("--recent", type=int, help="Only show posts from last N days")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    sites = [args.site] if args.site else SITES
    run_dashboard(sites=sites, top_n=args.top, recent_days=args.recent, json_output=args.json)


if __name__ == "__main__":
    main()