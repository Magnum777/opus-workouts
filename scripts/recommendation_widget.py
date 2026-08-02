#!/usr/bin/env python3
"""
AI Tool Recommendation Widget Generator for aitoolalliance.com

Generates a lightweight embeddable JS widget that asks visitors what they need
and recommends AI tools with affiliate tracking. Serves as a conversion layer
on top of existing content.

The widget:
1. Asks "What are you trying to do?" with category buttons
2. Shows 3-5 tool recommendations per category
3. Links to detailed review articles on the site (internal links)
4. Appends affiliate tracking parameters to outbound links
5. Collects anonymized click data for optimization

Usage:
    python recommendation_widget.py build         # Generate widget JS + HTML
    python recommendation_widget.py test          # Test locally
    python recommendation_widget.py deploy        # Deploy to aitoolalliance via WP API
"""

import argparse
import json
import hashlib
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("C:/Users/compj/.openclaw/workspace")
OUTPUT_DIR = WORKSPACE / "scripts" / "recommendation-widget"
WIDGET_JS = OUTPUT_DIR / "ai-tool-recommender.js"
WIDGET_HTML = OUTPUT_DIR / "widget-embed.html"
WIDGET_CSS = OUTPUT_DIR / "widget-styles.css"

# Tool categories mapped to site content
TOOL_CATEGORIES = {
    "write-content": {
        "label": "Write & Create Content",
        "icon": "✍️",
        "question": "What kind of content are you creating?",
        "subcategories": [
            {"id": "blog-posts", "label": "Blog Posts & Articles"},
            {"id": "social-media", "label": "Social Media Posts"},
            {"id": "email-marketing", "label": "Email Marketing"},
            {"id": "seo-content", "label": "SEO Content"},
        ],
        "tools": [
            {"name": "Jasper", "tagline": "AI writing assistant for marketing teams", "url": "/best-ai-writing-tools/", "affiliate_id": "aitoolalliance-20", "price": "$49/mo+", "best_for": "Marketing teams"},
            {"name": "Copy.ai", "tagline": "Quick AI copy for any channel", "url": "/best-ai-copywriting-tools/", "affiliate_id": "aitoolalliance-20", "price": "Free plan", "best_for": "Quick copy"},
            {"name": "Grammarly", "tagline": "AI-powered writing assistant", "url": "/grammarly-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $12/mo", "best_for": "Editing & polish"},
            {"name": "Surfer SEO", "tagline": "Content optimization for search", "url": "/surfer-seo-review/", "affiliate_id": "aitoolalliance-20", "price": "$89/mo+", "best_for": "SEO content"},
            {"name": "Writesonic", "tagline": "Budget-friendly AI writer", "url": "/writesonic-review/", "affiliate_id": "aitoolalliance-20", "price": "$16/mo+", "best_for": "Budget writers"},
        ]
    },
    "automate-work": {
        "label": "Automate My Work",
        "icon": "🤖",
        "question": "What are you trying to automate?",
        "subcategories": [
            {"id": "workflows", "label": "Workflows & Processes"},
            {"id": "data-entry", "label": "Data Entry & Processing"},
            {"id": "customer-support", "label": "Customer Support"},
            {"id": "scheduling", "label": "Scheduling & Booking"},
        ],
        "tools": [
            {"name": "Zapier", "tagline": "Connect 6000+ apps, automate anything", "url": "/zapier-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $19.99/mo+", "best_for": "App automation"},
            {"name": "Make", "tagline": "Visual workflow automation", "url": "/make-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $9/mo+", "best_for": "Complex flows"},
            {"name": "n8n", "tagline": "Open-source automation you self-host", "url": "/n8n-review/", "affiliate_id": "aitoolalliance-20", "price": "Free (self-host)", "best_for": "Tech-savvy"},
            {"name": "Bardeen", "tagline": "AI-powered browser automation", "url": "/bardeen-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $15/mo", "best_for": "Browser tasks"},
            {"name": "Relevance AI", "tagline": "Build AI agents for your workflows", "url": "/best-ai-agent-platforms/", "affiliate_id": "aitoolalliance-20", "price": "Free trial", "best_for": "AI agents"},
        ]
    },
    "build-product": {
        "label": "Build a Product",
        "icon": "💻",
        "question": "What are you building?",
        "subcategories": [
            {"id": "saas", "label": "SaaS App"},
            {"id": "website", "label": "Website or Landing Page"},
            {"id": "mobile-app", "label": "Mobile App"},
            {"id": "api", "label": "API or Integration"},
        ],
        "tools": [
            {"name": "Cursor", "tagline": "AI-first code editor", "url": "/cursor-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $20/mo", "best_for": "Coding"},
            {"name": "V0", "tagline": "Generate React components from text", "url": "/best-ai-ui-generators/", "affiliate_id": "aitoolalliance-20", "price": "Free tier", "best_for": "Frontend"},
            {"name": "Replit", "tagline": "Code, deploy, collaborate in browser", "url": "/replit-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $25/mo", "best_for": "Quick protos"},
            {"name": "Framer", "tagline": "Design and publish websites with AI", "url": "/framer-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $5/mo", "best_for": "No-code sites"},
            {"name": "Supabase", "tagline": "Open-source Firebase alternative", "url": "/supabase-review/", "affiliate_id": "aitoolalliance-20", "price": "Free tier", "best_for": "Backend"},
        ]
    },
    "analyze-data": {
        "label": "Analyze Data",
        "icon": "📊",
        "question": "What kind of data are you working with?",
        "subcategories": [
            {"id": "spreadsheets", "label": "Spreadsheets & Reports"},
            {"id": "customer-data", "label": "Customer & Sales Data"},
            {"id": "market-research", "label": "Market Research"},
            {"id": "financial", "label": "Financial Analysis"},
        ],
        "tools": [
            {"name": "Julius AI", "tagline": "Chat with your data, get instant analysis", "url": "/julius-ai-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $20/mo", "best_for": "Quick analysis"},
            {"name": "Rows", "tagline": "Spreadsheet + AI + integrations", "url": "/rows-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $9/mo", "best_for": "Spreadsheets"},
            {"name": "Obviously AI", "tagline": "Predictive analytics without code", "url": "/obviously-ai-review/", "affiliate_id": "aitoolalliance-20", "price": "$99/mo", "best_for": "Predictions"},
            {"name": "Power BI", "tagline": "Microsoft's business intelligence platform", "url": "/power-bi-review/", "affiliate_id": "aitoolalliance-20", "price": "$10/user/mo", "best_for": "Enterprise reporting"},
        ]
    },
    "grow-business": {
        "label": "Grow My Business",
        "icon": "📈",
        "question": "What area needs growth?",
        "subcategories": [
            {"id": "seo", "label": "SEO & Traffic"},
            {"id": "social", "label": "Social Media"},
            {"id": "ads", "label": "Paid Advertising"},
            {"id": "email", "label": "Email Marketing"},
        ],
        "tools": [
            {"name": "Semrush", "tagline": "All-in-one SEO and marketing toolkit", "url": "/semrush-review/", "affiliate_id": "aitoolalliance-20", "price": "$129/mo+", "best_for": "SEO suite"},
            {"name": "Ahrefs", "tagline": "Backlinks, keywords, and content explorer", "url": "/ahrefs-review/", "affiliate_id": "aitoolalliance-20", "price": "$99/mo+", "best_for": "Link building"},
            {"name": "Mailchimp", "tagline": "Email marketing with AI features", "url": "/mailchimp-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $13/mo", "best_for": "Email"},
            {"name": "Predis.ai", "tagline": "AI social media content generator", "url": "/predis-ai-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $32/mo", "best_for": "Social posts"},
            {"name": "Google Analytics", "tagline": "Free analytics for every website", "url": "/google-analytics-setup-guide/", "affiliate_id": "", "price": "Free", "best_for": "Analytics"},
        ]
    },
    "manage-team": {
        "label": "Manage My Team",
        "icon": "👥",
        "question": "What do you need help managing?",
        "subcategories": [
            {"id": "projects", "label": "Projects & Tasks"},
            {"id": "communication", "label": "Team Communication"},
            {"id": "hiring", "label": "Hiring & HR"},
            {"id": "meetings", "label": "Meetings & Notes"},
        ],
        "tools": [
            {"name": "Notion", "tagline": "All-in-one workspace with AI", "url": "/notion-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $10/mo", "best_for": "Docs + projects"},
            {"name": "Asana", "tagline": "Project management with AI suggestions", "url": "/asana-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $10.99/mo", "best_for": "Task management"},
            {"name": "Otter.ai", "tagline": "AI meeting notes and summaries", "url": "/otter-ai-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $16.99/mo", "best_for": "Meeting notes"},
            {"name": "Loom", "tagline": "Record quick videos instead of meetings", "url": "/loom-review/", "affiliate_id": "aitoolalliance-20", "price": "Free / $12.50/mo", "best_for": "Async comms"},
        ]
    },
}


