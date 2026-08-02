"""TorrentDay - explore actual site structure with authenticated cookies"""
import requests
import re
import os

secrets_path = r"C:\Users\compj\.openclaw\workspace\.secrets"
cookies = {}
section = ""
with open(secrets_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("["):
            section = line.strip("[]")
            continue
        if "=" in line and section == "torrentday":
            key, val = line.split("=", 1)
            if key in ("uid", "pass_cookie", "td_theme"):
                cookie_key = "pass" if key == "pass_cookie" else key
                cookies[cookie_key] = val

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
})
session.cookies.set("uid", cookies["uid"], domain=".torrentday.com", path="/")
session.cookies.set("pass", cookies["pass"], domain=".torrentday.com", path="/")

base = "https://www.torrentday.com"

# The 404 page had content - let's look at the actual HTML structure
# First, try the root
print("=== Root page ===")
r = session.get(base + "/", allow_redirects=True)
print(f"Status: {r.status_code}, Length: {len(r.text)}, URL: {r.url}")
with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_root.html", "w", encoding="utf-8") as f:
    f.write(r.text)

# Find all links in the root page
links = re.findall(r'href="([^"]*)"', r.text)
unique_links = list(set(links))
print(f"Unique links: {len(unique_links)}")
for link in sorted(unique_links)[:30]:
    print(f"  {link}")

# Look for nav links specifically
nav_links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', r.text)
print(f"\nNav links ({len(nav_links)}):")
for href, text in nav_links[:30]:
    text = text.strip()
    if text:
        print(f"  {text} -> {href}")

# Try common TorrentDay paths
print("\n=== Testing paths ===")
paths = [
    "/",
    "/browse",
    "/browse.php",
    "/torrents",
    "/torrents/browse",
    "/torrents/browse.php",
    "/torrents/",
    "/index.php",
    "/main.php",
    "/download.php",
    "/details.php",
    "/torrents/details.php",
    "/rss.php",
    "/torrents/rss.php",
    "/torrents/rss",
    "/freeleech",
    "/torrents/freeleech",
]

for path in paths:
    try:
        r = session.get(base + path, allow_redirects=True, timeout=10)
        is_authed = "logout" in r.text.lower() or len(r.text) > 20000
        print(f"  {path} -> {r.status_code} {len(r.text)} chars authed={is_authed} url={r.url}")
    except Exception as e:
        print(f"  {path} -> Error: {str(e)[:80]}")

# Check the 404 page more carefully - it had content
print("\n=== Analyzing 404/browse page ===")
r = session.get(base + "/torrents/browse.php", allow_redirects=True)
# Look for JavaScript redirects
js_redirects = re.findall(r'(?:window\.)?location\s*=\s*["\']([^"\']*)', r.text)
print(f"JS redirects: {js_redirects}")

# Look for meta redirects
meta_redirects = re.findall(r'<meta[^>]*http-equiv=["\']refresh["\'][^>]*content=["\'][^"\']*url=([^"\']*)', r.text, re.I)
print(f"Meta redirects: {meta_redirects}")

# Look for form actions
form_actions = re.findall(r'<form[^>]*action=["\']([^"\']*)', r.text)
print(f"Form actions: {form_actions}")

# Look for script sources
script_srcs = re.findall(r'<script[^>]*src=["\']([^"\']*)', r.text)
print(f"Script sources: {script_srcs[:10]}")

# Check if it's a Cloudflare challenge page
if "challenge-platform" in r.text or "turnstile" in r.text.lower():
    print("STILL Cloudflare challenge page")
elif "login" in r.text.lower() and len(r.text) < 10000:
    print("Login page (short)")
else:
    print(f"Unknown page type, first 500 chars:")
    print(r.text[:500])

print("\nDone")