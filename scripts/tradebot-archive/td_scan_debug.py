"""Download .torrent files directly and add them to DS using the working URL method,
but this time via a local HTTP server or by finding the correct volume path."""
import requests, urllib3, json, os, subprocess, re
urllib3.disable_warnings()

secrets_path = r"C:\Users\compj\.openclaw\workspace\.secrets"
nas = {}
td = {}
section = ""
with open(secrets_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("["):
            section = line.strip("[]")
            continue
        if "=" in line and section == "nas":
            k, v = line.split("=", 1)
            nas[k] = v
        if "=" in line and section == "torrentday":
            k, v = line.split("=", 1)
            td[k] = v

# The video share is on /volume1/video (confirmed earlier)
# DS needs torrents accessible from its own filesystem
# Strategy: download .torrent files, copy to NAS video/watch via SMB,
# then use DS API with a file:// URI pointing to the NAS internal path

# Step 1: Download .torrent files from TorrentDay
print("=== Downloading .torrent files from TorrentDay ===")
session_td = requests.Session()
cookies = {"uid": td["uid"], "pass": td["pass_cookie"]}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Test with known torrent IDs from our scan data
test_ids = ["10042121"]  # Rick and Morty from earlier test

# Also try scanning the freeleech page more carefully
print("Scanning TorrentDay freeleech page...")
r = session_td.get("https://www.torrentday.com/t?free=1", cookies=cookies, headers=headers, timeout=30)
print("Page size: {} bytes".format(len(r.text)))
print("Page starts with: {}".format(r.text[:200]))

# Save page for debugging
with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_freeleench.html", "w", encoding="utf-8") as f:
    f.write(r.text)
print("Saved page to td_freeleench.html")

# Parse more carefully - check the actual HTML structure
from bs4 import BeautifulSoup
soup = BeautifulSoup(r.text, "html.parser")

# Check what tables exist
tables = soup.find_all("table")
print("Found {} tables".format(len(tables)))

# Check for browse rows
rows = soup.find_all("tr", class_="browse-row")
print("Found {} browse-row elements".format(len(rows)))

# Check all links for download.php
dl_links = soup.find_all("a", href=re.compile(r"download\.php"))
print("Found {} download links".format(len(dl_links)))

# Check all links for torrent details
detail_links = soup.find_all("a", href=re.compile(r"details\.php"))
print("Found {} detail links".format(len(detail_links)))

# Try different row selectors
for selector in ["tr.browse-row", "tr[id]", "tr[class]", "tbody tr"]:
    rows = soup.select(selector)
    if rows:
        print("  Selector '{}': {} rows".format(selector, len(rows)))
        if len(rows) > 0:
            print("    First row HTML: {}".format(str(rows[0])[:300]))

# Check for any torrent-related content
torrent_rows = soup.find_all("tr", {"id": re.compile(r".*")})
print("Rows with id attr: {}".format(len(torrent_rows)))

# Check if the page is actually a Cloudflare challenge or login page
if "challenge" in r.text.lower() or "cf-" in r.text[:500].lower():
    print("WARNING: Page appears to be a Cloudflare challenge page")
elif "login" in r.text[:1000].lower():
    print("WARNING: Page appears to be a login page - cookies may have expired")

# Show first 2000 chars of the page body
body = soup.find("body")
if body:
    print("\nPage body preview (first 2000 chars):")
    print(body.get_text()[:2000])