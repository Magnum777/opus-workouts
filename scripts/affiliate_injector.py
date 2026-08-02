#!/usr/bin/env python3
"""
Affiliate Link Injector for ContentNova Pipeline

Hybrid linking strategy:
- SaaS tools → link to product website with rel="sponsored nofollow"
- If product has an internal_slug → link to our own article instead (higher value)
- Amazon products → link to Amazon with ?tag=AITOOLALLIANCE-20

Rules:
- First mention only per product
- Max 8 links per post
- Min 100 words between links
- Skip headings and existing links

Usage:
    python affiliate_injector.py scan <site>
    python affiliate_injector.py inject <site> <post_id> [--dry-run]
    python affiliate_injector.py inject-all <site> [--dry-run]
    python affiliate_injector.py stats
    python affiliate_injector.py products list
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

AFFILIATE_TAGS = {
    "aitoolalliance": "aitoolalliance-20",
    "aicofounderstack": "aicofounderstack-20",
    "aibusinessinsider": "aibusinessinsider-20",
}

SITE_BASE_URLS = {
    "aitoolalliance": "https://aitoolalliance.com",
    "aicofounderstack": "https://aicofounderstack.com",
    "aibusinessinsider": "https://aibusinessinsider.org",
}

MAX_LINKS_PER_POST = 8
MIN_WORDS_BETWEEN_LINKS = 100


def load_products():
    """Load product registry from JSON."""
    if PRODUCTS_FILE.exists():
        try:
            data = json.loads(PRODUCTS_FILE.read_text(encoding='utf-8'))
            # Support both old dict format and new list format
            if isinstance(data, dict) and 'products' in data:
                return data
            return data
        except (json.JSONDecodeError, ValueError):
            pass
    return {"products": [], "amazon_products": [], "affiliate_tags": AFFILIATE_TAGS}


def save_products(data):
    """Save product registry."""
    PRODUCTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PRODUCTS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )


def log_injection(post_id, site, links_added, details, status="success"):
    """Log an injection to the JSONL log."""
    INJECTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "post_id": post_id,
        "site": site,
        "links_added": links_added,
        "details": details,
        "status": status,
        "version": "2.0",
    }
    with open(INJECTION_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def build_affiliate_link(product_name, product_info, site, tags):
    """
    Build the affiliate link based on product type.
    
    Strategy:
    1. If product has an internal_slug and it belongs to this site → link to our article
    2. If product is SaaS → link to product website (rel=sponsored nofollow)
    3. If product is Amazon → link to Amazon with affiliate tag
    """
    product_type = product_info.get("type", "saas")
    product_site = product_info.get("site", site)
    tag = tags.get(site, "aitoolalliance-20")
    
    # Strategy 1: Internal link (prefer our own content when available)
    internal_slug = product_info.get("internal_slug")
    if internal_slug and product_site == site:
        base = SITE_BASE_URLS.get(site, f"https://{site}.com")
        url = f"{base}{internal_slug}"
        return url, "internal"
    
    # Strategy 2: SaaS product → link to product website
    if product_type == "saas":
        url = product_info.get("url", product_info.get("affiliate_url", ""))
        if not url:
            return None, None
        # Add UTM params for tracking
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}utm_source={site}&utm_medium=affiliate&utm_campaign=content"
        return url, "saas_direct"
    
    # Strategy 3: Amazon product → direct Amazon link with affiliate tag
    if product_type == "amazon":
        asin = product_info.get("asin", "")
        if not asin:
            return None, None
        url = f"https://www.amazon.com/dp/{asin}/?tag={tag}&linkCode=ll1&ie=UTF8"
        return url, "amazon"
    
    return None, None


def inject_links(html_content, site, products_data=None, max_links=MAX_LINKS_PER_POST):
    """
    Scan HTML content for product mentions and inject affiliate links.
    
    Uses hybrid strategy: internal links > SaaS direct > Amazon.
    """
    if products_data is None:
        products_data = load_products()
    
    tags = products_data.get("affiliate_tags", AFFILIATE_TAGS)
    saas_products = products_data.get("products", [])
    amazon_products = products_data.get("amazon_products", [])
    
    # Combine all matchable products
    all_products = []
    for p in saas_products:
        all_products.append({**p, "_type": "saas"})
    for p in amazon_products:
        all_products.append({**p, "_type": "amazon"})
    
    # Sort by name length (longest first) to avoid partial matches
    all_products.sort(key=lambda x: max(len(m) for m in x.get("match", [x["name"]])), reverse=True)
    
    links_added = 0
    details = []
    link_positions = []
    
    for product in all_products:
        if links_added >= max_links:
            break
        
        matches = product.get("match", [product["name"]])
        # Build regex pattern for all match terms
        pattern_str = r'\b(' + '|'.join(re.escape(m) for m in matches) + r')\b'
        pattern = re.compile(pattern_str, re.IGNORECASE)
        
        # Build the affiliate link
        url, link_type = build_affiliate_link(product["name"], product, site, tags)
        if not url:
            continue
        
        for match in pattern.finditer(html_content):
            pos = match.start()
            
            # Check if we're inside an existing link or heading
            before = html_content[max(0, pos - 500):pos]
            
            # Inside an <a> tag?
            preceding_a_close = before.rfind('</a>')
            preceding_a_open = before.rfind('<a ')
            if preceding_a_open > preceding_a_close:
                continue
            
            # Inside a heading?
            if re.search(r'<h[1-6][^>]*>[^<]*$', before, re.IGNORECASE):
                continue
            
            # Minimum spacing from last link
            if link_positions:
                text_between = html_content[link_positions[-1]:pos]
                word_count = len(text_between.split())
                if word_count < MIN_WORDS_BETWEEN_LINKS:
                    continue
            
            # Determine rel attribute based on link type
            if link_type == "internal":
                rel = 'rel="noopener"'
            elif link_type == "saas_direct":
                rel = 'rel="sponsored noopener"'
            elif link_type == "amazon":
                rel = 'rel="noopener nofollow"'
            else:
                rel = 'rel="noopener nofollow"'
            
            # Inject the link
            original = match.group()
            replacement = f'<a href="{url}" {rel} target="_blank">{original}</a>'
            html_content = html_content[:pos] + replacement + html_content[match.end():]
            
            links_added += 1
            details.append({
                "product": product["name"],
                "type": link_type,
                "url": url,
                "position": pos,
            })
            link_positions.append(pos + len(replacement))
            
            break  # First mention only
    
    return html_content, details, links_added


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
        products_data = load_products()
        saas_products = products_data.get("products", [])
        amazon_products = products_data.get("amazon_products", [])
        
        print(f"\nFound {len(posts)} recent posts.\n")
        print(f"{'Post ID':<10} {'Title':<50} {'Products Found':<30}")
        print("-" * 90)
        
        for post in posts:
            post_id = post['id']
            title = post['title']['rendered'][:48]
            content = post['content']['rendered']
            
            # Find all product mentions
            found_saas = []
            found_amazon = []
            
            for p in saas_products:
                for m in p.get("match", [p["name"]]):
                    if re.search(r'\b' + re.escape(m) + r'\b', content, re.IGNORECASE):
                        found_saas.append(p["name"])
                        break
            
            for p in amazon_products:
                for m in p.get("match", [p["name"]]):
                    if re.search(r'\b' + re.escape(m) + r'\b', content, re.IGNORECASE):
                        found_amazon.append(p["name"])
                        break
            
            # Check which are already linked
            all_found = found_saas + found_amazon
            already_linked = []
            for name in all_found:
                if f'>{name}</a>' in content or f'>{name.lower()}</a>' in content:
                    already_linked.append(name)
            
            unlinked = [p for p in all_found if p not in already_linked]
            status = f"{len(unlinked)} unlinked" if unlinked else "all linked"
            detail = ""
            if found_saas:
                detail += f"{len(found_saas)}S "
            if found_amazon:
                detail += f"{len(found_amazon)}A "
            print(f"{post_id:<10} {title:<50} {status:<30} {detail}")
        
        print(f"\nS = SaaS products, A = Amazon products")
    
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
        
        new_content, details, links_added = inject_links(content, site)
        
        if links_added == 0:
            print("No affiliate links injected (no matching products found or all already linked).")
            return
        
        print(f"\nInjected {links_added} affiliate links:")
        for d in details:
            print(f"  - {d['product']} ({d['type']}) -> {d['url'][:80]}...")
        
        if args.dry_run:
            print("\n[DRY RUN] Not updating the post.")
            log_injection(post_id, site, links_added, details, status="dry_run")
            return
        
        print(f"\nUpdating post {post_id}...")
        update_resp = requests.post(
            f"{base_url}/wp-json/wp/v2/posts/{post_id}",
            headers=headers,
            json={"content": new_content},
            timeout=30
        )
        
        if update_resp.status_code in (200, 201):
            print(f"Post {post_id} updated successfully.")
            log_injection(post_id, site, links_added, details, status="success")
        else:
            print(f"ERROR updating post: {update_resp.status_code} {update_resp.text[:200]}")
            log_injection(post_id, site, links_added, details, status="error")
    
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
        type_counts = {"internal": 0, "saas_direct": 0, "amazon": 0}
        
        for post in posts:
            post_id = post['id']
            content = post['content']['rendered']
            
            new_content, details, links_added = inject_links(content, site)
            
            if links_added == 0:
                continue
            
            # Count link types
            for d in details:
                type_counts[d['type']] = type_counts.get(d['type'], 0) + 1
            
            if args.dry_run:
                print(f"  Post {post_id}: {links_added} links (dry run)")
                for d in details:
                    print(f"    {d['product']} ({d['type']}) -> {d['url'][:70]}...")
                log_injection(post_id, site, links_added, details, status="dry_run")
            else:
                update_resp = requests.post(
                    f"{base_url}/wp-json/wp/v2/posts/{post_id}",
                    headers=headers,
                    json={"content": new_content},
                    timeout=30
                )
                if update_resp.status_code in (200, 201):
                    print(f"  Post {post_id}: {links_added} links injected")
                    for d in details:
                        print(f"    {d['product']} ({d['type']})")
                    log_injection(post_id, site, links_added, details, status="success")
                else:
                    print(f"  Post {post_id}: ERROR - {update_resp.status_code}")
                    log_injection(post_id, site, links_added, details, status="error")
            
            total_links += links_added
            total_posts += 1
        
        print(f"\nTotal: {total_links} links across {total_posts} posts")
        print(f"  Internal: {type_counts.get('internal', 0)}, SaaS direct: {type_counts.get('saas_direct', 0)}, Amazon: {type_counts.get('amazon', 0)}")
    
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
    
    # Filter to v2 entries only (after the fix)
    v2_entries = [e for e in entries if e.get('version') == '2.0']
    v1_entries = [e for e in entries if e.get('version') != '2.0']
    
    if v2_entries:
        total_links = sum(e.get('links_added', 0) for e in v2_entries)
        total_posts = len(set(e.get('post_id') for e in v2_entries if e.get('status') == 'success'))
        
        # Count by link type
        type_counts = {"internal": 0, "saas_direct": 0, "amazon": 0}
        product_counts = {}
        for entry in v2_entries:
            for d in entry.get('details', []):
                t = d.get('type', 'unknown')
                type_counts[t] = type_counts.get(t, 0) + 1
                product_counts[d['product']] = product_counts.get(d['product'], 0) + 1
        
        print("Affiliate Injection Stats (v2 - Hybrid Strategy)")
        print("=" * 50)
        print(f"Total v2 injections: {len(v2_entries)}")
        print(f"Total posts modified: {total_posts}")
        print(f"Total links added: {total_links}")
        print(f"\nBy link type:")
        for t, c in type_counts.items():
            print(f"  {t}: {c}")
        print(f"\nTop products linked:")
        for product, count in sorted(product_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {product}: {count}x")
    
    if v1_entries:
        print(f"\n(Legacy v1 entries: {len(v1_entries)} — these were reverted)")


def cmd_products(args):
    """Manage product registry."""
    data = load_products()
    
    if args.action == "list":
        saas = data.get("products", [])
        amazon = data.get("amazon_products", [])
        
        print(f"SaaS Products ({len(saas)}):")
        print("=" * 70)
        for p in saas:
            slug = p.get('internal_slug', 'none')
            print(f"  {p['name']:<25} {p.get('type','saas'):<8} {p['site']:<20} slug: {slug}")
        
        print(f"\nAmazon Products ({len(amazon)}):")
        print("=" * 70)
        for p in amazon:
            print(f"  {p['name']:<25} ASIN: {p.get('asin','N/A'):<15} {p['category']}")
    
    elif args.action == "add":
        print("Edit scripts/affiliate_products.json directly to add products.")
    
    elif args.action == "remove":
        print("Edit scripts/affiliate_products.json directly to remove products.")


def main():
    parser = argparse.ArgumentParser(description="Affiliate Link Injector v2 (Hybrid Strategy)")
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