def generate_widget_js():
    """Generate the embeddable recommendation widget JavaScript."""
    categories_json = json.dumps(TOOL_CATEGORIES, indent=2)

    js = f"""/**
 * AI Tool Recommender Widget for aitoolalliance.com
 * Auto-generated by recommendation_widget.py on {datetime.now().strftime('%Y-%m-%d')}
 * 
 * Embedding: Add <div id="ai-tool-recommender"></div> and include this script.
 */
(function() {{
    'use strict';
    
    const CATEGORIES = {categories_json};
    const AFFILIATE_TAG = 'aitoolalliance-20';
    const SITE_BASE = 'https://aitoolalliance.com';
    
    // Simple state
    let currentStep = 'category';  // category | subcategory | results
    let selectedCategory = null;
    let selectedSubcategory = null;
    
    function createEl(tag, attrs = {{}}, children = []) {{
        const el = document.createElement(tag);
        Object.entries(attrs).forEach(([k, v]) => {{
            if (k === 'className') el.className = v;
            else if (k === 'innerHTML') el.innerHTML = v;
            else if (k.startsWith('on')) el.addEventListener(k.slice(2).toLowerCase(), v);
            else el.setAttribute(k, v);
        }});
        children.forEach(c => {{
            if (typeof c === 'string') el.appendChild(document.createTextNode(c));
            else if (c) el.appendChild(c);
        }});
        return el;
    }}
    
    function trackClick(action, label) {{
        // Anonymized click tracking - no PII
        if (typeof gtag !== 'undefined') {{
            gtag('event', 'recommender_click', {{
                event_category: 'ai_tool_recommender',
                event_action: action,
                event_label: label
            }});
        }}
        console.log('[Recommender]', action, label);
    }}
    
    function buildCategoryStep() {{
        const container = createEl('div', {{ className: 'rec-step' }});
        container.appendChild(createEl('h3', {{ className: 'rec-title', innerHTML: 'What are you trying to do?' }}));
        container.appendChild(createEl('p', {{ className: 'rec-subtitle', innerHTML: 'Pick a category and we\\'ll recommend the best AI tools for you' }}));
        
        const grid = createEl('div', {{ className: 'rec-grid' }});
        Object.entries(CATEGORIES).forEach(([key, cat]) => {{
            const card = createEl('div', {{ 
                className: 'rec-card',
                innerHTML: `<span class="rec-icon">${{cat.icon}}</span><span class="rec-card-title">${{cat.label}}</span>`
            }});
            card.addEventListener('click', () => {{
                trackClick('category_select', key);
                selectedCategory = key;
                currentStep = 'subcategory';
                render();
            }});
            grid.appendChild(card);
        }});
        container.appendChild(grid);
        return container;
    }}
    
    function buildSubcategoryStep() {{
        const cat = CATEGORIES[selectedCategory];
        const container = createEl('div', {{ className: 'rec-step' }});
        
        const backBtn = createEl('button', {{ className: 'rec-back', innerHTML: '← Back' }});
        backBtn.addEventListener('click', () => {{ currentStep = 'category'; render(); }});
        container.appendChild(backBtn);
        
        container.appendChild(createEl('h3', {{ className: 'rec-title', innerHTML: cat.question }}));
        
        const list = createEl('div', {{ className: 'rec-subcategories' }});
        cat.subcategories.forEach(sub => {{
            const item = createEl('div', {{ className: 'rec-sub-item', innerHTML: sub.label }});
            item.addEventListener('click', () => {{
                trackClick('subcategory_select', sub.id);
                selectedSubcategory = sub.id;
                currentStep = 'results';
                render();
            }});
            list.appendChild(item);
        }});
        container.appendChild(list);
        return container;
    }}
    
    function buildResultsStep() {{
        const cat = CATEGORIES[selectedCategory];
        const container = createEl('div', {{ className: 'rec-step' }});
        
        const backBtn = createEl('button', {{ className: 'rec-back', innerHTML: '← Back' }});
        backBtn.addEventListener('click', () => {{ currentStep = 'subcategory'; render(); }});
        container.appendChild(backBtn);
        
        container.appendChild(createEl('h3', {{ className: 'rec-title', innerHTML: `Top picks for ${{cat.label.toLowerCase()}}` }}));
        
        const tools = createEl('div', {{ className: 'rec-tools' }});
        cat.tools.forEach(tool => {{
            const affiliateUrl = tool.affiliate_id 
                ? `${{SITE_BASE}}${{tool.url}}?tag=${{tool.affiliate_id}}`
                : `${{SITE_BASE}}${{tool.url}}`;
            
            const card = createEl('div', {{ className: 'rec-tool-card' }});
            card.innerHTML = `
                <div class="rec-tool-header">
                    <span class="rec-tool-name">${{tool.name}}</span>
                    <span class="rec-tool-price">${{tool.price}}</span>
                </div>
                <p class="rec-tool-tagline">${{tool.tagline}}</p>
                <div class="rec-tool-footer">
                    <span class="rec-tool-best">Best for: ${{tool.best_for}}</span>
                    <a href="${{affiliateUrl}}" class="rec-tool-link" target="_blank" rel="noopener noreferrer">See Full Review →</a>
                </div>
            `;
            
            card.querySelector('.rec-tool-link').addEventListener('click', () => {{
                trackClick('tool_click', tool.name);
            }});
            
            tools.appendChild(card);
        }});
        container.appendChild(tools);
        
        // CTA for full list
        const cta = createEl('div', {{ className: 'rec-cta' }});
        cta.innerHTML = `Want more options? <a href="${{SITE_BASE}}/best-ai-tools/" target="_blank" rel="noopener">See all AI tool reviews →</a>`;
        container.appendChild(cta);
        
        return container;
    }}
    
    function render() {{
        const root = document.getElementById('ai-tool-recommender');
        if (!root) return;
        root.innerHTML = '';
        
        let step;
        switch(currentStep) {{
            case 'category': step = buildCategoryStep(); break;
            case 'subcategory': step = buildSubcategoryStep(); break;
            case 'results': step = buildResultsStep(); break;
        }}
        root.appendChild(step);
    }}
    
    // Auto-init when DOM ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', render);
    }} else {{
        render();
    }}
    
}})();
"""
    return js


