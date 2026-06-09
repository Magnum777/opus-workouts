import json, sys, urllib.request

if len(sys.argv) < 3:
    print("Usage: python fetch_esi_kill.py <kill_id> <hash>")
    sys.exit(1)

kill_id = sys.argv[1]
kill_hash = sys.argv[2]
url = f"https://esi.evetech.net/latest/killmails/{kill_id}/{kill_hash}/"

req = urllib.request.Request(url, headers={"User-Agent": "Kybernauts-Intel/1.0"})
with urllib.request.urlopen(req, timeout=15) as resp:
    d = json.load(resp)

a = len(d.get("attackers", []))
v = d.get("victim", {})
print(f"Kill: {d.get('killmail_id')}")
print(f"Attackers: {a}")
print(f"Victim ship: {v.get('ship_type_id')}")
print(f"System: {d.get('solar_system_id')}")
print(f"Time: {d.get('killmail_time')}")
print(f"Victim corp: {v.get('corporation_id')}")
