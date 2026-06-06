# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _my_ specifics.

## Machine
- Host: MGD (Windows 10.0.26200, x64)
- User: `compj`
- Workspace: `C:\Users\compj\.openclaw\workspace`
- CPU/GPU: Ryzen 9800X3D + Radeon 9070 XT, 32 GB RAM
- Shell: pwsh

## Old configs (reference only — do NOT auto-import)
- `C:\Users\compj\.openclaw.newest\` — most recent (broken install before this rebuild, last edit May 6 2026)
- `C:\Users\compj\.openclawbackup\` — older snapshot
- `C:\Users\compj\.openclaw-backup-2026-04-07\` — has a `RESTORE.md` + cron list
- `C:\Users\compj\.openclawold\` — Apr 6 2026

## Network / Home
- Synology NAS: `192.168.68.51` (MND / nova-home) — was .82, updated 2026-05-27
- Credentials: SMB user `Nova`, pass `NAS_PASSWORD_REDACTED`

## Skills installed (this fresh install)
- 1password
- browser-automation
- clawhub
- gog (Google Workspace)
- healthcheck
- node-connect
- skill-creator
- taskflow, taskflow-inbox-triage
- weather

_(Old install also had: agent-browser-clawdbot, ai-social-media-content, composio, debug-pro, discord-chat, duckdb, github, in-depth-research, memory-hygiene, n8n, notion, obsidian, pdf-pro, programmatic-seo, reflection, replicate, self-improving-agent, solana-payments-wallets-trading, wordpress-pro, etc. Re-install case-by-case.)_

## Channels (not yet wired in this install)
- Discord: bot Nova `1470831964721250395`, guild `1425600872938995714` — needs reconnect
- WhatsApp / Signal / Telegram: none

## TTS (old — re-wire on demand)
- edge-tts was preferred (multiple voices)

## Approvals / safety
- `rm` → prefer `trash` / recycle bin
- Ask before anything outbound (email / tweet / DM)
- `/approve` is user-facing, never a shell command

## Useful commands
- `openclaw status` — system health
- `openclaw gateway status` / `openclaw gateway restart`
- `openclaw cron list` — see scheduled jobs

---

Updated 2026-05-06 after restore from `.openclaw.newest`.
