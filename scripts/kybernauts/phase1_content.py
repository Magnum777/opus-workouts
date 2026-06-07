"""
Phase 1 Anti-Yagas Propaganda Content Generator
- Posts 1 vague Twitter/X post per day (automated)
- Generates Reddit + Forum drafts for manual posting
- Posts draft summaries to #kybernauts Discord for review
"""

import requests
import json
import random
import os
from datetime import datetime
from pathlib import Path

# Load API key from env file (not hardcoded)
CREDENTIALS_DIR = Path("credentials")
ENV_FILE = CREDENTIALS_DIR / "uploadpost.env"

def _load_env(path: Path):
    """Parse simple KEY=VALUE env file."""
    result = {}
    if path.exists():
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    result[k] = v
    return result

_env = _load_env(ENV_FILE)
API_KEY = _env.get("UPLOADPOST_API_KEY", "")
PROFILE = "EVEPropaganda"
API_BASE = "https://api.upload-post.com/api"

if not API_KEY:
    raise RuntimeError(f"UPLOADPOST_API_KEY not found in {ENV_FILE}. Check credentials/ directory.")

# Phase 1 Twitter pool — vague observation, no Yagas mention
PHASE1_TWEETS = [
    "Filaments bring 5-15 ships. Pochven was built for that. Wondering if the space is still serving its purpose. #EVEOnline #Pochven",
    "Anyone else notice bigger fleets in Pochven lately? Used to see 5v5s, now it's feeling more like nullsec. #EVEOnline #Pochven",
    "No local chat. Wormhole connections. Filament access. Pochven was an alternative to nullsec. Is it still? #EVEOnline #Pochven",
    "The proving grounds were meant for small-gang merit. Not sure that's what's happening out there anymore. #EVEOnline #Pochven",
    "Small gang PvPer here. Used to filament into Pochven for 5v5s and 10v10s. Lately it feels different. Anyone else? #EVEOnline #Pochven",
    "Pochven design philosophy: no local, filaments, wormholes = small-gang paradise. Current reality: TBD. #EVEOnline #Pochven",
    "Heard there's bigger groups holding space in Pochven now. As someone who likes small gangs, should I even bother filamenting in? #EVEOnline #Pochven",
    "Remember when Pochven was the place for small-gang roams? When did that change? #EVEOnline #Pochven",
    "CCP built Pochven with filaments for 5-15 ships, no local, wormhole connections. Great design. Hope it's still working as intended. #EVEOnline #Pochven",
    "Filament into Pochven with 10 friends. Find 30+ waiting. Is this the new normal? #EVEOnline #Pochven",
]

# Phase 1 Reddit drafts — neutral questions, community-building
PHASE1_REDDIT = [
    {
        "title": "What's the current state of Pochven PvP?",
        "body": "Haven't filamented in for a while. Used to find 5v5s and 10v10s. What's the vibe these days? Heard there's bigger groups holding space now. Still worth it for small gangs?",
        "flair": "Discussion"
    },
    {
        "title": "Pochven: still worth it for small gangs?",
        "body": "Thinking of taking a small gang into Pochven. But I've heard it's changed — bigger fleets, structure camps, less roaming. Is that accurate or just bad luck? Anyone filamenting in regularly?",
        "flair": "Discussion"
    },
    {
        "title": "Has Pochven shifted away from small-gang PvP?",
        "body": "Genuine question. When Pochven launched, the whole pitch was filaments for 5-15 ships, no local chat, wormhole connections. Small-gang heaven. Lately I'm hearing it's more like nullsec-lite. Is that the experience for people who actually go there?",
        "flair": "Discussion"
    },
    {
        "title": "Small gang PvPers: where are you finding content lately?",
        "body": "Used to filament into Pochven with 5-10 friends and find good fights. Lately it feels like bigger groups have moved in and the space isn't what it was. Where are you finding 5v5s and 10v10s these days? Or is that just dead everywhere now?",
        "flair": "Discussion"
    },
]

