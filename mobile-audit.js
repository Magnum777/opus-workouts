const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    isMobile: true,
    hasTouch: true,
    deviceScaleFactor: 3
  });
  const page = await context.newPage();

  await page.goto('https://magnum777.github.io/ga-parks-propagation/?_nocache=1', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(7000);

  const results = await page.evaluate(() => {
    const docWidth = document.documentElement.scrollWidth;
    const winWidth = window.innerWidth;
    const horizontalScroll = docWidth > winWidth;

    const checkSize = (el) => {
      const rect = el.getBoundingClientRect();
      return { width: rect.width, height: rect.height, pass: rect.width >= 44 && rect.height >= 44 };
    };

    const selectors = [
      { name: 'hamburger', selector: '.hamburger, .menu-toggle, [class*="hamburger"], [class*="menu"], button[aria-label*="menu"], button[aria-label*="Menu"]' },
      { name: 'filter buttons', selector: 'button, .filter-btn, [class*="filter"], .btn, .button' },
      { name: 'resource links', selector: 'a[href], .resource-link, [class*="resource"]' },
      { name: 'footer links', selector: 'footer a, .footer a' },
      { name: 'labels', selector: 'label, .label' },
      { name: 'zoom controls', selector: '[class*="zoom"], .leaflet-control-zoom a, .map-control' },
      { name: 'blog links', selector: '.blog a, [class*="blog"] a, article a' },
      { name: 'checkbox toggle', selector: 'input[type="checkbox"], .toggle, .switch' }
    ];

    const touchTargetResults = [];
    for (const { name, selector } of selectors) {
      const els = Array.from(document.querySelectorAll(selector));
      const sizes = els.map(el => {
        const rect = el.getBoundingClientRect();
        return { tag: el.tagName, class: el.className, width: Math.round(rect.width * 100) / 100, height: Math.round(rect.height * 100) / 100, pass: rect.width >= 44 && rect.height >= 44 };
      });
      if (sizes.length > 0) {
        touchTargetResults.push({ name, count: sizes.length, sizes, allPass: sizes.every(s => s.pass) });
      }
    }

    const images = Array.from(document.querySelectorAll('img'));
    const imageOverflow = images.map(img => {
      const rect = img.getBoundingClientRect();
      const parent = img.parentElement;
      const parentRect = parent ? parent.getBoundingClientRect() : rect;
      const overflowX = rect.width > winWidth || rect.right > winWidth || rect.left < 0;
      const overflowParent = rect.width > parentRect.width;
      return { src: img.src.split('/').pop(), width: Math.round(rect.width * 100) / 100, winWidth, overflowX, overflowParent };
    });

    return { docWidth, winWidth, horizontalScroll, touchTargetResults, imageOverflow };
  });

  console.log('=== Mobile Audit Results ===\n');

  console.log(`1. Horizontal Scrolling`);
  console.log(`   docWidth: ${results.docWidth}px, winWidth: ${results.winWidth}px`);
  console.log(`   ${results.horizontalScroll ? 'FAIL' : 'PASS'} — ${results.horizontalScroll ? 'page content exceeds viewport width' : 'no horizontal overflow'}\n`);

  console.log(`2. Touch Targets >= 44x44px`);
  let allTouchPass = true;
  for (const group of results.touchTargetResults) {
    const pass = group.allPass;
    if (!pass) allTouchPass = false;
    console.log(`   ${pass ? 'PASS' : 'FAIL'} — ${group.name} (${group.count} found)`);
    for (const s of group.sizes) {
      const status = s.pass ? '✓' : '✗';
      console.log(`      ${status} <${s.tag}>${s.class ? ' class="' + s.class.substring(0, 60) + '"' : ''} — ${s.width}x${s.height}px`);
    }
  }
  if (results.touchTargetResults.length === 0) {
    console.log('   (no matching elements found for listed selectors)');
  }
  console.log(`   Overall: ${allTouchPass && results.touchTargetResults.length > 0 ? 'PASS' : 'FAIL'}\n`);

  console.log(`3. Image Overflow`);
  let anyOverflow = false;
  for (const img of results.imageOverflow) {
    if (img.overflowX || img.overflowParent) {
      anyOverflow = true;
      console.log(`   FAIL — ${img.src}: ${img.width}px wide (viewport ${img.winWidth}px)`);
    }
  }
  if (!anyOverflow) {
    console.log(`   PASS — all ${results.imageOverflow.length} images fit within viewport/parent`);
  } else {
    console.log(`   Overall: FAIL`);
  }

  await browser.close();
})();
