const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const creds = fs.readFileSync('memory/kybernauts_credentials.txt','utf8').split(/\n/);
  const username = creds[0].split(': ')[1].trim();
  const password = creds[1].split(': ')[1].trim();
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.goto('https://forums.eveonline.com/login');
  await page.fill('input[name="login"]', username);
  await page.fill('input[name="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForNavigation({waitUntil: 'networkidle'});
  // navigate to thread
  await page.goto('https://forums.eveonline.com/t/kybernauts-call-pochven-home-small-mid-sized-fleets-w-blops/507971');
  // wait for reply box
  await page.waitForSelector('textarea[data-qa="reply-composer"]', { timeout: 5000 });
  await page.fill('textarea[data-qa="reply-composer"]', 'Bumping for visibility – still open for recruits!');
  await page.click('button[data-qa="reply-submit"]');
  await page.waitForTimeout(3000);
  await browser.close();
})();
