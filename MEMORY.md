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
| EveOnion | Active | 2 crons (news scan + article publish) |
| Kybernauts | Active | 3 crons (health, propaganda, forum bump) |
| WordPress Empire | Partial | aicofounderstack.com publishing. aitoolalliance (401), aibusinessinsider (403) |
| Affiliate Pipeline | Stalled | 11 applications, 0 approvals (as of May 6) |

## Spam Defense System (2026-06-07)
Self-learning spam pipeline:

1. **Spam sweep** (`gmail_spam_sweep_v2.py`) — runs every 4h, trashes known spam across 4 accounts
2. **Pattern discovery** (`discover_spam_patterns.py`) — runs daily at 6:45 AM, scans Spam folders, finds new recurring patterns, auto-injects them into sweep script, and commits to git
3. **False-positive filtering** — LEGIT domain whitelist, spam signal heuristics (sexual/dating keywords, verification code patterns, etc.)

Auto-commits changes with message: `spam: auto-add N discovered signatures (YYYY-MM-DD)`

### Schedule
- 6:45 AM — pattern discovery (auto-update)
- 7:15 AM — spam sweep (uses updated script)
- Every 4h — spam sweep

### Files
- `scripts/gmail_spam_sweep_v2.py` — sweep logic
- `scripts/discover_spam_patterns.py` — pattern discovery + auto-update
- `scripts/.spam_patterns_found.json` — last discovery output

## Key Rules (non-negotiable)
- "Mental notes" don't survive restart. WRITE IT DOWN.
- Act first, report after; quiet mode; short direct answers
- No em dashes in text for Opus (see .learnings/NO_EM_DASHES.md)
- Sub-agent timeout ~120s hard limit -- long-form writing stays in main session
- Isolated crons can't read Windows env vars -- use config files
- Recursive file scans through exec block the Node.js event loop and get me killed

## Channels
- Discord: bot Nova `1470831964721250395`, guild Layered Media LLC `1425600872938995714`
- Wired: #nova, #clawincome, #tradebot, #wordpress, #eveonion, #kybernauts

## Last Updated
2026-06-12 -- weekly compact: distilled 10 learnings from 8 daily logs, archived 35 stale files (Feb-Apr).

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
