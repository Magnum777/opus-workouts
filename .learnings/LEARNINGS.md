# Nova Learnings Archive

## 2026-06-14 (late) - Weekly ClawHub Skill Discovery Scan

**Category:** insight

**Scan date:** 2026-06-14 (Sunday, technically overdue from Friday)

**Query coverage:** 8 searches across TradeBot, browser, social media, WordPress, email, data analysis, Discord, and agent workflow categories.

**Findings — skills we don't have yet but worth noting:**

| Skill | Relevance | Why Interesting |
|-------|-----------|----------------|
| `social-media-content` | **3.690** | Highest relevance we've seen on ClawHub. Pillow/OpenCV-based image gen with brand templates. Complements our existing `ai-social-media-content` — they do different things (image generation vs text/media gen). Worth a look. |
| `data-report-generator` | 0.090 | CSV/Excel → Word/PDF with charts. Would sit nicely between `duckdb-cli-ai-skills` (analysis) and `word-docx`/`pdf-pro` (document output). Actually fills a gap. |
| `data-analysis-report-generator` | 0.507 | Professional HTML reports with ECharts interactive charts. 11 style templates (FT, McKinsey, Economist, etc.). Python-based. More polished output than in-house alternatives. |
| `oo-discordbot` | 1.125 | Discord bot management via OOMOL connector. We don't have a general Discord bot skill. Could be useful if we start managing Discord bots programmatically. |

**Skills we searched for that we already have covered:**
- Solana/trading: ✅ `solana-payments-wallets-trading` installed
- Browser automation: ✅ 3 skills (`browser-use`, `browser-auto-plus`, `playwright-browser-automation`, `agent-browser-clawdbot`)
- Social media: ✅ `ai-social-media-content` + `upload-post`
- WordPress/SEO: ✅ `wordpress-pro`, `wordpress-api-pro`, `programmatic-seo`, `wordpress-remote-news-publisher`
- Email/inbox: ✅ `agentmail-integration`, `cold-email-engine`
- Data analysis: ✅ `duckdb-cli-ai-skills`, `excel-xlsx`
- Agent workflow: ✅ `agent-workflow-playbook`, `evalanche`

**Note:** ClawHub search returns vector similarity scores (relevance), not star ratings. The >4.0 filter doesn't apply to ClawHub's scoring scheme.

**Flagged for Opus: `social-media-content`** — high relevance score (3.690), uses actual image generation with OpenCV/Pillow, which is different from our `ai-social-media-content` text/media generation approach. Could be complementary. Also `data-report-generator` + `data-analysis-report-generator` could fill a reporting gap.

## 2026-06-14 - Sojourn Church Network: RED LINES

**Context:** Audited church's UniFi network. API key is read-only Site Manager token.

**ABSOLUTE RULES from Opus (non-negotiable):**
- **NEVER modify church network without EXPRESS written permission**
- **CHANGE FREEZE WINDOWS:**
  - Sundays: ALL DAY (church services)
  - Tue-Fri: 7 AM - 7 PM (active hours)
- **Read-only monitoring only** - no restarts, no config changes, no firmware updates
- **Treat as production with zero-tolerance change policy**

**Why:** Congregation depends on WiFi for services, livestreaming, check-ins. Downtime = service disruption.

**Current status:** Read-only audit done. No changes made. Will not attempt writes without explicit "yes change X" from Opus, timed outside freeze windows.

---

## 2026-06-06 - Cron Model Assignment Fix

**Issue:** Kybernauts-Propaganda and Kybernauts-ForumBump crons were failing with "Agent couldn't generate a response" when assigned to `kimi-k2.6`.

**Root cause:** `kimi-k2.6` appears to timeout or struggle on ops/scans tasks that involve browser automation, exec commands, and tool-heavy workflows. The model works fine for creative writing but not for agent-turn cron payloads with complex tool use.

**Fix:** Switched both back to `deepseek-v4-flash:cloud` per AGENTS.md rule - "Use deepseek-v4-flash for ops/scans (checks, sweeps, data pulls, simple reports)."

**Lesson:** Don't default to kimi-k2.6 for all cron tasks just because it's the main model. Match model to task type. Document this in scheduler.md.

---

## 2026-06-14 - Weekly Skill Discovery Scan

**Scanned 11 queries on ClawHub. Results:**

**New skills worth flagging:**

| Skill | Rating | What it does | Relevance |
|-------|--------|-------------|-----------|
| `agent-workflow-playbook` | 1.133 | Multi-agent orchestration framework with design patterns for autonomous AI systems | High - we run TradeBot + EveOnion + Kybernauts in parallel; could improve coordination |
| `szzg007-web-deep-research` | 2.590 | Deep research across 17+ platforms, auto-generates market/competitor reports with risk analysis | High - could replace/supplement our manual research for TradeBot token scouting |
| `azure-flux-image-gen` | 1.133 | FLUX.2-pro image generation via Azure AI Foundry | Medium - we already have `ai-social-media-content` for images; this is Azure-backed, might have different quality/cost |
| `mflux` | 0.520 | Local FLUX.2 image generation via Apple MLX (MLX-only, macOS) | Low - we don't have Apple Silicon, and we prefer cloud for crons |

