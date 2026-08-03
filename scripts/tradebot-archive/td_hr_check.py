"""Check which added TD torrents might be H&R sources"""
import json

STATE_PATH = r"C:\Users\compj\.openclaw\workspace\scripts\td_state.json"

s = json.load(open(STATE_PATH))
added = s.get("added_torrents", {})
ds = s.get("ds_library", [])

print(f"Added torrents: {len(added)}")
print(f"DS library size: {len(ds)}")
print()

# Find added torrents NOT in DS library (not seeding at all)
not_in_ds = []
for tid, t in added.items():
    found = False
    title_lower = t["title"][:25].lower()
    for d in ds:
        if title_lower in d["title"][:25].lower() or d["title"][:25].lower() in title_lower:
            found = True
            break
    if not found:
        not_in_ds.append((tid, t))

print(f"Added torrents NOT in DS library: {len(not_in_ds)}")
print("(These were downloaded from TD but may not be seeding)")
for tid, t in not_in_ds:
    print(f"  {t['title'][:55]:55s}  Free:{t['freeleech']}  Size:{t['size']}  Added:{t['added_at'][:10]}")

# Also check DS tasks with low upload ratio (potential H&R candidates)
print()
print("DS tasks with ratio < 1.0 (potential H&R if not freeleech):")
low_ratio = []
for d in ds:
    if d.get("size", 0) > 0:
        dl = max(d.get("downloaded", 0), d.get("size", 0))
        ul = d.get("uploaded", 0)
        if dl > 0:
            r = ul / dl
            if r < 1.0:
                low_ratio.append((r, d))

low_ratio.sort(key=lambda x: x[0])
for r, d in low_ratio[:30]:
    ul_gb = d["uploaded"] / (1024**3)
    dl_gb = d["size"] / (1024**3)
    print(f"  R:{r:.3f} UL:{ul_gb:.1f}GB DL:{dl_gb:.1f}GB  {d['title'][:55]}")

print(f"\nTotal low-ratio DS tasks: {len(low_ratio)}")