const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const outDir = path.join(__dirname, 'sections');
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    isMobile: true,
    hasTouch: true,
    deviceScaleFactor: 3,
  });
  const page = await context.newPage();

  await page.route('**/*.{mp4,webm,ogg,mp3,wav}', route => route.abort());

  const url = 'https://magnum777.github.io/ga-parks-propagation/';
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);

  // Screenshot sections
  const sections = [
    { name: 'hero', selector: '#hero' },
    { name: 'about', selector: '#about' },
    { name: 'map', selector: '#map' },
    { name: 'stats', selector: '#stats' },
    { name: 'activation-log', selector: '#activation-log' },
    { name: 'conditions', selector: '#conditions' },
    { name: 'contact', selector: '#contact' },
    { name: 'footer', selector: 'footer' },
  ];

  for (const s of sections) {
    try {
      const el = await page.locator(s.selector).first();
      if (await el.count() > 0) {
        await el.screenshot({ path: path.join(outDir, `${s.name}.png`) });
        console.log(`Screenshot ${s.name}`);
      } else {
        console.log(`Missing ${s.name}`);
      }
    } catch (e) {
      console.log(`Error ${s.name}: ${e.message}`);
    }
  }

  // Also take top-of-page screenshot (first 1200px)
  await page.screenshot({ path: path.join(outDir, 'top.png'), clip: { x: 0, y: 0, width: 390, height: 1200 } });
  console.log('Screenshot top');

  // Take screenshot of nav/header area
  await page.screenshot({ path: path.join(outDir, 'nav.png'), clip: { x: 0, y: 0, width: 390, height: 200 } });
  console.log('Screenshot nav');

  await browser.close();
})();
