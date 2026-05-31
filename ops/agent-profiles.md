# Per-Agent Cron Profiles

## tradebot
- **skills:** solana-payments-wallets-trading, self-improving-agent
- **timeout:** 600
- **model:** ollama/deepseek-v4-flash:cloud
- **value-check:** portfolio > $20 (run if we have meaningful positions)
- **delivery:** discord:channel:1470957359248576699 (#tradebot)
- **failure-pattern:** timeout → bump to 900s, else escalate

## eveonion
- **skills:** upload-post, ai-social-media-content, self-improving-agent
- **timeout:** 180
- **model:** ollama/deepseek-v4-flash:cloud
- **value-check:** Twitter auth valid (skip if expired)
- **delivery:** discord:channel:1484624659633934587 (#eveonion)
- **failure-pattern:** auth error → flag manual fix, timeout → bump to 300s

## kybernauts
- **skills:** upload-post, browser-use, self-improving-agent
- **timeout:** 600
- **model:** ollama/kimi-k2.6:cloud
- **value-check:** Discord connected (always true)
- **delivery:** discord:channel:1479156871641436265 (#kybernauts)
- **failure-pattern:** browser error → kill chrome + retry once, else escalate

## wordpress (ContentNova)
- **skills:** wordpress-pro, self-improving-agent
- **timeout:** 300
- **model:** ollama/kimi-k2.6:cloud
- **value-check:** WordPress sites reachable
- **delivery:** discord:channel:1471281549646364805 (#wordpress)
- **failure-pattern:** timeout → bump to 600s, auth error → flag manual fix

## nova-chat (main)
- **skills:** self-improving-agent, memory-hygiene, reflection
- **timeout:** 180-600 depending on task
- **model:** varies by task
- **value-check:** —
- **delivery:** discord:channel:1470836415523983630 (#nova)
- **failure-pattern:** log all to `.learnings/ERRORS.md`
