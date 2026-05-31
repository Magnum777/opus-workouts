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
