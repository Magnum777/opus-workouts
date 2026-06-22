"""
ContentNova Publishing Pipeline v3 — Integrated Quality Gate

Usage:
    python publish_with_quality_gate.py draft.md --site aicofounderstack.com
    python publish_with_quality_gate.py draft.md --site aicofounderstack.com --publish

Flow:
1. Read draft
2. Run humanizer (strip AI patterns)
3. Run factual-claim-verifier (check assertions)
4. If gate passes → publish via wordpress-api-pro
5. If gate fails → save humanized version for review
"""

import sys
import os
import argparse
from pathlib import Path
import datetime

# LOGGING SETUP
LOG_FILE = Path(__file__).parent / 'pipeline.log'

def log_event(event_type, site, title_or_msg, extra=None):
    ts = datetime.datetime.now().isoformat()
    line = f"[{ts}] {event_type} | {site} | {title_or_msg}"
    if extra:
        line += f" | {extra}"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

# Add paths
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts\content-nova')

from content_quality_gate import quality_gate
from publisher_v3 import create_post, update_post, SITES


def publish_with_gate(article_path, site_key, auto_publish=False):
    """Full pipeline: quality gate → publish."""
    
    print("="*70)
    print(f"CONTENTNOVA PUBLISHING PIPELINE v3")
    print(f"Site: {site_key}")
    print(f"Auto-publish: {auto_publish}")
    print("="*70)
    
    # Step 1: Read draft
    with open(article_path, 'r', encoding='utf-8') as f:
        draft = f.read()
    
    # Extract title from H1
    lines = draft.split('\n')
    title = None
    if lines[0].startswith('# '):
        title = lines[0].replace('# ', '').strip()
        content = '\n'.join(lines[1:]).strip()
    else:
        content = draft
        title = "Untitled"
    
    # Step 2: Quality Gate
    print(f"\nRunning quality gate on: {title}")
    log_event('INIT', site_key, title)
    result = quality_gate(content, title)
    
    # Step 3: Decide
    if result['can_publish']:
        print(f"\n[PASS] Quality gate cleared")
        log_event('GATE_PASS', site_key, title, f"humanized={result.get('humanization_needed', False)}")
        
        if auto_publish:
            print(f"Publishing to {site_key}...")
            # Use humanized version if available
            publish_content = result['humanized'] if result['humanization_needed'] else content
            
            res = create_post(site_key, title, publish_content, status='publish')
            if 'ok' in res:
                print(f"[OK] Published LIVE: {res.get('link', 'N/A')}")
                print(f"Post ID: {res.get('id')}")
                
                # Auto-set slug from title if WordPress didn't generate one
                if res.get('id'):
                    post_id = res['id']
                    # Wait a moment for WordPress to process
                    import time
                    time.sleep(1)
                    
                    # Check if slug was generated
                    from publisher_v3 import update_post
                    import requests, base64
                    site = SITES.get(site_key)
                    creds = f"{site['user']}:{site['pass']}".encode()
                    token = base64.b64encode(creds).decode()
                    headers = {
                        'Authorization': f'Basic {token}',
                        'Accept': 'application/json'
                    }
                    url = f"{site['url']}/wp-json/wp/v2/posts/{post_id}"
                    r = requests.get(url, headers=headers, timeout=10)
                    if r.status_code == 200:
                        post_data = r.json()
                        slug = post_data.get('slug', '')
                        if not slug or slug == str(post_id):
                            # Generate slug from title
                            import re
                            slug = re.sub(r'[^\w\s-]', '', title.lower())
                            slug = re.sub(r'[-\s]+', '-', slug).strip('-')[:60]
                            update_post(site_key, post_id, slug=slug)
                            print(f"Slug set: {slug}")
                            # Refresh link
                            r2 = requests.get(url, headers=headers, timeout=10)
                            if r2.status_code == 200:
                                res['link'] = r2.json().get('link', res['link'])
                                print(f"Updated URL: {res['link']}")
                
                return {'ok': True, 'id': res.get('id'), 'link': res.get('link')}
            else:
                print(f"[ERROR] Publish failed: {res}")
                return False
        else:
            print(f"\n[DRY RUN] Would publish to {site_key}")
            print(f"  Title: {title}")
            print(f"  Humanization needed: {result['humanization_needed']}")
            if result['humanization_needed']:
                print(f"  Fixes applied: {len(result['humanization_fixes'])}")
            print(f"\nTo actually publish, add --publish flag")
        
        return True
    else:
        print(f"\n[BLOCKED] Quality gate failed:")
        print(f"  Verdict: {result['final_verdict']}")
        
        # Save humanized version for review
        review_path = article_path.replace('.md', '_humanized.md')
        with open(review_path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(result['humanized'])
        print(f"\nHumanized version saved to: {review_path}")
        print("Review fixes and rerun when ready")
        
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ContentNova with Quality Gate')
    parser.add_argument('file', help='Article markdown file')
    parser.add_argument('--site', choices=list(SITES.keys()), required=True)
    parser.add_argument('--publish', action='store_true', help='Actually publish (default: dry run)')
    args = parser.parse_args()
    
    success = publish_with_gate(args.file, args.site, args.publish)
    sys.exit(0 if success else 1)
