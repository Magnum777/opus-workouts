"""
Amazon Affiliate Link Injector
Scans published WordPress articles for product mentions and injects
Amazon affiliate links where they don't already exist.

Usage: python amazon_affiliate_injector.py [--dry-run]
"""

import requests
import json
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add creds.py to import path
sys.path.insert(0, str(Path(__file__).parent))
from creds import get_wp_site, get_wp_auth_header

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
STATE_FILE = WORKSPACE / "scripts" / "affiliate_inject_state.json"
TRACKING_ID = "layeredmedial-20"

SITES = {
    "aitoolalliance": {
        "api": "https://aitoolalliance.com/wp-json/wp/v2/posts",
        "site_name": "aitoolalliance",
    },
    "aibusinessinsider": {
        "api": "https://aibusinessinsider.org/wp-json/wp/v2/posts",
        "site_name": "aibusinessinsider",
    },
    "aicofounderstack": {
        "api": "https://aicofounderstack.com/wp-json/wp/v2/posts",
        "site_name": "aicofounderstack",
    },
}

PRODUCTS = {
    # Books
    "Atomic Habits": "B07D23CFGR",
    "Deep Work": "B00X47ZVXM",
    "The Lean Startup": "B005PR422K",
    "Zero to One": "B00J6YBOFQ",
    "Thinking, Fast and Slow": "B00555X8OA",
    "The 4-Hour Workweek": "B002WE6QV4",
    "Essentialism": "B00G1J1D5E",
    "Hooked": "B00LMGLXTS",
    "Start with Why": "B074VF2ZJ6",
    "Never Split the Difference": "B014DUR7L2",
    "Radical Candor": "B01HRLUV2G",
    "Measure What Matters": "B078Y9RP56",
    "The Hard Thing About Hard Things": "B00DQ845EA",
    "Mindset": "B000QCS8TW",
    "Grit": "B010MH9V3W",
    "Innovator's Dilemma": "B00E257S7E",
    "Business Model Generation": "B00E3FP4OE",
    "Crossing the Chasm": "B000FC1J8I",
    "Traction": "B00TY3ZOMS",
    "Good to Great": "B0058DRUV6",
    # Audio / Video
    "Blue Yeti": "B002VA464S",
    "Rode NT-USB": "B00KQPGRRE",
    "Logitech C920": "B006JH8T3S",
    # Tablets / Computers
    "Kindle Paperwhite": "B08KTZ8249",
    "MacBook Air": "B0B3C2R8MP",
    "MacBook Pro": "B0B3C54BKD",
    "Samsung T7": "B0874XWW23",
    "Samsung T7 Shield": "B09ZDTN9XY",
    # Headphones
    "Sony WH-1000XM4": "B0863TXGM3",
    "Sony WH-1000XM5": "B09XS7JWHH",
    "AirPods Pro": "B0DHTYW7P5",
    "AirPods": "B0DHTYV3V4",
    # Tablets
    "iPad": "B0D3J7Z8P9",
    "iPad Pro": "B0D3J6W7WS",
    # Peripherals
    "MX Master": "B09VCC7L2J",
    "MX Master 3S": "B09VCC7L2J",
    "Logitech MX Keys": "B07S92Q6J1",
    "Stream Deck": "B06XKNZT1P",
    "Elgato Stream Deck": "B06XKNZT1P",
    "LG UltraFine": "B08DHLGQ9M",
    "LG 27UN880": "B08DHLGQ9M",
    "Dell UltraSharp": "B0932VJTGD",
    "Anker Hub": "B07ZVKTP53",
    "Anker PowerExpand": "B07ZVKTP53",
    "CalDigit TS4": "B09GK7B9G1",
    "Thunderbolt Dock": "B09GK7B9G1",
    # Furniture
    "Herman Miller": "B0894N1YGX",
    "Herman Miller Aeron": "B0894N1YGX",
    "Steelcase Gesture": "B07ZVKTP53",
    "Fully Jarvis": "B07ZVKTP53",
    "Uplift Desk": "B07ZVKTP53",
    "Autonomous Desk": "B07ZVKTP53",
    # Cameras
    "Razer Kiyo": "B07Q9T4Q2B",
    "Canon EOS": "B08J7S3B3X",
    "Fujifilm X100V": "B08J7S3B3X",
    # Drones
    "DJI Mini": "B09G4BZT5V",
    "DJI Mini 3": "B09G4BZT5V",
    "DJI Mini 4 Pro": "B0CHJX7G1P",
    "GoPro Hero": "B0B6K6R2G7",
    "GoPro Hero 12": "B0B6K6R2G7",
    "Insta360": "B0B7GJ1ZQ1",
    "Insta360 X3": "B0B7GJ1ZQ1",
}


def load_state():
    """Load the inject state from JSON file."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"processed": {}, "history": []}


def save_state(state):
    """Save the inject state to JSON file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_recent_posts(site_key, days=3):
    """Fetch recent published posts from a WordPress site."""
    site = SITES[site_key]
    after = (datetime.now() - timedelta(days=days)).isoformat()
    url = f"{site['api']}?after={after}&per_page=20&_embed"

    try:
        r = requests.get(url, timeout=30)
        if r.status_code == 200:
            try:
                return r.json()
            except:
                print(f"  WARN: Non-JSON response from {site_key}")
                return []
    except Exception as e:
        print(f"ERROR fetching {site_key}: {e}")

    return []


def has_amazon_link(content, product):
    """Check if content already has an Amazon affiliate link for this product."""
    patterns = [
        f"amazon\\.com/dp/\\w+.*tag={re.escape(TRACKING_ID)}",
        f"amazon\\.com/gp/product/\\w+.*tag={re.escape(TRACKING_ID)}",
    ]
    for pattern in patterns:
        if re.search(pattern, content, re.I):
            return True
    return False