def generate_widget_css():
    """Generate CSS for the recommendation widget."""
    return """/* AI Tool Recommender Widget Styles */
#ai-tool-recommender {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 720px;
    margin: 2rem auto;
    padding: 1.5rem;
    background: #f8f9fb;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
}

.rec-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 0.5rem 0;
}

.rec-subtitle {
    font-size: 0.95rem;
    color: #6b7280;
    margin: 0 0 1.25rem 0;
}

.rec-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
}

.rec-card {
    background: #fff;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
}

.rec-card:hover {
    border-color: #6366f1;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
    transform: translateY(-2px);
}

.rec-icon {
    font-size: 1.8rem;
    display: block;
    margin-bottom: 0.4rem;
}

.rec-card-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #374151;
}

.rec-subcategories {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.rec-sub-item {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.95rem;
}

.rec-sub-item:hover {
    background: #6366f1;
    color: #fff;
    border-color: #6366f1;
}

.rec-back {
    background: none;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 0.4rem 0.8rem;
    cursor: pointer;
    font-size: 0.85rem;
    color: #6b7280;
    margin-bottom: 1rem;
}

.rec-back:hover {
    background: #f3f4f6;
}

.rec-tools {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.rec-tool-card {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 1rem;
    transition: box-shadow 0.2s ease;
}

.rec-tool-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.rec-tool-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.3rem;
}

.rec-tool-name {
    font-weight: 700;
    font-size: 1.05rem;
    color: #111827;
}

.rec-tool-price {
    font-size: 0.8rem;
    color: #6366f1;
    font-weight: 600;
}

.rec-tool-tagline {
    font-size: 0.9rem;
    color: #4b5563;
    margin: 0.3rem 0 0.5rem 0;
}

.rec-tool-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.rec-tool-best {
    font-size: 0.8rem;
    color: #9ca3af;
}

.rec-tool-link {
    font-size: 0.85rem;
    color: #6366f1;
    text-decoration: none;
    font-weight: 600;
}

.rec-tool-link:hover {
    text-decoration: underline;
}

.rec-cta {
    text-align: center;
    margin-top: 1.25rem;
    font-size: 0.9rem;
    color: #6b7280;
}

.rec-cta a {
    color: #6366f1;
    text-decoration: none;
    font-weight: 600;
}

.rec-cta a:hover {
    text-decoration: underline;
}

@media (max-width: 480px) {
    .rec-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .rec-tool-footer {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.3rem;
    }
}
"""


