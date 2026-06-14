import requests, os, base64, json

# Try Pexels direct image URL
pexels_id = '36765715'
img_url = f'https://images.pexels.com/photos/{pexels_id}/pexels-photo-{pexels_id}.jpeg?auto=compress&cs=tinysrgb&w=1600&h=900&dpr=2'

print(f'Downloading from: {img_url}')
r = requests.get(img_url, timeout=20)
print(f'Status: {r.status_code}')

if r.status_code == 200:
    temp_path = r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\temp_images\featured_36765715.jpg'
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, 'wb') as f:
        f.write(r.content)
    print(f'Saved: {temp_path} ({len(r.content)} bytes)')
    
    site_url = 'https://aitoolalliance.com/wp-json/wp/v2'
    user = 'aitoolalliance_u6cbhe'
    password = <SCRUBBED_WORDPRESS_APP_PASSWORD>
    creds = f'{user}:{password}'.encode()
    token = base64.b64encode(creds).decode()
    headers = {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'User-Agent': 'ContentNovaBot/2.0'
    }
    
    url = f'{site_url}/media'
    upload_headers = {k: v for k, v in headers.items() if k != 'Content-Type'}
    
    with open(temp_path, 'rb') as f:
        files = {'file': ('featured_36765715.jpg', f, 'image/jpeg')}
        data = {'alt_text': 'Professional business meeting in modern office with digital technology', 'post': 306}
        upload_r = requests.post(url, headers=upload_headers, files=files, data=data, timeout=60)
    
    print(f'Upload status: {upload_r.status_code}')
    if upload_r.status_code in (200, 201):
        res = upload_r.json()
        media_id = res.get('id')
        print(f'Media ID: {media_id}')
        
        set_url = f'{site_url}/posts/306'
        set_headers = headers.copy()
        set_headers['Content-Type'] = 'application/json'
        set_r = requests.post(set_url, headers=set_headers, json={'featured_media': media_id}, timeout=30)
        print(f'Set featured status: {set_r.status_code}')
        if set_r.status_code in (200, 201):
            print('SUCCESS: Featured image set!')
            os.remove(temp_path)
        else:
            print(f'Failed to set featured: {set_r.text[:200]}')
    else:
        print(f'Upload failed: {upload_r.text[:300]}')
else:
    print('Image download failed')
