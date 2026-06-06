# Night School Protocol - Local Version

## Concept

Nova's autonomous learning system - reads material overnight, distills into playbooks for daytime use.

## Local Setup

```
docs/night-school/
├── ai-ml/
│   ├── playbook.md      # ✅ First: Expeditionary Force
│   └── reading-list.md
├── business/
│   ├── playbook.md
│   └── reading-list.md
├── creative/
│   ├── playbook.md
│   └── reading-list.md
├── social-posting-automation/
│   ├── playbook.md      # ✅ May 28, 2026
│   └── RESEARCH.md
├── print-on-demand/
│   ├── playbook.md      # ✅ May 29, 2026
├── postiz/
│   ├── playbook.md
├── mixpost/
│   ├── playbook.md
├── cron-model-tiering/
│   ├── playbook.md      # ✅ May 31, 2026
└── queue/              # Add files here to be read
```

## Completed Sessions

- **Expeditionary Force** (Books 1-6) - Craig Alanson → `ai-ml/playbook.md`
  - Submind architecture, swarm patterns, emergent behavior
- **Social Posting Automation** (May 28, 2026) → `social-posting-automation/playbook.md`
  - Surveyed self-hosted social schedulers: BrightBean Studio, Postiz, Mixpost, Blurt
  - Researched n8n + AI pipeline
  - BrightBean Studio recommended as best all-rounder for Layered Media
- **Print on Demand** (May 29, 2026) → `print-on-demand/playbook.md`
  - Rebuilt stub playbook with fresh 2026 research
  - Validated the $12.39B market, platform strategies, product niches, and pricing formulas
  - Identified our specific advantages (Midjourney prompts bundle, Gumroad, AI creative)
- **Cron Model Tiering** (May 31, 2026) → `cron-model-tiering/playbook.md`
  - Read existing playbook on model cost optimization
  - Distilled key insights for Opus: default to cheap, classify before routing, fallback chains, local first
  - Directly applicable to Nova cron jobs right now

## Usage

Tell Nova:
- "Read [book] tonight"
- "What did Night School learn about X?"
- Add files to queue folder

## NAS Version

- Blocked until NAS password reconnected
- Would use: \\192.168.68.82\home\nova-library\
