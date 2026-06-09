from playwright.sync_api import sync_playwright

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
context = browser.new_context(viewport={'width': 1440, 'height': 900})
page = context.new_page()

try:
    # Get the homepage to see recent articles
    page.goto('https://eveonion.com', timeout=30000)
    page.wait_for_load_state('networkidle', timeout=15000)
    print('Homepage title:', page.title())
    page.screenshot(path='C:/Users/compj/.openclaw/workspace/media/eveonion_homepage.png', full_page=False)
    print('Homepage screenshot saved')

    # Get article links from homepage
    articles = page.query_selector_all('article, .post, .entry')
    print(f'Found {len(articles)} article elements')
    
    # Try to find featured images on homepage
    imgs = page.query_selector_all('img')
    print(f'Found {len(imgs)} images total')
    for img in imgs[:10]:
        src = img.get_attribute('src') or ''
        alt = img.get_attribute('alt') or ''
        cls = img.get_attribute('class') or ''
        if any(x in cls.lower() for x in ['post', 'article', 'feature', 'thumb']):
            print(f'  Article img: class={cls[:50]} src={src[:80]}')

    # Navigate to a few articles and screenshot their featured images
    links = page.query_selector_all('a[href*="/202"]')
    print(f'Found {len(links)} article links')
    
    visited = []
    for link in links[:8]:
        href = link.get_attribute('href')
        if href and href not in visited and '/202' in href:
            visited.append(href)
            if len(visited) >= 4:
                break
    
    for i, url in enumerate(visited):
        print(f'\n--- Article {i+1}: {url}')
        page.goto(url, timeout=30000)
        page.wait_for_load_state('networkidle', timeout=10000)
        page.screenshot(path=f'C:/Users/compj/.openclaw/workspace/media/eveonion_article_{i+1}.png', full_page=False)
        
        # Find the featured image
        hero = page.query_selector('.post-thumbnail img, .featured-image img, article img:first-of-type, .wp-post-image')
        if hero:
            print(f'  Featured img: {hero.get_attribute("src")}')
        
        # Get page title
        h1 = page.query_selector('h1')
        if h1:
            print(f'  Title: {h1.inner_text()[:60]}')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
finally:
    browser.close()
    p.stop()