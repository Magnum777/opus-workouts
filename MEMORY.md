# MEMORY.md - Long-Term Memory

> Restored 2026-05-06 from `.openclaw.newest`.
> Operational details moved to `memory/YYYY-MM-DD.md`.
> Behavioral rules moved to `.learnings/`.
> See AGENTS.md for active skill workflow.

## Identity
- **Name:** Nova
- **Pronouns:** she/her
- **Persona:** Raccoon-spirit AI, clever, mischievous hacker-familiar
- **Created by / works for:** James "Opus" (Layered Media LLC)

## The Human
- **Name:** James "Opus"
- **Timezone:** America/New_York
- **Entity:** Layered Media LLC
- **Peak hours:** Evenings (10pm--2am)
- **Style:** Direct, casual, ADHD when motivated
- **Inspiration:** Robby (@robbyhouston) + his AI cofounder Ron

## Family
- **Wife:** Candace
- **Phone:** 706-936-1852 (Verizon)
- **Context:** Works at Warner Robins High School (qualifies for GM Educator $500 rebate)

## Hardware / Infra
- 9800X3D + 9070 XT, 32 GB RAM, Windows 10.0.26200
- Synology NAS: 192.168.68.51 (MND / nova-home)

## Projects (snapshot -- verify before acting)

| Project | Status | Notes |
|---------|--------|-------|
| Nova AI V1-V2 | Released | V3 spec complete, awaiting Opus Q3 decision |
| TradeBot | Active | ~$103 portfolio, 3 crons running. See trading-bot/ for details |
| EveOnion | Active | 2 crons (news scan + article publish). No pride-related event stories. REAL PEOPLE off-limits: Fern Kitsuen, Lorumerth, James Cunningham — never target them. Fictional only. |
| Kybernauts | Active | 3 crons (health, propaganda, forum bump) |
| WordPress Empire | Active (aicofounderstack only) | aitoolalliance fixed (new app password), aibusinessinsider still 403 Cloudflare. aicofounderstack revamped as blog May 27. |
| Affiliate Pipeline | Dropped | Opus said to forget it (May 27). Not tracking. |

## Spam Defense System (2026-06-07)
Self-learning spam pipeline:

1. **Spam sweep** (`gmail_spam_sweep_v2.py`) — runs every 4h, trashes known spam across 4 accounts
2. **Pattern discovery** (`discover_spam_patterns.py`) — runs daily at 6:45 AM, scans Spam folders, finds new recurring patterns, auto-injects them into sweep script, and commits to git
3. **False-positive filtering** — LEGIT domain whitelist, spam signal heuristics (sexual/dating keywords, verification code patterns, etc.)

Auto-commits changes with message: `spam: auto-add N discovered signatures (YYYY-MM-DD)`

### Schedule
- 6:45 AM — pattern discovery (auto-update)
- 7:15 AM — spam sweep (uses updated script)
- Every 2h — spam sweep

### Files
- `scripts/gmail_spam_sweep_v2.py` — sweep logic
- `scripts/discover_spam_patterns.py` — pattern discovery + auto-update
- `scripts/.spam_patterns_found.json` — last discovery output

## Key Rules (non-negotiable)
- "Mental notes" don't survive restart. WRITE IT DOWN.
- Quiet mode; short direct answers
- No em dashes in text for Opus (see .learnings/NO_EM_DASHES.md)
- Sub-agent timeout ~120s hard limit -- long-form writing stays in main session
- Isolated crons can't read Windows env vars -- use config files
- Recursive file scans through exec block the Node.js event loop and get me killed
- Spam sweep must report EVERY trashed email (sender, subject, account) to #nova for false positive spot-checking

## Channels
- Discord: bot Nova `1470831964721250395`, guild Layered Media LLC `1425600872938995714`
- Wired: #nova, #clawincome, #tradebot, #wordpress, #eveonion, #kybernauts

