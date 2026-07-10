#!/usr/bin/env python3
"""Publish just the 2 aibusinessinsider articles."""
import requests, base64, os, re

from vault_helper import get_credential

SITES = {
    "aibusinessinsider": {
        "url": get_credential('wordpress', 'aibusinessinsider_url'),
        "user": get_credential('wordpress', 'aibusinessinsider_user'),
        "pass": get_credential('wordpress', 'aibusinessinsider_pass')
    }
}

ARTICLES = [
    {
        "file": "output/wp_aibusiness_1_agency_scaling.md",
        "title": "How Small Agencies Are Using AI to Scale 10x Without Hiring"
    },
    {
        "file": "output/wp_aibusiness_2_100_stack.md",
        "title": "The $100 AI Stack: Build a Full Business Operation for Under $100/Month"
    }
]

def md_to_html(md_text):
    lines = md_text.split('\n')
    if lines and lines[0].startswith('# '):
        md_text = '\n'.join(lines[1:]).strip()
    html = md_text
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    html = re.sub(r'```[\w]*\n(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
    paragraphs = html.split('\n\n')
    new_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<h') or p.startswith('<pre') or p.startswith('<ul') or p.startswith('<ol') or p.startswith('<li'):
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

for article in ARTICLES:
    filepath = os.path.join(workspace, article['file'])
    with open(filepath, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = md_to_html(md_content)
    site = SITES['aibusinessinsider']
    auth = base64.b64encode(f"{site['user']}:{site['pass']}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth}',
        'User-Agent': 'ContentNovaBot/2.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    url = f"{site['url']}/wp-json/wp/v2/posts"
    data = {
        'title': article['title'],
        'content': html_content,
        'status': 'publish'
    }
    print(f"Publishing: {article['title']}...")
    r = requests.post(url, json=data, headers=headers, timeout=30)
    if r.status_code in [200, 201]:
        print(f"  OK: {r.json().get('link', 'unknown')}")
    else:
        print(f"  FAIL: HTTP {r.status_code}: {r.text[:200]}")

print("Done.")
