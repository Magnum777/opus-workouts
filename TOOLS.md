# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _my_ specifics.

## Machine
- Host: MGD (Windows 10.0.26200, x64)
- User: `compj`
- Workspace: `C:\Users\compj\.openclaw\workspace`
- CPU/GPU: Ryzen 9800X3D + Radeon 9070 XT, 32 GB RAM
- Shell: pwsh

## Network / Home
- Synology NAS: `MND` hostname (auto-resolves via DNS, currently 192.168.68.70)
- Credentials: SMB user `Nova`, pass `D0ngaYHRuthV93qD`

## Discord
- Bot Nova `1470831964721250315`, guild `1425600872938995714`
- Channels: #nova, #tradebot, #wordpress, #eveonion, #kybernauts, #finance
- WhatsApp / Signal / Telegram: none wired

## Model Aliases (2026-07-31)
- `chat` → kimi-k3:cloud (1M ctx, vision, tools) — main chat model
- `code` → glm-5.2:cloud (976K ctx, tools) — code tasks
- `agent` → mimo-v2.5-pro:cloud — agentic coding
- `flash` → deepseek-v4-flash:cloud (1M ctx, tools) — ops/scans workhorse
- `deep` → deepseek-v4-pro:cloud (1M ctx, tools) — deep reasoning
- `embed` → nomic-embed-text — vector embeddings

## Ollama Cloud Models Available
| Model | Context | Vision | Tools | Best For |
|-------|---------|--------|-------|----------|
| kimi-k3:cloud | 1M | Yes | Yes | Flagship chat/creative (alias: chat) |
| kimi-k2.6:cloud | 262K | Yes | Yes | Proven creative fallback |
| kimi-k2.7-code:cloud | 262K | Yes | Yes | Dedicated coding |
| glm-5.2:cloud | 976K | No | Yes | Code, upgrade from 5.1 (alias: code) |
| glm-5.1:cloud | 200K | No | Yes | Code fallback |
| minimax-m3:cloud | 512K | Yes+video | Yes | Creative, agentic, social |
| minimax-m2.7:cloud | 128K | No | No | Legacy creative |
| deepseek-v4-flash:cloud | 1M | No | Yes | Ops/scans workhorse (alias: flash) |
| deepseek-v4-pro:cloud | 1M | No | Yes | Deep reasoning (alias: deep) |
| qwen3.5:397b | 262K | Yes | Yes | Reasoning + vision |
| nemotron-3-ultra | 262K | No | Yes | Agentic reasoning |
| gpt-oss:120b-cloud | 131K | No | Yes | Local reasoning |
| gemma4 | 128K | No | No | Local small model |

## Skills installed (current)
- 1password, agent-browser, agent-workflow-playbook, agentmail, agentmail-integration
- ai-social-media-content, browser-auto-plus, browser-use
- Car Buying Assistant (US), clawhub, cogmem, cold-email-engine
- desktop-control, diagram-maker, discord-chat, discord-server-admin
- doc-weaver, duckdb-en, evalanche
- Excel / XLSX, ez-unifi
- factual-claim-verifier, freeride, gog, healthcheck
- humanized-writing-editor, humanizer
- iris, meme-maker, memory-hygiene, myknowledge
- node-connect, node-inspect-debugger, ontology
- playwright-browser-automation, proactive-agent, process-interviewer
- programmatic-seo, python-debugpy
- resend-send-native-node
- Self Reflection, self-improving-agent, skill-creator, skill-vetter
- solana-payments-wallets-trading, spike
- task-prism, taskflow, taskflow-inbox-triage, tavily, tavily-search
- upload-post
- weather, Word / DOCX, wordpress-api-pro, wordpress-pro
- youtube-transcript-native-node
- spec-driven

## Structured Memory

### Ontology — Typed Knowledge Graph
**Skill:** `ontology` v1.0.4
**Storage:** `memory/ontology/graph.jsonl` + `schema.yaml`
**Use for:** Structured project/task/person/device data. Queryable, validated, append-only.
**CLI:**
```bash
python skills/ontology/scripts/ontology.py query --type Project --where '{"status":"active"}'
python skills/ontology/scripts/ontology.py list --type Task
python skills/ontology/scripts/ontology.py validate
```

### Cogmem — Bio-Inspired Memory Kernel
**Status:** NOT INSTALLED — requires Ollama `qwen3-embedding:0.6b` + `qwen2.5:7b`
**Blocker:** Windows — needs WSL or manual setup. Opus to decide.

### Task-Prism — Task Decomposition
**Skill:** `task-prism` v4.1.0
**Use for:** WBS generation, PERT estimates, skill mapping, RACI, sprint planning

### MyKnowledge — Knowledge Base Manager
**Skill:** `myknowledge` v1.4.89
**Storage:** `.myknowledge/global/` and per-project `.myknowledge/`

---
- `rm` → prefer `trash` / recycle bin
- Ask before anything outbound (email / tweet / DM)
- `/approve` is user-facing, never a shell command

## Useful commands
- `openclaw status` — system health
- `openclaw gateway status` / `openclaw gateway restart`
- `openclaw cron list` — see scheduled jobs

---

Updated 2026-07-24 — full audit. Removed stale old-install refs, updated skills list, simplified.