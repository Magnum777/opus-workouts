import csv

path = r"C:\Users\compj\.openclaw\media\inbound\STIG_APPIAN_REVIEWED---c4f9d089-0337-4c23-8afd-fd0f631e28a0.csv"

# Search for open items where the comments mention Admin Console, config, settings, etc.
with open(path, 'r', encoding='utf-8', newline='') as f:
    f.readline()
    for row in csv.DictReader(f):
        status = (row.get('Status') or '').strip().lower()
        if status != 'open':
            continue
        
        comments = (row.get('Comments') or '').lower()
        fix_text = (row.get('Fix Text') or '').lower()
        rt = (row.get('Rule Title') or '').lower()
        
        # Look for items where comments indicate the config exists but is wrong/incomplete
        # Or where it's a simple numeric value
        combined = comments + ' ' + fix_text
        
        # Keywords suggesting it's a simple config value
        config_keywords = [
            'admin console', 'administration console', 'configured', 'configuration',
            'set to', 'default', 'timeout', 'idle', 'session', 'password', 'lockout',
            'concurrent', 'disabled', 'enabled', 'value', 'days', 'minutes', 'attempts'
        ]
        
        matched = False
        for kw in config_keywords:
            if kw in combined:
                matched = True
                break
        
        if matched:
            gid = row['Group ID']
            sid = row['STIG ID']
            sev = row['Severity'].upper()
            print(gid + " | " + sid + " | " + sev)
            print("  Rule: " + rt[:100])
            print("  Comments: " + comments[:250])
            print()
