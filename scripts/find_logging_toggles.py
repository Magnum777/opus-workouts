import csv

path = r"C:\Users\compj\.openclaw\media\inbound\STIG_APPIAN_REVIEWED---c4f9d089-0337-4c23-8afd-fd0f631e28a0.csv"

# Look for OPEN items where logging/auditing might be fixable via Admin Console toggles
audit_logging_keywords = [
    'log user actions', 'log content', 'audit record', 'audit log', 'log changes',
    'audit event', 'audit information', 'audit trail', 'log event', 'log file',
    'record time stamp', 'timestamp', 'audit reduction', 'report generation',
    'log management', 'logging configuration'
]

# Exclude items that require external systems (SIEM, centralized, syslog, etc.)
external_keywords = ['centralized', 'syslog', 'siem', 'off-load', 'different system',
                     'external system', 'stream', 'fips', 'cryptographic module',
                     'certificate', 'saml', 'cac', 'pki', 'piv', 'mutual', 'tls',
                     'penetration test', 'contingency', 'backup', 'recovery']

found_items = []
with open(path, 'r', encoding='utf-8', newline='') as f:
    f.readline()
    for row in csv.DictReader(f):
        status = (row.get('Status') or '').strip().lower()
        if status != 'open':
            continue
        
        rt = (row.get('Rule Title') or '').lower()
        comments = (row.get('Comments') or '').lower()
        fix = (row.get('Fix Text') or '').lower()
        check = (row.get('Check Content') or '').lower()
        combined = rt + ' ' + comments + ' ' + fix + ' ' + check
        
        # Must relate to audit logging
        is_audit = any(k in combined for k in audit_logging_keywords)
        # Must not require external systems
        requires_external = any(k in combined for k in external_keywords)
        
        if is_audit and not requires_external:
            gid = row['Group ID']
            sid = row['STIG ID']
            sev = row['Severity'].upper()
            title = row['Rule Title']
            print("=" * 80)
            print(f"{gid} | {sid} | {sev}")
            print(f"Rule: {title}")
            print()
            print(f"Fix Text: {fix[:300]}")
            print()
            print(f"Check Content: {check[:300]}")
            print()
            print(f"Comments: {comments[:300]}")
            print()
            found_items.append(row)

print(f"\n\nFound {len(found_items)} potential Admin Console logging toggle items")
