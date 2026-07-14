# Trading Bot Research - Feb 24, 2026

## Current Status
- Wallet configured via env vars
- Balance: ~0.056 ETH (~$106)

## Notes
- Old Base wallet address removed from repo for security
- Keys now stored in trading-bot/.env
- USDC sent back to Coinbase (~$100)

## What Works
- Web3.py for reading blockchain ✅
- Checking balances ✅
- Signing transactions ✅

## What's Blocked
- Uniswap V3 swap (complex ABI)
- Polymarket (US restrictions)
- Coinbase API (OAuth complexity)

## Research Findings

### 0x Swap API
- https://0x.org/docs/0x-swap-api
- Free quote endpoint for price discovery
- Execution requires API key

### Coinbase CDP Swap API
- New! "CDP Swap API" - seamless token swaps
- Part of Coinbase Developer Platform
- Should work with our CDP credentials!

### Alternatives
- Hummingbot - open source market making
- DexScreener - prices only, no trading
- ChangeNow - simple swap API

## Next Steps
1. Try Coinbase CDP Swap API (we have credentials!)
2. Get 0x API key (free)
3. Or use manual trading for now

## Links
- https://0x.org/docs/0x-swap-api
- https://www.coinbase.com/developer-platform/discover/launches/swap-api
