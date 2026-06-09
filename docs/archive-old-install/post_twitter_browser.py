#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post to Twitter via browser automation"""

from playwright.sync_api import sync_playwright
import random
import os
import sys

# Ensure UTF-8 encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Varying captions
CAPTIONS = [
    "The stars call to those brave enough to answer. Will you answer with us?",
    "New Eden doesn't forgive the weak. Join those who refuse to be prey.",
    "Every undock is a chance to write your legend. Make it count.",
    "The galaxy is vast, but only the bold claim their place in it.",
    "War is coming. The question is: which side will you be on?",
    "From the shadows we hunt. From the darkness we strike. Join us.",
    "Your pod awaits. Your enemies await. What are you waiting for?"
]

caption_text = random.choice(CAPTIONS)
full_caption = f"{caption_text}\n\njoin.kybernauts.today\n#EVEOnline"

IMAGE_PATH = r"C:\Users\compj\.openclaw\workspace\docs\kybernauts_poster.png"

print(f"Caption: {caption_text}")
print(f"Image: {IMAGE_PATH}")
print(f"\nNote: Browser posting requires user to be logged into Twitter")
print(f"Opening Twitter compose page...")

with sync_playwright() as p:
    # Launch browser
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # Go to Twitter compose
    print("Navigating to Twitter...")
    page.goto("https://twitter.com/compose", wait_until="networkidle")
    
    # Wait for page to load
    page.wait_for_timeout(3000)
    
    # Check if logged in
    if "login" in page.url.lower() or "welcome" in page.url.lower():
        print("\n[INFO] Not logged in to Twitter. Please log in manually.")
        print("After logging in, the script will continue...")
        
        # Wait for user to log in (up to 2 minutes)
        for i in range(24):
            page.wait_for_timeout(5000)
            if "compose" in page.url.lower():
                print("Login detected! Continuing...")
                break
            print(f"Waiting for login... ({(i+1)*5}s)")
    
    # Find the tweet text area and type
    print("\nFinding compose box...")
    
    try:
        # Twitter's compose textarea
        textbox = page.locator('textarea[data-testid="tweetTextarea_0"]').first
        textbox.wait_for(state="visible", timeout=10000)
        textbox.fill(full_caption)
        print("Caption entered")
        
        # Upload image
        print("Uploading image...")
        file_input = page.locator('input[type="file"]')
        file_input.set_files(IMAGE_PATH)
        
        # Wait for upload
        page.wait_for_timeout(5000)
        print("Image uploaded")
        
        # Click post button
        print("Posting tweet...")
        post_button = page.locator('button[data-testid="tweetButton"]').first
        post_button.wait_for(state="enabled", timeout=10000)
        post_button.click()
        
        # Wait for confirmation
        page.wait_for_timeout(3000)
        
        print("\n[SUCCESS] Tweet posted!")
        print(f"Check: https://twitter.com/home")
        
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        print("\nManual posting required:")
        print(f"1. Go to twitter.com/compose")
        print(f"2. Upload: {IMAGE_PATH}")
        print(f"3. Caption: {full_caption}")
    
    # Keep browser open for a bit
    page.wait_for_timeout(5000)
    browser.close()
