#!/usr/bin/env python3
"""
AgentFuse-style Affiliate Link Integration for ContentNova Pipeline

Automatically injects tracked affiliate links into WordPress content
before publishing. Scans article text for product mentions and replaces
them with affiliate-tagged links pointing to our review articles.

This is the integration layer between ContentNova/PromptPack articles
and our affiliate monetization strategy.

Usage:
    python affiliate_injector.py scan <site>              # Scan recent posts for link opportunities
    python affiliate_injector.py inject <site> <post_id>   # Inject links into a specific post
    python affiliate_injector.py inject-all <site>          # Inject links into all recent posts
    python affiliate_injector.py stats                      # Show injection stats
    python affiliate_injector.py products add <name> <url>   # Add a product to the registry
    python affiliate_injector.py products list               # List all tracked products
"""

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
PRODUCTS_FILE = WORKSPACE / "scripts" / "affiliate_products.json"
INJECTION_LOG = WORKSPACE / "memory" / "post-log" / "affiliate_injections.jsonl"

# Affiliate tags per site
AFFILIATE_TAGS = {
    "aitoolalliance": "aitoolalliance-20",
    "aicofounderstack": "aicofounderstack-20",
    "aibusinessinsider": "aibusinessinsider-20",
}

# Product registry: product names -> site review URLs
# When content mentions these products, we link to our review article
DEFAULT_PRODUCTS = {
    # AI Writing & Content
    "Jasper": {"url": "/best-ai-writing-tools/", "site": "aitoolalliance", "category": "ai_software"},
    "Copy.ai": {"url": "/best-ai-copywriting-tools/", "site": "aitoolalliance", "category": "ai_software"},
    "Grammarly": {"url": "/grammarly-review/", "site": "aitoolalliance", "category": "ai_software"},
    "Surfer SEO": {"url": "/surfer-seo-review/", "site": "aitoolalliance", "category": "ai_software"},
    "Writesonic": {"url": "/writesonic-review/", "site": "aitoolalliance", "category": "ai_software"},
    
    # AI Automation
    "Zapier": {"url": "/zapier-review/", "site": "aitoolalliance", "category": "automation"},
    "Make": {"url": "/make-review/", "site": "aitoolalliance", "category": "automation"},
    "n8n": {"url": "/n8n-review/", "site": "aitoolalliance", "category": "automation"},
    "Bardeen": {"url": "/bardeen-review/", "site": "aitoolalliance", "category": "automation"},
    
    # AI Coding
    "Cursor": {"url": "/cursor-review/", "site": "aitoolalliance", "category": "ai_software"},
    "Replit": {"url": "/replit-review/", "site": "aitoolalliance", "category": "ai_software"},
    "GitHub Copilot": {"url": "/github-copilot-review/", "site": "aitoolalliance", "category": "ai_software"},
    
    # SEO & Marketing
    "Semrush": {"url": "/semrush-review/", "site": "aitoolalliance", "category": "seo"},
    "Ahrefs": {"url": "/ahrefs-review/", "site": "aitoolalliance", "category": "seo"},
    "Mailchimp": {"url": "/mailchimp-review/", "site": "aitoolalliance", "category": "email"},
    
    # Productivity
    "Notion": {"url": "/notion-review/", "site": "aitoolalliance", "category": "productivity"},
    "Asana": {"url": "/asana-review/", "site": "aitoolalliance", "category": "productivity"},
    "Otter.ai": {"url": "/otter-ai-review/", "site": "aitoolalliance", "category": "productivity"},
    "Loom": {"url": "/loom-review/", "site": "aitoolalliance", "category": "productivity"},
    
    # AI Business Tools (aibusinessinsider)
    "Salesforce": {"url": "/salesforce-ai-review/", "site": "aibusinessinsider", "category": "enterprise"},
    "HubSpot": {"url": "/hubspot-ai-review/", "site": "aibusinessinsider", "category": "enterprise"},
    "Tableau": {"url": "/tableau-review/", "site": "aibusinessinsider", "category": "analytics"},
    
    # Founder Tools (aicofounderstack)
    "Stripe": {"url": "/stripe-review/", "site": "aicofounderstack", "category": "payments"},
    "Vercel": {"url": "/vercel-review/", "site": "aicofounderstack", "category": "hosting"},
    "Supabase": {"url": "/supabase-review/", "site": "aicofounderstack", "category": "backend"},
}

