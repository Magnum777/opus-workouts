#!/usr/bin/env python3
"""
Amazon Affiliate Topic Generator v2
Generates high-converting affiliate article topics with natural titles.
Outputs to a JSON queue file that amazon_publish_from_queue.py consumes.

Usage:
    python amazon_topic_generator.py                  # Generate 5 topics
    python amazon_topic_generator.py --count 10      # Generate 10 topics
    python amazon_topic_generator.py --category tech  # Focus on a category
    python amazon_topic_generator.py --list           # List categories
    python amazon_topic_generator.py --queue          # Show queue
"""

import argparse
import json
import hashlib
import random
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
QUEUE_FILE = WORKSPACE / "scripts" / "amazon_queue.json"
STATE_FILE = WORKSPACE / "scripts" / "amazon_pipeline_state.json"

CATEGORIES = {
    "tech_gadgets": {
        "name": "Tech Gadgets & Electronics",
        "commission": "2.5-4%",
        "site_focus": {
            "aitoolalliance": "AI tools, productivity gadgets, smart home",
            "aicofounderstack": "Founder tech stack, startup gear",
        }
    },
    "home_office": {
        "name": "Home Office & Remote Work",
        "commission": "3-4.5%",
        "site_focus": {
            "aitoolalliance": "Remote work productivity, home office essentials",
            "aicofounderstack": "Founder office build-outs",
        }
    },
    "ai_software": {
        "name": "AI Software & SaaS Tools",
        "commission": "2-3%",
        "site_focus": {
            "aitoolalliance": "Free and freemium AI tools for small business",
            "aibusinessinsider": "Enterprise AI platforms and ROI analysis",
            "aicofounderstack": "AI cofounder tools, solopreneur automation",
        }
    },
    "security": {
        "name": "Cybersecurity & Privacy",
        "commission": "3-4%",
        "site_focus": {
            "aitoolalliance": "Small business security essentials",
            "aibusinessinsider": "Enterprise security stack",
        }
    },
    "networking": {
        "name": "Networking & Infrastructure",
        "commission": "2.5-3%",
        "site_focus": {
            "aitoolalliance": "Home office networking and Wi-Fi",
            "aibusinessinsider": "Small business infrastructure",
        }
    },
    "books_courses": {
        "name": "Books & Online Courses",
        "commission": "4.5%",
        "site_focus": {
            "aitoolalliance": "AI and productivity books for small business",
            "aibusinessinsider": "Business leadership and strategy books",
            "aicofounderstack": "Founder and startup books",
        }
    },
}

# Pre-written title templates that sound natural and convert well
# Each tuple is (template, audience_type) where audience_type maps to site
TITLE_TEMPLATES = {
    "aitoolalliance": [
        "{N} Best {keyword} for Small Business Owners in {year}",
        "Best {keyword} for Remote Workers: {N} Tested Picks ({year})",
        "The Small Business {keyword} Guide: {N} Tools Worth Your Money",
        "{keyword} That Actually Save Time: Our Top {N} Picks for {year}",
        "Best {keyword} Under ${price}: {N} Budget Picks for Small Teams",
        "We Tested {N} {keyword} for Productivity — These Actually Work",
        "The Ultimate {keyword} Stack for Freelancers in {year}",
        "{N} {keyword} Every Small Business Needs Right Now",
        "Best {keyword} for Solopreneurs: {year} Buyer's Guide",
        "The {N} Best {keyword} for Working From Home ({year} Edition)",
    ],
    "aibusinessinsider": [
        "Best {keyword} for Enterprise Teams: {N} Top Picks for {year}",
        "The C-Suite Guide to {keyword}: {N} Solutions That Deliver ROI",
        "{keyword} for Business Leaders: {N} Tools Worth the Investment",
        "Enterprise {keyword} Comparison: {N} Leaders for {year}",
        "Best {keyword} for IT Directors: {N} Reviewed and Ranked",
        "{N} {keyword} Every CTO Should Evaluate in {year}",
        "How to Choose {keyword} for Your Business ({year} Guide)",
        "The Business Case for {keyword}: {N} Platforms That Deliver",
        "{keyword} ROI Analysis: {N} Tools That Pay for Themselves",
        "Best {keyword} for Growing Companies in {year}",
    ],
    "aicofounderstack": [
        "The Solo Founder's {keyword} Guide: {N} Essentials for {year}",
        "Best {keyword} for Indie Hackers: {N} Tools That Actually Help",
        "{N} {keyword} Every Startup Founder Needs in {year}",
        "{keyword} for Bootstrapped Founders: {N} Picks Under ${price}",
        "The AI Founder's {keyword} Stack: {N} Tools That Replace a Team",
        "Best {keyword} for First-Time Founders ({year} Edition)",
        "{N} {keyword} Worth Buying if You're a Solo Entrepreneur",
        "The {keyword} Every Startup Needs (And {N} That Don't Work)",
        "Building on a Budget: {N} {keyword} for Under ${price}",
        "{keyword} for Solo Founders: {N} Tools I Actually Use in {year}",
    ],
}

