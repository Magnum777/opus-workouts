"""
Scan Baba Yagas kills on zKillboard, find Pochven fights with 25+ attackers.
Outputs a JSON report with all qualifying kills.
"""

import json
import urllib.request
import time
import sys
from pathlib import Path

BABA_YAGAS_CORP_ID = 98754582
POCHVEN_REGION_ID = 10000070
ZKB_BASE = "https://zkillboard.com/api"
ESI_BASE = "https://esi.evetech.net/latest"

DATA_DIR = Path("data/kybernauts")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Cache for system_id -> region_id lookups
_system_cache = {}


def zkill_get(path):
    url = f"{ZKB_BASE}{path}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Kybernauts-Intel/1.0",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except Exception as e:
        print(f"zKill error for {url}: {e}", file=sys.stderr)
        return None


def esi_get(path):
    url = f"{ESI_BASE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "Kybernauts-Intel/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp)
    except Exception as e:
        print(f"ESI error for {url}: {e}", file=sys.stderr)
        return None


def get_system_region(system_id):
    if system_id in _system_cache:
        return _system_cache[system_id]
    data = esi_get(f"/universe/systems/{system_id}/")
    if data:
        region_id = data.get("region_id")
        _system_cache[system_id] = region_id
        return region_id
    return None


def fetch_kill_detail(kill_id, kill_hash):
    return esi_get(f"/killmails/{kill_id}/{kill_hash}/")


def main(max_pages=5):
    results = []
    for page in range(1, max_pages + 1):
        print(f"Fetching page {page}...", file=sys.stderr)
        kills = zkill_get(f"/kills/corporationID/{BABA_YAGAS_CORP_ID}/page/{page}/")
        if not kills:
            break
        if not isinstance(kills, list):
            kills = [kills]

        for summary in kills:
            if isinstance(summary, list):
                summary = summary[0] if summary else {}
            kill_id = summary.get("killmail_id")
            zkb = summary.get("zkb", {})
            kill_hash = zkb.get("hash")
            total_value = zkb.get("totalValue", 0)

            if not kill_id or not kill_hash:
                continue

            # Fetch ESI detail
            detail = fetch_kill_detail(kill_id, kill_hash)
            if not detail:
                continue

            attackers = detail.get("attackers", [])
            attacker_count = len(attackers)
            if attacker_count < 25:
                continue

            system_id = detail.get("solar_system_id", 0)
            region_id = get_system_region(system_id)
            if region_id != POCHVEN_REGION_ID:
                continue

            victim = detail.get("victim", {})
            # Build result
            result = {
                "killmail_id": kill_id,
                "killmail_time": detail.get("killmail_time"),
                "solar_system_id": system_id,
                "region_id": region_id,
                "attackers": attacker_count,
                "total_value": total_value,
                "zkill_url": f"https://zkillboard.com/kill/{kill_id}/",
                "victim": {
                    "character_id": victim.get("character_id"),
                    "corporation_id": victim.get("corporation_id"),
                    "alliance_id": victim.get("alliance_id"),
                    "ship_type_id": victim.get("ship_type_id"),
                    "damage_taken": victim.get("damage_taken"),
                },
                "attacker_corp_ids": list(set(a.get("corporation_id") for a in attackers if a.get("corporation_id"))),
            }
            results.append(result)
            print(f"FOUND: {kill_id} | {attacker_count} attackers | {total_value/1e6:.1f}M | sys {system_id}", file=sys.stderr)

        time.sleep(1.5)  # Rate limit

    # Save
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_file = DATA_DIR / f"yagas_pochven_bigfights_{timestamp}.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"Total Pochven blob fights found: {len(results)}", file=sys.stderr)
    print(f"Saved to: {out_file}", file=sys.stderr)

    # Print summary to stdout
    for r in results:
        print(f"{r['killmail_id']} | {r['attackers']} attackers | {r['total_value']/1e6:.1f}M | {r['zkill_url']}")

    return results


if __name__ == "__main__":
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(pages)