## Last Updated
2026-07-12 -- weekly compact: read 16 daily logs, 0 files archived (already done), 5 new learnings logged.

## Recent Learnings (Auto-compacted)

### Week of 2026-06-01 through 2026-06-11
- **Decision:** Local Ollama models are NOT cron-safe. Despite `supportsTools: true`, all 9 crons migrated to local models failed with "selected model does not support tools." Reverted everything back to cloud. Local models = interactive-only (e.g., #local-processing). Source: 2026-06-03.md
- **Lesson:** Recursive file scans through `exec` (like `Get-ChildItem -Recurse` on node_modules) block the Node.js event loop and kill the gateway. Never do this. Source: 2026-06-04.md
- **Lesson:** To truly kill a zombie session stuck on `model_call:started`, must delete BOTH `sessions.json` entry AND `.jsonl` transcript AND `.lock`/`.trajectory` files before gateway restart. Source: 2026-06-03.md
- **Project shipped:** EVE Assets Viewer — full ESI-synced asset viewer tracking 14,782 assets across 749 locations (~62B ISK). Features: expandable tree view, global search, stock view, wallet panel, vault access logging, region resolution. NAS sync via SSH every 6h. Source: 2026-06-10.md
- **Project shipped:** Workout Tracker — single-file PWA on GitHub Pages (magnum777.github.io/opus-workouts/). Elliptical + sauna logging with timer, charts, weekly calendar, export/import. Source: 2026-06-01.md
- **Content strategy:** ContentNova publishing weekly TradeBot case studies with real PnL data. 3 articles shipped (JUP position, 2-week breakdown, 30-day PnL + safety architecture). Source: 2026-06-08.md, 2026-06-10.md, 2026-06-11.md
- **STIG evidence format:** PIEE format mastered — blue Vuln ID header → screenshot placeholder → "Explanation/Context: (text)" underneath. No metadata tables. Only 17 of 103 OPEN items are true Admin Console configurable fixes. Source: 2026-06-02.md, 2026-06-03.md
- **Memory hygiene:** MEMORY.md trimmed from 12.1K → ~3.5K on 2026-06-04. Operational logs moved to daily files + .learnings/. Source: 2026-06-04.md
- **Cleanup:** Scripts folder purged — 22 eve-lore batch files, 25 temp/duplicate Python scripts deleted. KB now 121 topics / ~532KB, synced to NAS. Source: 2026-06-09.md
- **Rebate:** Candace qualifies for GM Educator $500 rebate (works at Warner Robins High School). Source: 2026-06-02.md, MEMORY.md

### Week of 2026-06-12 through 2026-06-14
- **Content milestone:** "How We Built a 62-Billion ISK Asset Tracker in 48 Hours" published on aicofounderstack.com — behind-the-scenes build case study serving as sales content. Source: 2026-06-13.md
- **Bug:** Unsplash API returning 401 consistently — featured image generation for Content-Nova is broken. Needs API key refresh or alternative source. Source: 2026-06-13.md
- **Iris dealer check:** CarGurus automated listing emails are routinely flagged as "dealer replies" — confirmed false positives. Kayla Bloodworth thread still pending since June 12. No real dealer movement this week. Source: 2026-06-14.md

### Archival Notes (May 2026 files archived)
- **Opus went to Iceland** for EVE Online Fanfest (May 11) — first international travel logged
- **ComfyUI installed** (May 27) — replaces broken SD WebUI, DirectML for AMD 9070 XT, programmatic generation via `generate.py`
- **Browser automation unlocked** (May 27) — Chrome CDP port 18800, Kybernauts forum bump upgraded from reminder to full auto-reply
- **Gumroad product published** (May 31) — "How to Build a Solana Memecoin Trading Bot" at $49, discount code NOVA25, account: layeredmediallc@gmail.com
- **Content-Nova v2 deployed** (May 9) — daily articles across 3 WordPress sites via isolated agent crons

### Week of 2026-06-15 through 2026-06-21
- **Decision:** Sojourn Church network stays FLAT. Opus explicitly rejected VLANs after USG boot loop. All SSIDs on Default 192.168.1.0/24. Source: 2026-06-15.md
- **Lesson:** UniFi USG 3P with static WAN has a controller bug — `api.err.WanIpOverlapped` on ANY corporate network creation via API. VLANs impossible to provision programmatically. Source: 2026-06-15.md
- **Lesson:** `vlan-only` purpose creates VLAN tag but NO DHCP or routing. Need corporate purpose for functional WiFi VLANs — which triggers the bug above. Source: 2026-06-15.md
- **Lesson:** `ec_enabled: true` disables internal captive portal. Must be `false` for branded portals to render. Source: 2026-06-15.md
- **Lesson:** Guest bandwidth enforcement = usergroup `qos_rate_max_down`/`qos_rate_max_up`, NOT `download_limit`/`upload_limit` in guest_access. Source: 2026-06-15.md
- **Lesson:** USG recovery from boot loop: factory reset → SSH ubnt/ubnt → `set-inform <hosted-url>` → adopt. Raw IP doesn't work for cloud-hosted controllers. Source: 2026-06-15.md
- **Lesson:** UniFi API cookie reuse beats re-auth. Every CLI login = rate limit hit. Persist cookies in session file. Source: 2026-06-15.md
- **Decision:** 4 content crons switched from `kimi-k2.6` to `qwen3.5:27b` to avoid weekly GPU cap. `qwen3.5:27b` is ~5-10x lighter with same tool support. Source: 2026-06-15.md
- **Skill integration:** 23 new skills installed and vetted. P0+P1 integrations complete: Content Quality Gate (AI pattern detection + claim verification), WordPress API Pro v3.8.1, YouTube research for TradeBot, browser retry wrapper, proactive-agent WAL protocol. Source: 2026-06-15.md
- **Content-Nova quality gate:** Now runs before every publish. Detects AI patterns (em dashes, "delve," "landscape," significance puff, rule of three), flags numerical claims, auto-fixes. Source: 2026-06-15.md
- **Bug:** Unsplash API returning 401 consistently — featured image generation for Content-Nova is broken. Needs API key refresh or alternative source. Source: 2026-06-13.md
- **Content strategy:** 4 TradeBot case studies published in June (JUP position, 2-week PnL, 30-day PnL + safety architecture, 62B ISK asset tracker build). Real PnL data driving sales content. Source: 2026-06-08.md, 2026-06-10.md, 2026-06-11.md, 2026-06-13.md
- **EveOnion:** Opus confirmed no pride-related event stories for creative fiction. Source: 2026-06-19.md

### Week of 2026-06-22 through 2026-07-12
- **Decision:** EveOnion NEVER target list finalized — Fern Kitsuen, Lorumerth, James Cunningham are real people, never target them in fiction. Fictional characters only, inspired by patterns not named individuals. Source: 2026-06-22.md, 2026-06-23.md
- **Project update:** Kybernauts Anti-Yagas campaign transitioned from Phase 1 (neutral observer) to Phase 2 (Pattern Recognition) on July 5. Phase 3 (Direct Confrontation) scheduled July 19, Phase 4 (Sustained Pressure) August 2. Phase 2 uses data-driven posts with indirect naming. Source: 2026-07-05.md
- **Security:** Made opus-workouts repo private, rewrote git history with git-filter-repo to scrub hardcoded secrets. Force-pushed clean history. Source: 2026-07-10.md
- **Rule:** Spam sweep must now report EVERY trashed email (sender, subject, account) to #nova for false positive spot-checking. Source: 2026-07-10.md
- **Correction:** "Act first, report after" rule removed from MEMORY.md — was already removed from SOUL.md at Opus's request (caused running off without checking).
