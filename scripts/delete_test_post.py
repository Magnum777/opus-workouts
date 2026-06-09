import requests, base64

site = {
    'url': 'https://aibusinessinsider.org/wp-json/wp/v2',
    'user': 'nova.cofounder@gmail.com',
    'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>
}
creds = f"{site['user']}:{site['pass']}".encode()
token = base64.b64encode(creds).decode()
headers = {
    'Authorization': f'Basic {token}',
    'User-Agent': 'ContentNovaBot/2.0',
    'Accept': 'application/json'
}

# Find test post
r = requests.get(f"{site['url']}/posts", headers=headers, params={'per_page': 10, 'status': 'draft'}, timeout=15)
if r.status_code == 200:
    for p in r.json():
        if p['title']['rendered'] == 'Test Post - Delete Me':
            d = requests.delete(f"{site['url']}/posts/{p['id']}", headers=headers, params={'force': 'true'}, timeout=15)
            print(f"Deleted test post {p['id']}: HTTP {d.status_code}")
            break
    else:
        print("Test post not found")
else:
    print(f"Could not list posts: HTTP {r.status_code}")
