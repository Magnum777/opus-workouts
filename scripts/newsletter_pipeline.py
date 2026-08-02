#!/usr/bin/env python3
"""
AI Tools Newsletter Pipeline for Beehiiv

Generates and publishes a weekly "AI Tools That Actually Work" newsletter
via Beehiiv's API. Pulls from our content sites and adds affiliate context.

Usage:
    python newsletter_pipeline.py generate          # Generate newsletter content
    python newsletter_pipeline.py generate --dry-run # Preview without publishing
    python newsletter_pipeline.py schedule          # Schedule for next send date
    python newsletter_pipeline.py stats             # Show subscriber/campaign stats
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
QUEUE_FILE = WORKSPACE / "scripts" / "amazon_queue.json"
NEWSLETTER_DIR = WORKSPACE / "scripts" / "newsletter"
NEWSLETTER_ARCHIVE = NEWSLETTER_DIR / "archive"

# Newsletter config
NEWSLETTER_NAME = "AI Tools That Actually Work"
NEWSLETTER_TAGLINE = "The no-BS weekly guide to AI tools worth your time and money"
SENDER_NAME = "Nova from AI Tool Alliance"
SENDER_EMAIL = "hello@aitoolalliance.com"

# Content sections for the newsletter template
SECTIONS = {
    "headline": {
        "name": "This Week's Headliner",
        "description": "One big story or tool launch worth knowing about",
        "word_count": "150-200",
    },
    "tool_spotlight": {
        "name": "Tool Spotlight",
        "description": "Deep dive into one tool we tested this week",
        "word_count": "200-300",
    },
    "quick_hits": {
        "name": "Quick Hits",
        "description": "3-5 tools, updates, or tips in brief",
        "word_count": "50-75 each",
    },
    "deal_alert": {
        "name": "Deal Alert",
        "description": "Current discounts, lifetime deals, or free tiers worth grabbing",
        "word_count": "75-100",
    },
    "learn_something": {
        "name": "Learn Something",
        "description": "One actionable tip or technique for getting more from AI tools",
        "word_count": "100-150",
    },
}

# Affiliate link templates per site
AFFILIATE_LINKS = {
    "aitoolalliance": {
        "tag": "aitoolalliance-20",
        "base": "https://aitoolalliance.com",
    },
    "aicofounderstack": {
        "tag": "aicofounderstack-20",
        "base": "https://aicofounderstack.com",
    },
    "aibusinessinsider": {
        "tag": "aibusinessinsider-20",
        "base": "https://aibusinessinsider.org",
    },
}


def generate_newsletter_content(dry_run=False, week_offset=0):
    """Generate newsletter content for the current or upcoming week."""
    
    # Determine send date
    today = datetime.now()
    # Send on Wednesdays
    days_until_wed = (2 - today.weekday()) % 7
    if days_until_wed == 0:
        days_until_wed = 7  # If today is Wednesday, schedule for next week
    send_date = today + timedelta(days=days_until_wed + (week_offset * 7))
    
    issue_number = (send_date - datetime(2026, 1, 7)).days // 7 + 1
    
    content = {
        "issue": issue_number,
        "send_date": send_date.strftime("%Y-%m-%d"),
        "subject_line": f"Issue #{issue_number}: ",  # Filled by agent
        "preview_text": "",  # Filled by agent
        "sections": {},
        "affiliate_links": [],
        "cta_links": [],
    }
    
    # Build each section with instructions for the agent
    for section_key, section in SECTIONS.items():
        content["sections"][section_key] = {
            "name": section["name"],
            "description": section["description"],
            "target_word_count": section["word_count"],
            "content": "",  # Agent fills this in
        }
    
    # Pull recent posts from queue for CTA links
    recent_posts = []
    if QUEUE_FILE.exists():
        try:
            queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
            for topic in queue.get("topics", [])[:5]:
                recent_posts.append({
                    "title": topic.get("title", ""),
                    "site": topic.get("site", ""),
                    "slug": topic.get("slug", ""),
                })
        except (json.JSONDecodeError, ValueError):
            pass
    
    content["recent_posts"] = recent_posts
    content["affiliate_tags"] = AFFILIATE_LINKS
    
    # Generate the prompt for the agent
    prompt = f"""Write newsletter Issue #{issue_number} for "{NEWSLETTER_NAME}".

Send date: {send_date.strftime("%A, %B %d, %Y")}

Sections to write:

1. **This Week's Headliner** ({SECTIONS['headline']['word_count']} words)
   One big story about AI tools this week. Could be a major launch, a significant update, or a trend worth paying attention to. Use web_search to find current news.

2. **Tool Spotlight** ({SECTIONS['tool_spotlight']['word_count']} words)
   Deep dive into one AI tool. Include what it does, who it's for, pricing, and honest assessment. Link to our review if we have one.

3. **Quick Hits** (3-5 items, {SECTIONS['quick_hits']['word_count']} each)
   Brief mentions of tools, updates, or tips. Each gets 2-3 sentences and a link.

