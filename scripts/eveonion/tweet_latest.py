#!/usr/bin/env python3
"""Tweet the latest EveOnion article. Single line format: quote headline + article URL + #EVEOnline.

Skips articles that were already tweeted (tracked in tweet_history.json).
"""
import requests, re, json
from pathlib import Path

ARTICLES_DIR   = Path("C:/Users/compj/.openclaw/workspace/eveonion/articles")
CREDS_FILE     = Path("C:/Users/compj/.openclaw/workspace/credentials/uploadpost.env")
HISTORY_FILE   = Path("C:/Users/compj/.openclaw/workspace/eveonion/tweet_history.json")

# Load API key
api_key = None
with open(CREDS_FILE) as f:
    for line in f:
        line = line.strip()
        if line.startswith("UPLOADPOST_API_KEY="):
            api_key = line.split("=", 1)[1].strip()
            break
if not api_key:
    print("[ERROR] No API key")
    exit(1)

# Load tweet history
history = {}
if HISTORY_FILE.exists():
    try:
        history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        history = {}

# Latest article by modification time
articles = sorted(ARTICLES_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
if not articles:
    print("[ERROR] No articles")
    exit(1)

latest = articles[0]

# Check if already tweeted
if history.get("last_tweeted_file") == latest.name:
    print(f"[SKIP] Already tweeted: {latest.name}")
    print(f"[IDLE] No new articles since last tweet. Staying silent.")
    exit(0)

content = articles[0].read_text(encoding="utf-8")

# Headline from H1
hm = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
headline = hm.group(1).strip() if hm else ""
print(f"[FILE] {articles[0].name}")
print(f"[HEADLINE] {headline}")

# Source URL (only if actual http)
source_url = ""
sm = re.search(r"\*\*Source:\*\*\s*(.+)", content)
if sm and sm.group(1).strip().startswith("http"):
    source_url = sm.group(1).strip()
print(f"[SOURCE] {source_url}")

# Build WordPress slug from headline (full, no truncation)
def wp_slug(title):
    s = title.lower()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    s = s.strip('-')
    return s

slug = wp_slug(headline)
article_url = f"https://eveonion.com/{slug}/"
print(f"[ARTICLE] {article_url}")

# Build tweet - single line format for Twitter
# Format: "quoted headline" + article URL + #EVEOnline
tweet = f'"{headline}" {article_url} #EVEOnline'

print(f"[LENGTH] {len(tweet)}")

# Truncate headline if needed
if len(tweet) > 280:
    overhead = len(article_url) + 12
    max_head = 280 - overhead
    truncated = headline[:max_head]
    # Back up to last clean break
    for sep in ["; ", " - ", ", ", ": "]:
        cut = truncated.rfind(sep)
        if cut > max_head * 0.4:
            truncated = truncated[:cut]
            break
    truncated = truncated.rstrip(",;: ") + "..."
    tweet = f'"{truncated}" {article_url} #EVEOnline'
    print(f"[TRUNCATED] {len(tweet)}")

print(f"\n[TWEET]\n{tweet}\n")

# Post to X and Bluesky via upload-post (form-encoded)
url = "https://api.upload-post.com/api/upload_text"
data = {"user": "Eveonion", "platform[]": ["x", "bluesky"], "title": tweet}
r = requests.post(url, data=data, headers={"Authorization": f"Apikey {api_key}"})

if r.status_code == 200:
    resp = r.json()
    if resp.get("success"):
        x_url = resp.get("results", {}).get("x", {}).get("url") or f"https://x.com/EVEOnionNews/status/{resp['results']['x'].get('post_id', '?')}"
        bsky_url = resp.get("results", {}).get("bluesky", {}).get("url", "N/A")
        print(f"[OK - X] {x_url}")
        print(f"[OK - Bluesky] {bsky_url}")

        # Record this tweet so we don't repeat it
        history["last_tweeted_file"] = latest.name
        history["last_tweeted_at"] = latest.stat().st_mtime
        HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
    else:
        print(f"[FAIL] {resp}")
else:
    print(f"[ERROR] {r.status_code} {r.text[:200]}")
