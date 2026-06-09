import requests
import json

API_KEY = 'UPLOADPOST_API_KEY_REDACTED'
headers = {'Authorization': f'Apikey {API_KEY}'}

# Check history
r = requests.get('https://api.upload-post.com/api/uploadposts/history', headers=headers)
print(f'History: {r.status_code}')
data = r.json()

# Print keys
print(f"Keys: {data.keys()}")

# Get results
results = data.get('results', data.get('data', []))
print(f"Total results: {len(results)}")

for item in results[:15]:
    print(f"  {item.get('created_at')}: platform={item.get('platform')} status={item.get('status')} type={item.get('post_type', item.get('type', 'unknown'))}")
    if item.get('post_url'):
        print(f"    URL: {item['post_url']}")
    if item.get('title'):
        print(f"    Title: {item['title'][:60]}")
    if item.get('error'):
        print(f"    Error: {item['error']}")
    print()
