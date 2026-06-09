import requests, base64, sys
sys.stdout.reconfigure(encoding='utf-8')

site = {
    'url': 'https://aitoolalliance.com/wp-json/wp/v2',
    'user': 'aitoolalliance_u6cbhe',
    'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>
}

creds = f"{site['user']}:{site['pass']}".encode()
token = base64.b64encode(creds).decode()
headers = {
    'Authorization': f'Basic {token}',
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Nova/1.0'
}

print(f"Fetching posts from {site['url']}...")

page = 1
all_posts = []
while True:
    r = requests.get(f"{site['url']}/posts", headers=headers,
                     params={'per_page': 100, 'status': 'publish', 'page': page}, timeout=30)
    if r.status_code != 200:
        print(f"Error fetching posts: HTTP {r.status_code}")
        break
    posts = r.json()
    if not posts:
        break
    all_posts.extend(posts)
    print(f"  Page {page}: {len(posts)} posts")
    if len(posts) < 100:
        break
    page += 1

print(f"Total: {len(all_posts)} posts")

closed_count = 0
already_closed = 0

for p in all_posts:
    post_id = p['id']
    title = p['title']['rendered']
    current_status = p.get('comment_status', 'open')
    
    if current_status == 'closed':
        already_closed += 1
        continue
    
    update_url = f"{site['url']}/posts/{post_id}"
    update_data = {'comment_status': 'closed'}
    r = requests.post(update_url, headers=headers, json=update_data, timeout=30)
    if r.status_code in (200, 201):
        closed_count += 1
    else:
        print(f"  [FAIL] Post {post_id}: HTTP {r.status_code}")

print(f"Posts: {closed_count} closed, {already_closed} already closed")

# Set default
r = requests.post(f"{site['url']}/settings", headers=headers,
                  json={'default_comment_status': 'closed', 'default_ping_status': 'closed'},
                  timeout=30)
if r.status_code in (200, 201):
    print("Default comment status: closed")
else:
    print(f"Settings: HTTP {r.status_code}")

print("Done.")
