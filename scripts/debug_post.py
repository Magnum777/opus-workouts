import requests, base64, json

auth = base64.b64encode('nova:EVEONION_APP_PASSWORD_REDACTED'.encode()).decode()
headers = {
    'Authorization': f'Basic {auth}',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

post_ids = [25005, 25004, 25003, 24999, 24998, 24997, 24996, 24993]
for post_id in post_ids:
    r = requests.get(f'https://eveonion.com/wp-json/wp/v2/posts/{post_id}', headers=headers)
    d = r.json()
    fm = d.get('featured_media', 'none')
    title = d['title']['rendered'][:50]
    print(f'ID {post_id} | featured_media={fm} | {title}')