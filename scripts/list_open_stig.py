import csv
path = r'C:\Users\compj\.openclaw\media\inbound\STIG_APPIAN_REVIEWED---c4f9d089-0337-4c23-8afd-fd0f631e28a0.csv'
open_items = []
with open(path, 'r', encoding='utf-8', newline='') as f:
    f.readline()
    for row in csv.DictReader(f):
        if (row.get('Status') or '').strip().lower() == 'open':
            open_items.append({
                'Group ID': row.get('Group ID'),
                'STIG ID': row.get('STIG ID'),
                'Severity': row.get('Severity'),
                'Rule Title': row.get('Rule Title'),
                'Comments': row.get('Comments', '')[:200]
            })

print(f'Total Open items: {len(open_items)}')
print()
for item in open_items:
    gid = item['Group ID']
    sid = item['STIG ID']
    sev = item['Severity'].upper()
    title = item['Rule Title'][:70]
    comments = item['Comments'][:150]
    print(f"{gid} | {sid} | {sev} | {title}...")
    print(f"  -> {comments}")
    print()
