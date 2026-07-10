import requests, base64, re, json, html

from vault_helper import get_credential

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

print(f"Total published posts: {len(all_posts)}")

# Check for raw markdown in rendered content
for p in all_posts:
    content = p.get('content', {}).get('rendered', '')
    raw_content = p.get('content', {}).get('raw', '')  # Sometimes raw is available
    
    # Look for markdown patterns NOT inside HTML tags (meaning raw markdown)
    # Use regex to find ### not inside <
    md_headers = re.findall(r'(?:^|>)\s*#{1,3}\s+([^\n<]+)', content)
    md_bold = re.findall(r'\*\*([^\*]+)\*\*', content)
    md_lists = re.findall(r'(?:^|>)\s*-\s+([^\n<]+)', content)
    
    if md_headers or md_bold or md_lists:
        print(f"\nPOST {p['id']}: {p['title']['rendered']}")
        print(f"  Headers: {md_headers[:3]}")
        print(f"  Bold: {md_bold[:3]}")
        print(f"  Lists: {md_lists[:3]}")
        print(f"  Content preview:\n{content[:500]}")

# Also check for specific post about "Sales" from the screenshot
for p in all_posts:
    if 'sales' in p['title']['rendered'].lower() or 'outreach' in p['title']['rendered'].lower():
        print(f"\n--- MATCHING POST: {p['id']} - {p['title']['rendered']} ---")
        print(p.get('content', {}).get('rendered', '')[:1500])
