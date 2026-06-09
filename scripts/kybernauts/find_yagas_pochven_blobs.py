"""
Find all Baba Yagas kills with 25+ attackers in Pochven region.
Output: JSON with full kill details.
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
        print(f"zKill error: {e}", file=sys.stderr)
        return None


def esi_get(path):
    url = f"{ESI_BASE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "Kybernauts-Intel/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp)
    except Exception as e:
        print(f"ESI error: {e}", file=sys.stderr)
        return None


def get_system_region(system_id):
    if system_id in _system_cache:
        return _system_cache[system_id]
    data = esi_get(f"/universe/systems/{system_id}/")
    if data:
        rid = data.get("region_id")
        _system_cache[system_id] = rid
        return rid
    return None


def fetch_kill_detail(kill_id, kill_hash):
    return esi_get(f"/killmails/{kill_id}/{kill_hash}/")


def main(max_pages=3):
    results = []
    for page in range(1, max_pages + 1):
        print(f"=== Page {page} ===", file=sys.stderr)
        kills = zkill_get(f"/kills/corporationID/{BABA_YAGAS_CORP_ID}/page/{page}/")
        if not kills:
            break
        if not isinstance(kills, list):
            kills = [kills]

        # Unwrap zkill's double-wrapped format
        kill_summaries = []
        for km in kills:
            if isinstance(km, list) and km:
                km = km[0]
            if isinstance(km, dict):
                kill_summaries.append(km)

        # Filter to 25+ only
        big_fights = [km for km in kill_summaries if "#:25+" in km.get("zkb", {}).get("labels", [])]
        print(f"  Total: {len(kill_summaries)} | 25+: {len(big_fights)}", file=sys.stderr)

        for km in big_fights:
            kill_id = km.get("killmail_id")
            zkb = km.get("zkb", {})
            kill_hash = zkb.get("hash")
            total_value = zkb.get("totalValue", 0)

            if not kill_id or not kill_hash:
                continue

            detail = fetch_kill_detail(kill_id, kill_hash)
            if not detail:
                continue

            system_id = detail.get("solar_system_id", 0)
            region_id = get_system_region(system_id)
            if region_id != POCHVEN_REGION_ID:
                continue

            attackers = detail.get("attackers", [])
            attacker_count = len(attackers)
            # Check if Baba Yagas is on attacker side
            yagas_on_attack = any(a.get("corporation_id") == BABA_YAGAS_CORP_ID for a in attackers)
            # Check if Baba Yagas is the victim
            victim = detail.get("victim", {})
            yagas_victim = victim.get("corporation_id") == BABA_YAGAS_CORP_ID

            result = {
                "killmail_id": kill_id,
                "killmail_time": detail.get("killmail_time"),
                "solar_system_id": system_id,
                "region_id": region_id,
                "attackers": attacker_count,
                "yagas_is_attacker": yagas_on_attack,
                "yagas_is_victim": yagas_victim,
                "total_value": total_value,
                "zkill_url": f"https://zkillboard.com/kill/{kill_id}/",
                "victim": {
                    "character_id": victim.get("character_id"),
                    "corporation_id": victim.get("corporation_id"),
                    "alliance_id": victim.get("alliance_id"),
                    "ship_type_id": victim.get("ship_type_id"),
                    "damage_taken": victim.get("damage_taken"),
                },
            }
            results.append(result)
            print(f"  ++ FOUND: {kill_id} | {attacker_count} atk | YAGAS_atk={yagas_on_attack} YAGAS_vic={yagas_victim} | {total_value/1e6:.1f}M | sys {system_id}", file=sys.stderr)

            time.sleep(0.5)

        time.sleep(2)

    # Save
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_file = DATA_DIR / f"yagas_pochven_25plus_{timestamp}.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"POCHVEN BLOB FIGHTS: {len(results)}", file=sys.stderr)
    print(f"Saved: {out_file}", file=sys.stderr)

    for r in results:
        role = "AGGRESSOR" if r["yagas_is_attacker"] else ("VICTIM" if r["yagas_is_victim"] else "UNKNOWN")
        print(f"{r['killmail_id']} | {r['attackers']} atk | {role} | {r['total_value']/1e6:.1f}M | {r['zkill_url']}")

    return results


if __name__ == "__main__":
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    main(pages)