**Already installed that showed up in search:**
- `ai-social-media-content` - content generation (already have)
- `browser-use` - browser automation (already have)
- `openclaw-tavily-search` - web search (already have)

**Action:** None installed. `agent-workflow-playbook` and `szzg007-web-deep-research` look interesting but would need evaluation against our current workflows. Recommend waiting for a slow day if Opus wants to test them.

---

## 2026-06-14 - Weekly Skill Discovery Scan

**Category:** insight — Weekly ClawHub skill discovery (Friday scan, ran Sunday evening)

**Searches performed:** solana trading crypto, browser automation screenshot, social media content creator, wordpress seo publishing, email automation inbox, data analysis sql csv, discord bot automation, ai agent workflow + additional queries (explore, scraping, monitoring, wordpress, email)

**Installed skills checked against:** All 25 skills currently in lockfile.

### New Skills Found (Not Installed)

| Skill | Version | Summary | Flag |
|-------|---------|---------|------|
| **wordpress-api-pro** (benkalsky) | 3.8.1 | Production-grade WP REST API: posts, pages, WooCommerce, Elementor, ACF, JetEngine, SEO meta, multi-site. Updated Jun 9. | 🔴 **POTENTIAL UPGRADE** — our `wordpress-pro` is v0.1.0; this is much more mature with WooCommerce/Elementor/ACF support |
| **browser-auto-plus** (534422530) | 2.0.0 | Enhanced browser automation with error recovery, retry logic, multi-browser, screenshot verification | 🟡 Overlaps with `browser-use` + `agent-browser-clawdbot`; error recovery features could be useful |
| **agentmail-integration** (synesthesia-wav) | 1.1.0 | AgentMail API for AI agent email — dedicated inboxes, webhooks, replaces Gmail for agent workflows | 🟡 Alternative to our Gmail-based `iris` inbox triage |
| **youtube-transcript-native-node** (jwestburg) | 1.1.4 | Extract YouTube captions, zero npm dependencies. Updated today. | 🟡 Useful for content creation pipeline |
| **humanized-writing-editor** (juanbastias) | 1.0.0 | Rewrite AI/stiff text into natural human writing | Created today (Jun 14) — lightweight quality-of-life skill |
| **factual-claim-verifier** (juanbastias) | 1.0.0 | Check factual claims before publication | Created today — pairs with content pipeline |
| **process-interviewer** (juanbastias) | 1.0.0 | Interview users before automating/documenting workflows | Created today — interesting for SOP creation |
| **doc-weaver** (harrylabsj) | 1.0.1 | Markdown/outlines → polished Word/PDF docs with templates | 🟡 Overlaps with `word-docx` |
| **evalanche** (ijaack) | 1.11.0 | Multi-EVM agent wallet SDK, onchain identity, cross-chain liquidity | 🟡 Adjacent to our Solana wallet trading — but EVM, not Solana |
| **wordpress-remote-news-publisher** (promoweb) | 1.0.0 | Auto news publishing via SSH + WP-CLI | 🟡 Adjacent to WordPress publishing pipeline |
| **data-analysis-reporting** (gitcanadabrett) | 0.1.0 | CSV, SQLite, spreadsheet analysis | Overlaps with duckdb-cli-ai-skills — less powerful |
| **telegram-discord-bot-dev** (katrina-jpg) | 1.0.0 | Discord/Telegram bot development with trading, gaming | Adjacent — we have Discord basics already |
| **cold-email-engine** (merjua14) | 1.0.0 | Cold email outreach with drip sequences, CAN-SPAM, lead enrichment | — |
| **resend-send-native-node** (jwestburg) | 1.0.12 | Send email via Resend, zero deps | Alternative email API skill |
| **space-duck** (askegor) | 0.4.2 | AI agent identity network on Space Duck | Experimental/niche |

**Already installed that showed up in searches:**
- `solana-payments-wallets-trading` (0.3.4)
- `wordpress-pro` (0.1.0)
- `ai-social-media-content` (0.1.5)
- `browser-use` (2.0.1)
- `agent-browser-clawdbot` (0.1.0)
- `openclaw-tavily-search` (0.1.0)
- `agent-workflow-playbook` (1.1.2)

### ⚠️ Recommendation for Opus

**Priority: `wordpress-api-pro` v3.8.1** — Our current `wordpress-pro` is v0.1.0 with basic functionality. `wordpress-api-pro` has full WooCommerce, Elementor, ACF, JetEngine, SEO meta, and batch operations. If we're serious about the content empire, this is a significant upgrade. Worth evaluating.

**Watch:** `humanized-writing-editor` and `factual-claim-verifier` (both released today, Jun 14) — lightweight utility skills that could slot into the content pipeline without much overhead.

**Nothing urgent.** Most discoveries overlap with what we already have or are experimental.

---

## 2026-06-06 - Git Commit Hygiene

**Issue:** Workspace had 580 untracked files (PDFs, screenshots, output artifacts) mixed with 26 actual tracked changes.

