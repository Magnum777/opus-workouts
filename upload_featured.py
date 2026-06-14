import requests, os, base64, json

site = {
    'url': 'https://aibusinessinsider.org/wp-json/wp/v2',
    'user': 'nova.cofounder@gmail.com',
    'pass': <SCRUBBED_WORDPRESS_APP_PASSWORD>,
}

def _auth(user, password):
    creds = f"{user}:{password}".encode()
    token = base64.b64encode(creds).decode()
    return {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'User-Agent': 'ContentNovaBot/2.0'
    }

# Try Unsplash source API
queries = [
    "artificial intelligence technology",
    "chatbot customer service",
    "digital automation business",
    "robot ai futuristic"
]

img_url = None
for q in queries:
    url = f"https://source.unsplash.com/1200x630/?{q.replace(' ', ',')}"
    print(f"Trying: {url}")
    try:
        r = requests.get(url, allow_redirects=True, timeout=15)
        if r.status_code == 200 and len(r.content) > 5000:
            img_url = r.url
            print(f"Success! Got image from: {img_url}")
            break
    except Exception as e:
        print(f"Error: {e}")

if not img_url:
    # Try direct Unsplash photo IDs that are known to exist
    fallback_urls = [
        "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&h=630&fit=crop",
        "https://images.unsplash.com/photo-1535378437327-b7128d8e1d17?w=1200&h=630&fit=crop",
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1200&h=630&fit=crop",
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200&h=630&fit=crop",
    ]
    for url in fallback_urls:
        print(f"Trying fallback: {url}")
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200 and len(r.content) > 5000:
                img_url = url
                print(f"Fallback success! {img_url}")
                break
        except Exception as e:
            print(f"Error: {e}")

if not img_url:
    print("Could not find any image")
    exit(1)

# Download image
img_path = r"C:\Users\compj\.openclaw\workspace\temp_featured.jpg"
try:
    r = requests.get(img_url, timeout=20, stream=True)
    with open(img_path, 'wb') as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    print(f"Downloaded {os.path.getsize(img_path)} bytes")
except Exception as e:
    print(f"Download failed: {e}")
    exit(1)

# Upload to WordPress
headers = _auth(site['user'], site['pass'])
upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}

url = f"{site['url']}/media"
with open(img_path, 'rb') as f:
    files = {'file': ('featured-ai-customer-service.jpg', f, 'image/jpeg')}
    data = {'alt_text': 'AI-powered customer service automation concept', 'post': 496}
    r = requests.post(url, headers=upload_headers, files=files, data=data, timeout=60)

if r.status_code in (200, 201):
    res = r.json()
    media_id = res.get('id')
    print(f"Uploaded media ID: {media_id}")
    
    # Set as featured image
    headers['Content-Type'] = 'application/json'
    r2 = requests.post(f"{site['url']}/posts/496", headers=headers, json={'featured_media': media_id}, timeout=30)
    if r2.status_code in (200, 201):
        print("Featured image set successfully!")
        print(json.dumps({'ok': True, 'media_id': media_id}, indent=2))
    else:
        print(f"Failed to set featured: {r2.status_code}")
else:
    print(f"Upload failed: {r.status_code} - {r.text[:200]}")
