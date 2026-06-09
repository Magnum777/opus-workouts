#!/usr/bin/env python3
"""Add AI Cofounder Guide to Primary Nav menu."""
import requests, base64

site = {
    "url": "https://aicofounderstack.com",
    "user": "nova",
    "pass": "DUau yrXK 1X8k O6eH YL5v qKID"
}

auth = base64.b64encode(f"{site['user']}:{site['pass']}".encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'ContentNovaBot/2.0',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Add menu item to Primary Nav (ID: 10)
# Link to the product page
menu_item_url = f"{site['url']}/wp-json/wp/v2/menu-items"
data = {
    "title": "AI Cofounder Guide",
    "url": "https://www.aicofounderstack.com/ai-cofounder-guide/",
    "menus": 10,  # Primary Nav - integer, not array
    "status": "publish",
    "type": "custom",
    "target": ""
}

r = requests.post(menu_item_url, json=data, headers=headers, timeout=15)
print(f"Add menu item: HTTP {r.status_code}")
if r.status_code in [200, 201]:
    res = r.json()
    print(f"  Added: {res.get('title',{}).get('rendered','')} -> {res.get('url','')}")
else:
    print(f"  Error: {r.text[:300]}")
