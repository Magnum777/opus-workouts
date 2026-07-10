api_key = """UPLOADPOST_API_KEY_REDACTED"""
tweet = """New from the Onion: Fenris just dropped a module that protects against Breacher pods. Every single EVE player is now googling "what is a Breacher pod" #EVEOnline"""

import requests

url = 'https://api.upload-post.com/api/upload_text'
headers = {
    'Authorization': 'Apikey ' + api_key
}

# Build form data with platform[] as repeated fields
data = [
    ('user', 'Eveonion'),
    ('platform[]', 'x'),
    ('platform[]', 'bluesky'),
    ('platform[]', 'discord'),
    ('title', tweet),
]

r = requests.post(url, headers=headers, data=data)
print('Status:', r.status_code)
print('Response:', r.text[:800])
