#!/usr/bin/env python3
"""Create products page on aicofounderstack.com."""
import requests, base64, re, os

from vault_helper import get_credential

site = {
    "url": get_credential("wordpress", "aicofounderstack_url"),
    "user": get_credential("wordpress", "aicofounderstack_user"),
    "pass": get_credential("wordpress", "aicofounderstack_pass")
}

def md_to_html(md_text):
    lines = md_text.split('\n')
    if lines and lines[0].startswith('# '):
        md_text = '\n'.join(lines[1:]).strip()
    html = md_text
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
    paragraphs = html.split('\n\n')
    new_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<h') or p.startswith('<hr'):
            new_paragraphs.append(p)
        else:
            if not p.startswith('<'):
                p = f'<p>{p}</p>'
            new_paragraphs.append(p)
    html = '\n\n'.join(new_paragraphs)
    return html

workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(workspace, "output/products_page.md"), 'r', encoding='utf-8') as f:
    md = f.read()

html = md_to_html(md)

# Style the Gumroad links as buttons
html = html.replace(
    '<a href="https://layeredmedia.gumroad.com/l/AICofounderQuickStartGuide">Get it on Gumroad - $25</a>',
    '<a href="https://layeredmedia.gumroad.com/l/AICofounderQuickStartGuide" style="background:#e94560; color:white; padding:12px 30px; border-radius:5px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:10px;">Get it on Gumroad - $25</a>'
)
html = html.replace(
    '<a href="https://layeredmedia.gumroad.com/l/memecointrader">Get it on Gumroad - $49</a>',
    '<a href="https://layeredmedia.gumroad.com/l/memecointrader" style="background:#e94560; color:white; padding:12px 30px; border-radius:5px; text-decoration:none; font-weight:bold; display:inline-block; margin-top:10px;">Get it on Gumroad - $49</a>'
)

auth = base64.b64encode(f"{site['user']}:{site['pass']}".encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'ContentNovaBot/2.0',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Create as WordPress PAGE
url = f"{site['url']}/wp-json/wp/v2/pages"
data = {
    'title': 'Products',
    'content': html,
    'status': 'publish',
    'slug': 'products'
}

r = requests.post(url, json=data, headers=headers, timeout=30)
if r.status_code in [200, 201]:
    res = r.json()
    page_id = res.get('id')
    page_link = res.get('link')
    print(f"Published: {page_link}")
    
    # Add to Primary Nav menu (ID: 10)
    menu_item_url = f"{site['url']}/wp-json/wp/v2/menu-items"
    menu_data = {
        "title": "Products",
        "url": page_link,
        "menus": 10,
        "status": "publish",
        "type": "custom"
    }
    mr = requests.post(menu_item_url, json=menu_data, headers=headers, timeout=15)
    if mr.status_code in [200, 201]:
        print(f"Added to menu: Products")
    else:
        print(f"Menu add failed: HTTP {mr.status_code}")
else:
    print(f"FAIL: HTTP {r.status_code}: {r.text[:300]}")
