#!/usr/bin/env python3
"""
Kybernauts Evening Brief — fast, reliable Pochven intel.
Outputs a clean summary. No hanging ESI calls.
"""
import json, urllib.request

BABA_YAGAS_CORP_ID = 98754582
POCHVEN_REGION_ID = 10000070
ISEEU_CORP_ID = 98769631

HEADERS = {"User-Agent": "Kybernauts-Intel/1.0", "Accept": "application/json"}

def fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)

def fetch_page(corp_id, page=1):
    url = f"https://zkillboard.com/api/kills/corporationID/{corp_id}/regionID/{POCHVEN_REGION_ID}/page/{page}/"
    try:
        return fetch_json(url, timeout=15)
    except Exception as e:
        print(f"[ERROR] zKill fetch failed: {e}")
        return []

def analyze_kills(kills):
    total_isk = 0
    count = 0
    tz_dist = {"EU": 0, "US": 0, "RU": 0, "AU": 0, "Unknown": 0}
    top_kills = []

    for km in kills:
        if isinstance(km, list):
            km = km[0]
        zkb = km.get("zkb", {})
        val = zkb.get("totalValue", 0)
        total_isk += val
        count += 1

        # Timezone heuristic from killmail time
        time_str = km.get("killmail_time", "")
        if "T" in time_str:
            hour = int(time_str.split("T")[1].split(":")[0])
            if 6 <= hour < 12:
                tz = "RU"
            elif 12 <= hour < 18:
                tz = "EU"
            elif 18 <= hour < 23:
                tz = "US"
            else:
                tz = "AU"
        else:
            tz = "Unknown"
        tz_dist[tz] += 1

        if val > 500e6:
            top_kills.append({
                "id": km.get("killmail_id"),
                "value": val,
                "url": f"https://zkillboard.com/kill/{km.get('killmail_id')}/"
            })

    top_kills.sort(key=lambda x: x["value"], reverse=True)
    return {
        "count": count,
        "isk_b": total_isk / 1e9,
        "tz_dist": tz_dist,
        "top_kills": top_kills[:5]
    }

if __name__ == "__main__":
    print("=== KYBERNAUTS EVENING BRIEF ===")
    print()

    # Fetch Baba Yagas Pochven data
    yagas_kills = fetch_page(BABA_YAGAS_CORP_ID, 1)
    if yagas_kills:
        stats = analyze_kills(yagas_kills)
        print(f"**Baba Yagas in Pochven (last ~200 kills):**")
        print(f"  Kills: {stats['count']} | ISK: {stats['isk_b']:.1f}B")
        print(f"  Timezone: EU={stats['tz_dist']['EU']} US={stats['tz_dist']['US']} RU={stats['tz_dist']['RU']} AU={stats['tz_dist']['AU']}")
        if stats['top_kills']:
            print(f"  Top kills:")
            for k in stats['top_kills']:
                print(f"    {k['value']/1e9:.1f}B — {k['url']}")
    else:
        print("[ERROR] Could not fetch Baba Yagas data")

    print()

    # Fetch ISEEU Pochven data
    iseeu_kills = fetch_page(ISEEU_CORP_ID, 1)
    if iseeu_kills:
        stats = analyze_kills(iseeu_kills)
        print(f"**ISEEU in Pochven (last ~200 kills):**")
        print(f"  Kills: {stats['count']} | ISK: {stats['isk_b']:.1f}B")
        print(f"  Timezone: EU={stats['tz_dist']['EU']} US={stats['tz_dist']['US']} RU={stats['tz_dist']['RU']} AU={stats['tz_dist']['AU']}")
    else:
        print("[ERROR] Could not fetch ISEEU data")

    print()
    print("=== END BRIEF ===")
