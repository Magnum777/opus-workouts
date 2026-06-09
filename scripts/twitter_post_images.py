#!/usr/bin/env python3
"""Post images to Twitter/X v2 using Twitter API v2 with OAuth1"""
import os, sys, requests
from requests_oauthlib import OAuth1
import json

# EveOnion Twitter credentials
API_KEY = "u4R67N43iKvS8cpwmvqLdU515"
API_SECRET = "ARBg39EkWMFtB353cbjeu0RhMrFVjXyaY4xGyJz7GM2lWJLu4F"
ACCESS_TOKEN = "2022391980672655362-lGEIk3e2Yf3KXIBFIlAbOmEl5NNpU9"
ACCESS_SECRET = "y8dqX45uSYorKeAJ0z1AvuoRklND9mIS2BTJhM0S4huuU"

auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
BASE_URL = "https://api.twitter.com/2"

def get_me():
    url = f"{BASE_URL}/users/me"
    r = requests.get(url, auth=auth)
    return r

def upload_image(filepath):
    """Upload image and return media_id"""
    url = "https://upload.twitter.com/1.1/media/upload.json"
    with open(filepath, 'rb') as f:
        files = {'media': f.read()}
        r = requests.post(url, auth=auth, files=files)
    if r.status_code != 200:
        return None, f"Upload failed: {r.status_code} {r.text}"
    return r.json()['media_id_string'], None

def post_tweet(text, media_ids=None):
    url = f"{BASE_URL}/tweets"
    data = {"text": text}
    if media_ids:
        data["media"] = {"media_ids": media_ids}
    r = requests.post(url, auth=auth, json=data)
    return r

def get_twitter_handle():
    me = get_me()
    if me.status_code != 200:
        return None
    return me.json()['data']['username']

def thread_tweet(text, images):
    """Post thread - first tweet with first image, reply chain with remaining images"""
    if not images:
        r = post_tweet(text)
        if r.status_code == 201:
            return r.json()['data']['id']
        return None
    
    # Upload all images first
    media_ids = []
    for img in images:
        mid, err = upload_image(img)
        if err:
            print(f"  Upload error: {err}")
            continue
        media_ids.append(mid)
        print(f"  Uploaded {os.path.basename(img)}: {mid}")
    
    if media_ids:
        r = post_tweet(text, [media_ids[0]])
    else:
        r = post_tweet(text)
    
    if r.status_code != 201:
        print(f"Tweet failed: {r.status_code} {r.text}")
        return None
    
    tweet_id = r.json()['data']['id']
    parent_id = tweet_id
    
    # Reply with remaining images
    for mid in media_ids[1:]:
        r = post_tweet("", [mid])
        if r.status_code == 201:
            parent_id = r.json()['data']['id']
        else:
            print(f"  Reply failed: {r.status_code} {r.text}")
    
    return tweet_id

def main():
    images = sys.argv[1:]
    if not images:
        print("Usage: python twitter_post_images.py <image1.jpg> [image2.jpg] ... [text]")
        sys.exit(1)
    
    # Last arg is tweet text, rest are images
    text = "New satirical EVE Online art from EveOnion.com 🦝"
    if len(images) > 1 and not os.path.exists(images[-1]):
        text = images[-1]
        images = images[:-1]
    
    print(f"Posting to Twitter as @EveOnionNews...")
    
    me = get_me()
    if me.status_code != 200:
        print(f"[X] Auth failed: {me.status_code} {me.text}")
        sys.exit(1)
    username = me.json()['data']['username']
    print(f"[*] Authenticated as: @{username}")
    
    tweet_id = thread_tweet(text, images)
    if tweet_id:
        print(f"[OK] Posted! Tweet ID: {tweet_id}")
        print(f"[LINK] https://twitter.com/i/status/{tweet_id}")
    else:
        print("[X] Failed to post tweet")
        sys.exit(1)

if __name__ == "__main__":
    main()