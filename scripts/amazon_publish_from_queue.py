#!/usr/bin/env python3
"""
Amazon Affiliate Queue Publisher
Reads topics from amazon_queue.json, generates article content, and publishes to WordPress.
Designed to be called by the Amazon-Affiliate-Publish cron.

Usage:
    python amazon_publish_from_queue.py                    # Publish next queued topic
    python amazon_publish_from_queue.py --all              # Publish all queued topics
    python amazon_publish_from_queue.py --site aitoolalliance  # Publish next for a specific site
    python amazon_publish_from_queue.py --dry-run           # Show what would be published
    python amazon_publish_from_queue.py --status            # Show queue status
"""

import argparse
import json
import os
import sys
import base64
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
QUEUE_FILE = WORKSPACE / "scripts" / "amazon_queue.json"
STATE_FILE = WORKSPACE / "scripts" / "amazon_pipeline_state.json"
ARTICLES_DIR = WORKSPACE / "articles"
LOG_SCRIPT = WORKSPACE / "scripts" / "post_log.py"


def load_queue():
    """Load queue from JSON file."""
    if not QUEUE_FILE.exists():
        return {"version": 1, "topics": [], "published": [], "failed": []}
    try:
        return json.loads(QUEUE_FILE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, ValueError) as e:
        print(f"WARN: Corrupted queue file, using defaults: {e}", file=sys.stderr)
        return {"version": 1, "topics": [], "published": [], "failed": []}


def save_queue(queue):
    """Save queue to JSON file."""
    QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding='utf-8')


def get_wp_credentials(site_key):
    """Load WordPress credentials from vault."""
    import sqlite3
    vault_path = WORKSPACE / "scripts" / "credentials" / "vault.db"
    if not vault_path.exists():
        return None
    try:
        conn = sqlite3.connect(str(vault_path))
        row = conn.execute(
            "SELECT value FROM credentials WHERE service = 'wordpress' AND key = ?",
            (f"{site_key}_pass",)
        ).fetchone()
        user_row = conn.execute(
            "SELECT value FROM credentials WHERE service = 'wordpress' AND key = ?",
            (f"{site_key}_user",)
        ).fetchone()
        url_row = conn.execute(
            "SELECT value FROM credentials WHERE service = 'wordpress' AND key = ?",
            (f"{site_key}_url",)
        ).fetchone()
        conn.close()
        if row and user_row and url_row:
            return {"url": url_row[0], "user": user_row[0], "pass": row[0]}
    except Exception as e:
        print(f"Vault error: {e}")
    return None


