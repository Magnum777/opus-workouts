import tweepy

# Twitter API credentials from CREDENTIALS.md (corrected)
API_KEY = "u4R67N43iKvS8cpwmvqLdU515"
API_SECRET = "ARBg39EkWMFtB353cbjeu0RhMrFVjXyaY4xGyJz7GM2lWJLu4F"
ACCESS_TOKEN = "2022391980672655362-lGEIk3e2Yf3KXIBFIlAbOmEl5NNpU9"
ACCESS_SECRET = "y8dqX45uSYorKeAJ0z1AvuoRklND9mIS2BTJhM0S4huuU"

# Create API v1.1 object for media upload
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# Create Client v2 for posting
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET
)

# Upload media using API v1.1
print("Uploading media to Twitter...")
media = api.media_upload(filename=r"C:\Users\compj\.openclaw\workspace\docs\kybernauts_poster.png")
print(f"Media ID: {media.media_id_string}")

# Post tweet with media using Client v2
caption = """🔥 FIGHT WITH PURPOSE 🔥

Your fleet. Your family. Your war.

The Kybernauts are recruiting elite pilots ready to dominate New Eden. Join us in the stars.

🚀 join.kybernauts.today

#EVEOnline #PvP #NullSec"""

print("\nPosting tweet...")
tweet = client.create_tweet(text=caption, media_ids=[media.media_id_string])

print(f"\n✅ SUCCESS! Tweet posted!")
print(f"Tweet ID: {tweet.data['id']}")
print(f"URL: https://twitter.com/i/status/{tweet.data['id']}")
