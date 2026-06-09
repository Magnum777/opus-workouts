#!/usr/bin/env python3
"""Check Gmail for affiliate program approval/rejection emails."""
import subprocess, json, re, sys

ACCOUNTS = ["compjunkie@gmail.com", "jhenderson87@gmail.com", "layeredmediallc@gmail.com", "nova.cofounder@gmail.com"]

AFFILIATE_PATTERNS = [
    r"jasper", r"copy\.?ai", r"descript", r"elevenlabs", r"hubspot",
    r"midjourney", r"notion", r"replicate", r"surferseo", r"tubebuddy",
    r"writesonic", r"affiliate", r"partner", r"application approved",
    r"application rejected", r"welcome to", r"affiliate program",
    r"firstpromoter", r"impact\.com", r"partnerstack"
]

def check_account(account):
    """Check inbox for affiliate-related emails."""
    try:
        cmd = f'gog gmail thread list --account {account} --limit 50 --label INBOX'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        
        lines = output.split('\n')
        affiliate_emails = []
        
        for line in lines:
            line_lower = line.lower()
            if any(re.search(p, line_lower) for p in AFFILIATE_PATTERNS):
                affiliate_emails.append(line.strip())
        
        return {
            "account": account,
            "affiliate_emails_found": len(affiliate_emails),
            "emails": affiliate_emails[:10]  # limit
        }
    except Exception as e:
        return {"account": account, "error": str(e)}

def main():
    print("=== Affiliate Email Scan ===\n")
    for account in ACCOUNTS:
        result = check_account(account)
        print(f"Account: {result['account']}")
        if "error" in result:
            print(f"  ERROR: {result['error']}")
        else:
            print(f"  Affiliate emails found: {result['affiliate_emails_found']}")
            for email in result['emails']:
                print(f"    - {email}")
        print()

if __name__ == "__main__":
    main()
