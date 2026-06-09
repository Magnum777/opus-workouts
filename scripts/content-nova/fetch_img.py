import requests, os, base64, json

img_path = r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\temp_featured.jpg'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# Try Unsplash source direct
url = 'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200&q=80'
r = requests.get(url, headers=headers, timeout=15, stream=True)
print('Unsplash status:', r.status_code, 'Content-Type:', r.headers.get('content-type', 'unknown'))
if r.status_code == 200 and 'image' in r.headers.get('content-type', ''):
    with open(img_path, 'wb') as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    print('Saved, size:', os.path.getsize(img_path))
else:
    # Try picsum
    r2 = requests.get('https://picsum.photos/1200/800', headers=headers, timeout=15, stream=True, allow_redirects=True)
    print('Picsum status:', r2.status_code, 'Content-Type:', r2.headers.get('content-type', 'unknown'))
    if r2.status_code == 200 and 'image' in r2.headers.get('content-type', ''):
        with open(img_path, 'wb') as f:
            for chunk in r2.iter_content(8192):
                f.write(chunk)
        print('Saved picsum, size:', os.path.getsize(img_path))
