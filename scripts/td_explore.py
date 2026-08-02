"""TorrentDay explorer - login and understand site structure"""
import requests
import re
import os
import json

# Read credentials from .secrets
secrets_path = r"C:\Users\compj\.openclaw\workspace\.secrets"
td_user = ""
td_pass = ""
section = ""
with open(secrets_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("["):
            section = line.strip("[]")
            continue
        if "=" in line and section == "torrentday":
            key, val = line.split("=", 1)
            if key == "username":
                td_user = val
            elif key == "password":
                td_pass = val

print(f"Creds loaded: user={td_user} pass_len={len(td_pass)}")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
})

base = "https://www.torrentday.com"

# Step 1: GET login page
print("\n=== Step 1: GET login page ===")
r = session.get(f"{base}/torrents/login.php")
print(f"Status: {r.status_code}, Length: {len(r.text)}")
print(f"Cookies: {dict(session.cookies)}")

# Check for Cloudflare challenge
if "turnstile" in r.text.lower() or "challenge-platform" in r.text.lower():
    print("CLOUDFLARE TURNSTILE detected - need browser automation")

# Find form fields
inputs = re.findall(r'<input[^>]*name=["\']([^"\']+)["\'][^>]*>', r.text)
print(f"Form fields: {inputs}")

# Find CSRF tokens
csrf = re.findall(r'name=["\']([^"\']*(?:csrf|token)[^"\']*)["\'][^>]*value=["\']([^"\']+)', r.text, re.I)
print(f"CSRF tokens: {csrf}")

# Save login page
with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_login_page.html", "w", encoding="utf-8") as f:
    f.write(r.text)

# Step 2: POST login
print("\n=== Step 2: POST login ===")
login_data = {"username": td_user, "password": td_pass}
# Add any CSRF tokens
for name, val in csrf:
    login_data[name] = val

r = session.post(f"{base}/torrents/login.php", data=login_data, allow_redirects=True)
print(f"Login status: {r.status_code}, Length: {len(r.text)}")
print(f"Final URL: {r.url}")
print(f"Cookies: {dict(session.cookies)}")

# Check success indicators
if "logout" in r.text.lower() or "browse" in r.text.lower():
    print("LOGIN APPEARS SUCCESSFUL")
elif "error" in r.text.lower() or "incorrect" in r.text.lower():
    print("LOGIN FAILED - error found in response")
else:
    print("Login result unclear")
    with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_login_response.html", "w", encoding="utf-8") as f:
        f.write(r.text)

# Step 3: Browse torrents
print("\n=== Step 3: Browse torrents ===")
r = session.get(f"{base}/torrents/browse.php", allow_redirects=True)
print(f"Browse status: {r.status_code}, Length: {len(r.text)}")
print(f"Final URL: {r.url}")

if len(r.text) > 10000:
    print("Got substantial content - likely authenticated!")
    # Count torrent rows
    rows = re.findall(r'<tr[^>]*class=["\']([^"\']*)', r.text)
    print(f"Table rows: {len(rows)}")
    # Freeleech count
    free_count = len(re.findall(r'free', r.text, re.I))
    print(f"'free' mentions: {free_count}")
    with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_browse_authed.html", "w", encoding="utf-8") as f:
        f.write(r.text)
else:
    print(f"Short response - probably login page. First 500 chars:")
    print(r.text[:500])

# Step 4: Try freeleech filter
print("\n=== Step 4: Try freeleech browse ===")
for url in [
    f"{base}/torrents/browse.php?freeleech=1",
    f"{base}/torrents/browse.php?cat=0&freeleech=on",
    f"{base}/torrents/browse.php?free=1",
]:
    r = session.get(url, allow_redirects=True)
    print(f"  {url.split('?')[-1]} -> status={r.status_code} len={len(r.text)}")

# Step 5: Check for RSS
print("\n=== Step 5: Check RSS feed ===")
for url in [
    f"{base}/rss",
    f"{base}/torrents/rss.php",
    f"{base}/torrents/rss/",
]:
    try:
        r = session.get(url, allow_redirects=True, timeout=10)
        is_xml = "xml" in r.headers.get("content-type", "") or r.text.startswith("<?xml")
        print(f"  {url.split('/')[-1] or 'rss'} -> status={r.status_code} len={len(r.text)} xml={is_xml}")
        if is_xml and len(r.text) > 500:
            with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_rss.xml", "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"    RSS saved! First 300 chars:")
            print(f"    {r.text[:300]}")
    except Exception as e:
        print(f"  Error: {e}")

print("\nDone")