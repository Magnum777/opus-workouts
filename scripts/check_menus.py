#!/usr/bin/env python3
"""Add AI Cofounder Guide to aicofounderstack.com navigation menu."""
import requests, base64, json, sys

from vault_helper import get_credential

site = {
    "url": get_credential("wordpress", "aicofounderstack_url"),
    "user": get_credential("wordpress", "aicofounderstack_user"),
    "pass": get_credential("wordpress", "aicofounderstack_pass")
}

auth = base64.b64encode(f"{site['user']}:{site['pass']}".encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'ContentNovaBot/2.0',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# List all menus
menus_url = f"{site['url']}/wp-json/wp/v2/menus"
r = requests.get(menus_url, headers=headers, timeout=15)
print(f"Menus: HTTP {r.status_code}")
if r.status_code == 200:
    menus = r.json()
    for m in menus:
        print(f"  ID:{m['id']} | {m.get('name','unnamed')} | slug:{m.get('slug','')}")
        # Get menu items
        items_url = f"{site['url']}/wp-json/wp/v2/menu-items"
        ir = requests.get(items_url, headers=headers, params={'menus': m['id']}, timeout=15)
        if ir.status_code == 200:
            items = ir.json()
            for item in items:
                print(f"    - {item.get('title','').get('rendered','')} -> {item.get('url','')}")