def find_product_mentions(content):
    """Find product mentions in content that aren't already linked."""
    mentions = []
    content_lower = content.lower()

    for product, asin in PRODUCTS.items():
        # Skip if already has an affiliate link
        if has_amazon_link(content, product):
            continue

        # Find all occurrences of the product name
        pattern = rf"\b{re.escape(product.lower())}\b"
        matches = list(re.finditer(pattern, content_lower))

        for match in matches:
            idx = match.start()

            # Get context around the match
            context_start = max(0, idx - 80)
            context_end = min(len(content), idx + len(product) + 80)
            context = content[context_start:context_end]

            # Check if already inside an HTML link
            if "<a" in context and "</a>" in context:
                link_start = content.rfind("<a", 0, idx)
                link_end = content.find("</a>", idx)
                if link_start != -1 and link_end != -1 and link_start < idx < link_end:
                    continue  # Already inside a link

            mentions.append(
                {
                    "product": product,
                    "asin": asin,
                    "position": idx,
                    "context": context,
                }
            )

    return mentions


def inject_affiliate_links(content, mentions):
    """Inject affiliate links into content for product mentions."""
    if not mentions:
        return content, 0

    # Sort mentions by position (reverse to avoid offset issues)
    sorted_mentions = sorted(mentions, key=lambda x: x["position"], reverse=True)
    modified = content
    injected = 0

    for mention in sorted_mentions:
        product = mention["product"]
        asin = mention["asin"]
        pos = mention["position"]

        # Build the affiliate link
        link = f"https://www.amazon.com/dp/{asin}?tag={TRACKING_ID}"

        # Find the product name in the modified content
        pattern = re.compile(re.escape(product), re.I)
        match = pattern.search(modified, pos if pos < len(modified) else 0)
        if not match:
            continue

        start, end = match.span()

        # Check context before the match
        before = modified[:start]
        after = modified[end:]

        # Skip if already inside an <a> tag
        last_a = before.rfind("<a")
        last_close_a = before.rfind("</a>")
        if last_a > last_close_a:
            continue  # Already inside a link tag

        # Create the linked text
        linked_text = f'<a href="{link}" target="_blank" rel="nofollow sponsored">{modified[start:end]}</a>'
        modified = before + linked_text + after
        injected += 1

    return modified, injected


def update_post(site_key, post_id, new_content):
    """Update a WordPress post with new content via REST API."""
    creds = get_wp_site(site_key)
    if not creds:
        return False, "No credentials"

    headers = get_wp_auth_header(site_key)

    url = f"{creds['url']}/wp-json/wp/v2/posts/{post_id}"
    data = {"content": new_content}

    try:
        r = requests.post(url, json=data, headers=headers, timeout=30)
        if r.status_code in (200, 201):
            return True, "Updated"
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def main(dry_run=False):
    """Main entry point: scan posts and inject affiliate links."""
    state = load_state()
    now = datetime.now().isoformat()
    total_injected = 0
    total_posts = 0
    results = []

    print(f"=== Amazon Affiliate Injector {'(DRY RUN)' if dry_run else ''} ===")
    print(f"Tracking ID: {TRACKING_ID}")
    print(f"Products in catalog: {len(PRODUCTS)}")
    print()

    for site_key, site_info in SITES.items():
        print(f"Checking {site_key}...")
        posts = fetch_recent_posts(site_key, days=3)

        for post in posts:
            post_id = post.get("id")
            title = post.get("title", {}).get("rendered", "")
            content = post.get("content", {}).get("rendered", "")
            link = post.get("link", "")
            date = post.get("date", "")

            if not post_id or not content:
                continue

            post_key = f"{site_key}:{post_id}"

            # Skip if already processed
            if post_key in state.get("processed", {}):
                continue

            total_posts += 1

            # Find product mentions
            mentions = find_product_mentions(content)

            if not mentions:
                # Mark as processed (no products found)
                state.setdefault("processed", {})[post_key] = now
                continue

            # Inject affiliate links
            new_content, injected = inject_affiliate_links(content, mentions)

            result = {
                "site": site_key,
                "post_id": post_id,
                "title": title,
                "link": link,
                "date": date,
                "mentions_found": len(mentions),
                "injected": injected,
            }

            if injected > 0 and not dry_run:
                success, msg = update_post(site_key, post_id, new_content)
                result["update_success"] = success
                result["update_msg"] = msg
                if success:
                    total_injected += injected
                    state.setdefault("processed", {})[post_key] = now
                else:
                    print(f"  FAILED to update {title}: {msg}")
            elif injected > 0 and dry_run:
                result["update_success"] = None
                result["update_msg"] = "DRY RUN - not posted"
                total_injected += injected
            else:
                state.setdefault("processed", {})[post_key] = now

            results.append(result)

    # Build summary
    summary = ""
    for r in results:
        if r["injected"] > 0:
            status = "✅" if r.get("update_success") else "🔶" if r.get("update_success") is None else "❌"
            summary += f"{status} [{r['site']}:{r['post_id']}] {r['title'][:60]}\n"
            summary += f"  {r['mentions_found']} mentions, {r['injected']} linked\n"
            summary += f"  <{r['link']}>\n"

    if total_injected > 0:
        summary += f"\nTracking ID: `{TRACKING_ID}`"

    print(summary)

    # Save state
    save_state(state)

    return {
        "status": "ok",
        "posts_checked": total_posts,
        "links_injected": total_injected,
        "dry_run": dry_run,
        "results": results,
        "discord_summary": summary,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Show what would be injected without modifying posts")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
