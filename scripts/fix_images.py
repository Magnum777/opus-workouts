import requests, base64

auth = base64.b64encode('nova:EVEONION_APP_PASSWORD_REDACTED'.encode()).decode()
headers = {'Authorization': f'Basic {auth}', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Re-upload each image to WordPress to get a fresh media ID
images_map = {
    25003: 'C:/Users/compj/.openclaw/workspace/media/generated/20260522-122529.jpg',
    24998: 'C:/Users/compj/.openclaw/workspace/media/generated/20260522-122658.jpg',
    24997: 'C:/Users/compj/.openclaw/workspace/media/generated/20260522-122228.jpg',
    24996: 'C:/Users/compj/.openclaw/workspace/media/generated/20260522-122359.jpg',
    25005: 'C:/Users/compj/.openclaw/workspace/media/generated/20260522-122228.jpg',  # was wrong image
}

media_ids = {}
for post_id, image_path in images_map.items():
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    fname = image_path.split('/')[-1]
    r = requests.post(
        'https://eveonion.com/wp-json/wp/v2/media',
        headers=headers,
        files={'file': (fname, image_data, 'image/jpeg')},
        data={'title': fname, 'alt_text': 'EVE Onion article feature image'}
    )
    if r.status_code in (200, 201):
        media = r.json()
        media_ids[post_id] = media['id']
        print(f'Post {post_id}: uploaded {fname} -> media ID {media["id"]}')
    else:
        print(f'Post {post_id}: FAILED upload {r.status_code} - {r.text[:100]}')

print()
# Now attach each fresh media ID to the post
for post_id, media_id in media_ids.items():
    r = requests.post(f'https://eveonion.com/wp-json/wp/v2/posts/{post_id}', headers=headers, json={'featured_media': media_id})
    print(f'Post {post_id}: set featured_media={media_id} -> {r.status_code}')