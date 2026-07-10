const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });

  await page.goto('https://magnum777.github.io/ga-parks-propagation/?_nocache=1', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(8000);

  const r = await page.evaluate(() => {
    const btns = document.querySelectorAll('button');
    const btnInfo = [];
    for (const b of btns) {
      const r = b.getBoundingClientRect();
      btnInfo.push({ tag: b.tagName, class: b.className, aria: b.getAttribute('aria-label'), text: b.textContent.trim().slice(0,30), w: r.width.toFixed(1), h: r.height.toFixed(1) });
    }
    const roleBtns = document.querySelectorAll('[role="button"]');
    const roleInfo = [];
    for (const b of roleBtns) {
      const r = b.getBoundingClientRect();
      roleInfo.push({ tag: b.tagName, class: b.className, text: b.textContent.trim().slice(0,30), w: r.width.toFixed(1), h: r.height.toFixed(1) });
    }
    const menuEls = document.querySelectorAll('[class*="menu" i], [class*="toggle" i], [aria-label*="menu" i], [aria-label*="toggle" i]');
    const menuInfo = [];
    for (const b of menuEls) {
      const r = b.getBoundingClientRect();
      menuInfo.push({ tag: b.tagName, class: b.className, aria: b.getAttribute('aria-label'), w: r.width.toFixed(1), h: r.height.toFixed(1) });
    }
    return { btnInfo, roleInfo, menuInfo };
  });

  console.log('=== HAMBURGER / MENU SEARCH ===\n');
  console.log('--- BUTTONS ---');
  r.btnInfo.forEach(b => console.log(JSON.stringify(b)));
  console.log('\n--- ROLE=BUTTON ---');
  r.roleInfo.forEach(b => console.log(JSON.stringify(b)));
  console.log('\n--- MENU/TOGGLE ---');
  r.menuInfo.forEach(b => console.log(JSON.stringify(b)));

  await browser.close();
})();
