#!/usr/bin/env python3
"""
Amazon Affiliate Content Pipeline
Publishes dedicated affiliate articles to WordPress sites on schedule.

Usage: python amazon_content_pipeline.py --publish-now
       python amazon_content_pipeline.py --list
"""

import argparse
import json
import os
import re
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add creds.py to import path
sys.path.insert(0, str(Path(__file__).parent))
from creds import get_wp_site, get_wp_auth_header

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
ARTICLES_DIR = WORKSPACE / "articles"
STATE_FILE = WORKSPACE / "scripts" / "amazon_pipeline_state.json"

# Mapping of article files to target sites
CONTENT_REGISTRY = [
    {
        "file": "articles/amazon-aitoolalliance-remote-work-gear.md",
        "site": "aitoolalliance",
        "title": "The Remote Work Gear Stack That Actually Boosts Productivity (Tested in 2026)",
        "slug": "remote-work-gear-productivity-2026",
        "type": "post",
        "published": False
    },
    {
        "file": "articles/amazon-aibusinessinsider-ai-books.md",
        "site": "aibusinessinsider",
        "title": "12 Books Every AI Leader Should Read in 2026",
        "slug": "ai-leader-books-2026",
        "type": "post",
        "published": False
    },
    {
        "file": "articles/amazon-aitoolalliance-founder-desk-setup.md",
        "site": "aitoolalliance",
        "title": "The AI Founder's Desk Setup: Building for Under $1,500",
        "slug": "ai-founder-desk-setup-2026",
        "type": "post",
        "published": False
    },
    {
        "file": "articles/amazon-aitoolalliance-solopreneur-stack.md",
        "site": "aitoolalliance",
        "title": "The AI-Powered Solopreneur: 15 Tools That Replace a Team",
        "slug": "ai-solopreneur-tools-stack",
        "type": "post",
        "published": False
    },
    {
        "file": "articles/amazon-aicofounderstack-ai-cofounder-toolkit.md",
        "site": "aicofounderstack",
        "title": "The AI Cofounder Toolkit: 11 Devices for Under $2,000",
        "slug": "ai-cofounder-toolkit-devices",
        "type": "post",
        "published": False
    },
    {
        "file": "articles/amazon-aibusinessinsider-enterprise-ai-infrastructure.md",
        "site": "aibusinessinsider",
        "title": "The Enterprise AI Infrastructure Stack: What We Actually Deployed",
        "slug": "enterprise-ai-infrastructure-stack",
        "type": "post",
        "published": False
    },
    {
        "file": "articles/amazon-aitoolalliance-ai-note-taking-tools.md",
        "site": "aitoolalliance",
        "title": "The Best AI Note-Taking Tools for Research-Heavy Work",
        "slug": "ai-note-taking-tools-research",
        "type": "post",
        "published": False
    },
    {
        "file": "scripts/recommended_gear_page_aitoolalliance.md",
        "site": "aitoolalliance",
        "title": "Recommended Gear",
        "slug": "recommended-gear",
        "type": "page",
        "published": False
    },
    {
        "file": "scripts/recommended_gear_page_aibusinessinsider.md",
        "site": "aibusinessinsider",
        "title": "Recommended Resources",
        "slug": "recommended-resources",
        "type": "page",
        "published": False
    },
]

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"published": {}, "queue": [], "last_run": None}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def md_to_html(md_text):
    """Simple markdown to HTML conversion."""
    lines = md_text.split('\n')
    if lines and lines[0].startswith('# '):
        md_text = '\n'.join(lines[1:]).strip()
    
    html = md_text
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'```[\w]*\n(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
    
    paragraphs = html.split('\n\n')
    new_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<h') or p.startswith('<pre') or p.startswith('<ul') or p.startswith('<ol') or p.startswith('<li') or p.startswith('<table') or p.startswith('<tr'):
            new_paragraphs.append(p)
        else:
            if not p.startswith('<'):
                p = f'<p>{p}</p>'
            new_paragraphs.append(p)
    html = '\n\n'.join(new_paragraphs)
    
    lines = html.split('\n')
    in_list = False
    new_lines = []
    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                new_lines.append('<ul>')
                in_list = True
            content = line.strip()[2:]
            new_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                new_lines.append('</ul>')
                in_list = False
            new_lines.append(line)
    if in_list:
        new_lines.append('</ul>')
    html = '\n'.join(new_lines)
    return html

