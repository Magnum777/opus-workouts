import requests, base64
auth = base64.b64encode('nova:EVEONION_APP_PASSWORD_REDACTED'.encode()).decode()
r = requests.get(
    'https://eveonion.com/wp-json/wp/v2/posts?per_page=20&orderby=date&order=desc',
    headers={'Authorization': f'Basic {auth}', 'User-Agent': 'Mozilla/5.0'},
    timeout=10
)
posts = r.json()
print('All posts with featured images:')
for p in posts:
    fm = p.get('featured_media', 'none')
    title = p['title']['rendered']
    print(f'ID {p["id"]} | featured_media={fm} | {title[:70]}')