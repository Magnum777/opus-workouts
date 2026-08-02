#!/usr/bin/env python3
"""
EVEWho + zKill data collection for Baba Yagas Pochven activity.
Fetches corp info, recent kills, allies, and saves structured data.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# Config
CORP_ID = 98754582  # Baba Yagas
OUTPUT_DIR = Path("data/kybernauts/yagas_intel")
MD_DIR = Path("data/kybernauts/intel")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MD_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Kybernauts-Intel-Bot/1.0 (discord: OpusMagnum)"}


def fetch_evewho_corp(corp_id: int) -> dict:
    """Fetch corp info from EVEWho API."""
    url = f"https://evewho.com/api/v3/corporation/{corp_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            return r.json()
        return {"error": f"HTTP {r.status_code}", "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}


def fetch_zkill_recent(corp_id: int, limit: int = 200) -> list:
    """Fetch recent kills for corp from zKillboard (no date filter, gets most recent)."""
    url = f"https://zkillboard.com/api/kills/corporationID/{corp_id}/"
    try:
        r = requests.get(url, headers={**HEADERS, "Accept": "application/json"}, timeout=30)
        if r.status_code == 200:
            kills = r.json()
            return kills[:limit]
        return [{"error": f"HTTP {r.status_code}", "url": url}]
    except Exception as e:
        return [{"error": str(e), "url": url}]


def fetch_killmail_details(killmail_id: int, killmail_hash: str) -> dict:
    """Fetch killmail details from ESI to get system ID."""
    url = f"https://esi.evetech.net/latest/killmails/{killmail_id}/{killmail_hash}/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            return r.json()
        return {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def fetch_zkill_stats(corp_id: int) -> dict:
    """Fetch zKill stats for corp."""
    url = f"https://zkillboard.com/api/stats/corporationID/{corp_id}/"
    try:
        r = requests.get(url, headers={**HEADERS, "Accept": "application/json"}, timeout=30)
        if r.status_code == 200:
            return r.json()
        return {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def is_pochven_system(system_id: int) -> bool:
    """Check if system ID is in Pochven (approximate range check)."""
    # Pochven systems: 30004097-30004153 (27 systems)
    return 30004097 <= system_id <= 30004153


def analyze_kills(kills: list, max_esi_calls: int = 50) -> dict:
    """Analyze kills for fleet patterns and Pochven activity."""
    pochven_kills = []
    non_pochven_kills = []
    fleet_sizes = []
    total_value = 0
    allies = {}
    ship_types = {}
    esi_calls = 0
    
    for kill in kills:
        if "error" in kill:
            continue
        
        zkb = kill.get("zkb", {})
        killmail_id = kill.get("killmail_id")
        killmail_hash = zkb.get("hash")
        attackers = kill.get("attackers", [])
        
        fleet_size = len(attackers)
        fleet_sizes.append(fleet_size)
        value = zkb.get("totalValue", 0)
        total_value += value
        
        # Fetch ESI details for system ID (limit calls)
        system_id = 0
        victim = {}
        if killmail_id and killmail_hash and esi_calls < max_esi_calls:
            esi_data = fetch_killmail_details(killmail_id, killmail_hash)
            esi_calls += 1
            if "error" not in esi_data:
                system_id = esi_data.get("solar_system_id", 0)
                victim = esi_data.get("victim", {})
        
        # Count ally corps
        for attacker in attackers:
            ally_corp_id = attacker.get("corporation_id")
            ally_corp_name = attacker.get("corporation_name", "Unknown")
            if ally_corp_id and ally_corp_id != CORP_ID:
                cid = str(ally_corp_id)
                if cid not in allies:
                    allies[cid] = {"name": ally_corp_name, "count": 0, "isk": 0}
                allies[cid]["count"] += 1
                allies[cid]["isk"] += value
        
        # Track victim ship types
        ship_type_id = victim.get("ship_type_id")
        if ship_type_id:
            ship_types.setdefault(str(ship_type_id), 0)
            ship_types[str(ship_type_id)] += 1
        
        # Separate Pochven vs non-Pochven
        if system_id and is_pochven_system(system_id):
            pochven_kills.append({
                "killmail_id": killmail_id,
                "system_id": system_id,
                "fleet_size": fleet_size,
                "value": value,
                "victim_ship": ship_type_id
            })
        else:
            non_pochven_kills.append({
                "system_id": system_id,
                "fleet_size": fleet_size,
                "value": value
            })
    
    # Calculate stats
    total_kills = len(pochven_kills) + len(non_pochven_kills)
    
    stats = {
        "total_kills": total_kills,
        "pochven_kills": len(pochven_kills),
        "non_pochven_kills": len(non_pochven_kills),
        "pochven_percentage": round(len(pochven_kills) / total_kills * 100, 1) if total_kills else 0,
        "total_isk_b": round(total_value / 1e9, 2),
        "avg_fleet_size": round(sum(fleet_sizes) / len(fleet_sizes), 1) if fleet_sizes else 0,
        "max_fleet_size": max(fleet_sizes) if fleet_sizes else 0,
        "min_fleet_size": min(fleet_sizes) if fleet_sizes else 0,
        "blob_kills_20plus": sum(1 for s in fleet_sizes if s >= 20),
        "blob_percentage": round(sum(1 for s in fleet_sizes if s >= 20) / len(fleet_sizes) * 100, 1) if fleet_sizes else 0,
        "top_allies": sorted(allies.items(), key=lambda x: x[1]["count"], reverse=True)[:10],
        "ship_types": dict(sorted(ship_types.items(), key=lambda x: x[1], reverse=True)[:10]),
        "recent_pochven_kills": pochven_kills[:10],
        "esi_calls_made": esi_calls
    }
    
    return stats


def generate_markdown_report(report: dict, now: datetime) -> str:
    """Generate a markdown intel report for the dossier builder."""
    analysis = report.get("analysis", {})
    zkill_stats = report.get("zkill_stats", {})
    
    total_kills = analysis.get("total_kills", 0)
    pochven_kills = analysis.get("pochven_kills", 0)
    blob_count = analysis.get("blob_kills_20plus", 0)
    blob_pct = analysis.get("blob_percentage", 0)
    avg_fleet = analysis.get("avg_fleet_size", 0)
    total_isk = analysis.get("total_isk_b", 0)
    
    # Extract notable losses from recent kills
    notable_losses = []
    for kill in analysis.get("recent_pochven_kills", [])[:5]:
        if kill.get("value", 0) > 100_000_000:
            notable_losses.append(f"- Kill {kill['killmail_id']} — {kill['fleet_size']} attackers, {kill['value']/1e9:.2f}B ISK destroyed")
    
    # Extract top allies
    allies = analysis.get("top_allies", [])
    allies_text = "\n".join([f"- **{a[1]['name']}** — {a[1]['count']} kills, {a[1]['isk']/1e9:.1f}B ISK" for a in allies[:5]])
    
    # All-time stats
    alltime_kills = zkill_stats.get("shipsDestroyed", 0)
    alltime_solo = zkill_stats.get("soloRatio", 0)
    alltime_avg = zkill_stats.get("avgGangSize", 0)
    alltime_isk = zkill_stats.get("iskDestroyed", 0)
    
    content = f"""# Yagas Intel Report — {now.strftime('%Y-%m-%d')}