4. **Deal Alert** ({SECTIONS['deal_alert']['word_count']} words)
   Current deals, discounts, or lifetime offers on AI tools. Use web_search to find real current deals.

5. **Learn Something** ({SECTIONS['learn_something']['word_count']} words)
   One actionable tip or technique. Practical, not theoretical.

AFFILIATE LINKS:
When mentioning products with Amazon links, use tag: aitoolalliance-20
When linking to our sites:
- AI Tool Alliance: https://aitoolalliance.com
- AI CoFounder Stack: https://aicofounderstack.com
- AI Business Insider: https://aibusinessinsider.org

Recent posts from our sites (use for CTA links):
{json.dumps(recent_posts, indent=2)}

TONE: Direct, conversational, no fluff. Like a friend who actually tested this stuff. No em dashes. Short paragraphs. Write like you're emailing a colleague, not writing a press release.

FORMAT: Output valid JSON with keys: subject_line, preview_text, headline, tool_spotlight, quick_hits (array of objects with title and text), deal_alert, learn_something

IMPORTANT: Search the web for CURRENT AI tool news and deals before writing. This needs to be timely and relevant."""

    if dry_run:
        content["agent_prompt"] = prompt
        NEWSLETTER_DIR.mkdir(parents=True, exist_ok=True)
        output_file = NEWSLETTER_DIR / f"issue-{issue_number}-draft.json"
        output_file.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Draft prompt saved to: {output_file}")
        print(f"Issue #{issue_number} — send date: {send_date.strftime('%A, %B %d, %Y')}")
        print(f"\nPrompt for agent:\n{'-'*40}\n{prompt[:500]}...\n{'-'*40}\n(Prompt is {len(prompt)} chars)")
        return content
    
    return content


def cmd_generate(args):
    """Generate newsletter content."""
    content = generate_newsletter_content(
        dry_run=args.dry_run,
        week_offset=args.week or 0,
    )
    
    if not args.dry_run:
        # Save for the cron agent to pick up
        NEWSLETTER_DIR.mkdir(parents=True, exist_ok=True)
        output_file = NEWSLETTER_DIR / f"issue-{content['issue']}-prompt.json"
        output_file.write_text(
            json.dumps(content, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"Newsletter prompt saved to: {output_file}")
        print(f"Run this through a kimi-k2.6 or minimax-m3 agent for content generation.")


def cmd_schedule(args):
    """Schedule the newsletter for the next available send date."""
    content = generate_newsletter_content(dry_run=True, week_offset=0)
    print(f"Newsletter Issue #{content['issue']} scheduled for: {content['send_date']}")
    print(f"Content needs to be generated by the cron agent before send date.")


def cmd_stats(args):
    """Show newsletter stats."""
    NEWSLETTER_DIR.mkdir(parents=True, exist_ok=True)
    
    # Count archived issues
    archive = NEWSLETTER_ARCHIVE
    if archive.exists():
        issues = list(archive.glob("issue-*.json"))
        print(f"Archived issues: {len(issues)}")
        if issues:
            latest = max(issues, key=lambda p: p.stat().st_mtime)
            print(f"Latest issue: {latest.stem}")
    else:
        print("No archived issues yet.")
    
    # Check pending
    pending = list(NEWSLETTER_DIR.glob("issue-*-prompt.json"))
    print(f"Pending prompts: {len(pending)}")
    
    # Queue stats
    if QUEUE_FILE.exists():
        try:
            queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
            print(f"Amazon queue topics available for CTAs: {len(queue.get('topics', []))}")
        except (json.JSONDecodeError, ValueError):
            print("Amazon queue: unable to read")
    
    print(f"\nNewsletter: {NEWSLETTER_NAME}")
    print(f"Tagline: {NEWSLETTER_TAGLINE}")
    print(f"Platform: Beehiiv (setup needed)")
    print(f"\nNext steps:")
    print(f"  1. Create Beehiiv account at beehiiv.com")
    print(f"  2. Set up newsletter with name '{NEWSLETTER_NAME}'")
    print(f"  3. Get API key from Beehiiv settings")
    print(f"  4. Add BEEHIIV_API_KEY to .secrets")
    print(f"  5. Create a cron job to generate + send weekly")


def main():
    parser = argparse.ArgumentParser(description="AI Tools Newsletter Pipeline")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Generate
    gen_parser = subparsers.add_parser("generate", help="Generate newsletter content")
    gen_parser.add_argument("--dry-run", action="store_true", help="Preview without publishing")
    gen_parser.add_argument("--week", type=int, default=0, help="Week offset (0=this week, 1=next week)")
    
    # Schedule
    subparsers.add_parser("schedule", help="Schedule for next send date")
    
    # Stats
    subparsers.add_parser("stats", help="Show newsletter stats")
    
    args = parser.parse_args()
    
    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "schedule":
        cmd_schedule(args)
    elif args.command == "stats":
        cmd_stats(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()