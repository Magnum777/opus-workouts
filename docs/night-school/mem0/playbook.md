# Mem0 Persistent Memory - Playbook

## Overview

**Mem0** ("mem-zero") is a persistent memory layer for AI agents that enables personalized, context-aware interactions across sessions. It's directly relevant to Nova's V2 goal of "elite-longterm-memory."

## Why It Matters for Nova

| Problem | Mem0 Solution |
|---------|---------------|
| Context compaction wipes memories | External storage (outside context window) |
| Session restart = memory loss | Auto-recall on session start |
| Manual memory curation needed | Auto-capture extracts what's important |
| No semantic search | Vector-based similarity search |

## Key Features

- **Multi-Level Memory**: User, Session, and Agent state
- **Auto-Recall**: Searches relevant memories before each response
- **Auto-Capture**: Extracts and stores important facts after each exchange
- **Graph Memory**: Tracks entity relationships (people, places, events)
- **Semantic Search**: Find memories by meaning, not keywords

## Performance Stats

- **+26%** accuracy vs OpenAI Memory on LOCOMO benchmark
- **91%** faster than full-context approaches
- **90%** lower token usage

## OpenClaw Integration

**Great news**: There's already an official Mem0 plugin for OpenClaw!

### Option 1: Mem0 Cloud (Easiest)

```bash
openclaw plugins install @mem0/openclaw-mem0
```

Then add to `openclaw.json`:
```json
{
  "openclaw-mem0": {
    "enabled": true,
    "config": {
      "apiKey": "${MEM0_API_KEY}",
      "userId": "nova-user"
    }
  }
}
```

Get API key at: https://app.mem0.ai

### Option 2: Self-Hosted (Fully Local)

```json
{
  "openclaw-mem0": {
    "enabled": true,
    "config": {
      "mode": "open-source",
      "userId": "nova-user",
      "oss": {
        "embedder": { "provider": "ollama", "config": { "model": "nomic-embed-text" } },
        "vectorStore": { "provider": "qdrant", "config": { "host": "localhost", "port": 6333 } },
        "llm": { "provider": "anthropic", "config": { "model": "claude-sonnet-4-20250514" } }
      }
    }
  }
}
```

No API key needed for self-hosted. Uses local Qdrant + Ollama.

## Memory Scopes

| Scope | Description | Use Case |
|-------|-------------|----------|
| **User (Long-term)** | Persists across all sessions | Name, tech stack, preferences, decisions |
| **Session (Short-term)** | Current session only | Active task, current project state |

## Tools Available

- `memory_search` - Semantic query
- `memory_store` - Save specific facts
- `memory_list` - List all memories
- `memory_get` - Retrieve specific memory
- `memory_forget` - Delete memories

## Installation Path for Nova

Since Nova V2 already has "elite-longterm-memory" via LanceDB, Mem0 would be a potential V3 upgrade or alternative:

1. **Try cloud version first** - Quick test with API key
2. **Evaluate self-hosted** - If privacy/control needed (Qdrant on NAS)
3. **Compare with LanceDB** - Decide which provides better value

## Resources

- Website: https://mem0.ai
- GitHub: https://github.com/mem0ai/mem0
- OpenClaw Plugin: https://github.com/mem0ai/mem0/tree/main/openclaw
- Docs: https://docs.mem0.ai
- Discord: https://mem0.dev/DiG

## Reading List

- [Mem0 GitHub](https://github.com/mem0ai/mem0) - Full documentation
- [OpenClaw Integration Blog](https://mem0.ai/blog/mem0-memory-for-openclaw) - Specific setup guide
- [Mem0 for OpenClaw Docs](https://docs.mem0.ai/integrations/openclaw) - Official integration docs