def generate_embed_html():
    """Generate the HTML snippet to embed the widget in a WordPress page."""
    css = generate_widget_css()
    return f"""<!-- AI Tool Recommender Widget -->
<style>
{css}
</style>
<div id="ai-tool-recommender"></div>
<script src="/wp-content/uploads/ai-tool-recommender/ai-tool-recommender.js" defer></script>
"""


def cmd_build():
    """Build the widget files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    js_content = generate_widget_js()
    WIDGET_JS.write_text(js_content, encoding='utf-8')
    print(f"Built: {WIDGET_JS} ({len(js_content)} bytes)")
    
    css_content = generate_widget_css()
    WIDGET_CSS.write_text(css_content, encoding='utf-8')
    print(f"Built: {WIDGET_CSS} ({len(css_content)} bytes)")
    
    html_content = generate_embed_html()
    WIDGET_HTML.write_text(html_content, encoding='utf-8')
    print(f"Built: {WIDGET_HTML} ({len(html_content)} bytes)")
    
    # Also export categories as JSON for easy updates
    categories_json = json.dumps(TOOL_CATEGORIES, indent=2, ensure_ascii=False)
    categories_file = OUTPUT_DIR / "categories.json"
    categories_file.write_text(categories_json, encoding='utf-8')
    print(f"Built: {categories_file} ({len(categories_json)} bytes)")
    
    print(f"\nWidget built successfully!")
    print(f"  Categories: {len(TOOL_CATEGORIES)}")
    print(f"  Total tools: {sum(len(c['tools']) for c in TOOL_CATEGORIES.values())}")
    print(f"  Embed HTML in {WIDGET_HTML}")


def cmd_test():
    """Create a local test page."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Make sure JS exists
    if not WIDGET_JS.exists():
        cmd_build()
    
    css = generate_widget_css()
    js = WIDGET_JS.read_text(encoding='utf-8')
    
    test_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Tool Recommender Widget Test</title>
