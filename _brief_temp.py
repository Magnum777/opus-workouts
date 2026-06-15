import json

with open("C:/Users/compj/.openclaw/workspace/scripts/kybernauts/data/kybernauts/yagas_pochven_25plus_20260614_210007.json") as f:
    kills = json.load(f)

total_isk = sum(k["value"] for k in kills)
print("=== KYBERNAUTS EVENING BRIEF ===")
print("Sun, June 14, 2026 | 9:12 PM ET")
print()
print(f"Active Pochven kills (25+ pilots): {len(kills)}")
print(f"Total ISK destroyed: {total_isk/1e9:.1f}B")
print()

import collections
cats = collections.Counter()
tzs = collections.Counter()
for k in kills:
    for l in k["labels"]:
        if l.startswith("cat:"):
            cats[l] += 1
        if l.startswith("tz:"):
            tzs[l] += 1
structs = [k for k in kills if k.get("is_structure")]

cat_names = {
    "cat:6": "Battleship", "cat:5": "Destroyer", "cat:4": "Cruiser",
    "cat:3": "Frigate", "cat:2": "Industrial", "cat:25": "Structure",
    "cat:1": "Corvette", "cat:7": "Hauler", "cat:8": "Capital"
}
print("Ship class breakdown:")
for c, n in sorted(cats.items(), reverse=True):
    name = cat_names.get(c, c.replace("cat:", ""))
    print(f"  {name}: {n}")

print()
print("Timezone activity:")
for tz, n in tzs.most_common():
    print(f"  {tz}: {n}")

print()
if structs:
    print(f"Structures destroyed: {len(structs)}")
    for s in structs:
        print(f'  {s["value"]/1e9:.1f}B - {s["url"]}')
else:
    print("No structures destroyed in these kills.")

print()
sorted_kills = sorted(kills, key=lambda x: x["value"], reverse=True)
print("Top 10 kills by ISK:")
for i, k in enumerate(sorted_kills[:10]):
    print(f'  {i+1}. {k["value"]/1e9:.1f}B - {k["url"]}')
