import urllib.request
import json
import base64

url = "https://aicofounderstack.com/wp-json/wp/v2/posts?per_page=100&status=publish"
req = urllib.request.Request(url, headers={"User-Agent": "Nova/1.0"})
with urllib.request.urlopen(req) as resp:
    data = json.load(resp)

print(f"Total posts: {len(data)}")
for p in data:
    print(f"ID: {p['id']} | Title: {p['title']['rendered']}")
