#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post Kybernauts propaganda to Twitter using Tweepy"""

import tweepy
import random
import sys
import os

# Ensure UTF-8 encoding for stdout
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Twitter API credentials from CREDENTIALS.md
CONSUMER_KEY = "u4R67N43iKvS8cpwmvqLdU515"
CONSUMER_SECRET = "ARBg39EkWMFtB353cbjeu0RhMrFVjXyaY4xGyJz7GM2lWJLu4F"
ACCESS_TOKEN = "2022391980672655362-lGEIk3e2Yf3KXIBFIlAbOmEl5NNpU9"
ACCESS_SECRET = "y8dqX45uSYorKeAJ0z1AvuoRklND9mIS2BTJhM0S4huuU"

# Varying caption templates
CAPTIONS = [
    "The stars call to those brave enough to answer. Will you answer with us?",
    "New Eden doesn't forgive the weak. Join those who refuse to be prey.",
    "Every undock is a chance to write your legend. Make it count.",
    "The galaxy is vast, but only the bold claim their place in it.",
    "War is coming. The question is: which side will you be on?",
    "From the shadows we hunt. From the darkness we strike. Join us.",
    "Your pod awaits. Your enemies await. What are you waiting for?"
]

# Select random caption
caption_text = random.choice(CAPTIONS)
full_caption = f"{caption_text}\n\njoin.kybernauts.today\n#EVEOnline"

print(f"Caption: {caption_text}")
print(f"Full caption:\n{full_caption}")

# Image path
IMAGE_PATH = r"C:\Users\compj\.openclaw\workspace\docs\kybernauts_poster.png"

if not os.path.exists(IMAGE_PATH):
    print(f"ERROR: Image not found at {IMAGE_PATH}")
    sys.exit(1)

print(f"\nImage: {IMAGE_PATH}")
print(f"Image size: {os.path.getsize(IMAGE_PATH)} bytes")

# Authenticate with Twitter
print("\nAuthenticating with Twitter...")
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True)

try:
    # Verify credentials
    user = api.verify_credentials()
    print(f"Authentication successful! Logged in as: @{user.screen_name}")
    
    # Try uploading media with chunked upload
    print("\n[1/2] Uploading media (chunked)...")
    
    # Use chunked upload for media - pass file object directly
    with open(IMAGE_PATH, 'rb') as f:
        media = api.media_upload(
            filename="kybernauts_poster.png",
            file=f,
            chunked=True
        )
    print(f"Media ID: {media.media_id_string}")
    print(f"Media type: {media.media_type}")
    print(f"Media size: {media.size}")
    
    # Post tweet with media
    print("\n[2/2] Posting tweet...")
    tweet = api.update_status(
        status=full_caption,
        media_ids=[media.media_id_string]
    )
    
    print(f"\n[SUCCESS] Tweet posted!")
    print(f"Tweet ID: {tweet.id_str}")
    print(f"URL: https://twitter.com/i/status/{tweet.id_str}")
    
except tweepy.errors.Forbidden as e:
    print(f"\n[ERROR] Forbidden (403): {e}")
    print("\nThis usually means the app doesn't have write permissions.")
    print("Check Twitter Developer Portal app settings:")
    print("  - App must have 'Read and Write' permissions")
    print("  - User must have authorized the app")
    
    # Try text-only as fallback
    print("\nTrying text-only post as fallback...")
    try:
        tweet = api.update_status(status=full_caption)
        print(f"\n[SUCCESS] Text-only tweet posted!")
        print(f"Tweet ID: {tweet.id_str}")
        print(f"URL: https://twitter.com/i/status/{tweet.id_str}")
    except Exception as e2:
        print(f"Text-only also failed: {e2}")
        
except tweepy.TweepyException as e:
    print(f"\n[ERROR] Tweepy error: {e}")
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
