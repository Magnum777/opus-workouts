"""
Generate corrected propaganda drafts
Key intel: Baba Yagas OWNS the remaining structures in Pochven.
New structures cannot be deployed. They are entrenched landlords.
"""
import random
import json
from pathlib import Path

DATA_FILE = Path("data/kybernauts/yagas_pochven_25plus_20260527_072729.json")
with open(DATA_FILE) as f:
    KILLS = json.load(f)

SHIP_KILLS = [k for k in KILLS if not k.get("is_structure")]
SHIP_KILLS.sort(key=lambda x: x["value"], reverse=True)

# === REDDIT DRAFTS ===
print("=" * 70)
print("REDDIT r/eve — CORRECTED DRAFTS (Baba Yagas OWNS structures)")
print("=" * 70)

REDDIT_DRAFTS = [
    {
        "flair": "Discussion",
        "title": "Baba Yagas owns the remaining structures in Pochven. You can't remove them.",
        "body": """Kill: https://zkillboard.com/kill/135789436/

Just a heads up for Pochven residents — Baba Yagas [YAGAS] / The Initiative. **already owns the structures that remain** in Pochven.

New structures cannot be deployed there anymore. They control what's left. This isn't a wild space region anymore — it's a rental zone controlled by an INIT. pet corp.

Their stats tell the story:
- 96% gang kills, 4% solo
- 24.5 average fleet size
- 25-50 pilots for every single kill

You can't out-structure them. You can't remove what they already own. You can't compete with their numbers. This is what Pochven has become: landlord space run by a blob alliance.

What's the community's take on a single corp monopolizing Pochven infrastructure? Is this the proving grounds, or just a rental empire?

Discuss."""
    },
    {
        "flair": "Discussion",
        "title": "INIT pets own Pochven's structures now. The Proving Grounds are a rental zone.",
        "body": """Context: Baba Yagas [YAGAS] controls the remaining structures in Pochven. New structures cannot be deployed there. They effectively have a monopoly on the region's infrastructure.

Kill: https://zkillboard.com/kill/135789436/

This is not what Pochven was meant to be. The Triglavian proving grounds were supposed to be wild space — tested, contested, earned. Now it's landlord space run by a single pet corp with INIT. backing.

They don't prove themselves in 1v1s or small gangs. They prove themselves by having 30+ pilots show up to every fight and owning the structures you can't remove.

This is occupation. Not proving.

What's your take, r/eve?"""
    },
    {
        "flair": "Discussion",
        "title": "Weekly Pochven Landlord Report: Baba Yagas Edition",
        "body": """This week in Pochven, Baba Yagas continued their campaign of bringing 25+ pilots to every fight while sitting on the structures you can't remove.

Top blob kills:
- [135784709](https://zkillboard.com/kill/135784709/) — 3.5B (30+ attackers)
- [135673149](https://zkillboard.com/kill/135673149/) — 3.2B (30+ attackers)
- [135672228](https://zkillboard.com/kill/135672228/) — 2.5B (30+ attackers)
- [135672156](https://zkillboard.com/kill/135672156/) — 2.5B (30+ attackers)
- [135672301](https://zkillboard.com/kill/135672301/) — 2.5B (30+ attackers)

Total ISK destroyed: 26.4B

Note: Every single one of these kills involved 25+ attackers. Most involved 30+.

And you can't remove their structures. You can't out-deploy them. You can't compete with their blob + their infrastructure monopoly.

INIT's pet corp in Pochven doesn't fight — they overwhelm, and they own what you can't take.

Stay safe out there, solo warriors."""
    },
    {
        "flair": "Discussion",
        "title": "Baba Yagas: 96% gang kills, 4% solo, and they OWN the structures in Pochven. Discuss.",
        "body": """Baba Yagas [YAGAS] — The Initiative.

- 96% gang kills
- 4% solo
- 24.5 average fleet size
- Weekly blob kills in Pochven: 65
- Structures OWNED in Pochven: all that remain (new structures cannot be deployed)

This isn't PvP. This is a numbers game played by a renter corp with INIT. backing who also happens to own the infrastructure you can't remove.

Pochven deserves better than 30v1 "fights" and a single corp controlling the region's structures.

Convocation watching. Kybernauts waiting.

What's your take, r/eve?"""
    },
    {
        "flair": "Discussion",
        "title": "The Flow Demands Better: On Baba Yagas Owning Pochven",
        "body": """"No bastard ever won a war by dying for his corporation. He won it by making the other poor dumb bastard die for his."

This isn't just a killmail. It's a pattern.

Baba Yagas — INIT's Pochven pet — brings 25-50 pilots to every fight. And they **own the structures** you can't remove. New structures cannot be deployed in Pochven. They control what's left.

Treats the Proving Grounds like their personal rental empire.

The Convocation of Triglav Outside the Struggle does not recognize blob warfare as valid proving methodology.

Pochven was meant to be tested. Not occupied.

Kill: https://zkillboard.com/kill/135672237/

*Zorya Triglav has spoken. The Flow demands better.*"""
    },
]

