import json,sys,urllib.request

url = "https://zkillboard.com/api/kills/corporationID/98754582/regionID/10000070/page/1/"
req = urllib.request.Request(url, headers={"User-Agent":"Kybernauts-Intel/1.0","Accept":"application/json"})

with urllib.request.urlopen(req, timeout=20) as resp:
    d = json.load(resp)

total_isk = 0
count = 0
for km in d:
    if isinstance(km, list):
        km = km[0]
    z = km.get("zkb", {})
    total_isk += z.get("totalValue", 0)
    count += 1

print(f"Total Pochven kills on page 1: {count}")
print(f"Total ISK: {total_isk/1e9:.1f}B")
