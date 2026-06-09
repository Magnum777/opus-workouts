import json,sys
d=json.load(sys.stdin)
print(f"Results: {len(d) if isinstance(d,list) else 'not list'}")
if isinstance(d,list) and d:
    for i,km in enumerate(d[:5]):
        if isinstance(km, list): km=km[0]
        print(f"{km.get('killmail_id')} value={km.get('zkb',{}).get('totalValue',0)/1e6:.1f}M labels={km.get('zkb',{}).get('labels',[])}")
