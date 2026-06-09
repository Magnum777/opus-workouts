import requests
import random

# Upload-post API key from memory
API_KEY = "UPLOADPOST_API_KEY_REDACTED"

# Poster path
poster_path = r"C:\Users\compj\.openclaw\workspace\docs\kybernauts_poster.png"

# Varying propaganda captions
captions = [
    "🩸 The void calls. Will you answer? Join the Kybernauts and carve your name into the stars. join.kybernauts.today #EVEOnline",
    "⚔️ Null sec isn't just a place—it's a way of life. Stand with us. join.kybernauts.today #EVEOnline",
    "🔥 Brothers in arms. Ships in formation. Victory in our sights. The Kybernauts recruit. join.kybernauts.today #EVEOnline",
    "💀 They fear the dark. We own it. Join the hunt. join.kybernauts.today #EVEOnline",
    "🌌 Your capsule. Your choice. Your legacy. The Kybernauts await. join.kybernauts.today #EVEOnline",
    "⚡ Power to the Pochven. Glory to the Kybernauts. Your fleet awaits. join.kybernauts.today #EVEOnline"
]

caption = random.choice(captions)

# Upload photos endpoint
url = "https://api.upload-post.com/api/upload_photos"
headers = {
    "Authorization": f"Apikey {API_KEY}"
}

# Read the image file
with open(poster_path, 'rb') as f:
    files = {
        'user': (None, 'Kybernauts'),
        'platform[]': (None, 'x'),
        'photos[]': ('kybernauts_poster.png', f, 'image/png'),
        'title': (None, caption)
    }
    
    response = requests.post(url, headers=headers, files=files)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code in [200, 201]:
    data = response.json()
    print(f"SUCCESS! Posted to Twitter/X")
    print(f"Caption: {caption}")
    if 'request_id' in data:
        print(f"Request ID: {data['request_id']}")
else:
    print(f"Failed to post")
