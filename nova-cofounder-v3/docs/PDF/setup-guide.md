# Nova AI Cofounder V3 — Setup Guide

---

## Page 1-3: What You're Getting

**Nova AI Cofounder V3** is not a chatbot. It is an AI coworker that lives on your machine, works while you sleep, and handles the tasks you hate.

### What makes this different?
- **Self-hosted** — Your data stays on your machine. No cloud subscription. No API bills unless you want them.
- **Autonomous** — Set it to L3+ and it executes tasks, cleans your inbox, posts to social, monitors projects — without waking you.
- **Customizable** — You define its personality, its boundaries, and what it's allowed to do. Raccoon, fox, owl, dragon, or custom.
- **Skill-based** — Add capabilities like WordPress publishing, Gmail cleanup, trade monitoring, social media posting. Install only what you need.

### What you'll have after setup:
- An AI that knows your name, your projects, and your communication style
- Morning briefings with weather, calendar, and project status
- Automatic email spam cleanup
- Scheduled social media posts
- Project tracking with milestone reminders
- A growing memory of everything you've done together

### Setup time: 30-45 minutes
**Requirements:**
- Windows 10/11, macOS, or Linux
- 8GB RAM minimum (16GB recommended for local AI model)
- Python 3.11+ (installer will install if missing)
- Internet connection (for initial download)

---

## Page 4-8: Before You Start

### Have ready:
1. **Gmail account with IMAP enabled** (optional but recommended)
   - Settings → Forwarding and POP/IMAP → Enable IMAP
   - myaccount.google.com/apppasswords → Generate app password

2. **Discord account** (optional, for bot integration)
   - You'll create a bot at discord.com/developers/applications
   - Copy the bot token during setup

3. **API key** (optional, if you want cloud model instead of local)
   - OpenAI, Anthropic, or Google AI
   - Local Ollama model is free and runs on your GPU

4. **WordPress sites** (optional, for content publishing)
   - Application password from each site's admin panel

### Expected flow:
```
Run install.ps1 → Answer prompts → Configure channels → Test first task → Done
```

### If something goes wrong:
- Check `docs/troubleshooting.pdf` (included in download)
- Post in Discord #nova-help: https://discord.gg/XxDCEwg7Wh
- No paid support, but the community helps

---

## Page 9-18: Step-by-Step Setup

### Step 1: Download and Extract
1. Purchase from Gumroad (link in your receipt)
2. Download `nova-cofounder-v3.zip`
3. Extract to a folder (e.g., `C:\Tools\Nova` or `~/nova`)

### Step 2: Run the Installer
**Windows (PowerShell as Admin):**
```powershell
cd nova-cofounder-v3\setup
.\install.ps1
```

**Options:**
- `install.ps1 -Docker` — Use Docker containers (advanced)
- `install.ps1 -Model api` — Use cloud API instead of local Ollama
- `install.ps1 -SkipIntake` — Skip the onboarding (do it later)

### Step 3: Prerequisites Check
The installer will check for and install if missing:
- Python 3.11+ (via winget on Windows, brew on macOS)
- Git (for skill updates)
- Node.js (for OpenClaw Gateway)
- Ollama (for local AI model, unless using API)

You'll see green checkmarks as each passes. If something fails, the script will tell you how to fix it.

### Step 4: OpenClaw Gateway Install
The script downloads and installs the OpenClaw Gateway — the runtime that connects you to the AI model, skills, and channels.

Default install location:
- Windows: `%USERPROFILE%\.openclaw\gateway`
- macOS/Linux: `~/.openclaw/gateway`

### Step 5: Channel Configuration
The installer will ask about channels one by one:

