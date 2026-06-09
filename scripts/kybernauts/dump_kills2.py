import json, sys
d = json.load(sys.stdin)
print(f"Type: {type(d).__name__}")
if isinstance(d, list):
    print(f"Count: {len(d)}")
    for i, km in enumerate(d[:5]):
        if isinstance(km, list):
            km = km[0]
        z = km.get("zkb", {})
        labels = z.get("labels", [])
        val = z.get("totalValue", 0) / 1e6
        kid = km.get("killmail_id")
        print(f"  {kid} labels={labels} value={val:.1f}M")
