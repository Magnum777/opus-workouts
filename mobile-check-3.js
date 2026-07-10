const { chromium, devices } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  
  // iPhone 12 Pro: 390x844
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    isMobile: true,
    hasTouch: true,
    deviceScaleFactor: 3
  });
  
  const page = await context.newPage();
  
  console.log('Loading https://magnum777.github.io/ga-parks-propagation/?_nocache=1 ...');
  await page.goto('https://magnum777.github.io/ga-parks-propagation/?_nocache=1', {
    waitUntil: 'domcontentloaded',
    timeout: 60000
  });
  
  // Wait 5 seconds for JS to load
  console.log('Waiting 5 seconds for JS to fully load...');
  await page.waitForTimeout(5000);
  
  // Take a screenshot for reference
  await page.screenshot({ path: 'mobile-check-3.png', fullPage: true });
  console.log('Screenshot saved to mobile-check-3.png');
  
  // Run diagnostics
  const results = await page.evaluate(() => {
    const issues = [];
    const fixed = [];
    
    // 1. Horizontal scrolling check
    const windowWidth = window.innerWidth;
    const scrollWidth = document.documentElement.scrollWidth;
    const hasHorizontalScroll = scrollWidth > windowWidth;
    
    if (hasHorizontalScroll) {
      issues.push(`HORIZONTAL SCROLLING: scrollWidth (${scrollWidth}px) > windowWidth (${windowWidth}px). Excess: ${scrollWidth - windowWidth}px`);
    } else {
      fixed.push('Horizontal scrolling: FIXED (scrollWidth <= windowWidth)');
    }
    
    // 2. Touch target sizes
    // Check hamburger button
    const hamburger = document.querySelector('.menu-toggle, .hamburger, button[aria-label*="menu"], #menu-toggle, .navbar-toggler');
    if (hamburger) {
      const rect = hamburger.getBoundingClientRect();
      const isLargeEnough = rect.width >= 44 && rect.height >= 44;
      if (!isLargeEnough) {
        issues.push(`HAMBURGER BUTTON: ${Math.round(rect.width)}x${Math.round(rect.height)}px (needs >= 44x44px)`);
      } else {
        fixed.push(`Hamburger button: FIXED (${Math.round(rect.width)}x${Math.round(rect.height)}px)`);
      }
    } else {
      issues.push('HAMBURGER BUTTON: Not found on page');
    }
    
    // Check filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn, .filter-button, button[class*="filter"], .btn-filter, [class*="filter"] button');
    let smallFilters = [];
    filterButtons.forEach((btn, i) => {
      const rect = btn.getBoundingClientRect();
      if (rect.width < 44 || rect.height < 44) {
        smallFilters.push(`Filter #${i+1}: ${Math.round(rect.width)}x${Math.round(rect.height)}px`);
      }
    });
    
    if (smallFilters.length > 0) {
      issues.push(`FILTER BUTTONS (${smallFilters.length} too small): ${smallFilters.join('; ')}`);
    } else if (filterButtons.length > 0) {
      fixed.push(`Filter buttons: FIXED (all ${filterButtons.length} buttons >= 44x44px)`);
    } else {
      issues.push('FILTER BUTTONS: None found on page');
    }
    
    // Also check ALL buttons/interactive elements
    const allButtons = document.querySelectorAll('button, a, [role="button"], input[type="submit"], input[type="button"]');
    let smallTargets = [];
    allButtons.forEach((btn, i) => {
      const rect = btn.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0 && (rect.width < 44 || rect.height < 44)) {
        const text = btn.textContent?.trim().substring(0, 20) || btn.className?.substring(0, 20) || 'unknown';
        smallTargets.push(`${btn.tagName} "${text}": ${Math.round(rect.width)}x${Math.round(rect.height)}px`);
      }
    });
    if (smallTargets.length > 0) {
      issues.push(`SMALL TOUCH TARGETS (${smallTargets.length} total under 44x44): ${smallTargets.slice(0, 5).join('; ')}${smallTargets.length > 5 ? '...' : ''}`);
    }
    
    // 3. Image overflow check
    const images = document.querySelectorAll('img');
    let overflowImages = [];
    images.forEach((img, i) => {
      const rect = img.getBoundingClientRect();
      if (rect.width > window.innerWidth) {
        overflowImages.push(`Image #${i+1}: ${Math.round(rect.width)}px wide (viewport: ${window.innerWidth}px)`);
      }
    });
    
    if (overflowImages.length > 0) {
      issues.push(`IMAGE OVERFLOW (${overflowImages.length} images exceed viewport): ${overflowImages.join('; ')}`);
    } else if (images.length > 0) {
      fixed.push(`Image overflow: FIXED (all ${images.length} images fit within viewport)`);
    } else {
      issues.push('IMAGES: No images found on page');
    }
    
    // 4. Other mobile layout issues
    // Check for fixed-width elements
    const allElements = document.querySelectorAll('*');
    let fixedWidthIssues = [];
    allElements.forEach((el, i) => {
      const style = window.getComputedStyle(el);
      const width = style.width;
      if (width && width.includes('px')) {
        const pxVal = parseInt(width);
        if (pxVal > window.innerWidth && pxVal < 10000) {
          fixedWidthIssues.push(`${el.tagName}.${el.className}: ${pxVal}px`);
        }
      }
    });
    if (fixedWidthIssues.length > 0) {
      issues.push(`FIXED-WIDTH ELEMENTS exceeding viewport: ${fixedWidthIssues.slice(0, 5).join('; ')}${fixedWidthIssues.length > 5 ? '...' : ''}`);
    }
    
    // Check viewport meta tag
    const viewportMeta = document.querySelector('meta[name="viewport"]');
    if (!viewportMeta) {
      issues.push('VIEWPORT META: Missing! This causes mobile scaling issues.');
    } else {
      fixed.push(`Viewport meta: Present (${viewportMeta.content})`);
    }
    
    // Check for overflow-x on body/html
    const bodyStyle = window.getComputedStyle(document.body);
    const htmlStyle = window.getComputedStyle(document.documentElement);
    if (bodyStyle.overflowX === 'hidden' || htmlStyle.overflowX === 'hidden') {
      fixed.push('Overflow-x: hidden applied (prevents horizontal scroll)');
    }
    
    return { issues, fixed, windowWidth, scrollWidth, imageCount: images.length, buttonCount: allButtons.length };
  });
  
  console.log('\n=== MOBILE LAYOUT CHECK RESULTS ===\n');
  console.log(`Viewport: ${results.windowWidth}x844 (iPhone 12 Pro)`);
  console.log(`Window width: ${results.windowWidth}px, Scroll width: ${results.scrollWidth}px`);
  console.log(`Images found: ${results.imageCount}, Buttons/interactive: ${results.buttonCount}\n`);
  
  console.log('--- FIXED / OK ---');
  if (results.fixed.length === 0) {
    console.log('(none)');
  } else {
    results.fixed.forEach(f => console.log(`✅ ${f}`));
  }
  
  console.log('\n--- ISSUES FOUND ---');
  if (results.issues.length === 0) {
    console.log('✅ No issues found!');
  } else {
    results.issues.forEach(i => console.log(`❌ ${i}`));
  }
  
  await browser.close();
})();
