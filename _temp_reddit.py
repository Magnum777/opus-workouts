import urllib.request, json
req = urllib.request.Request("https://www.reddit.com/r/Eve/new.json?limit=15", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "application/json"})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    for post in data["data"]["children"][:15]:
        p = post["data"]
        print(p["title"], "|", p["score"], "pts", "|", p["num_comments"], "comments")
except Exception as e:
    print("Error:", e)
