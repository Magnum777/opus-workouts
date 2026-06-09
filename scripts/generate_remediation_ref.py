import csv
from collections import defaultdict

# Load all OPEN items from CSV
path = r"C:\Users\compj\.openclaw\media\inbound\STIG_APPIAN_REVIEWED---c4f9d089-0337-4c23-8afd-fd0f631e28a0.csv"
open_items = []
with open(path, 'r', encoding='utf-8', newline='') as f:
    f.readline()
    for row in csv.DictReader(f):
        if (row.get('Status') or '').strip().lower() == 'open':
            open_items.append(row)

# Categorize by remediation theme
categories = {
    "Authentication / CAC / PKI / SAML": [],
    "TLS / Encryption / FIPS / Cryptography": [],
    "Audit Logging / Centralized Management / SIEM": [],
    "Session Management / Timeout / Concurrent Users": [],
    "Password Policy / Account Lockout / Temporary Accounts": [],
    "Audit Integrity / Protection / Hashing": [],
    "Audit Reporting / Reduction / Filtering": [],
    "Audit Alerting / Failure Handling": [],
    "Mutual SSL / Endpoint Device Auth": [],
    "System Hardening / Whitelist / Ports / PPSM": [],
    "Contingency / Backup / Recovery": [],
    "Code Security / Pen Testing / Race Conditions": [],
    "Application Admin / ISSO Responsibilities": [],
    "Data Marking / Classification": [],
    "Other / General": []
}

for item in open_items:
    rt = (item.get('Rule Title') or '').lower()
    gid = item.get('Group ID', '')
    
    if any(k in rt for k in ['pki', 'cac', 'piv', 'saml', 'certificate', 'identity', 'revocation', 'alt. token', 'alt token', 'mutual authen', 'replay']):
        if 'mutual' in rt or 'endpoint' in rt or 'network connected' in rt:
            categories["Mutual SSL / Endpoint Device Auth"].append(item)
        else:
            categories["Authentication / CAC / PKI / SAML"].append(item)
    elif any(k in rt for k in ['tls', 'encrypt', 'cryptograph', 'fips', 'hash', 'session id', 'password transmit']):
        categories["TLS / Encryption / FIPS / Cryptography"].append(item)
    elif any(k in rt for k in ['audit', 'log', 'centralized', 'siem', 'syslog', 'off-load', 'transaction recovery']):
        if any(k in rt for k in ['filter', 'reduction', 'report generation', 'on-demand', 'after-the-fact']):
            categories["Audit Reporting / Reduction / Filtering"].append(item)
        elif any(k in rt for k in ['alert', 'alarm', 'failure', 'shut down', 'warn', 'notify']):
            categories["Audit Alerting / Failure Handling"].append(item)
        elif any(k in rt for k in ['integrity', 'protect', 'unauthorized access', 'unauthorized mod', 'unauthorized del', 'cryptographically hash', 'hash']):
            categories["Audit Integrity / Protection / Hashing"].append(item)
        else:
            categories["Audit Logging / Centralized Management / SIEM"].append(item)
    elif any(k in rt for k in ['session', 'concurrent', 'logon session', 'idle', 'reauthenticate']):
        categories["Session Management / Timeout / Concurrent Users"].append(item)
    elif any(k in rt for k in ['password', 'account lock', 'temporary', 'disable account']):
        categories["Password Policy / Account Lockout / Temporary Accounts"].append(item)
    elif any(k in rt for k in ['whitelist', 'deny-all', 'non-essential', 'ports', 'protocols', 'ppsm', 'mobile code']):
        categories["System Hardening / Whitelist / Ports / PPSM"].append(item)
    elif any(k in rt for k in ['contingency', 'backup', 'recovery', 'disaster']):
        categories["Contingency / Backup / Recovery"].append(item)
    elif any(k in rt for k in ['race condition', 'overflow', 'pen test', 'security training', 'incident response', 'vulnerability testing']):
        categories["Code Security / Pen Testing / Race Conditions"].append(item)
    elif any(k in rt for k in ['isso', 'isso', 'program manager', 'security training', 'report violation']):
        categories["Application Admin / ISSO Responsibilities"].append(item)
    elif any(k in rt for k in ['mark', 'classification', 'banner', 'cui']):
        categories["Data Marking / Classification"].append(item)
    else:
        categories["Other / General"].append(item)

# Generate report
report = []
report.append("=" * 80)
report.append("APPIAN ASD STIG V6R4 - OPEN ITEMS REMEDIATION REFERENCE")
report.append(f"Total Open Items: {len(open_items)}")
report.append("Generated: 2026-06-02")
report.append("=" * 80)
report.append("")