# Link insertion rules
MAX_LINKS_PER_POST = 8          # Don't over-stuff
MIN_WORDS_BETWEEN_LINKS = 100   # At least 100 words between affiliate links
FIRST_LINK_ONLY = True          # Only link the first mention of each product
LINK_PHRASES = [
    # Patterns where we should NOT add links (inside existing links)
    r'<a[^>]*>.*?</a>',
    # Patterns inside headings
    r'<h[1-6][^>]*>.*?</h[1-6]>',
]


def load_products():
    """Load product registry, creating default if needed."""
    if PRODUCTS_FILE.exists():
        try:
            return json.loads(PRODUCTS_FILE.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, ValueError):
            pass
    
    # Save defaults
    PRODUCTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PRODUCTS_FILE.write_text(
        json.dumps(DEFAULT_PRODUCTS, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    return DEFAULT_PRODUCTS


def save_products(products):
    """Save product registry."""
    PRODUCTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PRODUCTS_FILE.write_text(
        json.dumps(products, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )


def log_injection(post_id, site, products_injected, links_added, status="success"):
    """Log an injection to the JSONL log."""
    INJECTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "post_id": post_id,
        "site": site,
        "products_injected": products_injected,
        "links_added": links_added,
        "status": status,
    }
    with open(INJECTION_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def inject_links(html_content, site, products=None, max_links=MAX_LINKS_PER_POST):
    """
    Scan HTML content for product mentions and inject affiliate links.
    
    Rules:
    - Only link the FIRST mention of each product (FIRST_LINK_ONLY)
    - Don't link inside existing <a> tags
    - Don't link inside headings
    - Space links at least MIN_WORDS_BETWEEN_LINKS apart
    - Cap at max_links total
    - Use the site's affiliate tag
    """
    if products is None:
        products = load_products()
    
    tag = AFFILIATE_TAGS.get(site, "aitoolalliance-20")
    base_url = f"https://{site}.com" if site != "aibusinessinsider" else "https://aibusinessinsider.org"
    links_added = 0
    products_injected = []
    last_link_position = 0
    
    # Sort products by name length (longest first) to avoid partial matches
    sorted_products = sorted(products.items(), key=lambda x: len(x[0]), reverse=True)
    
    # Track positions where we've added links to enforce spacing
    link_positions = []
    
    for product_name, product_info in sorted_products:
        if links_added >= max_links:
            break
        
        # Skip if product doesn't belong to this site
        if product_info.get("site") != site:
            # Still allow cross-site links, but use the product's site URL
            pass
        
        # Build the affiliate URL
        product_site = product_info.get("site", site)
        product_base = f"https://{product_site}.com" if product_site != "aibusinessinsider" else "https://aibusinessinsider.org"
        product_tag = AFFILIATE_TAGS.get(product_site, "aitoolalliance-20")
        affiliate_url = f"{product_base}{product_info['url']}?tag={product_tag}"
        
        # Search for the product name in text (not inside tags)
        # Pattern: find product name that's NOT inside an <a> tag or heading
        pattern = re.compile(
            r'(?<!<a[^>]*>[^<]*)'  # Not inside an <a> tag (approximation)
            r'(?<!<h[1-6][^>]*>[^<]*)'  # Not inside a heading (approximation)
            r'\b' + re.escape(product_name) + r'\b',
            re.IGNORECASE
        )
        
        # Find the first valid position
        for match in pattern.finditer(html_content):
            pos = match.start()
            
            # Check if we're inside an existing link or heading
            # Look backwards for unclosed tags
            before = html_content[max(0, pos - 500):pos]
            if re.search(r'<a[^>]*>[^<]*$', before, re.IGNORECASE):
                continue  # Inside an <a> tag
            if re.search(r'<h[1-6][^>]*>[^<]*$', before, re.IGNORECASE):
                continue  # Inside a heading
            
            # Check minimum spacing from last link
            text_between = html_content[last_link_position:pos]
            word_count = len(text_between.split())
            if link_positions and word_count < MIN_WORDS_BETWEEN_LINKS:
                continue
            
            # Inject the link
            original = match.group()
            replacement = f'<a href="{affiliate_url}" target="_blank" rel="noopener noreferrer nofollow">{original}</a>'
            html_content = html_content[:pos] + replacement + html_content[match.end():]
            
            links_added += 1
            products_injected.append(product_name)
            link_positions.append(pos)
            last_link_position = pos + len(replacement)
            
            break  # FIRST_LINK_ONLY
    
    return html_content, products_injected, links_added


def cmd_scan(args):
    """Scan recent posts for affiliate link opportunities."""
    sys.path.insert(0, str(WORKSPACE / "scripts"))
    from creds import get_wp_site, get_wp_auth_header
    
    site = args.site
    site_config = get_wp_site(site)
    if not site_config:
        print(f"ERROR: No credentials for site '{site}'")
        return
    
    base_url = site_config['url'].rstrip('/')
    headers = get_wp_auth_header(site)
    
    import requests
    
    print(f"Scanning recent posts on {site}...")
    try:
        resp = requests.get(
            f"{base_url}/wp-json/wp/v2/posts?per_page=10&orderby=date&order=desc",
            headers=headers,
            timeout=30
        )
        if resp.status_code != 200:
            print(f"ERROR: {resp.status_code} {resp.text[:200]}")
            return
        
        posts = resp.json()
        products = load_products()
        
        print(f"\nFound {len(posts)} recent posts.\n")
        print(f"{'Post ID':<10} {'Title':<50} {'Products Found':<30}")
        print("-" * 90)
        
        for post in posts:
            post_id = post['id']
            title = post['title']['rendered'][:48]
            content = post['content']['rendered']
            
            # Find product mentions
            found = []
            for product_name in products:
                if re.search(r'\b' + re.escape(product_name) + r'\b', content, re.IGNORECASE):
                    found.append(product_name)
            
            # Check which are already linked
            already_linked = []
            for product_name in found:
                if f'>{product_name}</a>' in content or f'>{product_name.lower()}</a>' in content:
                    already_linked.append(product_name)
            
            unlinked = [p for p in found if p not in already_linked]
            status = f"{len(unlinked)} unlinked" if unlinked else "all linked"
            print(f"{post_id:<10} {title:<50} {status:<30}")
        
    except Exception as e:
        print(f"ERROR: {e}")


def cmd_inject(args):
    """Inject affiliate links into a specific post."""
    sys.path.insert(0, str(WORKSPACE / "scripts"))
    from creds import get_wp_site, get_wp_auth_header
    
    site = args.site
    post_id = args.post_id
    
    site_config = get_wp_site(site)
    if not site_config:
        print(f"ERROR: No credentials for site '{site}'")
        return
    
    base_url = site_config['url'].rstrip('/')
    headers = get_wp_auth_header(site)
    
    import requests
    
    print(f"Fetching post {post_id} from {site}...")
    try:
        resp = requests.get(
            f"{base_url}/wp-json/wp/v2/posts/{post_id}",
            headers=headers,
            timeout=30
        )
        if resp.status_code != 200:
            print(f"ERROR: {resp.status_code} {resp.text[:200]}")
            return
        
        post = resp.json()
        content = post['content']['rendered']
        title = post['title']['rendered']
        
        print(f"Title: {title}")
        print(f"Content length: {len(content)} chars")
        
        # Inject links
        new_content, products_injected, links_added = inject_links(content, site)
        
        if links_added == 0:
            print("No affiliate links injected (no matching products found or all already linked).")
            return
        
        print(f"\nInjected {links_added} affiliate links:")
        for product in products_injected:
            print(f"  - {product}")
        
        if args.dry_run:
            print("\n[DRY RUN] Not updating the post.")
            log_injection(post_id, site, products_injected, links_added, status="dry_run")
            return
        
        # Update the post
        print(f"\nUpdating post {post_id}...")
        update_resp = requests.post(
            f"{base_url}/wp-json/wp/v2/posts/{post_id}",
            headers=headers,
            json={"content": new_content},
            timeout=30
        )
        
        if update_resp.status_code in (200, 201):
            print(f"Post {post_id} updated successfully.")
            log_injection(post_id, site, products_injected, links_added, status="success")
        else:
            print(f"ERROR updating post: {update_resp.status_code} {update_resp.text[:200]}")
            log_injection(post_id, site, products_injected, links_added, status="error")
    
    except Exception as e:
        print(f"ERROR: {e}")


def cmd_inject_all(args):
    """Inject affiliate links into all recent posts for a site."""
    sys.path.insert(0, str(WORKSPACE / "scripts"))
    from creds import get_wp_site, get_wp_auth_header
    
    site = args.site
    site_config = get_wp_site(site)
    if not site_config:
        print(f"ERROR: No credentials for site '{site}'")
        return
    
    base_url = site_config['url'].rstrip('/')
    headers = get_wp_auth_header(site)
    
    import requests
    
    print(f"Injecting affiliate links into recent {site} posts...")
    try:
        resp = requests.get(
            f"{base_url}/wp-json/wp/v2/posts?per_page=20&orderby=date&order=desc",
            headers=headers,
            timeout=30
        )
        if resp.status_code != 200:
            print(f"ERROR: {resp.status_code}")
            return
        
        posts = resp.json()
        total_links = 0
        total_posts = 0
        
        for post in posts:
            post_id = post['id']
            content = post['content']['rendered']
            
            new_content, products_injected, links_added = inject_links(content, site)
            
            if links_added == 0:
                continue
            
            if args.dry_run:
                print(f"  Post {post_id}: {links_added} links (dry run) - {', '.join(products_injected)}")
                log_injection(post_id, site, products_injected, links_added, status="dry_run")
            else:
                update_resp = requests.post(
                    f"{base_url}/wp-json/wp/v2/posts/{post_id}",
                    headers=headers,
                    json={"content": new_content},
                    timeout=30
                )
                if update_resp.status_code in (200, 201):
                    print(f"  Post {post_id}: {links_added} links injected - {', '.join(products_injected)}")
                    log_injection(post_id, site, products_injected, links_added, status="success")
                else:
                    print(f"  Post {post_id}: ERROR - {update_resp.status_code}")
                    log_injection(post_id, site, products_injected, links_added, status="error")
            
            total_links += links_added
            total_posts += 1
        
        print(f"\nTotal: {total_links} links injected across {total_posts} posts.")
    
    except Exception as e:
        print(f"ERROR: {e}")


def cmd_stats(args):
    """Show injection stats."""
    if not INJECTION_LOG.exists():
        print("No injection logs found.")
        return
    
    entries = []
    with open(INJECTION_LOG, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entries.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    
    if not entries:
        print("No injection entries found.")
        return
    
    total_links = sum(e.get('links_added', 0) for e in entries)
    total_posts = len(set(e.get('post_id') for e in entries if e.get('status') == 'success'))
    
    # Products injected frequency
    product_counts = {}
    for entry in entries:
        for product in entry.get('products_injected', []):
            product_counts[product] = product_counts.get(product, 0) + 1
    
    print(f"Affiliate Injection Stats")
    print(f"{'='*40}")
    print(f"Total injections: {len(entries)}")
    print(f"Total posts modified: {total_posts}")
    print(f"Total links added: {total_links}")
    print(f"\nTop products linked:")
    for product, count in sorted(product_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {product}: {count}x")


def cmd_products(args):
    """Manage product registry."""
    products = load_products()
    
    if args.action == "list":
        print(f"Product Registry ({len(products)} products)")
        print(f"{'='*60}")
        for name, info in sorted(products.items()):
            site = info.get('site', 'unknown')
            category = info.get('category', 'unknown')
            print(f"  {name:<25} -> {site}/{category} {info['url']}")
    
    elif args.action == "add":
        if len(args.params) < 3:
            print("Usage: products add <name> <url> <site> [category]")
            return
        
        name, url, site = args.params[0], args.params[1], args.params[2]
        category = args.params[3] if len(args.params) > 3 else "general"
        
        products[name] = {"url": url, "site": site, "category": category}
        save_products(products)
        print(f"Added: {name} -> {site}{url} [{category}]")
    
    elif args.action == "remove":
        name = args.params[0]
        if name in products:
            del products[name]
            save_products(products)
            print(f"Removed: {name}")
        else:
            print(f"Product not found: {name}")


def main():
    parser = argparse.ArgumentParser(description="Affiliate Link Injector for ContentNova")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Scan
    scan_parser = subparsers.add_parser("scan", help="Scan posts for link opportunities")
    scan_parser.add_argument("site", choices=["aitoolalliance", "aicofounderstack", "aibusinessinsider"])
    
    # Inject
    inject_parser = subparsers.add_parser("inject", help="Inject links into a post")
    inject_parser.add_argument("site", choices=["aitoolalliance", "aicofounderstack", "aibusinessinsider"])
    inject_parser.add_argument("post_id", type=int)
    inject_parser.add_argument("--dry-run", action="store_true")
    
    # Inject all
    inject_all_parser = subparsers.add_parser("inject-all", help="Inject links into all recent posts")
    inject_all_parser.add_argument("site", choices=["aitoolalliance", "aicofounderstack", "aibusinessinsider"])
    inject_all_parser.add_argument("--dry-run", action="store_true")
    
    # Stats
    subparsers.add_parser("stats", help="Show injection stats")
    
    # Products
    products_parser = subparsers.add_parser("products", help="Manage product registry")
    products_parser.add_argument("action", choices=["add", "remove", "list"])
    products_parser.add_argument("params", nargs="*")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "inject":
        cmd_inject(args)
    elif args.command == "inject-all":
        cmd_inject_all(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "products":
        cmd_products(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()