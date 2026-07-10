import requests, json

api_key = None
with open('C:/Users/compj/.openclaw/workspace/credentials/uploadpost.env') as f:
    for line in f:
        if line.startswith('UPLOADPOST_API_KEY='):
            api_key = line.split('=',1)[1].strip()
            break

tweet = 'Test post from EVE Onion. This account covers the most absurd, dramatic, and hilarious moments in New Eden. More to come soon. https://eveonion.com #EVEOnline'

url = 'https://api.upload-post.com/api/upload_text'
data = {'user': 'Eveonion', 'platform[]': ['x', 'bluesky'], 'title': tweet}
r = requests.post(url, data=data, headers={'Authorization': f'Apikey {api_key}'}, timeout=30)
print(f"Status: {r.status_code}")
resp = r.json()
print(json.dumps(resp, indent=2))