# Appian Documentation URLs Reference
report.append("APPIAN DOCUMENTATION REFERENCE")
report.append("-" * 40)
docs = [
    ("Administration Console (security settings)", "https://docs.appian.com/suite/help/26.5/Appian_Administration_Console.html"),
    ("Authentication (CAC/SAML/PKI)", "https://docs.appian.com/suite/help/26.5/Authentication.html"),
    ("SAML for Single Sign-On", "https://docs.appian.com/suite/help/26.5/SAML_for_Single_Sign-On.html"),
    ("TLS Policies", "https://docs.appian.com/suite/help/26.5/TLS_Policies.html"),
    ("System Logging", "https://docs.appian.com/suite/help/26.5/Logging.html"),
    ("Log Streaming to Syslog/SIEM", "https://docs.appian.com/suite/help/26.5/Log_Streaming_for_Appian_Cloud.html"),
    ("Managing Log Files", "https://docs.appian.com/suite/help/26.5/managing-log-files.html"),
    ("Application Logging Config", "https://docs.appian.com/suite/help/26.5/customizing-application-logging.html"),
    ("Post-Install Configurations", "https://docs.appian.com/suite/help/26.5/Post-Install_Configurations.html"),
    ("User Management", "https://docs.appian.com/suite/help/26.5/User_Management.html"),
    ("Installation Guide", "https://docs.appian.com/suite/help/26.5/Installation_Guide.html"),
]
for name, url in docs:
    report.append(f"  {name}")
    report.append(f"    {url}")
report.append("")

# Summary by category
report.append("OPEN ITEMS BY CATEGORY")
report.append("-" * 40)
for cat, items in categories.items():
    if items:
        report.append(f"  {cat}: {len(items)} items")
report.append("")
report.append("=" * 80)
report.append("")

# Detailed breakdown
for cat, items in categories.items():
    if not items:
        continue
    report.append(f"\n{'='*80}")
    report.append(f"CATEGORY: {cat} ({len(items)} items)")
    report.append(f"{'='*80}")
    
    # Determine primary Appian doc reference
    doc_ref = ""
    if "Authentication" in cat:
        doc_ref = "Primary: Appian Administration Console > Authentication; docs.appian.com/suite/help/26.5/Authentication.html"
    elif "TLS" in cat or "Encryption" in cat or "Cryptography" in cat:
        doc_ref = "Primary: TLS Policies, Admin Console > Security; docs.appian.com/suite/help/26.5/TLS_Policies.html"
    elif "Audit Logging" in cat and "Centralized" in cat:
        doc_ref = "Primary: Log Streaming to Syslog/SIEM; docs.appian.com/suite/help/26.5/Log_Streaming_for_Appian_Cloud.html"
    elif "Audit Reporting" in cat or "Audit Reduction" in cat:
        doc_ref = "Primary: Application Logging, System Logs; docs.appian.com/suite/help/26.5/Logging.html"
    elif "Audit Alerting" in cat:
        doc_ref = "Primary: Customizing Application Logging (log4j); docs.appian.com/suite/help/26.5/customizing-application-logging.html"
    elif "Audit Integrity" in cat or "Protection" in cat:
        doc_ref = "Primary: Managing Log Files (permissions/rotation); docs.appian.com/suite/help/26.5/managing-log-files.html"
    elif "Session" in cat:
        doc_ref = "Primary: Admin Console > Session Timeout settings; docs.appian.com/suite/help/26.5/Appian_Administration_Console.html"
    elif "Password" in cat or "Account" in cat:
        doc_ref = "Primary: Admin Console > Password Policy, Account Lockout; docs.appian.com/suite/help/26.5/Appian_Administration_Console.html"
    elif "Mutual SSL" in cat or "Endpoint" in cat:
        doc_ref = "Primary: Admin Console > Certificates, SAML; docs.appian.com/suite/help/26.5/Appian_Administration_Console.html#certificates"
    elif "Hardening" in cat:
        doc_ref = "Primary: Post-Install Configurations; docs.appian.com/suite/help/26.5/Post-Install_Configurations.html"
    elif "Contingency" in cat:
        doc_ref = "Primary: Configuring Backup and Restoration; docs.appian.com/suite/help/26.5/Configuring_Backup_and_Restoration.html"
    elif "Code Security" in cat:
        doc_ref = "Customer responsibility: Appian provides quarterly pen test results; customer must review and validate"
    elif "ISSO" in cat or "Admin" in cat:
        doc_ref = "Customer/ISSO responsibility: Process/procedure documentation required"
    
    if doc_ref:
        report.append(f"\nREMEDIATION REFERENCE: {doc_ref}")
    
    report.append("")
    for item in items:
        gid = item.get('Group ID', '')
        sid = item.get('STIG ID', '')
        sev = (item.get('Severity') or '').upper()
        title = item.get('Rule Title', '')
        comments = (item.get('Comments') or '').strip()
        fix_text = (item.get('Fix Text') or '').strip()
        
        report.append(f"\n  {gid} | {sid} | {sev}")
        report.append(f"  Rule: {title}")
        report.append(f"  Fix: {fix_text[:200]}{'...' if len(fix_text) > 200 else ''}")
        if comments:
            report.append(f"  Current Comment: {comments[:250]}{'...' if len(comments) > 250 else ''}")
        report.append("")

# Write output
out_path = r"C:\Users\compj\.openclaw\workspace\output\Appian_STIG_Open_Items_Remediation_Reference.txt"
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"Report written: {out_path}")
print(f"Total Open Items: {len(open_items)}")
for cat, items in categories.items():
    if items:
        print(f"  {cat}: {len(items)}")
