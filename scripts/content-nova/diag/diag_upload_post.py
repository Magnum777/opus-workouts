"""Diagnostic: figure out what upload-post actually wants when profile='nova'"""
import sqlite3, json, sys
try:
    import requests
except ImportError:
    print("requests missing")
    sys.exit(1)

conn = sqlite3.connect(r'C:\Users\compj\.openclaw\workspace\scripts\credentials\vault.db')
row = conn.execute("SELECT value FROM credentials WHERE service='upload_post' AND key='api_key'").fetchone()
conn.close()
if not row:
    print("no api key")
    sys.exit(1)
key = row[0]
headers = {'Authorization': f'Apikey {key}'}

URL = 'https://api.upload-post.com/api/upload_text'

tests = [
    {"name": "test1: skill.md shape (json, user+platform+title)",
     "kwargs": {"headers": headers, "json": {"user": "nova", "platform": ["x"], "title": "diagnostic test 1"}}},
    {"name": "test2: + username field",
     "kwargs": {"headers": headers, "json": {"user": "nova", "username": "AICofounderStack", "platform": ["x"], "title": "diagnostic test 2"}}},
    {"name": "test3: form-encoded",
     "kwargs": {"headers": headers, "data": {"user": "nova", "platform": "x", "username": "AICofounderStack", "title": "diagnostic test 3"}}},
    {"name": "test4: profile_username instead of user",
     "kwargs": {"headers": headers, "json": {"profile_username": "nova", "platform": ["x"], "title": "diagnostic test 4"}}},
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
