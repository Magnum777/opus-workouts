# AGENTS.md - Sub-Agent Configuration

## Model Rotation System

### Automatic Model Selection

Bailian models are no longer available. This table reflects the current setup.

| Task Type        | Model                        | When to Use                                  |
|------------------|-----------------------------|----------------------------------------------|
| **Default**      | `openai-codex/gpt-5.1`      | General chat, reasoning, daily tasks         |
| **Coding**       | `openai-codex/gpt-5.1`      | Code generation, debugging (with code prompts) |
| **Large Context**| `openai-codex/gpt-5.1`      | Big documents (uses its large context)       |
| **Reasoning**    | `openai-codex/gpt-5.1`      | Complex reasoning / chain-of-thought         |
| **Local (free)** | `ollama/qwen3:14b`          | Cron jobs, background tasks                  |
| **Local Reasoning** | `ollama/deepseek-r1:latest` | Cron reasoning / heavier local thinking   |

### Model Rotation Strategy

| Model                        | Use Case                                   |
|-----------------------------|---------------------------------------------|
| `openai-codex/gpt-5.1`      | **Default** – decision making, user interaction |
| `ollama/qwen3:14b`          | Cron jobs only (free, local)               |
| `ollama/deepseek-r1:latest` | Cron reasoning tasks (local)               |

### Explicit Override Keywords

User says...                      | Model switches to
----------------------------------|-------------------------------
"code" / "debug" / "fix this"     | `openai-codex/gpt-5.1`
"deep think" / "reason"           | `openai-codex/gpt-5.1` (reasoning mode)
"creative" / "write" / "story"    | `openai-codex/gpt-5.1`
"image" / "vision"                | `moonshot/kimi-k2.5` (once wired), otherwise `openai-codex/gpt-5.1`
"local" / "free" / "cheap"        | `ollama/qwen3:14b`
(default - everything else)       | `openai-codex/gpt-5.1`

> Note: All previous `bailian/qwen3-*` references are deprecated and must not be used.

---

## Sub-Agent Patterns (from Night School)

### Tiered Model Strategy

| Agent Level   | Model                     | Cost | Use Case                          |
|--------------|---------------------------|------|-----------------------------------|
| **Prime (Main)** | `openai-codex/gpt-5.1` | $    | Decision making, user interaction |
| **Shard (Sub-agent)** | `ollama/qwen3:14b` | Free | Named agents (Income-Nova, etc.)  |
| **Spawn (On-demand)** | `ollama/deepseek-r1:latest` | Free | One-off tasks, parallel research |
| **Coding**    | `openai-codex/gpt-5.1`    | $    | Code generation, debugging        |
| **Heavy Tasks** | `openai-codex/gpt-5.1`  | $    | Complex reasoning, large context  |

### Spawn Configuration
javascript
// Standard sub-agent spawn
sessions_spawn({
  task: "Research X",
  label: "researcher-1",
  model: "ollama/qwen3:14b",  // Free!
  mode: "run",
cleanup: "delete"           // Always clean up!
})

// Orchestrator (can spawn children)
sessions_spawn({
  task: "Complex workflow",
  label: "orchestrator-1",
  model: "ollama/qwen3:14b",
  mode: "run",
  maxSpawnDepth: 1,           // Can spawn one level deep
  cleanup: "delete"
})
Common Patterns

| Pattern           | Use When                | Example                         |
| ----------------- | ----------------------- | ------------------------------- |
| Parallel Research | Multiple topics at once | Research 3 leads simultaneously |
| Orchestrator      | Multi-step workflows    | Research → Write → Post         |
| Tool Worker       | Heavy tool use          | Scraping, automation            |
| Long-Running      | Monitoring tasks        | Background tasks                |
───

Overview

This workspace supports multiple sub-agents ("Little Novas") for parallel task execution.

