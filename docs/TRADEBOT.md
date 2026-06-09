# TradeBot — Documentation

> Current as of 2026-05-08

## Overview

TradeBot V2 is a Solana memecoin trading system that runs automated scans, research, and trade execution via cron jobs. It delivers all reports to `#tradebot` on Discord.

## Wallet & Portfolio

- **Wallet**: `7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA`
- **RPC**: Helius mainnet (`trading-bot/.env`)
- **Current positions** (as of 2026-05-08):
  - SOL: ~0.475 SOL (~$43)
  - PENGU: 3,900 tokens (~$41)
  - FARTCOIN: 72 tokens (~$18)
  - Total: ~$103

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scout_v2.py` | Scan portfolio, fetch prices, detect signals |
| `research_v2.py` | Deep research on tokens, confidence scoring |
| `executor_v2.py` | Process queued signals, execute trades |
| `tradebot_auto.py` | Legacy all-in-one runner |
| `portfolio_db_v2.py` | Portfolio state management |
| `jupiter_swap.py` | Jupiter DEX swap execution |

## Cron Jobs

| Job | Schedule | What it does |
|-----|----------|-------------|
| TradeBot-Scout | Every 10min | Runs `scout_v2.py` + `research_v2.py`, reports portfolio status |
| TradeBot-Executor | Every 15min | Runs `executor_v2.py`, processes queued signals |
| TradeBot-CryptoResearch | Every 1hr | Web search market scan, trending tokens |

All use model `ollama/deepseek-v4-flash:cloud` and deliver to `#tradebot` (1470957359248576699).

## Signal Types

| Signal | Trigger | Action |
|--------|---------|--------|
| `STRONG_BUY` | Confidence ≥70% or dip reversal | Aggressive buy |
| `BUY` | Confidence 50-69% | Standard buy |
| `TAKE_PROFIT` | P&L ≥5% | Sell for profit |
| `STOP_LOSS` | P&L ≤-3% | Cut losses |
| `TRAILING_STOP_SELL` | Price dropped 2% from peak | Protect gains |
| `STRONG_SELL` | Peak reversal + profitable | Momentum exit |

## Bug Fixes Applied (2026-05-08)

1. **Token program ID** — Changed from standard SPL Token to Token Extension program (`TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`)
2. **Jupiter pricing** — Made decimals-aware (SOL=9 decimals, others=6)
3. **Value calculations** — Use `uiAmount * price` instead of `raw_amount * price / 1e6`
4. **FART → FARTCOIN** — Renamed token across all scripts and DB

## Files

- `trading-bot/.env` — Coinbase API keys, Helius RPC URL
- `trading-bot/portfolio.db.json` — Current portfolio state
- `trading-bot/trading-queue.json` — Pending signals
- `trading-bot/scout-log.json` — Scout run history

## Key Lessons

- API rate limiting matters: Scout 10min, Executor 15min, Research 1hr
- Jupiter price API needs decimals-aware parsing
- Always use `uiAmount` (human-readable) not raw amounts for value calc