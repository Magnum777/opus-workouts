from playwright.sync_api import sync_playwright

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
context = browser.new_context(viewport={'width': 1440, 'height': 900})
page = context.new_page()

try:
    page.goto('https://eveonion.com/fenris-creations-announces-ai-powered-capsuleers-will-replace-human-players-in-shocking-move/', timeout=30000)
    page.wait_for_load_state('networkidle', timeout=15000)
    page.screenshot(path='C:/Users/compj/.openclaw/workspace/media/article_25000_full.png', full_page=False)
    
    # Try to find all images
    imgs = page.query_selector_all('img')
    print(f'All images on page: {len(imgs)}')
    for img in imgs:
        src = img.get_attribute('src') or ''
        cls = img.get_attribute('class') or ''
        if any(x in src.lower() for x in ['wp-content', 'uploads', 'media']) or any(x in cls.lower() for x in ['feature', 'post', 'thumb']):
            print(f'  src={src[:100]}')
            print(f'  cls={cls[:80]}')
            print()

    # Try to find h1
    h1s = page.query_selector_all('h1, .entry-title')
    print(f'Headings found: {len(h1s)}')
    for h in h1s:
        print(f'  tag={h.evaluate("el => el.tagName")} text={h.inner_text()[:80]}')
    
    # Look at body content structure
    body_class = page.query_selector('body').get_attribute('class') or ''
    print(f'Body class: {body_class[:100]}')
    
    # Try to find article tag
    article = page.query_selector('article')
    if article:
        print(f'Article found, class: {article.get_attribute("class")}')
        # Check article's first child
        children = article.query_selector_all(':scope > *')
        print(f'Article children ({len(children)}):')
        for c in children[:5]:
            print(f'  tag={c.evaluate("el => el.tagName")} cls={c.get_attribute("class") or ""} id={c.get_attribute("id") or ""}')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    browser.close()
    p.stop()