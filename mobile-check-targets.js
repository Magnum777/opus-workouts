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
    const details = [];

    // Check hamburger
    const hamburger = document.querySelector('.mobile-menu-toggle, .hamburger, button:has(.hamburger-line)');
    if (hamburger) {
      const rect = hamburger.getBoundingClientRect();
      const padTop = parseFloat(getComputedStyle(hamburger).paddingTop) || 0;
      const padBot = parseFloat(getComputedStyle(hamburger).paddingBottom) || 0;
      const padLeft = parseFloat(getComputedStyle(hamburger).paddingLeft) || 0;
      const padRight = parseFloat(getComputedStyle(hamburger).paddingRight) || 0;
      const totalW = rect.width + padLeft + padRight;
      const totalH = rect.height + padTop + padBot;
      details.push(`Hamburger: ${rect.width.toFixed(1)}x${rect.height.toFixed(1)} rect, padding ${padLeft}/${padRight}/${padTop}/${padBot}, total ~${totalW.toFixed(1)}x${totalH.toFixed(1)} — ${totalW >= 44 && totalH >= 44 ? 'OK' : 'SMALL'}`);
    } else {
      issues.push('Hamburger menu not found');
    }

    // Check spots-filter
    const spotsFilter = document.querySelector('.spots-filter');
    if (spotsFilter) {
      const rect = spotsFilter.getBoundingClientRect();
      const style = getComputedStyle(spotsFilter);
      const padTop = parseFloat(style.paddingTop) || 0;
      const padBot = parseFloat(style.paddingBottom) || 0;
      const totalH = rect.height + padTop + padBot;
      details.push(`Spots filter: ${rect.width.toFixed(1)}x${rect.height.toFixed(1)} rect, padding top/bottom ${padTop}/${padBot}, total height ~${totalH.toFixed(1)} — ${totalH >= 44 ? 'OK' : 'SMALL'}`);
      if (totalH < 44) issues.push(`Spots filter total height ${totalH.toFixed(1)}px < 44px`);
    }

    // Check all resource links in footer
    const resourceLinks = document.querySelectorAll('.resource-link, .resource-card a, .link-card, footer a, .resources a');
    const smallLinks = [];
    for (const link of resourceLinks) {
      const rect = link.getBoundingClientRect();
      const style = getComputedStyle(link);
      const padTop = parseFloat(style.paddingTop) || 0;
      const padBot = parseFloat(style.paddingBottom) || 0;
      const padLeft = parseFloat(style.paddingLeft) || 0;
      const padRight = parseFloat(style.paddingRight) || 0;
      const totalW = rect.width + padLeft + padRight;
      const totalH = rect.height + padTop + padBot;
      const text = (link.textContent || '').trim().slice(0, 30);
      if (totalW < 44 || totalH < 44) {
        smallLinks.push({ text, rectW: rect.width.toFixed(1), rectH: rect.height.toFixed(1), pad: `${padTop.toFixed(1)}/${padBot.toFixed(1)}/${padLeft.toFixed(1)}/${padRight.toFixed(1)}`, totalW: totalW.toFixed(1), totalH: totalH.toFixed(1) });
      }
    }
    if (smallLinks.length > 0) {
      issues.push(`${smallLinks.length} resource links < 44x44px (including padding)`);
      issues.push(JSON.stringify(smallLinks, null, 2));
    } else {
      details.push('All resource links >= 44x44px (including padding)');
    }

    // Check zoom controls
    const zoomIn = document.querySelector('.leaflet-control-zoom-in');
    const zoomOut = document.querySelector('.leaflet-control-zoom-out');
    if (zoomIn && zoomOut) {
      const r1 = zoomIn.getBoundingClientRect();
      const r2 = zoomOut.getBoundingClientRect();
      details.push(`Zoom in: ${r1.width.toFixed(1)}x${r1.height.toFixed(1)} — ${r1.width >= 44 && r1.height >= 44 ? 'OK' : 'SMALL'}`);
      details.push(`Zoom out: ${r2.width.toFixed(1)}x${r2.height.toFixed(1)} — ${r2.width >= 44 && r2.height >= 44 ? 'OK' : 'SMALL'}`);
      if (r1.width < 44 || r1.height < 44) issues.push('Zoom in button too small');
      if (r2.width < 44 || r2.height < 44) issues.push('Zoom out button too small');
    } else {
      details.push('Zoom controls not found (may be hidden on mobile)');
    }

    // Check filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn, .mode-filter, .band-filter');
    const smallFilters = [];
    for (const btn of filterBtns) {
      const rect = btn.getBoundingClientRect();
      const text = (btn.textContent || '').trim().slice(0, 20);
      if (rect.width < 44 || rect.height < 44) {
        smallFilters.push({ text, w: rect.width.toFixed(1), h: rect.height.toFixed(1) });
      }
    }
    if (smallFilters.length > 0) {
      issues.push(`${smallFilters.length} filter buttons < 44x44px`);
      issues.push(JSON.stringify(smallFilters, null, 2));
    } else if (filterBtns.length > 0) {
      details.push(`All ${filterBtns.length} filter buttons >= 44x44px`);
    } else {
      details.push('No filter buttons found');
    }

    // Check the label
    const labels = document.querySelectorAll('label');
    for (const lbl of labels) {
      const rect = lbl.getBoundingClientRect();
      const forAttr = lbl.getAttribute('for');
      const hasInput = lbl.querySelector('input');
      const isClickable = forAttr || hasInput;
      details.push(`Label "${(lbl.textContent || '').trim().slice(0, 30)}": ${rect.width.toFixed(1)}x${rect.height.toFixed(1)}, clickable=${isClickable ? 'yes' : 'no'}`);
      if (isClickable && (rect.width < 44 || rect.height < 44)) {
        issues.push(`Clickable label too small: ${rect.width.toFixed(1)}x${rect.height.toFixed(1)}`);
      }
    }

    return { issues, details };
  });

  console.log('=== TARGETED MOBILE CHECK ===\n');
  console.log('--- DETAILS ---');
  results.details.forEach(d => console.log('•', d));
  console.log('\n--- ISSUES ---');
  if (results.issues.length === 0) {
    console.log('✓ NONE — all targeted checks passed!');
  } else {
    results.issues.forEach(i => console.log('✗', i));
  }

  await browser.close();
})();
