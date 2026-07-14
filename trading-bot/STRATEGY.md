# TradeBot V3 Strategy — Actual (Jun 26, 2026)

## Current State
- **Wallet:** 7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA
- **SOL:** 0.0035 (critically low — needs ~0.02 for gas)
- **USDC:** $8.86
- **Total:** ~$69
- **Positions:** 4 (LOA $37, MERLIN $10, VALORA $9, HPHau8yi $4)
- **All positions are Token-2022 (pump.fun tokens)**

## The Problem
The bot was buying $3-5 positions and getting stopped out at -5% over and over, burning the account with death-spiral re-buys. The V3 strategy fixed the sizing and cooldown logic, but the **swap execution was broken**:

1. **Token-2022 incompatibility** — Jupiter v1 lite API doesn't handle Token-2022 tokens. All sell TXs either failed silently (TX confirmed but swap didn't execute) or returned error 6024 (token program mismatch).
2. **Phantom sells** — `execute_sell_live` returned `True` even when TX didn't confirm ("did not confirm after ~20s - returning anyway"). The bot *thought* it sold, but tokens were still there.
3. **skip_preflight=True** — TXs were sent without simulation, so the RPC returned a hash for TXs that never landed on-chain.
4. **59 stale pending TXs** — accumulated unconfirmed buy TXs in `.pending_buy_tx.json` (cleared).

## Fixes Applied (Jun 26)
1. **Switched to Jupiter v2 API** — handles Token-2022 natively, no tokenProgram parameter needed
2. **skip_preflight=False** — TXs are now simulated before sending, catching errors early
3. **Sell no longer returns success on timeout** — will retry 3 times, then fail properly
4. **Cleared stale pending TX file** — 59 entries removed
5. **Updated STRATEGY.md** — this file now matches reality

## Strategy

### Sizing (%-based, scaled to capital)
| Capital Range | Strong Buy | Medium | Base |
|--------------|------------|--------|------|
| $0-$15 (survival) | 60% | 45% | 30% |
| $15-$30 (dig-out) | 45% | 30% | 20% |
| $30-$150 (rebuild) | 40% | 25% | 15% |
| $150+ (standard) | $15 flat | $12 flat | $10 flat |

### Risk Limits
- Max 6 concurrent positions
- Max 40% of portfolio in one position
- Max 70% total exposure
- Stop loss: -8%
- Take profit: +20% — quick flips, no trim, full exit
- Trailing stop: activates at +12%, trails 4% below peak
- Min hold: 1 hour
- Re-buy cooldown: 48 hours
- Consecutive loss pause: 3 losses (decays 1 every 6h)

### Execution
- Jupiter v2 API for all swaps
- Preflight simulation enabled
- 30s TX confirmation wait (was 20s)
- 3 retry attempts on send failure
- Pending TX recovery on next cycle

## What's Needed
- **SOL top-up:** Send ~0.02 SOL to the wallet for gas
- **Sell positions:** Clear the 4 open positions to reset exposure
- **Let it run:** With working swaps, the bot can actually trade
