# Infrastructure & Processes — Nova Ops

> Last updated: 2026-08-02
> Owner: Nova, maintained via Daily-MemorySweep + manual updates

## System Architecture

### Host Machine: MGD
- Ryzen 9800X3D + Radeon 9070 XT, 32 GB RAM
- Windows 10.0.26200
- OpenClaw host, all crons run here
- C: drive ~9.5% free (~163 GB of 1.7 TB) — monitor this

### NAS: MND (nova-home)
- Synology NAS, DSM 4.1.2
- Hostname: MND (DNS auto-resolves, currently 192.168.68.70)
- SMB shares: `\\MND\home`, `\\MND\video`
- DS API file upload broken (error 101) — use SMB drop to `\\MND\video\watch`
- Credentials: read from `.secrets`, never hardcoded

### Model Stack (2026-07-31)
| Alias | Model | Context | Use |
|-------|-------|---------|-----|
| chat | kimi-k3:cloud | 1M | Flagship chat, vision |
| code | glm-5.2:cloud | 976K | Code tasks |
| agent | mimo-v2.5-pro:cloud | — | Agentic coding |
| flash | deepseek-v4-flash:cloud | 1M | Ops/scans workhorse |
| deep | deepseek-v4-pro:cloud | 1M | Deep reasoning |
| — | minimax-m3:cloud | 512K | Creative, social content |
| — | kimi-k2.6:cloud | 262K | Creative fallback, special crons |
| embed | nomic-embed-text | — | Vector embeddings (memory search) |

## Cron Registry (29 enabled)

### Content Production (9 crons)
| Name | Schedule | Model | Channel | Post Log |
|------|----------|-------|---------|----------|
| ContentNova-aitoolalliance | 2am daily | minimax-m3 | #wordpress | Yes |
| ContentNova-aibusinessinsider | 3am daily | minimax-m3 | #wordpress | Yes |
| ContentNova-aicofounderstack | 4am daily | minimax-m3 | #wordpress | Yes |
| EveOnion-NewsScan | 8:15am daily | minimax-m3 | #eveonion | Yes |
| EveOnion-Article | 9:30am Tue/Fri | kimi-k2.6 | #eveonion | Yes |
| EveOnion-RedditTweet | 10am daily | minimax-m3 | #eveonion | Yes |
| EveOnion-PersonaScan | 10am every 3 days | deepseek-v4-flash | #eveonion | Yes |
| Kybernauts-Propaganda | Sun 6:15pm | minimax-m3 | #kybernauts | Yes |
| Yagas-Propaganda-Post | 5pm daily | minimax-m3 | #kybernauts | Yes |

### Intel & Monitoring (3 crons)
| Name | Schedule | Model | Channel | Post Log |
|------|----------|-------|---------|----------|
| Yagas-Intel-Collect | 2pm daily | minimax-m3 | #kybernauts | Yes |
| Amazon-Affiliate-Injector | 11am daily | deepseek-v4-flash | #wordpress | Yes |
| Amazon-Tracker-Weekly | Mon noon | deepseek-v4-flash | #finance | Yes |

### Publishing (2 crons)
| Name | Schedule | Model | Channel | Post Log |
|------|----------|-------|---------|----------|
| Amazon-Affiliate-Publish | 10:15am Tue/Fri | deepseek-v4-flash | #wordpress | Yes |

### Nova Ops (15 crons)
| Name | Schedule | Model | Channel |
|------|----------|-------|---------|
| spam-sweep-every-4h | every 2h | deepseek-v4-flash | #nova |
| spam-pattern-discovery | 6:45am daily | deepseek-v4-flash | #nova |
| Daily-MemorySweep | 6:45am daily | deepseek-v4-flash | #nova |
| TD-Scanner | 6:30am daily | deepseek-v4-flash | #nova |
| DS-Seed-Enforcer | 7:30am daily | deepseek-v4-flash | #nova |
| daily-brief-7am | 7am daily | kimi-k2.6 | #nova |
| gmail-cleanup-daily | 7:15am daily | deepseek-v4-flash | #nova |
| Iris-all-accounts-digest | 7:30am daily | deepseek-v4-flash | #nova |
| Nova-Ops-Assessment | 9am daily | deepseek-v4-flash | #nova |
| Finance-NAS-Backup | 3:38am daily | deepseek-v4-flash | #nova |
| NightSchool-8pm | 8pm daily | deepseek-v4-flash | #nova |
| NightSchool-NAS-Sync | 8:15pm daily | deepseek-v4-flash | #nova |
| Workspace-NAS-Backup | 11pm daily | deepseek-v4-flash | #nova |
| Weekly-MemoryHygiene | Sun 10pm | kimi-k2.6 | #nova |
| Weekly-SkillUpdate | Mon 6am | deepseek-v4-flash | #nova |
| Weekly-SkillDiscovery | Fri 6pm | deepseek-v4-flash | #nova |