</head>
<body style="max-width:800px;margin:2rem auto;font-family:sans-serif;">
    <h1>AI Tool Recommender - Test Page</h1>
    <p>This simulates how the widget will appear on aitoolalliance.com</p>
    <style>{css}</style>
    <div id="ai-tool-recommender"></div>
    <script>{js}</script>
</body>
</html>"""
    
    test_file = OUTPUT_DIR / "test.html"
    test_file.write_text(test_html, encoding='utf-8')
    print(f"Test page: {test_file}")
    print(f"Open in browser to test the widget.")


def cmd_deploy():
    """Deploy widget files to aitoolalliance via WordPress REST API."""
    import sys
    sys.path.insert(0, str(WORKSPACE / "scripts"))
    from creds import get_wp_site, get_wp_auth_header
    
    site_config = get_wp_site("aitoolalliance")
    if not site_config:
        print("ERROR: Could not get aitoolalliance credentials")
        return
    
    base_url = site_config['url'].rstrip('/')
    headers = get_wp_auth_header("aitoolalliance")
    if not headers:
        print("ERROR: Could not get auth headers")
        return
    
    import requests
    
    # Ensure JS exists
    if not WIDGET_JS.exists():
        cmd_build()
    
    # Upload JS file as media
    js_content = WIDGET_JS.read_text(encoding='utf-8')
    
    # Create the upload payload
    files = {
        'file': ('ai-tool-recommender.js', js_content.encode('utf-8'), 'application/javascript')
    }
    data = {
        'title': 'AI Tool Recommender Widget',
    }
    
    print(f"Uploading widget JS to {base_url}...")
    try:
        resp = requests.post(
            f"{base_url}/wp-json/wp/v2/media",
            headers=headers,
            files=files,
            data=data,
            timeout=30
        )
        if resp.status_code in (200, 201):
            media = resp.json()
            js_url = media.get('source_url', '')
            print(f"JS uploaded: {js_url}")
        else:
            print(f"Upload failed: {resp.status_code} {resp.text[:200]}")
            print("You may need to upload manually via WP admin.")
            return
    except Exception as e:
        print(f"Upload error: {e}")
        print("You may need to upload manually via WP admin.")
        return
    
    # Upload CSS as media
    css_content = generate_widget_css()
    files = {
        'file': ('ai-tool-recommender.css', css_content.encode('utf-8'), 'text/css')
    }
    
    print(f"Uploading widget CSS to {base_url}...")
    try:
        resp = requests.post(
            f"{base_url}/wp-json/wp/v2/media",
            headers=headers,
            files=files,
            data={'title': 'AI Tool Recommender Styles'},
            timeout=30
        )
        if resp.status_code in (200, 201):
            media = resp.json()
            css_url = media.get('source_url', '')
            print(f"CSS uploaded: {css_url}")
        else:
            print(f"CSS upload failed: {resp.status_code}")
    except Exception as e:
        print(f"CSS upload error: {e}")
    
    print(f"\nDeployment complete!")
    print(f"\nTo embed the widget, add this HTML to any page or post:")
    print(f'<div id="ai-tool-recommender"></div>')
    print(f'<link rel="stylesheet" href="{css_url or "/wp-content/uploads/ai-tool-recommender.css"}">')
    print(f'<script src="{js_url or "/wp-content/uploads/ai-tool-recommender.js"}" defer></script>')


def main():
    parser = argparse.ArgumentParser(description="AI Tool Recommendation Widget Generator")
    parser.add_argument('command', choices=['build', 'test', 'deploy'],
                       help='build: generate widget files, test: create test page, deploy: upload to WP')
    args = parser.parse_args()
    
    if args.command == 'build':
        cmd_build()
    elif args.command == 'test':
        cmd_test()
    elif args.command == 'deploy':
        cmd_deploy()


if __name__ == '__main__':
    main()