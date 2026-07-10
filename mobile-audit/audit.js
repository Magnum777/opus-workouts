const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const outDir = path.join(__dirname, 'mobile-audit');
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

  const url = 'https://magnum777.github.io/ga-parks-propagation/';
  console.log('Navigating to', url);
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(2000);

  // Full-page screenshot
  const screenshotPath = path.join(outDir, 'fullpage-mobile.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log('Screenshot saved to', screenshotPath);

  // Audit results collector
  const issues = [];

  function addIssue(severity, category, message, selectorOrElement) {
    issues.push({ severity, category, message, element: selectorOrElement || '' });
  }

  // --- 1. Horizontal scroll / overflow ---
  const hasHScroll = await page.evaluate(() => {
    return document.documentElement.scrollWidth > window.innerWidth;
  });
  if (hasHScroll) {
    const overflowEls = await page.evaluate(() => {
      const all = Array.from(document.querySelectorAll('*'));
      const offenders = [];
      const vw = window.innerWidth;
      all.forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.right > vw + 2 || rect.left < -2) {
          const tag = el.tagName.toLowerCase();
          const cls = el.className ? '.' + el.className.toString().split(' ').slice(0,3).join('.') : '';
          offenders.push(`${tag}${cls} (right:${Math.round(rect.right)}px)`);
        }
      });
      return offenders.slice(0, 10);
    });
    addIssue('high', 'layout', 'Horizontal scrolling detected — content wider than viewport.', offenders.join('; '));
  }

  // --- 2. Text too small ---
  const tinyText = await page.evaluate(() => {
    const all = Array.from(document.querySelectorAll('*'));
    const bad = [];
    all.forEach(el => {
      const style = window.getComputedStyle(el);
      const size = parseFloat(style.fontSize);
      if (size > 0 && size < 12) {
        const text = el.textContent.trim().slice(0, 40);
        if (text) bad.push(`${el.tagName.toLowerCase()}: "${text}" (${size}px)`);
      }
    });
    return [...new Set(bad)].slice(0, 10);
  });
  if (tinyText.length) {
    addIssue('medium', 'typography', 'Font sizes below 12px detected (hard to read on mobile).', tinyText.join('; '));
  }

  // --- 3. Buttons / links too close ---
  const crowded = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button, a, input[type="button"], input[type="submit"], [role="button"]'));
    const issues = [];
    for (let i = 0; i < btns.length; i++) {
      const a = btns[i].getBoundingClientRect();
      if (a.width === 0 || a.height === 0) continue;
      for (let j = i + 1; j < btns.length; j++) {
        const b = btns[j].getBoundingClientRect();
        if (b.width === 0 || b.height === 0) continue;
        const dx = Math.max(0, Math.max(a.left, b.left) - Math.min(a.right, b.right));
        const dy = Math.max(0, Math.max(a.top, b.top) - Math.min(a.bottom, b.bottom));
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 8) {
          const t1 = btns[i].textContent.trim().slice(0, 20) || btns[i].tagName;
          const t2 = btns[j].textContent.trim().slice(0, 20) || btns[j].tagName;
          issues.push(`"${t1}" and "${t2}" ~${Math.round(dist)}px apart`);
        }
      }
    }
    return [...new Set(issues)].slice(0, 8);
  });
  if (crowded.length) {
    addIssue('medium', 'accessibility', 'Touch targets are very close together (risk of mis-taps).', crowded.join('; '));
  }

  // --- 4. Images without proper scaling ---
  const imgIssues = await page.evaluate(() => {
    const imgs = Array.from(document.querySelectorAll('img'));
    const bad = [];
    imgs.forEach(img => {
      const rect = img.getBoundingClientRect();
      const style = window.getComputedStyle(img);
      const maxW = style.maxWidth;
      const w = style.width;
      if (rect.width > window.innerWidth) {
        bad.push(`img src="${img.src.slice(-40)}" overflows viewport (${Math.round(rect.width)}px wide)`);
      } else if (w && parseFloat(w) > 0 && maxW === 'none') {
        bad.push(`img src="${img.src.slice(-40)}" has fixed width without max-width`);
      }
    });
    return [...new Set(bad)].slice(0, 8);
  });
  if (imgIssues.length) {
    addIssue('high', 'images', 'Images may not scale properly on mobile.', imgIssues.join('; '));
  }

  // --- 5. Viewport meta tag ---
  const viewportMeta = await page.evaluate(() => {
    const meta = document.querySelector('meta[name="viewport"]');
    return meta ? meta.content : null;
  });
  if (!viewportMeta) {
    addIssue('high', 'meta', 'Missing viewport meta tag — page will not render correctly on mobile.', '');
  } else if (!viewportMeta.includes('width=device-width')) {
    addIssue('high', 'meta', `Viewport meta does not set width=device-width: "${viewportMeta}"`, '');
  }

  // --- 6. Navigation/menu issues ---
  const navIssues = await page.evaluate(() => {
    const nav = document.querySelector('nav') || document.querySelector('header');
    const issues = [];
    if (nav) {
      const links = Array.from(nav.querySelectorAll('a'));
      if (links.length > 6) {
        issues.push(`Navigation has ${links.length} links — may crowd on mobile.`);
      }
      const toggle = nav.querySelector('[class*="menu"], [class*="hamburger"], [class*="toggle"], button');
      if (!toggle && links.length > 4) {
        issues.push('No hamburger/toggle menu found for large navigation.');
      }
    }
    return issues;
  });
  if (navIssues.length) {
    addIssue('medium', 'navigation', 'Potential navigation menu issues on mobile.', navIssues.join('; '));
  }

  // --- 7. Tables / wide elements ---
  const wideTables = await page.evaluate(() => {
    const tables = Array.from(document.querySelectorAll('table, pre, iframe, .table, [class*="table"]'));
    const vw = window.innerWidth;
    return tables
      .map(t => {
        const r = t.getBoundingClientRect();
        return { tag: t.tagName.toLowerCase(), width: Math.round(r.width), overflow: r.width > vw };
      })
      .filter(t => t.overflow)
      .slice(0, 5);
  });
  if (wideTables.length) {
    addIssue('high', 'layout', 'Wide elements (tables, pre, iframe) exceed viewport width.', wideTables.map(t => `${t.tag} ${t.width}px`).join('; '));
  }

  // --- 8. Meta / tap target size ---
  const smallTapTargets = await page.evaluate(() => {
    const interactive = Array.from(document.querySelectorAll('a, button, input, select, textarea, [role="button"], [onclick]'));
    const small = [];
    interactive.forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width > 0 && r.height > 0 && (r.width < 44 || r.height < 44)) {
        const text = (el.textContent || el.value || el.tagName).trim().slice(0, 25);
        small.push(`${el.tagName.toLowerCase()} "${text}" (${Math.round(r.width)}×${Math.round(r.height)}px)`);
      }
    });
    return [...new Set(small)].slice(0, 10);
  });
  if (smallTapTargets.length) {
    addIssue('medium', 'accessibility', 'Interactive elements smaller than 44×44px (WCAG minimum tap target).', smallTapTargets.join('; '));
  }

  // --- 9. Content width vs window width ---
  const dims = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    windowWidth: window.innerWidth,
  }));

  // --- Save report ---
  const report = {
    url,
    viewport: { width: 390, height: 844 },
    dimensions: dims,
    viewportMeta,
    issueCount: issues.length,
    issues,
  };
  const reportPath = path.join(outDir, 'report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log('Report saved to', reportPath);

  await browser.close();
})();
