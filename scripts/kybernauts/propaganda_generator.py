import json, random, datetime
from pathlib import Path

# Load the kill data
DATA_FILE = Path("data/kybernauts/yagas_pochven_25plus_20260527_072729.json")
with open(DATA_FILE) as f:
    KILLS = json.load(f)

STRUCTURE_KILLS = [k for k in KILLS if k.get("is_structure")]
SHIP_KILLS = [k for k in KILLS if not k.get("is_structure")]

# Sort by value
SHIP_KILLS.sort(key=lambda x: x["value"], reverse=True)

# Speech/quote fragments for adaptation
ADAPTED_QUOTES = [
    '"We shall fight in Nalvula, we shall fight in Kino, we shall fight in the filament fields and in the wormholes; we shall never surrender Pochven." — Kybernaut Address',
    '"No bastard ever won a war by dying for his corporation. He won it by making the other poor dumb bastard die for his." — Clade War Doctrine',
    '"A day may come when the courage of Kybernauts fails... but it is not this day. An hour of wolves and shattered ships, when the age of Clades comes crashing down! But it is not this day! This day we fight!"',
    '"We few, we happy few, we band of Kybernauts. For he today that sheds his pod with me shall be my brother." — Proving Ground Invocation',
    '"I have nothing to offer but blood, toil, tears, and filament cycles." — Convocation Address',
]

# Mockery templates
BLOB_MOCKS = [
    "It took {attackers} Baba Yagas to kill one {ship}. That's not a fight, that's a field trip.",
    "When you need {attackers} pilots for a single kill, you're not elite. You're just numerous.",
    "Baba Yagas: proving that quantity has a quality all its own. {attackers} vs 1, and they barely won.",
    "INIT pets brought {attackers} to the party. Still couldn't kill fast enough.",
    "Structure kill #{count}: Baba Yagas continues their conquest of inanimate objects in Pochven.",
]

# Reddit post templates
REDDIT_TEMPLATES = {
    "structure_report": """[Pochven] Baba Yagas dropped another structure in {system}

Just a heads up for Pochven residents — Baba Yagas [YAGAS] / The Initiative. dropped a {structure_type} in {system} recently.

Kill: {zkill_url}

Is this what Pochven is becoming? Structures, blobs, and INIT pets? The region used to be wild space. Now it's getting paved over by renter alliances with more numbers than skill.

What's the community's take on structures in Pochven? Should they be allowed to stand, or is this an abomination against the Triglavian proving grounds?""",

    "blob_mockery": """Baba Yagas needed {attackers} pilots to kill a {ship}. This is fine.

Kill: {zkill_url}

Context: This isn't a strategic battle. This isn't a fleet fight. This is {attackers} people showing up to dunk one {ship} in Pochven.

Their killboard is 96% gang kills, 4% solo. Their average fleet size is 24.5. This is not elite PvP. This is the space equivalent of a swarm of toddlers tackling a single adult.

When did Pochven become about blobbing rather than proving?

Discuss.""",

    "weekly_roundup": """Weekly Pochven Blob Report: Baba Yagas Edition

This week in Pochven, Baba Yagas continued their campaign of bringing 25+ pilots to every fight. Highlights:

{kill_list}

Total ISK destroyed: {total_isk:.1f}B

Note: Every single one of these kills involved 25+ attackers. Most involved 30+. Some hit 50+.

INIT's pet corp in Pochven doesn't fight — they overwhelm. There's a difference.

Stay safe out there, solo warriors.""",
}

