import requests, json

headers = {'User-Agent': 'EVEOnionBot/1.0 (satire; contact: nova.cofounder@gmail.com)'}

endpoints = [
    'https://www.reddit.com/r/Eve/hot.json?limit=5',
    'https://www.reddit.com/r/Eve/hot/.json?limit=5',
    'https://www.reddit.com/r/Eve/new.json?limit=5',
]

for url in endpoints:
    r = requests.get(url, headers=headers, timeout=10)
    print(f"URL: {url}")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        try:
            data = r.json()
            posts = data.get('data', {}).get('children', [])
            print(f"Posts: {len(posts)}")
            for p in posts[:3]:
                d = p.get('data', {})
                print(f"  - {d.get('title', '')[:80]} | score={d.get('score')}")
        except:
            print(f"Parse error: {r.text[:200]}")
    else:
        print(f"Error: {r.text[:300]}")
    print()
