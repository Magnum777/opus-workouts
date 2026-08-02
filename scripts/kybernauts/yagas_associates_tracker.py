#!/usr/bin/env python3
"""
YAGAS Known Associates Tracker
Analyzes killmails to build social network maps of who flies with who.
Also tracks where departed characters went and where new joins came from.
"""
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# --- Config ---
REPORTS_DIR = Path("data/kybernauts/intel")
ASSOCIATES_FILE = REPORTS_DIR / "associates_state.json"
YAGAS_CORP_ID = "98754582"
INIT_ALLIANCE_ID = "99003581"
POCHVEN_REGION_IDS = ["10000070", "10000071", "10000072", "10000073", "10000074", "10000075", "10000076"]  # Pochven region IDs
POCHVEN_SYSTEM_IDS = []  # Will be populated dynamically

# These are the 25 characters we're tracking
TRACKED_CHARS = [
    "True Killjoy", "ShepherdE", "Yuoree", "Zhaturin Lemonseeker", "Ivrae-1",
    "Korkisgod", "Heldrum", "Sir Tikon", "Pigii AkA", "Yzy Andedare",
    "rapthera", "Thanaatos Amatin", "Warr Cry", "K0r3", "Uthreignish",
    "Orbis Bellum", "ISDN Ndsi", "zomg harkonnen", "Leuna town",
    "Kylon Olgidar", "Kylon Muutaras", "Kylon Triplet",
    "Gabriell Bemenacth", "Caleopi", "VpFalcon",
]

# Additional INIT. characters detected in Pochven will be auto-added
POCHVEN_INIT_TRACKED = []  # Dynamically populated

def get_pochven_system_ids():
    """Fetch Pochven system IDs from ESI."""
    import urllib.request
    url = "https://esi.evetech.net/latest/universe/regions/10000070/systems/"
    system_ids = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Nova Intel Tracker"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            system_ids = data
    except Exception:
        # Fallback: known Pochven system IDs
        system_ids = [
            30000142, 30000157, 30001357, 30001433, 30002225, 30002737,
            30002768, 30003504, 30010141, 30010142, 30015001, 30015002,
            30020141, 30020142, 30030141, 30030142, 30040141, 30040142,
            30050141, 30050142, 30060141, 30060142, 30070141, 30070142,
            30080141, 30080142, 30090141, 30090142, 30100141, 30100142,
            30110141, 30110142, 31000001, 31000002, 31000003, 31000004,
            31000005, 31000006, 31000007, 31000008, 31000009, 31000010,
        ]
    return system_ids


def fetch_init_pochven_killmails(days=4):
    """Fetch INIT. killmails in Pochven systems."""
    import urllib.request
    
    pochven_systems = get_pochven_system_ids()
    system_filter = ",".join(map(str, pochven_systems))
    
    # zKillboard API for alliance kills in specific systems
    url = f"https://zkillboard.com/api/alliance/{INIT_ALLIANCE_ID}/kills/pastdays/{days}/"
    
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            # Filter for Pochven systems only
            pochven_kills = []
            for km in data:
                if isinstance(km, dict):
                    system_id = km.get("solar_system_id", 0)
                    if system_id in pochven_systems:
                        pochven_kills.append(km)
            return pochven_kills
    except Exception as e:
        print(f"[WARN] Failed to fetch INIT Pochven killmails: {e}")
        return []


def extract_init_characters_from_killmails(killmails):
    """Extract INIT. character names from killmails."""
    characters = set()
    
    for km in killmails[:50]:  # Limit to avoid rate limits
        killmail_id = km.get("killmail_id")
        hash_value = km.get("zkb", {}).get("hash", "")
        
        if not killmail_id or not hash_value:
            continue
        
        # Fetch full killmail details
        details = fetch_killmail_details(killmail_id, hash_value)
        if not details:
            continue
        
        # Extract attackers from INIT.
        for attacker in details.get("attackers", []):
            corp_id = attacker.get("corporation_id", 0)
            char_id = attacker.get("character_id")
            
            # Check if this is an INIT. member
            # We'd need to check alliance, but zKillboard API already filters by alliance
            if char_id:
                char_name = resolve_character_id(char_id)
                if char_name and not char_name.startswith("CharID:"):
                    characters.add(char_name)
    
    return sorted(characters)

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_associates_state():
    if ASSOCIATES_FILE.exists():
        with open(ASSOCIATES_FILE) as f:
            return json.load(f)
    return {
        "associations": {},  # char -> {other_char: killmail_count}
        "last_updated": None,
        "departure_tracking": {},  # char -> {left_date, went_to, note}
        "arrival_tracking": {},  # char -> {joined_date, came_from, note}
        "movement_history": [],  # list of movement events
    }


