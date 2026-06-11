# NAS Cron Setup — Kybernauts Assets Viewer

## What This Does
Runs **4 times per day** (every 6 hours) on the Synology NAS to:
1. Refresh ESI tokens for 3 Director alts
2. Pull corp assets + wallet divisions
3. Resolve type names, locations, market prices
4. Encrypt + push to GitHub Pages

## Files on NAS
Place these in a folder (e.g., `/volume1/kybernauts-sync/`):
- `esi-sync.js` — main sync script
- `esi-auth.js` — for initial token capture (run once per director)
- `.env` — credentials
- `tokens.json` — refresh tokens (auto-updated)
- `.cache/` — type/location/market caches (auto-created)

## Prerequisites

### 1. Install Node.js on Synology
```bash
# Via Package Center, or:
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 2. Create `.env`
```bash
cd /volume1/kybernauts-sync
nano .env
```

Contents:
```
ESI_CLIENT_ID=16e0d5faa2984b3aac5c6eaed7a077fc
GITHUB_TOKEN=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
ENCRYPT_PASSPHRASE=u^w%dEUq!$_&E5l++oGjXT%5UYqlSWZEiASjtTdd_Cbn&ob5w6e9Y8v
REPO=Magnum777/kybernauts-assets
```

### 3. Copy scripts from GitHub
```bash
cd /volume1/kybernauts-sync
curl -O https://raw.githubusercontent.com/Magnum777/kybernauts-assets/main/scripts/esi-sync.js
curl -O https://raw.githubusercontent.com/Magnum777/kybernauts-assets/main/scripts/esi-auth.js
```

### 4. Get initial tokens (run once per director)
Run on a machine with a browser:
```bash
node esi-auth.js
```
Log in with each Director alt. Tokens save to `tokens.json`.

Copy the resulting `tokens.json` to the NAS.

## Synology Task Scheduler

1. **Open DSM** → Control Panel → Task Scheduler
2. **Create** → Scheduled Task → User-defined script
3. **General** tab:
   - Task: `KybernautsAssetsSync`
   - User: `root`
   - Enabled: ✅
4. **Schedule** tab:
   - Run every: `6 hours` (00:00, 06:00, 12:00, 18:00)
   - First run time: `00:00`
5. **Task Settings** tab:
   - Send run details by email: (optional)
   - User-defined script:
```bash
cd /volume1/kybernauts-sync
/usr/local/bin/node esi-sync.js >> sync.log 2>&1
```
6. Click **OK**

## Test Run
```bash
cd /volume1/kybernauts-sync
/usr/local/bin/node esi-sync.js
```

Should output:
```
=== Kybernauts ESI Sync (Full Resolution) ===
...
✅ Pushed to GitHub
=== Sync Complete ===
Locations: NNN
Systems: N
Total ISK: NNN,NNN,NNN
Total Items: NNN
```

## Manual Refresh
If you need to force a refresh outside the schedule:
```bash
ssh admin@192.168.68.51
cd /volume1/kybernauts-sync
node esi-sync.js
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Rate limit 420 | Wait 60s, retry. Script auto-delays 500ms. |
| Bad credentials | Regenerate GitHub token at github.com/settings/tokens |
| Token expired | Run `esi-auth.js` again to refresh |
| 0 assets | Check corp IDs in `tokens.json`. Directors must be in corp. |

## Live Site
- **URL:** https://magnum777.github.io/kybernauts-assets/
- **Passphrase:** `u^w%dEUq!$_&E5l++oGjXT%5UYqlSWZEiASjtTdd_Cbn&ob5w6e9Y8v`
- **Updates:** 4x/day via NAS cron

## Source Code
https://github.com/Magnum777/kybernauts-assets
