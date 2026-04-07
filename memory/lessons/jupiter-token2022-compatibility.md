# Jupiter DEX - Token-2022 Compatibility Issue

## Problem
Some Solana tokens use the Token-2022 standard (extended token program) which Jupiter aggregator may not fully support for swap routing.

## Symptoms
- Repeated transaction failures with error `0x1788` (custom program error)
- Error message: `SendTransactionPreflightFailure` or `Transaction simulation failed`
- Affects both buys AND sells via Jupiter API
- Bot retries fail continuously (every 30s in our case)

## Tokens Affected (Feb 2026)
- **BIRB** (G7vQWurMkMMm2dU3iZpXYFTHT9Biio4F4gZCrwFpKNwG) - -77.5% loss, stuck
- **SKR** (SKRbvo6Gf7GondiT3BbTfuRDPqLWei4j2Qy2NPGZhW3) - -39.6% loss, stuck

## Workarounds
1. **Manual sale via Phantom/Solflare** - Most reliable
2. **Try alternative DEX APIs** - Orca, Raydium direct (not via Jupiter aggregator)
3. **Remove from positions.json** - Stop bot from retrying failed sells
4. **Pre-trade verification** - Check if token is Token-2022 before buying via Jupiter

## Lesson
Before buying any token via Jupiter API:
- Verify token standard (Token vs Token-2022)
- Check liquidity on multiple DEXs
- Test with small amount first
- Have manual exit strategy ready

## References
- Solana Token-2022: https://spl.solana.com/token-2022
- Jupiter API docs: https://station.jup.ag/docs/apis/swap-api
