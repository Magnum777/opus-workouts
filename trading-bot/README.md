# TradeBot Portfolio Tracker v3

## Overview

The portfolio tracker is the data layer for the TradeBot. It tracks:
- Current balances (SOL, USDC, tokens)
- Open positions with unrealized PnL
- Trade history with realized PnL
- Performance metrics (win rate, avg profit, etc.)

## Architecture

### Two-Layer Design

The system has two layers for portfolio data:

**1. Reporting Layer (LIVE on-chain) — `portfolio.py`**
- Queries on-chain balances on EVERY call
- Checks BOTH Token program AND Token-2022 program
- Gets prices from DexScreener API (fallback Jupiter)
- Used by the executor for Discord reports
- **This is the source of truth for what you actually hold**

**2. Trading Layer (DB cache) — `portfolio.db.json` + `portfolio_db_v2.py`**
- Caches position data for the bot's internal trading logic
- Tracks cost basis, buy prices, trailing stops, PnL per position
- Used by threshold checks (stop loss / take profit / trim)
- **This is the source of truth for trading decisions**

### Key Design Principles

1. **On-chain balances are ALWAYS the source of truth for reporting**
2. The DB is a cache for trading state (cost basis, PnL tracking)
3. Both Token program AND Token-2022 program are queried
4. Prices come from DexScreener API (free, no API key needed)
5. The executor's Discord reports use LIVE on-chain data, not the DB

### Files

| File | Purpose |
|------|---------|
| `portfolio.py` | **NEW** — Live on-chain portfolio module (single source of truth for reporting) |
| `portfolio.db.json` | The portfolio database (JSON cache for trading state) |
| `portfolio_tracker.py` | V3 tracker — fetches on-chain data, manages DB |
| `verify_portfolio.py` | Verification script — checks DB against on-chain |
| `portfolio_db_v2.py` | Legacy V2 module (kept for backward compat — trading logic) |
| `run_executor.py` | Main executor — runs every 10 min, uses `portfolio.py` for reports |

## Usage

### View live portfolio (on-chain)

```bash
python portfolio.py
```

This queries on-chain in real-time and shows what you actually hold.

### Refresh portfolio DB from on-chain

```bash
python portfolio_tracker.py --refresh
```

This will:
1. Query on-chain for SOL balance
2. Query Token program for all SPL tokens
3. Query Token-2022 program for all Token-2022 tokens
4. Get prices from DexScreener API
5. Update the DB with current state
6. Recalculate performance metrics

### View current portfolio (from DB)

```bash
python portfolio_tracker.py
```

### Verify DB against on-chain

```bash
python verify_portfolio.py
```

This compares the DB against live on-chain data and reports any discrepancies.

### Auto-fix discrepancies

```bash
python verify_portfolio.py --fix
```

This will refresh the DB from on-chain if discrepancies are found.

### JSON output (for programmatic use)

```bash
python portfolio.py --json
python verify_portfolio.py --json
```

## How It Works

### On-Chain Queries

The tracker queries two Solana programs:
- **Token Program** (`TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`): Standard SPL tokens
- **Token-2022 Program** (`TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`): Newer token standard

### Price Discovery

Prices are fetched from:
1. **DexScreener API** (primary) — free, no API key, covers most tokens
2. **Jupiter API** (fallback) — for tokens not on DexScreener

### PnL Calculation

- **Realized PnL** = close_value - cost_basis (per trade)
- **Unrealized PnL** = current_value - cost_basis (per open position)
- **Total Realized PnL** = sum of all trade PnLs
- **Win Rate** = winning trades / total trades

### Failed Transaction Handling

The executor stores pending TX hashes in `.pending_buy_tx.json`. On the next cycle, it checks if these TXs confirmed. If they failed, the portfolio state is NOT updated.

## Cron Jobs

The TradeBot runs on several cron schedules:

| Cron | Schedule | Purpose |
|------|----------|---------|
| TradeBot-Executor | Every 10 min | Execute trades, report live portfolio |
| TradeBot-Research | Every 2 hours | Research new tokens |
| TradeBot-DailyResearch | Daily 9:15 AM | Daily research scan |
| TradeBot-WeeklyReview | Weekly Saturday 2 PM | Weekly performance review |
| TradeBot-Analytics | Weekly Monday 10 AM | Analytics report |

## Troubleshooting

### "DB doesn't match on-chain"

Run `python verify_portfolio.py --fix` to auto-correct.

### "Token not found in portfolio"

The tracker only shows tokens with value > $0.01. Dust tokens are skipped.

### "Price shows $0"

The token might not be on DexScreener. Try Jupiter API as fallback. Some very new or low-liquidity tokens may not have a price feed.

### "USDC balance wrong"

The tracker queries both Token and Token-2022 programs for USDC. If you have USDC in a Token-2022 account, it will be found.

### "Executor reports wrong numbers"

The executor now uses `portfolio.py` for live on-chain data. If numbers look wrong, run `python portfolio.py` to check the live state. If the live state is correct but the executor report is wrong, the executor may need updating.
