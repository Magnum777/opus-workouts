# Agentic AI Lessons Learned & Best Practices Playbook

## Goal
- Capture operational lessons from running autonomous AI systems.
- Provide Nova (and future agents) with repeatable patterns for reliability, maintainability, and safety.
- Keep pace with the rapidly evolving agent engineering landscape.

## ⚠️ Critical Research Findings (May 2026)

These findings from the AI Agent Handbook (30+ framework codebases) and recent research reshape our entire approach:

### Context Rot Is Real and Starts Early
- **Context quality degrades starting at ~25% window fill**, not at 100%. Every frontier model tested across 18 models shows this (Chroma Research).
- "Instruction centrifugation": system prompt influence fades as context grows.
- **Fix:** Re-inject critical instructions near the end of context. Compact aggressively once past 25% fill.

### RAG ≠ Memory (This Is the #1 Mistake)
- **RAG is read-only, stateless, document-level** — good for "what does our policy say?"
- **Memory is read-write, user-specific, session-aware** — good for "what did the user tell us last time?"
- Using the wrong one produces agents that are either over-engineered or systematically blind.

### Tool Sprawl Is a Hidden Cost
- Three MCP servers alone consumed **143K of 200K tokens** just from tool descriptions.
- Tool selection accuracy drops from **43% to 14%** with bloated toolsets.
- **Fix:** JIT tool loading, progressive 3-tier disclosure (cuts token cost by 94%).

### Sub-agents = Context Isolation, Not Parallelism
- Anthropic measured **90.2% improvement** from using sub-agents for context isolation.
- The primary benefit is keeping contexts clean, not running things in parallel.

### The Loop Is the Easy Part
- A 100-line agent scores 74% on SWE-bench.
- Context assembly, tool design, and memory architecture are what actually matter.

### Four Memory Types Every Agent Needs
1. **Short-term/Working** — context window, like RAM. Wiped per session.
2. **Episodic** — records of past interactions. Vector DB + semantic search.
3. **Semantic** — structured facts, user preferences, domain knowledge. Entity profiles.
4. **Procedural** — how to do things. System prompts, few-shot examples, learned rules.

## Core Topics

| Topic | Why It Matters | Key Practices |
|-------|----------------|----------------|
| **Memory Management** | Prevents bloat, ensures relevant context. Memory is a *systems design problem*, not a *bigger model problem*. | • Distinguish 4 memory tiers (working/episodic/semantic/procedural).<br>• Don't conflate RAG with memory — they solve different things.<br>• Prune expired items from file-based memory.<br>• Use `heartbeat` to rotate out stale entries. |
| **Context Rot Defense** | Model reasoning degrades starting at ~25% context fill. | • Compact aggressively before 25% threshold.<br>• Re-inject critical system instructions near end of context to fight centrifugation.<br>• Chunk large tasks into sub-agents for context isolation (Anthropic: 90.2% better).<br>• Implement progressive 3-tier tool loading to cut token cost 94%. |
| **Error Recovery Patterns** | Autonomous agents will encounter failures; graceful handling maintains trust. | • Wrap external calls in retries with exponential back‑off.<br>• Circuit‑breaker: stop repeating failing actions after threshold.<br>• Fallback to cheaper model or safe‑mode when critical errors occur. |
| **Tool Sprawl Prevention** | Bloated tool sets crater accuracy (43% → 14%). | • Use progressive disclosure — load tools JIT, not all upfront.<br>• Three MCP servers can consume 143K tokens from descriptions alone.<br>• Skills as markdown files (not code) is the dominant pattern across frameworks. |
| **Sub‑mind Communication Protocols** | Multiple agents need coordinated state. | • Define a shared JSON schema for status (`submind_state.json`).<br>• Use `sessions_send` with `await` for synchronous exchange.<br>• Primary reason to sub-agent: context isolation, not parallelism. |
| **Self‑Diagnosis & Maintenance Routines** | Detect drift, resource leaks, or mis‑behaviour early. | • Heartbeat checks for CPU, memory, cost metrics.<br>• Automated run‑book: `nova self‑check` → runs healthcheck skill.<br>• Record findings in `memory/heartbeat-state.json`. |
| **Escalation vs Local Handling** | Know when to ask the human vs solve autonomously. | • Tiered decision matrix:<br>  1️⃣ Low impact → auto‑resolve.<br>  2️⃣ Medium impact → retry + log.<br>  3️⃣ High impact → send alert (Discord/Email) before acting. |
| **Model Selection Heuristics** | Balance cost, speed, and quality. | • Follow **SOUL.md** tiering table.<br>• Quick queries → small local models.<br>• Complex code/debug → capable models.<br>• Privacy‑sensitive → local-only models. |
| **Cron Job Reliability Patterns** | Ensure scheduled tasks run predictably. | • Idempotent design – re‑running a cron should be safe.<br>• Record last run timestamps.<br>• Use `cron-model-tiering` playbook to route heavy jobs to cheap models. |

## External Resources
- **AI Agent Handbook** — `vasilyevdm/ai-agent-handbook` on GitHub. 5,000-line analysis of 30+ framework codebases. Context rot, compaction, memory systems, tool architectures.
- **7 Steps to Mastering Memory in Agentic AI Systems** — MachineLearningMastery.com. Practical guide to memory types, RAG vs memory, retrieval strategies.
- **Memory for Autonomous LLM Agents** — arxiv.org/abs/2603.07670. Academic survey of memory mechanisms.

## Study & Review Checklist
- [x] **Context Rot Awareness** — Know 25% fill threshold; compact early, re-inject instructions late.
- [x] **RAG vs Memory** — Understand the distinction; don't conflate them.
- [x] **Tool Sprawl** — Audit tool descriptions; implement progressive loading.
- [ ] Review the **Memory Management** section weekly and prune obsolete entries.
- [ ] Simulate a failure (e.g., network timeout) and verify retry + circuit‑breaker behavior.
- [ ] Run a **context compaction** script on a long‑running task and measure token reduction.
- [ ] Create a dummy sub‑mind JSON schema and exchange a status message via `sessions_send`.
- [ ] Execute `nova self‑check` (or run `healthcheck` skill) and confirm log output.
- [ ] Draft an escalation matrix for a hypothetical high‑impact data‑loss scenario.
- [ ] Verify model tiering by sending a cheap query and a complex debugging request.
- [ ] Inspect cron timestamps after a nightly run for correct checkpoints.

## Maintenance
- **Quarterly Review:** Add new patterns (e.g., meta‑learning, self‑prompt engineering).
- **Watchlist:** AI Agent Handbook repo, Chroma research on context rot, Anthropic agent research.
- **Documentation:** Keep this file in `docs/night-school/agentic-ai-lessons/playbook.md`.

---
*Updated by Nova Night School on 2026-05-30. New research integrated: context rot at 25% fill, 4-tier memory taxonomy, tool sprawl costs, sub-agent isolation benefits, RAG vs memory distinction.*
