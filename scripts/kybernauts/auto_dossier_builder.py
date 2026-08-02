#!/usr/bin/env python3
"""
YAGAS Auto-Dossier Builder
Runs every 4 days as part of AntiYagas-Phase1-Daily cron.
Reads intel reports, finds new character IDs, resolves names, builds dossiers.
"""
import json
import time
import urllib.request
import gzip
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# --- Config ---
REPORTS_DIR = Path("data/kybernauts/intel")
INTEL_JSON_DIR = Path("data/kybernauts/yagas_intel")
DOSSIERS_DIR = Path("data/kybernauts/dossiers")
STATE_FILE = REPORTS_DIR / "auto_dossier_state.json"
YAGAS_CORP_ID = "98754582"

# zKillboard API config
ZKILL_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "User-Agent": "Nova Auto-Dossier Builder (Kybernauts) / Contact: layeredmediallc@gmail.com",
}
ZKILL_DELAY = 2

DOSSIERS_DIR.mkdir(parents=True, exist_ok=True)


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            state = json.load(f)
        # Ensure all expected keys exist (handles legacy state files)
        state.setdefault("built_dossiers", [])
        state.setdefault("tracked_char_ids", [])
        state.setdefault("last_run", None)
        return state
    return {
        "last_run": None,
        "built_dossiers": [],
        "tracked_char_ids": [],
    }


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def zkill_api_fetch(url):
    """Fetch from zKillboard API."""
    time.sleep(ZKILL_DELAY)
    try:
        req = urllib.request.Request(url, headers=ZKILL_HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            if resp.info().get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return json.loads(raw.decode("utf-8", errors="ignore"))
    except Exception as e:
        print(f"[WARN] Failed to fetch {url}: {e}")
        return None


def resolve_character_name(char_id):
    """Resolve character ID to name via ESI."""
    if not char_id:
        return "Unknown"
    cache_file = REPORTS_DIR / "name_cache.json"
    cache = {}
    if cache_file.exists():
        cache = json.loads(cache_file.read_text(encoding="utf-8"))
    
    if str(char_id) in cache:
        return cache[str(char_id)]
    
    try:
        url = f"https://esi.evetech.net/latest/characters/{char_id}/"
        req = urllib.request.Request(url, headers={"User-Agent": "Nova Auto-Dossier Builder"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            name = data.get("name", f"CharID:{char_id}")
            cache[str(char_id)] = name
            cache_file.write_text(json.dumps(cache, indent=2), encoding="utf-8")
            return name
    except Exception:
        return f"CharID:{char_id}"


def fetch_character_zkill_summary(char_name):
    """Fetch character summary from zKillboard."""
    # Search for character ID first
    search_url = f"https://zkillboard.com/api/search/{char_name.replace(' ', '%20')}/"
    search_data = zkill_api_fetch(search_url)
    
    if not search_data or not isinstance(search_data, list):
        return None
    
    char_id = None
    for result in search_data:
        if result.get("category") == "character":
            char_id = result.get("id")
            break
    
    if not char_id:
        return None
    
    # Fetch stats
    stats_url = f"https://zkillboard.com/api/stats/characterID/{char_id}/"
    stats = zkill_api_fetch(stats_url)
    
    return {
        "char_id": char_id,
        "char_name": char_name,
        "stats": stats,
    }


def fetch_evewho_data(char_id):
    """Fetch character data from EVEWho API."""
    if not char_id or char_id == "Unknown":
        return {"birth_date": "Unknown", "current_corp": "Unknown", "corp_history": []}

    url = f"https://evewho.com/api/character/{char_id}"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Nova Auto-Dossier Builder (Kybernauts) / Contact: layeredmediallc@gmail.com",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))

        info = data.get("info", {})
        history = data.get("history", [])

        # Extract corp history (newest first)
        corp_history = []
        for entry in history[:5]:
            corp_name = entry.get("corporation_name", "Unknown")
            start_date = entry.get("start_date", "")[:10]  # YYYY-MM-DD
            corp_history.append(f"{corp_name} (from {start_date})")

        return {
            "birth_date": info.get("birthday", "Unknown")[:10] if info.get("birthday") else "Unknown",
            "current_corp": info.get("corporation_name", "Unknown"),
            "current_alliance": info.get("alliance_name", ""),
            "security_status": info.get("security_status", 0.0),
            "corp_history": corp_history,
        }
    except Exception as e:
        print(f"[WARN] Failed to fetch EVEWho for char_id {char_id}: {e}")
        return {"birth_date": "Unknown", "current_corp": "Unknown", "corp_history": []}


def generate_dossier(char_name, char_id, zkill_data, evewho_data):
    """Generate a dossier markdown file."""
    stats = zkill_data.get("stats", {}) if zkill_data else {}
    
    # Extract stats
    ships_destroyed = stats.get("shipsDestroyed", 0) if stats else 0
    ships_lost = stats.get("shipsLost", 0) if stats else 0
    isk_destroyed = stats.get("iskDestroyed", 0) if stats else 0
    isk_lost = stats.get("iskLost", 0) if stats else 0
    efficiency = stats.get("efficiency", 0) if stats else 0
    
    # Top ships
    top_ships = []
    if stats and "topLists" in stats:
        for top_list in stats["topLists"]:
            if top_list.get("type") == "ship":
                for item in top_list.get("values", [])[:5]:
                    top_ships.append(f"{item.get('shipName', 'Unknown')} ({item.get('kills', 0)} kills)")
    
    # Solo ratio
    solo_kills = stats.get("soloKills", 0) if stats else 0
    total_kills = ships_destroyed
    solo_ratio = (solo_kills / total_kills * 100) if total_kills > 0 else 0
    
    now = datetime.now(timezone.utc)
    
    content = f"""# Dossier: {char_name}

## Basic Info
- **Character Name:** {char_name}
- **Character ID:** {char_id}
- **Current Corp:** {evewho_data.get('current_corp', 'Unknown')}
- **Alliance:** The Initiative. [INIT.]
- **Birth Date:** {evewho_data.get('birth_date', 'Unknown')}
- **Generated:** {now.strftime('%Y-%m-%d')}

## Kill/Loss Summary (zKillboard)
- **Total Kills:** {ships_destroyed:,}
- **Total Losses:** {ships_lost:,}
- **ISK Destroyed:** {isk_destroyed / 1_000_000_000:.2f}B ISK
- **ISK Lost:** {isk_lost / 1_000_000_000:.2f}B ISK
- **Efficiency:** {efficiency:.1f}%
- **Solo Kills:** {solo_kills:,} ({solo_ratio:.0f}% solo ratio)

## Top Ships
{"- " + "\\n- ".join(top_ships) if top_ships else "- No ship data available"}

## Activity Patterns
- **Primary Timezone:** Unknown (requires manual analysis)
- **Solo vs Gang:** {"Solo specialist" if solo_ratio > 20 else "Fleet-dependent" if solo_ratio < 5 else "Mixed"}

## Assessment
- **Threat Level:** {"5/5 — High solo capability, dangerous" if solo_ratio > 20 else "3/5 — Fleet warrior, separate from blob to neutralize" if solo_ratio < 5 else "4/5 — Moderate solo, mainly fleet"}
- **Propaganda Angle:** {generate_propaganda_angle(char_name, stats)}

---
*Auto-generated by YAGAS Auto-Dossier Builder*
*Verify data before use — zKillboard stats may be incomplete*
"""
    return content


def generate_propaganda_angle(char_name, stats):
    """Generate a suggested propaganda angle."""
    if not stats:
        return "No data — manual research needed"
    
    ships_destroyed = stats.get("shipsDestroyed", 0)
    ships_lost = stats.get("shipsLost", 0)
    efficiency = stats.get("efficiency", 0)
    solo_kills = stats.get("soloKills", 0)
    
    if efficiency < 50:
        return f"Low efficiency ({efficiency:.0f}%) — loses more than they kill"
    elif ships_lost > 1000:
        return f"Feeder — {ships_lost:,} losses, dies frequently"
    elif solo_kills > 100:
        return f"Solo threat — {solo_kills:,} solo kills, dangerous alone"
    else:
        return "Standard fleet member — no obvious angle yet"


def update_index(char_name, char_id):
    """Update the dossier INDEX.md with new entry."""
    index_path = DOSSIERS_DIR / "INDEX.md"
    
    entry = f"| [{char_name}]({char_name.replace(' ', '_')}.md) | Auto-detected | CharID:{char_id} | New | ⚠️⚠️⚠️ |\n"
    
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        if char_name not in content:
            # Find the Individual Dossiers section and append
            lines = content.split("\n")
            new_lines = []
            inserted = False
            for line in lines:
                new_lines.append(line)
                if "## Individual Dossiers" in line and not inserted:
                    new_lines.append("")
                    new_lines.append("### Auto-Detected (from zKillboard scan)")
                    new_lines.append("| Character | Role | ID | Status | Threat |")
                    new_lines.append("|-----------|------|-----|--------|--------|")
                    inserted = True
            
            # Find the auto-detected table and add entry
            content = "\n".join(new_lines)
            # Simple append for now
            with open(index_path, "a", encoding="utf-8") as f:
                f.write(f"\n{entry}")
    
    print(f"[Index] Updated with {char_name}")


def find_new_characters_from_intel():
    """Find character names from latest intel report that don't have dossiers."""
    # Try new JSON format first
    latest_json = INTEL_JSON_DIR / "latest.json"
    if latest_json.exists():
        print(f"[Auto-Dossier] Reading {latest_json}")
        data = json.loads(latest_json.read_text(encoding="utf-8"))
        
        # Extract character IDs from zKill stats topAllTime
        zkill_stats = data.get("zkill_stats", {})
        top_chars = zkill_stats.get("topAllTime", [])
        char_entries = []
        for entry in top_chars:
            if entry.get("type") == "character":
                for char_data in entry.get("data", [])[:20]:  # Top 20 killers
                    char_id = char_data.get("characterID")
                    if char_id:
                        char_entries.append(str(char_id))
        
        # Resolve names
        char_names = []
        for char_id in char_entries:
            name = resolve_character_name(int(char_id))
            if name and not name.startswith("CharID:"):
                char_names.append(name)
        
        print(f"[Auto-Dossier] Found {len(char_names)} characters from JSON intel")
        return sorted(set(char_names))
    
    # Fallback to old markdown reports
    reports = sorted(REPORTS_DIR.glob("*_intel_report.md"))
    if not reports:
        print("[Auto-Dossier] No intel reports found")
        return []
    
    latest_report = reports[-1]
    print(f"[Auto-Dossier] Reading {latest_report}")
    
    content = latest_report.read_text(encoding="utf-8")
    
    # Extract character names from the report
    import re
    char_names = set()
    
    # Match resolved names in high-value deaths
    for match in re.finditer(r'\*\*([^*]+)\*\*\s*—\s*[\d.]+B ISK lost', content):
        char_name = match.group(1).strip()
        if char_name and not char_name.startswith("CharID:"):
            char_names.add(char_name)
    
    # Also match notable losses
    for match in re.finditer(r'\*\*([^*]+)\*\*\s*—\s*[\d.]+M ISK lost', content):
        char_name = match.group(1).strip()
        if char_name and not char_name.startswith("CharID:"):
            char_names.add(char_name)
    
    print(f"[Auto-Dossier] Found {len(char_names)} unique character names from markdown")
    return sorted(char_names)


def check_dossier_exists(char_name):
    """Check if a dossier already exists for this character."""
    dossier_path = DOSSIERS_DIR / f"{char_name.replace(' ', '_')}.md"
    return dossier_path.exists()


def main():
    print("[YAGAS Auto-Dossier Builder] Starting...")
    
    state = load_state()
    now = datetime.now(timezone.utc)
    
    # Check if we should run (every 4 days)
    last_run_str = state.get("last_run")
    if last_run_str:
        last_run = datetime.fromisoformat(last_run_str)
        days_since = (now - last_run).days
        if days_since < 4:
            print(f"[Auto-Dossier] Skipping — last run was {days_since} days ago (need 4)")
            return
    
    print(f"[Auto-Dossier] Running auto-dossier build")
    
    # Step 1: Find new characters from intel reports
    print("[Step 1] Finding new characters from intel reports...")
    char_ids = find_new_characters_from_intel()
    
    if not char_ids:
        print("[Auto-Dossier] No new characters found")
        state["last_run"] = now.isoformat()
        save_state(state)
        return
    
    # Step 2: Build dossiers
    char_names = find_new_characters_from_intel()
    print(f"[Step 2] Building dossiers for {len(char_names)} characters...")
    built = 0
    skipped = 0
    
    for char_name in char_names:
        if check_dossier_exists(char_name):
            print(f"[Skip] Dossier already exists for {char_name}")
            skipped += 1
            continue
        
        print(f"[Build] Building dossier for {char_name}...")
        
        # Fetch zKillboard data (search by name)
        zkill_data = fetch_character_zkill_summary(char_name)
        
        # Get char_id from zkill data
        char_id = zkill_data.get("char_id", "Unknown") if zkill_data else "Unknown"
        
        # Fetch EVEWho data (uses char_id for API lookup)
        evewho_data = fetch_evewho_data(char_id if char_id != "Unknown" else None)
        
        # Generate dossier
        dossier_content = generate_dossier(char_name, char_id, zkill_data, evewho_data)
        
        # Save dossier
        dossier_path = DOSSIERS_DIR / f"{char_name.replace(' ', '_')}.md"
        with open(dossier_path, "w", encoding="utf-8") as f:
            f.write(dossier_content)
        print(f"[Build] Saved dossier: {dossier_path}")
        
        # Update index
        update_index(char_name, char_id)
        
        # Track in state
        state["built_dossiers"].append({
            "char_name": char_name,
            "char_id": char_id,
            "built_date": now.isoformat(),
        })
        if char_id != "Unknown":
            state["tracked_char_ids"].append(char_id)
        
        built += 1
        time.sleep(2)  # Rate limit between builds
    
    print(f"[Auto-Dossier] Complete: {built} built, {skipped} skipped")
    
    # Update state
    state["last_run"] = now.isoformat()
    save_state(state)


if __name__ == "__main__":
    main()
