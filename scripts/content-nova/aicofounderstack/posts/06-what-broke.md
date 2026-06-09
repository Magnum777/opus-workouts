# What Broke This Week: Real Failures from an AI Operation

**Author:** James "Opus" Henderson  
**Date:** June 2026  
**Tags:** AI, Failures, Debugging, Operations, OpenClaw

---

## Nobody Talks About the Breakages

Every AI automation blog shows the wins. Nobody shows the 3 AM failures, the rate limit meltdowns, the model hallucinations that cost money. Here's what actually broke in my operation this week — and how I fixed it.

---

## Failure 1: Jupiter API Rate-Limited the Trading Bot

**What happened:** The TradeBot hit Jupiter's quote API 47 times in 10 minutes. Jupiter returned 429 errors. The bot couldn't price tokens. Three buy signals sat unexecuted.

**Root cause:** No rate limit logic. The scout and executor both called Jupiter independently. When market volatility spiked, both fired repeatedly.

**Fix:** Added exponential backoff. First retry waits 2s, second waits 4s, third waits 8s. Also added a shared rate limiter — max 5 Jupiter calls per minute across all bot functions.

**Cost of failure:** 3 missed trades. Estimated opportunity cost: ~$12.

**Lesson:** APIs have limits. Even "free" tiers. Always assume you'll hit them during volatility.

---

## Failure 2: Cron Job Timeouts Killed the Spam Sweep

**What happened:** The Gmail spam cleanup cron was timing out after 30 seconds. Spam accumulated for 3 days. ~200 sexual spam/phishing emails hit the inbox.

**Root cause:** The script used `gog gmail thread list` which paginates slowly. 30 seconds wasn't enough for 800+ threads.

**Fix:** Bumped timeout to 600 seconds. Added date filtering — only check last 7 days instead of all time. Script now completes in ~90 seconds.

**Cost of failure:** 10 minutes of manual cleanup. Minor annoyance.

**Lesson:** Timeout defaults are aggressive. For I/O-heavy tasks (email, web scraping), give yourself 5-10x headroom.

---

## Failure 3: Model Hallucination Wrote a Fake Affiliate Link

**What happened:** The Content Nova pipeline generated an article mentioning "Jasper AI's new 50% discount code JASPER50." The code doesn't exist. Jasper has no public discount program.

**Root cause:** Kimi K2.5 hallucinated a plausible-sounding promo to make the article more engaging. No fact-checking step caught it.

**Fix:** Added a verification layer. Any article mentioning discounts, pricing, or specific claims gets a web search pass. If the claim can't be verified in 30 seconds, it's stripped or flagged for manual review.

**Cost of failure:** Had to edit the post before publishing. 5 minutes of manual work. If it had gone live, potential affiliate relationship damage.

**Lesson:** LLMs are creative writers, not fact-checkers. Never trust a specific claim without verification.

---

## Failure 4: Browser Automation Scope Got Stuck

**What happened:** The Kybernauts forum bump cron couldn't approve its own browser scope upgrade. The CLI device needed `operator.admin` to approve the scope request, but it only had `operator.read`. Deadlock.

**Root cause:** Scope upgrades require an already-authorized device. The CLI device couldn't approve itself.

**Fix:** Manually edited `devices/paired.json` and `identity/device-auth.json` to grant full scopes. Proper long-term fix: set a gateway password and use shared-secret auth for approvals.

**Cost of failure:** 2 hours of debugging. Forum bump was manual for 1 week.

**Lesson:** Authentication chicken-and-egg problems are real. Have a fallback admin path that doesn't depend on the device being upgraded.

---

## Failure 5: Portfolio DB Corruption Showed Fake $174K Gains

**What happened:** The trading bot's portfolio database somehow accumulated 3 corrupted closed positions with tiny amounts but massive realized PnL. The analytics showed a 100% win rate and $174K in gains. On a $93 portfolio.

**Root cause:** Micro-trades (dust amounts from failed transactions) were being logged as full position closures without proper cost basis tracking. `amount_raw` vs `amount_token` mismatch.

**Fix:** Purged the corrupted entries. Fixed the cost basis calculation in the executor. Added validation: any trade with `realized_pnl > portfolio_value * 2` gets flagged as suspicious.

**Cost of failure:** Believed the numbers for ~6 hours before noticing the decimal mismatch. Could have led to bad strategy decisions.

**Lesson:** Data validation is non-negotiable. If a number looks too good, it's probably wrong.

---

## The Pattern

Every failure follows the same arc:
1. **Everything works in testing**
2. **Scale or edge case exposes the flaw**
3. **Quick fix applied**
4. **Deeper fix needed later**

None of these were catastrophic because each system has a human checkpoint (me) before anything irreversible happens. The bot can trade, but I approve the strategy changes. The bot can publish, but I review before it goes live.

**Automation without oversight is gambling. Automation with oversight is leverage.**

---

## What's Being Fixed Next

1. **Circuit breakers** — If 3 failures happen in 10 minutes, pause the system and alert me
2. **Health check dashboard** — Real-time status of all crons, API quotas, and error rates
3. **Rollback system** — One-click revert for bad model outputs, broken configs, or failed trades

**Want the failure tracking system?** I'll include it in the Nova Operations blueprint — error logging, alerting thresholds, and recovery playbooks.

---

*This is not a complaint post. This is an honest log of what running AI automation actually looks like. For every success I tweet about, there's a failure I debug at 2 AM. Both are part of the job.*
