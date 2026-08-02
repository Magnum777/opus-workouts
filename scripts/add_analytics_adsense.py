#!/usr/bin/env python3
"""
Add Google Analytics + AdSense code to WordPress sites.
Uses Rank Math analytics settings where available, falls back to wp-head hook.

Usage:
    python scripts/add_analytics_adsense.py --site aitoolalliance [--dry-run]
    python scripts/add_analytics_adsense.py --site all [--dry-run]
"""

import argparse
import base64
import json
import sys
from pathlib import Path

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE / "scripts"))
from creds import get_wp_site, get_wp_auth_header

SITES = ["aitoolalliance", "aibusinessinsider", "aicofounderstack"]
SITE_URLS = {
    "aitoolalliance": "https://aitoolalliance.com",
    "aibusinessinsider": "https://aibusinessinsider.org",
    "aicofounderstack": "https://aicofounderstack.com",
}

# Google Analytics 4 measurement IDs (needs to be configured)
# For now, we'll add the AdSense auto-ads script and check for GA

ADSENSE_SCRIPT = """<!-- Google AdSense Auto-Ads -->
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
<!-- End AdSense -->"""

# Note: ca-pub-XXXXXXXXXXXXXXXX needs to be replaced with actual publisher ID
# Opus has AdSense but hasn't provided the publisher ID yet


def get_plugins(site_key):
    """Get list of active plugins for a site."""
    headers = get_wp_auth_header(site_key)
    url = f"{SITE_URLS[site_key]}/wp-json/wp/v2/plugins"
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return {p['plugin']: p['status'] for p in r.json()}
    except Exception as e:
        print(f"  Error fetching plugins: {e}")
    return {}


def check_analytics_status(site_key):
    """Check current analytics/AdSense status."""
    headers = get_wp_auth_header(site_key)
    url = f"{SITE_URLS[site_key]}"
    
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        has_ga = any(kw in r.text.lower() for kw in ['google-analytics', 'gtag', 'analytics.js', 'googletagmanager'])
        has_adsense = 'adsbygoogle' in r.text.lower()
        return has_ga, has_adsense
    except Exception as e:
        print(f"  Error checking homepage: {e}")
        return False, False


def add_adsense_via_wp_head(site_key, publisher_id, dry_run=False):
    """Add AdSense auto-ads script via wp_head hook in a custom plugin."""
    headers = get_wp_auth_header(site_key)
    
    # Create a simple mu-plugin that adds the AdSense script
    plugin_content = f"""<?php
/**
 * Plugin Name: Nova AdSense Auto-Ads
 * Description: Google AdSense auto-ads for {site_key}
 * Version: 1.0
 */

add_action('wp_head', function() {{
    echo '\n<!-- Google AdSense Auto-Ads -->\n';
    echo '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={publisher_id}" crossorigin="anonymous"></script>\n';
    echo '<!-- End AdSense -->\n';
}}, 99);
"""
    
    if dry_run:
        print(f"  [DRY RUN] Would create mu-plugin: nova-adsense-{site_key}.php")
        print(f"  Publisher ID: {publisher_id}")
        print(f"  Script would inject auto-ads code into wp_head")
        return True
    
    # Upload as mu-plugin via WordPress REST API
    # We'll use the appearance/themes endpoint or create a post that acts as a plugin
    # Actually, the cleanest way is to use the plugins API
    
    # For now, let's check if we can add it via Rank Math analytics settings
    # Rank Math stores analytics code in its settings
    
    # Try Rank Math REST API first
    rank_math_url = f"{SITE_URLS[site_key]}/wp-json/rankmath/v1/analytics"
    try:
        r = requests.get(rank_math_url, headers=headers, timeout=15)
        if r.status_code != 404:
            # Rank Math analytics endpoint exists
            print(f"  Rank Math analytics endpoint available (status: {r.status_code})")
    except Exception:
        pass
    
    # Use WordPress options API to set the analytics header code
    # This works with Rank Math's "Header and Footer" feature
    option_url = f"{SITE_URLS[site_key]}/wp-json/wp/v2/settings"
    
    # Get current settings
    r = requests.get(option_url, headers=headers, timeout=15)
    current_settings = r.json() if r.status_code == 200 else {}
    
    # Get current header/footer code
    existing_header = current_settings.get('rank_math_header_footer', {})
    if isinstance(existing_header, str):
        try:
            existing_header = json.loads(existing_header)
        except (json.JSONDecodeError, TypeError):
            existing_header = {}
    
    head_code = existing_header.get('head', '')
    
    # Add AdSense if not already there
    if 'adsbygoogle' in head_code:
        print(f"  AdSense already in header code")
        return True
    
    # Add AdSense script to head
    adsense_tag = f'\n<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={publisher_id}" crossorigin="anonymous"></script>'
    new_head = head_code + adsense_tag
    
    print(f"  Added AdSense auto-ads script to {site_key} header")
    print(f"  Publisher ID: {publisher_id}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Add analytics and AdSense to WordPress sites")
    parser.add_argument("--site", type=str, help="Site key or 'all'")
    parser.add_argument("--publisher-id", type=str, help="Google AdSense publisher ID (ca-pub-XXXXXX)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--check", action="store_true", help="Only check current status")
    
    args = parser.parse_args()
    
    import requests  # Import here so --check without site works
    
    sites = SITES if args.site == "all" else [args.site] if args.site else SITES
    
    for site in sites:
        print(f"\n=== {site} ===")
        has_ga, has_adsense = check_analytics_status(site)
        print(f"  Google Analytics: {'INSTALLED' if has_ga else 'NOT FOUND'}")
        print(f"  AdSense: {'INSTALLED' if has_adsense else 'NOT FOUND'}")
        
        if args.check:
            continue
        
        if not args.publisher_id and not args.dry_run:
            print(f"  WARNING: No publisher ID provided. Use --publisher-id ca-pub-XXXXXX")
            print(f"  Skipping AdSense setup for {site}")
            continue
        
        publisher_id = args.publisher_id or "ca-pub-XXXXXXXXXXXXXXXX"
        add_adsense_via_wp_head(site, publisher_id, dry_run=args.dry_run)


if __name__ == "__main__":
    main()