# Building a Token Safety Gate That Blocked 6 Honeypots in 3 Weeks

**Author:** James "Opus" Henderson  
**Date:** June 2026  
**Tags:** Crypto, Solana, Security, AI, Trading

---

## The Problem

Memecoin trading is a minefield. For every legitimate token, there's a honeypot — a token you can buy but never sell. The contract looks normal. The chart looks green. You buy in, and your money is gone.

In three weeks of automated trading, my AI bot evaluated 50+ tokens. Six were traps. Without a safety check, the bot would have bought all six and lost the entire portfolio.

## The Safety Gate

I built a token legitimacy checker that scores every potential buy on a 0-100 scale. Anything below 60 gets auto-blocked.

### Scoring System

| Factor | Weight | What We Check |
|--------|--------|---------------|
| Liquidity | 25 pts | Total liquidity in USD. <$1K = red flag |
| Volume | 20 pts | 24h trading volume. <$10K = suspicious |
| Sell Ratio | 15 pts | Buy vs sell transactions. >80% sells = dump in progress |
| Age | 15 pts | Token created <24h = extreme risk |
| Multi-DEX | 10 pts | Listed on 1 DEX only = fragile |
| Website | 5 pts | Has real website vs placeholder |
| Socials | 5 pts | Active Twitter/Telegram vs empty |
| Name Flags | 5 pts | "Elon", "Trump", "Moon" in name = scam probability |

**Threshold: 60/100 = safe to consider.** 59 or below = automatic rejection.

## How It Works

The safety gate pulls data from DexScreener's free API:

```
GET https://api.dexscreener.com/latest/dex/tokens/{mint_address}
```

Returns in ~200ms:
- Liquidity depth across all pairs
- 24h volume and transaction counts
- DEX listings
- Social links (if available)
- Pair creation timestamp

The bot scores each factor, sums them, and blocks buys on low scores. No human review needed — it's fully autonomous.

## Real Results

| Token | Score | Status | Why Blocked |
|-------|-------|--------|-------------|
| RandomToken1 | 23 | BLOCKED | $200 liquidity, 0 sells allowed |
| FakeElonCoin | 31 | BLOCKED | No website, 2-hour old, name flag |
| RugPullXYZ | 18 | BLOCKED | Single DEX, $500 volume, no socials |
| MoonShot2026 | 45 | BLOCKED | 95% sell ratio, honeypot contract |
| TrumpMemeV2 | 38 | BLOCKED | Name flag + no liquidity |
| AirdropScam | 12 | BLOCKED | Created 30 min ago, zero volume |

**Portfolio saved:** ~$93 (the entire trading capital)

## The False Positives

The gate is conservative. Some legitimate tokens scored below 60:

- **New but real tokens** (24-48h old) — age penalty hits hard
- **Niche community tokens** — low liquidity but loyal holders
- **Post-dump recovery tokens** — sell ratio skewed from recent dump

I manually overrode two of these. Both turned out to be legitimate. The lesson: the gate is a filter, not a final decision. For borderline cases (45-59), the bot alerts me on Discord and I decide.

## Integration

The safety gate runs as a pre-buy check in the TradeBot daemon:

1. Scout finds a buy signal
2. Safety gate fetches token data → scores it
3. Score < 60 → **BLOCKED**, reported to Discord failures list
4. Score 60+ → proceeds to execution
5. Score 45-59 → pauses, asks for human approval

**Latency added:** ~300ms per trade. Negligible.

## Building Your Own

You don't need my exact code. Here's the minimal version:

```python
import requests

def check_token(mint):
    r = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{mint}")
    data = r.json()['pairs'][0]
    
    score = 0
    score += min(data['liquidity']['usd'] / 1000, 25)  # liquidity
    score += min(data['volume']['h24'] / 10000, 20)   # volume
    # ... etc
    
    return score
```

Add your own weights based on your risk tolerance. Mine is conservative because the portfolio is small.

## What's Next

1. **RugCheck.xyz integration** — deeper contract analysis for tax tokens and mint authority
2. **Historical scoring** — track score changes over time, catch deteriorating tokens
3. **Community data** — aggregate reports from multiple traders for crowd-sourced scam detection

## The Lesson

Automation without guardrails is gambling. The safety gate turns memecoin trading from Russian roulette into calculated risk. It's not perfect — but it's better than trusting a green chart and a Twitter hype thread.

**Want the full safety gate code?** It's included in the TradeBot automation package ($25) — scoring algorithm, API integration, and Discord reporting.

---

*This is not financial advice. This is a security tool I built because I was tired of losing money to scams. Use at your own risk. Verify everything yourself.*