def save_associates_state(state):
    with open(ASSOCIATES_FILE, "w") as f:
        json.dump(state, f, indent=2)


def fetch_killmail_details(killmail_id, hash_value):
    """Fetch detailed killmail from ESI."""
    import urllib.request
    import time
    time.sleep(0.5)  # Rate limit protection
    url = f"https://esi.evetech.net/latest/killmails/{killmail_id}/{hash_value}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Nova Intel Tracker"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8", errors="ignore"))
    except Exception as e:
        print(f"[WARN] Failed to fetch killmail {killmail_id}: {e}")
        return None


def analyze_killmail_for_associates(killmail_data, tracked_char):
    """Extract other characters on this killmail with our tracked target."""
    if not killmail_data:
        return []
    
    associates = []
    attackers = killmail_data.get("attackers", [])
    victim = killmail_data.get("victim", {})
    
    # Get all character names on the killmail
    char_names = set()
    
    # Victim
    if "character_id" in victim:
        # We need to resolve character_id to name
        # For now, skip victim since we'd need ESI lookup
        pass
    
    # Attackers
    for attacker in attackers:
        if "character_id" in attacker:
            char_id = attacker["character_id"]
            # We'd need to resolve char_id to name via ESI
            # For now, this is a placeholder — in production we'd cache char_id->name mappings
            pass
    
    return associates