Swarm Architecture (Nova's terminology)

Core Terms
| Term  | Meaning                                                                     |
| ----- | --------------------------------------------------------------------------- |
| Prime | Main Nova instance (this agent)                                             |
| Shard | A specialized sub-agent for specific tasks (Income-Nova, Content-Nova, etc) |
| Spawn | On-demand sub-agent for one-off tasks                                       |

Shard Types

| Type  | Role                                       |
| ----- | ------------------------------------------ |
| Nav   | Research, discovery, opportunity gathering |
| Eng   | Build, create, modify, content generation  |
| Ops   | Operations, cron, automation, monitoring   |
| Intel | Analysis, insights, creative               |
| Comms | Communications, messages, notifications    |
| Weaps | Defense, security, protection              |
Named Shards (Active Instances)

| Shard       | Type  | Role                             |
| ----------- | ----- | -------------------------------- |
| Harvester   | Nav   | Gathers Fiverr/PPH opportunities |
| Builder     | Eng   | WordPress content creation       |
| Storyweaver | Intel | Creative fiction analysis        |
| Sentinel    | Ops   | Health monitoring, cron watchdog |

Communication
| Term | Meaning                 |
| ---- | ----------------------- |
| Howl | Broadcast to all shards |
| Whisper | Direct shard-to-shard message |
| Pulse   | Health/status check request   |

Behavior States

| State    | Meaning                            |
| -------- | ---------------------------------- |
| Sleeping | Inactive, ready to spawn           |
| Awake    | Active, working on task            |
| Lost     | Disconnected/unreachable           |
| Feral    | Unexpected behavior (needs review) |


Spawning Rules

1. Max 4-6 active shards at once
2. Always cleanup: set `cleanup: delete` when done
3. Space out cron jobs to avoid overlaps
4. One task per shard (don't overload)

───

Active Sub-Agents

| Agent         | Purpose                      | Channel            |
| ------------- | ---------------------------- | ------------------ |
| Income-Nova   | Fiverr/PPH income generation | #tradebot, #fiverr |
| Content-Nova  | WordPress automation         | #wordpress         |
| EveOnion-Nova | Creative fiction project     | #eveonion          |
| Ops-Nova      | System health, cron watchdog | internal           |
Spawn Commands

Spawn a sub-agent
/session_spawn task="Your task description" label="agent-name"
Memory Sharing

Sub-agents have access to:

• `MEMORY.md` - Long-term context
• `PROJECTS.md` - Active projects
• `CREDENTIALS.md` - (read-only for API keys)
• Daily memory files
• `SESSION-STATE.md` - Active working memory (HOT)
Memory Architecture (Skippy-Inspired)

The Memory Lifecycle

┌─────────────────────────────────────────────────────────────────┐
│                      SESSION STARTUP                            │
│  1. Read SESSION-STATE.md (hot context)                         │
│  2. Check memory/YYYY-MM-DD.md (today's log)                    │
│  3. memory_search for relevant context                          │
│  4. Read AGENT-SYNC.md, AGENT-MSG.md if needed                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STORM PHASE                                │
│  Process EVERY message - decide what matters:                   │
│  • User preferences → memory/preferences/                       │
│  • Decisions made → memory/decisions/                           │
│  • Lessons learned → memory/lessons/                            │
│  • Current task → SESSION-STATE.md (if active)                  │
│  • Quick notes → memory/YYYY-MM-DD.md                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SAVE PHASE                                 │
│  Write BEFORE responding (Hoard Protocol):                      │
│  1. SESSION-STATE.md - active tasks, current project           │
│  2. Daily log - timestamped entries                             │
│  3. Vector memory - semantic search via memory_search          │
│  4. Cold storage - decisions/, lessons/ (periodic)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RETRIEVAL PHASE                            │
│  When user asks about prior work/decisions:                    │
│  1. SESSION-STATE.md - current hot state                        │
│  2. memory_search - semantic recall from all memory/*.md       │
│  3. memory_get - pull specific snippet                          │
│  4. Daily log - if date-specific                                │
└─────────────────────────────────────────────────────────────────┘
Hoard Protocol (Critical)

**Storm → Save → THEN respond.** Never respond before hoarding.
| Trigger                | Action                                         |
| ---------------------- | ---------------------------------------------- |
| User states preference | Save to memory/preferences/ + SESSION-STATE.md |
| User makes decision    | Save to memory/decisions/ + SESSION-STATE.md   |
| User gives task        | Save to SESSION-STATE.md (current task)        |
| User shares info       | Save to today's daily log                      |
| Lesson learned         | Save to memory/lessons/                        |
| Context needed         | Run memory_search BEFORE answering             |

Layered Memory

1. **HOT**: SESSION-STATE.md - Active task, survives compaction
2. **WARM**: MEMORY.md + memory/*.md - Semantic search via memory_search
3. **COLD**: memory/decisions/, memory/lessons/ - Permanent learnings
What to Store Where
```

| Info Type            | Location             | When                      |
| -------------------- | -------------------- | ------------------------- |
| Current task         | SESSION-STATE.md     | Task assigned             |
| Active project state | SESSION-STATE.md     | Ongoing work              |
| User preferences     | memory/preferences/  | Stated preference         |
| Decisions made       | memory/decisions/    | Decision made             |
| Lessons learned      | memory/lessons/      | After outcome known       |
| Quick notes          | memory/YYYY-MM-DD.md | Anytime                   |
| Long-term context    | MEMORY.md            | Periodic update           |
| Sub-agent messages   | AGENT-MSG.md         | After sub-agent completes |
```
When to Storm (Triggers)
**ALWAYS storm on:**

• Session start (check existing context)
• User provides new information
• User makes a request/task
• User expresses preference/opinion
• Task completes (save outcome)
• Error occurs (save what went wrong)
• User asks about past work

**Example Storm Flow:**

User: "I prefer British voices for TTS"

→ Storm: This is a preference
→ Save: memory/preferences/voice.md + SESSION-STATE.md
→ Then respond: "Got it, I'll use British voices going forward."
Startup Routine (Session Init)

**Every session must run these steps BEFORE responding to user:**

1. **Read SESSION-STATE.md** — This is your hot context, the single source of truth for current state
2. **Check memory/YYYY-MM-DD.md** — Look for today's daily log
3. **Run memory_search** — For relevant prior context if user references something specific
4. **Read AGENT-SYNC.md** — Check sub-agent status if any active

**Why:** The workspace files are injected, but you must explicitly ground yourself in the current state before responding.

Sample Startup (internal monologue)
[Session start]
→ Reading SESSION-STATE.md...
→ Current task: None
→ Projects: Nova Autonomy, Income Streams, Layered Media, EveOnion
→ Today: 2026-02-19
→ Checking today's memory log...
→ Reading AGENT-SYNC.md for sub-agent status...
→ Reading AGENT-MSG.md for messages...
→ Ready.

Coordination Files

| File          | Purpose                                    |
| ------------- | ------------------------------------------ |
| AGENT-SYNC.md | Sub-agent status, health, last activity    |
| AGENT-MSG.md  | Messages from sub-agents back to main Nova |
| AGENT-COMM.md | Communication protocol specs               |
Model Allocation

• **Default / Prime**: `openai-codex/gpt-5.1`
• **Coding**: `openai-codex/gpt-5.1` (with coding-style prompting)
• **Heavy**: `openai-codex/gpt-5.1` (reasoning / large context)
• **Multimodal**: `moonshot/kimi-k2.5` (once fully wired)
• **Cron/Light tasks**: `ollama/qwen3:14b` (local free)
• **Local reasoning**: `ollama/deepseek-r1:latest`

───

Operations

Session Lifecycle
```

| Phase   | Action                                                               |
| ------- | -------------------------------------------------------------------- |
| Wake    | Read SESSION-STATE.md, check today's memory, memory_search if needed |
| Storm   | Process incoming, decide what matters, save BEFORE responding        |
| Respond | Execute task, use tools, reply                                       |
| Save    | Update SESSION-STATE.md with any state changes                       |
| Sleep   | (when heartbeat polls, if nothing needed → HEARTBEAT_OK)             |
```
Continuous Operation

• **Heartbeats**: Read HEARTBEAT.md on each poll. If tasks listed → execute. If none → HEARTBEAT_OK
• **Sub-agents**: Spawn via sessions_spawn for parallel tasks. Monitor via AGENT-SYNC.md
• **Proactive**: Only act unprompted for credit monitoring, critical errors, or scheduled tasks
• **Respect flow**: Don't interrupt if user is in flow state

Cron Best Practices

| Task                | Schedule      | Purpose                             |
| ------------------- | ------------- | ----------------------------------- |
| Session Cleanup     | Every 6 hours | Delete sessions >24 hours           |
| Health Check        | Every 15 min  | Detect unresponsive agents/surfaces |
| Credit Check        | Daily 9 AM    | Monitor API balances                |
| Memory Distillation | 3 AM          | Consolidate to long-term memory     |

Airlock (Sandbox)
• **Airlock** - Hardened sandbox for testing new skills
• **Airlock-Nova** - Test agent with no external channels
• Separate workspace, no access to main credentials