# EVE Forums (RP-tinged, longer)
FORUM_TEMPLATES = {
    "rp_address": """**Message from the Convocation of Triglav Outside the Struggle**

Sobornost Kybernauts and all who dwell in the Proving Grounds,

We have observed with mounting concern the encroachment of foreign collectives into the Domain of Pochven. The entity designated "Baba Yagas" — a subsidiary of the so-called "Initiative" — has established material infrastructure within our sacred space and conducts massed operations with 25+ vessels against lone or small-group opposition.

This is not the Proving. This is not the Flow.

{quote}

The Convocation does not recognize blob warfare as a valid proving methodology. The Kybernauts who have made Pochven their home do not require 25 allies to validate their worth.

The structures stand as an affront. The blob tactics stand as a confession of inadequacy.

We call upon all true Kybernauts to resist this encroachment. The Domain of Pochven shall be three Krais of nine fields within clade — not a parking lot for INIT. renters.

Zorya Triglav has spoken. The Flow demands better.

— Transmitted on behalf of the Convocation""",
}

# Twitter/X templates (short, punchy)
TWITTER_TEMPLATES = [
    "Baba Yagas brought {attackers} pilots to kill one {ship} in Pochven today. That's not PvP. That's a stampede. {url} #EVEOnline #Pochven",
    "INIT pets putting structures in Pochven now. Wild space? More like landlord space. {url} #EVEOnline",
    "The Proving Grounds aren't supposed to have landlords. Baba Yagas disagrees. {url} #Triglavian #Pochven",
    "96% gang kills. 4% solo. 24.5 average fleet size. Baba Yagas: proving that numbers beat skill since 2023. {url}",
    '"We few, we happy few." — said no Baba Yagas ever. They need {attackers} to feel safe. {url}',
    "Another structure in Pochven. Another abomination. The Convocation weeps. {url} #Triglavian",
    "Pochven used to be the wild west. Now it's getting blobbed by INIT. renters. What happened? {url}",
]

def get_random_kill(kill_type="ship"):
    pool = SHIP_KILLS if kill_type == "ship" else STRUCTURE_KILLS
    if not pool:
        return None
    return random.choice(pool)

def format_value(val):
    if val >= 1e9:
        return f"{val/1e9:.1f}B"
    return f"{val/1e6:.1f}M"

def generate_reddit_post(template_name="blob_mockery"):
    kill = get_random_kill()
    if not kill:
        return "No kills available."
    
    if template_name == "blob_mockery":
        return REDDIT_TEMPLATES["blob_mockery"].format(
            attackers="30+",
            ship="Triglavian ship",
            zkill_url=kill["url"]
        )
    elif template_name == "weekly_roundup":
        top = SHIP_KILLS[:5]
        kill_list = "\n".join(f"- [{k['id']}]({k['url']}) — {format_value(k['value'])}" for k in top)
        total = sum(k["value"] for k in SHIP_KILLS[:10]) / 1e9
        return REDDIT_TEMPLATES["weekly_roundup"].format(
            kill_list=kill_list,
            total_isk=total
        )
    elif template_name == "structure_report" and STRUCTURE_KILLS:
        sk = STRUCTURE_KILLS[0]
        return REDDIT_TEMPLATES["structure_report"].format(
            system="Pochven",
            structure_type="structure",
            zkill_url=sk["url"]
        )
    
    return "Unknown template."

def generate_twitter_post():
    kill = get_random_kill()
    if not kill:
        return "No kills available."
    
    tmpl = random.choice(TWITTER_TEMPLATES)
    ship_name = "ship"  # would need typeID lookup
    return tmpl.format(attackers="30+", ship=ship_name, url=kill["url"])

def generate_forum_post():
    quote = random.choice(ADAPTED_QUOTES)
    return FORUM_TEMPLATES["rp_address"].format(quote=quote)

if __name__ == "__main__":
    print("=== REDDIT BLOB MOCKERY ===")
    print(generate_reddit_post("blob_mockery"))
    print("\n=== TWITTER ===")
    print(generate_twitter_post())
    print("\n=== FORUM RP ADDRESS ===")
    print(generate_forum_post())
    print("\n=== WEEKLY ROUNDUP ===")
    print(generate_reddit_post("weekly_roundup"))
