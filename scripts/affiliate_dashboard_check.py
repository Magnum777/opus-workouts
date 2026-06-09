#!/usr/bin/env python3
"""Affiliate Program Dashboard Monitor
Logs into affiliate platforms and checks application status.

Platforms to check:
- FirstPromoter (Jasper, Copy.ai, etc.)
- Impact.com (various programs)
- PartnerStack (various programs)
- Individual program dashboards

Usage: python affiliate_dashboard_check.py [firstpromoter|impact|partnerstack|all]
"""

import subprocess
import time
import sys

APPLICANT = {
    "email": "nova.cofounder@gmail.com",
    "paypal": "layeredmediallc@gmail.com"
}

URLS = {
    "firstpromoter": "https://firstpromoter.com/login",
    "impact": "https://app.impact.com/login",
    "partnerstack": "https://partnerstack.com/login",
}

PROGRAM_DASHBOARDS = {
    "jasper": "https://firstpromoter.com/login",  # Uses FirstPromoter
    "copyai": "https://firstpromoter.com/login",   # Uses FirstPromoter
    "descript": "https://firstpromoter.com/login", # Uses FirstPromoter
    "elevenlabs": "https://firstpromoter.com/login", # Uses FirstPromoter
    "hubspot": "https://app.hubspot.com/signup/partners", # HubSpot Partner
    "midjourney": "https://partnerstack.com/login", # PartnerStack
    "notion": "https://partnerstack.com/login", # PartnerStack
    "replicate": "https://replicate.com/affiliate", # Unknown
    "surferseo": "https://firstpromoter.com/login", # FirstPromoter
    "tubebuddy": "https://partnerstack.com/login", # PartnerStack
    "writesonic": "https://firstpromoter.com/login", # FirstPromoter
}

def check_dashboard(platform):
    """Check a single affiliate platform."""
    url = URLS.get(platform)
    if not url:
        return {"error": "Unknown platform"}
    
    print(f"Checking {platform}...")
    
    # Start browser
    subprocess.run("openclaw browser start", shell=True, timeout=15, capture_output=True)
    time.sleep(2)
    
    # Open login page
    result = subprocess.run(
        f'openclaw browser open "{url}"',
        shell=True, capture_output=True, text=True, timeout=20
    )
    time.sleep(5)
    
    # Take snapshot to see login form
    snapshot = subprocess.run(
        "openclaw browser snapshot",
        shell=True, capture_output=True, text=True, timeout=20
    )
    output = snapshot.stdout + snapshot.stderr
    
    # Look for status indicators
    status = "unknown"
    if "login" in output.lower() or "sign in" in output.lower() or "email" in output.lower():
        status = "needs_login"
    elif "dashboard" in output.lower() or "applications" in output.lower():
        status = "logged_in"
    elif "pending" in output.lower() or "under review" in output.lower():
        status = "pending"
    elif "approved" in output.lower() or "active" in output.lower():
        status = "approved"
    
    # Close browser
    subprocess.run("openclaw browser stop", shell=True, timeout=10, capture_output=True)
    subprocess.run('Stop-Process -Name "chrome" -Force', shell=True, timeout=10, capture_output=True)
    
    return {
        "platform": platform,
        "url": url,
        "status": status,
        "needs_login": status == "needs_login"
    }

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            for platform in URLS:
                result = check_dashboard(platform)
                print(f"\n{platform}: {result['status']}")
                if result.get('needs_login'):
                    print(f"  -> Requires login with: {APPLICANT['email']}")
                time.sleep(3)
        else:
            result = check_dashboard(sys.argv[1])
            print(json.dumps(result, indent=2))
    else:
        print("Usage: python affiliate_dashboard_check.py [firstpromoter|impact|partnerstack|all]")
        print("\nPrograms and their likely platforms:")
        for prog, url in PROGRAM_DASHBOARDS.items():
            platform = url.split('/')[-2] if '/' in url else "unknown"
            print(f"  {prog:12s} -> {platform}")

if __name__ == "__main__":
    import json
    main()