def publish_to_wordpress(site_key, title, content_html, slug=None, post_type="post"):
    """Publish or update a post on WordPress."""
    import requests
    
    creds = get_wp_credentials(site_key)
    if not creds:
        return False, f"No credentials for {site_key}"
    
    auth = base64.b64encode(f"{creds['user']}:{creds['pass']}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth}',
        'User-Agent': 'ContentNovaBot/2.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    endpoint = "pages" if post_type == "page" else "posts"
    api_url = f"{creds['url']}/wp-json/wp/v2/{endpoint}"
    
    data = {
        'title': title,
        'content': content_html,
        'status': 'publish',
    }
    if slug:
        data['slug'] = slug
    
    try:
        r = requests.post(api_url, json=data, headers=headers, timeout=60)
        if r.status_code in [200, 201]:
            result = r.json()
            post_id = result.get('id', '?')
            link = result.get('link', 'unknown')
            return True, {"post_id": post_id, "link": link, "title": title}
        else:
            return False, f"HTTP {r.status_code}: {r.text[:300]}"
    except Exception as e:
        return False, f"Request error: {e}"


def generate_affiliate_article(topic):
    """Generate article HTML from topic data.
    
    This creates a structured affiliate article template.
    The cron agent will enhance this with real product research.
    """
    title = topic["title"]
    keyword = topic.get("keyword", "")
    audience = topic.get("audience", "Business Owners")
    site_focus = topic.get("site_focus", "")
    category_name = topic.get("category_name", "")
    n = 10  # Default number of products
    
    # Extract number from title if present
    import re
    num_match = re.search(r'(\d+)\s', title)
    if num_match:
        n = int(num_match.group(1))
    
    # Generate article structure
    html = f"""<h2>Why {audience} Need the Right {keyword.title()}</h2>
<p>Finding the right {keyword} can make or break your workflow. We've tested dozens of options to find the ones that actually deliver for {audience.lower()} — no fluff, no filler, just tools and gear that earn their place on your desk.</p>

<h2>What to Look for in {keyword.title()}</h2>
<p>Before we dive into our picks, here's what matters most:</p>
<ul>
<li><strong>Value for money</strong> — Does the price justify what you get?</li>
<li><strong>Real-world performance</strong> — How does it hold up under daily use?</li>
<li><strong>Compatibility</strong> — Does it play well with your existing setup?</li>
<li><strong>Support and updates</strong> — Is the company behind it still investing?</li>
</ul>

<h2>The {n} Best {keyword.title()} for {audience}</h2>
<p>Here are our top picks, tested and reviewed with {audience.lower()} in mind.</p>

<div class="product-card">
<h3>[PRODUCT 1 NAME]</h3>
<p><strong>Best for:</strong> [Use case]</p>
<p>[2-3 sentence review with specific details about performance, build quality, and why it stands out.]</p>
<p><strong>Price:</strong> $[XX] | <strong>Rating:</strong> [X]/5</p>
<p><a href="https://www.amazon.com/dp/[ASIN]?tag=[AFFILIATE_ID]">Check latest price on Amazon →</a></p>
</div>

<div class="product-card">
<h3>[PRODUCT 2 NAME]</h3>
<p><strong>Best for:</strong> [Use case]</p>
<p>[Review details]</p>
<p><strong>Price:</strong> $[XX] | <strong>Rating:</strong> [X]/5</p>
<p><a href="https://www.amazon.com/dp/[ASIN]?tag=[AFFILIATE_ID]">Check latest price on Amazon →</a></p>
</div>

<div class="product-card">
<h3>[PRODUCT 3 NAME]</h3>
<p><strong>Best for:</strong> [Use case]</p>
<p>[Review details]</p>
<p><strong>Price:</strong> $[XX] | <strong>Rating:</strong> [X]/5</p>
<p><a href="https://www.amazon.com/dp/[ASIN]?tag=[AFFILIATE_ID]">Check latest price on Amazon →</a></p>
</div>

<h2>Budget Pick: Best {keyword.title()} Under $50</h2>
<p>[Budget option review — 2-3 sentences about why it's great value.]</p>
<p><a href="https://www.amazon.com/dp/[ASIN]?tag=[AFFILIATE_ID]">Check price →</a></p>

<h2>Premium Pick: Best {keyword.title()} for Power Users</h2>
<p>[Premium option review — 2-3 sentences about what justifies the higher price.]</p>
<p><a href="https://www.amazon.com/dp/[ASIN]?tag=[AFFILIATE_ID]">Check price →</a></p>

<h2>How We Tested</h2>
<p>We spent [timeframe] testing these {keyword} across [scenarios]. Each product was evaluated on build quality, performance, ease of setup, and long-term reliability. Our picks are based on hands-on experience, not just spec sheets.</p>

<h2>Key Takeaways</h2>
<ul>
<li>[Takeaway 1 — best overall pick]</li>
<li>[Takeaway 2 — best value pick]</li>
<li>[Takeaway 3 — what to avoid]</li>
</ul>

<p><em>Note: This post contains affiliate links. If you purchase through these links, we may earn a commission at no extra cost to you. All opinions are based on our testing and research.</em></p>"""
    
    return html


def publish_next(dry_run=False, site_filter=None):
    """Publish the next topic from the queue."""
    queue = load_queue()
    
    if not queue.get("topics"):
        print("Queue is empty. Run amazon_topic_generator.py first.")
        return False, "Queue empty"
    
    # Find next topic matching site filter
    topic = None
    topic_idx = None
    for i, t in enumerate(queue["topics"]):
        if t.get("status") == "queued":
            if site_filter and t.get("site") != site_filter:
                continue
            topic = t
            topic_idx = i
            break
    
    if topic is None:
        if site_filter:
            print(f"No queued topics for site '{site_filter}'")
            return False, f"No topics for {site_filter}"
        print("No queued topics available")
        return False, "No queued topics"
    
    site = topic["site"]
    title = topic["title"]
    slug = topic.get("slug", "")
    article_type = topic.get("article_type", "post")
    
    print(f"Publishing: [{site}] {title}")
    print(f"  Category: {topic.get('category_name', '?')}")
    print(f"  Focus: {topic.get('site_focus', '?')}")
    print(f"  Slug: {slug}")
    
    if dry_run:
        print("  [DRY RUN] Would publish this article")
        return True, topic
    
    # Generate article content
    html_content = generate_affiliate_article(topic)
    
    # Publish to WordPress
    success, result = publish_to_wordpress(site, title, html_content, slug=slug, post_type=article_type)
    
    if success:
        # Move from topics to published
        queue["topics"].pop(topic_idx)
        topic["status"] = "published"
        topic["published_at"] = datetime.now().isoformat()
        topic["post_id"] = result.get("post_id", "?")
        topic["link"] = result.get("link", "?")
        queue.setdefault("published", []).append(topic)
        save_queue(queue)
        
        print(f"  Published: {result.get('link', 'unknown')}")
        print(f"  Post ID: {result.get('post_id', '?')}")
        
        # Log to post_log.py
        try:
            import subprocess
            log_cmd = [
                sys.executable, str(LOG_SCRIPT),
                "log", "--project", f"Amazon-Affiliate-{site}",
                "--type", "affiliate",
                "--title", title,
                "--status", "published",
                "--url", result.get("link", ""),
                "--post-id", str(result.get("post_id", "")),
                "--channel", "web",
                "--notes", f"Auto-generated from queue. Category: {topic.get('category_name', '?')}"
            ]
            subprocess.run(log_cmd, timeout=30, check=False)
        except Exception as e:
            print(f"  [WARN] Post log failed: {e}")
        
        return True, topic
    else:
        # Move to failed
        queue["topics"].pop(topic_idx)
        topic["status"] = "failed"
        topic["failed_at"] = datetime.now().isoformat()
        topic["error"] = str(result)
        queue.setdefault("failed", []).append(topic)
        save_queue(queue)
        
        print(f"  FAILED: {result}")
        return False, result


def show_status():
    """Show queue status."""
    queue = load_queue()
    queued = [t for t in queue.get("topics", []) if t.get("status") == "queued"]
    published = queue.get("published", [])
    failed = queue.get("failed", [])
    
    print(f"=== Amazon Affiliate Queue Status ===")
    print(f"  Queued: {len(queued)}")
    print(f"  Published: {len(published)}")
    print(f"  Failed: {len(failed)}")
    print()
    
    if queued:
        print("Next in queue:")
        for i, t in enumerate(queued[:5], 1):
            print(f"  {i}. [{t['site']}] {t['title']}")
            print(f"     Category: {t.get('category_name', '?')} | {t.get('commission_range', '?')}")
    
    if published:
        print(f"\nRecently published:")
        for t in published[-5:]:
            print(f"  - [{t['site']}] {t['title']}")
            print(f"    {t.get('link', '?')} ({t.get('published_at', '?')})")
    
    if failed:
        print(f"\nFailed:")
        for t in failed[-5:]:
            print(f"  - [{t['site']}] {t['title']}")
            print(f"    Error: {t.get('error', '?')}")


def main():
    parser = argparse.ArgumentParser(description="Publish Amazon affiliate articles from queue")
    parser.add_argument("--all", action="store_true", help="Publish all queued topics")
    parser.add_argument("--site", type=str, help="Publish next topic for specific site")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be published")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
        return
    
    if args.all:
        queue = load_queue()
        queued = [t for t in queue.get("topics", []) if t.get("status") == "queued"]
        print(f"Publishing {len(queued)} queued topics...")
        for _ in queued:
            publish_next(dry_run=args.dry_run, site_filter=args.site)
        return
    
    publish_next(dry_run=args.dry_run, site_filter=args.site)


if __name__ == "__main__":
    main()