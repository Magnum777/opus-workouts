import csv
import json

csv_path = r"C:\Users\compj\.openclaw\media\inbound\STIG_APPIAN_REVIEWED---7e6ecd86-0b9e-4d4c-a9e1-3bbf51cccfdd.csv"
targets = {"V-222411", "V-222432", "V-222520", "V-222536"}

with open(csv_path, "r", encoding="utf-8", newline='') as f:
    f.readline()  # skip classification banner
    reader = csv.DictReader(f)
    
    header = reader.fieldnames
    
    targets_found = []
    naf_found = []
    
    for row in reader:
        gid = (row.get("Group ID") or "").strip()
        status = (row.get("Status") or "").strip()
        comments = (row.get("Comments") or "").strip()
        effective = status if status else comments
        
        item = {k: (row.get(k) or "").strip() for k in header}
        
        if gid in targets:
            targets_found.append(item)
        
        if "not a finding" in effective.lower():
            naf_found.append(item)

# Save both
with open(r"C:\Users\compj\.openclaw\workspace\output\stig_4_targets_full.json", "w", encoding="utf-8") as f:
    json.dump(targets_found, f, indent=2)

with open(r"C:\Users\compj\.openclaw\workspace\output\stig_all_naf_full.json", "w", encoding="utf-8") as f:
    json.dump(naf_found, f, indent=2)

print(f"Targets: {len(targets_found)}")
for t in targets_found:
    print(f"  {t['Group ID']} | {t['Severity']} | {t['STIG ID']}")
    print(f"    Status: '{t['Status']}'")
    print(f"    Comments: '{t['Comments'][:60]}...'")
    print(f"    Finding Details: '{t['Finding Details'][:60]}...'")
    print(f"    Severity Override: '{t['Severity Override']}'")
    print()

print(f"Not a Finding total: {len(naf_found)}")
