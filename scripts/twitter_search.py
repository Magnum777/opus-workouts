#!/usr/bin/env python3
"""
Twitter API - App-only (Bearer Token) for reading
"""

import requests
import sys

# Bearer Token (app-only auth - read only)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAG9h7gEAAAAAmU9kFWjqjB5bCQBuUB65b0a7uhM%3DlM8pt5Veu7OyzUuUgRUJXtINoaXN6DCazryTR4cM80pXalihd5"

def bearer_auth(r):
    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    return r

def search_tweets(query, max_results=10):
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {"query": query, "max_results": max_results}
    response = requests.get(url, auth=bearer_auth, params=params)
    return response

def main():
    query = "AI cofounder" if len(sys.argv) < 2 else sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"Searching: {query}")
    result = search_tweets(query, max_results)
    
    if result.status_code == 200:
        data = result.json()
        print(f"[OK] Found {len(data.get('data', []))} tweets")
        for tweet in data.get('data', [])[:5]:
            print(f"  - {tweet['text'][:100]}...")
    else:
        print(f"[X] Error: {result.status_code}")
        print(result.text)

if __name__ == "__main__":
    main()
