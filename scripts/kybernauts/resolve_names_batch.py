import urllib.request
import json
import time

# Character IDs to resolve
char_ids = [2118722264, 2123754656, 2122675250, 2118896777, 2116969318, 273213517, 831308740, 91755520]

# System IDs to resolve  
system_ids = [30004768, 30004651, 30004666, 30000021, 30002128, 30004304, 30000593, 30005196, 30001252, 30004808, 30000240, 30004738, 30000192, 30004620, 30000589, 30001380]

print("Resolving character names...")
for cid in char_ids:
    try:
        url = f"https://esi.evetech.net/latest/characters/{cid}/"
        req = urllib.request.Request(url, headers={"User-Agent": "Nova Intel Tracker"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            print(f"  {cid} -> {data.get('name', 'N/A')}")
    except Exception as e:
        print(f"  {cid} -> ERROR: {e}")
    time.sleep(0.2)

print("\nResolving system names...")
for sid in system_ids:
    try:
        url = f"https://esi.evetech.net/latest/universe/systems/{sid}/"
        req = urllib.request.Request(url, headers={"User-Agent": "Nova Intel Tracker"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
            print(f"  {sid} -> {data.get('name', 'N/A')}")
    except Exception as e:
        print(f"  {sid} -> ERROR: {e}")
    time.sleep(0.2)

print("\nDone.")
