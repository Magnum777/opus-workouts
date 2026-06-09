const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const credsPath = path.resolve('memory/kybernauts_credentials.txt');
  const [userLine, passLine] = fs.readFileSync(credsPath, 'utf8').trim().split('\n');
  const username = userLine.split(':')[1].trim();
  const password = passLine.split(':')[1].trim();

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // 1️⃣ Open CCP login page (the forum redirects to this)
    await page.goto('https://login.eveonline.com/account/logon', { waitUntil: 'networkidle' });

    // 2️⃣ Cloudflare challenge – click the "I am not a robot" checkbox if present
    const cfIframe = page.frameLocator('iframe');
    const checkbox = cfIframe.locator('input[type="checkbox"]');
    if (await checkbox.count()) {
      console.log('🔐 Cloudflare checkbox found – clicking');
      await checkbox.check();
      // wait a bit for challenge to resolve
      await page.waitForTimeout(3000);
    } else {
      console.log('✅ No Cloudflare checkbox detected');
    }

    // 3️⃣ Fill in username/email – adjust selector if needed
    //   Common selectors on CCP login: input[name="login"] or input[id="login"]
    const userSel = 'input[name="login"], input[id="login"], input[type="email"]';
    await page.fill(userSel, username);
    // 4️⃣ Fill in password – adjust selector if needed
    const passSel = 'input[name="password"], input[id="password"], input[type="password"]';
    await page.fill(passSel, password);

    // 5️⃣ Submit the form – locate a button with type submit or text "Log In"
    const submitBtn = page.locator('button[type="submit"], button:has-text("Log In"), input[type="submit"]');
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle' }),
      submitBtn.click()
    ]);

    console.log('✅ Logged in – navigating to thread');
    // 6️⃣ Go to the Kybernauts thread
    const threadUrl = 'https://forums.eveonline.com/t/kybernauts-call-pochven-home-small-mid-sized-fleets-w-blops/507971';
    await page.goto(threadUrl, { waitUntil: 'networkidle' });

    // 7️⃣ Wait for the reply composer – selector may vary
    const replyArea = page.locator('textarea[data-qa="reply-composer"], textarea#reply');
    await replyArea.waitFor({ timeout: 20000 });
    await replyArea.fill('Bumping for visibility – still open for recruits!');

    // 8️⃣ Click the post button – find by data-qa or text
    const postBtn = page.locator('button[data-qa="reply-submit"], button:has-text("Post Reply"), button:has-text("Reply")');
    await Promise.all([
      page.waitForResponse(r => r.url().includes('/posts/') && r.status() === 200),
      postBtn.click()
    ]);

    console.log('✅ Thread successfully bumped!');
  } catch (err) {
    console.error('❌ Automation error:', err);
  } finally {
    await browser.close();
  }
})();
