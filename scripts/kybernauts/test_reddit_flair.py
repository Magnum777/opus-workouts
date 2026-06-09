"""
Test Reddit posting with flair parameter
"""
import requests

API_KEY = "UPLOADPOST_API_KEY_REDACTED"
API_BASE = "https://api.upload-post.com/api"

headers = {"Authorization": f"Apikey {API_KEY}"}

# Try with flair parameter (common r/eve flairs)
flair_options = ["Discussion", "Propaganda", "News", "AAR", "General", "Pochven"]

for flair in flair_options:
    form_data = {
        "user": (None, "EVEPropaganda"),
        "platform[]": (None, "reddit"),
        "title": (None, f"[Pochven Intel] Blob tracking test — flair={flair}"),
        "body": (None, "Test post for Pochven intel. Please ignore. This is a bot test."),
        "subreddit": (None, "eve"),
        "flair": (None, flair),
    }
    print(f"=== Trying flair: '{flair}' ===")
    resp = requests.post(f"{API_BASE}/upload_text", headers=headers, files=form_data, timeout=30)
    print(f"Status: {resp.status_code}")
    try:
        data = resp.json()
        success = data.get("results", {}).get("reddit", {}).get("success")
        error = data.get("results", {}).get("reddit", {}).get("error", "")
        print(f"Success: {success}")
        if error:
            print(f"Error: {error[:200]}")
        if success:
            print(f"✅ WORKING FLAIR: {flair}")
            break
    except:
        print(f"Text: {resp.text[:300]}")
    print()

# Also try upload_photos endpoint with image + text for Reddit
print("=== Test Reddit with upload_photos + flair ===")
image_path = "media/kybernauts/pochvenintel_avatar_v2.png"
with open(image_path, "rb") as img:
    form_data = {
        "user": (None, "EVEPropaganda"),
        "platform[]": (None, "reddit"),
        "photos[]": ("avatar.png", img, "image/png"),
        "title": (None, "[Pochven] Test image post with flair"),
        "subreddit": (None, "eve"),
        "flair": (None, "Screenshot"),
    }
    resp = requests.post(f"{API_BASE}/upload_photos", headers=headers, files=form_data, timeout=30)
    print(f"Status: {resp.status_code}")
    try:
        print(f"Response: {resp.json()}")
    except:
        print(f"Text: {resp.text[:300]}")

print("\n=== Done ===")
