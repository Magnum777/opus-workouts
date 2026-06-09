"""
Anti-Baba Yagas Propaganda Poster (Multi-Platform)
Posts to r/eve AND Twitter/X via Upload-Post API (EVEPropaganda profile)

KEY INTEL UPDATE (2026-05-27):
- Baba Yagas controls Pochven structures. New ones can't be deployed.
- Structures CAN be destroyed, but Yagas defends with 400 pilots. Small gangs can't even attempt it.
- Yagas: 96% gang, 4% solo, 24.5 avg fleet size. 25-50 pilots per Pochven kill.
- Pochven was designed for 5-15 ship filaments, no local, wormhole connections = small-gang space.
- Yagas applies nullsec bloc logic to a space designed to be an alternative to nullsec.
- NOT cheating. Just the wrong game in the wrong arena.
- NO "INIT pets" framing (Opus directive)
- NO "landlord/rental empire" framing (Opus directive)
- ISEEU: 72% gang, 5.3 avg — normal corp stats. No hard multiboxing evidence found.
"""

import requests
import random
import json
import time
from pathlib import Path

API_KEY = "UPLOADPOST_API_KEY_REDACTED"
PROFILE = "EVEPropaganda"
API_BASE = "https://api.upload-post.com/api"

# Pick the newest data file
import glob
data_files = sorted(glob.glob("data/kybernauts/yagas_pochven_25plus_*.json"), reverse=True)
DATA_FILE = Path(data_files[0]) if data_files else Path("data/kybernauts/yagas_pochven_25plus_20260527_072729.json")
if DATA_FILE.exists():
    with open(DATA_FILE) as f:
        KILLS = json.load(f)
else:
    KILLS = []

SHIP_KILLS = [k for k in KILLS if not k.get("is_structure")]
SHIP_KILLS.sort(key=lambda x: x["value"], reverse=True)

# === REDDIT TEMPLATES (Nuanced, Evidence-Based) ===
REDDIT_TITLES = [
    "Baba Yagas is playing nullsec in Pochven. That's the problem.",
    "Pochven's identity crisis: small-gang design vs. nullsec reality",
    "Baba Yagas: 96% gang kills. Pochven: designed for 5-15 ship gangs. Discuss.",
    "Weekly Pochven Reality Check: What Yagas brought to small-gang space",
    "The Flow Demands Better: On Nullsec Logic in the Proving Grounds",
]