# Phase 1 Forum drafts — RP observation, no corp named
PHASE1_FORUMS = [
    {
        "title": "Observation from the Filament Fields",
        "body": """We speak as those who traverse the filament paths into Pochven.

Lately, the Proving Grounds feel different. Where once a gang of five or ten might find worthy adversaries and be tested, the skies now seem to hold larger formations. Greater numbers. Swarms where squads once roamed.

We do not speak against any Clade or collective. We merely observe: the character of the Proving Grounds appears to be shifting.

The Convocation watches. The Flow shifts.

Something is different in the Domain of Pochven.

— Transmitted on behalf of interested observers"""
    },
    {
        "title": "On the Changing Winds of Pochven",
        "body": """Hear our observation and consider it.

The Domain of Pochven was established as a space apart from the great nullsec wars. Filaments teleport small fleets. No local chat reveals all. Wormhole connections prevent predictable camping. The design spoke of small-group merit.

Yet those who filament in of late report encountering forces of greater number than the design intended. Not the 5v5 or 10v10 of proving, but formations more suited to territorial warfare.

We ask not for condemnation. We ask for observation.

Has Pochven remained true to its design, or has the logic of the outer regions found purchase within?

— Voice of the Filament Wanderers"""
    },
    {
        "title": "Question for the Clades: On Fleet Sizes in the Proving Grounds",
        "body": """We come seeking wisdom.

The filament system was designed to teleport 5-15 vessels. The wormhole connections were designed to prevent predictable routes. The absence of local chat was designed to encourage scanning, awareness, and small-group tactics.

Those of us who still filament into Pochven have noticed larger fleet presences than these systems were built to accommodate. Not hostile observations — merely factual ones.

What do the Clades make of this? Is Pochven still a proving ground for small gangs, or has it become something else?

— Curious Kybernaut"""
    },
]

STATE_FILE = Path("data/kybernauts/phase1_state.json")

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"tweets_posted": [], "reddit_used": [], "forums_used": [], "day": 0}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def post_twitter(text):
    url = f"{API_BASE}/upload_text"
    headers = {"Authorization": f"Apikey {API_KEY}"}
    data = {
        "user": PROFILE,
        "platform[]": "x",
        "title": text,
    }
    try:
        r = requests.post(url, headers=headers, data=data, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def pick_next_tweet(state):
    available = [t for t in PHASE1_TWEETS if t not in state["tweets_posted"]]
    if not available:
        # Reset if all used
        state["tweets_posted"] = []
        available = PHASE1_TWEETS[:]
    tweet = random.choice(available)
    state["tweets_posted"].append(tweet)
    return tweet

def pick_next_reddit(state):
    available = [r for i, r in enumerate(PHASE1_REDDIT) if i not in state["reddit_used"]]
    if not available:
        state["reddit_used"] = []
        available = PHASE1_REDDIT[:]
    draft = random.choice(available)
    idx = PHASE1_REDDIT.index(draft)
    state["reddit_used"].append(idx)
    return draft

def pick_next_forum(state):
    available = [f for i, f in enumerate(PHASE1_FORUMS) if i not in state["forums_used"]]
    if not available:
        state["forums_used"] = []
        available = PHASE1_FORUMS[:]
    draft = random.choice(available)
    idx = PHASE1_FORUMS.index(draft)
    state["forums_used"].append(idx)
    return draft

if __name__ == "__main__":
    state = load_state()
    state["day"] += 1

    # 1. Pick and post tweet
    tweet = pick_next_tweet(state)
    print(f"=== DAY {state['day']} — TWITTER ===")
    print(f"Posting: {tweet}")
    result = post_twitter(tweet)
    print(json.dumps(result, indent=2))

    # 2. Generate Reddit draft (manual — just print it)
    reddit = pick_next_reddit(state)
    print(f"\n=== REDDIT DRAFT (manual — post to r/eve) ===")
    print(f"Flair: {reddit['flair']}")
    print(f"Title: {reddit['title']}")
    print(f"Body:\n{reddit['body']}\n")

    # 3. Generate Forum draft (manual — just print it)
    forum = pick_next_forum(state)
    print(f"=== FORUM DRAFT (manual — post to Intergalactic Summit) ===")
    print(f"Title: {forum['title']}")
    print(f"Body:\n{forum['body']}\n")

    save_state(state)

    # Summary for Discord
    print(f"\n=== PHASE 1 DAY {state['day']} SUMMARY ===")
    print("Twitter: Posted (auto)")
    print("Reddit: Draft ready (manual)")
    print("Forums: Draft ready (manual)")
    print("Phase: 1 (vague observation)")
    print("Approach: No Yagas mention. Neutral tone. Build credibility.")
