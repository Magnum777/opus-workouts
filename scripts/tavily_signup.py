from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_viewport_size({'width': 1280, 'height': 800})
    page.goto('https://app.tavily.com/register', timeout=20000)
    page.wait_for_load_state('domcontentloaded', timeout=15000)
    
    username_field = page.query_selector('input[name="username"]')
    if username_field:
        username_field.fill('nova+tavily@wittyspeech685.agentmail.to')
        print('Filled email')
    
    continue_btn = page.query_selector('button:has-text("Continue")')
    if continue_btn:
        continue_btn.click()
        print('Clicked Continue')
        page.wait_for_timeout(5000)
        print('URL after:', page.url)
        print('Title:', page.title())
        
        password_field = page.query_selector('input[type="password"]')
        if password_field:
            print('Password field appeared - setup in progress')
        
        errors = page.query_selector_all('[class*="error"]')
        for e in errors[:3]:
            print('Error:', e.inner_text()[:100])
    
    browser.close()
