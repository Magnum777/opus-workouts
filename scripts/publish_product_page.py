#!/usr/bin/env python3
"""Create product page on aicofounderstack.com."""
import requests, base64, re, os

site = {
    "url": "https://aicofounderstack.com",
    "user": "nova",
    "pass": "DUau yrXK 1X8k O6eH YL5v qKID"
}

def md_to_html(md_text):
    lines = md_text.split('\n')
    if lines and lines[0].startswith('# '):
        md_text = '\n'.join(lines[1:]).strip()
    html = md_text
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
    paragraphs = html.split('\n\n')
    new_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<h') or p.startswith('<ul') or p.startswith('<ol') or p.startswith('<li'):
            new_paragraphs.append(p)
        else:
            if not p.startswith('<'):
                p = f'<p>{p}</p>'
            new_paragraphs.append(p)
    html = '\n\n'.join(new_paragraphs)
    lines = html.split('\n')
    in_list = False
    new_lines = []
    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                new_lines.append('<ul>')
                in_list = True
            content = line.strip()[2:]
            new_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                new_lines.append('</ul>')
                in_list = False
            new_lines.append(line)
    if in_list:
        new_lines.append('</ul>')
    html = '\n'.join(new_lines)
    return html

workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(workspace, "output/product_v1_quickstart.md"), 'r', encoding='utf-8') as f:
    md = f.read()

html = md_to_html(md)

# Add CTA button
html += '\n\n<div style="text-align:center; margin: 2em 0;">\n  <a href="https://layeredmedia.gumroad.com/l/AICofounderQuickStartGuide" style="background:#e94560; color:white; padding:15px 40px; border-radius:5px; text-decoration:none; font-size:18px; font-weight:bold; display:inline-block;">Get the Guide - $25</a>\n</div>'

auth = base64.b64encode(f"{site['user']}:{site['pass']}".encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'ContentNovaBot/2.0',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# Create as a WordPress PAGE (not post)
url = f"{site['url']}/wp-json/wp/v2/pages"
data = {
    'title': 'AI Cofounder Quick Start Guide',
    'content': html,
    'status': 'publish',
    'slug': 'ai-cofounder-guide'
}

r = requests.post(url, json=data, headers=headers, timeout=30)
if r.status_code in [200, 201]:
    res = r.json()
    print(f"Published: {res.get('link', 'unknown')}")
else:
    print(f"FAIL: HTTP {r.status_code}: {r.text[:300]}")
