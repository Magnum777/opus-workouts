"""TorrentDay profile scraper - get accurate ratio/stats"""
import requests
import re
import json

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

# Pull profile page
r = session.get(f"{base}/u/{cookies['uid']}", allow_redirects=True)
print(f"Profile page: {r.status_code} {len(r.text)} chars")

# Save for analysis
with open(r"C:\Users\compj\.openclaw\workspace\scripts\td_profile_v2.html", "w", encoding="utf-8") as f:
    f.write(r.text)

# Look for stat blocks - search broadly
# Try to find patterns like "Ratio: 1.797" or "Uploaded: X TB" etc
print("\n=== Searching for stats patterns ===")

# Find all number-heavy blocks
blocks = re.findall(r'(?:ratio|upload|download|seed|leech|bonus|freeleech)[^<]{0,200}', r.text, re.I)
for b in blocks[:30]:
    clean = b.strip().replace('\n', ' ').replace('\r', '')[:150]
    print(f"  {clean}")

# Find specific stat divs/spans
# Look for class="stat" or similar
stat_divs = re.findall(r'<[^>]*(?:stat|ratio|info|detail)[^>]*>([^<]+)', r.text, re.I)
print(f"\nStat divs ({len(stat_divs)}):")
for s in stat_divs[:20]:
    print(f"  {s.strip()[:100]}")

# Find table cells with numbers
td_content = re.findall(r'<td[^>]*>([^<]+)</td>', r.text)
print(f"\nTable cells ({len(td_content)}):")
for cell in td_content[:40]:
    cell = cell.strip()
    if cell and len(cell) < 100:
        print(f"  {cell}")

# Look for ratio specifically
print("\n=== Ratio search ===")
# Common patterns: "Ratio" followed by a number
ratio_patterns = re.findall(r'Ratio[^>]*>([^<]+)', r.text, re.I)
print(f"Ratio patterns: {ratio_patterns}")

# Find all numbers near "ratio"
ratio_context = re.findall(r'ratio.{0,50}([\d.]+)', r.text, re.I)
print(f"Ratio numbers: {ratio_context}")

# Find all numbers near "upload"
upload_context = re.findall(r'upload.{0,50}([\d.]+\s*[TGMK]?B)', r.text, re.I)
print(f"Upload numbers: {upload_context}")

# Find all numbers near "download"  
dl_context = re.findall(r'download.{0,50}([\d.]+\s*[TGMK]?B)', r.text, re.I)
print(f"Download numbers: {dl_context}")

# Find "Seed" and nearby numbers
seed_context = re.findall(r'Seed[^<]{0,100}', r.text, re.I)
print(f"\nSeed contexts:")
for s in seed_context[:10]:
    print(f"  {s.strip()[:120]}")

print("\nDone")