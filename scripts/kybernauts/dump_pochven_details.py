import json, urllib.request

BABA_YAGAS_CORP_ID = 98754582
POCHVEN_REGION_ID = 10000070

# Fetch all pages of Pochven kills
all_kills = []
for page in range(1, 4):
    url = "https://zkillboard.com/api/kills/corporationID/98754582/regionID/10000070/page/%d/" % page
    req = urllib.request.Request(url, headers={"User-Agent": "Kybernauts-Intel/1.0", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            d = json.load(resp)
            for km in d:
                if isinstance(km, list):
                    km = km[0]
                all_kills.append(km)
    except Exception as e:
        print("Error page %d: %s" % (page, e))
        break

# Filter 25+ and dump
results = []
for km in all_kills:
    if "#:25+" not in km.get("zkb", {}).get("labels", []):
        continue
    kill_id = km.get("killmail_id")
    zkb = km.get("zkb", {})
    labels = zkb.get("labels", [])
    val = zkb.get("totalValue", 0)
    is_structure = "cat:22" in labels
    results.append({
        "id": kill_id,
        "value": val,
        "labels": labels,
        "is_structure": is_structure,
        "url": "https://zkillboard.com/kill/%d/" % kill_id,
    })

# Sort by value desc
results.sort(key=lambda x: x["value"], reverse=True)

print("TOTAL Pochven 25+ fights: %d" % len(results))
print("\n--- STRUCTURE KILLS (cat:22) ---")
for r in results:
    if r["is_structure"]:
        print("  %s | %.1fM ISK | %s" % (r["id"], r["value"]/1e6, r["url"]))

print("\n--- SHIP KILLS (cat:6) ---")
for r in results:
    if not r["is_structure"]:
        print("  %s | %.1fM ISK | %s" % (r["id"], r["value"]/1e6, r["url"]))

# Save JSON
import time
out = "data/kybernauts/yagas_pochven_25plus_%s.json" % time.strftime("%Y%m%d_%H%M%S")
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved to: %s" % out)