REDDIT_BODIES = {
    "blob_data": """Let's look at the facts.

Pochven was designed for small-gang PvP:
- Filament-based fleet access (5-15 ships)
- No local chat (wormhole-style)
- Multiple wormhole connections
- Standings-based entry limiting who can stay

Baba Yagas [YAGAS] — The Initiative.:
- 96% gang kills
- 4% solo
- 24.5 average fleet size
- 25-50 pilots per engagement

They're not doing anything against the rules. But they're playing a completely different game than what Pochven was built for.

Small-gang PvPers filament into Pochven looking for 5v5s, 10v10s, roaming fights. They find Baba Yagas with 400 pilots camping gates, holding structures, and dropping on anyone who enters.

It's not cheating. It's just nullsec bloc tactics in a space that was supposed to be an alternative to nullsec.

And because they control the structures — which CAN be destroyed, but only by an overwhelming force that no small gang can field — they've made Pochven into what they know: held territory defended by overwhelming numbers.

What do you think? Can a space designed for small-gang survive when nullsec blocs move in?""",

    "identity_crisis": """I want to talk about what Pochven was supposed to be vs. what it is.

**The Design:**
- Filaments let small fleets (5-15 ships) yeet into the region
- No local chat = you can't see who's there until they see you
- Wormhole connections = unpredictable routes, hard to camp
- The whole concept was "find content, fight, extract"

**The Reality (Baba Yagas edition):**
- 25-50 pilots on every kill
- 96% gang kills, 4% solo
- Structures held, territory controlled
- Gate camps with blob-sized fleets

Yagas is a nullsec bloc corp (The Initiative.). They know one way to play: hold space, bring numbers, defend what you have.

Pochven wasn't built for that. Pochven was built for people who want a 5v5 in the dark, not a 30v1 with a bloc behind it.

The structures CAN be removed — but only if you can bring overwhelming force. Small groups can't. So Pochven becomes just another nullsec region with a Triglavian skin.

Is this working as intended, or did CCP design something the nullsec meta just swallowed whole?""",

    "weekly_check": """This week in Pochven, Baba Yagas continued their campaign. Here's what that looks like:

Top kills:
{kill_list}

Every single one: 25-50 pilots. Total ISK destroyed: {total_isk}B.

Pochven was supposed to be where you take 5-15 friends, filament in, and find fights. Where you don't know who's in system until you scan them down. Where a small gang can actually matter.

Instead, if you filament in with 10 friends, you run into Baba Yagas with 400 pilots, structure support, and the numbers to make your fleet irrelevant.

This isn't "elite PvP." This isn't even "blob PvP." This is applying nullsec sovereignty logic to a space that was explicitly designed to avoid it.

And because Yagas defends those structures with 400 pilots, small groups can't even attempt to remove them. They can just... not go there.

That's the real problem. Not that Yagas is cheating. But that Pochven was supposed to be an alternative, and it's not.""",

    "ninety_six": """Baba Yagas [YAGAS] — The Initiative.

- 96% gang kills
- 4% solo
- 24.5 average fleet size
- 65 Pochven kills on record, all 25+ attackers

CCP designed Pochven with filaments that teleport 5-15 ships. They designed it with no local chat. They designed it with wormhole connections so you can't predict who's coming.

They did not design it for 400 pilots to camp gates and hold structures.

Baba Yagas is a nullsec bloc corp. They do what nullsec bloc corps do: hold territory, bring numbers, defend assets. That's how The Initiative. operates. That's how nullsec works.

But Pochven isn't nullsec. Or at least, it wasn't supposed to be.

The question isn't "are they allowed to do this?" The question is "what happens to a space designed for small gangs when nullsec blocs move in and can't be dislodged?"

Because that's the situation. Structures CAN be destroyed — but Yagas defends them with 400 pilots. You can't fight that with 10. So you either bring a bloc, or you stop going.

Convocation watching. Kybernauts waiting.

What's your take, r/eve?""",

    "flow_demands": """"We shall fight in Nalvula, we shall fight in Kino, we shall fight in the filament fields and in the wormholes; we shall never surrender Pochven."

But we might stop filamenting in.

Baba Yagas [YAGAS] — The Initiative. — operates in Pochven with 25-50 pilots per engagement. They hold the structures. They apply nullsec bloc logic to a space that was built for something smaller.

The Convocation of Triglav Outside the Struggle designed the Proving Grounds to test worth through individual and small-group merit. Not through who can field the most ships.

Kill: {zkill_url}

A proving ground where the only way to contest structures is to out-blob the blob isn't a proving ground. It's a nullsec region with a Triglavian paint job.

*Zorya Triglav has spoken. The Flow demands better.*""",
}

# === TWITTER TEMPLATES (Evidence-Based, #EVEOnline on every post) ===
TWITTER_TEMPLATES = [
    "Pochven was built for 5-15 ship filaments. Baba Yagas brings 25-50. This is what nullsec logic does to small-gang space. #EVEOnline #Pochven #Kybernauts",
    "The structures in Pochven can't be removed by small gangs. Yagas defends with 400 pilots. You need a bloc to contest a bloc. #EVEOnline #Pochven",
    "Yagas isn't cheating. They're playing nullsec in a space that was supposed to be an alternative to nullsec. That's the actual problem. #EVEOnline #Pochven #Kybernauts",
    "25-50 pilots to kill one ship. 96% gang kills. Pochven's proving grounds were meant for 5-15. Can small-gang space survive nullsec blocs? #EVEOnline #Pochven",
    "Kill {kill_id}: {value}B destroyed. {attackers} attackers. Every Yagas Pochven kill follows this pattern. Nullsec tactics in small-gang space. #EVEOnline #Pochven",
    "The Flow of Vyraj doesn't recognize a 50-ship gank as proving methodology. It recognizes worth — individual worth. Yagas brings numbers instead. #EVEOnline #Pochven #Kybernauts",
    "Structures CAN be destroyed in Pochven. But Yagas defends with 400 pilots. Small gangs can't even attempt it. That's the structural lockout. #EVEOnline #Pochven",
    "CCP built Pochven with no local chat, filaments, and wormholes — all for small-gang. Baba Yagas brought 400 pilot blobs. Wrong game, wrong arena. #EVEOnline #Pochven",
]

