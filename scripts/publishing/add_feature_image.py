import requests, base64, json

# WordPress credentials
WP_URL = "https://eveonion.com/wp-json/wp/v2"
WP_USER = "nova"
WP_PASS = "EVEONION_APP_PASSWORD_REDACTED"
WP_AUTH = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
WP_HEADERS = {
    "Authorization": f"Basic {WP_AUTH}",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

# Upload image as media
image_path = r"C:\Users\compj\.openclaw\workspace\scripts\publishing\eveonion_feature_fenris.jpg"
with open(image_path, "rb") as f:
    image_data = f.read()

files = {
    "file": ("fenris-ai-capsuleers.jpg", image_data, "image/jpeg")
}
data = {
    "title": "Fenris Creations Announces AI-Powered Capsuleers Will Replace Human Players",
    "alt_text": "AI robot sits at a spaceship command console replacing human EVE Online players",
    "caption": "An AI capsuleer takes the helm while human pilots watch in disbelief. (EVE Onion)"
}

print("Uploading image to WordPress...")
r = requests.post(
    f"{WP_URL}/media",
    headers=WP_HEADERS,
    files=files,
    data=data
)
print(f"Upload status: {r.status_code}")

if r.status_code in (200, 201):
    media = r.json()
    media_id = media["id"]
    media_url = media["source_url"]
    print(f"Image uploaded! ID: {media_id}")
    print(f"URL: {media_url}")

    # Update the article with featured image
    post_id = 25000
    update_data = {"featured_media": media_id}
    r2 = requests.post(
        f"{WP_URL}/posts/{post_id}",
        headers={**WP_HEADERS, "Content-Type": "application/json"},
        json=update_data
    )
    print(f"Update status: {r2.status_code}")
    if r2.status_code == 200:
        post = r2.json()
        print(f"Article updated! Featured image set.")
        print(f"Article URL: {post['link']}")
    else:
        print(f"Update error: {r2.text[:300]}")
else:
    print(f"Upload error: {r.text[:300]}")