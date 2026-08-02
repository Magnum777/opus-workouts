#!/usr/bin/env python3
"""
Affiliate Content Upgrade — Amazon Affiliate Pipeline Extension
================================================================
Adds three new article types to the existing Amazon affiliate pipeline:
    1. Comparison Articles   — head-to-head product comparisons with tables
    2. Buying Guides         — educational buyer's guides
    3. Product Reviews       — single-product deep dives

Output is JSON-compatible with the existing amazon_queue.json format used
by amazon_publish_from_queue.py. The new `article_type` field distinguishes
content types ("comparison", "buying_guide", "product_review").

Usage:
    python affiliate_content_upgrade.py                    # Generate 5 mixed topics
    python affiliate_content_upgrade.py --count 10         # Generate 10 mixed topics
    python affiliate_content_upgrade.py --type comparison  # Generate comparisons only
    python affiliate_content_upgrade.py --site aitoolalliance --type buying_guide
    python affiliate_content_upgrade.py --status           # Show queue + upgrade stats
    python affiliate_content_upgrade.py --append           # Append to amazon_queue.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Shared constants with amazon_topic_generator.py (redefined here for
# standalone import-safety; keep in sync.)
# ---------------------------------------------------------------------------

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
QUEUE_FILE = WORKSPACE / "scripts" / "amazon_queue.json"
STATE_FILE = WORKSPACE / "scripts" / "amazon_pipeline_state.json"

# ---------------------------------------------------------------------------
# 1. CATEGORIES (mirrors amazon_topic_generator.py)
# ---------------------------------------------------------------------------

CATEGORIES = {
    "tech_gadgets": {
        "name": "Tech Gadgets & Electronics",
        "commission": "2.5-4%",
        "site_focus": {
            "aitoolalliance": "AI tools, productivity gadgets, smart home",
            "aicofounderstack": "Founder tech stack, startup gear",
        },
    },
    "home_office": {
        "name": "Home Office & Remote Work",
        "commission": "3-4.5%",
        "site_focus": {
            "aitoolalliance": "Remote work productivity, home office essentials",
            "aicofounderstack": "Founder office build-outs",
        },
    },
    "ai_software": {
        "name": "AI Software & SaaS Tools",
        "commission": "2-3%",
        "site_focus": {
            "aitoolalliance": "Free and freemium AI tools for small business",
            "aibusinessinsider": "Enterprise AI platforms and ROI analysis",
            "aicofounderstack": "AI cofounder tools, solopreneur automation",
        },
    },
    "security": {
        "name": "Cybersecurity & Privacy",
        "commission": "3-4%",
        "site_focus": {
            "aitoolalliance": "Small business security essentials",
            "aibusinessinsider": "Enterprise security stack",
        },
    },
    "networking": {
        "name": "Networking & Infrastructure",
        "commission": "2.5-3%",
        "site_focus": {
            "aitoolalliance": "Home office networking and Wi-Fi",
            "aibusinessinsider": "Small business infrastructure",
        },
    },
    "books_courses": {
        "name": "Books & Online Courses",
        "commission": "4.5%",
        "site_focus": {
            "aitoolalliance": "AI and productivity books for small business",
            "aibusinessinsider": "Business leadership and strategy books",
            "aicofounderstack": "Founder and startup books",
        },
    },
}

# ---------------------------------------------------------------------------
# 2. KEYWORD & AUDIENCE POOLS (mirrors amazon_topic_generator.py)
# ---------------------------------------------------------------------------

CATEGORY_KEYWORDS = {
    "tech_gadgets": [
        "smart home devices", "wearable tech", "productivity gadgets",
        "wireless chargers", "desk accessories", "portable monitors",
        "smart speakers", "webcams", "mechanical keyboards", "USB-C hubs",
        "noise cancelling headphones", "digital planners", "second monitors",
        "presentation clickers", "lap desks",
    ],
    "home_office": [
        "standing desks", "ergonomic chairs", "monitor arms", "desk mats",
        "webcams", "microphones", "ring lights", "cable management",
        "docking stations", "desk organizers", "keyboard trays", "footrests",
        "desk lamps", "whiteboards", "webcam covers",
    ],
    "ai_software": [
        "AI writing tools", "AI coding assistants", "AI image generators",
        "AI video editors", "AI chatbot platforms", "AI SEO tools",
        "AI analytics software", "AI automation tools", "AI note taking apps",
        "AI research tools", "AI meeting assistants", "AI design tools",
        "AI email tools", "AI project management", "AI CRM tools",
    ],
    "security": [
        "VPN services", "password managers", "firewall appliances",
        "encrypted drives", "cloud backup services", "identity protection",
        "secure routers", "2FA security keys", "privacy screens",
        "antivirus software",
    ],
    "networking": [
        "mesh Wi-Fi systems", "NAS devices", "network switches",
        "business routers", "fiber converters", "server racks",
        "UPS battery backups", "cable testers", "PoE switches", "SD-WAN solutions",
    ],
    "books_courses": [
        "AI books", "startup books", "leadership books", "programming courses",
        "business strategy books", "entrepreneur books", "productivity books",
        "data science courses", "management books", "investing books",
    ],
}

AUDIENCES = {
    "aitoolalliance": [
        "Small Business Owners", "Freelancers", "Remote Workers",
        "Solopreneurs", "Startups",
    ],
    "aibusinessinsider": [
        "Enterprise Teams", "C-Suite Executives", "IT Directors",
        "Business Analysts", "Product Managers",
    ],
    "aicofounderstack": [
        "Solo Founders", "Indie Hackers", "AI Entrepreneurs",
        "First-Time CEOs", "Bootstrapped Founders",
    ],
}

# ---------------------------------------------------------------------------
# 3. TITLE TEMPLATES — 15+ per site per new article type
# ---------------------------------------------------------------------------

# ── Type 1: Comparison Articles ──
COMPARISON_TEMPLATES: dict[str, list[str]] = {
    "aitoolalliance": [
        "{A} vs {B}: Which {keyword} Is Better for {audience}?",
        "{A} vs {B} vs {C}: {keyword} Showdown for {audience} ({year})",
        "{A} or {B}? The Best {keyword} for {audience} ({year})",
        "{A} vs {B}: Honest Comparison for {audience} in {year}",
        "{keyword} Battle: {A} vs {B} for {audience} ({year})",
        "{A} vs {B} vs {C}: Which {keyword} Wins for {audience}?",
        "{A} vs {B}: A {audience}'s Guide to Choosing {keyword} in {year}",
        "Side-by-Side: {A} vs {B} ({keyword}) for {audience} ({year})",
        "{A} vs {B}: {keyword} Tested by {audience} in {year}",
        "{keyword} Showdown: {A} vs {B} vs {C} for {audience} ({year})",
        "{A} vs {B}: The {keyword} Showdown Every {audience} Needs to See",
        "{A} vs {B}: Real-World {keyword} Comparison for {audience}",
        "Which {keyword} Should {audience} Buy? {A} vs {B} ({year})",
        "{A} vs {B} vs {C}: Best {keyword} Reviewed for {audience}",
        "The Ultimate {keyword} Face-Off: {A} vs {B} for {audience} ({year})",
    ],
    "aibusinessinsider": [
        "{A} vs {B}: Enterprise {keyword} Comparison for {audience} ({year})",
        "{A} vs {B} vs {C}: {keyword} Showdown for {audience} ({year})",
        "Enterprise {keyword} Face-Off: {A} vs {B} for {audience}",
        "{A} or {B}? Choosing {keyword} for {audience} in {year}",
        "{A} vs {B}: ROI Analysis for {audience} Buying {keyword}",
        "{A} vs {B} vs {C}: Best {keyword} for {audience} Reviewed ({year})",
        "{keyword} Comparison: {A} vs {B} for {audience} ({year})",
        "{A} vs {B}: A {audience}'s Guide to {keyword} in {year}",
        "{A} vs {B} vs {C}: Enterprise-Grade {keyword} for {audience}",
        "{A} vs {B}: Which {keyword} Delivers for {audience}? ({year})",
        "Head-to-Head: {A} vs {B} ({keyword}) for {audience}",
        "{A} vs {B}: {keyword} Showdown for {audience} in {year}",
        "{keyword} Battle: {A} vs {B} for {audience} ({year})",
        "{A} vs {B} vs {C}: The {audience} Guide to {keyword}",
        "{A} vs {B}: Enterprise {keyword} Showdown ({year})",
    ],
    "aicofounderstack": [
        "{A} vs {B}: Best {keyword} for {audience} in {year}",
        "{A} vs {B} vs {C}: {keyword} Showdown for {audience} ({year})",
        "Solo Founder Showdown: {A} vs {B} ({keyword}) for {audience}",
        "{A} or {B}? The {keyword} Every {audience} Should Compare ({year})",
        "{A} vs {B}: A Bootstrapped Founder's Guide to {keyword}",
        "{A} vs {B} vs {C}: Best {keyword} for {audience} ({year})",
        "{A} vs {B}: Which {keyword} Is Worth It for {audience}?",
        "{A} vs {B}: Honest {keyword} Comparison for {audience} ({year})",
        "{keyword} Face-Off: {A} vs {B} for {audience} in {year}",
        "{A} vs {B} vs {C}: The {audience} Guide to {keyword} ({year})",
        "{A} vs {B}: {keyword} Showdown for Bootstrapped {audience}",
        "{A} vs {B}: Which {keyword} Do {audience} Actually Use?",
        "{keyword} Battle: {A} vs {B} for {audience} ({year})",
        "{A} vs {B}: Founder's Guide to Choosing {keyword} in {year}",
        "{A} vs {B} vs {C}: Best {keyword} Tested by {audience}",
    ],
}

# ── Type 2: Buying Guides ──
BUYING_GUIDE_TEMPLATES: dict[str, list[str]] = {
    "aitoolalliance": [
        "How to Choose {keyword} for {audience}: The {year} Buying Guide",
        "The Complete {keyword} Buying Guide for {audience} ({year})",
        "{audience}'s Guide to Buying {keyword} in {year}",
        "What to Look for in {keyword}: A {audience} Buyer's Guide ({year})",
        "The {year} {keyword} Buying Guide for {audience}",
        "Everything {audience} Need to Know Before Buying {keyword} ({year})",
        "{keyword} Buying Guide: Tips for {audience} in {year}",
        "How {audience} Can Choose the Best {keyword} ({year} Edition)",
        "A Practical {keyword} Buying Guide for {audience} ({year})",
        "Before You Buy: {keyword} Guide for {audience} in {year}",
        "The Smart {audience} Guide to {keyword} ({year})",
        "{keyword} Buying Guide: What {audience} Should Know in {year}",
        "How to Pick the Right {keyword} for {audience} ({year})",
        "{audience} Guide: Buying {keyword} Without the Headache ({year})",
        "The No-Nonsense {keyword} Buying Guide for {audience} ({year})",
    ],
    "aibusinessinsider": [
        "How to Choose Enterprise {keyword} for {audience}: {year} Guide",
        "The Complete {keyword} Buying Guide for {audience} ({year})",
        "{audience}'s Guide to Procuring {keyword} in {year}",
        "What {audience} Should Look for in {keyword} ({year} Buying Guide)",
        "Enterprise {keyword} Buying Guide for {audience} ({year})",
        "The Strategic {keyword} Buying Guide for {audience} ({year})",
        "How {audience} Evaluate {keyword}: A {year} Buyer's Guide",
        "{keyword} Procurement Guide for {audience} in {year}",
        "Buying {keyword} for {audience}: The {year} Decision Framework",
        "The {audience} Playbook for Buying {keyword} ({year})",
        "How to Choose {keyword} That Deliver ROI for {audience} ({year})",
        "{keyword} Buying Guide: What Enterprise {audience} Need to Know ({year})",
        "A Practical {keyword} Procurement Guide for {audience} ({year})",
        "{audience} Guide: Evaluating and Buying {keyword} in {year}",
        "The Executive {keyword} Buying Guide for {audience} ({year})",
    ],
    "aicofounderstack": [
        "How to Choose {keyword} for {audience}: The {year} Buying Guide",
        "The Bootstrapped Founder's Guide to Buying {keyword} ({year})",
        "{audience}'s Guide: Buying {keyword} on a Budget ({year})",
        "What {audience} Should Look for in {keyword} ({year} Edition)",
        "The Complete {keyword} Buying Guide for {audience} ({year})",
        "How Solo Founders Choose {keyword}: A {year} Buyer's Guide",
        "{keyword} Buying Guide: Smart Picks for {audience} in {year}",
        "A Founder's Guide to {keyword} Without Overspending ({year})",
        "How to Pick {keyword} That Scale With Your {audience} Journey ({year})",
        "The Indie Founder's {keyword} Buying Guide ({year})",
        "{audience} Guide: Getting the Most Value From {keyword} ({year})",
        "Before You Buy {keyword}: A Guide for {audience} in {year}",
        "The Frugal Founder's {keyword} Buying Guide ({year})",
        "{keyword} Buying Guide: What {audience} Actually Need ({year})",
        "How to Choose {keyword} That Won't Break the Bank ({audience}, {year})",
    ],
}

# ── Type 3: Product Reviews (single-product) ──
PRODUCT_REVIEW_TEMPLATES: dict[str, list[str]] = {
    "aitoolalliance": [
        "Is {product_name} Worth It? Honest Review for {audience}",
        "I Used {product_name} for 30 Days — Here's My Honest Take",
        "{product_name} Review: Does It Work for {audience}?",
        "{product_name} Honest Review: A {audience}'s Perspective ({year})",
        "Is {product_name} the Best {keyword} for {audience}? ({year})",
        "{product_name} Deep Dive: What {audience} Should Know ({year})",
        "My Honest {product_name} Review After Real-World Use",
        "{product_name}: Worth the Hype for {audience}? ({year} Review)",
        "Should {audience} Buy {product_name}? An Honest Review ({year})",
        "{product_name} Review: The Good, the Bad, and the Price ({year})",
        "A {audience}'s Honest Review of {product_name} ({year})",
        "{product_name} Long-Term Review for {audience} ({year})",
        "Is {product_name} Right for {audience}? My Honest Take ({year})",
        "{product_name} Review: Real Results for {audience} ({year})",
        "I Tried {product_name} for a Month — Here's the Truth for {audience}",
    ],
    "aibusinessinsider": [
        "Is {product_name} Worth It? Enterprise Review for {audience}",
        "{product_name} Review: Does It Deliver for {audience}? ({year})",
        "Enterprise Test: {product_name} Review for {audience} ({year})",
        "{product_name} Honest Review: A {audience} Analysis ({year})",
        "Is {product_name} the Right {keyword} for {audience}? ({year})",
        "{product_name} Deep Dive: What {audience} Need to Know ({year})",
        "My {product_name} Review After 30 Days of Enterprise Use",
        "{product_name}: Worth the Investment for {audience}? ({year})",
        "Should {audience} Adopt {product_name}? An Honest Review ({year})",
        "{product_name} Review: Performance, Pricing, and ROI ({year})",
        "A {audience}'s Review of {product_name} ({year})",
        "{product_name} Long-Term Enterprise Review ({year})",
        "Is {product_name} Enterprise-Ready? Review for {audience} ({year})",
        "{product_name} Review: Real-World Results for {audience} ({year})",
        "I Evaluated {product_name} for 30 Days — Here's My Verdict for {audience}",
    ],
    "aicofounderstack": [
        "Is {product_name} Worth It? Honest Review for {audience}",
        "I Used {product_name} for 30 Days — Here's My Honest Take",
        "{product_name} Review: Does It Help {audience}? ({year})",
        "{product_name} Honest Review: A {audience}'s Take ({year})",
        "Is {product_name} the Best {keyword} for {audience}? ({year})",
        "{product_name} Deep Dive: What {audience} Should Know ({year})",
        "My Honest {product_name} Review as a Solo Founder",
        "{product_name}: Worth the Money for {audience}? ({year})",
        "Should {audience} Buy {product_name}? An Honest Review ({year})",
        "{product_name} Review: Pros, Cons, and Verdict ({year})",
        "A Bootstrapped Founder's Review of {product_name} ({year})",
        "{product_name} Long-Term Review for {audience} ({year})",
        "Is {product_name} Right for {audience}? My Honest Opinion ({year})",
        "{product_name} Review: Real Results for Bootstrapped {audience} ({year})",
        "I Tried {product_name} Solo — Here's the Truth for {audience}",
    ],
}

# ── Product name pools (for product_review) ──
PRODUCT_POOLS: dict[str, list[str]] = {
    "tech_gadgets": [
        "Echo Dot (5th Gen)", "Apple Watch Series 10", "Anker 737 Power Bank",
        "Logitech MX Master 3S", "Samsung Galaxy Watch 7", "JBL Flip 6",
        "Ring Video Doorbell 4", "Sony WH-1000XM5", "Garmin Venu 3",
        "Anker Soundcore Liberty 4 NC",
    ],
    "home_office": [
        "FlexiSpot E7 Standing Desk", "Herman Miller Aeron", "BenQ ScreenBar Halo",
        "Logitech Brio 500 Webcam", "Elgato Wave:3 Microphone", "Fully Jarvis Desk",
        "Steelcase Leap V2", "LG 27UP850N Monitor", "Rode NT-USB Mini",
        "Fellowes Lotus DX Footrest",
    ],
    "ai_software": [
        "Jasper AI", "Copy.ai Pro Plan", "Grammarly Business",
        "Notion AI", "ChatGPT Plus", "Midjourney Subscription",
        "Descript Pro", "Otter.ai Business", "Surfer SEO",
        "Zapier Professional",
    ],
    "security": [
        "NordVPN", "1Password Families", "YubiKey 5 NFC",
        "Bitdefender Total Security", "Synology DS923+", "ExpressVPN",
        "LastPass Premium", "CrowdStrike Falcon", "Fortinet FortiGate 40F",
        "Dell Trusted Platform Module",
    ],
    "networking": [
        "Ubiquiti Dream Machine Pro", "Netgear Orbi 970", "TP-Link Omada",
        "Synology RT6600ax", "Cisco Meraki Go", "Aruba Instant On",
        "ASUS ZenWiFi Pro XT12", "Eero Pro 6E", "MikroTik hEX S",
        "QNAP QHora-301W",
    ],
    "books_courses": [
        "Zero to One by Peter Thiel", "The Lean Startup by Eric Ries",
        "Atomic Habits by James Clear", "Deep Work by Cal Newport",
        "The $100 Startup by Chris Guillebeau", "Superintelligence by Nick Bostrom",
        "Python for Data Science Handbook", "Harvard CS50 Online",
        "Start with Why by Simon Sinek", "Measure What Matters by John Doerr",
    ],
}

# ── Comparison product pairs/triples (for comparison articles) ──
COMPARISON_POOLS: dict[str, list[tuple[str, ...]]] = {
    "tech_gadgets": [
        ("Echo Dot", "Google Nest Mini"),
        ("Apple Watch", "Samsung Galaxy Watch"),
        ("Sony WH-1000XM5", "Bose QuietComfort Ultra"),
        ("Logitech MX Master 3S", "Razer Pro Click", "Microsoft Sculpt"),
        ("JBL Flip 6", "Sonos Roam", "Bose SoundLink Flex"),
    ],
    "home_office": [
        ("FlexiSpot E7", "Fully Jarvis"),
        ("Herman Miller Aeron", "Steelcase Leap V2", "Haworth Zody"),
        ("BenQ ScreenBar", "Quntis Monitor Light"),
        ("Logitech Brio 500", "Razer Kiyo Pro", "Elgato Facecam"),
        ("Rode NT-USB", "Blue Yeti", "Audio-Technica AT2020"),
    ],
    "ai_software": [
        ("Jasper AI", "Copy.ai"),
        ("ChatGPT Plus", "Claude Pro", "Perplexity Pro"),
        ("Notion AI", "Mem.ai", "Obsidian"),
        ("Midjourney", "DALL·E 3", "Stable Diffusion XL"),
        ("Surfer SEO", "Clearscope", "Frase"),
    ],
    "security": [
        ("NordVPN", "ExpressVPN"),
        ("1Password", "Bitwarden", "LastPass"),
        ("Bitdefender", "Kaspersky", "Norton"),
        ("YubiKey 5", "Google Titan", "Thetis FIDO2"),
        ("CrowdStrike", "SentinelOne", "Microsoft Defender"),
    ],
    "networking": [
        ("Ubiquiti UDM Pro", "Netgear Orbi"),
        ("Eero Pro 6E", "ASUS ZenWiFi", "Synology RT6600ax"),
        ("Aruba Instant On", "Cisco Meraki Go"),
        ("TP-Link Omada", "Ubiquiti UniFi"),
        ("MikroTik", "Cisco Catalyst"),
    ],
    "books_courses": [
        ("Zero to One", "The Lean Startup"),
        ("Atomic Habits", "Deep Work", "The Power of Habit"),
        ("Superintelligence", "Life 3.0"),
        ("Start with Why", "Find Your Why"),
        ("Harvard CS50", "MIT 6.0001", "Stanford CS106A"),
    ],
}

# ---------------------------------------------------------------------------
# 4. DATA MODELS
# ---------------------------------------------------------------------------

@dataclass
class AffiliateProduct:
    product_name: str
    amazon_search_term: str
    price_range: str
    why_recommended: str
    best_for: str = ""
    rating_estimate: str = "4.5/5"


@dataclass
class ArticleStructure:
    sections: list[dict[str, Any]]

    @classmethod
    def comparison(cls, products: list[str]) -> "ArticleStructure":
        return cls(sections=[
            {"heading": "Introduction", "content": f"Why comparing {len(products)} matters for the target audience."},
            {"heading": "Quick Comparison Table", "content": "Side-by-side table: product, price, key feature, best for, rating."},
            {"heading": f"{products[0]}: Full Review", "content": "Deep dive into first product with pros/cons and use cases."},
            {"heading": f"{products[1]}: Full Review", "content": "Deep dive into second product with pros/cons and use cases."},
            *([{"heading": f"{products[2]}: Full Review", "content": "Deep dive into third product with pros/cons and use cases."}] if len(products) > 2 else []),
            {"heading": "Head-to-Head: Key Differences", "content": "Direct comparison on performance, price, features, support."},
            {"heading": "Which One Should You Buy?", "content": "Clear recommendation with scenario-based guidance."},
            {"heading": "Final Verdict", "content": "Summary winner and runner-up with Amazon affiliate links."},
            {"heading": "FAQ", "content": "3-5 common questions answered."},
        ])

    @classmethod
    def buying_guide(cls) -> "ArticleStructure":
        return cls(sections=[
            {"heading": "Introduction", "content": "Why this buying guide matters and who it's for."},
            {"heading": "What to Look For", "content": "5-7 critical factors: price, features, compatibility, support, durability, ease of use, scalability."},
            {"heading": "Budget Tiers Explained", "content": "Entry-level, mid-range, premium tiers with expected features at each price point."},
            {"heading": "Top Picks by Budget", "content": "Recommended products in each tier with brief rationale and Amazon links."},
            {"heading": "Common Mistakes to Avoid", "content": "Pitfalls buyers often fall into."},
            {"heading": "FAQ", "content": "5-7 frequently asked questions."},
            {"heading": "Final Recommendations", "content": "Summary of best overall, best value, best premium with affiliate links."},
        ])

    @classmethod
    def product_review(cls, product_name: str) -> "ArticleStructure":
        return cls(sections=[
            {"heading": "Introduction", "content": f"First impressions and why {product_name} caught our attention."},
            {"heading": f"What Is {product_name}?", "content": "Product overview, who makes it, and what it promises."},
            {"heading": "Key Features", "content": "Bullet breakdown of standout features and specifications."},
            {"heading": "Pros", "content": "3-5 genuine strengths based on real-world testing."},
            {"heading": "Cons", "content": "2-4 honest weaknesses or limitations."},
            {"heading": "Who It's For", "content": "Ideal user profile and use cases."},
            {"heading": "Who Should Skip It", "content": "Scenarios where this product isn't the right fit."},
            {"heading": "Price Analysis", "content": "Current price, value vs competitors, whether it's worth the money."},
            {"heading": "Real-World Performance", "content": "Hands-on experience and testing notes."},
            {"heading": "Verdict", "content": "Clear buy/skip/wait recommendation with Amazon affiliate link."},
            {"heading": "FAQ", "content": "3-5 common questions."},
        ])


@dataclass
class SEOMeta:
    meta_title: str
    meta_description: str
    focus_keyword: str


@dataclass
class GeneratedTopic:
    article_type: str  # "comparison" | "buying_guide" | "product_review"
    title: str
    site: str
    category: str
    keywords: list[str]
    target_audience: str
    article_structure: dict[str, Any]
    seo_meta: dict[str, str]
    affiliate_products: list[dict[str, str]]
    # Extra fields for queue compatibility
    id: str = ""
    slug: str = ""
    category_name: str = ""
    site_focus: str = ""
    commission_range: str = ""
    status: str = "queued"
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    target_word_count: int = 1500
    notes: str = ""

    def to_queue_entry(self) -> dict[str, Any]:
        """Convert to the flat dict format expected by amazon_queue.json."""
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "site": self.site,
            "category": self.category,
            "category_name": self.category_name,
            "site_focus": self.site_focus,
            "keyword": self.keywords[0] if self.keywords else "",
            "commission_range": self.commission_range,
            "status": self.status,
            "created": self.created,
            "article_type": self.article_type,   # NEW field for upgrade types
            "target_word_count": self.target_word_count,
            "target_audience": self.target_audience,
            "notes": self.notes,
            # Preserve structured data for downstream consumers
            "article_structure": self.article_structure,
            "seo_meta": self.seo_meta,
            "affiliate_products": self.affiliate_products,
        }


# ---------------------------------------------------------------------------
# 5. HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def _slugify(text: str, max_len: int = 80) -> str:
    """Create a URL-safe slug from a title."""
    slug = text.lower()
    for ch in ["—", "–", ":", ",", ".", "(", ")", "?", "!", "'", '"']:
        slug = slug.replace(ch, "")
    slug = slug.replace(" ", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    slug = slug.strip("-")
    return slug[:max_len].rstrip("-")


def _topic_id(title: str, site: str) -> str:
    raw = f"{site}:{title}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


def _load_queue() -> dict[str, Any]:
    if QUEUE_FILE.exists():
        try:
            data = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "topics" in data:
                return data
        except (json.JSONDecodeError, ValueError) as e:
            print(f"WARN: Corrupted queue file, using defaults: {e}", file=sys.stderr)
    return {"version": 2, "created": datetime.now().isoformat(), "topics": [], "published": [], "failed": []}


def _save_queue(queue: dict[str, Any]) -> None:
    QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")


def _used_titles(queue: dict[str, Any]) -> set[str]:
    """Collect all titles already in queue/state to avoid duplicates."""
    used: set[str] = set()
    for lst in (queue.get("topics", []), queue.get("published", []), queue.get("failed", [])):
        for entry in lst:
            t = entry.get("title", "").lower()
            if t:
                used.add(t)
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            for info in state.get("published", {}).values():
                t = info.get("title", "").lower()
                if t:
                    used.add(t)
            for t in state.get("queue", []):
                title = t.get("title", "").lower() if isinstance(t, dict) else ""
                if title:
                    used.add(title)
        except Exception:
            pass
    return used


# ---------------------------------------------------------------------------
# 6. GENERATORS — one per article type
# ---------------------------------------------------------------------------

def _pick_year() -> int:
    return random.choice([2026, 2027])


def _pick_price() -> int:
    return random.choice([50, 100, 150, 200, 500])


def _pick_site_for_category(cat_key: str, site_filter: str | None = None) -> str:
    """Pick a site that supports the given category. If site_filter is provided,
    validate that it exists in the category's site_focus; otherwise pick randomly."""
    available = list(CATEGORIES[cat_key]["site_focus"].keys())
    if site_filter and site_filter in available:
        return site_filter
    return random.choice(available)


