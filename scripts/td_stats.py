"""TorrentDay - pull user stats, ratio, and build the scanner/manager system"""
import requests
import re
import json
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

# 1. Pull user profile/stats
print("=== User Stats ===")
r = session.get(f"{base}/u/{cookies['uid']}", allow_redirects=True)
print(f"Profile page: {r.status_code} {len(r.text)} chars")

# Look for ratio, upload, download stats
ratio_matches = re.findall(r'(?i)ratio[^<]*?([\d.]+)', r.text)
upload_matches = re.findall(r'(?i)upload(?:ed)?[^<]*?([\d.]+\s*[TGMK]?B)', r.text)
download_matches = re.findall(r'(?i)download(?:ed)?[^<]*?([\d.]+\s*[TGMK]?B)', r.text)

print(f"Ratio mentions: {ratio_matches[:5]}")
print(f"Upload mentions: {upload_matches[:5]}")
print(f"Download mentions: {download_matches[:5]}")

# Look for stat blocks
stat_blocks = re.findall(r'(?i)(uploaded|downloaded|ratio|seed|leech|bonus)[^<]{0,100}([\d.]+\s*[TGMK]?B?|[\d.]+)', r.text)
for label, value in stat_blocks[:20]:
    print(f"  {label}: {value}")

# Save profile page for analysis
with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_profile.html", "w", encoding="utf-8") as f:
    f.write(r.text)

# 2. Check freeleech page structure more carefully
print("\n=== Freeleech Page ===")
r = session.get(f"{base}/t?free=1", allow_redirects=True)
with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_freeleech_full.html", "w", encoding="utf-8") as f:
    f.write(r.text)

# Find all torrent entries on freeleech page
# TorrentDay uses table rows with torrent data
# Pattern: /t/ID links with title text
torrent_entries = re.findall(r'/t/(\d+)[^>]*>([^<]+)', r.text)
print(f"Freeleech torrent entries: {len(torrent_entries)}")
for tid, title in torrent_entries[:10]:
    print(f"  [{tid}] {title.strip()[:80]}")

# Find download links on freeleech page
dl_links = re.findall(r'/download\.php/(\d+)/([^"]+)', r.text)
print(f"\nFreeleech download links: {len(dl_links)}")
for tid, fname in dl_links[:5]:
    print(f"  [{tid}] {fname[:80]}")

# 3. Pull freeleech + movies
print("\n=== Freeleech Movies ===")
r = session.get(f"{base}/t?25&free=1", allow_redirects=True)
movie_entries = re.findall(r'/t/(\d+)[^>]*>([^<]+)', r.text)
dl_links_movies = re.findall(r'/download\.php/(\d+)/([^"]+)', r.text)
print(f"Freeleech movies: {len(movie_entries)} entries, {len(dl_links_movies)} download links")

# 4. Parse a detail page to understand the full torrent data structure
print("\n=== Detail Page Structure ===")
r = session.get(f"{base}/t/10057847", allow_redirects=True)
detail = r.text

# Extract structured data from detail page
title = re.search(r'<title>([^<]+)', detail)
seeders = re.search(r'(?i)seeders?[^\d]*(\d+)', detail)
leechers = re.search(r'(?i)leechers?[^\d]*(\d+)', detail)
size = re.search(r'(?i)size[^\d]*([\d.]+\s*[TGMK]B)', detail)
freeleech = 'free' in detail.lower()[:5000] and 'leech' in detail.lower()[:5000]

print(f"Title: {title.group(1) if title else 'N/A'}")
print(f"Seeders: {seeders.group(1) if seeders else 'N/A'}")
print(f"Leechers: {leechers.group(1) if leechers else 'N/A'}")
print(f"Size: {size.group(1) if size else 'N/A'}")
print(f"Freeleech: {freeleech}")

# Find all stat-like patterns on detail page
stat_patterns = re.findall(r'(?i)(seeders?|leechers?|snatched|uploaded|downloaded|ratio|freeleech|bonus)[^<]{0,200}', detail)
for pattern in stat_patterns[:20]:
    clean = pattern.strip().replace('\n', ' ').replace('\r', '')[:120]
    print(f"  {clean}")

# 5. Download Station stats - current ratio summary
print("\n=== Download Station Current Summary ===")
nas_pass = ""
with open(secrets_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("password=") and section == "nas":
            nas_pass = line.split("=", 1)[1]
        if line.startswith("["):
            section = line.strip("[]")

# We'll use the DS2 API to get task stats
import urllib3
urllib3.disable_warnings()

from http.cookiejar import CookieJar
import json

# Login to DSM
login_url = f"https://MND:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=login&account=Nova&passwd={cookies.get('pass', '')[:0]}D0ngaYHRuthV93qD&format=sid"
# Actually use the proper NAS password from secrets
nas_creds = {}
section = ""
with open(secrets_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("["):
            section = line.strip("[]")
            continue
        if "=" in line and section == "nas":
            key, val = line.split("=", 1)
            nas_creds[key] = val

encoded_pass = urllib3.parse.quote(nas_creds.get("password", ""))
login_url = f"https://MND:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=login&account={nas_creds.get('user', 'Nova')}&passwd={encoded_pass}&format=sid"

import warnings
warnings.filterwarnings("ignore")

try:
    resp = requests.get(login_url, verify=False)
    login_data = resp.json()
    if login_data.get("success"):
        sid = login_data["data"]["sid"]
        print(f"DSM login OK")
        
        # Get task stats
        stats_url = f"https://MND:5001/webapi/entry.cgi?api=SYNO.DownloadStation2.Task.Statistic&version=1&method=get&_sid={sid}"
        resp = requests.get(stats_url, verify=False)
        stats = resp.json()
        if stats.get("success"):
            print(f"DS Stats: {json.dumps(stats.get('data', {}), indent=2)}")
        
        # Logout
        requests.get(f"https://MND:5001/webapi/auth.cgi?api=SYNO.API.Auth&version=6&method=logout&_sid={sid}", verify=False)
    else:
        print(f"DSM login failed: {login_data}")
except Exception as e:
    print(f"DSM error: {e}")

print("\nDone")