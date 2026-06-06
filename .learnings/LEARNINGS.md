# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## 2026-05-31 — Skill Registry Bulk Registration
**Category:** best_practice
**Pattern-Key:** clawhub-install-existing-skills

When skills exist from a restored workspace but aren't in `.clawhub/lock.json`, `clawhub install <slug>` fails with "Already installed". Use `--force` to overwrite and register them properly in the lockfile. Without this, they won't auto-update via `clawhub update`.

Batch via `;` semicolons in PowerShell works but spawns multiple processes. One-by-one is cleaner for verifying each install.

Source: simplify-and-harden

---

## 2026-06-01 - Nova Ops Assessment: Timeout Bumping
**Category:** best_practice
**Pattern-Key:** cron-timeout-prevention

Three weekly crons (Iris-all-accounts-digest, Weekly-MemoryHygiene, Weekly-SkillUpdate) hit their timeout limits by ~1 second each. Root cause: default timeouts of 120-240s are tight for multi-step jobs.

Action: Bumped Iris from 240s→300s (4 Gmail accounts), MemoryHygiene 120s→180s, SkillUpdate 120s→180s.

Lesson: When setting timeouts for agent-style crons, add 50% headroom above the expected duration. IRIS checking 4 accounts sequentially will always run longer than sweeter single-account sweeps.

Source: nova-ops-assessment

---

## 2026-06-05 — Weekly Skill Discovery Scan
**Category:** insight
**Pattern-Key:** clawhub-weekly-discovery-2026w23

Ran weekly Friday skill discovery scan across 8 queries. Summary of findings:

### Already Have (pass):
- **solana-payments-wallets-trading** ✓ — already installed v0.3.4
- **ai-social-media-content** ✓ — already installed v0.1.5
- **upload-post** ✓ — already installed v1.0.0
- **browser-use** ✓ — already installed v2.0.1
- **agent-browser-clawdbot** ✓ — already installed v0.1.0
- **duckdb-cli-ai-skills** ✓ — already installed v1.0.0
- **wordpress-pro** ✓ — already installed v0.1.0
- **iris** ✓ — already installed v1.0.4
- **composio** ✓ — already installed v1.0.0

### Notable Finds Not Installed:
1. **agent-browser-assistant** v1.0.0 — Browser automation with web data scraping, form filling, screenshots, UI testing. Lower rating (0.644) than what we have. Similar to existing agent-browser-clawdbot + browser-use. Skip.
2. **browser-auto-plus** v2.0.0 — Enhanced browser automation with error recovery, retry logic, multi-browser support, screenshot verification. New (June 5). Worth watching but recently published, unrated.
3. **agentmail-integration** v1.1.0 — AgentMail API integration for email automation. We already have agentmail skill registered via the skill system. Redundant.
4. **wordpress-publishing-skill-for-claude** v0.1.0 — WordPress publishing via REST API with Gutenberg blocks. Already have wordpress-pro which is more comprehensive. Skip.
5. **data-analysis-reporting** v0.1.0 — CSV/SQLite/spreadsheet → analytical reports. Redundant with duckdb-cli-ai-skills + excel-xlsx. Skip.
6. **openclaw-agent-browser** v1.0.0 — Headless browser automation CLI. Similar to agent-browser-clawdbot. Skip.
7. **lazarus** v1.0.5 — Recover dead websites via Wayback Machine, deploy with AutoCode. Interesting niche tool not related to current workflows.
8. **knowledge-mapper** v1.0.2 — Parse MD/TXT documents → knowledge graphs. Interesting but not aligned with current needs.
9. **social-media-content** v1.0.0 — Brand-specific social posts (LevelUpLove/PayLessTax). More niche than ai-social-media-content. Skip.

### Flag for Opus:
- **browser-auto-plus** v2.0.0 — Released today (June 5, 2026). Features error recovery, retry logic, multi-browser support. Could be better than our current browser setup. Needs evaluation.
- **lazarus** v1.0.5 — Site recovery via Wayback Machine + AutoCode deploy. Novel concept but not immediately useful.

### No Results (search returned empty/irrelevant):
- "social media content creator" — empty results
- "ai agent workflow" — empty results
- "discord bot automation" — only returned low-relevance result

### Tools that we have that cover these bases well:
- Solana: solana-payments-wallets-trading
- Browser: browser-use + agent-browser-clawdbot
- Social: ai-social-media-content + upload-post
- WordPress: wordpress-pro
- Email: iris + agentmail
- Data: duckdb-cli-ai-skills + excel-xlsx + pdf-pro
- Learning: self-improving-agent + reflection + memory-hygiene
- General: composio (500+ app integrations)

No high-priority new installations recommended. Current skill suite is well-covered.

---

## 2026-06-02 — Iris-all-accounts-digest 2nd consecutive timeout — expanded to 360s + failure alerts
**Category:** best_practice
**Pattern-Key:** cron-iris-high-traffic

Iris-all-accounts-digest timed out for the 2nd consecutive run. First fix (240→300s, June 1) was insufficient — the 3rd run hit 300.6s with a 300s limit.

Action: Bumped timeout 300→360s. Also enabled failure alerts (alert #nova after 1 consecutive failure) so Opus is notified immediately if it fails again.

Lesson: Multi-account email triage via IMAP is inherently slow. Each account requires a full IMAP connection, auth, and mailbox scan. 4 accounts × ~75s each = ~300s minimum. Setting 50% overhead is insufficient when a single slow IMAP session can take >90s. At 360s, this gives ~90s per account which should handle sporadic IMAP slowness. If it still fails, the root cause is the Iris script hanging on a specific Gmail account.
