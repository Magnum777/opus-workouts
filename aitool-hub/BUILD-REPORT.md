# aitoolalliance.com Hub Page Build Report
**Sub-Agent:** content-builder-aitool | **Date:** 2026-04-07

---

## WP DATABASE AUDIT FINDINGS

### Custom Post Types / DB Structure
- **No custom post types detected** — WordPress REST API only exposes `post` and `page` (plus `attachment`, `nav_menu_item`, `wp_block`, `wp_template`)
- **No ACF fields** — Advanced Custom Fields not active on this install
- **No WP All Import data** — No evidence of import plugin structure
- **No tool directory** — The site currently operates as a blog with AI tool reviews/articles, NOT a directory. Existing content is editorial reviews (Jasper, CopyAI, ChatGPT Plus, etc.)
- **Existing post categories:** `category` (uncategorized, and ad-hoc blog categories like "AI Agents", "Productivity", etc.)
- **Theme:** Standard WordPress (no visible custom theme structure from sitemap)
- **Conclusion:** No proprietary tool database to export. Must build the programmatic pages from scratch using public data sources (tool websites, G2, Capterra, Product Hunt, AlternativeTo)

### Existing Content That Already Exists (source data):
- Jasper AI review, CopyAI review, ChatGPT Plus review, Canva AI, Grammarly, Tidio AI, Writesonic, Midjourney vs DALL-E
- Category round-ups: Best AI tools for small business, best AI scheduling assistants, best AI chatbot tools, etc.

---

## HUB PAGES BUILT

### 1. `/alternatives/` — Main Alternatives Hub
**URL:** `https://aitoolalliance.com/alternatives/`
**Type:** WordPress Page (hub page, parent of category hubs)
**Purpose:** Landing page linking to all category hub pages

### 2. `/alternatives/chatbots/` — Chatbots Category Hub
**URL:** `https://aitoolalliance.com/alternatives/chatbots/`
**Type:** WordPress Page (category hub, child of /alternatives/)
**Purpose:** Lists all chatbot tool alternatives pages

---

## GUTENBERG/HTML TEMPLATE

**File:** `template-single-alternative.html`
**Applies to:** `/alternatives/{category}/{tool-slug}/` URLs
**Structure (8 sections per strategy doc §4b):**
1. Hero Block — H1, intro paragraph, meta description
2. Quick-Start Comparison Table — Tool | Best For | Price | Free Tier | Rating
3. Top 3 Alternatives Deep Dives — per tool: description, standout feature, pricing, CTA link
4. Alternatives by Use Case — conditional sub-sections
5. Feature Comparison Table — multi-tool feature matrix
6. How to Choose — decision framework (~150 words)
7. Verdict / Summary — 3–4 persona-based bullet recommendations
8. Internal Links — category hub, related pages, cross-site links

---

## 3 SEEDED INDIVIDUAL PAGES

| Page | URL | Status |
|------|-----|--------|
| ChatGPT Alternatives | `/alternatives/chatbots/chatgpt-alternatives/` | ✅ READY TO CREATE — content written |
| Claude Alternatives | `/alternatives/chatbots/claude-alternatives/` | ✅ READY TO CREATE — content written |
| ChatSonic Alternatives | `/alternatives/chatbots/chatsonic-alternatives/` | ✅ READY TO CREATE — content written |

All 3 use real data: tool names, pricing, features from public sources.

---

## TECHNICAL NOTES FOR WORDPRESS ADMIN

1. **Pages must be created first** — `/alternatives/` → `/alternatives/chatbots/` before any individual tool pages (internal linking depends on hub hierarchy)
2. **No database tool** — Content must be created manually in WP admin or via REST API with authentication
3. **Template approach:** Use WordPress Page Templates (page-alternatives.php) or Gutenberg reusable blocks
4. **URL structure requires:** WordPress pages with matching slugs (not posts)
5. **Internal linking:** Each tool page links to: chatbots hub, other chatbot tool pages, aibusinessinsider.org "best AI chatbot tools" page
6. **Next steps:** Create pages in WP admin using the content in `pages/` directory, then expand to 50–200 tool alternatives pages following the template
