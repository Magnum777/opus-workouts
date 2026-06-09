from playwright.sync_api import sync_playwright

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
context = browser.new_context(viewport={'width': 1440, 'height': 900})
page = context.new_page()

try:
    # Get the article with the fenris image (ID 25000)
    page.goto('https://eveonion.com/fenris-creations-announces-ai-powered-capsuleers-will-replace-human-players-in-shocking-move/', timeout=30000)
    page.wait_for_load_state('networkidle', timeout=15000)
    page.screenshot(path='C:/Users/compj/.openclaw/workspace/media/article_25000.png', full_page=False)
    
    h1 = page.query_selector('h1')
    print(f'Article title: {h1.inner_text()[:80] if h1 else "N/A"}')
    
    # Check how the featured image is displayed
    featured = page.query_selector('.post-thumbnail, .featured-image, article img, .wp-block-image')
    if featured:
        print(f'Featured element tag: {featured.evaluate("el => el.tagName")}')
        print(f'Featured src: {featured.get_attribute("src")}')
        print(f'Featured class: {featured.get_attribute("class")}')
        style = featured.get_attribute("style") or ""
        print(f'Featured style: {style[:200]}')
    
    # Get the 24999 article  
    page.goto('https://eveonion.com/capsuleer-accidentally-arms-entire-enemy-fleet-after-purchasing-1000-missile-launchers-instead-of-ammo/', timeout=30000)
    page.wait_for_load_state('networkidle', timeout=10000)
    page.screenshot(path='C:/Users/compj/.openclaw/workspace/media/article_24999.png', full_page=False)
    print('\n--- Article 24999 ---')
    h1 = page.query_selector('h1')
    print(f'Title: {h1.inner_text()[:80] if h1 else "N/A"}')
    
    # Get 25004 article (no image yet)
    page.goto('https://eveonion.com/fenris-creations-announces-eve-online-expansion-that-players-note-is-basically-just-the-war-they-have-been-fighting-for-22-years/', timeout=30000)
    page.wait_for_load_state('networkidle', timeout=10000)
    page.screenshot(path='C:/Users/compj/.openclaw/workspace/media/article_25004.png', full_page=False)
    print('\n--- Article 25004 (no image) ---')
    h1 = page.query_selector('h1')
    print(f'Title: {h1.inner_text()[:80] if h1 else "N/A"}')
    hero = page.query_selector('.td-post-featured-image img, .post-thumbnail img, article > img')
    if hero:
        print(f'Hero src: {hero.get_attribute("src")}')
    else:
        print('No hero image found')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    browser.close()
    p.stop()