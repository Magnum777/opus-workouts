import requests
import os
import base64

urls_to_try = [
    'https://source.unsplash.com/1600x900/?healthcare,technology',
    'https://source.unsplash.com/1600x900/?medical,digital',
    'https://source.unsplash.com/1600x900/?hospital,technology',
]

temp_dir = r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\temp_images'
os.makedirs(temp_dir, exist_ok=True)

img_path = os.path.join(temp_dir, 'healthcare_ai_featured.jpg')
success = False

for url in urls_to_try:
    try:
        print('Trying:', url)
        r = requests.get(url, timeout=15, allow_redirects=True)
        ct = r.headers.get('content-type', '')
        print('  Status:', r.status_code, 'Content-Type:', ct, 'Length:', len(r.content))
        if r.status_code == 200 and 'image' in ct and len(r.content) > 10000:
            with open(img_path, 'wb') as f:
                f.write(r.content)
            print('  Saved to:', img_path)
            success = True
            break
    except Exception as e:
        print('  Error:', e)

if success:
    # Upload to WordPress
    user = 'nova.cofounder@gmail.com'
    password = <SCRUBBED_WORDPRESS_APP_PASSWORD>
    creds = f'{user}:{password}'.encode()
    token = base64.b64encode(creds).decode()
    headers = {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'User-Agent': 'ContentNovaBot/2.0'
    }
    
    upload_url = 'https://aibusinessinsider.org/wp-json/wp/v2/media'
    
    with open(img_path, 'rb') as f:
        files = {'file': ('healthcare_ai_featured.jpg', f, 'image/jpeg')}
        data = {'alt_text': 'Healthcare AI technology digital medical interface', 'post': '466'}
        r = requests.post(upload_url, headers=headers, files=files, data=data, timeout=60)
    
    print('Upload status:', r.status_code)
    if r.status_code in (200, 201):
        res = r.json()
        media_id = res.get('id')
        print('Media ID:', media_id)
        
        # Set as featured
        post_url = 'https://aibusinessinsider.org/wp-json/wp/v2/posts/466'
        headers['Content-Type'] = 'application/json'
        r2 = requests.post(post_url, headers=headers, json={'featured_media': media_id}, timeout=30)
        print('Featured image set status:', r2.status_code)
        if r2.status_code in (200, 201):
            print('SUCCESS: Featured image set!')
        else:
            print('Failed to set featured image:', r2.text[:200])
    else:
        print('Upload failed:', r.text[:300])
else:
    print('All URLs failed.')