def fetch_zkillboard_page_via_browser(url):
    """Use Playwright browser to fetch zKillboard pages when API is blocked."""
    try:
        import subprocess
        result = subprocess.run(
            ["python", "-c", f"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('{url}', wait_until='networkidle', timeout=30000)
        content = await page.content()
        await browser.close()
        print(content)

asyncio.run(main())
"""],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout
    except Exception as e:
        print(f"[WARN] Browser fetch failed for {url}: {e}")
        return None


def fetch_zkillboard_sync(url):
    """Synchronous wrapper for browser fetch."""
    import time
    time.sleep(3)  # Delay between browser requests
    return fetch_zkillboard_page_via_browser(url)


def parse_killmail_list_from_html(html):
    """Parse killmail list from zKillboard HTML."""
    import re
    killmails = []
    
    # zKillboard killmail rows have data-killid attributes
    for match in re.finditer(r'data-killid="(\d+)"', html):
        killmail_id = match.group(1)
        killmails.append({"killmail_id": int(killmail_id)})
    
    # Also extract from table rows
    for match in re.finditer(r'<tr[^>]*data-killid="(\d+)"[^>]*>.*?<td[^>]*class="[^"]*kill[^"]*"[^>]*>.*?<a[^>]*href="/kill/(\d+)/"[^>]*>.*?(\d{4}-\d{2}-\d{2})', html, re.DOTALL):
        killmail_id = int(match.group(1))
        killmails.append({
            "killmail_id": killmail_id,
            "killmail_time": match.group(3)
        })
    
    return killmails


def parse_character_id_from_html(html, char_name):
    """Parse character ID from zKillboard search results HTML."""
    import re
    # Look for character links in search results
    for match in re.finditer(r'<a[^>]*href="/character/(\d+)/"[^>]*>([^<]+)</a>', html):
        found_name = match.group(2).strip()
        if found_name.lower() == char_name.lower():
            return int(match.group(1))
    return None


def fetch_recent_killmails_zkill(char_name, days=30):
    """Fetch recent killmails for a character from zKillboard via browser."""
    # Step 1: Search for character
    search_url = f"https://zkillboard.com/search/{char_name.replace(' ', '%20')}/"
    search_html = fetch_zkillboard_sync(search_url)
    
    if not search_html:
        print(f"[WARN] Failed to search for {char_name}")
        return []
    
    char_id = parse_character_id_from_html(search_html, char_name)
    if not char_id:
        print(f"[WARN] Could not find character ID for {char_name}")
        return []
    
    print(f"[INFO] Found character ID for {char_name}: {char_id}")
    
    # Step 2: Fetch kills page
    kills_url = f"https://zkillboard.com/character/{char_id}/kills/"
    kills_html = fetch_zkillboard_sync(kills_url)
    kills = parse_killmail_list_from_html(kills_html) if kills_html else []
    
    # Step 3: Fetch losses page
    losses_url = f"https://zkillboard.com/character/{char_id}/losses/"
    losses_html = fetch_zkillboard_sync(losses_url)
    losses = parse_killmail_list_from_html(losses_html) if losses_html else []
    
    print(f"[INFO] {char_name}: {len(kills)} kills, {len(losses)} losses found via browser")
    
    return kills + losses


def resolve_character_id(char_id):
    """Resolve a character ID to name via ESI."""
    import urllib.request
    url = f"https://esi.evetech.net/latest/characters/{char_id}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Nova Intel Tracker"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            return data.get("name", f"CharID:{char_id}")
    except Exception:
        return f"CharID:{char_id}"


def get_pochven_system_ids():
    """Fetch Pochven system IDs from ESI."""
    import urllib.request
    # Pochven constellation IDs
    constellation_ids = [
        21000001, 21000002, 21000003, 21000004, 21000005, 21000006,
        21000007, 21000008, 21000009, 21000010, 21000011, 21000012,
    ]
    system_ids = []
    for constellation_id in constellation_ids:
        url = f"https://esi.evetech.net/latest/universe/constellations/{constellation_id}/"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Nova Intel Tracker"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                system_ids.extend(data.get("systems", []))
        except Exception:
            pass
    return system_ids if system_ids else [30000142, 30001357, 30002768, 30003504, 31000001]


def fetch_init_pochven_killmails(days=4):
    """Fetch INIT. killmails in Pochven systems."""
    import urllib.request
    
    pochven_systems = get_pochven_system_ids()
    
    # zKillboard API for alliance kills
    url = f"https://zkillboard.com/api/alliance/{INIT_ALLIANCE_ID}/kills/pastdays/{days}/"
    
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            # Filter for Pochven systems
            pochven_kills = []
            for km in data:
                if isinstance(km, dict):
                    system_id = km.get("solar_system_id", 0)
                    if system_id in pochven_systems:
                        pochven_kills.append(km)
            return pochven_kills
    except Exception as e:
        print(f"[WARN] Failed to fetch INIT Pochven killmails: {e}")
        return []


def extract_init_characters_from_killmails(killmails):
    """Extract INIT. character names from killmails."""
    characters = set()
    
    for km in killmails[:50]:
        killmail_id = km.get("killmail_id")
        hash_value = km.get("zkb", {}).get("hash", "")
        
        if not killmail_id or not hash_value:
            continue
        
        details = fetch_killmail_details(killmail_id, hash_value)
        if not details:
            continue
        
        for attacker in details.get("attackers", []):
            char_id = attacker.get("character_id")
            if char_id:
                char_name = resolve_character_id(char_id)
                if char_name and not char_name.startswith("CharID:"):
                    characters.add(char_name)
    
    return sorted(characters)


def build_associations_for_character(char_name, days=30):
    """Build association map for a single tracked character."""
    print(f"[Associates] Analyzing {char_name}...")
    
    killmails = fetch_recent_killmails_zkill(char_name, days)
    if not killmails:
        print(f"[Associates] No killmails found for {char_name}")
        return {}
    
    associations = defaultdict(int)
    
    for km in killmails[:20]:  # Limit to recent 20 to avoid rate limits
        killmail_id = km.get("killmail_id")
        hash_value = km.get("zkb", {}).get("hash", "")
        
        if not killmail_id or not hash_value:
            continue
        
        # Fetch full killmail details from ESI
        details = fetch_killmail_details(killmail_id, hash_value)
        if not details:
            continue
        
        # Extract all attacker character IDs
        attacker_ids = set()
        for attacker in details.get("attackers", []):
            char_id = attacker.get("character_id")
            if char_id:
                attacker_ids.add(char_id)
        
        # Victim character ID
        victim_char_id = details.get("victim", {}).get("character_id")
        if victim_char_id:
            attacker_ids.add(victim_char_id)
        
        # Resolve to names and check against tracked list
        for char_id in attacker_ids:
            resolved_name = resolve_character_id(char_id)
            if resolved_name != char_name and resolved_name in TRACKED_CHARS:
                associations[resolved_name] += 1
    
    return dict(associations)


def track_character_movements(state):
    """Check tracked characters for corp movements using EVEWho."""
    print("[Associates] Tracking character movements...")
    
    movements = []
    
    for char_name in TRACKED_CHARS:
        import urllib.request
        evewho_url = f"https://evewho.com/pilot/{char_name.replace(' ', '%20')}"
        
        try:
            req = urllib.request.Request(
                evewho_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                
                # Extract current corp from page
                # This is heuristic — EVEWho pages have corp info
                corp_match = __import__("re").search(r'corporation[^\u003e]*\u003e([^\u003c]+)\u003c', html)
                current_corp = corp_match.group(1).strip() if corp_match else "Unknown"
                
                # Check if this is a change from what we knew
                prev_corp = state.get("departure_tracking", {}).get(char_name, {}).get("last_known_corp")
                
                if prev_corp and prev_corp != current_corp and current_corp != "Unknown":
                    movement = {
                        "character": char_name,
                        "from": prev_corp,
                        "to": current_corp,
                        "date": datetime.utcnow().isoformat(),
                        "type": "movement",
                    }
                    movements.append(movement)
                    state["movement_history"].append(movement)
                    
                    # Update tracking
                    state["departure_tracking"][char_name] = {
                        "left_date": datetime.utcnow().isoformat(),
                        "went_to": current_corp,
                        "last_known_corp": current_corp,
                    }
                    
                    print(f"[Associates] MOVEMENT: {char_name} moved from {prev_corp} to {current_corp}")
                else:
                    # Update last known corp
                    if char_name not in state["departure_tracking"]:
                        state["departure_tracking"][char_name] = {}
                    state["departure_tracking"][char_name]["last_known_corp"] = current_corp
                    
        except Exception as e:
            print(f"[WARN] Failed to track {char_name}: {e}")
    
    return movements


def generate_associates_report(state, new_movements, init_pochven_chars=None):
    """Generate markdown associates report."""
    now = datetime.utcnow()
    report_date = now.strftime("%Y-%m-%d")
    
    report_lines = [
        f"# YAGAS Known Associates Report — {report_date}",
        "",
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
    ]
    
    # INIT. Pochven operators section
    if init_pochven_chars:
        report_lines.append("## INIT. Characters Active in Pochven (Auto-Detected)")
        report_lines.append("")
        report_lines.append(f"**{len(init_pochven_chars)} INIT. character(s)** detected in Pochven systems (last 4 days):")
        report_lines.append("")
        for char_name in init_pochven_chars[:30]:
            report_lines.append(f"- {char_name}")
        if len(init_pochven_chars) > 30:
            report_lines.append(f"- ... and {len(init_pochven_chars) - 30} more")
        report_lines.append("")
    else:
        report_lines.append("## INIT. Characters Active in Pochven")
        report_lines.append("")
        report_lines.append("- No INIT. characters detected in Pochven (API blocked or no activity)")
        report_lines.append("")
    
    # Character associations
    report_lines.append("## Character Associations (Killmail Co-Presence)")
    report_lines.append("")
    report_lines.append("Characters who appear on killmails together frequently.")
    report_lines.append("")
    
    if state.get("associations"):
        report_lines.append("| Character | Associates (shared killmails) |")
        report_lines.append("|-----------|------------------------------|")
        
        for char_name in sorted(state["associations"].keys()):
            associates = state["associations"][char_name]
            if associates:
                assoc_str = ", ".join([f"{name} ({count})" for name, count in sorted(associates.items(), key=lambda x: -x[1])[:5]])
                report_lines.append(f"| {char_name} | {assoc_str} |")
            else:
                report_lines.append(f"| {char_name} | No tracked associates |")
    else:
        report_lines.append("*No association data collected yet. zKillboard API may be rate-limiting.*")
    
    report_lines.append("")
    
    # Movement tracking
    report_lines.append("## Recent Character Movements")
    report_lines.append("")
    
    if new_movements:
        report_lines.append(f"**{len(new_movements)} new movement(s) detected:**")
        report_lines.append("")
        for movement in new_movements:
            report_lines.append(
                f"- **{movement['character']}** moved from **{movement['from']}** → **{movement['to']}** "
                f"({movement['date'][:10]})"
            )
    else:
        report_lines.append("- No new movements detected since last run")
    
    report_lines.append("")
    
    # Full movement history
    recent_movements = [m for m in state.get("movement_history", [])
                       if datetime.fromisoformat(m["date"]).replace(tzinfo=None) <= now and
                       (now - datetime.fromisoformat(m["date"]).replace(tzinfo=None)).days <= 30]
    
    if recent_movements:
        report_lines.append("### Movement History (Last 30 Days)")
        report_lines.append("")
        for movement in recent_movements[-10:]:
            report_lines.append(
                f"- {movement['date'][:10]}: {movement['character']} → {movement['to']}"
            )
    
    report_lines.append("")
    report_lines.append("## Key Cliques/Networks")
    report_lines.append("")
    
    # Identify cliques
    cliques = []
    for char_name, associates in state.get("associations", {}).items():
        if len(associates) >= 2:
            clique = set([char_name] + list(associates.keys()))
            if len(clique) >= 3:
                cliques.append(clique)
    
    if cliques:
        seen = set()
        for clique in cliques:
            clique_key = frozenset(clique)
            if clique_key not in seen:
                seen.add(clique_key)
                report_lines.append(f"- **{' / '.join(sorted(clique))}** — frequent co-presence on killmails")
    else:
        report_lines.append("- No strong cliques identified yet")
    
    report_lines.append("")
    report_lines.append("## Recommendations")
    report_lines.append("")
    
    if init_pochven_chars:
        report_lines.append(f"- **{len(init_pochven_chars)} INIT. Pochven operators detected** — prioritize for dossier building")
    
    if new_movements:
        report_lines.append("- **Investigate new movements:** Track departed characters — where did they go? Why?")
    
    if cliques:
        report_lines.append("- **Target cliques:** Groups that fly together can be separated. Hit one, the others respond.")
    
    report_lines.append("- **Monitor known associates:** Characters with high co-presence likely share FC/schedule. Exploit timing.")
    
    if not init_pochven_chars and not new_movements and not cliques:
        report_lines.append("- **API limitations:** zKillboard/EVEWho may be rate-limiting. Consider manual killmail review or alternative data sources.")
    
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("*Report generated by YAGAS Known Associates Tracker*")
    
    return "\n".join(report_lines)


def run_associates_tracker(days=30):
    """Main entry point."""
    print("[YAGAS Associates Tracker] Starting...")
    
    state = load_associates_state()
    
    # Step 1: Fetch INIT. characters active in Pochven
    print("[Step 0] Fetching INIT. Pochven operators...")
    pochven_kills = fetch_init_pochven_killmails(days=4)
    init_pochven_chars = extract_init_characters_from_killmails(pochven_kills)
    print(f"[Step 0] Found {len(init_pochven_chars)} INIT. characters in Pochven")
    
    # Update tracked list
    global TRACKED_CHARS
    for char_name in init_pochven_chars:
        if char_name not in TRACKED_CHARS:
            TRACKED_CHARS.append(char_name)
            print(f"[Step 0] Auto-added: {char_name}")
    
    # Step 2: Build associations for tracked characters
    all_associations = {}
    for char_name in TRACKED_CHARS:
        associations = build_associations_for_character(char_name, days)
        if associations:
            all_associations[char_name] = associations
            print(f"[Associates] {char_name}: {len(associations)} associate(s)")
        else:
            print(f"[Associates] {char_name}: No associations found")
    
    # Merge with existing state
    if state.get("associations"):
        for char_name, new_associations in all_associations.items():
            if char_name not in state["associations"]:
                state["associations"][char_name] = {}
            for assoc_name, count in new_associations.items():
                state["associations"][char_name][assoc_name] = (
                    state["associations"][char_name].get(assoc_name, 0) + count
                )
    else:
        state["associations"] = all_associations
    
    # Track movements
    new_movements = track_character_movements(state)
    
    # Generate report
    report = generate_associates_report(state, new_movements, init_pochven_chars)
    
    now = datetime.utcnow()
    report_file = REPORTS_DIR / f"{now.strftime('%Y-%m-%d')}_associates_report.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"[Associates] Report saved to {report_file}")
    
    # Update state
    state["last_updated"] = now.isoformat()
    save_associates_state(state)
    
    print(f"[YAGAS Associates Tracker] Complete. Associations: {len(all_associations)}, Movements: {len(new_movements)}, INIT Pochven: {len(init_pochven_chars)}")
    return str(report_file)


if __name__ == "__main__":
    run_associates_tracker()
