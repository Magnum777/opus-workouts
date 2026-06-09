"""
Test Reddit posting with form data (multipart)
"""
import requests

API_KEY = "UPLOADPOST_API_KEY_REDACTED"
API_BASE = "https://api.upload-post.com/api"

headers = {"Authorization": f"Apikey {API_KEY}"}

# Form data with all required fields
form_data = {
    "user": (None, "EVEPropaganda"),
    "platform[]": (None, "reddit"),
    "title": (None, "[Pochven Intel] Baba Yagas blob report — May 2026"),
    "body": (None, "Test post for Pochven intel tracking. Please ignore."),
    "subreddit": (None, "eve"),
}

print("=== Reddit form-data test ===")
resp = requests.post(f"{API_BASE}/upload_text", headers=headers, files=form_data, timeout=30)
print(f"Status: {resp.status_code}")
try:
    print(f"Response: {resp.json()}")
except:
    print(f"Text: {resp.text[:500]}")

# Also try with url parameter (some Reddit posts are links)
form_data2 = {
    "user": (None, "EVEPropaganda"),
    "platform[]": (None, "reddit"),
    "title": (None, "[Pochven] Weekly blob watch"),
    "url": (None, "https://zkillboard.com/corporation/98754582/"),
    "subreddit": (None, "eve"),
}

print("\n=== Reddit URL link test ===")
resp2 = requests.post(f"{API_BASE}/upload_text", headers=headers, files=form_data2, timeout=30)
print(f"Status: {resp2.status_code}")
try:
    print(f"Response: {resp2.json()}")
except:
    print(f"Text: {resp2.text[:500]}")

# Check Reddit posts to see what's already there
print("\n=== Reddit post history ===")
resp3 = requests.get(f"{API_BASE}/uploadposts/reddit/detailed-posts", headers={"Authorization": f"Apikey {API_KEY}"}, timeout=15)
print(f"Status: {resp3.status_code}")
try:
    data = resp3.json()
    posts = data.get("posts", [])
    print(f"Posts found: {len(posts)}")
    for p in posts[:3]:
        print(f"  - {p.get('title','No title')}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Text: {resp3.text[:500]}")

print("\n=== Done ===")
