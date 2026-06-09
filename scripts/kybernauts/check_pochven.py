import json, sys, urllib.request

BABA_YAGAS_CORP_ID = 98754582
POCHVEN_REGION_ID = 10000070

# Fetch page 1 of kills
url = "https://zkillboard.com/api/kills/corporationID/98754582/page/1/"
req = urllib.request.Request(url, headers={"User-Agent": "Kybernauts-Intel/1.0", "Accept": "application/json"})
with urllib.request.urlopen(req, timeout=20) as resp:
    kills = json.load(resp)

# Filter 25+
big = []
for km in kills:
    if isinstance(km, list):
        km = km[0]
    if "#:25+" in km.get("zkb", {}).get("labels", []):
        big.append(km)

print("Found %d 25+ fights on page 1" % len(big))
print("Checking each system...")

_system_cache = {}

def get_region(system_id):
    if system_id in _system_cache:
        return _system_cache[system_id]
    try:
        req = urllib.request.Request(
            "https://esi.evetech.net/latest/universe/systems/%d/" % system_id,
            headers={"User-Agent": "Kybernauts-Intel/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            d = json.load(resp)
            rid = d.get("region_id")
            _system_cache[system_id] = rid
            return rid
    except Exception as e:
        print("  ESI error for system %d: %s" % (system_id, e))
        return None

for km in big[:5]:
    kill_id = km.get("killmail_id")
    zkb = km.get("zkb", {})
    kill_hash = zkb.get("hash")
    val = zkb.get("totalValue", 0) / 1e6

    # Fetch ESI detail
    try:
        req = urllib.request.Request(
            "https://esi.evetech.net/latest/killmails/%d/%s/" % (kill_id, kill_hash),
            headers={"User-Agent": "Kybernauts-Intel/1.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            detail = json.load(resp)
    except Exception as e:
        print("  ESI error for kill %d: %s" % (kill_id, e))
        continue

    sys_id = detail.get("solar_system_id", 0)
    region = get_region(sys_id)
    victim = detail.get("victim", {})
    vship = victim.get("ship_type_id", 0)

    is_pochven = (region == POCHVEN_REGION_ID)
    print("  %d | sys=%d region=%s POCHVEN=%s | %d attackers | %.1fM | ship=%s" % (
        kill_id, sys_id, region, is_pochven, len(detail.get("attackers", [])), val, vship
    ))
    sys.stdout.flush()
