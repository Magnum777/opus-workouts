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

### 3. Wider stops, longer holds + trailing stop
- Stop loss: **-8%** (was -5% - too tight for memecoins)
- Take profit: **+25%** (was +10%)
- **Trailing stop activates at +15%** — once a position is up 15%+, the stop starts trailing
- **Trailing distance: 5%** — stop follows 5% below the highest price seen
  - Example: buy at $10, price hits $16.70 (+67%), stop is at $15.87 — you lock in ~+59%
  - Example: buy at $10, price hits $11.50 (+15%), stop is at $10.93 — you lock in ~+9%
- Trailing stop overrides the hard -8% stop once active (it's always higher)
- Minimum hold: **1 hour** (was 0 - sold immediately)
- Max position: **40% of portfolio** (was 90% - WTF)

### 4. Smarter loss tracking
- Consecutive losses counter only counts trades **over $1** (ignores dust)
- Trading pauses after **3 consecutive real losses** (was being reset by 1-cent trades)

### 5. No daily trade limit
- Daily limit: **unlimited** (other guardrails handle discipline)
- Run cycle: **15min** (was 10min)

### 6. Partial trim at +12%
- Sell **50%** at +12% to free capital for new positions
- Let remaining 50% ride to +25% full TP or trailing stop exit
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
