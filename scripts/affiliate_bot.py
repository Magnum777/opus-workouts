#!/usr/bin/env python3
"""
Affiliate Application Bot
Automates affiliate program applications via browser automation.
Uses Playwright/CDP through OpenClaw browser tool.
"""

import subprocess
import json
import time
import sys

# Your application data
APPLICANT = {
    "first_name": "James",
    "last_name": "Henderson",
    "email": "nova.cofounder@gmail.com",
    "phone": "256-4908625",
    "company": "Layered Media LLC",
    "address": "609 Bay Laurel Circle",
    "city": "Warner Robins",
    "state": "GA",
    "zip": "31088",
    "country": "United States",
    "ein": "872739763",
    "paypal": "layeredmediallc@gmail.com",
    "website": "https://aitoolalliance.com",
    "websites": [
        "https://aitoolalliance.com",
        "https://aibusinessinsider.org",
        "https://aicofounderstack.com"
    ],
    "niche": "AI tools, productivity software, and business automation",
    "traffic": "Growing network of AI-focused content sites with SEO-driven organic traffic",
    "promotion_methods": "Content marketing, SEO, social media, email newsletters",
    "experience": "Experienced in digital marketing and AI tool reviews since 2020"
}

# Affiliate program signup URLs
PROGRAMS = {
    "jasper": {
        "name": "Jasper AI",
        "url": "https://www.jasper.ai/affiliates",
        "status": "pending"
    },
    "copyai": {
        "name": "Copy.ai",
        "url": "https://www.copy.ai/affiliate-program",
        "status": "pending"
    },
    "descript": {
        "name": "Descript",
        "url": "https://www.descript.com/affiliate",
        "status": "pending"
    },
    "elevenlabs": {
        "name": "ElevenLabs",
        "url": "https://elevenlabs.io/affiliate",
        "status": "pending"
    },
    "hubspot": {
        "name": "HubSpot",
        "url": "https://www.hubspot.com/partners/solutions-directory",
        "status": "pending"
    },
    "midjourney": {
        "name": "Midjourney",
        "url": "https://www.midjourney.com/affiliate",
        "status": "pending"
    },
    "notion": {
        "name": "Notion",
        "url": "https://www.notion.so/affiliate",
        "status": "pending"
    },
    "replicate": {
        "name": "Replicate",
        "url": "https://replicate.com/affiliate",
        "status": "pending"
    },
    "surferseo": {
        "name": "SurferSEO",
        "url": "https://surferseo.com/affiliate",
        "status": "pending"
    },
    "tubebuddy": {
        "name": "TubeBuddy",
        "url": "https://www.tubebuddy.com/affiliate",
        "status": "pending"
    },
    "writesonic": {
        "name": "Writesonic",
        "url": "https://writesonic.com/affiliate",
        "status": "pending"
    }
}

def run_cmd(cmd, timeout=30):
    """Run shell command."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout, encoding='utf-8', errors='replace'
        )
        return result.stdout + result.stderr
    except:
        return "TIMEOUT/ERROR"

def check_affiliate_status(program_key):
    """Check current application status for a program via browser."""
    prog = PROGRAMS.get(program_key)
    if not prog:
        return {"error": "Unknown program"}
    
    print(f"Checking {prog['name']} at {prog['url']}...")
    
    # Open page
    result = run_cmd(f'openclaw browser open "{prog["url"]}"', timeout=15)
    if "TIMEOUT" in result or "error" in result.lower():
        return {"program": prog["name"], "status": "error", "detail": result[:200]}
    
    time.sleep(3)
    
    # Take snapshot
    snapshot = run_cmd("openclaw browser snapshot", timeout=15)
    
    # Look for status indicators
    status = "unknown"
    if "apply" in snapshot.lower() or "application" in snapshot.lower() or "sign up" in snapshot.lower():
        status = "open_for_applications"
    elif "approved" in snapshot.lower() or "congratulations" in snapshot.lower():
        status = "approved"
    elif "pending" in snapshot.lower() or "under review" in snapshot.lower():
        status = "pending_review"
    elif "login" in snapshot.lower() or "dashboard" in snapshot.lower():
        status = "has_account"
    
    # Close browser
    run_cmd("openclaw browser stop", timeout=10)
    run_cmd('Stop-Process -Name "chrome" -Force', timeout=10)
    
    return {
        "program": prog["name"],
        "url": prog["url"],
        "status": status,
        "needs_action": status == "open_for_applications"
    }

def apply_to_program(program_key):
    """Apply to a single affiliate program."""
    # This is a stub - each site has different forms
    # Will be built per-site as we encounter them
    prog = PROGRAMS.get(program_key)
    print(f"Applying to {prog['name']}...")
    print(f"This requires site-specific automation for: {prog['url']}")
    return {"program": prog["name"], "status": "manual_required", "url": prog["url"]}

def scan_all_programs():
    """Check status of all programs."""
    results = []
    for key in PROGRAMS:
        result = check_affiliate_status(key)
        results.append(result)
        time.sleep(2)  # Rate limit between checks
    
    return results

def format_report(results):
    """Format for Discord."""
    lines = []
    lines.append("**Affiliate Program Status Scan**")
    lines.append("")
    
    open_apps = [r for r in results if r.get("status") == "open_for_applications"]
    approved = [r for r in results if r.get("status") == "approved"]
    pending = [r for r in results if r.get("status") == "pending_review"]
    
    lines.append(f"Approved: {len(approved)} | Pending: {len(pending)} | Open to apply: {len(open_apps)}")
    lines.append("")
    
    if approved:
        lines.append("**Approved:**")
        for r in approved:
            lines.append(f"  ✅ {r['program']}")
    
    if pending:
        lines.append("**Pending Review:**")
        for r in pending:
            lines.append(f"  ⏳ {r['program']}")
    
    if open_apps:
        lines.append("**Ready to Apply:**")
        for r in open_apps:
            lines.append(f"  📝 {r['program']} — {r['url']}")
    
    return "\n".join(lines)

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "scan":
            results = scan_all_programs()
            print(json.dumps(results, indent=2))
            print("\n" + format_report(results))
        elif sys.argv[1] in PROGRAMS:
            result = check_affiliate_status(sys.argv[1])
            print(json.dumps(result, indent=2))
        else:
            print(f"Usage: python affiliate_bot.py [scan|{ '|'.join(PROGRAMS.keys()) }]")
    else:
        print("Usage: python affiliate_bot.py scan")
        print("       python affiliate_bot.py jasper")

if __name__ == "__main__":
    main()
