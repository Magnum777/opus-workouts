#!/usr/bin/env python3
"""Publish all 6 articles to WordPress sites."""
import requests, base64, os, re, json

from vault_helper import get_credential

# Site configs
SITES = {
    "aitoolalliance": {
        "url": get_credential('wordpress', 'aitoolalliance_url'),
        "user": get_credential('wordpress', 'aitoolalliance_user'),
        "pass": get_credential('wordpress', 'aitoolalliance_pass')
    },
    "aibusinessinsider": {
        "url": get_credential('wordpress', 'aibusinessinsider_url'),
        "user": get_credential('wordpress', 'aibusinessinsider_user'),
        "pass": get_credential('wordpress', 'aibusinessinsider_pass')
    },
    "aicofounderstack": {
        "url": get_credential('wordpress', 'aicofounderstack_url'),
        "user": get_credential('wordpress', 'aicofounderstack_user'),
        "pass": get_credential('wordpress', 'aicofounderstack_pass')
    }
}

# Article mapping
ARTICLES = [
    {
        "file": "output/wp_aitool_1_claude_vs_gpt.md",
        "site": "aitoolalliance",
        "title": "Claude 4 vs GPT-5: Which AI Assistant Wins for Entrepreneurs in 2026?"
    },
    {
        "file": "output/wp_aitool_2_best_tools.md",
        "site": "aitoolalliance",
        "title": "The 7 Best AI Tools for Solopreneurs (Tested & Ranked)"
    },
    {
        "file": "output/wp_aibusiness_1_agency_scaling.md",
        "site": "aibusinessinsider",
        "title": "How Small Agencies Are Using AI to Scale 10x Without Hiring"
    },
    {
        "file": "output/wp_aibusiness_2_100_stack.md",
        "site": "aibusinessinsider",
        "title": "The $100 AI Stack: Build a Full Business Operation for Under $100/Month"
    },
    {
        "file": "output/wp_aicofounder_1_48hour_product.md",
        "site": "aicofounderstack",
        "title": "How I Built a $49 AI Product in 48 Hours (Step-by-Step)"
    },
    {
        "file": "output/wp_aicofounder_2_agents_vs_saas.md",
        "site": "aicofounderstack",
        "title": "AI Agents vs Traditional SaaS: Why the Future Is Autonomous"
    }
]

def md_to_html(md_text):
    """Simple markdown to HTML conversion."""
    # Strip first # title line (WordPress already has title from API)
    lines = md_text.split('\n')
    if lines and lines[0].startswith('# '):
        md_text = '\n'.join(lines[1:]).strip()
    
    html = md_text
    # Headers (start at h2 now since h1 is stripped)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    # Bold/italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    # Code blocks
    html = re.sub(r'```[\w]*\n(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    # Inline code
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    # Links
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
    # Paragraphs
    paragraphs = html.split('\n\n')
    new_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith('<h') or p.startswith('<pre') or p.startswith('<ul') or p.startswith('<ol') or p.startswith('<li'):
            new_paragraphs.append(p)
        else:
            # Wrap in <p> if not already a block element
            if not p.startswith('<'):
                p = f'<p>{p}</p>'
            new_paragraphs.append(p)
    html = '\n\n'.join(new_paragraphs)
    # Lists (basic)
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

def publish_article(site_key, title, content_html, md_text=""):
    site = SITES[site_key]
    auth = base64.b64encode(f"{site['user']}:{site['pass']}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth}',
        'User-Agent': 'ContentNovaBot/2.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    url = f"{site['url']}/wp-json/wp/v2/posts"
    # Extract meta description from content (first paragraph or explicit meta tag)
    meta_desc = ""
    # Look for meta description in HTML comments
    meta_match = re.search(r'&lt;!--\s*Meta Description:\s*(.+?)\s*--&gt;', md_text)
    if meta_match:
        meta_desc = meta_match.group(1).strip()
    else:
        # Use first substantial paragraph
        paragraphs = re.findall(r'&lt;p&gt;(.{50,300}?)&lt;/p&gt;', content_html)
        if paragraphs:
            meta_desc = paragraphs[0].replace('&lt;', '').replace('&gt;', '')[:160]
    
    # Generate focus keyword from title
    focus_kw = title.lower().replace(':', '').replace(',', '').split()[:3]
    focus_keyword = ' '.join(focus_kw)
    
    data = {
        'title': title,
        'content': content_html,
        'status': 'publish',
        'meta': {
            'rank_math_title': title + ' | ' + site_key.replace('_', ' ').title(),
            'rank_math_description': meta_desc,
            'rank_math_focus_keyword': focus_keyword
        }
    }
    try:
        r = requests.post(url, json=data, headers=headers, timeout=30)
        if r.status_code in [200, 201]:
            result = r.json()
            post_id = result.get('id')
            post_link = result.get('link', 'unknown')
            
            # Auto-share to social media after successful publish
            try:
                share_to_social(site_key, post_id, title, post_link, md_text)
            except Exception as e:
                print(f"  Social share error: {e}")
            
            return True, post_link
        else:
            return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)

def share_to_social(site_key, post_id, title, post_link, md_text=""):
    """Share published post to X, Bluesky, and Pinterest via upload-post."""
    import subprocess, sys
    
    # Build the social sharing script call
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'share_to_social.py')
    if os.path.exists(script_path):
        result = subprocess.run(
            [sys.executable, script_path, site_key, str(post_id)],
            capture_output=True, text=True, timeout=60
        )
        print(f"  Social: {result.stdout.strip()}")
        if result.returncode != 0:
            print(f"  Social ERR: {result.stderr.strip()[:200]}")
    else:
        print(f"  Social: share_to_social.py not found, skipping")

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for article in ARTICLES:
        filepath = os.path.join(workspace, article['file'])
        if not os.path.exists(filepath):
            print(f"SKIP: {filepath} not found")
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        html_content = md_to_html(md_content)
        site_key = article['site']
        title = article['title']
        
        print(f"Publishing: {title} -> {site_key}...")
        success, result = publish_article(site_key, title, html_content, md_content)
        
        if success:
            print(f"  OK Published: {result}")
        else:
            print(f"  FAIL: {result}")
    
    print("\nDone.")
