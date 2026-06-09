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
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'ContentNovaBot/2.0'
}

r = requests.post(f"{site['url']}/posts", headers=headers, json={
    'title': 'Test Post - Delete Me',
    'content': '<p>This is a test. Delete this post.</p>',
    'status': 'draft'
}, timeout=30)

print(f'Status: {r.status_code}')
print(f'Response: {r.text[:300]}')
