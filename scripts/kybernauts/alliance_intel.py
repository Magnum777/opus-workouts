import json, urllib.request

# Observatory Great Bear alliance stats
ALLIANCE_ID = 99011350  # Need to verify

# Search for it
url = "https://zkillboard.com/api/stats/allianceID/99011350/"
req = urllib.request.Request(url, headers={"User-Agent":"Kybernauts-Intel/1.0","Accept":"application/json"})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        d = json.load(resp)
        print(json.dumps(d, indent=2)[:1000])
except Exception as e:
    print(f"Error: {e}")

# Also check ISEEU stats
url2 = "https://zkillboard.com/api/stats/corporationID/98769631/"
req2 = urllib.request.Request(url2, headers={"User-Agent":"Kybernauts-Intel/1.0","Accept":"application/json"})
with urllib.request.urlopen(req2, timeout=15) as resp2:
    d2 = json.load(resp2)
    print("\nISEEU Stats:")
    if isinstance(d2, dict):
        print(f"  Dangerous: {d2.get('dangerRatio', 'N/A')}%")
        print(f"  Gang/Solo: {d2.get('gangRatio', 'N/A')}% gang")
        print(f"  Ships destroyed: {d2.get('shipsDestroyed', 'N/A')}")
        print(f"  Ships lost: {d2.get('shipsLost', 'N/A')}")
    else:
        print(f"  Type: {type(d2)}")
        print(f"  Data: {str(d2)[:500]}")
