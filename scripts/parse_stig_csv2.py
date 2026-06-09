import csv
import json
import re

csv_path = r"C:\Users\compj\.openclaw\media\inbound\STIG_APPIAN_REVIEWED---7e6ecd86-0b9e-4d4c-a9e1-3bbf51cccfdd.csv"

targets = {"V-222411", "V-222432", "V-222520", "V-222536"}

results = []
not_a_finding_all = []

with open(csv_path, "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        gid = row.get("Group ID", "").strip()
        status = row.get("Status", "").strip()
        comments = row.get("Comments", "").strip()
        
        # Effective status: if Status is empty, use Comments
        effective_status = status if status else comments
        
        item = {
            "group_id": gid,
            "severity": row.get("Severity", "").strip(),
            "stig_id": row.get("STIG ID", "").strip(),
            "rule_title": row.get("Rule Title", "").strip(),
            "status": status,
            "comments": comments,
            "finding_details": row.get("Finding Details", "").strip(),
            "fix_text": row.get("Fix Text", "").strip(),
            "check_content": row.get("Check Content", "").strip(),
            "discussion": row.get("Discussion", "").strip(),
            "severity_override": row.get("Severity Override", "").strip(),
            "severity_override_reason": row.get("Severity Override Reason", "").strip(),
        }
        
        if gid in targets:
            results.append(item)
        
        is_naf = "not a finding" in effective_status.lower()
        if is_naf:
            not_a_finding_all.append(item)

# Save
with open(r"C:\Users\compj\.openclaw\workspace\output\stig_4_targets.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

with open(r"C:\Users\compj\.openclaw\workspace\output\stig_all_naf.json", "w", encoding="utf-8") as f:
    json.dump(not_a_finding_all, f, indent=2)

print(f"4 targets extracted: {len(results)}")
for r in results:
    print(f"  {r['group_id']} | sev={r['severity']} | status='{r['status']}' | comments='{r['comments'][:50]}...'")
    print(f"    finding_details='{r['finding_details'][:60]}...'")

print(f"\nAll Not a Finding: {len(not_a_finding_all)}")
for r in not_a_finding_all[:5]:
    print(f"  {r['group_id']} | {r['severity']} | {r['stig_id']}")
