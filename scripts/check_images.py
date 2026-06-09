from playwright.sync_api import sync_playwright
import time, re

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
context = browser.new_context(viewport={'width': 1440, 'height': 900})
page = context.new_page()

articles = {
    25005: 'fenris-creations-promises-new-players-safe-space-to-learn-game-then-immediately-deletes-it-in-galaxy-wide-war',
    25004: 'fenris-creations-announces-eve-online-expansion-that-players-note-is-basically-just-the-war-they-have-been-fighting-for-22-years',
    25003: 'ccp-games-becomes-fenris-creations-promises-eve-will-outlast-the-heat-death-of-the-universe',
    24999: 'capsuleer-accidentally-arms-entire-enemy-fleet-after-purchasing-1000-missile-launchers-instead-of-ammo',
    24998: 'area-capsuleer-spends-800-million-isk-on-1000-missile-launchers-after-confusing-item-name-with-ammunition',
    24997: 'npc-achieves-top-rank-in-eve-online-pvp-event-marking-first-time-ccp-acknowledged-drone-issues',
    24996: 'npc-outranks-entire-player-base-in-ccps-pvp-fest-claims-it-was-just-doing-its-job',
    24993: 'miners-officially-stripped-of-capsuleer-status-by-concord-after-years-of-complaint-letters',
}

for post_id, slug in articles.items():
    page.goto(f'https://eveonion.com/{slug}/', timeout=15000)
    page.wait_for_load_state('networkidle', timeout=10000)
    time.sleep(3)
    
    tdb_bg = page.query_selector('.tdb-featured-image-bg')
    
    if tdb_bg:
        computed_bg = tdb_bg.evaluate("el => window.getComputedStyle(el).backgroundImage")
        match = re.search(r'/([0-9a-z_-]+\.jpg)', computed_bg)
        fname = match.group(1) if match else computed_bg[:60]
        print(f'ID {post_id}: OK - {fname}')
    else:
        print(f'ID {post_id}: MISSING .tdb-featured-image-bg')

browser.close()
p.stop()