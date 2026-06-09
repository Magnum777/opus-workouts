import json, urllib.request

# Fetch a few Pochven kills with ESI detail to see ship types
kill_ids = [
    (135784709, "618ea9651d8e3230ca6b19a5be8218d8a833328d"),
    (135704240, "f897f2be62d0c749c1adc149979ce9c46ee4dbd8"),
    (135673149, "7c6e8b5e7e2e1e1e1e1e1e1e1e1e1e1e1e1e1e"),
    (135672228, "need_hash"),
    (135672156, "need_hash"),
]

# Get hashes from zKill first
for kill_id, _ in kill_ids[:3]:
    url = f"https://zkillboard.com/api/killID/{kill_id}/"
    req = urllib.request.Request(url, headers={"User-Agent":"Kybernauts-Intel/1.0","Accept":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            d = json.load(resp)
            if isinstance(d, list) and d:
                km = d[0]
                z = km.get("zkb", {})
                h = z.get("hash")
                v = z.get("totalValue", 0)
                labels = z.get("labels", [])
                print(f"{kill_id}: hash={h}, value={v/1e6:.1f}M, labels={labels}")
    except Exception as e:
        print(f"{kill_id}: error={e}")

# Now get ship types from ESI
print("\n--- Ship types ---")
for kill_id, kill_hash in kill_ids[:3]:
    if kill_hash == "need_hash":
        continue
    url = f"https://esi.evetech.net/latest/killmails/{kill_id}/{kill_hash}/"
    req = urllib.request.Request(url, headers={"User-Agent":"Kybernauts-Intel/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            d = json.load(resp)
            victim = d.get("victim", {})
            attackers = d.get("attackers", [])
            v_ship = victim.get("ship_type_id")
            v_corp = victim.get("corporation_id")
            print(f"Kill {kill_id}: victim_ship={v_ship}, victim_corp={v_corp}, attackers={len(attackers)}")
            # Check Yagas ships used
            yagas_ships = set()
            for a in attackers:
                if a.get("corporation_id") == 98754582:
                    yagas_ships.add(a.get("ship_type_id"))
            print(f"  Yagas ships used: {yagas_ships}")
    except Exception as e:
        print(f"Kill {kill_id}: ESI error={e}")
