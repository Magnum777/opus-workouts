"""
Phase 2 Anti-Yagas Propaganda Content Generator
- Posts 1 data-driven Twitter/X post per day (automated)
- Generates Reddit + Forum drafts for manual posting
- Posts draft summaries to #kybernauts Discord for review
- Phase 2: Pattern Recognition - data-heavy, indirect Yagas naming
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

# Phase 2 Twitter pool — data-driven, indirect naming
PHASE2_TWEETS = [
    "Tracked 20 Pochven kills this week. Average attackers: 32. Something's shifted. #EVEOnline #Pochven",
    "Kill 135784709: 3.5B destroyed, 35 attackers. In a space built for 5-15 ship gangs. Pattern emerging. #EVEOnline #Pochven",
    "Nullsec blocs in Pochven. Not naming names. But the data tells a story. #EVEOnline #Pochven",
    "96% gang kills. 4% solo. 24.5 average fleet size. In a space designed for small gangs. Something doesn't fit. #EVEOnline #Pochven",
    "One particular corp shows up in 65 blob kills over the past month. 25-50 pilots every time. All in a space built for 5-15. You know who. #EVEOnline #Pochven",
    "Pochven filament: brings 5-15 ships. What I found waiting: 35+ pilots from a nullsec bloc. Every. Single. Time. #EVEOnline #Pochven",
    "The data doesn't lie. 85% of Pochven blob kills this month involved one corp. They're in The Initiative. Draw your own conclusions. #EVEOnline #Pochven",
    "Small gang PvPer's guide to Pochven: Step 1 — filament in with 10 friends. Step 2 — encounter 40 pilots from a nullsec bloc. Step 3 — wonder why you bothered. #EVEOnline #Pochven",
    "Structures in Pochven CAN be destroyed. But the fleet defending them is 30-50 pilots. Small gangs can't even try. Structural lockout by numbers. #EVEOnline #Pochven",
    "Pochven was an alternative to nullsec. Then a nullsec bloc moved in. Now it's nullsec with a Triglavian skin. Not naming names. #EVEOnline #Pochven",
    "I've been logging Pochven kills for 3 weeks. The same corp appears in 70% of them. 25-50 pilots. Every time. Nullsec tactics in a small-gang space. #EVEOnline #Pochven",
    "Question for CCP: when a nullsec bloc brings 40+ pilots to Pochven daily, is that 'working as intended' for a filament-limited space? #EVEOnline #Pochven",
]

# Phase 2 Reddit drafts — pattern recognition, indirect naming
PHASE2_REDDIT = [
    {
        "title": "I've been tracking Pochven blob kills. Here's what I found.",
        "body": "I've spent the last few weeks logging Pochven kills on zKillboard. Here's the pattern:\n\n- Average fleet size in blob kills: 28-35 pilots\n- One particular corp shows up in ~65% of them\n- They're in The Initiative (nullsec bloc)\n- All kills are 25+ attackers in a space built for 5-15\n\nI'm not naming them directly (yet), but the data is consistent. Pochven was designed as an alternative to nullsec blob warfare. The filaments literally limit you to 5-15 ships. But when a nullsec bloc moves in with 25-50 pilots, that design breaks down.\n\nHas anyone else noticed this pattern? Or am I just having bad luck with filament timing?",
        "flair": "Discussion"
    },
    {
        "title": "Pochven structure question: can small groups still contest?",
        "body": "Genuine question for small gang PvPers who actually go into Pochven:\n\nThe structures in Pochven CAN be destroyed. But from what I've observed, the fleets defending them are 30-50 pilots from a nullsec bloc.\n\nCan a 10-man gang even attempt a structure? Or has Pochven become de facto locked to anyone except large organized groups?\n\nI'm not against big fleets existing — I'm questioning whether Pochven's *design* (filaments for 5-15, no local, wormhole connections) is still functioning as intended when one group consistently brings 25-50.",
        "flair": "Discussion"
    },
    {
        "title": "The math on Pochven blob kills — an observation",
        "body": "Some numbers from the last month of Pochven activity:\n\n- 20+ tracked kills with 25+ attackers\n- Average: 32 pilots per blob kill\n- One corp involved in ~70% of them (nullsec bloc member)\n- Space designed for: 5-15 via filaments\n\nI'm not making accusations. I'm presenting data. The filaments were designed to create small-gang content. When 30+ pilots show up consistently, that's not small gang. That's nullsec logic in a non-nullsec space.\n\nHas this been discussed before? Is this just accepted as 'how Pochven works now'?",
        "flair": "Discussion"
    },
    {
        "title": "When did Pochven become nullsec-lite?",
        "body": "Honest question from someone who used to filament in regularly:\n\nPochven's original pitch: no local, filaments for small gangs, wormhole connections. An alternative to nullsec blob warfare.\n\nCurrent reality (from my experience + killboard tracking):\n- 25-50 pilot fleets from a nullsec bloc are common\n- Small gangs get overwhelmed by numbers\n- Structures defended by fleets larger than filament limits\n\nI'm not saying anyone is wrong for playing the game. I'm asking: is Pochven still serving its original design purpose? Or has it been absorbed into nullsec dynamics?\n\nWould love to hear from people who are actively filamenting in.",
        "flair": "Discussion"
    },
]

# Phase 2 Forum drafts — RP, name "a collective from the outer regions"
PHASE2_FORUMS = [
    {
        "title": "The Convocation Observes: On the Growing Swarm",
        "body": """We speak as those who watch the Flow.