CATEGORY_KEYWORDS = {
    "tech_gadgets": ["smart home devices", "wearable tech", "productivity gadgets", "wireless chargers", "desk accessories", "portable monitors", "smart speakers", "webcams", "mechanical keyboards", "USB-C hubs", "noise cancelling headphones", "digital planners", "second monitors", "presentation clickers", "lap desks"],
    "home_office": ["standing desks", "ergonomic chairs", "monitor arms", "desk mats", "webcams", "microphones", "ring lights", "cable management", "docking stations", "desk organizers", "keyboard trays", "footrests", "desk lamps", "whiteboards", "webcam covers"],
    "ai_software": ["AI writing tools", "AI coding assistants", "AI image generators", "AI video editors", "AI chatbot platforms", "AI SEO tools", "AI analytics software", "AI automation tools", "AI note taking apps", "AI research tools", "AI meeting assistants", "AI design tools", "AI email tools", "AI project management", "AI CRM tools"],
    "security": ["VPN services", "password managers", "firewall appliances", "encrypted drives", "cloud backup services", "identity protection", "secure routers", "2FA security keys", "privacy screens", "antivirus software"],
    "networking": ["mesh Wi-Fi systems", "NAS devices", "network switches", "business routers", "fiber converters", "server racks", "UPS battery backups", "cable testers", "PoE switches", "SD-WAN solutions"],
    "books_courses": ["AI books", "startup books", "leadership books", "programming courses", "business strategy books", "entrepreneur books", "productivity books", "data science courses", "management books", "investing books"],
}

AUDIENCES = {
    "aitoolalliance": ["Small Business Owners", "Freelancers", "Remote Workers", "Solopreneurs", "Startups"],
    "aibusinessinsider": ["Enterprise Teams", "C-Suite Executives", "IT Directors", "Business Analysts", "Product Managers"],
    "aicofounderstack": ["Solo Founders", "Indie Hackers", "AI Entrepreneurs", "First-Time CEOs", "Bootstrapped Founders"],
}


def load_queue():
    if QUEUE_FILE.exists():
        try:
            data = json.loads(QUEUE_FILE.read_text(encoding='utf-8'))
            if isinstance(data, dict) and "topics" in data:
                return data
        except (json.JSONDecodeError, ValueError) as e:
            print(f"WARN: Corrupted queue file, using defaults: {e}", file=sys.stderr)
    return {"version": 2, "created": datetime.now().isoformat(), "topics": [], "published": [], "failed": []}


def save_queue(queue):
    QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding='utf-8')


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, ValueError) as e:
            print(f"WARN: Corrupted state file, using defaults: {e}", file=sys.stderr)
    return {"published": {}, "queue": [], "last_run": None}


