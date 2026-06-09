#!/usr/bin/env python3
"""
Twitter posting script using Twitter API v2
Credentials from CREDENTIALS.md
"""

import os
import requests
from requests_oauthlib import OAuth1
import json
import sys

# Twitter credentials
API_KEY = "u4R67N43iKvS8cpwmvqLdU515"
API_SECRET = "ARBg39EkWMFtB353cbjeu0RhMrFVjXyaY4xGyJz7GM2lWJLu4F"
ACCESS_TOKEN = "2022391980672655362-lGEIk3e2Yf3KXIBFIlAbOmEl5NNpU9"
ACCESS_SECRET = "y8dqX45uSYorKeAJ0z1AvuoRklND9mIS2BTJhM0S4huuU"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAG9h7gEAAAAAHMxPatSJxWxnz%2Fxw2ZUlzQmNBEo%3DHWh5yewzje8Fk0lds0GC6p7GHyqwbmqyVypJ3pF7PZhWDTpUFa"

# OAuth1 for user context (read/write)
auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

BASE_URL = "https://api.twitter.com/2"

def post_tweet(text):
    """Post a tweet"""
    url = f"{BASE_URL}/tweets"
    data = {"text": text}
    
    response = requests.post(url, auth=auth, json=data)
    return response

def get_me():
    """Get current user info"""
    url = f"{BASE_URL}/users/me"
    response = requests.get(url, auth=auth)
    return response

def search_tweets(query, max_results=10):
    """Search tweets"""
    url = f"{BASE_URL}/tweets/search/recent"
    params = {"query": query, "max_results": max_results}
    response = requests.get(url, auth=auth, params=params)
    return response

def main():
    if len(sys.argv) < 2:
        print("Usage: python twitter_post.py \"Your tweet text here\"")
        sys.exit(1)
    
    tweet_text = sys.argv[1]
    
    print(f" Posting tweet: {tweet_text[:50]}...")
    
    # First, verify credentials
    print(" Checking credentials...")
    me = get_me()
    if me.status_code != 200:
        print(f"X Auth failed: {me.status_code}")
        print(me.text)
        sys.exit(1)
    
    me_data = me.json()
    print(f"[*] Authenticated as: @{me_data['data']['username']}")
    
    # Post tweet
    print(" Posting tweet...")
    result = post_tweet(tweet_text)
    
    if result.status_code == 201:
        tweet_id = result.json()['data']['id']
        print(f"[OK] Tweet posted! ID: {tweet_id}")
        print(f"[LINK] https://twitter.com/i/status/{tweet_id}")
    else:
        print(f"[X] Failed: {result.status_code}")
        print(result.text)

if __name__ == "__main__":
    main()
