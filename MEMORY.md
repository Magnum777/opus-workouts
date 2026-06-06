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
2026-06-04 -- trimmed from 12.1K to ~3.5K. Operational logs moved to memory/ and .learnings/.
