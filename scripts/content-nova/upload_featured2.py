import requests, base64, json, os

site = {
    'url': 'https://aitoolalliance.com/wp-json/wp/v2',
    'user': 'aitoolalliance_u6cbhe',
    'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>
}

def _auth(user, password):
    creds = f"{user}:{password}".encode()
    token = base64.b64encode(creds).decode()
    return {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'Content-Type': 'image/jpeg',
        'User-Agent': 'ContentNovaBot/2.0'
    }

img_path = r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\featured.jpg'

with open(img_path, 'rb') as f:
    img_data = f.read()

headers = _auth(site['user'], site['pass'])
headers['Content-Disposition'] = 'attachment; filename="ai-image-generators-ranked.jpg"'

url = f"{site['url']}/media"
resp = requests.post(url, headers=headers, data=img_data, timeout=60)
print('Upload Status:', resp.status_code)
data = resp.json()
print(json.dumps(data, indent=2)[:1500])

if 'id' in data:
    media_id = data['id']
    # Also update alt text
    post_url = f"{site['url']}/media/{media_id}"
    payload = {'alt_text': 'AI image generators comparison showing photorealistic portraits, artistic concept art, and text-based graphics'}
    headers2 = _auth(site['user'], site['pass'])
    headers2['Content-Type'] = 'application/json'
    r2 = requests.post(post_url, headers=headers2, json=payload, timeout=60)
    print('Alt text set:', r2.status_code)
    
    # Set as featured image on post 276
    post_update = f"{site['url']}/posts/276"
    payload2 = {'featured_media': media_id}
    r3 = requests.post(post_update, headers=headers2, json=payload2, timeout=60)
    print('Featured image set:', r3.status_code)
    print(r3.json())
