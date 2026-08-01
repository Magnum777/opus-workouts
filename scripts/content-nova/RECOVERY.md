# Prompt Pack Recovery Procedure

**Read this first** if Prompt Pack isn't working and you need to rebuild it from scratch.

## Quick Health Check

```powershell
# 1. Are the crons still registered?
openclaw cron list | Select-String "PromptPack"

# Expected output: 3 lines (aitoolalliance, aicofounderstack, aibusinessinsider)

# 2. Is upload-post API healthy?
python scripts\check_upload_post.py

# Expected: Status: 200, "Token is valid"

# 3. Can WP REST API be reached for each site?
python scripts\check_wordpress_theme.py
python scripts\check_aib_page.py

# Expected: 200 from each site

# 4. Is the topic rotation state intact?
cat scripts\content-nova\prompt-pack-state.json
```

If any of those fail, jump to the appropriate fix below.

## Recovery Scenario A: Crons are missing

```powershell
# Recreate the 3 crons from the JSON specs
cd C:\Users\compj\.openclaw\workspace

# aitoolalliance - 5:00am ET
$msg = (Get-Content scripts\content-nova\prompt_pack_cron_aitoolalliance.json -Raw | ConvertFrom-Json).payload.message
openclaw cron add --name "PromptPack-aitoolalliance" --cron "0 5 * * *" --tz "America/New_York" `
  --model "ollama/kimi-k2.6:cloud" --session "isolated" --announce `
  --channel "discord" --to "1471281549646364805" `
  --timeout-seconds 420 --tools "exec read write" --message $msg

# aicofounderstack - 5:02am ET
$msg = (Get-Content scripts\content-nova\prompt_pack_cron_aicofounderstack.json -Raw | ConvertFrom-Json).payload.message
openclaw cron add --name "PromptPack-aicofounderstack" --cron "2 5 * * *" --tz "America/New_York" `
  --model "ollama/kimi-k2.6:cloud" --session "isolated" --announce `
  --channel "discord" --to "1471281549646364805" `
  --timeout-seconds 420 --tools "exec read write" --message $msg

# aibusinessinsider - 5:04am ET
$msg = (Get-Content scripts\content-nova\prompt_pack_cron_aibusinessinsider.json -Raw | ConvertFrom-Json).payload.message
openclaw cron add --name "PromptPack-aibusinessinsider" --cron "4 5 * * *" --tz "America/New_York" `
  --model "ollama/kimi-k2.6:cloud" --session "isolated" --announce `
  --channel "discord" --to "1471281549646364805" `
  --timeout-seconds 420 --tools "exec read write" --message $msg
```

Verify: `openclaw cron list | Select-String "PromptPack"` should show all 3.

## Recovery Scenario B: Code files are missing

The system lives in 4 directories:

1. `scripts/content-nova/prompt_pack_*.py` — generator, cross-poster, orchestrator
2. `scripts/content-nova/wxr_export.py` — 403 fallback
3. `scripts/content-nova/replay_*.py` — recovery scripts
4. `scripts/shared_text.py` — text sanitization helper

If git is intact: `git checkout HEAD -- scripts/content-nova/ scripts/shared_text.py`

If git is gone: re-author from the docstrings. Each file has a module-level docstring with usage examples that are also valid CLI invocations.

## Recovery Scenario C: Credentials are missing

The vault is at `scripts/credentials/vault.db`. Keys needed:

```python
# Required vault entries:
"wordpress", "aitoolalliance_url"     # https://aitoolalliance.com
"wordpress", "aitoolalliance_user"
"wordpress", "aitoolalliance_pass"
"wordpress", "aicofounderstack_url"   # https://aicofounderstack.com
"wordpress", "aicofounderstack_user"
"wordpress", "aicofounderstack_pass"
"wordpress", "aibusinessinsider_url"  # https://aibusinessinsider.org (currently 403'd)
"wordpress", "aibusinessinsider_user"
"wordpress", "aibusinessinsider_pass"
"upload_post", "api_key"              # Basic plan, nova.cofounder@gmail.com
```

To add a credential (use the existing `credential_vault.py` or `store_upload_post_key.py`):
```python
python scripts\store_upload_post_key.py --key "your-api-key-here"
```

To verify: `python scripts\check_upload_post.py` should return 200.

## Recovery Scenario D: State file corruption

```powershell
# Backup current state
cp scripts\content-nova\prompt-pack-state.json scripts\content-nova\prompt-pack-state.json.bak

# Reset to empty (will start topic rotation from index 0)
echo '{"sites": {}}' > scripts\content-nova\prompt-pack-state.json

