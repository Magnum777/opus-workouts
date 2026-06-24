# Task Prism Integration — Nova/OpenClaw Workspace
# Created 2026-06-15 during P2 Integration Day

## Purpose

Use `task-prism` skill when Opus (or I) needs:
- Task decomposition for complex multi-step projects
- WBS (Work Breakdown Structure) for new features
- Sprint planning for agile workflows
- Resource/skill mapping before starting work

## Quick-Start Template

When Opus says something like:
- "I need to build X"
- "How should we approach Y?"
- "Break this down for me"

→ Switch to **Quick Mode** (he gave goal + rough scope)
→ Generate a condensed WBS with PERT estimates
→ Output as a Task in ontology + update PROJECT-STATUS.md

## Integration Points

### 1. Ontology Bridge

After task-prism produces a WBS, I can:
1. Create Project entity (if new) in `memory/ontology/graph.jsonl`
2. Create Task entities for each WBS item
3. Link them via `belongs_to` / `blocks` relations
4. Query later: `python skills/ontology/scripts/ontology.py query --type Task --where '{"project":"proj_X"}'`

### 2. MyKnowledge Bridge

Large task decomposition outputs go into:
- `.myknowledge/global/{project-name}/requirements/REQ-YYYYMMDD-001/README.md`
- `.myknowledge/global/{project-name}/PROJECT-STATUS.md`

### 3. MEMORY.md Bridge

Only distilled learnings from task-prism go into MEMORY.md:
- "TradeBot v2 decomposition: 6 phases, 23 tasks, 14-week estimate"
- Not the full WBS (too large)

## Pattern Library

### Pattern: Feature Build
```
Input: "Add a portfolio rebalancing feature to TradeBot"
Mode: Quick (Opus knows the domain)
Output: 4-phase WBS with PERT, skill mapping (Solana/web3 + Python)
→ Create Tasks in ontology, link to proj_tradebot
→ Write requirements to .myknowledge/global/tradebot-rebalance/
```

### Pattern: New Project Discovery
```
Input: "I want to build a crypto tax reporter"
Mode: Full (needs clarification)
Questions: Which chains? API or CLI? Free or paid? Tax year scope?
→ After clarification → WBS → ontology + myknowledge
```

### Pattern: Sprint Planning
```
Input: "Plan next 2 weeks for ContentNova"
Mode: Agile
Output: Sprint backlog with story points, content pipeline tasks
→ Link to proj_contentnova in ontology
```

## Usage Command

When triggered by Opus, I invoke task-prism natively (no external CLI — it's prompt-based skill).
Just apply the 12-dimension framework from SKILL.md inline.

---
Last updated: 2026-06-15
