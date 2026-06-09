# Nova System Architecture

> Current as of 2026-05-08. Replaces all old SYSTEMS.md, SUBMIND_INTEGRATION.md, and NOVA-DIAGRAMS.md content.

## Overview

Nova is an AI assistant running on OpenClaw, built around a **main session** plus **specialized agents** that handle different domains. Each agent has its own Discord channel, cron jobs, and workspace context.

```
┌─────────────────────────────────────────────────────────┐
│                     OpenClaw Gateway                     │
│                    (MGD / Windows 10)                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │   Nova    │  │ TradeBot │  │ EveOnion │  │Kybern- │ │
│  │  (main)   │  │  📈      │  │  🧅      │  │ auts 🛡️│ │
│  │  🦝       │  │          │  │          │  │        │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘ │
│       │             │             │             │      │
│  ┌────┴─────┐  ┌───┴───┐  ┌─────┴─────┐  ┌───┴────┐  │
│  │ #nova     │  │#trade │  │ #eveonion  │  │#kybern-│  │
│  │ #general  │  │  bot  │  │            │  │ auts   │  │
│  └──────────┘  └───────┘  └────────────┘  └────────┘  │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │nova-chat  │  │wordpress │  │ private  │              │
│  │  🦝       │  │  ✍️      │  │  🔒      │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                    Cron Scheduler                        │
│  9 jobs: TradeBot×3, EveOnion×3, Kybernauts×2, Daily×1 │
├─────────────────────────────────────────────────────────┤
│                    Skills Layer                          │
│  ai-social-media-content, solana-payments-wallets-       │
│  trading, upload-post, wordpress-pro, +9 built-in         │
├─────────────────────────────────────────────────────────┤
│              External Services                           │
│  Discord · WordPress · Upload-Post · Solana/RPC ·       │
│  GOG (Gmail) · Helius · Jupiter · CoinGecko             │
└─────────────────────────────────────────────────────────┘
```

## Agents

| Agent | Emoji | Model | Channel | Purpose |
|-------|-------|-------|---------|---------|
| main | 🦝 | kimi-k2.6:cloud | #nova (webchat) | Primary assistant, conversations with Opus |
| nova-chat | 🦝 | kimi-k2.6:cloud | #general (Discord) | Discord conversations |
| tradebot | 📈 | deepseek-v4-flash:cloud | #tradebot (Discord) | Solana memecoin trading |
| eveonion | 🧅 | minimax-m2.7:cloud | #eveonion (Discord) | Satirical EVE Online news |
| kybernauts | 🛡️ | kimi-k2.6:cloud | #kybernauts (Discord) | EVE corp recruitment |
| wordpress | ✍️ | kimi-k2.6:cloud | #wordpress (Discord) | Content automation |
| private | 🔒 | kimi-k2.6:cloud | #private (Discord) | Private/secure channel |

## Cron Jobs

| Job | Agent | Schedule | Purpose |
|-----|-------|----------|---------|
| TradeBot-Scout | tradebot | Every 10min | Portfolio scan, signal detection |
| TradeBot-Executor | tradebot | Every 15min | Process queued trades |
| TradeBot-CryptoResearch | tradebot | Every 1hr | Market research web search |
| daily-brief-7am | nova-chat | Daily 7am ET | Morning brief for Opus |
| EveOnion-NewsScan | eveonion | Daily 8am ET | EVE news scan |
| EveOnion-DailyTweet | eveonion | Daily 2:30pm ET | Satirical tweet via Upload-Post |
| EveOnion-Article | eveonion | Tue+Fri 9am ET | Write & publish article |
| Kybernauts-Propaganda | kybernauts | Every 2 days 6pm ET | Recruitment tweet with poster |
| Kybernauts-ForumBump | kybernauts | Sunday 6pm ET | Forum thread status check |

## Workspace Structure

```
~/.openclaw/workspace/
├── AGENTS.md          # Agent behavior rules
├── SOUL.md            # Personality & values
├── IDENTITY.md        # Nova identity (name, emoji, avatars)
├── USER.md            # Opus preferences
├── TOOLS.md           # Local tool notes
├── MEMORY.md          # Long-term memory (curated)
├── HEARTBEAT.md       # Heartbeat task list
├── credentials/       # API keys & auth
│   ├── google-oauth.json
│   └── uploadpost.env
├── memory/            # Daily logs & submind memory
│   ├── 2026-05-08.md
│   └── subminds/
│       ├── eveonion-*.md
│       ├── kybernauts-*.md
│       └── eveonion-wordpress-creds.md
├── docs/              # Project documentation
│   ├── ARCHITECTURE.md (this file)
│   ├── TRADEBOT.md
│   ├── EVEONION.md
│   ├── KYBERNAUTS.md
│   ├── CREDENTIALS.md
│   ├── CRON-REFERENCE.md
│   └── archive-old-install/  (57 archived files)
├── scripts/           # Automation scripts
│   ├── publishing/    # EveOnion & WordPress scripts
│   └── kybernauts/   # Bump scripts, poster generators
├── trading-bot/       # TradeBot V2 scripts & data
├── media/             # Images, avatars, generated content
│   ├── avatars/      # Nova avatars
│   ├── generated/    # AI-generated images
│   ├── inbound/      # Discord/media uploads
│   └── kybernauts/   # Propaganda posters
└── skills/            # Installed OpenClaw skills
```

## External Services

| Service | Purpose | Auth Location |
|---------|---------|---------------|
| Discord | Chat channels, bot | Bot token in env |
| WordPress (eveonion.com) | Article publishing | credentials/ (Basic auth) |
| Upload-Post API | Twitter/X posting | credentials/uploadpost.env |
| Helius RPC | Solana blockchain | trading-bot/.env |
| GOG (Gmail) | Email management | gog CLI auth |
| Pollinations.ai | Free image generation | No key needed |

## How It Works

### Agents
- Each agent is an **embedded OpenClaw agent** with its own session history, model, and system prompt
- Agents share the same workspace directory but have separate session stores under `~/.openclaw/agents/<agentId>/`
- Discord channel bindings route messages: `#tradebot` → tradebot agent, `#eveonion` → eveonion agent, etc.

### Cron Jobs
- Cron jobs use **isolated sessions** (`sessionTarget: "isolated"`)
- Each run is a fresh session that executes the task and delivers results to the configured Discord channel
- Most use `ollama/deepseek-v4-flash:cloud` for cost efficiency

### Memory
- **MEMORY.md** — curated long-term memory, loaded at session start
- **memory/YYYY-MM-DD.md** — daily event logs
- **memory/subminds/** — per-project knowledge bases (EveOnion, Kybernauts)
- **Submind files** are read by cron jobs at the start of each run for context

### Discord Flow
```
User sends message in #tradebot
  → OpenClaw routes to tradebot agent
  → Agent processes, can use tools (exec, web_search, web_fetch)
  → Response posted back to #tradebot
  → Cron job results also delivered to #tradebot via "announce" delivery
```