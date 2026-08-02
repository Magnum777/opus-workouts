#!/usr/bin/env python3
"""
Anti-Yagas Propaganda Post Generator
Reads intel data + phased plan, generates post based on current phase.
Posts to Twitter/X @PochvenIntel and Bluesky via EVEPropaganda profile.
"""
import json
import os
import sys
import random
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Paths
INTEL_DIR = Path("data/kybernauts/yagas_intel")
PLAN_FILE = Path("anti-yagas-phased-plan.md")
PSYOPS_FILE = Path("anti-yagas-psyops.md")
STATE_FILE = Path("data/kybernauts/phase_state.json")

# Upload-Post config
API_KEY = os.environ.get("UPLOADPOST_API_KEY") or ""
PROFILE = "EVEPropaganda"

# Phase definitions
PHASES = {
    1: {"name": "Vague Observation", "start": "2026-05-27", "direct_naming": False},
    2: {"name": "Pattern Recognition", "start": "2026-06-10", "direct_naming": False},
    3: {"name": "Direct Confrontation", "start": "2026-06-24", "direct_naming": True},
    4: {"name": "Sustained Pressure", "start": "2026-07-08", "direct_naming": True},
}


def load_intel() -> dict:
    """Load latest intel data."""
    latest_file = INTEL_DIR / "latest.json"
    if not latest_file.exists():
        print("ERROR: No intel data found. Run yagas_intel_collect.py first.")
        sys.exit(1)
    with open(latest_file, "r") as f:
        return json.load(f)


