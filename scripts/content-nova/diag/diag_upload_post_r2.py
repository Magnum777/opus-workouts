"""Round 2: figure out the exact form-data shape upload-post wants."""
import sqlite3, json, sys
import requests

conn = sqlite3.connect(r'C:\Users\compj\.openclaw\workspace\scripts\credentials\vault.db')
key = conn.execute("SELECT value FROM credentials WHERE service='upload_post' AND key='api_key'").fetchone()[0]
conn.close()
headers = {'Authorization': f'Apikey {key}'}

URL = 'https://api.upload-post.com/api/upload_text'

tests = [
    {"name": "r2t1: platform[] + username (form)",
     "kwargs": {"headers": headers, "data": {"user": "nova", "platform[]": "x", "username": "AICofounderStack", "title": "r2 test 1"}}},
    {"name": "r2t2: platform[] + username[] (form, array)",
     "kwargs": {"headers": headers, "data": {"user": "nova", "platform[]": ["x"], "username[]": ["AICofounderStack"], "title": "r2 test 2"}}},
    {"name": "r2t3: platform[] + twitter_username (form)",
     "kwargs": {"headers": headers, "data": {"user": "nova", "platform[]": "x", "twitter_username": "AICofounderStack", "title": "r2 test 3"}}},
    {"name": "r2t4: json with platform[] array key",
     "kwargs": {"headers": headers, "json": {"user": "nova", "platform[]": ["x"], "title": "r2 test 4"}}},
    {"name": "r2t5: form, just user+platform[]+title (no username)",
     "kwargs": {"headers": headers, "data": {"user": "nova", "platform[]": ["x"], "title": "r2 test 5"}}},
]

for t in tests:
    print(f"=== {t['name']} ===")
    try:
        r = requests.post(URL, timeout=30, **t['kwargs'])
        print(f"status: {r.status_code}")
        print(r.text[:500])
    except Exception as e:
        print(f"error: {e}")
    print()
