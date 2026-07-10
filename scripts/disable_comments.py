import requests, base64, sys

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
            print(f"Error page {page}: HTTP {r.status_code}")
            break
        posts = r.json()
        if not posts:
            break
        all_posts.extend(posts)
        if len(posts) < 100:
            break
        page += 1
    return all_posts

def main():
    posts = get_all_posts()
    print(f"Found {len(posts)} posts")
    
    closed_count = 0
    already_closed = 0
    
    for p in posts:
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
            print(f"[OK] Post {post_id}: {title[:50]} - comments closed")
            closed_count += 1
        else:
            print(f"[FAIL] Post {post_id}: HTTP {r.status_code} - {r.text[:200]}")
    
    print(f"\nDone: {closed_count} closed, {already_closed} already closed")

if __name__ == '__main__':
    main()