def _generate_comparison(
    cat_key: str | None = None,
    site_filter: str | None = None,
) -> GeneratedTopic:
    """Generate a comparison article topic."""
    cat_key = cat_key or random.choice(list(CATEGORIES.keys()))
    site = _pick_site_for_category(cat_key, site_filter)

    keyword = random.choice(CATEGORY_KEYWORDS.get(cat_key, ["tools"]))
    audience = random.choice(AUDIENCES.get(site, ["Business Owners"]))
    template = random.choice(COMPARISON_TEMPLATES.get(site, COMPARISON_TEMPLATES["aitoolalliance"]))

    # Pick product(s) to compare
    pool = COMPARISON_POOLS.get(cat_key, [("Option A", "Option B")])
    products = random.choice(pool)
    if len(products) == 2 and "{C}" in template:
        # If template expects 3 products but pool only has 2, force a 2-product template
        template = random.choice([t for t in COMPARISON_TEMPLATES[site] if "{C}" not in t])

    year = _pick_year()
    price = _pick_price()

    ctx = {"A": products[0], "B": products[1], "keyword": keyword, "audience": audience, "year": year}
    if len(products) == 3 and "{C}" in template:
        ctx["C"] = products[2]
    title = template.format(**ctx)

    # Affiliate products for queue
    affiliate_products = []
    for p in products:
        affiliate_products.append({
            "product_name": p,
            "amazon_search_term": f"{p} {keyword}",
            "price_range": f"${price - 20}-{price + 30}" if price > 50 else f"Under ${price + 20}",
            "why_recommended": f"Compared against rivals for {audience.lower()}; strong in core {keyword} metrics.",
            "best_for": audience,
            "rating_estimate": random.choice(["4.2/5", "4.5/5", "4.7/5", "4.8/5"]),
        })

    topic = GeneratedTopic(
        article_type="comparison",
        title=title,
        site=site,
        category=cat_key,
        keywords=[keyword],
        target_audience=audience,
        article_structure=asdict(ArticleStructure.comparison(list(products))),
        seo_meta=asdict(SEOMeta(
            meta_title=title[:60],
            meta_description=f"Compare {', '.join(products)} for {audience.lower()}. See which {keyword} wins in {year} with honest testing and Amazon links.",
            focus_keyword=f"{products[0]} vs {products[1]}",
        )),
        affiliate_products=affiliate_products,
        id=_topic_id(title, site),
        slug=_slugify(title),
        category_name=CATEGORIES[cat_key]["name"],
        site_focus=CATEGORIES[cat_key]["site_focus"][site],
        commission_range=CATEGORIES[cat_key]["commission"],
        notes=f"Comparison of {len(products)} products. Focus: {CATEGORIES[cat_key]['site_focus'][site]}. Target {CATEGORIES[cat_key]['commission']} commission.",
    )
    return topic


