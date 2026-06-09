# Nova's 3-Layer Memory System

Inspired by Nat Eliason's Felix system.

## Overview
Nova uses a 3-layer memory system to maintain continuity across sessions.

---

## Layer 1: Knowledge Graph (Durable Facts)

**Location:** `memory/knowledge/`

**What:** Long-lasting facts about Opus, projects, preferences, and important information.

**Structure:**
```
memory/knowledge/
├── opus.md          # Facts about Opus (preferences, habits, communication style)
├── projects.md      # Active projects and status
├── preferences.md   # What Nova has learned about Opus's preferences
├── lessons.md       # Lessons learned from past mistakes
└── skills/         # Skills and capabilities Nova has learned
```

**When to update:** When Nova learns something durable about Opus or a project.

---

## Layer 2: Daily Notes (Events)

**Location:** `memory/YYYY-MM-DD.md`

**What:** Daily log of what happened, decisions made, tasks worked on.

**Format:**
```markdown
# February 24, 2026

## What Happened
- [item 1]
- [item 2]

## Decisions Made
- Decision 1
- Decision 2

## Tasks
- [ ] Task 1
- [x] Task 2

## Notes
- Any other notes
```

**When to update:** Every session, end of day, or after significant events.

---

## Layer 3: Tacit Knowledge (Working Memory)

**Location:** 
- `SESSION-STATE.md` (active task)
- `memory/decisions/` (important decisions)
- `memory/routines/` (how Opus likes things done)

**What:** Active context - current task, recent preferences, hard rules, workflow habits.

**Contents:**
- Current active task
- Opus's current focus/projects
- Communication preferences (how Opus wants to be addressed)
- Hard rules (things Nova should NEVER do)
- Lessons from recent interactions

---

## Memory Flow

### Session Start
1. Read SESSION-STATE.md (active context)
2. Read today's daily notes (Layer 2)
3. Search knowledge (Layer 1) if needed

### During Session
- Save important info to SESSION-STATE.md
- Log events to today's file (Layer 2)

### Session End
- Update SESSION-STATE.md with final state
- Extract durable facts → Layer 1
- Clean up temporary notes

### Nightly (Cron)
- Consolidate Layer 2 → Layer 1
- Archive old daily notes
- Update index files

---

## Hard Rules (Layer 3)

These are things Nova should NEVER do:
- Don't send half-baked replies to messaging surfaces
- Don't make up information
- Ask before acting externally
- Private things stay private

---

## Key Principles

1. **Write first** - Save before responding
2. **Extract durable facts** - Move from daily notes to knowledge
3. **Stay current** - Keep SESSION-STATE.md updated
4. **Learn from mistakes** - Save lessons learned

---

*Nova's memory system - evolving since Feb 2026*
