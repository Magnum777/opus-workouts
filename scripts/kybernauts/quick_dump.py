import json,sys
d=json.load(sys.stdin)
print("Type: %s count=%s" % (type(d).__name__, len(d) if isinstance(d,list) else "n/a"))
if isinstance(d,list) and d:
    for i,km in enumerate(d[:10]):
        if isinstance(km,list): km=km[0]
        z=km.get("zkb",{})
        labels=z.get("labels",[])
        val=z.get("totalValue",0)/1e6
        kid=km.get("killmail_id")
        print("%s labels=%s value=%.1fM" % (kid, labels, val))
