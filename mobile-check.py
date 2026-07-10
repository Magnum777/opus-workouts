from playwright.sync_api import sync_playwright
import json

def check_mobile_page():
    results = {
        "horizontal_scroll": {"pass": True, "details": []},
        "touch_targets": {"pass": True, "details": [], "violations": []},
        "image_overflow": {"pass": True, "details": []}
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()
        
        # Navigate and wait
        page.goto("https://magnum777.github.io/ga-parks-propagation/?_nocache=1")
        page.wait_for_timeout(5000)
        
        # 1. Check horizontal scrolling
        scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
        client_width = page.evaluate("() => document.documentElement.clientWidth")
        
        if scroll_width > client_width:
            results["horizontal_scroll"]["pass"] = False
            results["horizontal_scroll"]["details"].append(
                f"scrollWidth ({scroll_width}) > clientWidth ({client_width})"
            )
        else:
            results["horizontal_scroll"]["details"].append(
                f"scrollWidth ({scroll_width}) <= clientWidth ({client_width}) - OK"
            )
        
        # Also check body
        body_scroll = page.evaluate("() => document.body.scrollWidth")
        body_client = page.evaluate("() => document.body.clientWidth")
        if body_scroll > body_client:
            results["horizontal_scroll"]["pass"] = False
            results["horizontal_scroll"]["details"].append(
                f"body scrollWidth ({body_scroll}) > body clientWidth ({body_client})"
            )
        
        # 2. Check touch targets >= 44x44px
        # Use JS evaluation for more reliable element checking
        touch_data = page.evaluate("""
            () => {
                const results = { checked: 0, violations: [] };
                const selectors = 'a, button, input, select, textarea, [role="button"], [onclick], [tabindex]:not([tabindex="-1"])';
                const elements = document.querySelectorAll(selectors);
                
                elements.forEach(el => {
                    // Skip hidden elements
                    if (el.offsetParent === null) return;
                    if (!el.checkVisibility || !el.checkVisibility()) {
                        // Fallback visibility check
                        const style = window.getComputedStyle(el);
                        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return;
                    }
                    
                    // Skip leaflet-proxy elements
                    if (el.classList && el.classList.contains('leaflet-proxy')) return;
                    
                    // Skip elements inside hidden nav/collapsed menus
                    let parent = el.parentElement;
                    for (let i = 0; i < 5 && parent; i++) {
                        const pStyle = window.getComputedStyle(parent);
                        if (pStyle.display === 'none' || pStyle.visibility === 'hidden' || pStyle.maxHeight === '0px') {
                            return;
                        }
                        if (parent.classList) {
                            const classes = Array.from(parent.classList);
                            if (classes.some(c => c.includes('collapse') && !parent.classList.contains('show'))) {
                                return;
                            }
                        }
                        parent = parent.parentElement;
                    }
                    
                    const rect = el.getBoundingClientRect();
                    const width = rect.width;
                    const height = rect.height;
                    
                    // Skip zero-size elements
                    if (width === 0 || height === 0) return;
                    
                    results.checked++;
                    
                    if (width < 44 || height < 44) {
                        results.violations.push({
                            tag: el.tagName.toLowerCase(),
                            id: el.id || '',
                            class: el.className || '',
                            text: (el.innerText || el.textContent || '').substring(0, 50),
                            width: Math.round(width * 10) / 10,
                            height: Math.round(height * 10) / 10
                        });
                    }
                });
                
                return results;
            }
        """)
        
        results["touch_targets"]["details"].append(f"Checked {touch_data['checked']} visible interactive elements")
        
        if touch_data["violations"]:
            results["touch_targets"]["pass"] = False
            results["touch_targets"]["violations"] = touch_data["violations"]
        
        # 3. Check image overflow
        img_data = page.evaluate("""
            () => {
                const results = { checked: 0, issues: [] };
                const images = document.querySelectorAll('img');
                const viewportWidth = window.innerWidth;
                
                images.forEach(img => {
                    if (img.offsetParent === null) return;
                    
                    // Skip Leaflet map tiles — they intentionally overflow for panning
                    const src = img.src || '';
                    if (src.includes('basemaps.cartocdn.com') || src.includes('tile') ||
                        (img.classList && img.classList.contains('leaflet-tile'))) return;
                    
                    const rect = img.getBoundingClientRect();
                    results.checked++;
                    
                    // Check if image extends beyond viewport horizontally
                    if (rect.right > viewportWidth || rect.left < 0) {
                        results.issues.push(`Image overflows: src=${img.src.substring(0, 100)}, x=${Math.round(rect.x)}, width=${Math.round(rect.width)}`);
                    }
                    
                    // Check computed style
                    const style = window.getComputedStyle(img);
                    if (style.maxWidth === 'none' && rect.width > viewportWidth) {
                        results.issues.push(`Image too wide without max-width: src=${img.src.substring(0, 100)}, width=${Math.round(rect.width)}`);
                    }
                });
                
                return results;
            }
        """)
        
        if img_data["issues"]:
            results["image_overflow"]["pass"] = False
            results["image_overflow"]["details"].extend(img_data["issues"])
        else:
            results["image_overflow"]["details"].append(f"Checked {img_data['checked']} images - no overflow found")
        
        browser.close()
    
    return results

if __name__ == "__main__":
    results = check_mobile_page()
    print(json.dumps(results, indent=2))
