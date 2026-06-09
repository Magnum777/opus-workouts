#!/usr/bin/env python3
"""Affiliate Account Creator
Creates accounts on affiliate platforms using browser automation.
Handles form filling, submission, and confirmation capture.
"""

import subprocess
import time
import re
import sys

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
    "password": "OpusMedia2026!"  # Generic strong password for affiliate accounts
}

PLATFORMS = {
    "firstpromoter": {
        "name": "FirstPromoter",
        "signup_url": "https://firstpromoter.com/signup",
        "login_url": "https://firstpromoter.com/login"
    },
    "impact": {
        "name": "Impact.com", 
        "signup_url": "https://app.impact.com/signup",
        "login_url": "https://app.impact.com/login"
    },
    "partnerstack": {
        "name": "PartnerStack",
        "signup_url": "https://partnerstack.com/signup",
        "login_url": "https://partnerstack.com/login"
    }
}

def browser_cmd(cmd, timeout=20):
    """Run browser command via openclaw."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout,
            encoding='utf-8', errors='replace'
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"ERROR: {e}"

def kill_browser():
    """Force close Chrome."""
    subprocess.run("openclaw browser stop", shell=True, timeout=10, capture_output=True)
    subprocess.run('Stop-Process -Name "chrome" -Force', shell=True, timeout=10, capture_output=True)
    time.sleep(2)

def create_firstpromoter_account():
    """Create FirstPromoter account (used by Jasper, Copy.ai, etc.)"""
    print("=== FirstPromoter Account Creation ===")
    
    kill_browser()
    browser_cmd("openclaw browser start", timeout=15)
    time.sleep(3)
    
    # Open signup page
    result = browser_cmd(f'openclaw browser open "{PLATFORMS["firstpromoter"]["signup_url"]}"', timeout=20)
    print(f"Opened signup page: {result[:100]}")
    time.sleep(5)
    
    # Get snapshot to see form fields
    snapshot = browser_cmd("openclaw browser snapshot", timeout=20)
    
    # Try to fill fields based on what's in the snapshot
    # Look for input fields and fill them
    if "email" in snapshot.lower():
        print("Found email field, filling...")
        browser_cmd('openclaw browser fill "input[type=email]" "nova.cofounder@gmail.com"')
    if "password" in snapshot.lower():
        print("Found password field, filling...")
        browser_cmd(f'openclaw browser fill "input[type=password]" "{APPLICANT["password"]}"')
    if "company" in snapshot.lower():
        browser_cmd(f'openclaw browser fill "input[name*=company]" "{APPLICANT["company"]}"')
    if "first" in snapshot.lower() or "name" in snapshot.lower():
        browser_cmd(f'openclaw browser fill "input[name*=first]" "{APPLICANT["first_name"]}"')
        browser_cmd(f'openclaw browser fill "input[name*=last]" "{APPLICANT["last_name"]}"')
    
    # Take final snapshot before submit
    time.sleep(2)
    final = browser_cmd("openclaw browser snapshot", timeout=20)
    
    # Try to find and click submit button
    if "submit" in final.lower() or "sign up" in final.lower() or "create" in final.lower():
        print("Attempting to submit form...")
        # Try common submit button selectors
        for selector in ["button[type=submit]", "input[type=submit]", "button:has-text('Sign Up')", "button:has-text('Create')"]:
            click_result = browser_cmd(f'openclaw browser click "{selector}"', timeout=15)
            if "error" not in click_result.lower():
                print(f"Clicked: {selector}")
                break
    
    time.sleep(5)
    
    # Capture confirmation page
    confirm = browser_cmd("openclaw browser snapshot", timeout=20)
    
    # Check for success indicators
    status = "unknown"
    if "verify" in confirm.lower() or "confirmation" in confirm.lower() or "check your email" in confirm.lower():
        status = "verification_email_sent"
    elif "welcome" in confirm.lower() or "dashboard" in confirm.lower() or "success" in confirm.lower():
        status = "success"
    elif "error" in confirm.lower() or "invalid" in confirm.lower():
        status = "error"
    
    # Get current URL
    url = browser_cmd("openclaw browser url", timeout=10)
    
    kill_browser()
    
    return {
        "platform": "FirstPromoter",
        "status": status,
        "url": url,
        "email": APPLICANT["email"],
        "notes": "Check email for verification link"
    }

def check_programs_via_firstpromoter():
    """After FirstPromoter account exists, check individual programs."""
    programs = ["jasper", "copyai", "descript", "elevenlabs", "surferseo", "writesonic"]
    print(f"\nPrograms using FirstPromoter: {', '.join(programs)}")
    print("After account creation, you'll need to apply to each program individually.")
    return programs

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "firstpromoter":
            result = create_firstpromoter_account()
            print(f"\nResult: {result}")
        elif sys.argv[1] == "impact":
            print("Impact.com signup requires invitation code or direct program links. Skipping for now.")
        elif sys.argv[1] == "partnerstack":
            print("PartnerStack signup requires invitation from individual programs. Skipping for now.")
        elif sys.argv[1] == "check":
            # Just check what's in emails
            print("Checking email for affiliate verifications...")
            print("(Run when Gmail API rate limit resets)")
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Usage: python affiliate_account_creator.py [firstpromoter|impact|partnerstack|check]")
    else:
        print("=== Affiliate Account Creator ===")
        print(f"\nApplicant: {APPLICANT['first_name']} {APPLICANT['last_name']}")
        print(f"Email: {APPLICANT['email']}")
        print(f"Company: {APPLICANT['company']}")
        print(f"Website: {APPLICANT['website']}")
        print(f"\nPlatforms needed:")
        for key, info in PLATFORMS.items():
            print(f"  - {info['name']}: {info['signup_url']}")
        print(f"\nRun with 'firstpromoter' to create FirstPromoter account (covers 6 programs)")

if __name__ == "__main__":
    main()
