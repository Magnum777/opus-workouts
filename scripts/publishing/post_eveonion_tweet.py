import requests

API_KEY = "UPLOADPOST_API_KEY_REDACTED"

url = "https://api.upload-post.com/api/upload_text"
headers = {"Authorization": f"Apikey {API_KEY}"}

data = {
    "user": "Eveonion",
    "platform": ["x"],
    "title": "Fenris Creations (formerly CCP Games) partners with Google DeepMind to train AI on 23 years of EVE player behavior. The AI has already learned to scam itself out of a Titan and blame it on awoxing. #EVEOnline"
}

r = requests.post(url, json=data, headers=headers)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:500]}")

if r.status_code == 200:
    resp = r.json()
    if resp.get("success"):
        print("Tweet posted successfully!")
    else:
        print(f"Issue: {resp}")