"""
Browser test script - verify Playwright works for cron tasks
"""
from playwright.sync_api import sync_playwright

def test_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Test navigation
        page.goto('https://example.com')
        print(f"[OK] Loaded: {page.title()}")
        
        # Test screenshot
        page.screenshot(path='browser_test.png')
        print("[OK] Screenshot saved")
        
        browser.close()
        print("[OK] Browser test complete")

if __name__ == "__main__":
    test_browser()
