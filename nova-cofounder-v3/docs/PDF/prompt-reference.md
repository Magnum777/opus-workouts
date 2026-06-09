# Prompt Reference — Nova AI Cofounder V3

## Identity Commands

### `/whoami`
Display your current USER.md profile.

**Example:**
```
> /whoami
Name: James "Opus"
Timezone: America/New_York
Style: Direct, casual, ADHD when motivated
Peak hours: 10pm–2am
```

### `/rename [name]`
Update what Nova calls you.

**Example:**
```
> /rename Boss
Done. I'll call you Boss from now on.
```

### `/personality [type]`
Swap Nova's personality archetype.

**Options:**
- `raccoon` — Clever, resourceful, hacker-familiar 🦝
- `fox` — Strategic, fast, witty 🦊
- `owl` — Thoughtful, precise, no fluff 🦉
- `dragon` — Bold, direct, high standards 🐉
- `custom` — Edit SOUL.md directly

**Example:**
```
> /personality owl
Personality updated to Owl. I will be precise and minimize fluff.
```

---

## Work Commands

### `/project add [name]`
Add a project to tracking.

**Example:**
```
> /project add Website Redesign
Project "Website Redesign" added. Status: Planning.
What are the first steps?
```

### `/project status [name]`
Check on a project's current state.

**Example:**
```
> /project status tradebot
TradeBot V2: Active
- Last check: 15 min ago
- Portfolio: $94.59
- Positions: 2 open
- Next action: Monitor for exit signals
```

### `/project done [name]`
Mark a project complete and archive it.

**Example:**
```
> /project done launch-v3
Project "launch-v3" archived. Lessons learned logged to MEMORY.md.
```

### `/delegate [task]`
Assign a task to Nova. She'll work on it and report back.

**Example:**
```
> /delegate Research competitors for Nova V3 pricing
Task accepted. I'll research AI assistant pricing and report back in ~10 minutes.
```

---

## System Commands

### `/skill list`
Show installed skills.

**Example:**
```
> /skill list
Installed skills (6):
  ✓ clawhub
  ✓ browser-automation
  ✓ memory-hygiene
  ✓ self-improving-agent
  ✓ duckdb-en
  ✓ taskflow
```

### `/skill add [name]`
Install a skill from ClawHub.

**Example:**
```
> /skill add wordpress-pro
Installing wordpress-pro... Done. Run `/skill list` to verify.
```

### `/skill remove [name]`
Uninstall a skill.

**Example:**
```
> /skill remove wordpress-pro
Removed wordpress-pro. Config preserved in case you reinstall.
```

### `/cron list`
Show scheduled recurring tasks.

**Example:**
```
> /cron list
Scheduled jobs:
  daily-brief-7am — Every day at 7:00 AM
  tradebot-monitor — Every 5 minutes
  memory-hygiene — Sundays at 10:00 PM
```

### `/cron add "[schedule]" [task]`
Add a new recurring task.

**Example:**
```
> /cron add "0 9 * * 1" "Check competitor prices"
Job created: competitor-check. Runs Mondays at 9am.
```

---

## Memory Commands

### `/remember [thing]`
Save something to long-term memory.

**Example:**
```
> /remember James hates em dashes in text
Saved. I will never use em dashes when writing for James.
```

### `/whatwas [query]`
Search your memory.

**Example:**
```
> /whatwas tradebot last week
Found in memory/2026-05-31.md:
- TradeBot portfolio: $94.59
- Positions: RAY + JUP
- Last sell: SELL PENGU TAKE_PROFIT (+13.7%)
```

### `/forget [thing]`
Remove from memory.

**Example:**
```
> /forget old password xyz123
Removed from MEMORY.md.
```

### `/review`
Show recent decisions and outcomes.

**Example:**
```
> /review
Last 5 decisions:
1. 2026-06-01: Disabled aicofounderstack ContentNova cron → case studies only
   Outcome: Better alignment with sales site purpose
2. 2026-05-31: Published TradeBot Guide on Gumroad
   Outcome: First product live, $49 price point set
```

---

## Autonomy Commands

### `/level`
Show current autonomy level and safety limits.

**Example:**
```
> /level
Current level: L3 — Execute most, notify after
Hard limits:
  - Max spend without ask: $50
  - New email contacts: Preview required
  - Social media posts: Approval required
  - File deletion: Move to trash only
```

### `/level up`
Increase autonomy (with safety check).

**Example:**
```
> /level up
Are you sure? L4 means I run overnight with only morning summaries.
Type CONFIRM to proceed, or CANCEL.
```

### `/level down`
Decrease autonomy.

**Example:**
```
> /level down
Dropped to L2 — Routine tasks auto, new tasks need approval.
```

### `/pause`
Stop all cron jobs temporarily.

**Example:**
```
> /pause
All cron jobs paused. They will not execute until you run `/resume`.
```

### `/resume`
Restart paused cron jobs.

**Example:**
```
> /resume
All cron jobs resumed. Next execution per schedule.
```

---

## Channel Commands

### `/channel list`
Show configured communication channels.

**Example:**
```
> /channel list
Channels:
  ✓ Discord — Guild: Layered Media, Bot: Nova
  ✗ WhatsApp — Not configured
  ✗ Telegram — Not configured
  ✓ Local — Web chat active
```

### `/channel add [type]`
Add a new channel.

**Example:**
```
> /channel add telegram
Follow BotFather steps: https://core.telegram.org/bots#6-botfather
Enter your bot token when ready.
```

---

## Utility Commands

### `/status`
Show system health.

**Example:**
```
> /status
Gateway: Running
Model: ollama/kimi-k2.6:cloud
Memory: 127MB used, 4.2GB free
Skills: 6 active
Crons: 3 scheduled
Channels: Discord connected
```

### `/help [topic]`
Get help on a topic.

**Example:**
```
> /help skills
Skills are modular capabilities. Install only what you need.
Core skills: clawhub, browser-automation, memory-hygiene, self-improving-agent, duckdb-en, taskflow
Browse more: https://clawhub.ai
```

---

## Quick Reference Card

| Command | What it does |
|---------|-------------|
| `/whoami` | Show your profile |
| `/project add` | Add a project |
| `/project status` | Check project state |
| `/delegate` | Assign a task |
| `/skill list` | Show installed skills |
| `/skill add` | Install a skill |
| `/cron list` | Show scheduled tasks |
| `/remember` | Save to memory |
| `/whatwas` | Search memory |
| `/level` | Check autonomy |
| `/level up` | More freedom |
| `/level down` | Less freedom |
| `/pause` | Stop all crons |
| `/resume` | Restart crons |
| `/status` | System health |
| `/help` | Get help |

---

**All commands work in any channel — Discord, web chat, or terminal.**
