import requests
import base64
import hashlib
import hmac
import time
from requests_oauthlib import OAuth1Session

# Twitter API credentials from CREDENTIALS.md
API_KEY = "u4R67N43iKvS8cpwmvqLdU515"
API_SECRET = "ARBg39EkWMFtB353cbjeu0RhMrFVjXyaY4xGyJz7GM2lWJLu4F"
ACCESS_TOKEN = "2022391980672655362-lGEIk3e2Yf3KXIBFIlAbOmEl5NNpU9"
ACCESS_SECRET = "y8dqX45uSYorKeAJ0z1AvuoRklND9mIS2BTJhM0S4huuU"

# Create OAuth1 session
twitter = OAuth1Session(
    API_KEY,
    client_secret=API_SECRET,
    resource_owner_key=ACCESS_TOKEN,
    resource_owner_secret=ACCESS_SECRET
)

# Step 1: Upload the image
image_path = r"C:\Users\compj\.openclaw\workspace\docs\kybernauts_poster.png"

with open(image_path, 'rb') as f:
    image_data = f.read()

# Upload media to Twitter
upload_url = "https://upload.twitter.com/1.1/media/upload.json"
files = {'media': image_data}
response = twitter.post(upload_url, files=files)

if response.status_code != 200:
    print(f"Upload failed: {response.status_code}")
    print(response.text)
    exit(1)

media_id = response.json()['media_id_string']
print(f"Media uploaded successfully: {media_id}")

# Step 2: Create the tweet with the media
# Varying propaganda caption
captions = [
    "🩸 The void calls. Will you answer? Join the Kybernauts and carve your name into the stars. join.kybernauts.today #EVEOnline",
    "⚔️ Null sec isn't just a place—it's a way of life. Stand with us. join.kybernauts.today #EVEOnline",
    "🔥 Brothers in arms. Ships in formation. Victory in our sights. The Kybernauts recruit. join.kybernauts.today #EVEOnline",
    "💀 They fear the dark. We own it. Join the hunt. join.kybernauts.today #EVEOnline",
    "🌌 Your capsule. Your choice. Your legacy. The Kybernauts await. join.kybernauts.today #EVEOnline",
    "⚡ Power to the Pochven. Glory to the Kybernauts. Your fleet awaits. join.kybernauts.today #EVEOnline"
]

# Pick caption based on time (varies each run)
import random
caption = random.choice(captions)

tweet_url = "https://api.twitter.com/2/tweets"
tweet_data = {
    "text": caption,
    "media": {
        "media_ids": [media_id]
    }
}

response = twitter.post(tweet_url, json=tweet_data)

if response.status_code in [200, 201]:
    tweet_id = response.json()['data']['id']
    print(f"Tweet posted successfully! ID: {tweet_id}")
    print(f"Caption: {caption}")
    print(f"View at: https://twitter.com/i/status/{tweet_id}")
else:
    print(f"Tweet failed: {response.status_code}")
    print(response.text)
