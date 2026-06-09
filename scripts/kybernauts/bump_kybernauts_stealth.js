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

  // Add script to hide automation
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    window.chrome = { runtime: {} };
  });

  try {
    console.log('Navigating to login...');
    await page.goto('https://forums.eveonline.com/login', {
      waitUntil: 'domcontentloaded',
      timeout: 60000
    });

    // Wait a bit for Cloudflare to settle
    await page.waitForTimeout(5000);

    // Check if we're on Cloudflare challenge page
    const cfCheck = await page.$('input[type="checkbox"], .cf-turnstile, iframe[src*="challenges"]');
    if (cfCheck) {
      console.log('Cloudflare detected. Trying to bypass via alternative route...');

      // Try direct CCP login bypass
      await page.goto('https://login.eveonline.com/account/logon', {
        waitUntil: 'domcontentloaded',
        timeout: 60000
      });
      await page.waitForTimeout(3000);
    }

    // Look for actual login form
    const userInput = await page.$('input[name="login"], input[name="email"], input[type="email"], #login');
    const passInput = await page.$('input[name="password"], input[type="password"], #password');

    if (!userInput || !passInput) {
      console.log('No standard login form found. Checking page content...');
      const html = await page.content();
      fs.writeFileSync('debug_login.html', html);
      console.log('Saved page HTML to debug_login.html for inspection');
      throw new Error('Login form not found - check debug_login.html');
    }

    console.log('Found login form, filling credentials...');
    await page.fill('input[name="login"], input[name="email"], input[type="email"], #login', 'opusmagnum');
    await page.fill('input[name="password"], input[type="password"], #password', 'Dr34k3r!123123');

    // Submit form
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle', timeout: 30000 }).catch(() => {}),
      page.click('button[type="submit"], input[type="submit"]').catch(() =>
        page.keyboard.press('Enter')
      )
    ]);

    // Check if logged in
    const currentUrl = page.url();
    console.log('Current URL:', currentUrl);

    if (currentUrl.includes('forums.eveonline.com') && !currentUrl.includes('/login')) {
      console.log('Login appears successful!');

      // Save session
      await context.storageState({ path: 'eve_auth.json' });
      console.log('Session saved to eve_auth.json');

      // Navigate to thread and bump
      console.log('Navigating to Kybernauts thread...');
      await page.goto('https://forums.eveonline.com/t/kybernauts-call-pochven-home-small-mid-sized-fleets-w-blops/507971', {
        waitUntil: 'networkidle',
        timeout: 30000
      });

      // Find reply textarea
      const replySelectors = [
        'textarea[data-qa="reply-composer"]',
        '.reply-area textarea',
        '.topic-post textarea',
        '.composer-editor textarea',
        'textarea[placeholder*="Reply"]',
        'textarea'
      ];

      let replyBox = null;
      for (const sel of replySelectors) {
        replyBox = await page.$(sel);
        if (replyBox) {
          console.log('Found reply box with selector:', sel);
          await page.fill(sel, 'Bumping for visibility – Kybernauts still recruiting!');
          break;
        }
      }

      if (!replyBox) {
        throw new Error('Reply textarea not found');
      }

      // Find and click post button
      const submitSelectors = [
        'button[data-qa="reply-submit"]',
        '.submit-reply',
        '.reply-button',
        'button:has-text("Post")',
        'button:has-text("Reply")',
        'button[type="submit"]'
      ];

      for (const sel of submitSelectors) {
        const btn = await page.$(sel);
        if (btn) {
          console.log('Clicking submit with selector:', sel);
          await btn.click();
          break;
        }
      }

      await page.waitForTimeout(3000);
      console.log('✅ Bump posted!');

    } else {
      console.log('Login may have failed. URL:', currentUrl);
      const html = await page.content();
      fs.writeFileSync('debug_after_login.html', html);
    }

  } catch (err) {
    console.error('Error:', err.message);
    const html = await page.content().catch(() => 'N/A');
    fs.writeFileSync('debug_error.html', html);
    console.log('Saved error page to debug_error.html');
  } finally {
    await browser.close();
  }
})();