### Disabled (6 TradeBot)
All stale, broken paths. Awaiting Opus decision on revival.

## Post Log System

**Script:** `scripts/post_log.py`
**Storage:** `memory/post-log/posts.jsonl` (append-only JSONL)
**Query:** `python scripts/post_log.py recent [--project X] [--days N] [--type X]`
**Stats:** `python scripts/post_log.py stats`
**Dedup:** `python scripts/post_log.py dedup [--days N]`

Every content cron runs `post_log.py log` as its final step. Statuses: published, draft, blocked, failed.

The ops-assessment cron checks the post log daily for:
- Missing entries (content crons that should have logged but didn't)
- blocked/failed entries
- Duplicate titles

## Ontology (Structured Knowledge Graph)

**CLI:** `python skills/ontology/scripts/ontology.py`
**Storage:** `memory/ontology/graph.jsonl` + `schema.yaml`
**Types:** Person, Organization, Project, Task, CronJob, Event, Device, Credential, ServiceAccount, Content, Note

Current state: 11 projects, 31 cron jobs, 7 service accounts, 4 key notes, 2 devices, full relation graph.

The Daily-MemorySweep cron also updates the ontology when project statuses or facts change.

## Known Issues

| Issue | Status | Impact |
|-------|--------|--------|
| UPLOAD_POST_API_KEY not configured | Open | Twitter/Bluesky posting blocked for all crons. EveOnion tweets stay drafts. Kybernauts propaganda can't post to X. |
| aibusinessinsider 403 Cloudflare | Open | ContentNova cron runs daily but site rejects with 403. Articles likely failing. |
| Unsplash API broken (401) | Open | Featured images not generating for ContentNova articles. |
| DS API file upload broken (101) | Workaround | Using SMB drop to `\\MND\video\watch` instead. |
| C: drive 9.5% free | Monitor | ~163 GB free of 1.7 TB. No alerting set up yet. |

## Security

- **No hardcoded passwords** in any script. All credentials read from `.secrets` file or env vars.
- **Pre-commit hook** catches `password=` patterns. Use `--no-verify` when safe.
- **Repo is private.** Git history rewritten with git-filter-repo, secrets scrubbed.
- **Ontology Credential type** only stores `secret_ref` (pointer to `.secrets`), never the secret itself.

## File Organization

```
workspace/
├── AGENTS.md          # Agent behavior rules
├── SOUL.md            # Persona definition
├── USER.md            # Human preferences
├── IDENTITY.md        # Nova identity + avatars
├── TOOLS.md           # Tool/skill notes
├── MEMORY.md          # Curated long-term memory
├── HEARTBEAT.md       # Heartbeat checklist
├── .secrets           # Credentials (gitignored)
├── .learnings/        # Error logs and corrections
├── docs/
│   └── scheduler.md   # Cron schedule + load analysis
├── memory/
│   ├── YYYY-MM-DD.md  # Daily logs
│   ├── archive/       # Compressed old dailies
│   ├── ontology/      # Structured knowledge graph
│   ├── post-log/      # Content tracking (JSONL)
│   ├── subminds/      # Campaign plans (Anti-Yagas, etc.)
│   └── working-buffer.md  # Context compaction recovery
├── scripts/
│   ├── content-nova/  # Content pipeline (quality gate, publish, images)
│   ├── kybernauts/     # Yagas intel scripts
│   ├── gmail_*.py      # Spam pipeline
│   ├── post_log.py    # Unified content tracker
│   ├── grep_context.py # Context-efficient file search
│   └── [50+ scripts]  # Various automation
└── skills/            # Installed skill definitions
```

## Adding a New Cron

Checklist:
- [ ] What model? (flash for ops, m3 for creative, k2.6 for live creative)
- [ ] What time? (check scheduler.md load chart, avoid conflicts)
- [ ] Timeout? (default 180s, heavy jobs 300-600s)
- [ ] Post log? (All content crons must call `post_log.py log` as final step)
- [ ] Delivery channel? (#nova, #wordpress, #eveonion, #kybernauts, #finance)
- [ ] Failure alerts? (after 2 consecutive errors, 1h cooldown)
- [ ] Update scheduler.md
- [ ] Update ontology (CronJob entity + belongs_to relation)
- [ ] Update this doc

## Changelog

### 2026-08-02 — Infrastructure Documentation Created
- Created docs/infrastructure.md with full system architecture
- Documented all 29 enabled crons with models, channels, post-log status
- Listed 5 known issues with status
- Documented post log system, ontology, file organization
- Added cron creation checklist