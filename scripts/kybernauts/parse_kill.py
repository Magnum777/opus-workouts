import json,sys
data=json.load(sys.stdin)
d=data[0] if isinstance(data, list) else data
a=len(d.get('attackers',[]))
v=d.get('victim',{})
print(f"Kill: {d.get('killmail_id')}")
print(f"Attackers: {a}")
print(f"Victim ship: {v.get('ship_type_id')}")
print(f"System: {d.get('solar_system_id')}")
print(f"Time: {d.get('killmail_time')}")
print(f"Value: {d.get('zkb',{}).get('totalValue',0)/1e6:.1f}M")
