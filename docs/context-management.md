# OpenClaw Context Management Guide
## Keeping Context Down While Retaining Viability

### The Core Philosophy
> "Treat the LLM context as a cache and disk memory as the source of truth."

---

## 1. OpenClaw's Built-in Features

### Compaction Modes
```json
"compaction": {
  "mode": "safeguard"  // Recommended: flushes memory before compact
}
```
- **safeguard** (default): Runs silent memory flush BEFORE compaction
- **aggressive**: More compacting, less retention
- **manual**: Only compact when you trigger it

### Pre-Compaction Memory Flush
OpenClaw already does this! When context hits ~80%, it triggers a silent turn:
```
"Store durable memories now. Write any lasting notes to memory/YYYY-MM-DD.md"
```

**Your job:** Reply with important info to save, or `NO_REPLY` if nothing needed.

---

## 2. Best Practices

### A. Session Forking (Most Effective)
Start new sessions for different topics:
```
Session 1: #nova (EVE skill plans)
Session 2: #wordpress (content)
Session 3: #clawincome (outreach)
```
This keeps each context focused and small.

### B. Memory Files as Source of Truth
Store persistent info in:
- `memory/` - Daily logs
- `MEMORY.md` - Long-term context
- Project-specific files

OpenClaw auto-loads these at session start!

### C. Limit Conversation Breadth
Within a session, keep discussions focused:
- ❌ Don't jump between EVE skills → WordPress → Layered Media → personal stuff
- ✅ One topic per session window

---

## 3. Configuration Tweaks

### Set Context Window Cap
```json
"agents": {
  "defaults": {
    "contextWindow": 100000  // Use only 100k instead of 200k
  }
}
```

### Reserve Tokens Floor
```json
"compaction": {
  "reserveTokensFloor": 20000  // Keep 20k tokens free
}
```

### Enable Mem0 (Persistent Memory)
Currently disabled. To enable:
```json
"plugins": {
  "entries": {
    "openclaw-mem0": {
      "enabled": true,
      "config": {
        "mode": "platform",
        "apiKey": "mem0-api-key",
        "userId": "opus"
      }
    }
  }
}
```
Mem0 stores memories externally - survives session restarts!

---

## 4. Quick Wins

| Technique | Effort | Impact |
|----------|--------|--------|
| Start new session for new topic | Low | 🔥🔥🔥 |
| Keep memory/MEMORY.md updated | Low | 🔥🔥 |
| Enable Mem0 | Medium | 🔥🔥🔥 |
| Lower context window cap | Low | 🔥🔥 |
| Fork sub-agents for heavy tasks | Medium | 🔥🔥 |

---

## 5. Recommended Workflow

1. **Daily:** Update `memory/YYYY-MM-DD.md` with key info
2. **Weekly:** Compact/backup `MEMORY.md` 
3. **When context > 70%:** Consider starting fresh session
4. **For big tasks:** Spawn sub-agent (uses separate session)

---

## 6. Current Status Recommendations

Based on your setup:
- ✅ Keep `compaction.mode: "safeguard"`
- ❌ Mem0 is disabled - consider enabling
- ⚠️ You're at 74% - next large task should spawn sub-agent or fork session
- ✅ Night School crons are good (isolated sessions)

---

## Summary

**Keep context down:**
1. Fork sessions for new topics
2. Update memory files proactively  
3. Keep MEMORY.md lean
4. Enable Mem0 for persistent external memory
5. Use sub-agents for heavy lifts

**Retain viability:**
- Safeguard mode auto-flushes before compact
- Memory files persist across sessions
- Forking preserves continuity for each topic
