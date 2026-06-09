import json, sys
d = json.load(sys.stdin)
big = [km[0] if isinstance(km, list) else km for km in d]
big = [km for km in big if "#:25+" in km.get("zkb", {}).get("labels", [])]
print(f"Big fights on page 1: {len(big)}")
for km in big[:10]:
    z = km["zkb"]
    print(f"  {km['killmail_id']} labels={z.get('labels')} value={z.get('totalValue', 0) / 1e6:.1f}M")
