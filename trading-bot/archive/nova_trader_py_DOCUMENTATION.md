# nova_trader.py - ARCHIVED

**Status:** ARCHIVED - No longer in active use
**Date Archived:** 2026-04-26
**Replaced By:** `scout.py` + `executor.py` (Solana/Jupiter)

## What This Was

Original trading bot for Ethereum/Base network using:
- **Chain:** Ethereum (Base L2)
- **DEX:** Uniswap V3 (planned)
- **Wallet:** `0x4d2049F1e4a1d34FF458944c13E4720d2BAbc6A8`
- **Assets:** ETH, USDC (wrapped on Base)
- **Features:** Notion integration, price alerts, portfolio tracking

## Why Archived

1. **Network Switch:** Migrated from Ethereum/Base to Solana
2. **Better Infrastructure:** Solana/Jupiter offers:
   - Faster transactions
   - Lower fees
   - Better meme coin liquidity
   - Native Jupiter API
3. **Simplified Architecture:** New system uses:
   - `scout.py` - Signal detection
   - `executor.py` - Trade execution
   - `portfolio_research.py` - Confidence scoring

## Key Differences

| Feature | nova_trader.py (Archived) | New System (Active) |
|---------|---------------------------|---------------------|
| Chain | Ethereum/Base | Solana |
| DEX | Uniswap (planned) | Jupiter |
| Wallet | 0x4d20... | 7FNLUAQQ... |
| Assets | ETH, USDC | SOL, PENGU, PUMP, etc. |
| Data | Notion | Local JSON + Helius RPC |

## Historical Note

This was the first iteration of Nova's trading bot, built during initial setup. It supported:
- Web3/Ethereum integration
- Base network (L2)
- Notion database for tracking
- Price alerts via CoinGecko
- Stop loss / take profit logic

Never fully deployed due to migration to Solana ecosystem.

## Preservation

Kept for:
- Historical reference
- Ethereum/Base trading logic examples
- Notion integration patterns
- Potential future Ethereum strategies

---
**File Location:** `trading-bot/archive/nova_trader.py`
**Original Location:** `trading-bot/nova_trader.py` (moved)