def load_phase_state() -> dict:
    """Load current phase state."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    # Default: calculate based on date
    now = datetime.now()
    for phase_num, phase_info in sorted(PHASES.items(), reverse=True):
        start = datetime.strptime(phase_info["start"], "%Y-%m-%d")
        if now >= start:
            return {"current_phase": phase_num, "since": phase_info["start"]}
    return {"current_phase": 1, "since": PHASES[1]["start"]}


def save_phase_state(state: dict):
    """Save phase state."""
    os.makedirs(STATE_FILE.parent, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# === TEMPLATES BY PHASE ===

PHASE1_TEMPLATES = [
    "Anyone else notice bigger fleets in Pochven lately? Used to see 5v5s, now it's feeling more like nullsec. #EVEOnline #Pochven",
    "Filaments bring 5-15 ships. Pochven was built for that. Wondering if the space is still serving its purpose. #EVEOnline #Pochven",
    "The proving grounds were meant for small-gang merit. Not sure that's what's happening out there anymore. #EVEOnline #Pochven #Kybernauts",
    "No local chat. Wormhole connections. Filament access. Pochven was an alternative to nullsec. Is it still? #EVEOnline #Pochven",
    "Tracked {blob_count} blob kills this week in Pochven. Average fleet size: {avg_fleet_size}. Something's shifted. #EVEOnline #Pochven",
]

PHASE2_TEMPLATES = [
    "Kill {sample_kill_id}: {sample_value}B destroyed, {avg_fleet_size} attackers. In a space built for 5-15 ship gangs. Pattern emerging. #EVEOnline #Pochven",
    "Nullsec blocs in Pochven. Not naming names. But the data tells a story. {blob_pct}% of kills this week were 20+ pilots. #EVEOnline #Pochven",
    "{pochven_pct}% of their activity is in Pochven. Avg fleet: {avg_fleet_size} pilots. This is what nullsec blocs do to small-gang space. #EVEOnline #Pochven",
    "{total_kills} kills this week. {blob_count} were blob kills (20+ pilots). Pochven was designed for filaments and small gangs. The data doesn't lie. #EVEOnline #Pochven",
    "Structures CAN be destroyed in Pochven. But when the defense fleet is {avg_fleet_size} pilots, small gangs can't even try. Structural lockout. #EVEOnline #Pochven",
]

PHASE3_TEMPLATES = [
    "Baba Yagas [YAGAS] — The Initiative. — {blob_pct}% gang kills, {avg_fleet_size} avg fleet size. This is what nullsec blocs do to small-gang space. #EVEOnline #Pochven",
    "Kill {sample_kill_id}: {sample_value}B, {sample_fleet_size} attackers. Baba Yagas. Pochven was built for 5-15 ships. They're bringing {avg_fleet_size}. #EVEOnline #Pochven",
    "The structures in Pochven CAN be destroyed. But Yagas defends with {max_fleet_size} pilots. Small gangs can't even attempt it. Structural lockout. #EVEOnline #Pochven",
    "Pochven was an alternative to nullsec. Then a nullsec bloc moved in. Now it's nullsec with a Triglavian skin. Thanks Baba Yagas. #EVEOnline #Pochven",
    "{total_kills} kills, {blob_count} blob kills, {total_isk}B ISK destroyed. Baba Yagas isn't cheating — they're just playing the wrong game in Pochven. #EVEOnline #Pochven",
]

PHASE4_TEMPLATES = [
    "Weekly blob watch: Baba Yagas {blob_count} blob kills, {avg_fleet_size} avg fleet size. Pochven small-gang life, week {weeks_since_start}. #EVEOnline #Pochven",
    "Fortress Pochven update: Yagas still bringing {avg_fleet_size} pilots to a space built for 5-15. When does this become the new normal? #EVEOnline #Pochven",
    "Kill {sample_kill_id}: {sample_fleet_size} attackers, {sample_value}B. Same pattern, different day. Baba Yagas in Pochven. #EVEOnline #Pochven",
    "Tired of blobs in Pochven? You're not alone. Baba Yagas brings nullsec logic to small-gang space. The data proves it. #EVEOnline #Pochven join.kybernauts.today",
    "{total_isk}B destroyed by blob fleets this week in Pochven. Small gangs need not apply. #EVEOnline #Pochven",
]


def generate_post(intel: dict, phase: int) -> str:
    """Generate a post based on phase and intel data."""
    analysis = intel.get("analysis", {})
    
    # Extract data points
    total_kills = analysis.get("total_kills", 0)
    blob_count = analysis.get("blob_kills_20plus", 0)
    blob_pct = analysis.get("blob_percentage", 0)
    avg_fleet = analysis.get("avg_fleet_size", 0)
    max_fleet = analysis.get("max_fleet_size", 0)
    total_isk = analysis.get("total_isk_b", 0)
    pochven_pct = analysis.get("pochven_percentage", 0)
    
    # Get sample kill for specifics
    sample_kill = None
    recent_kills = analysis.get("recent_pochven_kills", [])
    if recent_kills:
        sample_kill = random.choice(recent_kills)
    
    # Format data
    data = {
        "total_kills": total_kills,
        "blob_count": blob_count,
        "blob_pct": blob_pct,
        "avg_fleet_size": avg_fleet,
        "max_fleet_size": max_fleet,
        "total_isk": total_isk,
        "pochven_pct": pochven_pct,
        "sample_kill_id": sample_kill["killmail_id"] if sample_kill else "N/A",
        "sample_value": round(sample_kill["value"] / 1e9, 1) if sample_kill else 0,
        "sample_fleet_size": sample_kill["fleet_size"] if sample_kill else 0,
        "weeks_since_start": (datetime.now() - datetime.strptime(PHASES[1]["start"], "%Y-%m-%d")).days // 7,
    }
    
    # Select template based on phase
    if phase == 1:
        templates = PHASE1_TEMPLATES
    elif phase == 2:
        templates = PHASE2_TEMPLATES
    elif phase == 3:
        templates = PHASE3_TEMPLATES
    else:
        templates = PHASE4_TEMPLATES
    
    template = random.choice(templates)
    
    # Fill in data
    try:
        post = template.format(**data)
    except KeyError:
        # Fallback if data missing
        post = template
    
    return post


def post_to_social(text: str, dry_run: bool = False) -> dict:
    """Post text to Twitter/X and Bluesky via Upload-Post API."""
    if dry_run:
        print(f"[DRY RUN] Would post:\n{text}")
        return {"success": True, "dry_run": True}
    
    if not API_KEY:
        print("ERROR: UPLOADPOST_API_KEY not set")
        return {"success": False, "error": "API key missing"}
    
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://api.upload-post.com/api/upload_text",
        "-H", f"Authorization: Apikey {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "user": PROFILE,
            "platform": ["x", "bluesky"],
            "title": text,
        }),
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"success": False, "error": result.stdout or result.stderr}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4], help="Override phase")
    args = parser.parse_args()
    
    print(f"=== Yagas Propaganda Generator — {datetime.now().isoformat()} ===")
    
    # Load intel
    print("Loading intel...")
    intel = load_intel()
    
    # Determine phase
    state = load_phase_state()
    phase = args.phase or state.get("current_phase", 2)
    print(f"Current phase: {phase} ({PHASES[phase]['name']})")
    
    # Generate post
    print("Generating post...")
    post = generate_post(intel, phase)
    print(f"\nGenerated post:\n{post}\n")
    
    # Save draft
    draft_file = INTEL_DIR / f"draft_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(draft_file, "w") as f:
        f.write(post)
    print(f"Saved draft: {draft_file}")
    
    # Post to social media
    if not args.dry_run:
        print("Posting to social media...")
        result = post_to_social(post, dry_run=False)
        print(f"Result: {result}")
        
        # Update state
        state["last_post"] = datetime.now().isoformat()
        state["last_post_text"] = post
        save_phase_state(state)
    else:
        print("Dry run — not posting.")
    
    return 0


if __name__ == "__main__":
    import argparse
    sys.exit(main())