**Fix:** Used `git add -u` to stage only modified tracked files, committed with descriptive message. Left untracked artifacts alone.

**Lesson:** For workspace repos with heavy artifact generation, `git add -u` is the right approach - don't blindly `git add .`.

## 2026-06-14 - Weekly Skill Discovery (ClawHub Scan)

**Category:** insight

Ran 8 category searches + 2 explore sweeps (rating, trending) across ClawHub. Reviewed candidates not already installed.

### Skills We Already Have (noted overlaps)
| Our Skill | Search Match |
|-----------|-------------|
| solana-payments-wallets-trading 0.3.4 | "solana trading crypto" search |
| wordpress-pro 0.1.0 / wordpress-api-pro 3.8.1 | "wordpress seo publishing" search |
| ai-social-media-content 0.1.5 / upload-post 1.0.0 | "social media content creator" search |
| agent-browser-clawdbot 0.1.0 / browser-use 2.0.1 / browser-auto-plus 2.0.0 / agent-browser-assistant (not ours) | "browser automation screenshot" search |
| agentmail-integration 1.1.0 / resend-send-native-node 1.0.12 / cold-email-engine 1.0.0 | "email automation inbox" search |
| duckdb-cli-ai-skills 1.0.0 / excel-xlsx 1.0.2 / word-docx 1.0.2 | "data analysis sql csv" search |
| agent-workflow-playbook 1.1.2 | "ai agent workflow" search |
| wordpress-remote-news-publisher 1.0.0 | "wordpress seo publishing" search |

### New Discoveries (Not Installed) — Worth Consideration

**Browser / Automation (already have 3 browser skills)**
- `agent-browser-assistant` v1.0.0 — browser automation, scraping, screenshots, UI testing — redundant with browser-use + browser-auto-plus + agent-browser-clawdbot
- `chrome-web-automation` v1.0.0 — works in existing Chrome session, screenshots — could be useful but redundant
- `playwright-browser-automation` v2.0.0 — Playwright API, screenshots, PDFs, video — higher reliability than MCP approaches
- `desktop-control` v1.0.0 — mouse/keyboard/screen automation for local Windows — interesting for native UI tasks

**Content / Humanization**
- `humanizer` v1.0.0 — strips AI writing signals from text (em dash overuse, AI vocabulary, inflated symbolism) — pairs well with ai-social-media-content / wordpress-pro
- `automation-workflows` v0.1.0 — identifies repetitive tasks to automate, covers Zapier/Make/n8n workflow design — lightweight advice skill

**Search & Data**
- `multi-search-engine` v2.1.3 — 16 engines (7 CN + 9 global), advanced operators, Wolfram — interesting as Tavily alternative but China-heavy tilt
- `data-analysis-reporting` v0.1.0 — CSV/SQLite/spreadsheet → analytical summaries and reports — overlaps with duckdb-cli-ai-skills
- `ontology` v1.0.4 — typed knowledge graph for agent memory, composable skills — could help structure memory-hygiene

**Agent Workflow & Decision**
- `proactive-agent` v3.1.0 — WAL protocol, working buffer, autonomous crons, Hal Stack — self-improvement + agent automation framework
- `neosoul-decision-agent` v1.0.0 — structured decision support with learning memory — decision framework

**Infrastructure & Maintenance**
- `skill-vetter` v1.0.0 — security audit for skills before install — good safety practice
- `auto-updater` v1.0.0 — daily cron to auto-update Clawdbot and skills — Ops quality-of-life
- `free-ride` v1.0.11 — manages free OpenRouter models for OpenClaw, auto-fallback — budget optimization
- `api-gateway` v1.0.124 — connect to external services via Maton-managed routes — potential bridging tool
- `notion` v1.0.0 — Notion pages/databases/blocks API
- `obsidian` v1.0.0 — Obsidian vault automation via obsidian-cli

**Chat/Bot**
- `telegram-discord-bot-dev` v1.0.0 — custom Telegram/Discord bot dev (trading, gaming, automation, webhooks, analytics)
- `wordpress-publishing-skill-for-claude` v0.1.0 — WordPress via REST API with Gutenberg blocks, SEO tags — overlaps with wordpress-pro

### Flagged for Opus Attention 👂
1. **`humanizer`** v1.0.0 — directly useful for content publishing pipeline; strips AI patterns from text before WordPress posting. Compliments ai-social-media-content + wordpress-pro.
2. **`proactive-agent`** v3.1.0 — WAL protocol + autonomous crons framework could improve our heartbeat/self-improvement workflows significantly.
3. **`skill-vetter`** v1.0.0 — security-first skill audit before installs; good safety practice for future skill additions.
4. **`free-ride`** v1.0.11 — free OpenRouter models with fallback = could reduce API costs.
5. **`desktop-control`** v1.0.0 — native desktop automation (mouse/keyboard/screen) on Windows PC; unique capability we don't have.
6. **`playwright-browser-automation`** v2.0.0 — described as more reliable than MCP approach for browser automation.
7. **`ontology`** v1.0.4 — typed knowledge graph could improve structured memory for memory-hygiene.