def publish_to_wordpress(site_key, title, content_html, slug=None, post_type="post"):
    """Publish or update a post/page."""
    import requests
    
    creds = get_wp_site(site_key)
    if not creds:
        return False, "No credentials"
    
    headers = get_wp_auth_header(site_key)
    
    # Check if exists
    endpoint = "pages" if post_type == "page" else "posts"
    search_url = f"{creds['url']}/wp-json/wp/v2/{endpoint}?search={requests.utils.quote(title)}&per_page=1"
    try:
        r = requests.get(search_url, headers=headers, timeout=30)
        if r.status_code == 200 and r.json():
            existing = r.json()[0]
            post_id = existing['id']
            update_url = f"{creds['url']}/wp-json/wp/v2/{endpoint}/{post_id}"
            data = {'content': content_html}
            r = requests.post(update_url, json=data, headers=headers, timeout=30)
            if r.status_code in [200, 201]:
                return True, f"Updated: {existing.get('link', 'unknown')}"
            return False, f"Update failed: HTTP {r.status_code}"
    except:
        pass
    
    # Create new
    url = f"{creds['url']}/wp-json/wp/v2/{endpoint}"
    data = {
        'title': title,
        'content': content_html,
        'status': 'publish',
        'slug': slug
    }
    try:
        r = requests.post(url, json=data, headers=headers, timeout=30)
        if r.status_code in [200, 201]:
            result = r.json()
            return True, result.get('link', 'unknown')
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)

def run_injector():
    """Run affiliate link injector on recent posts."""
    injector_path = WORKSPACE / "scripts" / "amazon_affiliate_injector.py"
    if not injector_path.exists():
        return False, "Injector not found"
    try:
        result = subprocess.run(
            [sys.executable, str(injector_path)],
            capture_output=True, text=True, timeout=120
        )
        return result.returncode == 0, result.stdout[-500:] if result.stdout else "No output"
    except Exception as e:
        return False, str(e)

def publish_next_article(state, force=False):
    """Publish the next unpublished article from registry."""
    
    # Find next unpublished
    for item in CONTENT_REGISTRY:
        key = f"{item['site']}:{item['file']}"
        if key not in state["published"] or force:
            filepath = WORKSPACE / item["file"]
            if not filepath.exists():
                print(f"SKIP: {filepath} not found")
                continue
            
            with open(filepath, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            html_content = md_to_html(md_content)
            
            print(f"Publishing: {item['title']} -> {item['site']}")
            success, result = publish_to_wordpress(
                item["site"], item["title"], html_content,
                slug=item.get("slug"), post_type=item.get("type", "post")
            )
            
            if success:
                state["published"][key] = {
                    "date": datetime.now().isoformat(),
                    "link": result,
                    "title": item["title"]
                }
                save_state(state)
                print(f"  -> OK: {result}")
                
                # Run injector after publish
                print("  -> Running affiliate injector...")
                ok, msg = run_injector()
                print(f"     Injector: {'OK' if ok else 'FAIL'} - {msg}")
                
                # Cross-post to social media
                print("[SOCIAL] Cross-posting to social media...")
                try:
                    crossposter_path = WORKSPACE / "scripts" / "social_crossposter.py"
                    link = result if isinstance(result, str) else result.get('link', '')
                    subprocess.run([
                        sys.executable, str(crossposter_path),
                        '--post-url', link,
                        '--title', item['title'],
                        '--excerpt', item['title'][:200]
                    ], timeout=120, check=False)
                    print("[SOCIAL] Cross-post completed")
                except Exception as e:
                    print(f"[SOCIAL] Cross-post failed (non-fatal): {e}")
                
                return True, item
            else:
                print(f"  -> FAIL: {result}")
                return False, result
    
    return False, "All articles published"

def list_queue(state):
    """Show what's queued and what's published."""
    print("=== Amazon Affiliate Content Queue ===\n")
    print("PUBLISHED:")
    for key, info in state["published"].items():
        print(f"  [PUB] {info['title'][:60]}...")
        print(f"        {info.get('link', 'N/A')}")
        print(f"        {info.get('date', 'N/A')}")
    
    print("\nQUEUE (not yet published):")
    for item in CONTENT_REGISTRY:
        key = f"{item['site']}:{item['file']}"
        if key not in state["published"]:
            status = "FILE EXISTS" if (WORKSPACE / item["file"]).exists() else "FILE MISSING"
            print(f"  [QUE] {item['title'][:60]}...")
            print(f"        Site: {item['site']} | Type: {item['type']}")
            print(f"        {status}")

def main():
    parser = argparse.ArgumentParser(description='Amazon Affiliate Content Pipeline')
    parser.add_argument('--publish-now', action='store_true', help='Publish next article immediately')
    parser.add_argument('--list', action='store_true', help='Show queue status')
    parser.add_argument('--injector-only', action='store_true', help='Run injector only')
    parser.add_argument('--force', action='store_true', help='Force republish existing')
    args = parser.parse_args()
    
    state = load_state()
    
    if args.list:
        list_queue(state)
        return
    
    if args.injector_only:
        ok, msg = run_injector()
        print(f"Injector: {'OK' if ok else 'FAIL'}")
        print(msg)
        return
    
    if args.publish_now:
        success, result = publish_next_article(state, force=args.force)
        if success:
            print(f"\nPublished: {result['title']}")
        else:
            print(f"\nFailed: {result}")
        return
    
    # Default: publish next in queue
    success, result = publish_next_article(state)
    if success:
        print(f"Published: {result['title']}")
    else:
        print(f"Nothing to publish: {result}")

if __name__ == "__main__":
    main()