**Discord:**
- Enter your bot token (or press Enter to skip)
- If you have a guild ID, enter it (or I'll help you find it)

**Telegram:**
- Enter bot token from @BotFather (or skip)

**WhatsApp:**
- A QR code will be shown to link your phone (or skip)

**"Just local for now?"**
- Press Enter through all channel prompts
- You can add channels later via `openclaw config`

### Step 6: Core Skills Install
The script auto-installs essential skills:
- **clawhub** — skill marketplace
- **browser-automation** — web scraping, form filling
- **memory-hygiene** — keeps memory clean and fast
- **self-improving-agent** — learns from mistakes
- **duckdb-en** — data analysis
- **taskflow** — multi-step task management

Then it asks about optional skills:
- gmail-cleanup (spam sweep + inbox triage)
- wordpress-pro (publishing automation)
- ai-social-media-content (post generation)
- upload-post (posting to TikTok, IG, X, etc.)

Type `y` for each you want, `N` to skip.

### Step 7: Docker Setup (Optional)
If you used `-Docker`, the script:
- Checks Docker Desktop is installed
- Copies `docker-compose.yml` to your workspace
- Prints: `Run "docker-compose up" to start isolated services`

Docker containers run: Gateway, Redis (short-term memory), LanceDB (vector memory).

### Step 8: Launch Intake
After install completes, you'll see:
```
Nova is installed. Run 'openclaw nova-intake' to start Day 1.
```

Run it. This starts the 7-day onboarding. Day 1 takes 5 minutes.

---

## Page 19-24: Making It Yours

### Customize SOUL.md (Personality)
File location: `~/.openclaw/workspace/SOUL.md`

Edit with any text editor. Key sections:
- **Identity** — Name, creature, emoji
- **Approach** — How I think through problems
- **Execution** — When to ask vs when to act
- **Boundaries** — What I'm allowed to do unsupervised

Example customization:
```markdown
## Identity
- **Name:** Athena
- **Creature:** Owl-spirit AI
- **Vibe:** Precise, thoughtful, no fluff
- **Emoji:** 🦉
```

### Add Your Projects
File: `~/.openclaw/workspace/memory/projects.md`

List active projects. I reference this every session:
```markdown
## Active Projects
- **Website Redesign** — WordPress refresh for client X
- **TradeBot V2** — Solana memecoin trading automation
- **Nova V3 Launch** — AI cofounder product packaging
```

### Set Autonomy Level
Run: `/level` in chat

Or edit `SAFETY.md` directly:
```markdown
# Safety Invariants
Autonomy Level: L3 (Execute most, notify after)

Hard Limits:
- Never spend more than $50 without asking
- Never send emails to new contacts without preview
- Never post to social media without approval
- Trash > delete for all file operations
```

### Add Custom Cron Jobs
Example: Check a website every hour for changes
```powershell
openclaw cron add --name "price-check" --schedule "0 * * * *" --command "python check_price.py"
```

---

## Page 25-28: Common Issues

### "Python not found"
**Fix:** The installer should auto-install Python via winget. If it fails:
1. Download from python.org
2. Check "Add Python to PATH" during install
3. Re-run `install.ps1`

### "Ollama model too slow"
**Fix:** You're running a large model on CPU. Options:
1. Use a smaller model: `ollama pull deepseek-v4-flash`
2. Use API mode: Re-run installer with `-Model api`
3. Add a dedicated GPU (AMD or NVIDIA, 8GB+ VRAM)

### "Discord bot won't connect"
**Fix:**
1. Check token is correct (no extra spaces)
2. Bot must be invited to a server with permissions
3. Gateway must be running: `openclaw gateway status`

### "Cron jobs not running"
**Fix:**
1. Check gateway is running: `openclaw gateway status`
2. Check cron list: `openclaw cron list`
3. Check logs: `~/.openclaw/gateway/logs/`

### "Memory feels bloated"
**Fix:** Run memory hygiene:
```bash
openclaw skill run memory-hygiene
```
Or manually review `memory/YYYY-MM-DD.md` files and archive old ones.

---

## Page 29-30: What Now?

### Daily Commands
- `openclaw chat` — Start a conversation
- `/project add [name]` — Add a project
- `/project status [name]` — Check on something
- `/delegate [task]` — Assign a task, get back later
- `/level` — Check or change autonomy

### Weekly Rituals
- **Monday:** Skill update check (`clawhub update --all`)
- **Wednesday:** Memory review (archive old daily logs)
- **Sunday:** Autonomy level review (should I upgrade?)

### Community
- **Discord:** https://discord.gg/XxDCEwg7Wh
- **#nova-help:** Ask setup questions
- **#showcase:** Share your Nova configuration

### Upgrade Path
- **V3 → V4** (Q4 2026): Multi-agent teams, voice interface, mobile app
- **Skills:** New skills added to ClawHub weekly
- **Blog:** aicofounderstack.com for tips and case studies

---

**You're set. Welcome to having an AI coworker.**
