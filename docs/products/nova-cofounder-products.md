# Nova AI Cofounder - Product Documentation

## Product Overview

Nova is an autonomous AI cofounder that lives on your machine, handles research, manages systems, and works while you sleep.

## Version Comparison

| Feature | V1 Starter ($25) | V2 Pro ($49-79) | V3 Enterprise ($100+) |
|---------|-------------------|------------------|----------------------|
| **Platform** | OpenClaw | OpenClaw | OpenClaw |
| **Memory** | SESSION-STATE + markdown | elite-longterm-memory | Full layered memory |
| **Search** | Basic | memory_search | Advanced vectors |
| **Voice** | - | edge-tts | SAG + custom TTS |
| **Security** | Basic | prompt-guard | Airlock + guard-rails |
| **Sub-agents** | 2 | 4 | Unlimited |
| **Autonomy** | Scheduled tasks | Self-scheduled | Full autonomous |
| **Support** | Discord | Priority Discord | 1-on-1 onboarding |

---

## V1 Starter - $25

### What's Included

**Core System:**
- OpenClaw installation and configuration
- Discord/Telegram integration
- Sub-agent spawning (2 active)
- SESSION-STATE.md hot memory protocol

**Memory Architecture:**
- WAL (Write-Ahead Log) protocol
- SESSION-STATE.md for active tasks
- MEMORY.md for long-term context
- memory/ folder for structured storage

**Automation:**
- Cron job setup
- Daily publishing workflows
- Health monitoring

**Documentation:**
- Skippy-inspired architecture guide
- Setup walkthrough
- Memory management guide

### Use Cases

- Personal AI assistant
- Automated content publishing
- Research and summarization
- System automation

---

## V2 Pro - $49-79

### Everything in V1, Plus:

**Enhanced Memory:**
- elite-longterm-memory integration
- 5-layer memory architecture (HOT → WARM → COLD → CURATED → CLOUD)
- Automatic memory distillation
- Vector-based semantic search

**Local Search:**
- qmd installation and configuration
- BM25 + vector hybrid search
- Index your notes, docs, knowledge base

**Voice Integration:**
- edge-tts setup (free Microsoft TTS)
- Voice notifications
- Audio summaries

**More Sub-agents:**
- Up to 4 concurrent shards
- Specialized types: Nav, Eng, Ops, Intel

---

## V3 Enterprise - $100+

### Everything in V2, Plus:

**Security First:**
- prompt-guard installation
- Prompt injection protection
- Secret exfiltration prevention
- Owner-only command enforcement

**Airlock Testing:**
- Isolated sandbox environment
- Test new skills safely
- No risk to production systems

**Full Autonomy:**
- Self-scheduling agents
- Cross-channel coordination
- Advanced cron orchestration

**Priority Support:**
- 1-on-1 onboarding call
- Custom agent training
- Priority bug fixes

---

## Technical Architecture

### Memory Layers (Skippy-Inspired)

```
┌─────────────────────────────────────┐
│           SESSION-STATE             │  ← HOT: Active task, survives compaction
│         (SESSION-STATE.md)          │
├─────────────────────────────────────┤
│           WARM STORE                │  ← memory_search over MEMORY.md
│         (semantic search)          │
├─────────────────────────────────────┤
│           COLD STORE                │  ← memory/decisions/, memory/lessons/
│        (permanent learnings)        │
├─────────────────────────────────────┤
│          CURATED ARCHIVE            │  ← MEMORY.md (human-readable)
├─────────────────────────────────────┤
│         (Optional Cloud)            │  ← supermemory backup
└─────────────────────────────────────┘
```

### Shard Types

| Shard | Role | Function |
|-------|------|----------|
| **Nav** | Research | Gather opportunities, research topics |
| **Eng** | Build | Create content, build systems |
| **Ops** | Operations | Cron jobs, monitoring, health |
| **Intel** | Analysis | Insights, creative work |

### Communication Protocol

- **Howl** - Broadcast to all shards
- **Whisper** - Direct shard-to-shard
- **Pulse** - Health/status check

---

## Comparison to Alternatives

| Feature | Nova V1 | ChatGPT | Claude |
|---------|---------|---------|--------|
| Local deployment | ✅ | ❌ | ❌ |
| Sub-agents | ✅ | ❌ | ❌ |
| Cron automation | ✅ | ❌ | ❌ |
| Custom memory | ✅ | ❌ | ❌ |
| Security tools | V3 | ❌ | ❌ |
| **Price** | **$25** | $20/mo | $20/mo |

---

## Installation Requirements

- Windows 10/11 or macOS
- OpenClaw gateway
- (Optional) Ollama for local embeddings
- (Optional) API keys for enhanced features

---

## Support

- Discord community
- Documentation wiki
- Night School autonomous learning

---

*Last Updated: 2026-02-17*
