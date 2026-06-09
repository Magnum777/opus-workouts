"""
Test Upload-Post API connectivity and Reddit posting
"""
import requests

API_KEY = "UPLOADPOST_API_KEY_REDACTED"
API_BASE = "https://api.upload-post.com/api"

headers = {"Authorization": f"Apikey {API_KEY}", "Content-Type": "application/json"}

# Test 1: Check me endpoint
print("=== Test: /uploadposts/me ===")
resp = requests.get(f"{API_BASE}/uploadposts/me", headers=headers, timeout=15)
print(f"Status: {resp.status_code}")
try:
    print(f"Response: {resp.json()}")
except:
    print(f"Text: {resp.text[:500]}")

# Test 2: Reddit text with title + body
print("\n=== Test: Reddit text post ===")
payload = {
    "user": "EVEPropaganda",
    "platform": ["reddit"],
    "title": "[TEST] Pochven blob tracking",
    "body": "Test post for Pochven intel. Please ignore.",
    "subreddit": "eve",
}
resp = requests.post(f"{API_BASE}/upload_text", headers=headers, json=payload, timeout=30)
print(f"Status: {resp.status_code}")
try:
    print(f"Response: {resp.json()}")
except:
    print(f"Text: {resp.text[:500]}")

# Test 3: Try with just title (no body)
print("\n=== Test: Reddit text with just title ===")
payload2 = {
    "user": "EVEPropaganda",
    "platform": ["reddit"],
    "title": "[TEST] Pochven intel tracking test",
}
resp2 = requests.post(f"{API_BASE}/upload_text", headers=headers, json=payload2, timeout=30)
print(f"Status: {resp2.status_code}")
try:
    print(f"Response: {resp2.json()}")
except:
    print(f"Text: {resp2.text[:500]}")

# Test 4: Try with form data instead of JSON
print("\n=== Test: Form data ===")
form_data = {
    "user": (None, "EVEPropaganda"),
    "platform[]": (None, "reddit"),
    "title": (None, "[TEST] Pochven intel via form"),
}
resp3 = requests.post(f"{API_BASE}/upload_text", headers={"Authorization": f"Apikey {API_KEY}"}, files=form_data, timeout=30)
print(f"Status: {resp3.status_code}")
try:
    print(f"Response: {resp3.json()}")
except:
    print(f"Text: {resp3.text[:500]}")

print("\n=== Done ===")
