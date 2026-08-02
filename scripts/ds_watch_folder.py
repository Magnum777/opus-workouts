"""Set up DS watch folder: copy .torrent files to NAS video share via SMB,
then DS will auto-pick them up from there."""
import requests, urllib3, json, os, subprocess
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

# Step 1: Map SMB drive
print("=== Setting up SMB connection ===")
subprocess.run(["net", "use", r"\\MND\video", "/delete", "/y"],
               capture_output=True, timeout=10)
result = subprocess.run(
    ["net", "use", r"\\MND\video", "/user:Nova", nas["password"], "/persistent:no"],
    capture_output=True, text=True, timeout=15
)
print("net use video: {}".format(result.stdout.strip() + result.stderr.strip()))

# Step 2: Create a watch folder on the NAS
print("\n=== Creating watch folder ===")
result = subprocess.run(
    ["cmd", "/c", "mkdir", r"\\MND\video\watch"],
    capture_output=True, text=True, timeout=10
)
# mkdir returns error if dir exists, that's fine
print("mkdir watch: {}".format(result.stderr.strip() if result.stderr else "OK"))

# Verify it exists
result = subprocess.run(
    ["cmd", "/c", "dir", r"\\MND\video\watch"],
    capture_output=True, text=True, timeout=10
)
print("watch dir exists: {}".format("watch" in result.stdout.lower() if result.stdout else "checking..."))

# Step 3: Download .torrent files for top freeleech picks
print("\n=== Downloading .torrent files ===")
local_temp = r"C:\Users\compj\.openclaw\workspace\scripts\temp_torrents"
os.makedirs(local_temp, exist_ok=True)

# These are the top 5 freeleech torrents we want to add
torrents = [
    ("10042121", "Rick.and.Morty.S09E09"),  # Test torrent from earlier scan
]

# Let's scan freeleech again to get current top picks
session_td = requests.Session()
cookies = {"uid": td["uid"], "pass": td["pass_cookie"]}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Scan freeleech page
from bs4 import BeautifulSoup
r = session_td.get("https://www.torrentday.com/t?free=1", cookies=cookies, headers=headers, timeout=30)
soup = BeautifulSoup(r.text, "html.parser")

# Find torrent links
torrent_links = []
for row in soup.select("tr.browse-row"):
    title_elem = row.select_one("a.title, a[href*='details']")
    dl_elem = row.select_one("a[href*='download.php']")
    if dl_elem:
        href = dl_elem.get("href", "")
        title = title_elem.text.strip() if title_elem else dl_elem.text.strip()
        # Extract torrent ID from download link
        import re
        m = re.search(r'download\.php/(\d+)', href)
        if m:
            tid = m.group(1)
            torrent_links.append((tid, title[:80]))

print("Found {} freeleech torrents".format(len(torrent_links)))

# Download top 5
added = 0
for tid, title in torrent_links[:5]:
    dl_url = "https://www.torrentday.com/download.php/{}/{}.torrent".format(tid, tid)
    try:
        r = session_td.get(dl_url, cookies=cookies, headers=headers, timeout=30)
        if r.status_code == 200 and r.content.startswith(b'd8:'):
            # Save locally
            safe_title = "".join(c for c in title if c.isalnum() or c in ".-_ ")[:60]
            local_file = os.path.join(local_temp, "{}.torrent".format(safe_title))
            with open(local_file, "wb") as f:
                f.write(r.content)
            
            # Copy to NAS watch folder
            result = subprocess.run(
                ["cmd", "/c", "copy", "/Y", local_file, r"\\MND\video\watch\\"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                print("  Added: {} ({} bytes)".format(safe_title, len(r.content)))
                added += 1
            else:
                print("  Copy failed for {}: {}".format(safe_title, result.stderr.strip()[:100]))
        else:
            print("  Download failed for {}: HTTP {} ({} bytes)".format(title[:40], r.status_code, len(r.content)))
    except Exception as e:
        print("  Error: {}".format(str(e)[:100]))

print("\nCopied {} .torrent files to watch folder".format(added))

# Step 4: Check if DS has a watch folder feature we can enable
print("\n=== Checking DS watch/auto-add settings ===")
session = requests.Session()
session.verify = False
r = session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "login",
    "account": nas["user"], "passwd": nas["password"], "format": "sid"
})
sid = r.json()["data"]["sid"]

base_ds = "https://{}:5001/webapi/DownloadStation/task.cgi".format(nas["hostname"])

# Check DS config for watch/BT folder settings
r = session.get(base_ds, params={
    "api": "SYNO.DownloadStation.Info", "version": "1", "method": "getconfig", "_sid": sid
})
print("DS config: {}".format(json.dumps(r.json(), indent=2)))

# Also check DSM Task Scheduler for auto-add
base = "https://{}:5001/webapi/entry.cgi".format(nas["hostname"])
r = session.get(base, params={
    "api": "SYNO.Core.TaskScheduler", "version": "1", "method": "list", "_sid": sid
})
print("Task scheduler: {}".format(json.dumps(r.json(), indent=2)[:500]))

session.get("https://{}:5001/webapi/auth.cgi".format(nas["hostname"]), params={
    "api": "SYNO.API.Auth", "version": "6", "method": "logout", "_sid": sid
})