# Force-run any single cron to repopulate
openclaw cron run bba21e17-c1e9-44b9-a042-afd80746443a --wait --wait-timeout 7m
```

## Recovery Scenario E: aibusinessinsider 403 queue is full

```powershell
# See what's queued
ls memory\prompt-pack-aibusinessinsider-queue\

# Dry-run replay first (safe, doesn't actually post)
python scripts\content-nova\replay_aibusinessinsider.py

# When ready to actually push
python scripts\content-nova\replay_aibusinessinsider.py --execute
```

If 403 is still active, replay will detect it and leave the queue intact. Check with `python scripts\check_aib_page.py` first.

## Recovery Scenario F: Pinterest board routing broken

The `PIN_BOARDS` dict in `prompt_pack_crossposter.py` hardcodes:
```python
"aitoolalliance.com": "1124140825679666015"      # AI Tools & Startup Gear
"aicofounderstack.com": "1124140825679666017"    # Tech for Founders
```

If upload-post profile is rebuilt or boards change:
```powershell
# Get fresh board IDs from the upload-post API
python -c "import requests, sqlite3; conn=sqlite3.connect(r'C:\Users\compj\.openclaw\workspace\scripts\credentials\vault.db'); key=conn.execute(\"SELECT value FROM credentials WHERE service='upload_post' AND key='api_key'\").fetchone()[0]; r=requests.get('https://api.upload-post.com/api/uploadposts/pinterest/boards', headers={'Authorization':f'Apikey {key}'}); import json; print(json.dumps(r.json(), indent=2))"
```

Then update `PIN_BOARDS` in `prompt_pack_crossposter.py` with the new IDs.

## Recovery Scenario G: Cron times conflict with other jobs

```powershell
# List all crons sorted by time
openclaw cron list

# Look for PromptPack times: 5:00, 5:02, 5:04 ET
# Avoid stacking with other 5am jobs (ContentNova main crons run 2am/3am/4am - safe gap)
```

If conflict, change cron expr in `openclaw cron edit <id> --cron "..."`. Recommended alternate windows: 4:30/4:32/4:34 ET, or 6:00/6:02/6:04 ET.

## Manual Force-Run (smoke test)

```powershell
# Pick one site to verify end-to-end
openclaw cron run bba21e17-c1e9-44b9-a042-afd80746443a --wait --wait-timeout 7m

# Should produce: WP post URL + X/Bluesky success + Pinterest pin URL
# Time should be ~30-60 seconds for healthy state
```

## Verifying the Pipeline After Recovery

```powershell
# 1. WP publish
curl https://aitoolalliance.com  # Site loads
# Look at recent posts - should see "Daily Prompt Pack: <topic>"

# 2. X post
# Check @AICofounderStack for the daily post
# Body should have NO URL, just bare domain "aitoolalliance.com"
# First comment should have full URL

# 3. Bluesky post
# Check @nova-cofounder.bsky.social

# 4. Pinterest pin
# Check "AI Tools & Startup Gear" board for new pin
# Image: 1000x1500 vertical PNG with site branding + 3 prompts

# 5. No forbidden characters
python scripts\content-nova\audit_unicode.py
# Should report 0 CJK, 0 emoji, low em-dash count (only in pin image, not text)
```

## When To Escalate

If the recovery procedure doesn't fix it after one cycle, the problem is likely:
1. **upload-post account issue** — login to upload-post.com, verify the `nova` profile still has X/Bluesky/Pinterest accounts linked
2. **WordPress site hosting issue** — check DNS, SSL cert, WP version, plugin conflicts
3. **OpenClaw gateway issue** — `openclaw status` and `openclaw gateway status` for system health

Don't burn time debugging at the cron layer when the underlying service is the actual issue.

## Restore from Backup

The workspace gets backed up nightly to NAS (`\\MND\video\watch\workspace-NAS-Backup`). If files are truly gone:

```powershell
# List backups
dir \\MND\video\watch\workspace-NAS-Backup | Select-Object -Last 10

# Restore the most recent
$latest = Get-ChildItem \\MND\video\watch\workspace-NAS-Backup | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item -Path "$($latest.FullName)\scripts\content-nova\prompt_pack_*.py" -Destination C:\Users\compj\.openclaw\workspace\scripts\content-nova\ -Force
Copy-Item -Path "$($latest.FullName)\scripts\shared_text.py" -Destination C:\Users\compj\.openclaw\workspace\scripts\ -Force
```

## Key Contacts

- **Owner:** Opus (James, Layered Media LLC)
- **Maintainer:** Nova (this assistant)
- **NAS:** MND hostname, SMB user `Nova`
- **Discord:** #wordpress channel `1471281549646364805`
- **Vault:** `scripts/credentials/vault.db` (NEVER commit, NEVER share the raw file)