def _generate_buying_guide(
    cat_key: str | None = None,
    site_filter: str | None = None,
) -> GeneratedTopic:
    """Generate a buying guide article topic."""
    cat_key = cat_key or random.choice(list(CATEGORIES.keys()))
    site = _pick_site_for_category(cat_key, site_filter)

    keyword = random.choice(CATEGORY_KEYWORDS.get(cat_key, ["tools"]))
    audience = random.choice(AUDIENCES.get(site, ["Business Owners"]))
    template = random.choice(BUYING_GUIDE_TEMPLATES.get(site, BUYING_GUIDE_TEMPLATES["aitoolalliance"]))

    year = _pick_year()
    title = template.format(keyword=keyword, audience=audience, year=year)

    # Pick 3 representative products across budget tiers
    price = _pick_price()
    affiliate_products = []
    for tier, label in [("budget", "Best Budget Pick"), ("mid", "Best Overall"), ("premium", "Best Premium")]:
        tier_price = price if tier == "mid" else (price // 2 if tier == "budget" else price * 2)
        affiliate_products.append({
            "product_name": f"{label} {keyword.title()} for {audience}",
            "amazon_search_term": f"best {keyword} {tier} {year}",
            "price_range": f"${tier_price - 15}-{tier_price + 25}" if tier_price > 30 else f"Under ${tier_price + 20}",
            "why_recommended": f"Top {tier}-tier pick for {audience.lower()} based on features, reviews, and value.",
            "best_for": f"{audience} ({label})",
            "rating_estimate": random.choice(["4.3/5", "4.5/5", "4.7/5"]),
        })

    topic = GeneratedTopic(
        article_type="buying_guide",
        title=title,
        site=site,
        category=cat_key,
        keywords=[keyword, f"{keyword} buying guide", f"best {keyword}"],
        target_audience=audience,
        article_structure=asdict(ArticleStructure.buying_guide()),
        seo_meta=asdict(SEOMeta(
            meta_title=title[:60],
            meta_description=f"Everything {audience.lower()} need to know before buying {keyword} in {year}. Budget tiers, what to look for, and top picks with Amazon links.",
            focus_keyword=f"{keyword} buying guide",
        )),
        affiliate_products=affiliate_products,
        id=_topic_id(title, site),
        slug=_slugify(title),
        category_name=CATEGORIES[cat_key]["name"],
        site_focus=CATEGORIES[cat_key]["site_focus"][site],
        commission_range=CATEGORIES[cat_key]["commission"],
        notes=f"Educational buying guide. Focus: {CATEGORIES[cat_key]['site_focus'][site]}. Target {CATEGORIES[cat_key]['commission']} commission.",
    )
    return topic


def _generate_product_review(
    cat_key: str | None = None,
    site_filter: str | None = None,
) -> GeneratedTopic:
    """Generate a single-product review article topic."""
    cat_key = cat_key or random.choice(list(CATEGORIES.keys()))
    site = _pick_site_for_category(cat_key, site_filter)

    keyword = random.choice(CATEGORY_KEYWORDS.get(cat_key, ["tools"]))
    audience = random.choice(AUDIENCES.get(site, ["Business Owners"]))
    product_name = random.choice(PRODUCT_POOLS.get(cat_key, ["Popular Product"]))
    template = random.choice(PRODUCT_REVIEW_TEMPLATES.get(site, PRODUCT_REVIEW_TEMPLATES["aitoolalliance"]))

    year = _pick_year()
    title = template.format(product_name=product_name, keyword=keyword, audience=audience, year=year)

    price = _pick_price()
    affiliate_products = [{
        "product_name": product_name,
        "amazon_search_term": f"{product_name} {keyword}",
        "price_range": f"${price - 20}-{price + 30}" if price > 50 else f"Under ${price + 20}",
        "why_recommended": f"Deep-dive review for {audience.lower()}: tested, compared, and evaluated on price, features, and real-world performance.",
        "best_for": audience,
        "rating_estimate": random.choice(["4.2/5", "4.5/5", "4.7/5", "4.8/5"]),
    }]

    topic = GeneratedTopic(
        article_type="product_review",
        title=title,
        site=site,
        category=cat_key,
        keywords=[product_name, keyword, f"{product_name} review"],
        target_audience=audience,
        article_structure=asdict(ArticleStructure.product_review(product_name)),
        seo_meta=asdict(SEOMeta(
            meta_title=title[:60],
            meta_description=f"Honest {product_name} review for {audience.lower()}. Pros, cons, price analysis, and verdict after real-world testing. Amazon affiliate link included.",
            focus_keyword=f"{product_name} review",
        )),
        affiliate_products=affiliate_products,
        id=_topic_id(title, site),
        slug=_slugify(title),
        category_name=CATEGORIES[cat_key]["name"],
        site_focus=CATEGORIES[cat_key]["site_focus"][site],
        commission_range=CATEGORIES[cat_key]["commission"],
        notes=f"Single-product deep dive. Focus: {CATEGORIES[cat_key]['site_focus'][site]}. Target {CATEGORIES[cat_key]['commission']} commission.",
    )
    return topic


# ---------------------------------------------------------------------------
# 7. PUBLIC API
# ---------------------------------------------------------------------------

def generate(
    article_type: str = "comparison",
    category: str | None = None,
    site: str | None = None,
) -> dict[str, Any]:
    """Generate a single topic of the requested type.

    Parameters
    ----------
    article_type : str
        One of "comparison", "buying_guide", "product_review".
    category : str, optional
        Category key from CATEGORIES. Random if omitted.
    site : str, optional
        Site key (aitoolalliance, aibusinessinsider, aicofounderstack).

    Returns
    -------
    dict
        JSON-compatible topic dict ready for amazon_queue.json.
    """
    generators = {
        "comparison": _generate_comparison,
        "buying_guide": _generate_buying_guide,
        "product_review": _generate_product_review,
    }
    if article_type not in generators:
        raise ValueError(f"Unknown article_type: {article_type}. Choose from {list(generators.keys())}")
    topic = generators[article_type](cat_key=category, site_filter=site)
    return topic.to_queue_entry()


def generate_batch(
    count: int = 5,
    site: str | None = None,
    category: str | None = None,
    type_weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Generate a mixed batch of upgraded affiliate topics.

    Parameters
    ----------
    count : int
        Total topics to generate.
    site : str, optional
        Restrict to a single site.
    category : str, optional
        Restrict to a single category.
    type_weights : dict, optional
        Relative weights for article types. Defaults to roughly even.

    Returns
    -------
    list[dict]
        List of JSON-compatible topic dicts.
    """
    weights = type_weights or {"comparison": 1.0, "buying_guide": 1.0, "product_review": 1.0}
    types = list(weights.keys())
    type_probs = [weights[t] for t in types]
    total = sum(type_probs)
    type_probs = [p / total for p in type_probs]

    topics: list[dict[str, Any]] = []
    for _ in range(count):
        chosen = random.choices(types, weights=type_probs, k=1)[0]
        topics.append(generate(article_type=chosen, category=category, site=site))
    return topics


def append_to_queue(topics: list[dict[str, Any]], dry_run: bool = False) -> tuple[int, int]:
    """Append generated topics to amazon_queue.json, deduplicating by title.

    Returns
    -------
    tuple[int, int]
        (added_count, skipped_count)
    """
    queue = _load_queue()
    used = _used_titles(queue)
    added = 0
    skipped = 0
    for t in topics:
        title = t.get("title", "").lower()
        if title in used:
            skipped += 1
            continue
        queue["topics"].append(t)
        used.add(title)
        added += 1

    if not dry_run and added:
        _save_queue(queue)
    return added, skipped


# ---------------------------------------------------------------------------
# 8. CLI
# ---------------------------------------------------------------------------

def _show_queue_status() -> None:
    queue = _load_queue()
    queued = [t for t in queue.get("topics", []) if t.get("status") == "queued"]
    published = queue.get("published", [])
    failed = queue.get("failed", [])

    # Count by article_type
    type_counts: dict[str, int] = {}
    site_counts: dict[str, int] = {}
    for t in queued:
        at = t.get("article_type", "post")
        type_counts[at] = type_counts.get(at, 0) + 1
        site_counts[t.get("site", "unknown")] = site_counts.get(t.get("site", "unknown"), 0) + 1

    print("=== Amazon Affiliate Queue Status ===")
    print(f"  Queued:   {len(queued)}")
    print(f"  Published: {len(published)}")
    print(f"  Failed:   {len(failed)}")
    print()
    print("By article type:")
    for t, c in sorted(type_counts.items()):
        print(f"  {t:20s} {c}")
    print()
    print("By site:")
    for s, c in sorted(site_counts.items()):
        print(f"  {s:20s} {c}")
    print()
    if queued:
        print("Next in queue:")
        for i, t in enumerate(queued[:5], 1):
            print(f"  {i}. [{t['site']}] ({t.get('article_type', 'post')}) {t['title']}")
            print(f"     Category: {t.get('category_name', '?')} | {t.get('commission_range', '?')}")


def _show_preview(topics: list[dict[str, Any]]) -> None:
    print(f"=== Preview ({len(topics)} topics) ===\n")
    for t in topics:
        print(f"  [{t['site']}] ({t['article_type']}) {t['title']}")
        print(f"    Category: {t['category_name']} | Commission: {t['commission_range']}")
        print(f"    Audience: {t.get('target_audience', '?')}")
        print(f"    Focus: {t['site_focus']}")
        print(f"    Slug: {t['slug']}")
        print(f"    Products: {len(t.get('affiliate_products', []))}")
        for p in t.get("affiliate_products", []):
            print(f"      - {p['product_name']} ({p['price_range']}) — {p['why_recommended'][:60]}...")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate upgraded affiliate article topics (comparison, buying guide, product review).",
    )
    parser.add_argument("--count", type=int, default=5, help="Number of topics to generate (default: 5)")
    parser.add_argument("--type", type=str, choices=["comparison", "buying_guide", "product_review"],
                        help="Generate only one article type")
    parser.add_argument("--site", type=str, choices=["aitoolalliance", "aibusinessinsider", "aicofounderstack"],
                        help="Restrict to a specific site")
    parser.add_argument("--category", type=str, choices=list(CATEGORIES.keys()),
                        help="Restrict to a specific category")
    parser.add_argument("--append", action="store_true",
                        help="Append generated topics to amazon_queue.json")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without writing to queue")
    parser.add_argument("--status", action="store_true",
                        help="Show current queue status and exit")
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON to stdout")

    args = parser.parse_args()

    if args.status:
        _show_queue_status()
        return

    if args.type:
        topics = [generate(article_type=args.type, category=args.category, site=args.site) for _ in range(args.count)]
    else:
        topics = generate_batch(count=args.count, site=args.site, category=args.category)

    if args.json:
        print(json.dumps(topics, indent=2, ensure_ascii=False))
        return

    _show_preview(topics)

    if args.append:
        added, skipped = append_to_queue(topics, dry_run=args.dry_run)
        action = "Would append" if args.dry_run else "Appended"
        print(f"{action} {added} topics, skipped {skipped} duplicates.")
        if not args.dry_run:
            queue = _load_queue()
            print(f"Queue now has {len(queue['topics'])} total topics.")


if __name__ == "__main__":
    main()
