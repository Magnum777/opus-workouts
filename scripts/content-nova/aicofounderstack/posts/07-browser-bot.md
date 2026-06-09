# Building a Browser Bot That Logs In and Posts for You

**Author:** James "Opus" Henderson  
**Date:** June 2026  
**Tags:** Browser Automation, CDP, Playwright, OpenClaw, Web Scraping

---

## The Problem

Some tasks can't be done via API:
- Posting to forums that require JavaScript rendering
- Checking dashboards behind login walls
- Uploading images to WordPress Media Library
- Interacting with sites that have bot detection

I needed a browser automation layer that my AI could control programmatically — not just for testing, but for production tasks that run on cron schedules.

## The Stack

**Browser:** Chrome via Chrome DevTools Protocol (CDP)  
**Port:** 18800 (local)  
**Profile:** `openclaw` (persistent session, keeps cookies/logins)  
**Tool:** OpenClaw's built-in browser commands  
**Fallback:** Playwright for complex multi-step flows

## How It Works

The browser starts as a persistent Chrome instance:
```
openclaw browser start  # Launches Chrome at port 18800
openclaw browser open "https://example.com/login"  # Navigates
openclaw browser fill "#username" "myuser"  # Fills fields
openclaw browser fill "#password" "mypass"
openclaw browser click "button[type=submit]"  # Submits
openclaw browser snapshot  # Captures page state
```

For complex sites, I use Playwright directly:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:18800")
    page = browser.contexts[0].pages[0]
    page.goto("https://example.com")
    page.fill("#post-content", "Hello from automation")
    page.click("button.submit")
```

## Real Use Cases

**Forum Bumping**
Every Sunday at 6 PM, the bot:
1. Opens the recruitment thread
2. Clicks "Reply"
3. Types bump text
4. Submits
5. Verifies the post appears
6. Closes browser

Total time: ~45 seconds. Previously manual, now fully autonomous.

**WordPress Featured Images**
After publishing an article:
1. Log into WP admin
2. Navigate to Media → Upload
3. Select Unsplash image
4. Set alt text and caption
5. Attach to the new post

Previously 5 minutes manual work per article. Now 90 seconds automated.

**Affiliate Dashboard Checking**
The bot logs into FirstPromoter, Impact, and PartnerStack to check application status. No more manually checking 11 platforms.

## The Challenges

**JavaScript-Rendered Sites**
Some sites load content dynamically. The snapshot sometimes captures the skeleton before content fills. Fix: add `time.sleep(3)` after navigation, or use Playwright's `wait_for_selector()`.

**Bot Detection**
Cloudflare and similar services flag headless browsers. The `openclaw` profile runs with a real Chrome window (not headless), which passes most checks. For stubborn sites, I use the user's actual Chrome profile.

**Session Persistence**
Chrome CDP sessions don't persist cookies between restarts by default. The `openclaw` profile solves this — log in once, stay logged in until cookies expire.

**Cleanup**
Chrome processes sometimes hang. Every automation ends with:
```
openclaw browser stop
Stop-Process -Name "chrome" -Force  # Fallback kill
```

## The Economics

| Task | Manual Time | Automated Time | Monthly Frequency | Hours Saved |
|------|-------------|----------------|-------------------|-------------|
| Forum bump | 3 min | 45 sec | 4 | 0.17 |
| Featured image | 5 min | 90 sec | 90 | 6.75 |
| Dashboard check | 10 min | 2 min | 8 | 1.07 |
| **Total** | | | | **~8 hours/month** |

At my effective hourly rate (~$50), that's $400/month in saved labor. The browser automation setup took 2 hours to build. ROI: positive in week 1.

## What's Next

1. **Video automation** — Upload to YouTube with title, description, and tags
2. **Form filling** — Automated job applications, affiliate signups
3. **Screenshot monitoring** — Visual regression testing for the WordPress sites

**Want the browser automation scripts?** Included in the Nova Operations blueprint — forum bumper, image uploader, and dashboard checker, all with error handling and cleanup.

---

*This is not about replacing the browser. It's about removing the parts that don't need a human — clicking, waiting, typing the same thing over and over. The decisions still come from me. The execution comes from the bot.*
