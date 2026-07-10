import requests, json

api_key = None
with open('C:/Users/compj/.openclaw/workspace/credentials/uploadpost.env') as f:
    for line in f:
        if line.startswith('UPLOADPOST_API_KEY='):
            api_key = line.split('=',1)[1].strip()
            break

tweet = '"Local Miner Reports Asteroids More Aggressive Than War Target; CCP Refuses Comment" https://bbc.com/news/articles/cnvp7364q5no #EVEOnline'
print(f"Tweet length: {len(tweet)}")
print(f"Tweet: {tweet}")

url = 'https://api.upload-post.com/api/upload_text'
data = {'user': 'Eveonion', 'platform[]': 'x', 'title': tweet}
r = requests.post(url, data=data, headers={'Authorization': f'Apikey {api_key}'}, timeout=30)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")
