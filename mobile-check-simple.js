const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });

  await page.goto('https://magnum777.github.io/ga-parks-propagation/?_nocache=1', { waitUntil: 'networkidle' });
  await page.waitForTimeout(5000);

  const r = await page.evaluate(() => {
    const issues = [];
    const ok = [];

    // 1. Horizontal scroll
    const sw = document.documentElement.scrollWidth;
    const ww = window.innerWidth;
    if (sw > ww) issues.push(`Horizontal scroll: ${sw} > ${ww}`);
    else ok.push(`No horizontal scroll (${sw}x viewport)`);

    // 2. Hamburger
    const ham = document.querySelector('.mobile-menu-toggle, .hamburger, button:has(.hamburger-line)');
    if (ham) {
      const r = ham.getBoundingClientRect();
      const s = getComputedStyle(ham);
      const tw = r.width + (parseFloat(s.paddingLeft)||0) + (parseFloat(s.paddingRight)||0);
      const th = r.height + (parseFloat(s.paddingTop)||0) + (parseFloat(s.paddingBottom)||0);
      if (tw < 44 || th < 44) issues.push(`Hamburger too small: ${tw.toFixed(1)}x${th.toFixed(1)}`);
      else ok.push(`Hamburger OK: ${tw.toFixed(1)}x${th.toFixed(1)}`);
    } else issues.push('Hamburger not found');

    // 3. Filter buttons
    const fb = document.querySelectorAll('.filter-btn, .mode-filter, .band-filter');
    let fsmall = 0;
    for (const b of fb) {
      const r = b.getBoundingClientRect();
      if (r.width < 44 || r.height < 44) fsmall++;
    }
    if (fsmall) issues.push(`${fsmall}/${fb.length} filter buttons < 44x44`);
    else if (fb.length) ok.push(`All ${fb.length} filter buttons OK`);

    // 4. Resource links
    const rl = document.querySelectorAll('.resource-link, .resource-card a, .link-card, footer a[href], .resources a[href]');
    let rsmall = 0;
    const rlist = [];
    for (const a of rl) {
      const r = a.getBoundingClientRect();
      const s = getComputedStyle(a);
      const tw = r.width + (parseFloat(s.paddingLeft)||0) + (parseFloat(s.paddingRight)||0);
      const th = r.height + (parseFloat(s.paddingTop)||0) + (parseFloat(s.paddingBottom)||0);
      if (tw < 44 || th < 44) { rsmall++; rlist.push(a.textContent.trim().slice(0,20)+':'+tw.toFixed(0)+'x'+th.toFixed(0)); }
    }
    if (rsmall) issues.push(`${rsmall}/${rl.length} resource links < 44x44 (${rlist.slice(0,5).join(', ')})`);
    else if (rl.length) ok.push(`All ${rl.length} resource links OK`);

    // 5. Labels
    const lbls = document.querySelectorAll('label');
    let lsmall = 0;
    for (const l of lbls) {
      const r = l.getBoundingClientRect();
      const clickable = l.getAttribute('for') || l.querySelector('input');
      if (clickable && (r.width < 44 || r.height < 44)) lsmall++;
    }
    if (lsmall) issues.push(`${lsmall} clickable labels < 44x44`);
    else ok.push('All clickable labels OK');

    // 6. Zoom controls
    const zIn = document.querySelector('.leaflet-control-zoom-in');
    const zOut = document.querySelector('.leaflet-control-zoom-out');
    if (zIn && zOut) {
      const r1 = zIn.getBoundingClientRect();
      const r2 = zOut.getBoundingClientRect();
      if (r1.width < 44 || r1.height < 44) issues.push(`Zoom-in too small: ${r1.width.toFixed(1)}x${r1.height.toFixed(1)}`);
      else ok.push(`Zoom-in OK: ${r1.width.toFixed(1)}x${r1.height.toFixed(1)}`);
      if (r2.width < 44 || r2.height < 44) issues.push(`Zoom-out too small: ${r2.width.toFixed(1)}x${r2.height.toFixed(1)}`);
      else ok.push(`Zoom-out OK: ${r2.width.toFixed(1)}x${r2.height.toFixed(1)}`);
    } else ok.push('Zoom controls not present (mobile hides them)');

    // 7. Blog links
    const bl = document.querySelectorAll('.blog-link, .blog-card a, .article-link, .post-link');
    let bsmall = 0;
    for (const a of bl) {
      const r = a.getBoundingClientRect();
      if (r.width < 44 || r.height < 44) bsmall++;
    }
    if (bsmall) issues.push(`${bsmall}/${bl.length} blog links < 44x44`);
    else if (bl.length) ok.push(`All ${bl.length} blog links OK`);
    else ok.push('No blog links found');

    // 8. Map container overflow
    const mc = document.querySelector('#map, .leaflet-container');
    if (mc) {
      const r = mc.getBoundingClientRect();
      if (r.right > ww + 2) issues.push(`Map container overflows: right=${r.right.toFixed(1)} > ${ww}`);
      else ok.push(`Map container fits: ${r.width.toFixed(0)}px wide`);
    }

    // 9. Non-map image overflow
    const imgs = document.querySelectorAll('img:not(.leaflet-tile)');
    let iover = 0;
    for (const img of imgs) {
      const r = img.getBoundingClientRect();
      if (r.right > ww + 2 || r.left < -2) iover++;
    }
    if (iover) issues.push(`${iover} non-map images overflow viewport`);
    else ok.push('No non-map images overflow');

    return { issues, ok };
  });

  console.log('=== MOBILE FINAL CHECK (390x844) ===\n');
  r.ok.forEach(x => console.log('✓', x));
  console.log('');
  if (r.issues.length === 0) console.log('ALL CHECKS PASSED');
  else r.issues.forEach(x => console.log('✗', x));

  await browser.close();
})();
