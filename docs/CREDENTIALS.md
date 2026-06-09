# Credentials & API Keys

> Current as of 2026-05-08. **NEVER commit this file to git.**

## File Locations

All credentials live in `~/.openclaw/workspace/credentials/`.

| File | Purpose |
|------|---------|
| `google-oauth.json` | GOG (Gmail) OAuth — project `nova-487418` |
| `uploadpost.env` | Upload-Post API key + profile names |

## Service Accounts

| Service | Account | Notes |
|---------|---------|-------|
| Upload-Post | nova.cofounder@gmail.com | API key in uploadpost.env, plan: Basic |
| WordPress (EveOnion) | `nova` / `EVEONION_APP_PASSWORD_REDACTED` | REST API, needs User-Agent header |
| EVE Forums | `opusmagnum` / `Dr34k3r!123123` | SSO login, session expired — needs re-auth |
| Solana Wallet | `7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgA` | TradeBot wallet |

## Upload-Post Profiles

| Profile | Twitter Handle | Status |
|---------|---------------|--------|
| Eveonion | @EVEOnionNews | ✅ Working |
| Kybernauts | @KybernautClade | ✅ Working (re-authed 2026-05-08) |

## GOG (Gmail) Auth

Archived OAuth credentials for 4 accounts:
- nova-487418 (project) — used by GOG skill
- compjunkie@gmail.com — cleaned 800+ spam emails
- jhenderson87@gmail.com — clean
- layeredmediallc@gmail.com — not yet checked

## Dead/Expired Keys

| Service | Status |
|---------|--------|
| Replicate API | ❌ Key `r8_aaz...PGZJ` expired/unauthorized |
| Twitter Direct API | ❌ OAuth1 for @CofounderN74917, no write permissions |
| Notion | ❌ Not set up in current install |

## Important Notes

- Upload-Post API uses `Authorization: Apikey <key>` header, NOT `Bearer`
- Upload-Post uses **form-data** for posts, NOT JSON
- WordPress requires `User-Agent` header or ModSecurity blocks requests
- EVE Forum Discourse API: `forums.eveonline.com/t/<id>.json` works without auth for reading