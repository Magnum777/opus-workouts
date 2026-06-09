"""
Test different parameter names for Reddit posting via Upload-Post
"""
import requests

API_KEY = "UPLOADPOST_API_KEY_REDACTED"
API_BASE = "https://api.upload-post.com/api"

headers = {"Authorization": f"Apikey {API_KEY}"}

# Test 1: selftext instead of body
form_data = {
    "user": (None, "EVEPropaganda"),
    "platform[]": (None, "reddit"),
    "title": (None, "[Pochven] Test with selftext field"),
    "selftext": (None, "Test body text for r/eve. Please ignore this test post."),
    "subreddit": (None, "eve"),
}
print("=== Test: selftext field ===")
resp = requests.post(f"{API_BASE}/upload_text", headers=headers, files=form_data, timeout=30)
print(f"Status: {resp.status_code}")
try:
    data = resp.json()
    print(f"Success: {data.get('results',{}).get('reddit',{}).get('success')}")
    print(f"Error: {data.get('results',{}).get('reddit',{}).get('error','')[:200]}")
except:
    print(f"Text: {resp.text[:300]}")

# Test 2: text instead of body
form_data2 = {
    "user": (None, "EVEPropaganda"),
    "platform[]": (None, "reddit"),
    "title": (None, "[Pochven] Test with text field"),
    "text": (None, "Test body text for r/eve. Please ignore this test post."),
    "subreddit": (None, "eve"),
}
print("\n=== Test: text field ===")
resp2 = requests.post(f"{API_BASE}/upload_text", headers=headers, files=form_data2, timeout=30)
print(f"Status: {resp2.status_code}")
try:
    data = resp2.json()
    print(f"Success: {data.get('results',{}).get('reddit',{}).get('success')}")
    print(f"Error: {data.get('results',{}).get('reddit',{}).get('error','')[:200]}")
except:
    print(f"Text: {resp2.text[:300]}")

# Test 3: body + flair_template_id (dummy)
form_data3 = {
    "user": (None, "EVEPropaganda"),
    "platform[]": (None, "reddit"),
    "title": (None, "[Pochven] Test with flair_template_id"),
    "body": (None, "Test body text. Please ignore."),
    "subreddit": (None, "eve"),
    "flair_template_id": (None, "12345"),
}
print("\n=== Test: flair_template_id ===")
resp3 = requests.post(f"{API_BASE}/upload_text", headers=headers, files=form_data3, timeout=30)
print(f"Status: {resp3.status_code}")
try:
    data = resp3.json()
    print(f"Success: {data.get('results',{}).get('reddit',{}).get('success')}")
    print(f"Error: {data.get('results',{}).get('reddit',{}).get('error','')[:200]}")
except:
    print(f"Text: {resp3.text[:300]}")

# Test 4: Both body AND selftext
form_data4 = {
    "user": (None, "EVEPropaganda"),
    "platform[]": (None, "reddit"),
    "title": (None, "[Pochven] Test body+selftext"),
    "body": (None, "Body field text."),
    "selftext": (None, "Selftext field text."),
    "subreddit": (None, "eve"),
}
print("\n=== Test: body + selftext ===")
resp4 = requests.post(f"{API_BASE}/upload_text", headers=headers, files=form_data4, timeout=30)
print(f"Status: {resp4.status_code}")
try:
    data = resp4.json()
    print(f"Success: {data.get('results',{}).get('reddit',{}).get('success')}")
    print(f"Error: {data.get('results',{}).get('reddit',{}).get('error','')[:200]}")
except:
    print(f"Text: {resp4.text[:300]}")

# Test 5: body + kind=selftext (Reddit API parameter)
form_data5 = {
    "user": (None, "EVEPropaganda"),
    "platform[]": (None, "reddit"),
    "title": (None, "[Pochven] Test with kind=selftext"),
    "body": (None, "Test body text. Please ignore."),
    "subreddit": (None, "eve"),
    "kind": (None, "self"),
}
print("\n=== Test: kind=self ===")
resp5 = requests.post(f"{API_BASE}/upload_text", headers=headers, files=form_data5, timeout=30)
print(f"Status: {resp5.status_code}")
try:
    data = resp5.json()
    print(f"Success: {data.get('results',{}).get('reddit',{}).get('success')}")
    print(f"Error: {data.get('results',{}).get('reddit',{}).get('error','')[:200]}")
except:
    print(f"Text: {resp5.text[:300]}")

print("\n=== Done ===")
