"""Diagnose Pinterest board_id rejection in cross-poster.

The cross-poster sends board_id as a form field. Try several variants to
find what upload-post actually wants.
"""
import sqlite3, sys
import requests

conn = sqlite3.connect(r'C:\Users\compj\.openclaw/workspace/scripts/credentials/vault.db')
key = conn.execute("SELECT value FROM credentials WHERE service='upload_post' AND key='api_key'").fetchone()[0]
conn.close()
headers = {'Authorization': f'Apikey {key}'}

# Use an existing draft pin to avoid regenerating one
from pathlib import Path
draft_pins = sorted(Path(r'C:\Users\compj\.openclaw/workspace/memory/prompt-pack-social-drafts').glob('*_pin.png'))
if not draft_pins:
    print('No draft pins available - need to render one first')
    sys.exit(1)
test_pin = draft_pins[-1]
print(f'Using test pin: {test_pin}')

BOARD_ID = '1124140825679666015'  # AI Tools & Startup Gear
url = 'https://api.upload-post.com/api/upload_photos'

variants = [
    {"name": "A: board_id (current cross-poster shape)", "data": {
        "user": "nova", "platform[]": ["pinterest"], "title": "diag test",
        "board_id": BOARD_ID,
    }},
    {"name": "B: pinterest_board_id", "data": {
        "user": "nova", "platform[]": ["pinterest"], "title": "diag test",
        "pinterest_board_id": BOARD_ID,
    }},
    {"name": "C: board_id[] (array)", "data": {
        "user": "nova", "platform[]": ["pinterest"], "title": "diag test",
        "board_id[]": [BOARD_ID],
    }},
    {"name": "D: no board_id at all", "data": {
        "user": "nova", "platform[]": ["pinterest"], "title": "diag test",
    }},
]

for v in variants:
    print(f"\n=== {v['name']} ===")
    files = {"photos[]": (test_pin.name, open(test_pin, 'rb'), 'image/png')}
    r = requests.post(url, headers=headers, data=v['data'], files=files, timeout=30)
    print(f"status: {r.status_code}")
    print(r.text[:500])
