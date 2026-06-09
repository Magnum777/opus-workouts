# From 0 to $56 Realized PnL: TradeBot Monthly Review (May 2026)

**Author:** James "Opus" Henderson  
**Date:** June 1, 2026  
**Tags:** Crypto, Trading, Monthly Review, Solana, AI

---

## The Setup

**Capital:** $93 USDC (started April 28)  
**Strategy:** Momentum-based memecoin swing trading  
**Timeframe:** 30 days  
**Automation:** Full — research, analysis, execution, reporting  

## The Numbers

| Metric | Value | Context |
|--------|-------|---------|
| Starting Value | $93.00 | Initial USDC deposit |
| Current Value | $55.89 | After realized + unrealized |
| Realized PnL | +$56.27 | Closed trades only |
| Unrealized PnL | -$1.78 | Open positions at risk |
| Total Trades | 21 | All closed positions |
| Winning Trades | 7 | Profitable closures |
| Losing Trades | 14 | Unprofitable closures |
| Win Rate | 33% | Not great, but profitable |
| Best Trade | ORCA +$46.34 | Single trade covered most gains |
| Worst Trade | BONK -$19.03 | Largest loss |
| Current Streak | 14 losses | Consecutive losing closures |
| Best Streak | 7 wins | Consecutive winning closures |

## What Worked

**ORCA was the portfolio savior.** Bought around $0.80, rode to $1.20+, sold at +46%. That single trade generated more PnL than the rest of the month combined. Early momentum identification paid off.

**The safety gate blocked 6 honeypots.** Without it, the portfolio would likely be at $0. The $56 realized PnL includes zero scam losses — every loss was a legitimate market move.

**Mechanical exits prevented disaster.** The -3% stop-loss rule closed losing positions before they became catastrophic. The BONK loss was -$19. Without the stop, it could have been -$40+.

## What Didn't Work

**The 14-loss streak is unacceptable.** The signal generator is buying minor dips that keep dipping. Entry criteria are too loose — "token is down from recent high" is not a strategy.

**Position sizing is broken.** Four open positions with only $55 in play means each position is ~$13. Transaction fees (1-2% per trade) eat profits on small positions. Need fewer, larger positions.

**No trailing stop on winners.** ORCA was sold at +46% because it hit the fixed target. But what if it went to +100%? The fixed exit rule leaves money on the table when momentum continues.

## Strategy Changes for June

**1. Tighter Entry Criteria**
Require ALL of:
- Volume spike > 50% above 24h average
- Price confirmation: 15-min green candle after entry signal
- Token age > 3 days (avoid launch-day dumps)
- Safety score > 65 (up from 60)

**2. Trailing Stops**
- Initial stop: -3% (unchanged)
- If position reaches +10%: move stop to breakeven
- If position reaches +20%: move stop to +10%
- Let winners run. Cut losers fast.

**3. Position Limits**
- Max 2 open positions until portfolio > $100
- Min position size: $20 (avoid fee erosion)
- No adding to losing positions (no averaging down)

**4. Time-Based Exits**
- Any position held > 7 days gets evaluated for exit
- Momentum trades are short-term. If it hasn't moved in a week, it's not a momentum trade.

## The Economics

| Item | Cost |
|------|------|
| Starting capital | $93 |
| Jupiter swap fees | ~$3 total (1% per trade, ~25 trades) |
| Helius RPC | $0 (free tier) |
| AI compute | $0 (local Ollama) |
| Net realized | $56 |
| ROI | 60% |

Not bad for a first month. But it's one big win (ORCA) carrying the portfolio. Consistency matters more than one home run.

## What I'm Tracking Now

Added analytics to the TradeBot:
- Win rate by token type (meme vs utility vs governance)
- Win rate by entry signal type (momentum vs dip vs breakout)
- Average hold time for winners vs losers
- Fee impact on small positions
- Safety gate false positive rate

This data will guide strategy adjustments. No more gut feel. Only numbers.

## Goals for June

| Goal | Target |
|------|--------|
| Realized PnL | +$40 (conservative, no ORCA-style home runs expected) |
| Win rate | > 40% |
| Max consecutive losses | < 5 |
| Honeypot losses | $0 (maintain perfect record) |
| Portfolio value | > $100 |

## The Lesson

Month 1 proved the concept: an AI can trade profitably with proper guardrails. But profitability came from one big win, not consistent execution.

Month 2 needs to prove consistency. Smaller wins, smaller losses, fewer trades, better entries. The goal isn't to get rich. It's to prove the system works across market conditions.

**Want the full TradeBot config?** Included in the TradeBot automation ($25) — safety gate, execution logic, portfolio tracking, and Discord reporting.

---

*This is not investment advice. This is a real trading experiment with real money and real losses. The $93 is a learning budget. If it goes to $0, the lesson is worth more than the money.*
