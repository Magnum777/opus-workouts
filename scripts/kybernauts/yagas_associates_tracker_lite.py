#!/usr/bin/env python3
"""
YAGAS Known Associates Tracker — Lightweight Version
Doesn't require browser automation. Builds from existing data + generates zKillboard URLs.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# --- Config ---
REPORTS_DIR = Path("data/kybernauts/intel")
ASSOCIATES_FILE = REPORTS_DIR / "associates_state.json"
DOSSIERS_DIR = Path("data/kybernauts/dossiers")
YAGAS_CORP_ID = "98754582"
INIT_ALLIANCE_ID = "99003581"

# Core 25 tracked characters
TRACKED_CHARS = [
    "True Killjoy", "ShepherdE", "Yuoree", "Zhaturin Lemonseeker", "Ivrae-1",
    "Korkisgod", "Heldrum", "Sir Tikon", "Pigii AkA", "Yzy Andedare",
    "rapthera", "Thanaatos Amatin", "Warr Cry", "K0r3", "Uthreignish",
    "Orbis Bellum", "ISDN Ndsi", "zomg harkonnen", "Leuna town",
    "Kylon Olgidar", "Kylon Muutaras", "Kylon Triplet",
    "Gabriell Bemenacth", "Caleopi", "VpFalcon",
]

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_associates_state():
    if ASSOCIATES_FILE.exists():
        with open(ASSOCIATES_FILE) as f:
            return json.load(f)
    return {
        "associations": {},
        "last_updated": None,
        "departure_tracking": {},
        "arrival_tracking": {},
        "movement_history": [],
        "pochven_init_chars": [],
    }


def save_associates_state(state):
    with open(ASSOCIATES_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_zkill_search_url(char_name):
    """Generate zKillboard search URL for a character."""
    return f"https://zkillboard.com/search/{char_name.replace(' ', '%20')}/"


def get_zkill_character_url(char_name):
    """Generate zKillboard character page URL (requires char ID, fallback to search)."""
    return f"https://zkillboard.com/search/{char_name.replace(' ', '%20')}/"


def get_zkill_corp_url(corp_id):
    return f"https://zkillboard.com/corporation/{corp_id}/"


def get_zkill_alliance_url(alliance_id):
    return f"https://zkillboard.com/alliance/{alliance_id}/"


def get_evewho_character_url(char_name):
    return f"https://evewho.com/pilot/{char_name.replace(' ', '%20')}"


def get_evewho_corp_url(corp_name):
    return f"https://evewho.com/corp/{corp_name.replace(' ', '%20')}"


def parse_dossier_for_intel(dossier_path):
    """Parse existing dossier for association hints."""
    if not dossier_path.exists():
        return {}
    
    content = dossier_path.read_text(encoding='utf-8', errors='ignore')
    intel = {
        "corp_history": [],
        "known_associates": [],
        "notes": [],
    }
    
    # Extract corp history lines
    in_corp_history = False
    for line in content.split("\n"):
        line = line.strip()
        if "Corp History" in line or "corporation history" in line.lower():
            in_corp_history = True
            continue
        if in_corp_history:
            if line.startswith("-") or line.startswith("*"):
                intel["corp_history"].append(line.lstrip("- *").strip())
            elif not line:
                in_corp_history = False
    
    # Look for mentions of other tracked characters
    for other_char in TRACKED_CHARS:
        if other_char.lower() in content.lower() and other_char not in str(dossier_path):
            intel["known_associates"].append(other_char)
    
    return intel


def build_associations_from_dossiers():
    """Build association map by parsing existing dossiers."""
    associations = defaultdict(lambda: defaultdict(int))
    
    for char_name in TRACKED_CHARS:
        dossier_path = DOSSIERS_DIR / f"{char_name.replace(' ', '_')}.md"
        intel = parse_dossier_for_intel(dossier_path)
        
        for assoc in intel["known_associates"]:
            if assoc in TRACKED_CHARS and assoc != char_name:
                associations[char_name][assoc] += 1
    
    # Known associations from dossier research:
    # GameTheory clique
    associations["ShepherdE"]["Warr Cry"] = 5
    associations["ShepherdE"]["Leuna town"] = 5
    associations["Warr Cry"]["Leuna town"] = 4
    associations["Warr Cry"]["ShepherdE"] = 5
    associations["Leuna town"]["ShepherdE"] = 5
    associations["Leuna town"]["Warr Cry"] = 4
    
    # Kylon family (same player, confirmed alts)
    associations["Kylon Olgidar"]["Kylon Muutaras"] = 10
    associations["Kylon Olgidar"]["Kylon Triplet"] = 10
    associations["Kylon Muutaras"]["Kylon Olgidar"] = 10
    associations["Kylon Muutaras"]["Kylon Triplet"] = 10
    associations["Kylon Triplet"]["Kylon Olgidar"] = 10
    associations["Kylon Triplet"]["Kylon Muutaras"] = 10
    
    # Yzy family (confirmed alts)
    associations["Yzy Andedare"]["Yzy Diggler"] = 10
    
    # Defector connection
    associations["Orbis Bellum"]["ISDN Ndsi"] = 3  # Both came from Kybernauts
    associations["ISDN Ndsi"]["Orbis Bellum"] = 3
    
    return dict(associations)


def fetch_pochven_init_via_zkill_web(days=4):
    """
    Fetch INIT. killmails in Pochven via zKillboard web.
    Returns list of character names found.
    NOTE: This requires browser automation. In headless mode, returns empty.
    """
    # For now, return empty and flag for manual review
    return []


def generate_associates_report(state, init_pochven_chars=None):
    """Generate markdown associates report."""
    now = datetime.now(timezone.utc)
    report_date = now.strftime("%Y-%m-%d")
    
    report_lines = [
        f"# YAGAS Known Associates Report — {report_date}",
        "",
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Quick Links for Manual Review",
        "",
        "### zKillboard — YAGAS Corp",
        f"- [YAGAS Corp Killboard](https://zkillboard.com/corporation/98754582/)",
        "",
        "### zKillboard — INIT. Alliance",
        f"- [INIT. Alliance Killboard](https://zkillboard.com/alliance/99003581/)",
        "",
        "### EVEWho — YAGAS Corp Roster",
        f"- [YAGAS Corp Members](https://evewho.com/corp/Baba+Yagas)",
        "",
    ]
    
    # INIT. Pochven operators
    report_lines.append("## INIT. Characters Active in Pochven")
    report_lines.append("")
    
    if init_pochven_chars:
        report_lines.append(f"**{len(init_pochven_chars)} INIT. character(s)** detected in Pochven systems (last 4 days):")
        report_lines.append("")
        for char_name in init_pochven_chars:
            report_lines.append(f"- {char_name}")
    else:
        report_lines.append("- **Auto-detection requires browser automation** — currently unavailable in headless mode")
        report_lines.append("- **Manual check:** [zKillboard INIT. Pochven kills](https://zkillboard.com/alliance/99003581/kills/)")
        report_lines.append("- Look for kills in Pochven systems (Urhinichi, Ahbazon, etc.)")
    
    report_lines.append("")
    
    # Character Associations
    report_lines.append("## Character Associations (From Dossier Research)")
    report_lines.append("")
    report_lines.append("Based on corp history, known alts, and dossier cross-references.")
    report_lines.append("")
    
    associations = state.get("associations", {})
    
    if associations:
        report_lines.append("| Character | Associates | Strength |")
        report_lines.append("|-----------|-----------|----------|")
        
        for char_name in sorted(associations.keys()):
            assoc_list = associations[char_name]
            if assoc_list:
                for assoc_name, strength in sorted(assoc_list.items(), key=lambda x: -x[1]):
                    strength_label = "Strong" if strength >= 7 else "Moderate" if strength >= 3 else "Weak"
                    report_lines.append(f"| {char_name} | {assoc_name} | {strength_label} ({strength}) |")
    else:
        report_lines.append("*No association data. Run dossier deep-dive first.*")
    
    report_lines.append("")
    
    # Known Cliques
    report_lines.append("## Known Cliques/Networks")
    report_lines.append("")
    
    cliques = [
        ("GameTheory Alumni", ["ShepherdE", "Warr Cry", "Leuna town"], 
         "All came from GameTheory before joining YAGAS. Social connection.",
         "High"),
        ("Kylon Family", ["Kylon Olgidar", "Kylon Muutaras", "Kylon Triplet"],
         "Confirmed same-player alts. Same pilot, different characters.",
         "Confirmed"),
        ("Kybernauts Defectors", ["Orbis Bellum", "ISDN Ndsi"],
         "Both came from Kybernauts to YAGAS. May share intel about our operations.",
         "Critical"),
        ("Yzy Family", ["Yzy Andedare", "Yzy Diggler"],
         "Confirmed alts. Carebear mains with PVP alts.",
         "Confirmed"),
    ]
    
    for name, members, note, confidence in cliques:
        report_lines.append(f"### {name} (Confidence: {confidence})")
        report_lines.append("")
        report_lines.append(f"**Members:** {', '.join(members)}")
        report_lines.append(f"**Note:** {note}")
        report_lines.append("")
    
    report_lines.append("## Movement Tracking")
    report_lines.append("")
    
    recent_movements = [m for m in state.get("movement_history", [])
                       if (now - datetime.fromisoformat(m["date"]).replace(tzinfo=timezone.utc)).days <= 30]
    
    if recent_movements:
        report_lines.append(f"**{len(recent_movements)} movement(s)** in last 30 days:")
        report_lines.append("")
        for movement in recent_movements:
            report_lines.append(
                f"- {movement['date'][:10]}: **{movement['character']}** → {movement['to']}"
            )
    else:
        report_lines.append("- No movements detected in last 30 days")
        report_lines.append("- **Manual check:** Compare EVEWho roster week-over-week")
    
    report_lines.append("")
    
    # Per-character deep links
    report_lines.append("## Per-Character zKillboard Links")
    report_lines.append("")
    report_lines.append("For manual killmail review (right-click → open in browser):")
    report_lines.append("")
    
    for char_name in sorted(TRACKED_CHARS):
        report_lines.append(
            f"- [{char_name}]({get_zkill_character_url(char_name)}) — "
            f"[EVEWho]({get_evewho_character_url(char_name)})"
        )
    
    report_lines.append("")
    
    # Recommendations
    report_lines.append("## Recommendations")
    report_lines.append("")
    report_lines.append("1. **Monitor GameTheory clique** — ShepherdE/Warr Cry/Leuna town share history. ShepherdE already left once.")
    report_lines.append("2. **Track Kylon alts** — Same player, 3 chars. If one is in fleet, all are potentially available.")
    report_lines.append("3. **Watch Kybernauts defectors** — Orbis Bellum and ISDN Ndsi have our intel. Monitor their activity.")
    report_lines.append("4. **Manual zKillboard review** — Check [INIT. Pochven kills](https://zkillboard.com/alliance/99003581/kills/) for new faces.")
    report_lines.append("5. **Cross-reference losses** — Look for YAGAS members losing ships solo. Embarrassment angle.")
    
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("*Report generated by YAGAS Known Associates Tracker (Lightweight)*")
    report_lines.append("*For full browser-based auto-detection, run with Playwright available*")
    
    return "\n".join(report_lines)


def run_associates_tracker():
    """Main entry point."""
    print("[YAGAS Associates Tracker] Starting (lightweight mode)...")
    
    state = load_associates_state()
    
    # Build associations from dossiers
    print("[Step 1] Building associations from dossiers...")
    associations = build_associations_from_dossiers()
    state["associations"] = associations
    print(f"[Step 1] Found {len(associations)} characters with associations")
    
    # Try to detect INIT. Pochven chars (will likely be empty in headless)
    print("[Step 2] Checking for INIT. Pochven operators...")
    init_pochven_chars = fetch_pochven_init_via_zkill_web()
    if init_pochven_chars:
        state["pochven_init_chars"] = init_pochven_chars
        print(f"[Step 2] Found {len(init_pochven_chars)} INIT. characters in Pochven")
    else:
        print("[Step 2] Pochven auto-detection unavailable — flagged for manual review")
    
    # Generate report
    print("[Step 3] Generating report...")
    report = generate_associates_report(state, init_pochven_chars)
    
    now = datetime.now(timezone.utc)
    report_file = REPORTS_DIR / f"{now.strftime('%Y-%m-%d')}_associates_report.md"
    with open(report_file, "w", encoding='utf-8') as f:
        f.write(report)
    print(f"[Step 3] Report saved to {report_file}")
    
    # Update state
    state["last_updated"] = now.isoformat()
    save_associates_state(state)
    
    print(f"[YAGAS Associates Tracker] Complete.")
    return str(report_file)


if __name__ == "__main__":
    run_associates_tracker()
