# MyKnowledge — Nova Global Knowledge Base

> Initialized 2026-06-15 during P2 Integration Day

## Structure

```
.myknowledge/
├── global/              # Cross-project knowledge
│   ├── README.md        # This file
│   ├── requirements/    # Global requirements (rare)
│   ├── public/          # Shareable docs
│   ├── archive/         # Old/completed
│   └── PROJECT-STATUS.md
├── templates/           # Reusable templates
│   ├── task-prism-integration.md
│   └── ontology-usage.md
└── projects/            # Per-project KBs (if needed)
```

## Active Knowledge Bases

| Project | Status | Location |
|---------|--------|----------|
| TradeBot | Active | `.myknowledge/global/tradebot/` (on demand) |
| ContentNova | Active | `.myknowledge/global/contentnova/` (on demand) |
| WordPress Empire | Active | `.myknowledge/global/wordpress/` (on demand) |

## Usage

- **Create KB**: `mkdir .myknowledge/global/{project}/` + write README.md
- **Add requirement**: Create `requirements/REQ-YYYYMMDD-XXX/README.md`
- **Check status**: Read `PROJECT-STATUS.md`
- **Resume work**: Say "continue {project}" → I read PROJECT-STATUS.md + context

## Auto-Record Rules

Complex tasks (3+ steps, multi-day, or involving data/docs) trigger automatic KB creation:

```
Detected: Multi-step task "Build crypto tax reporter"
→ Created KB: .myknowledge/global/crypto-tax-reporter/
→ Created REQ: requirements/REQ-20260615-001/
```

---
