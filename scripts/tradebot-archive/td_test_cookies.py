"""Test TorrentDay access with Firefox cookies"""
import requests
import re
import os

# Read cookies from .secrets
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

print(f"Cookies loaded: uid={cookies.get('uid')}, pass={cookies.get('pass', '')[:10]}...")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
})
session.cookies.set("uid", cookies["uid"], domain=".torrentday.com", path="/")
session.cookies.set("pass", cookies["pass"], domain=".torrentday.com", path="/")
session.cookies.set("td_theme", cookies.get("td_theme", "dark"), domain="www.torrentday.com", path="/")

base = "https://www.torrentday.com"

# Test 1: Browse page
print("\n=== Test: Browse torrents ===")
r = session.get(f"{base}/torrents/browse.php", allow_redirects=True)
print(f"Status: {r.status_code}, Length: {len(r.text)}, URL: {r.url}")

is_login = "login" in r.url.lower() or "member access" in r.text.lower()
is_authed = "logout" in r.text.lower() or "browse" in r.url.lower()

if is_login and not is_authed:
    print("NOT AUTHENTICATED - still on login page")
else:
    print("AUTHENTICATED - got browse page!")
    
    # Save for analysis
    with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_browse_authed.html", "w", encoding="utf-8") as f:
        f.write(r.text)
    
    # Look for torrent table
    torrent_rows = re.findall(r'<tr[^>]*>', r.text)
    print(f"Table rows found: {len(torrent_rows)}")
    
    # Look for freeleech
    free_count = len(re.findall(r'free', r.text, re.I))
    print(f"'free' mentions: {free_count}")
    
    # Find category links
    cats = re.findall(r'cat=(\d+)[^>]*>([^<]+)', r.text)
    unique_cats = list(set(cats))
    print(f"Categories found: {len(unique_cats)}")
    for cid, cname in sorted(unique_cats, key=lambda x: int(x[0]))[:20]:
        print(f"  cat={cid}: {cname}")
    
    # Find torrent download links
    dl_links = re.findall(r'href="([^"]*download[^"]*)"', r.text, re.I)
    print(f"Download links found: {len(dl_links)}")
    for link in dl_links[:5]:
        print(f"  {link}")

# Test 2: Freeleech browse
print("\n=== Test: Freeleech torrents ===")
r = session.get(f"{base}/torrents/browse.php?freeleech=1", allow_redirects=True)
print(f"Status: {r.status_code}, Length: {len(r.text)}")
if len(r.text) > 10000 and "login" not in r.url.lower():
    print("Got freeleech page!")
    with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_freeleech_authed.html", "w", encoding="utf-8") as f:
        f.write(r.text)
else:
    print(f"Not authenticated for freeleech page, URL: {r.url}")

# Test 3: RSS
print("\n=== Test: RSS feed ===")
r = session.get(f"{base}/torrents/rss.php", allow_redirects=True)
print(f"Status: {r.status_code}, Length: {len(r.text)}, Type: {r.headers.get('content-type', 'unknown')}")
if r.text.startswith("<?xml") or "<rss" in r.text[:500]:
    print("Got RSS feed!")
    with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_rss.xml", "w", encoding="utf-8") as f:
        f.write(r.text)
    # Count items
    items = re.findall(r'<item>', r.text, re.I)
    print(f"RSS items: {len(items)}")
else:
    print(f"Not an RSS feed. First 300 chars: {r.text[:300]}")

# Test 4: Try JSON/API endpoints
print("\n=== Test: API endpoints ===")
for ep in ["/torrents/api.php", "/api.php"]:
    r = session.get(f"{base}{ep}", allow_redirects=True)
    print(f"  {ep} -> {r.status_code} ({r.headers.get('content-type', '?')}) {len(r.text)} chars")

print("\nDone!")