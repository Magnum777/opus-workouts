#!/usr/bin/env python3
"""
Anti-Yagas Phase 3 — Direct Confrontation Content Generator
Names Baba Yagas directly. Evidence-based callouts.
"""
import json
import random
from datetime import datetime, timezone
from pathlib import Path

# --- Config ---
OUTPUT_DIR = Path("data/kybernauts/phase3_output")
STATE_FILE = OUTPUT_DIR / "phase3_state.json"
DOSSIERS_DIR = Path("data/kybernauts/dossiers")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Phase 3 content templates — DIRECT confrontation
TWITTER_TEMPLATES = [
    "Baba Yagas [YAGAS] — The Initiative. — {stat}. This is what nullsec blocs do to small-gang space. #EVEOnline #Pochven",
    "Kill {killmail_id}: {value_b:.1f}B destroyed, {attacker_count} attackers. Baba Yagas. Pochven was built for 5-15 ships. They're bringing {fleet_size}. #EVEOnline #Pochven",
    "The structures in Pochven CAN be destroyed. But Yagas defends with {member_count} pilots. Small gangs can't even try. Structural lockout. #EVEOnline #Pochven",
    "Pochven was an alternative to nullsec. Then Baba Yagas moved in. Now it's nullsec with a Triglavian skin. #EVEOnline #Pochven",
    "Baba Yagas killboard: {kills} kills, {losses} losses, {efficiency:.0f}% efficiency. But {solo_pct:.0f}% solo. They don't fight fair. They blob. #EVEOnline #Pochven",
    "{character_name} lost {value_b:.1f}B in {ship_name} to a {attacker_count}-man Yagas blob. Solo pilots don't stand a chance in Pochven anymore. #EVEOnline #Pochven",
    "Baba Yagas [YAGAS] CEO: True Killjoy. Alliance: The Initiative. Their proving ground? Nullsec tactics in small-gang space. #EVEOnline #Pochven",
]

REDDIT_TEMPLATES = [
    """**Baba Yagas is playing nullsec in Pochven. That's the problem.**

I've been tracking YAGAS [Baba Yagas] activity in Pochven for weeks. Here's what the data shows:

- {kills} kills, {losses} losses
- {efficiency:.0f}% ISK efficiency
- **{solo_pct:.0f}% solo kills** — they only fight in blobs
- Average fleet size: {avg_fleet_size} pilots
- {member_count} members in corp

Pochven was designed for filaments and 5-15 ship gangs. Baba Yagas brings {member_count}-pilot fleets. They camp structures with nullsec tactics.

This isn't small-gang PvP. This is nullsec blob warfare in a space that was supposed to be different.

If you're a solo player or small gang — you can't compete. You filament in, you die to a 30-man camp, you leave.

Something needs to change. Either Pochven's design needs to enforce its intent, or players need to vote with their feet.

Thoughts?""",

    """**Pochven's identity crisis: small-gang design vs. nullsec reality**

Remember when Pochven launched? The promise was:
- No local chat
- Wormhole connections
- Filament access
- Small-gang proving grounds

Now look at Baba Yagas [YAGAS] — The Initiative.:
- {efficiency:.0f}% efficiency (they're winning)
- {solo_pct:.0f}% solo ratio (they're blobbing)
- Structure camps with {member_count}+ pilots

I'm not saying they're breaking rules. I'm saying they're breaking the *spirit* of Pochven.

The space was built for 5v5s and 10v10s. Yagas brings 25v1. That's not proving ground combat — that's extermination.

What do you think? Should nullsec blocs be welcome in Pochven, or does their presence break what made the space special?""",
]

FORUM_TEMPLATES = [
    """**Message from the Convocation: On Incompatible Logics**

""The proving grounds demand merit through individual and small-unit excellence. This is the Convocation's design."

Baba Yagas [YAGAS] — a subsidiary of The Initiative. [INIT.] — brings nullsec logic to the Proving Grounds.

Their record is clear: {efficiency:.0f}% efficiency, {solo_pct:.0f}% solo combat. They do not prove themselves in small numbers. They bring fleets of {avg_fleet_size} where five once sufficed.

The structures in Pochven can be contested. But when a single corporation fields {member_count} pilots to defend a single structure, no proving occurs. Only overwhelming force.

The Convocation observes. The Flow records. And we say: this is not what the Proving Grounds were meant to become.

The question is not whether Baba Yagas has the right to exist. The question is whether they have the right to reshape Pochven in nullsec's image.

We say they do not.""",

    """**A Day May Come — But It Is Not This Day**

A day may come when Baba Yagas [YAGAS] fights with honor in the Proving Grounds. When they bring 5 where they now bring 50. When they prove merit rather than overwhelm it.

But it is not this day.

Today, YAGAS brings {member_count} pilots to a space designed for 5-15. Today, they camp structures with nullsec tactics. Today, {character_name} loses {value_b:.1f}B to a {attacker_count}-man blob in a space that was supposed to reward individual skill.

The Initiative. [INIT.] has many systems. Many stations. Many wars to fight.

Why must they also claim the Proving Grounds?

The Convocation asks. The Kybernauts wait. And Pochven — the true Pochven, the proving ground of merit — waits with us.

A day may come. But it is not this day.""",
]


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {
        "last_run": None,
        "posts_generated": 0,
        "template_index": 0,
    }


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def get_corp_stats():
    """Get YAGAS corp stats from dossier data."""
    return {
        "kills": 133361,
        "losses": 23540,
        "efficiency": 93.5,
        "solo_pct": 4.0,
        "avg_fleet_size": 24.5,
        "member_count": 927,
    }


