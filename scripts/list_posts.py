import requests, base64

auth = base64.b64encode('nova:EVEONION_APP_PASSWORD_REDACTED'.encode()).decode()
r = requests.get(
    'https://eveonion.com/wp-json/wp/v2/posts?per_page=10&orderby=date&order=desc',
    headers={
        'Authorization': f'Basic {auth}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    },
    timeout=10
)
posts = r.json()
print(f'Found {len(posts)} posts:')
for p in posts:
    fm = p.get('featured_media', 0)
    print(f'ID {p["id"]} | {"HAS" if fm else "NO "} IMG | {p["date"][:10]} | {p["title"]["rendered"][:55]}')