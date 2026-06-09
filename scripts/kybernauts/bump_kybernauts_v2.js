const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--disable-web-security',
      '--disable-features=IsolateOrigins,site-per-process',
    ]
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
    timezoneId: 'America/New_York',
  });

  const page = await context.newPage();

  // Hide automation
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    window.chrome = { runtime: {} };
  });

  try {
    console.log('Navigating to EVE SSO login...');
    await page.goto('https://login.eveonline.com/account/logon', {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    });

    // Wait for page to load
    await page.waitForTimeout(3000);

    // Fill in the login form (found from debug HTML)
    console.log('Filling login form...');
    await page.fill('#UserName', 'opusmagnum');
    await page.fill('#Password', 'Dr34k3r!123123');

    // Click the submit button
    console.log('Submitting login...');
    await page.click('#submit-button');

    // Wait for navigation
    await page.waitForTimeout(5000);

    const currentUrl = page.url();
    console.log('After login URL:', currentUrl);

    // Check if we're logged in (should redirect to forum or oauth callback)
    if (currentUrl.includes('eveonline.com') && !currentUrl.includes('/account/logon')) {
      console.log('Login appears successful!');

      // Save auth state
      await context.storageState({ path: 'eve_auth.json' });
      console.log('Session saved to eve_auth.json');

      // Navigate to forum thread
      console.log('Going to Kybernauts thread...');
      await page.goto('https://forums.eveonline.com/t/kybernauts-call-pochven-home-small-mid-sized-fleets-w-blops/507971', {
        waitUntil: 'networkidle',
        timeout: 30000
      });

      // Wait for reply area
      await page.waitForTimeout(3000);

      // Try to find reply textarea
      const replySelectors = [
        'textarea[data-qa="reply-composer"]',
        '.reply-area textarea',
        '.topic-post textarea',
        '.composer-editor textarea',
        '[data-testid="reply-composer"]',
        'textarea[placeholder*="Reply"]',
        'textarea'
      ];

      let foundReply = false;
      for (const sel of replySelectors) {
        const el = await page.$(sel);
        if (el) {
          console.log('Found reply box:', sel);
          await page.fill(sel, 'Bumping for visibility – Kybernauts still recruiting!');
          foundReply = true;
          break;
        }
      }

      if (!foundReply) {
        // Save page for debugging
        const html = await page.content();
        fs.writeFileSync('debug_thread.html', html);
        throw new Error('Reply textarea not found, saved debug_thread.html');
      }

      // Find and click submit button
      const submitSelectors = [
        'button[data-qa="reply-submit"]',
        '.submit-reply',
        '.reply-button',
        'button:has-text("Post Reply")',
        'button:has-text("Reply")',
        'button[type="submit"]'
      ];

      for (const sel of submitSelectors) {
        const btn = await page.$(sel);
        if (btn) {
          console.log('Clicking submit:', sel);
          await btn.click();
          break;
        }
      }

      await page.waitForTimeout(3000);
      console.log('✅ Bump completed!');

    } else {
      console.log('Login may have failed. URL:', currentUrl);
      const html = await page.content();
      fs.writeFileSync('debug_post_login.html', html);
      console.log('Saved debug_post_login.html');
    }

  } catch (err) {
    console.error('Error:', err.message);
    const html = await page.content().catch(() => 'N/A');
    fs.writeFileSync('debug_error.html', html);
  } finally {
    await browser.close();
  }
})();
