"""Download top freeleech .torrents and drop them in \\MND\video\torrents\ for DS auto-add"""
import requests, urllib3, re, os, subprocess
from bs4 import BeautifulSoup
urllib3.disable_warnings()

SECRETS_PATH = r"C:\Users\compj\.openclaw\workspace\.secrets"
nas = {}
td = {}
section = ""
with open(SECRETS_PATH) as f:
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

# Ensure SMB connection
subprocess.run(["net", "use", r"\\MND\video", "/user:Nova", nas["password"], "/persistent:no"],
               capture_output=True, timeout=10)

# Scan TorrentDay freeleech
session_td = requests.Session()
cookies = {"uid": td["uid"], "pass": td["pass_cookie"]}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

print("Scanning TorrentDay freeleech...")
r = session_td.get("https://www.torrentday.com/t?free=1", cookies=cookies, headers=headers, timeout=30)
soup = BeautifulSoup(r.text, "html.parser")

# Find download links and torrent info
torrents = []
dl_links = soup.find_all("a", href=re.compile(r"download\.php"))
detail_links = soup.find_all("a", href=re.compile(r"/t/\d+"))

# Build a map of torrent IDs to titles from detail links
title_map = {}
for a in detail_links:
    m = re.search(r"/t/(\d+)", a.get("href", ""))
    if m:
        title_map[m.group(1)] = a.get_text(strip=True)

for a in dl_links:
    href = a.get("href", "")
    m = re.search(r"download\.php/(\d+)", href)
    if not m:
        continue
    tid = m.group(1)
    title = title_map.get(tid, a.get_text(strip=True))
    
    # Get parent row for seeders/leechers
    row = a.find_parent("tr")
    tds = row.find_all("td") if row else []
    seeders = 0
    leechers = 0
    if len(tds) >= 4:
        for td_elem in tds:
            text = td_elem.get_text(strip=True)
            # Seeders and leechers are usually in specific td positions
        # Try to find numbers in the row
        numbers = re.findall(r'\b(\d+)\b', row.get_text() if row else "")
    
    # Simple scoring: more detail links from the freeleech page = popular
    torrents.append({"id": tid, "title": title})

# Also scan movies freeleech
print("Scanning TorrentDay movies freeleech...")
r = session_td.get("https://www.torrentday.com/t?25&free=1", cookies=cookies, headers=headers, timeout=30)
soup2 = BeautifulSoup(r.text, "html.parser")
for a in soup2.find_all("a", href=re.compile(r"download\.php")):
    m = re.search(r"download\.php/(\d+)", a.get("href", ""))
    if m:
        tid = m.group(1)
        if tid not in [t["id"] for t in torrents]:
            title = title_map.get(tid, "Unknown")
            torrents.append({"id": tid, "title": title})

# Also scan TV freeleech
print("Scanning TorrentDay TV freeleech...")
r = session_td.get("https://www.torrentday.com/t?24&free=1", cookies=cookies, headers=headers, timeout=30)
soup3 = BeautifulSoup(r.text, "html.parser")
for a in soup3.find_all("a", href=re.compile(r"download\.php")):
    m = re.search(r"download\.php/(\d+)", a.get("href", ""))
    if m:
        tid = m.group(1)
        if tid not in [t["id"] for t in torrents]:
            title = title_map.get(tid, "Unknown")
            torrents.append({"id": tid, "title": title})

print("Found {} unique torrent IDs".format(len(torrents)))

# Download .torrent files and check their sizes
local_temp = r"C:\Users\compj\.openclaw\workspace\scripts\temp_torrents"
os.makedirs(local_temp, exist_ok=True)

# Clean existing files in watch folder
subprocess.run(["cmd", "/c", "del", r"\\MND\video\torrents\*.torrent", "/Q"],
               capture_output=True, timeout=10)

# Also remove our test watch folder
subprocess.run(["cmd", "/c", "rmdir", r"\\MND\video\watch"],
               capture_output=True, timeout=10)

added = 0
for t in torrents[:10]:  # Try top 10
    dl_url = "https://www.torrentday.com/download.php/{}/{}.torrent".format(t["id"], t["id"])
    try:
        r = session_td.get(dl_url, cookies=cookies, headers=headers, timeout=30)
        if r.status_code == 200 and r.content.startswith(b'd8:'):
            # Parse torrent to get size
            size_match = re.search(rb'lengthi(\d+)e', r.content[:200])
            size_bytes = int(size_match.group(1)) if size_match else 0
            size_gb = size_bytes / (1024**3) if size_bytes else 0
            
            # Skip huge torrents (>50GB)
            if size_gb > 50:
                print("  Skip: {} ({:.1f} GB)".format(t["title"][:50], size_gb))
                continue
            
            safe_title = "".join(c for c in t["title"] if c.isalnum() or c in ".-_ ")[:60]
            if not safe_title:
                safe_title = "td_{}".format(t["id"])
            
            local_file = os.path.join(local_temp, "{}.torrent".format(safe_title))
            with open(local_file, "wb") as f:
                f.write(r.content)
            
            # Copy to NAS watch folder
            result = subprocess.run(
                ["cmd", "/c", "copy", "/Y", local_file, r"\\MND\video\torrents\\"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                print("  Added: {} ({:.1f} GB, {} bytes)".format(safe_title[:50], size_gb, len(r.content)))
                added += 1
            else:
                print("  Copy failed: {} - {}".format(safe_title[:30], result.stderr.strip()[:100]))
        else:
            print("  Download failed: {} - HTTP {}".format(t["title"][:30], r.status_code))
    except Exception as e:
        print("  Error: {}".format(str(e)[:80]))

print("\nCopied {} .torrent files to \\MND\\video\\torrents\\".format(added))
print("DS should auto-add these from the watch folder.")

# Verify
result = subprocess.run(["cmd", "/c", "dir", r"\\MND\video\torrents"],
                       capture_output=True, text=True, timeout=10)
print("\nWatch folder contents:")
print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)