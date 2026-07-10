const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const outDir = path.join(__dirname);
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    isMobile: true,
    hasTouch: true,
    deviceScaleFactor: 3,
  });
  const page = await context.newPage();

  // Block heavy resources to speed up load
  await page.route('**/*.{mp4,webm,ogg,mp3,wav}', route => route.abort());
  await page.route('**/*.{png,jpg,jpeg,gif,svg,webp}', route => route.continue());

  const url = 'https://magnum777.github.io/ga-parks-propagation/';
  console.log('Navigating to', url);
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);

  // Screenshot full page
  const screenshotPath = path.join(outDir, 'fullpage-mobile.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log('Screenshot saved to', screenshotPath);

  // Collect issues
  const issues = [];
  function addIssue(severity, category, message, element) {
    issues.push({ severity, category, message, element: element || '' });
  }

  // 1. Horizontal scroll
  const hasHScroll = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  if (hasHScroll) {
    const offenders = await page.evaluate(() => {
      const vw = window.innerWidth;
      return Array.from(document.querySelectorAll('*'))
        .map(el => ({ el, r: el.getBoundingClientRect() }))
        .filter(({ r }) => r.right > vw + 2 || r.left < -2)
        .slice(0, 10)
        .map(({ el, r }) => {
          const tag = el.tagName.toLowerCase();
          const cls = el.className ? '.' + String(el.className).split(/\s+/).slice(0,2).join('.') : '';
          return `${tag}${cls} right=${Math.round(r.right)}px`;
        });
    });
    addIssue('high', 'layout', 'Horizontal scrolling detected.', offenders.join('; '));
  }

  // 2. Tiny text
  const tinyText = await page.evaluate(() => {
    const res = [];
    document.querySelectorAll('*').forEach(el => {
      const s = window.getComputedStyle(el);
      const sz = parseFloat(s.fontSize);
      if (sz > 0 && sz < 12) {
        const txt = el.textContent.trim().slice(0,40);
        if (txt) res.push(`${el.tagName.toLowerCase()}: "${txt}" (${sz}px)`);
      }
    });
    return [...new Set(res)].slice(0, 10);
  });
  if (tinyText.length) addIssue('medium', 'typography', 'Font sizes below 12px.', tinyText.join('; '));

  // 3. Touch targets too close
  const crowded = await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('button, a, input[type="button"], input[type="submit"], [role="button"]'));
    const bad = [];
    for (let i = 0; i < els.length; i++) {
      const a = els[i].getBoundingClientRect(); if (!a.width || !a.height) continue;
      for (let j = i+1; j < els.length; j++) {
        const b = els[j].getBoundingClientRect(); if (!b.width || !b.height) continue;
        const dx = Math.max(0, Math.max(a.left, b.left) - Math.min(a.right, b.right));
        const dy = Math.max(0, Math.max(a.top, b.top) - Math.min(a.bottom, b.bottom));
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 8) {
          const t1 = (els[i].textContent||els[i].tagName).trim().slice(0,20);
          const t2 = (els[j].textContent||els[j].tagName).trim().slice(0,20);
          bad.push(`"${t1}" & "${t2}" ~${Math.round(dist)}px`);
        }
      }
    }
    return [...new Set(bad)].slice(0, 8);
  });
  if (crowded.length) addIssue('medium', 'accessibility', 'Touch targets very close together.', crowded.join('; '));

  // 4. Images overflow
  const imgIssues = await page.evaluate(() => {
    const bad = [];
    document.querySelectorAll('img').forEach(img => {
      const r = img.getBoundingClientRect();
      const s = window.getComputedStyle(img);
      if (r.width > window.innerWidth) bad.push(`img overflows (${Math.round(r.width)}px)`);
      else if (parseFloat(s.width) > 0 && s.maxWidth === 'none') bad.push(`img fixed width no max-width`);
    });
    return [...new Set(bad)].slice(0, 8);
  });
  if (imgIssues.length) addIssue('high', 'images', 'Image scaling issues.', imgIssues.join('; '));

  // 5. Viewport meta
  const viewportMeta = await page.evaluate(() => {
    const m = document.querySelector('meta[name="viewport"]');
    return m ? m.content : null;
  });
  if (!viewportMeta) addIssue('high', 'meta', 'Missing viewport meta tag.', '');
  else if (!viewportMeta.includes('width=device-width')) addIssue('high', 'meta', `Viewport missing width=device-width: "${viewportMeta}"`, '');

  // 6. Navigation
  const navIssues = await page.evaluate(() => {
    const nav = document.querySelector('nav') || document.querySelector('header');
    const issues = [];
    if (nav) {
      const links = Array.from(nav.querySelectorAll('a'));
      if (links.length > 6) issues.push(`${links.length} nav links`);
      const toggle = nav.querySelector('[class*="menu"], [class*="hamburger"], [class*="toggle"], button');
      if (!toggle && links.length > 4) issues.push('No mobile toggle for large nav');
    }
    return issues;
  });
  if (navIssues.length) addIssue('medium', 'navigation', 'Nav concerns.', navIssues.join('; '));

  // 7. Wide tables/pre/iframe
  const wideEls = await page.evaluate(() => {
    const vw = window.innerWidth;
    return Array.from(document.querySelectorAll('table, pre, iframe, .table, [class*="table"]'))
      .map(t => ({ tag: t.tagName.toLowerCase(), w: Math.round(t.getBoundingClientRect().width) }))
      .filter(t => t.w > vw)
      .slice(0,5)
      .map(t => `${t.tag} ${t.w}px`);
  });
  if (wideEls.length) addIssue('high', 'layout', 'Wide elements exceed viewport.', wideEls.join('; '));

  // 8. Small tap targets
  const smallTargets = await page.evaluate(() => {
    const res = [];
    document.querySelectorAll('a, button, input, select, textarea, [role="button"], [onclick]').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width > 0 && r.height > 0 && (r.width < 44 || r.height < 44)) {
        const txt = (el.textContent || el.value || el.tagName).trim().slice(0,25);
        res.push(`${el.tagName.toLowerCase()} "${txt}" ${Math.round(r.width)}x${Math.round(r.height)}px`);
      }
    });
    return [...new Set(res)].slice(0, 10);
  });
  if (smallTargets.length) addIssue('medium', 'accessibility', 'Tap targets smaller than 44x44px.', smallTargets.join('; '));

  // 9. Dimensions
  const dims = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    windowWidth: window.innerWidth,
  }));

  const report = { url, viewport: { width: 390, height: 844 }, dimensions: dims, viewportMeta, issueCount: issues.length, issues };
  fs.writeFileSync(path.join(outDir, 'report.json'), JSON.stringify(report, null, 2));
  console.log('Report saved.');

  await browser.close();
})();
