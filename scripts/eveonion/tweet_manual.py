import requests, base64

CREDS_FILE = "C:/Users/compj/.openclaw/workspace/credentials/uploadpost.env"
api_key = None
with open(CREDS_FILE) as f:
    for line in f:
        line = line.strip()
        if line.startswith("UPLOADPOST_API_KEY="):
            api_key = line.split("=", 1)[1].strip()

tweet = '"Ganker Posts Killmail Expecting Tears; Victim Responds With 45-Minute Tutorial on Emotional Maturity"\n\n#EVEOnline\n\nhttps://eveonion.com/ganker-posts-killmail-expecting-tears-victim-responds-with-45-minute-tutorial-on-emotional-maturity/'

print(f"Tweet: {tweet}")
print(f"Length: {len(tweet)}")

url = "https://api.upload-post.com/api/upload_text"
data = {"user": "Eveonion", "platform[]": "x", "title": tweet}
headers = {"Authorization": f"Apikey {api_key}"}
r = requests.post(url, data=data, headers=headers)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:300]}")
