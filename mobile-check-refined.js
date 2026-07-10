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

    // 2. Check SPECIFIC interactive elements by selector
    const selectorsToCheck = [
      // Hamburger
      { sel: '.mobile-menu-toggle, .hamburger, [aria-label*="menu" i], button:has(.hamburger-line)', name: 'Hamburger menu' },
      // Filter buttons
      { sel: '.filter-btn, .mode-filter, .band-filter, [class*="filter"]', name: 'Filter buttons' },
      // Resource links
      { sel: '.resource-link, .resource-card a, .link-card', name: 'Resource links' },
      // Labels
      { sel: 'label, .label', name: 'Labels' },
      // Zoom controls
      { sel: '.leaflet-control-zoom a, .leaflet-control-zoom-in, .leaflet-control-zoom-out', name: 'Zoom controls' },
      // Blog links
      { sel: '.blog-link, .blog-card a, .article-link, .post-link', name: 'Blog links' },
      // General: all buttons and links
      { sel: 'button, a[href]', name: 'All buttons & links' },
    ];

    const checkedElements = new Set();
    const smallTargets = [];

    for (const { sel, name } of selectorsToCheck) {
      const els = document.querySelectorAll(sel);
      for (const el of els) {
        if (checkedElements.has(el)) continue;
        checkedElements.add(el);

        const rect = el.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
          if (rect.width < 44 || rect.height < 44) {
            const text = (el.textContent || el.getAttribute('aria-label') || el.className || el.tagName).slice(0, 40);
            smallTargets.push({ name, tag: el.tagName, class: el.className, text, width: rect.width.toFixed(1), height: rect.height.toFixed(1) });
          }
        }
      }
    }

    if (smallTargets.length > 0) {
      issues.push(`SMALL INTERACTIVE TARGETS: ${smallTargets.length} elements < 44x44px`);
      issues.push(JSON.stringify(smallTargets, null, 2));
    } else {
      pass.push('All interactive targets >= 44x44px');
    }

    // 3. Image overflow — check containers, not individual tiles
    const images = document.querySelectorAll('img:not(.leaflet-tile)');
    const overflowingImages = [];
    for (const img of images) {
      const rect = img.getBoundingClientRect();
      if (rect.right > window.innerWidth + 2 || rect.left < -2) {
        overflowingImages.push({ src: img.src.slice(-50), width: rect.width, right: rect.right, windowWidth: window.innerWidth });
      }
    }

    // Also check map container
    const mapContainer = document.querySelector('#map, .leaflet-container, .map-container');
    let mapContainerOk = true;
    if (mapContainer) {
      const mrect = mapContainer.getBoundingClientRect();
      if (mrect.right > window.innerWidth + 2 || mrect.left < -2) {
        mapContainerOk = false;
        issues.push(`MAP CONTAINER OVERFLOW: right=${mrect.right}, window=${window.innerWidth}`);
      } else {
        pass.push(`Map container fits viewport: ${mrect.width.toFixed(0)}px wide`);
      }
    }

    // Check for any non-map container overflow
    const allContainers = document.querySelectorAll('div, section, article, header, footer, main');
    const overflowingContainers = [];
    for (const cont of allContainers) {
      const rect = cont.getBoundingClientRect();
      if (rect.width > 0 && (rect.right > window.innerWidth + 2 || rect.left < -2)) {
        // Skip if it's a map-related container (tiles overflow intentionally)
        if (cont.closest('.leaflet-container') || cont.className.includes('leaflet')) continue;
        // Skip body/html
        if (cont.tagName === 'BODY' || cont.tagName === 'HTML') continue;
        overflowingContainers.push({ tag: cont.tagName, class: cont.className.slice(0, 50), width: rect.width.toFixed(1), right: rect.right.toFixed(1) });
      }
    }

    if (overflowingImages.length > 0) {
      issues.push(`NON-MAP IMAGE OVERFLOW: ${overflowingImages.length} images overflow viewport`);
      issues.push(JSON.stringify(overflowingImages, null, 2));
    } else {
      pass.push('No non-map images overflow viewport');
    }

    if (overflowingContainers.length > 0) {
      issues.push(`CONTAINER OVERFLOW: ${overflowingContainers.length} containers exceed viewport`);
      issues.push(JSON.stringify(overflowingContainers.slice(0, 10), null, 2));
    } else {
      pass.push('No containers exceed viewport width');
    }

    return { issues, pass, windowWidth, scrollWidth, smallTargetsCount: smallTargets.length, overflowingContainersCount: overflowingContainers.length };
  });

  console.log('=== REFINED MOBILE CHECK (390x844) ===\n');
  console.log('Window width:', results.windowWidth);
  console.log('Scroll width:', results.scrollWidth);
  console.log('Small interactive targets:', results.smallTargetsCount);
  console.log('Overflowing containers:', results.overflowingContainersCount);
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
