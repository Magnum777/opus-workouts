import requests, base64, re, sys

from vault_helper import get_credential
sys.stdout.reconfigure(encoding='utf-8')

site = {
    'url': get_credential('wordpress', 'aicofounderstack_url') + '/wp-json/wp/v2',
    'user': get_credential('wordpress', 'aicofounderstack_user'),
    'pass': get_credential('wordpress', 'aicofounderstack_pass')
}
creds = f"{site['user']}:{site['pass']}".encode()
token = base64.b64encode(creds).decode()
headers = {
    'Authorization': f'Basic {token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Nova/1.0'
}

def get_all_posts():
    all_posts = []
    page = 1
    while True:
        r = requests.get(f"{site['url']}/posts", headers=headers,
                         params={'per_page': 100, 'status': 'publish', 'page': page}, timeout=30)
        if r.status_code != 200:
            break
        posts = r.json()
        if not posts:
            break
        all_posts.extend(posts)
        if len(posts) < 100:
            break
        page += 1
    return all_posts

def fix_br_lists(text):
    """Fix <p>...<br />- item<br />- item...</p> to use <ul><li>"""
    
    # DASH_PATTERN matches: literal dash, en-dash, bullet, em-dash, or HTML entities for them
    DASH_PATTERN = r'(?:[-–•—]|\u0026#821[0-3];|\u0026mdash;|\u0026ndash;)\s+'
    
    def process_para(m):
        para = m.group(0)
        
        # Quick check: must have <br />
        if '<br' not in para:
            return para
        
        # Split by <br /> or <br>
        parts = re.split(r'<br\s*/?>\s*', para)
        if len(parts) < 2:
            return para
        
        # Categorize parts
        dash_items = []
        non_dash_parts = []
        
        for part in parts:
            # Strip tags for checking
            clean = re.sub(r'</?[^\u003e]+>', '', part).strip()
            if re.match(DASH_PATTERN, clean):
                dash_items.append(part)
            elif clean:  # skip empty
                non_dash_parts.append(part)
        
        if len(dash_items) < 2:
            return para
        
        # Build output
        result_parts = []
        
        # Add intro text as separate paragraphs
        for intro in non_dash_parts:
            intro = intro.strip()
            if not intro:
                continue
            # Ensure proper <p> wrapping
            if not intro.startswith('<'):
                result_parts.append(f'<p>{intro}</p>')
            elif intro.startswith('<p>'):
                if not intro.endswith('</p>'):
                    intro = intro + '</p>'
                result_parts.append(intro)
            else:
                result_parts.append(intro)
        
        # Build <ul> from dash items
        li_items = []
        for item in dash_items:
            # Remove dash prefix (including HTML entity)
            clean = re.sub(r'^\s*(?:<p>)?\s*' + DASH_PATTERN, '', item)
            clean = clean.strip()
            # Remove wrapping <p> tags if present
            clean = re.sub(r'^<p>\s*', '', clean)
            clean = re.sub(r'\s*</p>\s*$', '', clean)
            if clean:
                li_items.append(clean)
        
        if li_items:
            li_html = ''.join(f'<li>{item}</li>' for item in li_items)
            result_parts.append(f'<ul>{li_html}</ul>')
        
        return ''.join(result_parts)
    
    # Match <p> tags with content
    return re.sub(r'<p>(.+?)</p>', process_para, text, flags=re.DOTALL)

def main():
    posts = get_all_posts()
    print(f"Found {len(posts)} posts")
    
    fixed_count = 0
    
    for p in posts:
        post_id = p['id']
        title = p['title']['rendered']
        content = p.get('content', {}).get('rendered', '')
        
        if not content.strip():
            continue
        
        new_content = fix_br_lists(content)
        
        if new_content != content:
            print(f"\nPOST {post_id}: {title}")
            print(f"  Changed content (preview first 500 chars):")
            print(new_content[:500])
            
            update_url = f"{site['url']}/posts/{post_id}"
            update_data = {'content': new_content}
            r = requests.post(update_url, headers=headers, json=update_data, timeout=30)
            if r.status_code in (200, 201):
                print(f"  [OK] Updated")
                fixed_count += 1
            else:
                print(f"  [FAIL] HTTP {r.status_code}")
    
    print(f"\n{'='*50}")
    print(f"Done: {fixed_count} fixed")

if __name__ == '__main__':
    main()
