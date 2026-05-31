# Nova Ops Assessment System

## Purpose
Monitor all cron jobs, detect failure patterns, attempt self-healing, and report health weekly.

## Architecture

### Layer 1: Skill-Aware Cron Payloads
Every cron has minimal skill awareness:
- Pre-flight checks (auth, dependencies)
- Error logging to `.learnings/ERRORS.md` with `[agent]` tag
- Browser cleanup failsafes where applicable

### Layer 2: Pattern-Based Skill Injection (reactive)
Ops-Assessment detects recurring failures and suggests skill loading:
- 3x timeout → suggest `debug-pro` for diagnosis
- 3x browser error → suggest `browser-use` + extended timeout
- 3x auth error → flag for manual fix
- 3x success → no intervention needed

### Layer 3: Per-Agent Profiles
Config-driven behavior for each agent's crons:

| Agent | Skills | Timeout | Model | Value Check |
|-------|--------|---------|-------|-------------|
| tradebot | solana-payments, self-improving-agent | 600 | deepseek-v4-flash | portfolio > $50 |
| eveonion | upload-post, ai-social-media-content | 180 | deepseek-v4-flash | Twitter auth valid |
| kybernauts | upload-post, browser-use | 600 | kimi-k2.6 | Discord connected |
| wordpress | wordpress-pro | 300 | kimi-k2.6 | WordPress sites reachable |
| nova-chat | self-improving-agent, memory-hygiene | 180 | kimi-k2.6 | — |

### Layer 4: Self-Healing Workflow
When a cron fails twice consecutively:
1. Ops-Assessment reads the error pattern from `openclaw cron list --json`
2. Loads relevant skill (debug-pro, browser-use, etc.)
3. Attempts auto-fix:
   - Timeout → bump +60s
   - Browser stuck → kill chrome + restart
   - Auth → flag manual
4. Reports what it did to Opus
5. If fix works → log `best_practice` to `.learnings/LEARNINGS.md`
   If fails → escalate to Opus in Discord

## Assessment Report Format

```
**🛡️ Nova Ops Assessment — YYYY-MM-DD**

**Healthy (X):** [list]
**Attention Needed (Y):** [list with consecutiveErrors count]
**Fixed This Week (Z):** [list of auto-healed issues]
**Retirement Candidates:** [silent for 7+ days, value < cost]

**Action Items:**
- [agent/cron] [issue] [status]
```

## Files
- `ops/assessment-report.md` — weekly report archive
- `.learnings/ERRORS.md` — all cron errors tagged by agent
- `.learnings/LEARNINGS.md` — best practices from fixes
