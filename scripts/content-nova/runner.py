#!/usr/bin/env python3
"""
Content-Nova Orchestrator v2
Single entry point for daily content publishing pipeline.
Usage: python runner.py --site aitoolalliance.com --action publish
"""

import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from generator import pick_next_topic, generate_article
from publisher import create_post, list_posts, get_latest_post_date

def run_pipeline(site_key, dry_run=False):
    """Full pipeline: pick topic -> generate content -> publish draft."""
    print(f"[ContentNova] Starting pipeline for {site_key}")

    # 1. Pick topic
    topic = pick_next_topic(site_key)
    if not topic:
        print(f"[ERROR] No topic configured for {site_key}")
        return False
    print(f"[TOPIC] {topic}")

    # 2. Generate content prompt (AI fills this in via agent)
    article = generate_article(topic, site_key)
    print(f"[GENERATE] Prompt ready: {article['title'] if 'title' in article else topic}")

    # 3. Publish as DRAFT (AI will fill content later, or we pass to agent)
    if dry_run:
        print(f"[DRY-RUN] Would create draft: {topic}")
        return True

    # For now, create a draft with placeholder -- the agent cron will fill it
    res = create_post(site_key, title=f"DRAFT: {topic}", content="<p>Content pending generation.</p>", status='draft')
    if res.get('ok'):
        print(f"[OK] Draft created: {res['link']} (ID: {res['id']})")
        return res
    else:
        print(f"[ERROR] Publish failed: {res}")
        return False


def check_status(site_key):
    """Show latest post date and topic queue position."""
    latest = get_latest_post_date(site_key)
    print(f"[STATUS] {site_key}")
    print(f"  Latest post: {latest or 'NONE'}")
    # Show next topic
    next_topic = pick_next_topic(site_key)
    print(f"  Next topic: {next_topic}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Content-Nova Orchestrator')
    parser.add_argument('site', choices=['aitoolalliance.com','aibusinessinsider.org','aicofounderstack.com'])
    parser.add_argument('action', choices=['publish','status','dry-run'])
    args = parser.parse_args()

    if args.action == 'publish':
        ok = run_pipeline(args.site)
        sys.exit(0 if ok else 1)
    elif args.action == 'dry-run':
        ok = run_pipeline(args.site, dry_run=True)
        sys.exit(0 if ok else 1)
    elif args.action == 'status':
        check_status(args.site)
