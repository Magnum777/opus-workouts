// TorrentDay login - try with longer timeout and domcontentloaded instead of networkidle
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const secretsPath = path.join(process.env.USERPROFILE, '.openclaw', 'workspace', '.secrets');
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
    const browser = await chromium.launch({ headless: false, slowMo: 100 });
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        viewport: { width: 1280, height: 900 }
    });
    const page = await context.newPage();

    // Navigate with domcontentloaded instead of networkidle
    console.log('Navigating to TorrentDay...');
    try {
        await page.goto('https://www.torrentday.com/login.php', { waitUntil: 'domcontentloaded', timeout: 60000 });
    } catch (e) {
        console.log(`Navigation: ${e.message.substring(0, 100)}`);
    }
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: path.join(__dirname, 'td_step1.png') });
    console.log('Page loaded, checking state...');

    // Get page title and URL
    console.log(`URL: ${page.url()}`);
    console.log(`Title: ${await page.title()}`);

    // Fill in credentials
    console.log('Filling credentials...');
    const usernameInput = page.locator('input[name="username"]');
    const passwordInput = page.locator('input[name="password"]');
    
    if (await usernameInput.count() > 0) {
        await usernameInput.fill(tdUser);
        await passwordInput.fill(tdPass);
        console.log('Credentials filled');
    } else {
        console.log('No username/password inputs found - checking page content');
        const html = await page.content();
        console.log(`Page length: ${html.length}`);
        // Save for inspection
        fs.writeFileSync(path.join(__dirname, 'td_login_raw.html'), html);
    }
    
    await page.screenshot({ path: path.join(__dirname, 'td_step2_filled.png') });

    // Wait for Turnstile
    console.log('Waiting for Turnstile to solve (10s)...');
    await page.waitForTimeout(10000);
    
    // Try clicking the submit button
    console.log('Looking for submit button...');
    const submitBtn = page.locator('button[type="submit"], input[type="submit"], button:has-text("Login"), button:has-text("Sign In")').first();
    if (await submitBtn.count() > 0) {
        console.log('Found submit button, clicking...');
        await submitBtn.click();
        await page.waitForTimeout(8000);
    } else {
        console.log('No submit button found');
        // Try pressing Enter
        console.log('Trying Enter key...');
        await page.keyboard.press('Enter');
        await page.waitForTimeout(8000);
    }

    const currentUrl = page.url();
    console.log(`After login URL: ${currentUrl}`);
    await page.screenshot({ path: path.join(__dirname, 'td_step3_after.png') });

    // Check if logged in
    const bodyText = await page.locator('body').innerText().catch(() => '');
    const isLoggedIn = bodyText.toLowerCase().includes('logout') || 
                       bodyText.toLowerCase().includes('my stats') ||
                       !currentUrl.includes('login');
    console.log(`Logged in: ${isLoggedIn}`);

    if (isLoggedIn) {
        // Save cookies
        const cookies = await context.cookies();
        fs.writeFileSync(path.join(__dirname, 'td_cookies.json'), JSON.stringify(cookies, null, 2));
        console.log(`Saved ${cookies.length} cookies`);

        // Browse page
        console.log('Loading browse page...');
        await page.goto('https://www.torrentday.com/torrents/browse.php', { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
        await page.waitForTimeout(3000);
        const browseHtml = await page.content();
        fs.writeFileSync(path.join(__dirname, 'td_browse.html'), browseHtml);
        console.log(`Browse page: ${browseHtml.length} chars`);

        // Freeleech
        await page.goto('https://www.torrentday.com/torrents/browse.php?freeleech=1', { waitUntil: 'domcontentloaded', timeout: 30000 }).catch(() => {});
        await page.waitForTimeout(3000);
        const flHtml = await page.content();
        fs.writeFileSync(path.join(__dirname, 'td_freeleech.html'), flHtml);
        console.log(`Freeleech page: ${flHtml.length} chars`);
    }

    await browser.close();
    console.log('Done');
})().catch(e => { console.error(`Error: ${e.message}`); process.exit(1); });