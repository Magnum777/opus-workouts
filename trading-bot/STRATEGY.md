# TradeBot V3 Strategy — Rebuild from $90

## The Problem
The bot was buying $3-5 positions and getting stopped out at -5% over and over, burning the account with death-spiral re-buys (sell BONK at -91%, next cycle research says "dip = good entry, BUY", repeat).

## Fixes Applied

### 1. No more micro-trades
- Minimum buy: **$20** (was $3)
- Buy sizes: $30 / $50 / $70 (was $15 / $30 / $45)
- Cap: $70/trade

### 2. Re-buy cooldown
- Selling at a loss puts the token on a **24-hour cooldown list**
- Bot can't re-enter until cooldown expires
- Stored in `rebuy_cooldowns.json`

### 3. Wider stops, longer holds
- Stop loss: **-8%** (was -5% - too tight for memecoins)
- Take profit: **+15%** (was +10%)
- Minimum hold: **1 hour** (was 0 - sold immediately)
- Max position: **40% of portfolio** (was 90% - WTF)

### 4. Smarter loss tracking
- Consecutive losses counter only counts trades **over $1** (ignores dust)
- Trading pauses after **3 consecutive real losses** (was being reset by 1-cent trades)

### 5. No daily trade limit
- Daily limit: **unlimited** (other guardrails handle discipline)
- Run cycle: **15min** (was 10min)

### 6. Partial trim at +8%
- Sell **50%** at +8% to free capital for new positions
- Let remaining 50% ride to +15% full TP
- Trim only fires once per position (no repeated trims)

## The Plan: $90 → $500

### Phase 1: Stabilize (Week 1)
- Only take highest-confidence trades (80+ confidence)
- Max 2 concurrent positions (40% cap)
- Goal: survive, collect data, build confidence tracking

### Phase 2: Compound (Week 2-3)
- As USDC grows above $50, use larger sizes
- Let winners run with trailing stops
- Add profit from closed positions to position size pool

### Phase 3: Scale (Week 4+)
- Once portfolio hits $150+, enable position scaling
- 2 positions at $50-70 each
- Revisit confidence scoring against actual results

## Current Holdings
- SOL: ~0.038
- USDC: ~$35.93
- TRUMP: ~$25.62
- RAY: ~$25.16
- **Total: ~$90.57**

## Key Rules
- Never re-buy within 24h of a stop-loss
- Never go all-in on one token
- Never trade when 3 consecutive real losses hit
- Minimum $20 or no trade

## What to watch
- Win rate over next 20 trades
- Average profit per winner vs loss per loser
- Are the confidence thresholds actually predictive?
