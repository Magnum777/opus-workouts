import csv

path = r"C:\Users\compj\.openclaw\media\inbound\STIG_APPIAN_REVIEWED---530feffe-8008-47bf-9dae-3282b892629d.csv"

not_finding_items = []
with open(path, 'r', encoding='utf-8', newline='') as f:
    f.readline()  # Skip classification banner
    for row in csv.DictReader(f):
        status = (row.get('Status') or '').strip().lower()
        if status == 'not a finding':
            not_finding_items.append(row)

print(f"Total Not a Finding items: {len(not_finding_items)}")
print()
for item in not_finding_items:
    gid = item['Group ID']
    sid = item['STIG ID']
    sev = item['Severity'].upper()
    title = item['Rule Title'][:80]
    print(f"{gid} | {sid} | {sev} | {title}")
