import requests
import json

API_KEY = 'UPLOADPOST_API_KEY_REDACTED'
headers = {'Authorization': f'Apikey {API_KEY}'}

# Check profiles
r = requests.get('https://api.upload-post.com/api/uploadposts/history', headers=headers)
data = r.json()
print("Profiles:", data.get('profiles', []))

# Check if there are any posts
for key in ['history', 'in_progress']:
    items = data.get(key, [])
    print(f"\n{key}: {len(items)} items")
    for item in items[:5]:
        print(f"  {item}")

# Check all endpoints for POST
print("\n\n--- Testing POST endpoints ---")
for endpoint in ['upload_videos', 'uploads/videos', 'api/upload_videos', 'v1/upload_videos', 'upload/posts/videos']:
    r = requests.post(f'https://api.upload-post.com/api/{endpoint}', data={'user': 'Kybernauts', 'platform[]': 'x', 'title': 'test'}, headers=headers)
    print(f'POST /api/{endpoint}: {r.status_code}')
    if r.status_code != 404:
        print(f"  Response: {r.text[:200]}")

# Try upload_photos with video to instagram (where it's allowed)
print("\n--- Try video to instagram via photos endpoint ---")
video_path = r'C:\Users\compj\.openclaw\workspace\media\kybernauts\propaganda\EVE_Poster_15.11.mp4'
files = {'photos[]': open(video_path, 'rb')}
data = {'user': 'Kybernauts', 'platform[]': 'instagram', 'title': 'Test video on instagram'}
r = requests.post('https://api.upload-post.com/api/upload_photos', data=data, files=files, headers=headers)
print(f'upload_photos (video -> instagram): {r.status_code}')
print(r.text[:500])
