#!/usr/bin/env python3
"""
YAGAS/INIT Intel Tracker v3
Optimized for speed — resolves names via ESI with shorter timeouts.
"""
import json
import time
import urllib.request
import gzip
from datetime import datetime, timezone
from pathlib import Path

# --- Config ---
REPORTS_DIR = Path("data/kybernauts/intel")
STATE_FILE = REPORTS_DIR / "intel_state.json"
YAGAS_CORP_ID = "98754582"
INIT_ALLIANCE_ID = "99003581"

# zKillboard API config
ZKILL_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "User-Agent": "Nova Intel Tracker (Kybernauts) / Contact: layeredmediallc@gmail.com",
}
ZKILL_DELAY = 2  # Seconds between requests

# Thresholds
HIGH_VALUE_DEATH = 1_000_000_000  # 1B ISK

REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"last_run": None, "known_members": [], "previous_report": None}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def zkill_api_fetch(url):
    """Fetch from zKillboard API with proper headers and rate limiting."""
    time.sleep(ZKILL_DELAY)
    try:
        req = urllib.request.Request(url, headers=ZKILL_HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            if resp.info().get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return json.loads(raw.decode("utf-8", errors="ignore"))
    except urllib.error.HTTPError as e:
        print(f"[WARN] HTTP {e.code} for {url}: {e.reason}")
        return None
    except Exception as e:
        print(f"[WARN] Failed to fetch {url}: {e}")
        return None


def resolve_character_name_fast(char_id):
    """Resolve character ID to name via ESI — fast timeout."""
    if not char_id:
        return "Unknown"
    # Check cache first
    cache_file = REPORTS_DIR / "name_cache.json"
    cache = {}
    if cache_file.exists():
        cache = json.loads(cache_file.read_text(encoding="utf-8"))
    
    if str(char_id) in cache:
        return cache[str(char_id)]
    
    try:
        url = f"https://esi.evetech.net/latest/characters/{char_id}/"
        req = urllib.request.Request(url, headers={"User-Agent": "Nova Intel Tracker"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            name = data.get("name", f"CharID:{char_id}")
            cache[str(char_id)] = name
            cache_file.write_text(json.dumps(cache, indent=2), encoding="utf-8")
            return name
    except Exception:
        return f"CharID:{char_id}"


def resolve_system_name_fast(system_id):
    """Resolve system ID to name via ESI — fast timeout."""
    if not system_id:
        return "Unknown"
    cache_file = REPORTS_DIR / "system_cache.json"
    cache = {}
    if cache_file.exists():
        cache = json.loads(cache_file.read_text(encoding="utf-8"))
    
    if str(system_id) in cache:
        return cache[str(system_id)]
    
    try:
        url = f"https://esi.evetech.net/latest/universe/systems/{system_id}/"
        req = urllib.request.Request(url, headers={"User-Agent": "Nova Intel Tracker"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            name = data.get("name", f"System:{system_id}")
            cache[str(system_id)] = name
            cache_file.write_text(json.dumps(cache, indent=2), encoding="utf-8")
            return name
    except Exception:
        return f"System:{system_id}"


def resolve_ship_name_fast(ship_type_id):
    """Resolve ship type ID to name via ESI — fast timeout."""
    if not ship_type_id:
        return "Unknown Ship"
    cache_file = REPORTS_DIR / "ship_cache.json"
    cache = {}
    if cache_file.exists():
        cache = json.loads(cache_file.read_text(encoding="utf-8"))
    
    if str(ship_type_id) in cache:
        return cache[str(ship_type_id)]
    
    try:
        url = f"https://esi.evetech.net/latest/universe/types/{ship_type_id}/"
        req = urllib.request.Request(url, headers={"User-Agent": "Nova Intel Tracker"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            name = data.get("name", f"ShipType:{ship_type_id}")
            cache[str(ship_type_id)] = name
            cache_file.write_text(json.dumps(cache, indent=2), encoding="utf-8")
            return name
    except Exception:
        return f"ShipType:{ship_type_id}"


def fetch_zkill_recent(corp_id=None, alliance_id=None, seconds=345600):
    """Fetch recent killmails from zKillboard API."""
    kills = []
    losses = []
    
    if corp_id:
        urls = [
            f"https://zkillboard.com/api/corporationID/{corp_id}/kills/pastSeconds/{seconds}/",
            f"https://zkillboard.com/api/corporationID/{corp_id}/losses/pastSeconds/{seconds}/",
        ]
    elif alliance_id:
        urls = [
            f"https://zkillboard.com/api/allianceID/{alliance_id}/kills/pastSeconds/{seconds}/",
            f"https://zkillboard.com/api/allianceID/{alliance_id}/losses/pastSeconds/{seconds}/",
        ]
    else:
        return [], []
    
    for i, url in enumerate(urls):
        print(f"[API] Fetching: {url}")
        data = zkill_api_fetch(url)
        if data and isinstance(data, list):
            if i == 0:
                kills = data
            else:
                losses = data
    
    return kills, losses


def analyze_killmails(kills, losses):
    """Analyze killmails for notable activity with name resolution."""
    high_value_deaths = []
    notable_losses = []
    top_systems = {}
    
    char_ids = set()
    system_ids = set()
    ship_type_ids = set()
    
    for loss in losses:
        if not isinstance(loss, dict):
            continue
        
        victim = loss.get("victim", {})
        total_value = loss.get("zkb", {}).get("totalValue", 0)
        ship_type = victim.get("ship_type_id", "")
        system_id = loss.get("solar_system_id", "")
        character_id = victim.get("character_id")
        
        if character_id:
            char_ids.add(character_id)
        if system_id:
            system_ids.add(system_id)
        if ship_type:
            ship_type_ids.add(ship_type)
        
        if total_value >= HIGH_VALUE_DEATH:
            high_value_deaths.append({
                "character_id": character_id,
                "ship_type_id": ship_type,
                "value": total_value,
                "system_id": system_id,
                "killmail_id": loss.get("killmail_id"),
                "killmail_time": loss.get("killmail_time"),
            })
        
        if total_value >= 100_000_000:
            notable_losses.append({
                "character_id": character_id,
                "ship_type_id": ship_type,
                "value": total_value,
                "system_id": system_id,
                "killmail_id": loss.get("killmail_id"),
                "killmail_time": loss.get("killmail_time"),
            })
        
        if system_id:
            top_systems[system_id] = top_systems.get(system_id, 0) + 1
    
    # Resolve names with fast lookups
    print(f"[Resolve] Resolving {len(char_ids)} chars, {len(system_ids)} systems, {len(ship_type_ids)} ships...")
    char_names = {cid: resolve_character_name_fast(cid) for cid in char_ids}
    system_names = {sid: resolve_system_name_fast(sid) for sid in system_ids}
    ship_names = {sid: resolve_ship_name_fast(sid) for sid in ship_type_ids}
    print("[Resolve] Done")
    
    # Add resolved names
    for death in high_value_deaths:
        death["character_name"] = char_names.get(death["character_id"], f"CharID:{death['character_id']}")
        death["system_name"] = system_names.get(death["system_id"], f"System:{death['system_id']}")
        death["ship_name"] = ship_names.get(death["ship_type_id"], f"ShipType:{death['ship_type_id']}")
    
    for loss in notable_losses:
        loss["character_name"] = char_names.get(loss["character_id"], f"CharID:{loss['character_id']}")
        loss["system_name"] = system_names.get(loss["system_id"], f"System:{loss['system_id']}")
        loss["ship_name"] = ship_names.get(loss["ship_type_id"], f"ShipType:{loss['ship_type_id']}")
    
    for kill in kills:
        if not isinstance(kill, dict):
            continue
        system_id = kill.get("solar_system_id", "")
        if system_id:
            top_systems[system_id] = top_systems.get(system_id, 0) + 1
    
    hotspot_systems = {}
    for sys_id, count in top_systems.items():
        sys_name = system_names.get(sys_id, f"System:{sys_id}")
        hotspot_systems[sys_name] = count
    
    top_systems_sorted = sorted(hotspot_systems.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "high_value_deaths": high_value_deaths,
        "notable_losses": notable_losses,
        "top_systems": top_systems_sorted,
        "total_kills": len(kills),
        "total_losses": len(losses),
    }


def generate_report(state, current_members, analysis, days=4):
    """Generate markdown intel report with resolved names."""
    now = datetime.now(timezone.utc)
    report_date = now.strftime("%Y-%m-%d")
    
    previous_members = set(state.get("known_members", []))
    current_set = set(current_members)
    joined = current_set - previous_members
    left = previous_members - current_set
    
    report_lines = [
        f"# YAGAS/INIT Intel Report — {report_date}",
        "",
        f"**Period:** Last {days} days",
        f"**Generated:** {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Roster Changes",
        "",
    ]
    
    if joined:
        report_lines.append(f"### New Members ({len(joined)})")
        for member in sorted(joined):
            report_lines.append(f"- **{member}** — new join")
        report_lines.append("")
    else:
        report_lines.append("### New Members")
        report_lines.append("- No new joins detected")
        report_lines.append("")
    
    if left:
        report_lines.append(f"### Departures ({len(left)})")
        for member in sorted(left):
            report_lines.append(f"- **{member}** — left corp")
        report_lines.append("")
    else:
        report_lines.append("### Departures")
        report_lines.append("- No departures detected")
        report_lines.append("")
    
    # High-value deaths
    report_lines.append("## High-Value Deaths (>=1B ISK)")
    report_lines.append("")
    
    if analysis["high_value_deaths"]:
        for death in analysis["high_value_deaths"]:
            value_b = death["value"] / 1_000_000_000
            char_name = death.get("character_name", "Unknown")
            system_name = death.get("system_name", "Unknown")
            ship_name = death.get("ship_name", "Unknown Ship")
            report_lines.append(
                f"- **{char_name}** — {value_b:.2f}B ISK lost in **{ship_name}** "
                f"({system_name}) — [zKill](https://zkillboard.com/kill/{death['killmail_id']}/)"
            )
    else:
        report_lines.append("- No high-value deaths in period")
    
    report_lines.append("")
    
    # Notable losses
    report_lines.append("## Notable Losses (>=100M ISK)")
    report_lines.append("")
    
    if analysis["notable_losses"]:
        sorted_losses = sorted(analysis["notable_losses"], key=lambda x: x["value"], reverse=True)[:10]
        for loss in sorted_losses:
            value_m = loss["value"] / 1_000_000
            char_name = loss.get("character_name", "Unknown")
            system_name = loss.get("system_name", "Unknown")
            ship_name = loss.get("ship_name", "Unknown Ship")
            report_lines.append(
                f"- **{char_name}** — {value_m:.0f}M ISK lost in **{ship_name}** "
                f"({system_name}) — [zKill](https://zkillboard.com/kill/{loss['killmail_id']}/)"
            )
    else:
        report_lines.append("- No notable losses in period")
    
    report_lines.append("")
    
    # Activity hotspots
    report_lines.append("## Activity Hotspots")
    report_lines.append("")
    
    if analysis["top_systems"]:
        report_lines.append("| System | Activity Count |")
        report_lines.append("|--------|----------------|")
        for sys_name, count in analysis["top_systems"]:
            report_lines.append(f"| {sys_name} | {count} |")
    else:
        report_lines.append("- No activity detected")
    
    report_lines.append("")
    
    report_lines.append("## Summary")
    report_lines.append("")
    report_lines.append(f"- **Total kills (YAGAS):** {analysis['total_kills']}")
    report_lines.append(f"- **Total losses (YAGAS):** {analysis['total_losses']}")
    report_lines.append(f"- **Current known members:** {len(current_members)}")
    report_lines.append("")
    
    report_lines.append("## Recommendations")
    report_lines.append("")
    
    if analysis["high_value_deaths"]:
        report_lines.append(f"- **Exploit losses:** {len(analysis['high_value_deaths'])} high-value death(s)")
    
    if not any([joined, left, analysis["high_value_deaths"]]):
        report_lines.append("- **Quiet period:** No notable activity")
    
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("*Report generated by YAGAS/INIT Intel Tracker v3*")
    
    return "\n".join(report_lines)


def main():
    print("[YAGAS Intel Tracker v3] Starting...")
    
    state = load_state()
    now = datetime.now(timezone.utc)
    
    # Check if we should run (every 4 days)
    last_run_str = state.get("last_run")
    if last_run_str:
        last_run = datetime.fromisoformat(last_run_str)
        days_since = (now - last_run).days
        if days_since < 4:
            print(f"[YAGAS Intel Tracker] Skipping — last run was {days_since} days ago (need 4)")
            return
    
    print(f"[YAGAS Intel Tracker] Running intel sweep")
    
    # Step 1: Fetch zKillboard data for YAGAS
    print("[Step 1] Fetching zKillboard data for YAGAS...")
    seconds = 345600  # 4 days
    kills, losses = fetch_zkill_recent(corp_id=YAGAS_CORP_ID, seconds=seconds)
    print(f"[Step 1] Found {len(kills)} kills, {len(losses)} losses")
    
    # Step 2: Analyze with name resolution
    print("[Step 2] Analyzing killmails...")
    analysis = analyze_killmails(kills, losses)
    
    # Step 3: Generate report
    print("[Step 3] Generating report...")
    report = generate_report(state, [], analysis, days=4)
    
    report_file = REPORTS_DIR / f"{now.strftime('%Y-%m-%d')}_intel_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[Step 3] Report saved to {report_file}")
    
    # Update state
    state["last_run"] = now.isoformat()
    save_state(state)
    
    print(f"[YAGAS Intel Tracker v3] Complete.")


if __name__ == "__main__":
    main()
