const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
  });
  const page = await context.newPage();

  await page.goto('https://magnum777.github.io/ga-parks-propagation/?_nocache=1', { waitUntil: 'networkidle' });
  await page.waitForTimeout(5000);

  const results = await page.evaluate(() => {
    const issues = [];
    const pass = [];

    // 1. Horizontal scrolling
    const scrollWidth = document.documentElement.scrollWidth;
    const windowWidth = window.innerWidth;
    if (scrollWidth > windowWidth) {
      issues.push(`HORIZONTAL SCROLL: scrollWidth (${scrollWidth}) > windowWidth (${windowWidth})`);
    } else {
      pass.push(`No horizontal scroll: scrollWidth (${scrollWidth}) <= windowWidth (${windowWidth})`);
    }

    // 2. Touch targets >= 44x44
    const allElements = document.querySelectorAll('*');
    const smallTargets = [];
    for (const el of allElements) {
      const rect = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);
      const isClickable = style.cursor === 'pointer' ||
        el.tagName === 'A' ||
        el.tagName === 'BUTTON' ||
        el.onclick !== null ||
        el.getAttribute('role') === 'button' ||
        el.closest('a') ||
        el.closest('button') ||
        style.pointerEvents !== 'none';

      if (isClickable && rect.width > 0 && rect.height > 0) {
        if (rect.width < 44 || rect.height < 44) {
          const label = el.textContent?.slice(0, 30) || el.tagName;
          smallTargets.push({ tag: el.tagName, class: el.className, id: el.id, text: label, width: rect.width.toFixed(1), height: rect.height.toFixed(1) });
        }
      }
    }

    if (smallTargets.length > 0) {
      issues.push(`SMALL TOUCH TARGETS: ${smallTargets.length} elements < 44x44px`);
      issues.push(JSON.stringify(smallTargets.slice(0, 20), null, 2));
    } else {
      pass.push('All touch targets >= 44x44px');
    }

    // 3. Image overflow
    const images = document.querySelectorAll('img');
    const overflowingImages = [];
    for (const img of images) {
      const rect = img.getBoundingClientRect();
      if (rect.right > window.innerWidth + 2 || rect.left < -2) {
        overflowingImages.push({ src: img.src.slice(-50), width: rect.width, right: rect.right, windowWidth: window.innerWidth });
      }
    }
    if (overflowingImages.length > 0) {
      issues.push(`IMAGE OVERFLOW: ${overflowingImages.length} images overflow viewport`);
      issues.push(JSON.stringify(overflowingImages, null, 2));
    } else {
      pass.push('No images overflow viewport');
    }

    return { issues, pass, windowWidth, scrollWidth };
  });

  console.log('=== MOBILE VIEWPORT CHECK (390x844) ===\n');
  console.log('Window width:', results.windowWidth);
  console.log('Scroll width:', results.scrollWidth);
  console.log('\n--- PASSED ---');
  results.pass.forEach(p => console.log('✓', p));
  console.log('\n--- ISSUES ---');
  if (results.issues.length === 0) {
    console.log('✓ NONE — all checks passed!');
  } else {
    results.issues.forEach(i => console.log('✗', i));
  }

  await browser.close();
})();
