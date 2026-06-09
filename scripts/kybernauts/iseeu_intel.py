import json, urllib.request

ISEEU_CORP_ID = 98769631
POCHVEN_REGION_ID = 10000070

# Check ISEEU kills in Pochven
url = f"https://zkillboard.com/api/kills/corporationID/{ISEEU_CORP_ID}/regionID/{POCHVEN_REGION_ID}/page/1/"
req = urllib.request.Request(url, headers={"User-Agent":"Kybernauts-Intel/1.0","Accept":"application/json"})

with urllib.request.urlopen(req, timeout=20) as resp:
    d = json.load(resp)

print(f"ISEEU kills in Pochven on page 1: {len(d)}")
if d:
    # Unwrap
    km = d[0]
    if isinstance(km, list): km = km[0]
    z = km.get("zkb", {})
    labels = z.get("labels", [])
    val = z.get("totalValue", 0)
    print(f"Most recent: {km.get('killmail_id')} labels={labels} value={val/1e6:.1f}M")

# Also check their recent all-kills for ship types
url2 = f"https://zkillboard.com/api/kills/corporationID/{ISEEU_CORP_ID}/page/1/"
req2 = urllib.request.Request(url2, headers={"User-Agent":"Kybernauts-Intel/1.0","Accept":"application/json"})
with urllib.request.urlopen(req2, timeout=20) as resp2:
    d2 = json.load(resp2)

print(f"\nISEEU recent kills (all regions): {len(d2)}")
for i, km in enumerate(d2[:5]):
    if isinstance(km, list): km = km[0]
    z = km.get("zkb", {})
    print(f"  {km.get('killmail_id')} labels={z.get('labels',[])} value={z.get('totalValue',0)/1e6:.1f}M")
