# Nova Learnings Archive

## 2026-06-06 — Cron Model Assignment Fix

**Issue:** Kybernauts-Propaganda and Kybernauts-ForumBump crons were failing with "Agent couldn't generate a response" when assigned to `kimi-k2.6`.

**Root cause:** `kimi-k2.6` appears to timeout or struggle on ops/scans tasks that involve browser automation, exec commands, and tool-heavy workflows. The model works fine for creative writing but not for agent-turn cron payloads with complex tool use.

**Fix:** Switched both back to `deepseek-v4-flash:cloud` per AGENTS.md rule — "Use deepseek-v4-flash for ops/scans (checks, sweeps, data pulls, simple reports)."

**Lesson:** Don't default to kimi-k2.6 for all cron tasks just because it's the main model. Match model to task type. Document this in scheduler.md.

---

## 2026-06-14 — Weekly Skill Discovery Scan

**Scanned 11 queries on ClawHub. Results:**

**New skills worth flagging:**

| Skill | Rating | What it does | Relevance |
|-------|--------|-------------|-----------|
| `agent-workflow-playbook` | 1.133 | Multi-agent orchestration framework with design patterns for autonomous AI systems | High — we run TradeBot + EveOnion + Kybernauts in parallel; could improve coordination |
| `szzg007-web-deep-research` | 2.590 | Deep research across 17+ platforms, auto-generates market/competitor reports with risk analysis | High — could replace/supplement our manual research for TradeBot token scouting |
| `azure-flux-image-gen` | 1.133 | FLUX.2-pro image generation via Azure AI Foundry | Medium — we already have `ai-social-media-content` for images; this is Azure-backed, might have different quality/cost |
| `mflux` | 0.520 | Local FLUX.2 image generation via Apple MLX (MLX-only, macOS) | Low — we don't have Apple Silicon, and we prefer cloud for crons |

**Already installed that showed up in search:**
- `ai-social-media-content` — content generation (already have)
- `browser-use` — browser automation (already have)
- `openclaw-tavily-search` — web search (already have)

**Action:** None installed. `agent-workflow-playbook` and `szzg007-web-deep-research` look interesting but would need evaluation against our current workflows. Recommend waiting for a slow day if Opus wants to test them.

---

## 2026-06-06 — Git Commit Hygiene

**Issue:** Workspace had 580 untracked files (PDFs, screenshots, output artifacts) mixed with 26 actual tracked changes.

**Fix:** Used `git add -u` to stage only modified tracked files, committed with descriptive message. Left untracked artifacts alone.

**Lesson:** For workspace repos with heavy artifact generation, `git add -u` is the right approach — don't blindly `git add .`.