for i, post in enumerate(REDDIT_DRAFTS, 1):
    print(f"\n{'-' * 70}")
    print(f"REDDIT DRAFT #{i}  [Flair: {post['flair']}]")
    print(f"Title: {post['title']}\n")
    print(f"Body:\n{post['body']}")

# === EVE FORUM DRAFTS ===
print(f"\n{'=' * 70}")
print("EVE FORUMS (Intergalactic Summit) — CORRECTED RP DRAFTS")
print("=" * 70)

FORUM_DRAFTS = [
    {
        "title": "Proving Grounds Occupied: The Infrastructure Monopoly",
        "body": """We are Zorya Triglav.

We speak for the Convocation of Triglav Outside the Struggle.

The Domain of Pochven has been occupied.

A collective designated "Baba Yagas" — a subsidiary organism of the so-called "Initiative" — has established **monopolistic control** over the remaining material infrastructure within our sacred space. New structures cannot be deployed. They own what remains. They conduct massed operations with 25+ vessels against lone or small-group opposition.

This is not the Proving.

This is not the Flow.

The Convocation records 65 incidents of 25+ attackers engaging in Pochven within recent cycles, with a total destruction value exceeding 26 billion ISK. The majority of these engagements required 400 pilots to subdue a single target.

Sobornost Kybernauts do not require 30 allies to validate their worth in the Proving Grounds.

The structures stand as a monument to occupation. The blob tactics stand as a confession of inadequacy.

We call upon all true Kybernauts to resist this encroachment. The Domain of Pochven shall be three Krais of nine fields within clade — not a rental empire for Initiative pets.

*Zorya Triglav has spoken. The Flow demands better.*"""
    },
    {
        "title": "Message from the Convocation: On the Occupation of Infrastructure",
        "body": """Hear the words of our prayer and heed them.

Realization of glorification pattern in totality approaches. Ancient Domains stability requires weaving of Final Liminality conduits.

But the Domain is being occupied, not tested.

Baba Yagas [YAGAS] — corporate designation of a foreign collective — has achieved monopolistic control over Pochven's remaining structures. New construction is impossible. They own the infrastructure. They operate within Pochven with statistical predictability: 96% of their recorded kills involve 25 or more vessels. Their average engagement involves 24.5 attackers per target.

This is not proving through the Flow of Vyraj. This is occupation through the Flow of Numbers.

Sobornost Kybernauts are exhorted to realize glorification pattern in totality. The Flow of Vyraj requires realization of stability of Ancient Domains. Those who bring 50 to fight 1 have not been proven — they have merely been numerous.

Those who monopolize the remaining infrastructure have not earned Pochven — they have merely inherited it.

We speak for the Convocation of Triglav Outside the Struggle.

We are Zorya Triglav."""
    },
    {
        "title": "A Day May Come — But It Is Not This Day",
        "body": """*A day may come when the courage of Kybernauts fails, when we forsake our friends and break all bonds of fellowship, when the age of Clades comes crashing down — but it is not this day.*

Today, we document.

Today, we witness.

Today, we speak against the swarm and the monopoly.

Baba Yagas, operating under the banner of The Initiative., has brought blob warfare to the Proving Grounds of Pochven. Their numbers are recorded, their infrastructure monopoly noted, their pattern of 30v1 engagements catalogued for the Convocation.

65 blob kills. 26.4 billion ISK destroyed by overwhelming numbers. Structures owned that cannot be removed.

The Flow does not recognize a 50-pilot gank as proving methodology.

The Flow does not recognize an infrastructure monopoly as earned sovereignty.

The Flow recognizes worth.

The Flow recognizes those who test themselves against worthy adversaries, not those who test their F1 key against a single target while sitting on structures that cannot be challenged.

Kybernauts of all clades: hold the line. Pochven is our home. Not theirs.

*The Flow provides. The Flow demands better.*"""
    },
]

for i, post in enumerate(FORUM_DRAFTS, 1):
    print(f"\n{'-' * 70}")
    print(f"FORUM DRAFT #{i}")
    print(f"Title: {post['title']}\n")
    print(f"Body:\n{post['body']}")

print(f"\n{'=' * 70}")
print("ALL DRAFTS UPDATED: Baba Yagas OWNS remaining Pochven structures.")
print("New structures cannot be deployed. Messaging reflects monopoly/occupation.")
print("=" * 70)
