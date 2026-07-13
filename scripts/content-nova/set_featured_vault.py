"""Upload featured image and set on post using vault credentials."""
import sys, requests, base64, json, mimetypes, glob, os
sys.path.insert(0, r'C:\Users\compj\.openclaw\workspace\scripts')
from vault_helper import get_credential

site_key = sys.argv[1] if len(sys.argv) > 1 else 'aicofounderstack.com'
post_id = sys.argv[2] if len(sys.argv) > 2 else '656'

# Vault keys are like 'aicofounderstack_user', 'aicofounderstack_pass'
vault_prefix = site_key.replace('.com', '').replace('.org', '')

user = get_credential('wordpress', f'{vault_prefix}_user')
pwd = get_credential('wordpress', f'{vault_prefix}_pass')

url_base = f'https://www.{site_key}'

creds = f'{user}:{pwd}'.encode()
token = base64.b64encode(creds).decode()

# Find the image file
temp_dir = r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\temp_images'
image_files = glob.glob(os.path.join(temp_dir, '*'))
if not image_files:
    print('No image files found in temp_images')
    sys.exit(1)

filepath = image_files[0]
filename = os.path.basename(filepath)
mime_type = mimetypes.guess_type(filepath)[0] or 'image/jpeg'

print(f'Uploading: {filepath} ({mime_type})')

# Upload media
url = f'{url_base}/wp-json/wp/v2/media'
headers = {
    'Authorization': f'Basic {token}',
}

with open(filepath, 'rb') as f:
    files = {
        'file': (filename, f, mime_type)
    }
    r = requests.post(url, headers=headers, files=files, timeout=60)

print(f'Upload status: {r.status_code}')
if r.status_code in (200, 201):
    res = r.json()
    media_id = res.get('id')
    media_url = res.get('source_url')
    print(f'Media uploaded: id={media_id}, url={media_url}')
    
    # Set as featured image
    post_url = f'{url_base}/wp-json/wp/v2/posts/{post_id}'
    headers2 = {
        'Authorization': f'Basic {token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data2 = {'featured_media': media_id}
    r2 = requests.post(post_url, headers=headers2, json=data2, timeout=30)
    print(f'Featured image set: {r2.status_code}')
    if r2.status_code in (200, 201):
        print('Success!')
    else:
        print(f'Error: {r2.text[:500]}')
else:
    print(f'Error: {r.text[:500]}')
