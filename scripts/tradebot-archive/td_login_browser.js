// TorrentDay login via Playwright - handles Cloudflare Turnstile
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Read credentials from .secrets
const secretsPath = path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw', 'workspace', '.secrets');
const secrets = fs.readFileSync(secretsPath, 'utf8');
let tdUser = '', tdPass = '';
let section = '';
for (const line of secrets.split('\n')) {
    const trimmed = line.trim();
    if (trimmed.startsWith('[')) { section = trimmed.replace(/[\[\]]/g, ''); continue; }
    if (section === 'torrentday' && trimmed.includes('=')) {
        const [key, ...vals] = trimmed.split('=');
        const val = vals.join('=');
        if (key === 'username') tdUser = val;
        if (key === 'password') tdPass = val;
    }
}

console.log(`Creds loaded: user=${tdUser} pass_len=${tdPass.length}`);

(async () => {
    const browser = await chromium.launch({ headless: false }); // headful for Cloudflare
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    });
    const page = await context.newPage();

    // Navigate to login
    console.log('Navigating to TorrentDay login...');
    await page.goto('https://www.torrentday.com/login.php', { waitUntil: 'networkidle', timeout: 30000 });

    // Take screenshot of initial state
    await page.screenshot({ path: path.join(__dirname, 'td_step1_login.png') });
    console.log('Login page loaded');

    // Fill in credentials
    console.log('Filling credentials...');
    await page.locator('input[name="username"]').fill(tdUser);
    await page.locator('input[name="password"]').fill(tdPass);
    
    await page.screenshot({ path: path.join(__dirname, 'td_step2_filled.png') });

    // Wait for Turnstile to solve (it auto-solves in headful mode)
    console.log('Waiting for Cloudflare Turnstile to solve...');
    await page.waitForTimeout(5000); // Give Turnstile time to render and solve

    // Click login button
    console.log('Clicking login...');
    const loginBtn = page.locator('button[type="submit"], input[type="submit"], button:has-text("Login"), button:has-text("Sign")').first();
    await loginBtn.click();

    // Wait for navigation
    console.log('Waiting for post-login redirect...');
    await page.waitForTimeout(5000);
    
    const currentUrl = page.url();
    console.log(`Current URL: ${currentUrl}`);
    
    await page.screenshot({ path: path.join(__dirname, 'td_step3_after_login.png') });

    // Check if we're logged in
    const pageContent = await page.content();
    const isLoggedIn = pageContent.toLowerCase().includes('logout') || 
                       pageContent.toLowerCase().includes('browse') ||
                       !currentUrl.includes('login');
    console.log(`Logged in: ${isLoggedIn}`);

    if (isLoggedIn) {
        // Save cookies for future use
        const cookies = await context.cookies();
        const cookiesPath = path.join(__dirname, 'td_cookies.json');
        fs.writeFileSync(cookiesPath, JSON.stringify(cookies, null, 2));
        console.log(`Saved ${cookies.length} cookies to ${cookiesPath}`);

        // Now browse to the main page and understand the structure
        console.log('\nBrowsing torrents...');
        await page.goto('https://www.torrentday.com/torrents/browse.php', { waitUntil: 'networkidle', timeout: 30000 });
        await page.screenshot({ path: path.join(__dirname, 'td_step4_browse.png') });
        
        // Get page structure
        const html = await page.content();
        fs.writeFileSync(path.join(__dirname, 'td_browse.html'), html);
        console.log(`Browse page: ${html.length} chars`);

        // Try freeleech
        console.log('\nTrying freeleech page...');
        await page.goto('https://www.torrentday.com/torrents/browse.php?freeleech=1', { waitUntil: 'networkidle', timeout: 30000 });
        await page.screenshot({ path: path.join(__dirname, 'td_step5_freeleech.png') });
        const flHtml = await page.content();
        fs.writeFileSync(path.join(__dirname, 'td_freeleech.html'), flHtml);
        console.log(`Freeleech page: ${flHtml.length} chars`);

        // Try RSS
        console.log('\nTrying RSS...');
        const rssResponse = await page.goto('https://www.torrentday.com/torrents/rss.php', { waitUntil: 'networkidle', timeout: 30000 });
        const rssContent = await rssResponse.text();
        fs.writeFileSync(path.join(__dirname, 'td_rss.xml'), rssContent);
        console.log(`RSS: ${rssContent.length} chars, type: ${rssResponse.headers()['content-type'] || 'unknown'}`);

        // Try API endpoints
        const endpoints = [
            '/torrents/api.php',
            '/api.php',
            '/torrents/browse.php?json=1',
        ];
        for (const ep of endpoints) {
            try {
                const resp = await page.goto(`https://www.torrentday.com${ep}`, { timeout: 10000 });
                const ct = resp.headers()['content-type'] || '';
                const body = await resp.text();
                console.log(`  ${ep} -> ${resp.status()} (${ct}) ${body.length} chars`);
                if (ct.includes('json')) {
                    fs.writeFileSync(path.join(__dirname, `td_api_${ep.replace(/[^a-z0-9]/gi, '_')}.json`), body);
                }
            } catch (e) {
                console.log(`  ${ep} -> Error: ${e.message}`);
            }
        }
    } else {
        console.log('Login failed - check screenshot at td_step3_after_login.png');
    }

    await browser.close();
    console.log('\nDone');
})().catch(e => { console.error(e); process.exit(1); });