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

def fix_content(content):
    """Comprehensive fix for markdown and formatting issues."""
    original = content
    changes = []

    # 1. Remove duplicate H1 if content starts with one
    h1_match = re.search(r'^(?:\s*<p>\s*)?\s*<h1[^>]*>([^<]+)</h1>(?:\s*</p>\s*)?', content, re.IGNORECASE)
    if h1_match:
        content = content[h1_match.end():].lstrip()
        changes.append(f"Removed duplicate H1")

    md_h1 = re.search(r'^(?:\s*<p>\s*)?\s*#\s+([^\n<]+)(?:\s*</p>\s*)?', content)
    if md_h1:
        content = content[md_h1.end():].lstrip()
        changes.append("Removed markdown H1")

    # 2. Remove byline block (Author: / Date: / Tags:)
    byline_pattern = r'<p>\s*(?:<strong>)?Author:(?:</strong>)?\s*[^<]*(?:<br\s*/?>\s*){0,2}(?:<strong>)?Date:(?:</strong>)?[^<]*(?:<br\s*/?>\s*){0,2}(?:<strong>)?Tags:(?:</strong>)?[^<]*</p>'
    byline_match = re.search(byline_pattern, content, re.IGNORECASE | re.DOTALL)
    if byline_match:
        content = content[:byline_match.start()] + content[byline_match.end():]
        content = content.lstrip()
        changes.append("Removed byline block")

    # 3. Fix markdown headers inside paragraphs: <p>## Heading</p> or ### Heading
    def fix_md_heading(m):
        level = len(m.group(1))
        text = m.group(2).strip()
        tag = 'h2' if level >= 2 else 'h3'
        return f'<{tag}>{text}</{tag}>'

    content = re.sub(r'(?:<p>\s*)?(#{1,3})\s+([^\n<]+)(?:\s*</p>)?', fix_md_heading, content)
    if '###' in original and '###' not in content:
        changes.append("Fixed markdown headers")

    # 4. Fix **bold** → <strong>
    bold_fixed = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', content)
    if bold_fixed != content:
        content = bold_fixed
        changes.append("Fixed markdown bold")

    # 5. Fix *italic* → <em> (but not inside HTML attributes)
    italic_fixed = re.sub(r'(?![^\u003c]*>)\*([^*]+)\*', r'<em>\1</em>', content)
    if italic_fixed != content:
        content = italic_fixed
        changes.append("Fixed markdown italic")

    # 6. Convert list paragraphs with <p>- item</p> or <p>‑ item</p> to <ul><li>
    # Handle two patterns:
    # A. Single <p> with <br /> separated items: <p>‑ item1<br />‑ item2</p>
    # B. Multiple consecutive <p>-</p> paragraphs

    def fix_list_paragraphs(text):
        # Pattern A: <p>[optional intro text]<br />‑ item1<br />‑ item2...</p>
        # Find paragraphs that contain <br /> separated items starting with dash/en-dash
        def fix_br_list(m):
            full = m.group(0)
            # Check if it has <br /> separated items with dashes
            if '<br' not in full:
                return full
            # Split by <br /> or <br>
            parts = re.split(r'<br\s*/?>\s*', full)
            if not parts:
                return full
            # Check if parts have dash items
            dash_items = []
            intro = None
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                # Check if starts with dash/en-dash
                if re.match(r'^(?:<p>\s*)?[-–•—\u2011\u2013\u2014]\s+', part):
                    # Extract just the item text
                    clean = re.sub(r'^\s*(?:<p>\s*)?[-–•—\u2011\u2013\u2014]\s+', '', part)
                    clean = re.sub(r'</\w+>\s*$', '', clean)
                    dash_items.append(clean)
                elif part.startswith('<p>') or part.startswith('<strong>'):
                    # This might be the intro text
                    intro = part
            
            if len(dash_items) >= 2:
                li_html = ''.join(f'<li>{item}</li>' for item in dash_items)
                if intro:
                    return f'{intro}<ul>{li_html}</ul>'
                return f'<ul>{li_html}</ul>'
            return full

        # Apply to paragraphs with <br /> and dash items
        text = re.sub(r'<p>([^\u003c]*(?:<br\s*/?>\s*[-–•—\u2011\u2013\u2014]\s+[^\u003c]*)+)</p>', fix_br_list, text, flags=re.DOTALL)

        # Pattern B: Multiple consecutive <p>-</p> paragraphs
        list_para_pattern = r'(?:<p>\s*[-–•—\u2011\u2013\u2014]\s+([^<]+)</p>\s*)+'
        def replace_list_block(m):
            items = re.findall(r'<p>\s*[-–•—\u2011\u2013\u2014]\s+([^<]+)</p>', m.group(0))
            if not items:
                return m.group(0)
            li_tags = ''.join(f'<li>{item.strip()}</li>' for item in items)
            return f'<ul>{li_tags}</ul>'
        text = re.sub(list_para_pattern, replace_list_block, text)

        return text

    content = fix_list_paragraphs(content)
    if '<ul>' in content and '<ul>' not in original:
        changes.append("Converted lists to <ul>")

    # 7. Fix markdown tables: | col | col | → HTML table
    def fix_tables(text):
        # Find table-like blocks: lines starting with |
        table_pattern = r'(<p>)?\s*\|[^\n]+\|\s*(?:<br\s*/?>\s*\|[^\n]+\|)+\s*(</p>)?'
        def convert_table(m):
            full = m.group(0)
            # Remove wrapping <p> tags if present
            inner = re.sub(r'^<p>\s*', '', full)
            inner = re.sub(r'\s*</p>\s*$', '', inner)
            # Split by <br /> or newlines
            rows = re.split(r'<br\s*/?>\s*', inner)
            html_rows = []
            for i, row in enumerate(rows):
                if not row.strip():
                    continue
                cells = [c.strip() for c in row.split('|') if c.strip()]
                if not cells:
                    continue
                # Skip separator rows (all dashes)
                if all(re.match(r'^[-:]+$', c) for c in cells):
                    continue
                tag = 'th' if i == 0 else 'td'
                cell_html = ''.join(f'<{tag}>{c}</{tag}>' for c in cells)
                html_rows.append(f'<tr>{cell_html}</tr>')
            if html_rows:
                return '<table>' + ''.join(html_rows) + '</table>'
            return m.group(0)
        return re.sub(table_pattern, convert_table, text, flags=re.DOTALL)

    content = fix_tables(content)
    if '<table>' in content and '<table>' not in original:
        changes.append("Converted markdown tables")

    # 8. Clean up <br /> inside headings
    content = re.sub(r'(<h[1-6][^\u003e]*>)([^\u003c]*)<br\s*/?\u003e\s*', r'\1\2 ', content)

    # 9. Replace <p>—</p> with <hr /> for better semantics
    content = re.sub(r'<p>\s*[-—–]\s*</p>', '<hr />', content)

    # 10. Remove empty paragraphs
    content = re.sub(r'<p>\s*(?:&nbsp;)?\s*</p>', '', content)

    # 11. Fix multiple consecutive <hr />
    content = re.sub(r'(<hr\s*/?\u003e\s*){2,}', '<hr />', content)

    return content, changes

def main():
    print("Fetching all published posts...")
    posts = get_all_posts()
    print(f"Found {len(posts)} posts\n")

    fixed_count = 0
    skipped_count = 0

    for p in posts:
        post_id = p['id']
        title = p['title']['rendered']
        content = p.get('content', {}).get('rendered', '')

        if not content.strip():
            continue

        new_content, changes = fix_content(content)

        if changes:
            print(f"\nPOST {post_id}: {title}")
            for c in changes:
                print(f"  • {c}")

            update_url = f"{site['url']}/posts/{post_id}"
            update_data = {'content': new_content}
            r = requests.post(update_url, headers=headers, json=update_data, timeout=30)
            if r.status_code in (200, 201):
                print(f"  [OK] Updated")
                fixed_count += 1
            else:
                print(f"  [FAIL] HTTP {r.status_code} - {r.text[:200]}")
        else:
            skipped_count += 1

    print(f"\n{'='*50}")
    print(f"Done: {fixed_count} fixed, {skipped_count} unchanged")

if __name__ == '__main__':
    main()
