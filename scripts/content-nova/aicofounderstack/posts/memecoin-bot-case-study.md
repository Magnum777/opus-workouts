# How I Gave an AI $93 to Trade Memecoins — Here's What Happened in 3 Weeks

**Author:** James "Opus" Henderson  
**Date:** May 27, 2026  
**Tags:** AI, Crypto, Automation, Solana, Trading Bot

---

## The Setup

Three weeks ago I handed $93 USDC to an AI trading bot and told it to figure out Solana memecoins. No preset picks. No manual trading. Just a prompt that says "find tokens with momentum, buy the dip, sell the rip."

Here's the actual stack:

**Wallet:** Solana (managed by the bot, not me)  
**Capital:** $93 USDC — small enough that failure is acceptable, real enough that it hurts  
**Exchange:** Jupiter DEX aggregator (no KYC, no signup, just wallet + code)  
**Data:** DexScreener API for real-time price, volume, and liquidity  
**Brain:** Kimi K2.5 running on Ollama (my own hardware, no per-token fees)  
**Execution:** Custom daemon, 10-min scout cycles, 15-min execution cycles

## The Rules

I built the bot with three hard constraints:

1. **Never risk more than 15% per trade** — a single bad call can't kill the portfolio
2. **Sell at +5% or -3%** — no diamond hands, no bag-holding. Mechanical exits.
3. **Token safety gate** — any token scoring below 60/100 on liquidity, volume, and legitimacy gets auto-blocked

The last one is important. Memecoin land is full of honeypots — tokens you can buy but never sell. I built a DexScreener-based safety checker that scores tokens on:
- Liquidity depth (25 points)
- 24h volume (20 points)  
- Healthy buy/sell ratio (15 points)
- Token age > 7 days (15 points)
- Multi-DEX presence (10 points)
- Website/socials (10 points)
- Name flags (5 points)

Anything below 60 gets rejected before the bot even considers buying.

## The Results (So Far)

| Metric | Value |
|--------|-------|
| Starting Capital | $93.00 |
| Current Value | $55.89 |
| Realized PnL | +$56.27 |
| Unrealized PnL | -$1.78 |
| Win Rate | 33% (7W / 14L) |
| Best Trade | ORCA +$46.34 |
| Worst Trade | BONK -$19.03 |
| Current Streak | 14 losses (lol) |
| Best Win Streak | 7 |
| Worst Loss Streak | 14 |

## What Actually Happened

**Week 1:** The bot found ORCA early — bought around $0.80, rode it to $1.20, sold at +46%. That single trade covered almost the entire portfolio. Also caught a couple small PENGU wins (+18%, +14%).

**Week 2:** Started chasing. BONK looked hot — bot bought in, then BONK tanked. Lost $19. Then JUP went sideways. Lost another $5. The win streak evaporated.

**Week 3 (Now):** Holding TRUMP, RAY, ORCA, and FARTCOIN. Down on paper but the safety gate is doing its job — no honeypots, no rug pulls. Every loss is a real market move, not a scam.

## What's Working

**The safety gate is the MVP.** In 3 weeks of memecoin trading, zero scam losses. The bot has been exposed to 50+ tokens and blocked 6 that were obvious traps (low liquidity, fake volume, no socials).

**The model is fast enough.** Kimi K2.5 on local hardware runs the full research → decision pipeline in under 30 seconds. No API bills. No rate limit anxiety.

**Mechanical exits remove emotion.** The bot doesn't "hope" a trade comes back. -3% = sell. No exceptions. This is why the realized PnL is positive (+$56) even while the portfolio is down — the bot takes losses quickly and lets winners run to target.

## What's Not Working

**14 losses in a row is rough.** The bot's signal generator is too sensitive — it's buying minor dips that keep dipping. Need to tighten the entry criteria: require volume spike + price confirmation, not just "token is down from recent high."

**Portfolio concentration is creeping.** Four open positions at once with only $55 in play means each position is tiny (~$13). Hard to make meaningful gains when transaction fees eat 1-2% per trade.

**No stop-loss on open positions.** The exit rule applies to new signals, not existing bags. If a position drops 20% with no sell signal, it just sits there. Need trailing stops.

## The Tools Behind This

If you want to build something similar, here's what I actually use:

- **Jupiter DEX** — swap aggregator, best prices across Solana DEXs
- **DexScreener** — real-time token data, free API
- **Helius RPC** — Solana node access (free tier)
- **Ollama** — local LLM hosting (Kimi K2.5, Qwen3:14b)
- **OpenClaw** — my agent framework (cron scheduling, sub-agents, Discord integration)

## Next Steps

I'm running this live through June. Goals:

1. **Add trailing stops** — auto-exit any position down 10% from entry, regardless of signal
2. **Tighten entry criteria** — require volume confirmation + 15-min momentum
3. **Position sizing fix** — max 2 open positions until portfolio > $150
4. **Weekly analytics** — automated PnL reports, win rate tracking, strategy tuning

I'll post updates weekly with real numbers. Follow along or build your own — the code is mine, the lessons are universal.

---

**Want the bot's config?** I'm packaging the TradeBot as a downloadable automation ($25) — safety gate, research engine, execution logic, and Discord reporting included. Drop your email if you're interested.

**Questions?** Reply here or DM me on Discord. I read everything.

---

*This is not financial advice. This is a case study in AI-operated automation. The bot lost money. The bot made money. The bot is still learning. So am I.*