def generate_topic_id(title, site):
    raw = f"{site}:{title}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def generate_topics(count=5, category=None):
    queue = load_queue()
    state = load_state()

    # Collect all existing titles for dedup
    used_titles = set()
    for info in state.get("published", {}).values():
        t = info.get("title", "").lower()
        if t:
            used_titles.add(t)
    for topic in queue.get("topics", []):
        used_titles.add(topic.get("title", "").lower())
    for topic in queue.get("published", []):
        used_titles.add(topic.get("title", "").lower())
    for topic in queue.get("failed", []):
        used_titles.add(topic.get("title", "").lower())

    cats = {category: CATEGORIES[category]} if category and category in CATEGORIES else CATEGORIES

    new_topics = []
    attempts = 0
    max_attempts = count * 20

    while len(new_topics) < count and attempts < max_attempts:
        attempts += 1
        cat_key = random.choice(list(cats.keys()))
        cat = cats[cat_key]

        # Pick site that has this category
        available_sites = list(cat["site_focus"].keys())
        site = random.choice(available_sites)
        site_focus = cat["site_focus"][site]

        # Pick keyword and title template for this site
        keyword = random.choice(CATEGORY_KEYWORDS.get(cat_key, ["tools"]))
        template = random.choice(TITLE_TEMPLATES.get(site, TITLE_TEMPLATES["aitoolalliance"]))

        year = random.choice([2026, 2027])
        price = random.choice([50, 100, 150, 200, 500])
        n = random.choice([5, 7, 8, 10, 12, 15])

        title = template.format(N=n, keyword=keyword, year=year, price=price)

        # Dedup
        if title.lower() in used_titles:
            continue
        topic_id = generate_topic_id(title, site)
        if any(t.get("id") == topic_id for t in new_topics):
            continue

        # Clean slug
        slug = title.lower()
        for ch in ["—", "–", ":", ",", ".", "(", ")"]:
            slug = slug.replace(ch, "")
        slug = slug.replace(" ", "-")
        slug = "".join(c for c in slug if c.isalnum() or c == "-")[:80].rstrip("-")

        new_topic = {
            "id": topic_id,
            "title": title,
            "slug": slug,
            "site": site,
            "category": cat_key,
            "category_name": cat["name"],
            "site_focus": site_focus,
            "keyword": keyword,
            "commission_range": cat["commission"],
            "status": "queued",
            "created": datetime.now().isoformat(),
            "article_type": "post",
            "target_word_count": random.choice([1200, 1500, 1800]),
            "notes": f"Focus: {site_focus}. Target {cat['commission']} commission."
        }

        new_topics.append(new_topic)
        used_titles.add(title.lower())

    queue["topics"].extend(new_topics)
    queue["last_generated"] = datetime.now().isoformat()
    save_queue(queue)

    print(f"Generated {len(new_topics)} new topics (attempted {attempts})")
    print(f"Queue now has {len(queue['topics'])} topics\n")
    for t in new_topics:
        print(f"  [{t['site']}] {t['title']}")
        print(f"    Category: {t['category_name']} | Commission: {t['commission_range']}")
        print(f"    Focus: {t['site_focus']}\n")

    return new_topics


def list_categories():
    print("=== Amazon Affiliate Topic Categories ===\n")
    for key, cat in CATEGORIES.items():
        print(f"  {key}: {cat['name']} ({cat['commission']} commission)")
        sites = ", ".join(cat["site_focus"].keys())
        print(f"    Sites: {sites}\n")


def show_queue():
    queue = load_queue()
    queued = [t for t in queue.get("topics", []) if t.get("status") == "queued"]
    published = queue.get("published", [])
    failed = queue.get("failed", [])

    print(f"=== Amazon Affiliate Queue ({len(queued)} queued, {len(published)} published, {len(failed)} failed) ===\n")

    # Group queued by site
    by_site = {}
    for t in queued:
        by_site.setdefault(t["site"], []).append(t)
    for site, topics in sorted(by_site.items()):
        print(f"  {site} ({len(topics)} queued):")
        for t in topics[:5]:
            print(f"    - {t['title']}")
            print(f"      {t['category_name']} | {t['commission_range']}")
        if len(topics) > 5:
            print(f"    ... and {len(topics) - 5} more")
        print()

    if published:
        print(f"  Recently published:")
        for t in published[-3:]:
            print(f"    - [{t['site']}] {t['title']}")
            print(f"      {t.get('link', '?')}")

    if failed:
        print(f"\n  Failed:")
        for t in failed[-3:]:
            print(f"    - [{t['site']}] {t['title']}: {t.get('error', '?')}")


def main():
    parser = argparse.ArgumentParser(description="Generate Amazon affiliate article topics")
    parser.add_argument("--count", type=int, default=5, help="Number of topics to generate")
    parser.add_argument("--category", type=str, help="Focus on a specific category")
    parser.add_argument("--list", action="store_true", help="List available categories")
    parser.add_argument("--queue", action="store_true", help="Show current queue")
    parser.add_argument("--reset", action="store_true", help="Clear the queue (keep published history)")

    args = parser.parse_args()

    if args.list:
        list_categories()
        return
    if args.queue:
        show_queue()
        return
    if args.reset:
        queue = load_queue()
        queue["topics"] = []
        save_queue(queue)
        print("Queue cleared. Published history preserved.")
        return

    generate_topics(count=args.count, category=args.category)


if __name__ == "__main__":
    main()