import requests
from requests_oauthlib import OAuth1

API_KEY = "u4R67N43iKvS8cpwmvqLdU515"
API_SECRET = "ARBg39EkWMFtB353cbjeu0RhMrFVjXyaY4xGyJz7GM2lWJLu4F"
ACCESS_TOKEN = "2022391980672655362-lGEIk3e2Yf3KXIBFIlAbOmEl5NNpU9"
ACCESS_SECRET = "y8dqX45uSYorKeAJ0z1AvuoRklND9mIS2BTJhM0S4huuU"

auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

tweet_text = "Fenris Creations (formerly CCP Games) partners with Google DeepMind to train AI on 23 years of EVE player behavior. The AI has already learned to scam itself out of a Titan and blame it on awoxing. #EVEOnline"

url = "https://api.twitter.com/2/tweets"
data = {"text": tweet_text}

response = requests.post(url, auth=auth, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 201:
    resp = response.json()
    tweet_id = resp.get("data", {}).get("id", "?")
    print(f"Tweet posted! ID: {tweet_id}")
    print(f"URL: https://x.com/EveOnion_/status/{tweet_id}")