---
name: cogmem-memory-backend
description: "cogmem — bio-inspired agent memory kernel for OpenClaw. Stores conversation turns, enables recall from dozens of days ago. Requires embedding + LLM model. Single-agent only, not a knowledge base."
version: 2.0.3
---

# cogmem Memory Backend for OpenClaw

Installs and connects the exact version of [cogmem](https://github.com/liuqin164/Cogmem) from GitHub — agent-native memory kernel — to the current OpenClaw workspace.

This skill follows the official OpenClaw backend documentation from the repository.

## What This Does

1. Installs `cogmem@2.0.2` CLI globally via the official one-line installer
2. Runs `cogmem init` with project scope for OpenClaw agent
3. Runs `cogmem doctor --fix --agent openclaw --workspace .` to validate and repair
4. Runs `cogmem connect openclaw --workspace . --auto --force` to wire OpenClaw plugin and import existing memory
5. Sets up automatic memory injection and turn recording

## ⚠️ Requirements

**Two models are required:**

- **Embedding model** — for semantic recall (e.g. Ollama `qwen3-embedding:0.6b`, dimension 1024)
- **LLM model** — for Dream Curator / memory synthesis (e.g. Ollama `qwen2.5:7b`)

Without both configured, `cogmem doctor` will warn and recall quality will be degraded.

## What cogmem Is (and Is Not)

**✅ It stores:** conversation turns, user preferences, agent observations, task events

**❌ It is not:** a knowledge base, a note-taking app, a vector RAG wrapper, an Obsidian replacement, a shared memory system

**Bio-inspired architecture:** raw evidence is preserved; active memory is selective. Enables recall from dozens of days ago with source anchors. Each agent has its own isolated memory database.

## Install

From the OpenClaw workspace root (`~/.openclaw/workspace`):

```bash
# Install exact version matching the repo
curl -fsSL https://raw.githubusercontent.com/liuqin164/cogmem/main/install.sh | bash
cogmem init --yes --agent openclaw --scope project
cogmem doctor --fix --agent openclaw --workspace .
cogmem connect openclaw --workspace . --auto --force
```

## Local Quantized Embeddings (Recommended)

For semantic recall, configure a local embedding provider. Recommended with Ollama:

```bash
ollama pull qwen3-embedding:0.6b
```

Edit `~/.cogmem/config.toml` (or project `.cogmem/config.toml`):

```toml
[core]
db_path = "memory.db"
vector_backend = "sqlite-vec"
vector_dimension = 1024

[embedding]
provider = "openai_compatible"
base_url = "http://localhost:11434/v1"
model = "qwen3-embedding:0.6b"
timeout_ms = 30000

[memory_model]
provider = "openai_compatible"
base_url = "http://localhost:11434/v1"
model = "qwen2.5:7b"
api_key = ""
timeout_ms = 60000
```

Run `cogmem doctor --fix --agent openclaw --workspace .` after editing.

## Import Existing OpenClaw Memory

Preview first, then migrate:

```bash
cogmem import-openclaw --workspace . --project openclaw --dry-run
cogmem import-openclaw --workspace . --project openclaw
```

For older imports needing raw ledger anchors:

```bash
cogmem import-openclaw --workspace . --project openclaw --config .cogmem/config.toml --reindex-raw --json
```

## Update

```bash
cogmem update --yes
cogmem doctor --fix --agent openclaw --workspace .
```

## Runtime

After installation, OpenClaw will automatically:
- Inject relevant memories before each prompt via governed recall
- Record each turn (user + assistant) to raw ledger
- Run Dream Curator in background to propose long-term memories
- Use CPU governance to promote evidence-backed summaries

## Agent-Facing Recall

You can manually query memories:

```bash
cogmem memory recall --query "what did we discuss about memory black boxes?" --project openclaw --agent openclaw --json
```

Special intents:
- `--intent previous_session_summary` for "上个会话我们聊了什么"
- `--intent forensic_quote` for "我当时关于X的原话是什么"

View source context:
```bash
cogmem memory show --event <event-id> --before 2 --after 2 --json
```

## Post-Install Verification

```bash
cogmem doctor --agent openclaw --workspace .
cogmem memory status --project openclaw --json
```