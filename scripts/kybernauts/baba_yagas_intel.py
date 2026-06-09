"""
Baba Yagas Intelligence Scraper
Pulls kill/loss data from zKillboard API for propaganda targeting.

Usage:
    python baba_yagas_intel.py --recent-days 30 --min-attackers 25
    python baba_yagas_intel.py --losses --recent-days 7
"""

import requests
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

BABA_YAGAS_CORP_ID = 98754582
POCHVEN_REGION_ID = 10000070
ZKB_STATS_API = "https://zkillboard.com/api/stats/corporationID"
ZKB_KILLS_API = "https://zkillboard.com/api/kills/corporationID"

OUTPUT_DIR = Path("data/kybernauts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_stats():
    """Fetch Baba Yagas overall stats."""
    url = f"{ZKB_STATS_API}/{BABA_YAGAS_CORP_ID}/"
    resp = requests.get(url, headers={"Accept": "application/json"}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_recent_kills(page=1, past_seconds=2592000):
    """Fetch recent killmails (default last 30 days)."""
    url = f"{ZKB_KILLS_API}/{BABA_YAGAS_CORP_ID}/page/{page}/pastSeconds/{past_seconds}/"
    resp = requests.get(url, headers={"Accept": "application/json", "User-Agent": "Kybernauts-Intel/1.0"}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_losses(page=1, past_seconds=2592000):
    """Fetch recent losses."""
    url = f"https://zkillboard.com/api/losses/corporationID/{BABA_YAGAS_CORP_ID}/page/{page}/pastSeconds/{past_seconds}/"
    resp = requests.get(url, headers={"Accept": "application/json", "User-Agent": "Kybernauts-Intel/1.0"}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def filter_large_fights(killmails, min_attackers=25, pochven_only=True):
    """Filter for big blob fights in Pochven."""
    results = []
    for km in killmails:
        attackers = km.get("attackers", [])
        victim = km.get("victim", {})
        solar_system = km.get("solar_system_id", 0)

        if len(attackers) < min_attackers:
            continue

        # Check if Pochven (region 10000070)
        if pochven_only:
            # zkill doesn't always give region ID in kill list; we check common Pochven system IDs
            # Pochven systems are in range roughly 30000-32000
            if solar_system < 30000000 or solar_system > 32000000:
                # Fetch detail to confirm
                pass

        kill_id = km.get("killmail_id")
        kill_time = km.get("killmail_time", "unknown")
        ship_type = victim.get("ship_type_id", 0)
        victim_name = victim.get("character_id", "unknown")
        isk = km.get("zkb", {}).get("totalValue", 0)

        results.append({
            "killmail_id": kill_id,
            "url": f"https://zkillboard.com/kill/{kill_id}/",
            "time": kill_time,
            "attackers": len(attackers),
            "victim_ship": ship_type,
            "victim_char": victim_name,
            "isk_destroyed": isk,
            "solar_system": solar_system,
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Baba Yagas Intel Scraper")
    parser.add_argument("--recent-days", type=int, default=30)
    parser.add_argument("--min-attackers", type=int, default=25)
    parser.add_argument("--losses", action="store_true", help="Scan their losses instead")
    parser.add_argument("--pages", type=int, default=3)
    args = parser.parse_args()

    past_seconds = args.recent_days * 86400
    all_kills = []

    for page in range(1, args.pages + 1):
        print(f"Fetching page {page}...")
        try:
            if args.losses:
                data = fetch_losses(page, past_seconds)
            else:
                data = fetch_kills(page, past_seconds)
            if not data:
                break
            all_kills.extend(data)
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    print(f"\nTotal killmails fetched: {len(all_kills)}")

    big_fights = filter_large_fights(all_kills, min_attackers=args.min_attackers)
    print(f"Large fights ({args.min_attackers}+ attackers): {len(big_fights)}")

    # Sort by attacker count descending
    big_fights.sort(key=lambda x: x["attackers"], reverse=True)

    # Save to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    kind = "losses" if args.losses else "kills"
    out_file = OUTPUT_DIR / f"yagas_{kind}_{timestamp}.json"
    with open(out_file, "w") as f:
        json.dump(big_fights, f, indent=2)
    print(f"Saved to: {out_file}")

    # Print top 10
    print("\n--- TOP BLOB FIGHTS ---")
    for i, km in enumerate(big_fights[:10], 1):
        isk_m = km["isk_destroyed"] / 1_000_000
        print(f"{i}. [{km['attackers']} attackers] {isk_m:.1f}M ISK — {km['url']}")

    return big_fights


if __name__ == "__main__":
    main()
