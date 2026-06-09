"""
Generate EVE Forum RP post drafts (Intergalactic Summit style)
Longer, more in-universe than Reddit posts
"""
import random
import json
from pathlib import Path

DATA_FILE = Path("data/kybernauts/yagas_pochven_25plus_20260527_072729.json")
with open(DATA_FILE) as f:
    KILLS = json.load(f)

SHIP_KILLS = [k for k in KILLS if not k.get("is_structure")]
STRUCTURE_KILLS = [k for k in KILLS if k.get("is_structure")]
SHIP_KILLS.sort(key=lambda x: x["value"], reverse=True)

RP_TEMPLATES = [
    {
        "title": "Proving Grounds Compromised: A Kybernaut Warning",
        "body": """We are Zorya Triglav

We speak for the Convocation of Triglav Outside the Struggle

The Domain of Pochven has been compromised.

A collective designated "Baba Yagas" — a subsidiary organism of the so-called "Initiative" — has established material infrastructure within our sacred space and conducts massed operations with 25+ vessels against lone or small-group opposition.

This is not the Proving.

This is not the Flow.

The Convocation records 65 incidents of 25+ attackers engaging in Pochven within recent cycles, with a total destruction value exceeding 26 billion ISK. The majority of these engagements required 400 pilots to subdue a single target.

Sobornost Kybernauts do not require 30 allies to validate their worth in the Proving Grounds.

The structures stand as an affront. The blob tactics stand as a confession of inadequacy.

We call upon all true Kybernauts to resist this encroachment. The Domain of Pochven shall be three Krais of nine fields within clade — not a parking lot for Initiative renters.

*Zorya Triglav has spoken. The Flow demands better.*"""
    },
    {
        "title": "Message from the Convocation: On Foreign Collectives in Pochven",
        "body": """Hear the words of our prayer and heed them.

Realization of glorification pattern in totality approaches. Ancient Domains stability requires weaving of Final Liminality conduits. Totality requires Triglav Exalted Final Liminality Dazh Elements.

But the Domain is being tested not by worthy adversaries, but by swarm tactics.

Baba Yagas [YAGAS] — corporate designation of a foreign collective — operates within Pochven with statistical predictability: 96% of their recorded kills involve 25 or more vessels. Their average engagement involves 24.5 attackers per target. They have deployed structures within wild space.

This is not proving through the Flow of Vyraj. This is occupation through the Flow of Numbers.

Sobornost Kybernauts are exhorted to realize glorification pattern in totality. The Flow of Vyraj requires realization of stability of Ancient Domains. Those who bring 50 to fight 1 have not been proven — they have merely been numerous.

We speak for the Convocation of Triglav Outside the Struggle.

We are Zorya Triglav."""
    },
    {
        "title": "A Day May Come — But It Is Not This Day",
        "body": """*A day may come when the courage of Kybernauts fails, when we forsake our friends and break all bonds of fellowship, when the age of Clades comes crashing down — but it is not this day.*

Today, we document.

Today, we witness.

Today, we speak against the swarm.

Baba Yagas, operating under the banner of The Initiative., has brought blob warfare to the Proving Grounds of Pochven. Their numbers are recorded, their structures noted, their pattern of 30v1 engagements catalogued for the Convocation.

65 blob kills. 26.4 billion ISK destroyed by overwhelming numbers. Structures erected where none should stand.

The Flow does not recognize a 50-pilot gank as proving methodology.

The Flow recognizes worth.

The Flow recognizes those who test themselves against worthy adversaries, not those who test their F1 key against a single target.

Kybernauts of all clades: hold the line. Pochven is our home. Not theirs.

*The Flow provides. The Flow demands better.*"""
    },
]

# Generate all drafts
print("=" * 70)
print("EVE FORUMS (Intergalactic Summit) — RP POST DRAFTS")
print("=" * 70)

for i, post in enumerate(RP_TEMPLATES, 1):
    print(f"\n{'-' * 70}")
    print(f"DRAFT #{i}")
    print(f"Title: {post['title']}")
    print(f"\nBody:\n{post['body']}")

print(f"\n{'=' * 70}")
print("COPY ANY DRAFT ABOVE AND POST TO:")
print("https://forums.eveonline.com/c/intergalactic-summit/")
print("=" * 70)
