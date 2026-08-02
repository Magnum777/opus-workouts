"""TorrentDay - pull RSS feed and explore freeleech/hot torrents"""
import requests
import re
import json
import os
from html.parser import HTMLParser

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

# 1. Pull RSS feed
print("=== RSS Feed ===")
r = session.get(f"{base}/rss.php", allow_redirects=True)
print(f"Status: {r.status_code}, Length: {len(r.text)}, Type: {r.headers.get('content-type', '?')}")

# Check if it's actually RSS/XML
if r.text.strip().startswith("<?xml") or "<rss" in r.text[:500]:
    print("GOT RSS XML!")
    with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_rss.xml", "w", encoding="utf-8") as f:
        f.write(r.text)
    
    # Parse RSS
    items = re.findall(r'<item>(.*?)</item>', r.text, re.DOTALL)
    print(f"RSS items: {len(items)}")
    
    # Extract first few items
    for i, item in enumerate(items[:5]):
        title = re.search(r'<title>(.*?)</title>', item, re.I)
        link = re.search(r'<link>(.*?)</link>', item, re.I)
        desc = re.search(r'<description>(.*?)</description>', item, re.I)
        print(f"\n  [{i+1}] {title.group(1) if title else 'N/A'}")
        print(f"      Link: {link.group(1) if link else 'N/A'}")
        desc_text = desc.group(1) if desc else 'N/A'
        if len(desc_text) > 200:
            desc_text = desc_text[:200] + "..."
        print(f"      Desc: {desc_text}")
else:
    print(f"Not RSS. First 300 chars: {r.text[:300]}")

# 2. Pull the main browse page and extract torrent data
print("\n\n=== Main Browse Page ===")
r = session.get(f"{base}/t", allow_redirects=True)
print(f"Status: {r.status_code}, Length: {len(r.text)}")

with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_browse_full.html", "w", encoding="utf-8") as f:
    f.write(r.text)

# Extract torrent entries from the browse page
# Look for the torrent table structure
# TorrentDay uses /t/ID and /details.php?id=ID links

# Find all torrent links with IDs
torrent_ids = re.findall(r'/t/(\d+)', r.text)
torrent_ids = list(dict.fromkeys(torrent_ids))  # dedupe preserving order
print(f"Unique torrent IDs on front page: {len(torrent_ids)}")

# Find download links
dl_links = re.findall(r'/download\.php[^"\']*', r.text)
print(f"Download links: {len(dl_links)}")
for link in dl_links[:5]:
    print(f"  {link}")

# Find freeleech indicators
free_sections = re.findall(r'free[^<]{0,50}', r.text, re.I)
print(f"\nFreeleech mentions: {len(free_sections)}")
for s in free_sections[:10]:
    print(f"  {s.strip()[:80]}")

# Find category links
cats = re.findall(r'\?(\d+)#torrents[^>]*>([^<]+)', r.text)
unique_cats = list(dict.fromkeys(cats))
print(f"\nCategories ({len(unique_cats)}):")
for cid, cname in unique_cats[:30]:
    print(f"  cat={cid}: {cname.strip()}")

# 3. Try freeleech-specific URLs
print("\n\n=== Freeleech Browse ===")
for url in [
    f"{base}/t?freeleech=1",
    f"{base}/t?25&freeleech=1",  # Movies/480p + freeleech
    f"{base}/t?free=1",
    f"{base}/freeleech",
]:
    try:
        r = session.get(url, allow_redirects=True, timeout=10)
        is_different = len(r.text) != 113098  # Different from main page
        print(f"  {url.replace(base, '')} -> {r.status_code} {len(r.text)} chars different={is_different}")
        if is_different and len(r.text) > 5000:
            # Save first different page
            if 'freeleech' in url:
                with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_freeleech_page.html", "w", encoding="utf-8") as f:
                    f.write(r.text)
                print(f"    Saved freeleech page!")
    except Exception as e:
        print(f"  Error: {str(e)[:80]}")

# 4. Look at a specific torrent detail page
print("\n\n=== Torrent Detail Page ===")
if torrent_ids:
    test_id = torrent_ids[0]
    r = session.get(f"{base}/details.php?id={test_id}", allow_redirects=True)
    print(f"Detail page for torrent {test_id}: {r.status_code} {len(r.text)} chars")
    
    # Find download link on detail page
    dl_match = re.search(r'/download\.php[^"\']*', r.text)
    if dl_match:
        print(f"Download link: {dl_match.group(0)}")
    
    # Find seeders/leechers
    seed_match = re.search(r'Seeders?[^\d]*(\d+)', r.text, re.I)
    leech_match = re.search(r'Leechers?[^\d]*(\d+)', r.text, re.I)
    if seed_match:
        print(f"Seeders: {seed_match.group(1)}")
    if leech_match:
        print(f"Leechers: {leech_match.group(1)}")
    
    # Find size
    size_match = re.search(r'(?i)size[^\d]*([\d.]+\s*[GMK]B)', r.text)
    if size_match:
        print(f"Size: {size_match.group(1)}")

print("\nDone!")