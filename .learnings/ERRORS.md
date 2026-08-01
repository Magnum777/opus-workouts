# Errors

Command failures and integration errors.

---

## 2026-06-01 - Weekly cron timeouts (x3)
**Category:** integration
**Crons:** Iris-all-accounts-digest, Weekly-MemoryHygiene, Weekly-SkillUpdate

All three timed out by ~1s past their limit:
- Iris: 241s run / 240s limit → bumped to 300s
- MemoryHygiene: 121s run / 120s limit → bumped to 180s
- SkillUpdate: 121s run / 120s limit → bumped to 180s

Observation: These are the tightest-tolerance crons. All three are weekly or daily with multi-step payloads. The timeout bump should resolve — none had other errors (no runtime failures, no delivery issues).

## 2026-06-02 — Iris-all-accounts-digest 2nd timeout (300.6s / 300s limit)
**Category:** integration

Iris timed out again despite the 240→300s bump. The 2nd run took 300.6s vs the 300s limit — still ~0.2s over. Root cause: sequential IMAP connections across 4 Gmail accounts are slower than anticipated, with per-account scan times varying based on inbox size and connection quality.

**Fix:** Bumped timeout to 360s (+60s), enabled failure alerts (notify #nova after 1 consecutive error).

**Escalation path:** If it times out at 360s, the Iris script itself is hanging on a specific account — needs per-account timeout logic or account-specific debugging.
[kybernauts] Propaganda failed: Twitter/X auth not configured (no UPLOAD_POST_API_KEY or UPLOADPOST_API_KEY env var)

## 2026-07-26 — Kybernauts-Propaganda cron: image_generate billing failure
- **What:** OpenAI gpt-image-2 returned Billing hard limit has been reached (HTTP 400, type=billing_limit_user_error).
- **Impact:** Couldn't generate fresh poster. Fell back to existing propaganda_20260613_181521.png asset + fresh tagline in caption.
- **Mitigation:** Posted successfully, but visual freshness lost.
- **Fix needed:** Opus to top up OpenAI billing OR configure alternative provider (gemini, minimax, etc) for image_generate.
- **Also:** OpenRouter has no API key configured for this agent (openclaw agents add <id> to add).

## 2026-07-26 — Upload-Post API: 	itle with em-dash works only via --form-string
- **What:** Using -F "title=..." failed with Invalid API key format when title contained an em-dash (—). Decoded via --form-string worked.
- **Actually:** The 400 was likely a curl form-parsing issue with -F stripping/quoting the multibyte character. Real key was valid (verified via /uploadposts/me).
- **Fix:** Use --form-string "title=..." for caption text in upload-post calls.

## 2026-07-26 — image_generate alternative providers not configured
- The only provider with auth in this agent is openai. openrouter, google, minimax, al, xai, litellm, comfy, microsoft-foundry, ydra all show "not configured".
- If OpenAI billing hits a wall, image_generate is dead until another provider gets auth.


## 2026-07-28 - Yagas propaganda cron: Pochven tagging broken + API key still missing
- What: yagas_propaganda_post.py generated a post claiming 60.16B destroyed by blob fleets this week in Pochven, but the analysis shows pochven_kills: 0, pochven_percentage: 0.0, recent_pochven_kills: empty list. The 60.16B is total recent kill ISK across all systems, not Pochven-specific. Posting as-is would falsely claim Pochven-specific data.
- Root cause: Two issues stacked. (1) yagas_intel_collect.py analyzes 200 recent kills but caps ESI lookups at 50 (max_esi_calls=50); if none of the first 50 are Pochven, pochven_kills is empty. (2) UPLOADPOST_API_KEY env var is still not set, so even if the post text were correct, the script would fail at the post_to_social step.
- Why no post: Cron rules say posts MUST be evidence-based. With zero confirmed Pochven kills in the snapshot, claiming 60.16B in Pochven this week is exactly the kind of unverified claim we should NOT publish. Also: external action check (AGENTS.md asks first for tweets/posts).
- What I did: Held the post. Surfaced data and options to Opus. Wrote a corrected, evidence-anchored post draft using only zKillboard-aggregated Pochven system data (90,207 all-time Pochven kills, 27.8T ISK) for Opus to approve before any actual publish.
- Fix needed: (1) Opus to set UPLOADPOST_API_KEY in agent env. (2) yagas_intel_collect.py: raise max_esi_calls to >=200 OR sample Pochven systems more aggressively, OR add a fallback that uses zKillboard topAllTime[system] Pochven data when individual kill lookups fail. (3) Propaganda script: detect pochven_kills==0 and either regenerate fresh intel OR use a different template set.


## 2026-07-29 — yagas_propaganda_post.py: wrong upload-post API format

**Symptom:** Script prints 'Username required in form data' from upload-post API. Result: {'success': False, 'message': 'Username required in form data'} after a successful auth check.

**Root cause:** Script sends JSON body with platform: [x, bluesky] (no [] suffix, no form encoding). Working scripts in scripts/eveonion/tweet_latest.py and scripts/eveonion/post_test_tweet.py use form-encoded data={'user': PROFILE, 'platform[]': ['x', 'bluesky'], 'title': tweet} with equests.post(url, data=data, ...) not json=data.

**Secondary issue:** Script reads UPLOADPOST_API_KEY from os.environ only, but the credential is stored at credentials/uploadpost.env. Sibling scripts read the file directly. Without the env var set, the script silently fails the API call and only logs 'API key missing'.

**Fix for next pass:** Either (a) load credentials/uploadpost.env like the eveonion scripts do, AND (b) switch to form-encoded platform[] array. Both must be done for the script to work unattended.

