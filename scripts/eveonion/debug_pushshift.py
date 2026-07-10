import requests

# Try Pushshift (free, no auth) as Reddit mirror
url = "https://api.pushshift.io/reddit/search/submission/?subreddit=Eve&sort=score&sort_type=desc&size=5&score=>10"
headers = {'User-Agent': 'EVEOnionBot/1.0'}
r = requests.get(url, headers=headers, timeout=10)
print(f"Pushshift status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    posts = data.get('data', [])
    print(f"Posts: {len(posts)}")
    for p in posts[:5]:
        print(f"  - {p.get('title', '')[:80]} | score={p.get('score')} | comments={p.get('num_comments')}")

# Try old.reddit.com
print("\nTrying old.reddit.com...")
r2 = requests.get("https://old.reddit.com/r/Eve/hot.json?limit=5", headers={"User-Agent": "EVEOnionBot/1.0"}, timeout=10)
print(f"old.reddit.com status: {r2.status_code}")
if r2.status_code == 200:
    try:
        data = r2.json()
        posts = data.get('data', {}).get('children', [])
        print(f"Posts: {len(posts)}")
    except:
        print(f"Not JSON: {r2.text[:200]}")
