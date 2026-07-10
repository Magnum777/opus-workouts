#!/usr/bin/env python3
"""
EVE Onion - Daily Reddit Tweet Pipeline
Uses Pushshift/alternative discovery to surface EVE drama, writes staging file
for the cron agent to generate and post the tweet.

Pushshift is the free Reddit data mirror. Falls back to web search.
"""
import requests
import re
import json
from pathlib import Path
from datetime import datetime

SUBREDDITS = ["Eve", "evecirclejerk", "EveOnline"]
CREDS_FILE   = Path("C:/Users/compj/.openclaw/workspace/credentials/uploadpost.env")
HISTORY_FILE = Path("C:/Users/compj/.openclaw/workspace/eveonion/tweet_history.json")
STATE_FILE   = Path("C:/Users/compj/.openclaw/workspace/eveonion/reddit_pipeline_state.json")
OUTPUT_DIR   = Path("C:/Users/compj/.openclaw/workspace/eveonion/drafts")
LOG_FILE     = Path("C:/Users/compj/.openclaw/workspace/eveonion/reddit_pipeline.log")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"tweeted_ids": [], "last_run": None}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2, encoding="utf-8"))

KEYWORDS_BAD = [
    "mod post", "meta", "patch notes", "sticky", "announcement",
    "reddit api", "boycott", "blackout", "new player", "just started",
    "help me", "how do i", "is it worth", "returning player",
    "megathread", "server status", "downtime", "day 1", "day one",
]

KEYWORDS_GOOD = [
    "war", "scam", "gank", "kill", "blap", "exploded",
    "got blown up", "lost my", "betrayal", "spies", "disconnect",
    "alliance", "coalition", "fleet fight", "battle", "sotiyo",
    "titans lost", "super", "rorqual", "dreadnought", "carrier",
    "hell camp", "entosis", "wardec", "exploit", "bug",
    "Pochven", "triglavian", "abyssal", "faction warfare",
    "FW", "POS", "starbase", "sov", "creep", "j4lp", "code",
    "blob", "PPT", "PLEX", "skill injector", "ISK farmer", "RMT",
    "founder", "CEO", "alliance disbanded", "bank run",
]

def is_good_post(title):
    title_lower = title.lower()
    if any(kw.lower() in title_lower for kw in KEYWORDS_BAD):
        return False
    has_good = any(kw.lower() in title_lower for kw in KEYWORDS_GOOD)
    return has_good

def score_post(title):
    s = 0
    drama_kws = ["war", "scam", "betrayal", "gank", "blap", "exploded", "lost", "kicked", "banned", "exploit", "titans", "super", "flee"]
    for kw in drama_kws:
        if kw.lower() in title.lower():
            s += 30
    return s

# Try Pushshift (free Reddit data mirror)
def fetch_pushshift(subreddit, limit=10):
    url = f"https://api.pushshift.io/reddit/search/submission/?subreddit={subreddit}&sort=score&sort_type=desc&size={limit}&score=>5"
    headers = {"User-Agent": "EVEOnionBot/1.0"}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json().get("data", [])
    except Exception as e:
        log(f"[WARN] Pushshift failed for r/{subreddit}: {e}")
    return []

def extract_post(d):
    return {
        "title": d.get("title", ""),
        "url": d.get("full_link") or f"https://reddit.com{d.get('permalink', '')}",
        "score": d.get("score", 0),
        "num_comments": d.get("num_comments", 0),
        "subreddit": d.get("subreddit", ""),
        "selftext": d.get("selftext", "")[:500],
        "author": d.get("author", ""),
        "id": d.get("id", ""),
        "created_utc": d.get("created_utc", 0),
    }

def build_tweet_prompt(post):
    return f"""You are the EVE Onion, a satirical EVE Online news account that covers the game's most absurd, dramatic, and hilarious moments with fictional "journalism."

Convert this EVE Online post into a satirical EVE Onion tweet. Requirements:
- Tone: Deadpan mock-journalism, Onion-style (never ironic emojis, never "LOL")
- Output: A single tweet, 200-270 characters max
- Structure: Treat the real drama as if it's a genuine news story. Give it a serious headline-style opening.
- Reference the real situation but frame it as official/unexpected news
- Include the original Reddit post URL as your source
- NO em dashes. Use commas or semicolons instead.
- Keep it believable as fake news to someone who doesn't know EVE
- Do NOT use: delve, landscape, significance, testament, robust, comprehensive, facilitate, leverage

ORIGINAL POST:
Title: {post['title']}
Score: {post['score']} | Comments: {post['num_comments']} | r/{post['subreddit']}
Context: {post['selftext'] or '(no body text)'}

Write ONLY the tweet text, nothing else."""

def main():
    log("=== Starting EVE Onion Reddit Pipeline ===")
    state = load_state()

    # Try Pushshift first
    all_posts = []
    for sub in SUBREDDITS:
        posts = fetch_pushshift(sub, limit=15)
        log(f"Pushshift fetched {len(posts)} posts from r/{sub}")
        all_posts.extend([extract_post(p) for p in posts])

    if not all_posts:
        log("[ERROR] Pushshift returned nothing. Exiting.")
        # Write a marker so the agent knows to fall back to web search
        staging_file = OUTPUT_DIR / "_pending_tweet.json"
        staging_file.write_text(json.dumps({"fallback": True, "reason": "pushshift_empty"}, indent=2))
        print("[FALLBACK] web_search")
        exit(0)

    # Filter
    good_posts = [p for p in all_posts if is_good_post(p["title"])]
    if not good_posts:
        good_posts = sorted(all_posts, key=lambda p: score_post(p["title"]), reverse=True)[:5]
        log("[WARN] Using top 5 by drama score")

    good_posts.sort(key=lambda p: p["score"] + score_post(p["title"]), reverse=True)

    # Skip already-tweeted
    for p in good_posts:
        if p["id"] not in state.get("tweeted_ids", []):
            post = p
            break
    else:
        log("[INFO] All good posts already tweeted.")
        exit(0)

    log(f"Selected: {post['title'][:80]} | score={post['score']}")

    prompt = build_tweet_prompt(post)
    staging = {"post": post, "prompt": prompt, "source": "reddit"}
    staging_file = OUTPUT_DIR / "_pending_tweet.json"
    staging_file.write_text(json.dumps(staging, indent=2, encoding="utf-8"))

    print(f"[POST_ID] {post['id']}")
    print(f"[POST_TITLE] {post['title']}")
    print(f"[POST_URL] {post['url']}")
    print(f"[STAGING_FILE] {staging_file}")
    print(f"[PROMPT]\n{prompt}")

if __name__ == "__main__":
    main()
