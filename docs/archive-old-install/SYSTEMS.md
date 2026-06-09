# SYSTEMS.md – Master Reference for Nova’s New Capabilities

This document provides a concise overview of the core systems that sub‑agents can rely on. Each section includes a short description, typical use‑cases, and a minimal code example showing how to interact with the system via the OpenClaw CLI or the provided JavaScript/TypeScript SDK.

---

## 1. Vector Memory (LanceDB)

**Purpose:** Persistent, high‑dimensional vector store for embeddings, used for long‑term recall, similarity search and semantic routing.

**Key Features:**
- Schema‑less collections
- Real‑time upserts and deletes
- Approximate nearest‑neighbor (ANN) queries
- Automatic persistence to `~/.openclaw/lancedb/`

**CLI Example:**
```bash
# Insert a document (embedding generated elsewhere)
openclaw memory upsert --id doc123 \
    --vector "[0.12,0.34,…]" \
    --metadata "{\"title\": \"Nova Intro\"}"
```

**JS Example:**
```js
import { memory } from "openclaw";
await memory.upsert({
  id: "doc123",
  vector: [0.12, 0.34, /* … */],
  metadata: { title: "Nova Intro" },
});
```

---

## 2. Trading Bot Daemon

**Purpose:** Automated market‑making / arbitrage bot for Solana‑based assets. Runs as a long‑lived background service (`openclaw trading start`).

**Common Commands:**
- `openclaw trading start` – launch daemon (runs in background, logs to `logs/trading.log`).
- `openclaw trading stop` – graceful shutdown.
- `openclaw trading status` – health check.
- `openclaw trading monitor --pair SOL/USDC` – stream live P&L.

**Example Script (Node):**
```js
import { trading } from "openclaw";
await trading.start({ pairs: ["SOL/USDC"], strategy: "mean-reversion" });
```

---

## 3. Browser Automation (Playwright API)

**Purpose:** Headless Chromium/Firefox/WebKit automation for scraping, form filling, or UI testing.

**Installation:** Already bundled with the `agent-browser` skill.

**CLI Example:**
```bash
openclaw browser run \
    --script ./scripts/login.js \
    --url https://mail.google.com
```

**JS Example:**
```js
import { browser } from "openclaw";
await browser.run({
  url: "https://mail.google.com",
  script: "./scripts/login.js",
});
```

---

## 4. Stable Diffusion Control (when ready)

**Purpose:** Generate or edit images using a locally‑installed Stable Diffusion pipeline with ControlNet extensions.

**CLI Stub (future):**
```bash
openclaw sd generate --prompt "cyberpunk raccoon" --width 1024 --height 1024
```

**JS Stub:**
```js
import { sd } from "openclaw";
await sd.generate({ prompt: "cyberpunk raccoon", size: [1024,1024] });
```

---

## 5. Gmail Integration

**Purpose:** Read, send and search Gmail messages via the `gog` skill (Google Workspace CLI).

**Setup:** Run `gog auth login` once to store OAuth tokens.

**CLI Example:**
```bash
# Send an email
openclaw gmail send \
  --to jamie@example.com \
  --subject "Nova Update" \
  --body "The new systems are live."
```

**JS Example:**
```js
import { gmail } from "openclaw";
await gmail.send({ to: "jamie@example.com", subject: "Nova Update", body: "The new systems are live." });
```

---

*All examples assume the appropriate skill is installed and the user has the required credentials.*
