import csv

csv_path = r"C:\Users\compj\.openclaw\media\inbound\STIG_APPIAN_REVIEWED---7e6ecd86-0b9e-4d4c-a9e1-3bbf51cccfdd.csv"
targets = {"V-222411", "V-222432", "V-222520", "V-222536"}

# Read file raw to handle embedded newlines
with open(csv_path, "r", encoding="utf-8") as f:
    raw = f.read()

# Split by the pattern that starts a new row (benchmark name at start of line after quote)
# Actually, let's use csv reader with proper handling
import io

# The issue is newlines inside quoted fields. csv module should handle this if we open
# in text mode with newline='' - which we did. But maybe the file has mixed line endings.
# Let's try reading with different line endings.

with open(csv_path, "rb") as f:
    raw_bytes = f.read()

# Detect line endings
if b'\r\n' in raw_bytes[:1000]:
    print("CRLF line endings detected")
elif b'\n' in raw_bytes[:1000]:
    print("LF line endings detected")

# Try decoding with universal newlines disabled
with open(csv_path, "r", encoding="utf-8", newline='') as f:
    # Skip classification banner line
    first_line = f.readline()
    print(f"Skipped line: {first_line[:50].strip()}")
    
    reader = csv.reader(f)
    header = next(reader)
    print(f"Header columns: {len(header)}")
    print(f"Header first 10: {header[:10]}")
    
    # Find indexes for key fields
    idx_group_id = header.index("Group ID")
    idx_status = header.index("Status")
    idx_comments = header.index("Comments")
    idx_finding = header.index("Finding Details")
    idx_severity = header.index("Severity")
    idx_stig_id = header.index("STIG ID")
    idx_rule = header.index("Rule Title")
    idx_fix = header.index("Fix Text")
    idx_check = header.index("Check Content")
    idx_disc = header.index("Discussion")
    idx_sev_over = header.index("Severity Override")
    idx_sev_reason = header.index("Severity Override Reason")
    
    targets_found = []
    naf_found = []
    
    for row in reader:
        if len(row) < 35:
            continue  # skip malformed
        gid = row[idx_group_id].strip()
        status = row[idx_status].strip()
        comments = row[idx_comments].strip()
        effective = status if status else comments
        
        if gid in targets:
            targets_found.append({
                "group_id": gid,
                "severity": row[idx_severity],
                "stig_id": row[idx_stig_id],
                "rule_title": row[idx_rule],
                "status": status,
                "comments": comments,
                "finding_details": row[idx_finding],
                "fix_text": row[idx_fix],
                "check_content": row[idx_check],
                "discussion": row[idx_disc],
                "severity_override": row[idx_sev_over],
                "severity_override_reason": row[idx_sev_reason],
            })
        
        if "not a finding" in effective.lower():
            naf_found.append({
                "group_id": gid,
                "severity": row[idx_severity],
                "stig_id": row[idx_stig_id],
                "rule_title": row[idx_rule],
                "status": status,
                "comments": comments,
                "finding_details": row[idx_finding],
                "severity_override": row[idx_sev_over],
                "severity_override_reason": row[idx_sev_reason],
            })

print(f"\nTargets found: {len(targets_found)}")
for t in targets_found:
    print(f"  {t['group_id']} | {t['severity']} | status='{t['status']}'")

print(f"\nNot a Finding total: {len(naf_found)}")
for n in naf_found[:5]:
    print(f"  {n['group_id']} | {n['severity']} | {n['stig_id']}")
