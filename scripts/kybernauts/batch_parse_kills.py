import json, sys, urllib.request

def fetch_kill(kill_id, kill_hash):
    url = f"https://esi.evetech.net/latest/killmails/{kill_id}/{kill_hash}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Kybernauts-Intel/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp)
    except Exception as e:
        print(f"ERROR fetching {kill_id}: {e}", file=sys.stderr)
        return None

# Read kill summaries from stdin (zkill format)
summaries = json.load(sys.stdin)
if not isinstance(summaries, list):
    summaries = [summaries]

for summary in summaries:
    if isinstance(summary, list):
        summary = summary[0]
    kill_id = summary.get("killmail_id")
    zkb = summary.get("zkb", {})
    kill_hash = zkb.get("hash")
    total = zkb.get("totalValue", 0)
    labels = zkb.get("labels", [])

    if not kill_id or not kill_hash:
        continue

    detail = fetch_kill(kill_id, kill_hash)
    if not detail:
        continue

    attackers = len(detail.get("attackers", []))
    if attackers < 20:
        continue  # skip small fights

    victim = detail.get("victim", {})
    system = detail.get("solar_system_id", 0)
    time = detail.get("killmail_time", "unknown")
    ship = victim.get("ship_type_id", 0)
    corp = victim.get("corporation_id", "unknown")
    char = victim.get("character_id", "unknown")

    print(f"KILL {kill_id} | {attackers} attackers | {total/1e6:.1f}M ISK | sys:{system} | ship:{ship} | corp:{corp} | {time}")
    print(f"  URL: https://zkillboard.com/kill/{kill_id}/")
    print()