def post_to_twitter(text):
    """Post to Twitter/X via Upload-Post API (form-data, not JSON)."""
    url = f"{API_BASE}/upload_text"
    headers = {
        "Authorization": f"Apikey {API_KEY}",
    }
    data = {
        "user": PROFILE,
        "platform[]": "x",
        "title": text,
    }
    try:
        r = requests.post(url, headers=headers, data=data, timeout=30)
        data = r.json()
        print(f"Twitter post status: {r.status_code}")
        print(json.dumps(data, indent=2))
        return data
    except Exception as e:
        print(f"Twitter post failed: {e}")
        return None

def post_to_reddit(title, body, subreddit="eve"):
    """Post to Reddit via Upload-Post API. Currently blocked by flair requirements."""
    url = f"{API_BASE}/upload_text"
    headers = {
        "Authorization": f"Apikey {API_KEY}",
    }
    data = {
        "user": PROFILE,
        "platform[]": "reddit",
        "subreddit": subreddit,
        "title": title,
        "body": body,
    }
    try:
        r = requests.post(url, headers=headers, data=data, timeout=30)
        data = r.json()
        print(f"Reddit post status: {r.status_code}")
        print(json.dumps(data, indent=2))
        return data
    except Exception as e:
        print(f"Reddit post failed: {e}")
        return None

def generate_kill_list(kills, max_items=5):
    """Generate markdown kill list for Reddit posts."""
    lines = []
    total = 0
    for k in kills[:max_items]:
        kid = k.get("id", "???")
        val = k.get("value", 0) / 1e9
        atk = k.get("attackers", 0)
        zkill = k.get("url", f"https://zkillboard.com/kill/{kid}/")
        lines.append(f"- [{kid}]({zkill}) — {val:.1f}B, {atk} attackers")
        total += val
    return "\n".join(lines), total

def generate_reddit_post(mode="random"):
    """Generate a Reddit post using nuanced templates."""
    if mode == "random":
        mode = random.choice(list(REDDIT_BODIES.keys()))
    
    title = random.choice(REDDIT_TITLES)
    body_template = REDDIT_BODIES[mode]
    
    # Fill in kill data if needed
    if "{kill_list}" in body_template and SHIP_KILLS:
        kill_list, total_isk = generate_kill_list(SHIP_KILLS)
        body = body_template.format(
            kill_list=kill_list,
            total_isk=f"{total_isk:.1f}",
            zkill_url=f"https://zkillboard.com/kill/{SHIP_KILLS[0]['id']}/",
            attackers=SHIP_KILLS[0].get("attackers", "???")
        )
    elif "{zkill_url}" in body_template and SHIP_KILLS:
        body = body_template.format(
            zkill_url=SHIP_KILLS[0].get("url", f"https://zkillboard.com/kill/{SHIP_KILLS[0].get('id', '???')}/"),
            attackers=SHIP_KILLS[0].get("attackers", "???")
        )
    else:
        body = body_template
    
    return title, body

def generate_twitter_post():
    """Generate a Twitter/X post using nuanced templates."""
    template = random.choice(TWITTER_TEMPLATES)
    
    # Fill in kill data if template has placeholders
    if "{kill_id}" in template and SHIP_KILLS:
        k = SHIP_KILLS[0]
        atk = "25+"
        for label in k.get("labels", []):
            if label.startswith("#:"):
                atk = label[2:]
                break
        text = template.format(
            kill_id=k.get("id", "???"),
            value=f"{k.get('value', 0)/1e9:.1f}",
            attackers=atk
        )
    else:
        text = template
    
    return text

if __name__ == "__main__":
    import sys
    
    dry = "--dry" in sys.argv
    platforms = [a.lower() for a in sys.argv[1:] if not a.startswith("-")]
    if not platforms:
        print("Usage: python reddit_poster.py [--dry] [reddit|twitter|both]")
        sys.exit(1)
    
    platform = platforms[0]
    
    if platform in ("reddit", "both"):
        title, body = generate_reddit_post()
        print(f"=== REDDIT POST ===")
        print(f"Title: {title}")
        print(f"Body:\n{body}\n")
        if not dry:
            result = post_to_reddit(title, body)
    
    if platform in ("twitter", "both"):
        text = generate_twitter_post()
        print(f"=== TWITTER POST ===")
        print(f"Text: {text}\n")
        if not dry:
            result = post_to_twitter(text)
