import requests, base64, json

API_KEY = 'UPLOADPOST_API_KEY_REDACTED'
headers = {'Authorization': f'Apikey {API_KEY}'}

# Check media library
r = requests.get('https://api.upload-post.com/api/uploadposts/history?page=1&limit=50', headers=headers)
data = r.json()
results = data.get('results', data.get('data', []))
print(f'Total history items: {len(results)}')
for item in results[:20]:
    print(f"  {item.get('created_at')}: platform={item.get('platform')} status={item.get('status')}")
    if item.get('post_url'):
        print(f"    URL: {item['post_url']}")
    print()