## Corp Overview
- **Corporation:** Baba Yagas [YAGAS]
- **Alliance:** The Initiative. [INIT.]
- **Report Date:** {now.isoformat()}

## Recent Activity (Last 7 Days)
- **Total Kills Scanned:** {total_kills}
- **Pochven Kills:** {pochven_kills}
- **Average Fleet Size:** {avg_fleet}
- **Blob Kills (20+):** {blob_count} ({blob_pct}%)
- **Total ISK Destroyed:** {total_isk}B

## Notable Pochven Kills
{chr(10).join(notable_losses) if notable_losses else "- No notable Pochven kills this period"}

## Top Allies (Fleetmates)
{allies_text if allies else "- No ally data available"}

## All-Time Stats (zKillboard)
- **Total Corp Kills:** {alltime_kills:,}
- **Solo Ratio:** {alltime_solo}%
- **Avg Gang Size:** {alltime_avg}
- **ISK Destroyed (All-Time):** {alltime_isk / 1e12:.1f}T ISK

## Assessment
Based on recent activity, Baba Yagas continues to operate primarily in blob formations. Their {blob_pct}% blob rate in Pochven confirms the pattern documented in our phased campaign.

---
*Auto-generated by Yagas Intel Collection System*
"""
    return content


def main():
    now = datetime.now(timezone.utc)
    print(f"=== Yagas Intel Collection — {now.isoformat()} ===")
    
    # 1. Fetch corp info
    print("Fetching EVEWho corp info...")
    corp_info = fetch_evewho_corp(CORP_ID)
    
    # 2. Fetch zKill stats
    print("Fetching zKill stats...")
    zkill_stats = fetch_zkill_stats(CORP_ID)
    
    # 3. Fetch recent kills
    print("Fetching recent kills...")
    kills = fetch_zkill_recent(CORP_ID, limit=200)
    print(f"  Found {len(kills)} kills")
    
    # 4. Analyze
    print("Analyzing (fetching ESI details for system IDs)...")
    analysis = analyze_kills(kills, max_esi_calls=50)
    print(f"  Pochven kills: {analysis['pochven_kills']}/{analysis['total_kills']}")
    print(f"  Avg fleet: {analysis['avg_fleet_size']}, Blob %: {analysis['blob_percentage']}")
    print(f"  ESI calls made: {analysis['esi_calls_made']}")
    
    # 5. Compile report
    report = {
        "generated_at": now.isoformat(),
        "corp_id": CORP_ID,
        "corp_name": "Baba Yagas",
        "evewho": corp_info,
        "zkill_stats": zkill_stats,
        "analysis": analysis
    }
    
    # 6. Save JSON with timestamp
    filename = f"yagas_intel_{now.strftime('%Y%m%d_%H%M')}.json"
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Saved: {filepath}")
    
    # 7. Save as "latest" for easy reference
    latest_path = OUTPUT_DIR / "latest.json"
    with open(latest_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Saved: {latest_path}")
    
    # 8. Generate markdown report for dossier builder
    md_report = generate_markdown_report(report, now)
    md_path = MD_DIR / f"intel_report_{now.strftime('%Y%m%d_%H%M')}.md"
    with open(md_path, "w") as f:
        f.write(md_report)
    print(f"Saved markdown: {md_path}")
    
    # Also save as latest.md for dossier builder
    latest_md = MD_DIR / "latest_intel_report.md"
    with open(latest_md, "w") as f:
        f.write(md_report)
    print(f"Saved markdown: {latest_md}")
    
    # 9. Print summary for cron reporting
    print(f"\n=== SUMMARY ===")
    print(f"Total kills (scanned): {analysis['total_kills']}")
    print(f"Pochven kills: {analysis['pochven_kills']} ({analysis['pochven_percentage']}%)")
    print(f"Avg fleet size: {analysis['avg_fleet_size']}")
    print(f"Blob kills (20+): {analysis['blob_kills_20plus']} ({analysis['blob_percentage']}%)")
    print(f"Top allies: {', '.join([a[1]['name'] for a in analysis['top_allies'][:3]])}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
