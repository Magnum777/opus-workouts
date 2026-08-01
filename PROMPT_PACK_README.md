# Prompt Pack Daily — System Documentation

**Last updated:** 2026-07-31
**Owner:** Nova (Opus's assistant)
**Status:** Active, daily 5am ET staggered across 3 sites

## What This Is

Three crons, staggered 2 minutes apart, that publish a daily "prompt pack" to each ContentNova WordPress site. Each pack is a topic-aligned set of 3 highly refined AI prompts (tool-tagged, copy-pasteable, with a tangible deliverable in each). After WP publish, the post is cross-posted to X / Bluesky / Pinterest under the `nova` upload-post profile.

## Why It Exists

Reader value: bite-sized AI prompts they can actually use, not "Top 10 AI tools" listicles. SEO value: daily fresh content + keyword targeting on tool topics. Channel value: three social profiles feeding from one source of truth.

## Architecture

```
5:00am ET  → PromptPack-aitoolalliance    → aitoolalliance.com
5:02am ET  → PromptPack-aicofounderstack  → aicofounderstack.com
5:04am ET  → PromptPack-aibusinessinsider → aibusinessinsider.org (Cloudflare 403'd)
```

Each cron is an isolated `agentTurn` that:
1. Picks a topic via `prompt_pack_gen.pick_topic(site)` — 30-day no-repeat
2. Writes 3 prompts + intro/footer/title/excerpt as JSON
3. Humanizes the wrapper copy (model-based humanizer skill)
4. Calls `prompt_pack_orchestrator.py` with the JSON
5. Orchestrator publishes to WP, then calls `prompt_pack_crossposter.py`
6. Cross-poster hits upload-post API for X / Bluesky / Pinterest
7. Failures save to `memory/prompt-pack-social-drafts/` and surface in #wordpress

## File Map

| File | Purpose |
|---|---|
| `scripts/content-nova/prompt_pack_gen.py` | Topic rotation, 30-day no-repeat state |
| `scripts/content-nova/prompt_pack_crossposter.py` | X + Bluesky text + Pinterest image pin |
| `scripts/content-nova/prompt_pack_orchestrator.py` | WP publish + cross-post glue, 403 fallback |
| `scripts/content-nova/wxr_export.py` | WXR file writer for 403-fallback queue |
| `scripts/content-nova/replay_pinterest.py` | Replays failed Pinterest pins from drafts |
| `scripts/content-nova/replay_aibusinessinsider.py` | Drains WXR queue when aibusinessinsider 403 clears |
| `scripts/content-nova/prompt_pack_cron_*.json` | Cron specs (archived, live crons via `openclaw cron list`) |
| `scripts/shared_text.py` | `clean_for_posting()` — strips em-dash / CJK / emoji from all cron output |
| `scripts/content-nova/audit_unicode.py` | One-shot diagnostic for non-ASCII chars in live posts |
| `scripts/content-nova/diag_*.py` | One-shot upload-post API diagnostics |
| `scripts/content-nova/prompt-pack-state.json` | Per-site topic rotation state (committed) |
| `memory/prompt-pack-social-drafts/` | Fail-soft queue for failed cross-posts (gitignored runtime data) |
| `memory/prompt-pack-aibusinessinsider-queue/` | WXR fallback queue for 403'd posts (gitignored runtime data) |

## Cron Job IDs

```
PromptPack-aitoolalliance    bba21e17-c1e9-44b9-a042-afd80746443a
PromptPack-aicofounderstack  cba7f8b0-3e97-47f5-b63f-c404e74d1f1e
PromptPack-aibusinessinsider 0399339a-3dbd-41ae-a0a2-2092adf7121a
```

## Critical Rules (enforced by code, not just convention)

| Rule | Where enforced |
|---|---|
| **No em-dashes** in any cron output | `clean_for_posting()` in `shared_text.py` |
| **No curly quotes** | `clean_for_posting()` |
| **No emoji** | `clean_for_posting()` (Unicode ranges U+1F300-1FAFF etc.) |
| **No CJK** characters | `clean_for_posting()` (U+4E00-9FFF range) |
| **No Unicode ellipsis** | `clean_for_posting()` (replaces with `...`) |
| **Prompts stay verbatim** in their WORDS | Only chars get cleaned, not the prompt text itself |
| **No URL in X body** | `_build_x_text()` strips scheme+path, leaves bare domain |
| **X URL in first_comment** | `upload-post first_comment` field |
| **Pinterest title ≤100 chars** | `_build_pin_title()` enforces cap |
| **30-day topic no-repeat per site** | `prompt-pack-state.json` |
| **aibusinessinsider 403 → WXR queue** | `prompt_pack_orchestrator.py` 403-fallback branch |

## API Quirks Learned (the hard way)

These are non-obvious and cost time to discover. Documented so future-you doesn't re-discover them:

1. **upload-post `/upload_text` rejects JSON body** with `"Username required in form data"`. Must use form-encoded `data=` with `platform[]` array. (See `diag_upload_post.py` test 5.)
2. **upload-post `/upload_photos` Pinterest field is `pinterest_board_id`**, not `board_id`. (See `diag_pinterest.py` test B.)
3. **Pinterest title hard-cap is 100 chars**. Use `title` + `description` (separate fields, ~500 char desc cap). (See `diag_pinterest.py` round 2.)
4. **upload-post API exposes no profile-endpoint** to query handle mappings. Profile names + boards must be known out-of-band or queried from upload-post dashboard.
5. **Pinterest boards endpoint** (`/uploadposts/pinterest/boards`) returns `pinterest_account_used` field but does NOT list connected X/Bluesky accounts.
6. **aibusinessinsider.org sits behind Cloudflare bot-challenge** since at least 2026-07-20. Public site works, WP REST API 403s. WXR queue is the workaround.

## Known Sites

| Site | WP Status | Social | Notes |
|---|---|---|---|
| aitoolalliance.com | ✅ live | ✅ X / Bluesky / Pinterest | Production site, full pipeline |
| aicofounderstack.com | ✅ live | ✅ X / Bluesky / Pinterest | Production site, full pipeline |
| aibusinessinsider.org | ⚠️ Cloudflare 403 | Queued for replay | WXR queue at `memory/prompt-pack-aibusinessinsider-queue/` |

## Fail-soft Surfaces

Any cron failure path lands somewhere recoverable:

- **WP publish 403** → WXR queue, replayable
- **WP publish other error** → reported to #wordpress, agent turn fails soft
- **upload-post timeout** → draft saved to `memory/prompt-pack-social-drafts/`
- **upload-post 4xx** → draft saved + body logged
- **Prompt gen agent turn timeout (480s)** → cron failure alert to #wordpress
- **Cross-post fail after WP success** → post is live, social queue waits

## Recovery Procedure

See [`scripts/content-nova/RECOVERY.md`](./scripts/content-nova/RECOVERY.md) for the full step-by-step rebuild procedure.

## How to Test It

```powershell
# Smoke test the orchestrator with sample content
python scripts\content-nova\prompt_pack_orchestrator.py --site aitoolalliance.com --dry-run --content-json '{"title":"Test","excerpt":"test","intro_html":"<p>test</p>","prompts":[{"tag":"[Claude]","body":"test 1"},{"tag":"[ChatGPT]","body":"test 2"},{"tag":"[Cursor]","body":"test 3"}],"footer_html":""}'

# Force-run one cron (will publish live + cross-post)
openclaw cron run bba21e17-c1e9-44b9-a042-afd80746443a --wait --wait-timeout 7m

# Replay queued Pinterest pins
python scripts\content-nova\replay_pinterest.py

# Replay queued aibusinessinsider WXR files
python scripts\content-nova\replay_aibusinessinsider.py
```

## Owner Notes

- Built 2026-07-31 by Nova in #wordpress with Opus
- Replaces ad-hoc ContentNova crons which only published WP, no social
- aibusinessinsider.org 403 is pre-existing, not caused by this build
- Future extensions: thread scheduling (best-time posting per platform), Pinterest board expansion, cross-site series (3-day rollups)