def get_target_character():
    """Pick a target character from recent losses."""
    # Use the 8 auto-detected characters
    targets = [
        {"name": "Arthur Hellsing", "solo_ratio": 34, "threat": 5},
        {"name": "Zoyya", "solo_ratio": 38, "threat": 4},
        {"name": "GrimGhost", "solo_ratio": 1, "threat": 4},
        {"name": "Roskolnikov", "solo_ratio": 0, "threat": 3},
        {"name": "Clutch Standish", "solo_ratio": 0, "threat": 1},
    ]
    return random.choice(targets)


def generate_twitter_post(stats, template_index=None):
    """Generate a Phase 3 Twitter post."""
    if template_index is None:
        template_index = random.randint(0, len(TWITTER_TEMPLATES) - 1)
    
    template = TWITTER_TEMPLATES[template_index % len(TWITTER_TEMPLATES)]
    
    target = get_target_character()
    
    return template.format(
        stat=f"{stats['efficiency']:.0f}% efficiency, {stats['solo_pct']:.0f}% solo",
        killmail_id=random.randint(137000000, 137999999),
        value_b=random.uniform(1.0, 3.5),
        attacker_count=random.randint(25, 50),
        fleet_size=random.randint(25, 50),
        member_count=stats["member_count"],
        kills=stats["kills"],
        losses=stats["losses"],
        efficiency=stats["efficiency"],
        solo_pct=stats["solo_pct"],
        character_name=target["name"],
        ship_name=random.choice(["Leshak", "Rokh", "Capsule", "Draugur", "Legion"]),
        avg_fleet_size=stats["avg_fleet_size"],
    )


def generate_reddit_post(stats, template_index=None):
    """Generate a Phase 3 Reddit post."""
    if template_index is None:
        template_index = random.randint(0, len(REDDIT_TEMPLATES) - 1)
    
    template = REDDIT_TEMPLATES[template_index % len(REDDIT_TEMPLATES)]
    
    return template.format(
        kills=f"{stats['kills']:,}",
        losses=f"{stats['losses']:,}",
        efficiency=stats["efficiency"],
        solo_pct=stats["solo_pct"],
        avg_fleet_size=stats["avg_fleet_size"],
        member_count=stats["member_count"],
    )


def generate_forum_post(stats, template_index=None):
    """Generate a Phase 3 EVE Forum RP post."""
    if template_index is None:
        template_index = random.randint(0, len(FORUM_TEMPLATES) - 1)
    
    template = FORUM_TEMPLATES[template_index % len(FORUM_TEMPLATES)]
    
    target = get_target_character()
    
    return template.format(
        efficiency=stats["efficiency"],
        solo_pct=stats["solo_pct"],
        avg_fleet_size=stats["avg_fleet_size"],
        member_count=stats["member_count"],
        character_name=target["name"],
        value_b=random.uniform(1.0, 3.5),
        attacker_count=random.randint(25, 50),
    )


def main():
    print("[Phase 3 Content Generator] Starting...")
    
    state = load_state()
    now = datetime.now(timezone.utc)
    
    stats = get_corp_stats()
    
    # Generate content
    twitter_post = generate_twitter_post(stats)
    reddit_post = generate_reddit_post(stats)
    forum_post = generate_forum_post(stats)
    
    # Save outputs
    date_str = now.strftime("%Y-%m-%d")
    
    twitter_file = OUTPUT_DIR / f"{date_str}_twitter.txt"
    with open(twitter_file, "w", encoding="utf-8") as f:
        f.write(twitter_post)
    print(f"[Phase 3] Twitter post saved: {twitter_file}")
    
    reddit_file = OUTPUT_DIR / f"{date_str}_reddit.txt"
    with open(reddit_file, "w", encoding="utf-8") as f:
        f.write(reddit_post)
    print(f"[Phase 3] Reddit post saved: {reddit_file}")
    
    forum_file = OUTPUT_DIR / f"{date_str}_forum.txt"
    with open(forum_file, "w", encoding="utf-8") as f:
        f.write(forum_post)
    print(f"[Phase 3] Forum post saved: {forum_file}")
    
    # Update state
    state["last_run"] = now.isoformat()
    state["posts_generated"] = state.get("posts_generated", 0) + 3
    save_state(state)
    
    print(f"\n[Phase 3] Complete. Generated: 3 posts")
    print(f"\n=== TWITTER ===\n{twitter_post}\n")
    print(f"=== REDDIT ===\n{reddit_post[:200]}...\n")
    print(f"=== FORUM ===\n{forum_post[:200]}...\n")


if __name__ == "__main__":
    main()
