import requests, base64, sys
sys.stdout.reconfigure(encoding='utf-8')

SITES = {
    'aitoolalliance.com': {
        'url': 'https://aitoolalliance.com/wp-json/wp/v2',
        'user': 'aitoolalliance_u6cbhe',
        'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>
    },
    'aibusinessinsider.org': {
        'url': 'https://aibusinessinsider.org/wp-json/wp/v2',
        'user': 'nova.cofounder@gmail.com',
        'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>
    }
}

def close_comments(site_key, site):
    creds = f"{site['user']}:{site['pass']}".encode()
    token = base64.b64encode(creds).decode()
    headers = {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'Nova/1.0'
    }
    
    print(f"\n=== {site_key} ===")
    
    # 1. Close comments on all published posts
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
        if len(posts) < 100:
            break
        page += 1
    
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
            print(f"  [OK] Post {post_id}: {title[:50]} - closed")
            closed_count += 1
        else:
            print(f"  [FAIL] Post {post_id}: HTTP {r.status_code}")
    
    print(f"  Posts: {closed_count} closed, {already_closed} already closed")
    
    # 2. Set default comment status to closed for future posts
    r = requests.post(f"{site['url']}/settings", headers=headers,
                      json={'default_comment_status': 'closed', 'default_ping_status': 'closed'},
                      timeout=30)
    if r.status_code in (200, 201):
        print(f"  [OK] Default comment status set to closed")
    else:
        print(f"  [FAIL] Settings: HTTP {r.status_code}")

def main():
    for site_key, site in SITES.items():
        close_comments(site_key, site)
    
    print(f"\n{'='*50}")
    print("Done. Comments disabled across all sites.")

if __name__ == '__main__':
    main()
