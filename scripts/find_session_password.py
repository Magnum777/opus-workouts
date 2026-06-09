import csv

path = r"C:\Users\compj\.openclaw\media\inbound\STIG_APPIAN_REVIEWED---c4f9d089-0337-4c23-8afd-fd0f631e28a0.csv"

# Look for open items with session, password, lockout, idle, concurrent, deactivation, remember me, branding
target_keywords = ['session', 'password', 'lockout', 'idle', 'concurrent', 'deactivat', 'remember me', 'branding', 'banner', 'classification']

found = 0
with open(path, 'r', encoding='utf-8', newline='') as f:
    f.readline()
    for row in csv.DictReader(f):
        status = (row.get('Status') or '').strip().lower()
        if status != 'open':
            continue
        rt = (row.get('Rule Title') or '').lower()
        comments = (row.get('Comments') or '').lower()
        combined = rt + ' ' + comments
        
        for kw in target_keywords:
            if kw in combined:
                gid = row['Group ID']
                sid = row['STIG ID']
                sev = row['Severity'].upper()
                print(gid + " | " + sid + " | " + sev + " | " + rt[:80] + "...")
                print("  Comments: " + comments[:150])
                print()
                found += 1
                break

print("Found " + str(found) + " open items matching session/password/lockout/idle/etc.")