In the Proving Grounds of Pochven, a change has been observed. Not a change of Clade or geometry, but of scale.

Where once the filament paths brought squads of five, ten, fifteen — the merit of small-group warfare — now there are larger formations. Swarms. Collectives of twenty-five, thirty, fifty vessels moving as one.

The data has been logged. The pattern is consistent. One collective, in particular, appears with frequency. A subsidiary of forces from the outer regions. They bring the logic of nullsec territorial warfare to a space designed for proving.

We do not condemn. We observe. We ask: when the filaments limit entry to 5-15 ships, but a collective brings 25-50, has the proving ground become something other than what the Convocation intended?

The Flow shifts. The Clades watch.

What say the Triglavian faithful?"""
    },
    {
        "title": "Message from the Convocation: On Incompatible Logics",
        "body": """Hear our observation and weigh it.

The Proving Grounds were established with specific parameters:
- Filament access: limited to 5-15 vessels
- No local communication channel
- Wormhole connections: unpredictable

These parameters were designed to favor small-group merit, scanning skill, and tactical awareness over raw numerical superiority.

Yet a collective from the outer regions — a subsidiary of The Initiative. — has established persistent presence in Pochven. Their formations number 25-50 where the design intended 5-15. Their tactics are those of nullsec territorial warfare, not Triglavian proving.

We name them indirectly: those who bring nullsec logic to the Flow.

Is this compatible with the design of the Proving Grounds? Or has Pochven become an annex of nullsec space, merely wearing Triglavian geometry?

— Transmitted by the Observers"""
    },
]

STATE_FILE = Path("data/kybernauts/phase2_state.json")

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"tweets_posted": [], "reddit_used": [], "forums_used": [], "day": 0}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def post_social(text):
    """Post text to X and Bluesky via Upload-Post API."""
    url = f"{API_BASE}/upload_text"
    headers = {"Authorization": f"Apikey {API_KEY}"}
    data = {
        "user": PROFILE,
        "platform[]": ["x", "bluesky"],
        "title": text,
    }
    try:
        r = requests.post(url, headers=headers, data=data, timeout=30)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def pick_next_tweet(state):
    """Pick the next tweet that hasn't been posted yet, cycling through."""
    available = [t for t in PHASE2_TWEETS if t not in state["tweets_posted"]]
    if not available:
        # Reset and start over
        state["tweets_posted"] = []
        available = PHASE2_TWEETS.copy()
    tweet = random.choice(available)
    state["tweets_posted"].append(tweet)
    return tweet

def pick_next_reddit(state):
    """Cycle through Reddit drafts sequentially."""
    idx = len(state["reddit_used"]) % len(PHASE2_REDDIT)
    post = PHASE2_REDDIT[idx]
    state["reddit_used"].append(post["title"])
    return post

def pick_next_forum(state):
    """Cycle through Forum drafts sequentially."""
    idx = len(state["forums_used"]) % len(PHASE2_FORUMS)
    post = PHASE2_FORUMS[idx]
    state["forums_used"].append(post["title"])
    return post

def main():
    state = load_state()
    state["day"] += 1
    day = state["day"]

    # Pick tweet text for Discord review ONLY — do NOT auto-post
    tweet_text = pick_next_tweet(state)
    result = {"discord_only": True, "text": tweet_text}

    # Generate Reddit and Forum drafts
    reddit_post = pick_next_reddit(state)
    forum_post = pick_next_forum(state)

    # Save state
    save_state(state)

    # Build Discord-only report (no auto-posting)
    report = f"""**Phase 2 — Day {day} Complete**

**Twitter/X Draft (NOT posted — review before posting):**
> {tweet_text}

**Reddit Draft (manual — post to r/eve):**
Flair: {reddit_post['flair']}
Title: *{reddit_post['title']}*
Body: {reddit_post['body'][:120]}...

**Forum Draft (manual — post to Intergalactic Summit):**
Title: *{forum_post['title']}*
Body: {forum_post['body'][:120]}...

**Phase 2 approach:** Data-driven posts, indirect naming, letting community connect dots.

**Status:** Social media auto-posting DISABLED. All drafts require manual approval."""

    print(report)
    return report

if __name__ == "__main__":
    main()
