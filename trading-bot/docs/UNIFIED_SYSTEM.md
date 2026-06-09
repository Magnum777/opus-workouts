# Unified Trading System Documentation

**System:** TradeBot-Nova Solana Trading  
**Last Updated:** 2026-04-27  
**Status:** ✅ LIVE

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    UNIFIED DATABASE                          │
│              portfolio.db.json (Single Source)              │
├─────────────────────────────────────────────────────────────┤
│  Portfolio  │  Positions  │  Trades  │  Tax Summary         │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   scout.py   │      │ executor.py  │      │   research   │
│   (1 min)    │      │   (5 min)    │      │  (30 min)    │
└──────────────┘      └──────────────┘      └──────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
    Syncs to DB           Logs to DB           Updates DB
```

---

## Core Files

| File | Purpose | Updates DB? |
|------|---------|-------------|
| `portfolio.db.json` | Central database | - |
| `portfolio_db.py` | DB module (import) | - |
| `scout.py` | Portfolio scanning | ✅ Yes |
| `executor.py` | Trade execution | ✅ Yes |
| `portfolio_research.py` | Confidence scores | No (separate) |

---

## Database Schema

### portfolio.db.json

```json
{
  "schema_version": "1.0",
  "last_updated": "2026-04-27T11:10:20Z",
  "wallet": {
    "address": "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA",
    "chain": "solana",
    "rpc": "https://mainnet.helius-rpc.com"
  },
  "portfolio": {
    "sol_balance": 0.0753,
    "sol_price_usd": 0.09,
    "total_value_usd": 87.24,
    "positions_count": 2
  },
  "positions": [...],
  "trades": [...],
  "tax_summary": {...}
}
```

### Position Schema

```json
{
  "token": "PENGU",
  "mint": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv",
  "amount_raw": 3900533310,
  "current_price_usd": 0.00000962,
  "current_value_usd": 37.12,
  "current_value_sol": 436.01,
  "buy_price_usd": 37.52,
  "buy_price_sol": 440.28,
  "cost_basis_usd": 37.52,
  "unrealized_pnl_usd": -0.40,
  "unrealized_pnl_pct": -1.07,
  "status": "OPEN",
  "opened_at": "2026-04-26T13:21:25Z",
  "tx_hash": "Me2uVUsKMeTPV9Jk9dT7CWVxeCU45hXtBDPLXbF1xZxx..."
}
```

### Trade Schema

```json
{
  "timestamp": "2026-04-26T13:21:25Z",
  "token": "PENGU",
  "action": "BUY",
  "mint": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv",
  "amount_raw": 3900533310,
  "amount_sol": 0.2,
  "tx_hash": "Me2uVUsKMeTPV9Jk9dT7CWVxeCU45hXtBDPLXbF1xZxx...",
  "cost_basis_usd": 37.52,
  "proceeds_usd": 0,
  "pnl_usd": 0,
  "pnl_pct": 0
}
```

---

## Current Holdings

| Token | Amount | Value (USD) | Value (SOL) | Status |
|-------|--------|-------------|-------------|--------|
| PENGU | 3.90B | $37.12 | 436.01 | OPEN |
| PUMP | 28.58B | $50.11 | 588.07 | OPEN |
| **Total** | - | **$87.24** | **1,024.09 SOL** | - |

**SOL Balance:** 0.0753 SOL  
**SOL Price:** $0.09  
**Portfolio Value:** $87.24

### Historical Trades

Tokens traded: PENGU, PUMP, TRUMP, FART, BIRB

**Note:** TRUMP, FART, BIRB were sold (take profit) or didn't complete. Only PENGU and PUMP remain in current holdings.

---

## Tax Tracking

### Automatic Logging

Every trade automatically updates:
- `trade-history.json` (legacy)
- `portfolio.db.json` → `trades[]`
- `portfolio.db.json` → `tax_summary{year}`

### Tax Summary Format

```json
"tax_summary": {
  "2026": {
    "total_trades": 15,
    "realized_pnl": 127.45,
    "fees_paid": 2.34,
    "short_term_gains": 127.45,
    "long_term_gains": 0
  }
}
```

### Cost Basis Tracking

- **Buys:** Cost basis = purchase price
- **Sells:** Realized P&L = proceeds - cost basis
- **Unrealized:** Current value - cost basis (for open positions)

---

## How Scripts Use Unified DB

### scout.py

```python
import portfolio_db as pdb

# In main():
pdb.sync_from_blockchain(holdings, sol_balance, sol_price)
```

**What it does:**
- Reads blockchain via Helius RPC
- Calculates position values
- Syncs to unified DB
- Updates last_updated timestamp

### executor.py

```python
import portfolio_db as pdb

# On BUY:
pdb.add_position({...})

# On SELL:
pdb.close_position(token, close_data)

# Both:
pdb.add_trade(trade_data)
```

**What it does:**
- Adds new positions on buys
- Closes positions on sells (calculates realized P&L)
- Logs all trades to unified DB
- Updates tax summary

---

## Database Functions

### `load_db()`
Load central database from `portfolio.db.json`

### `save_db(db)`
Save database with updated timestamp

### `add_position(position)`
Add new position to DB

### `close_position(token, close_data)`
Close position, calculate realized P&L, update tax summary

### `add_trade(trade_data)`
Log trade to history and update tax summary

### `sync_from_blockchain(holdings, sol_balance, sol_price)`
Sync portfolio values from blockchain data

### `get_tax_report(year)`
Generate tax report for specific year

---

## Cron Schedule

| Cron | Script | Frequency | Purpose |
|------|--------|-----------|---------|
| Scout-1min | `scout.py` | Every 1 min | Portfolio scan + DB sync |
| Executor-5min | `executor.py` | Every 5 min | Trade execution |
| Portfolio-Research | `portfolio_research.py` | Every 30 min | Confidence scores |

---

## Verification

### Check DB Status

```python
import portfolio_db as pdb
db = pdb.load_db()
print(f"Portfolio: ${db['portfolio']['total_value_usd']:.2f}")
print(f"Positions: {len(db['positions'])}")
print(f"Trades: {len(db['trades'])}")
```

### Check Tax Summary

```python
import portfolio_db as pdb
report = pdb.get_tax_report("2026")
print(f"2026 Trades: {report['summary']['total_trades']}")
print(f"Realized P&L: ${report['summary']['realized_pnl']:.2f}")
```

---

## Safety & Best Practices

### ✅ Implemented
- ✅ Single source of truth (portfolio.db.json)
- ✅ All scripts use same DB module
- ✅ Automatic tax tracking on every trade
- ✅ Cost basis calculated for all positions
- ✅ Realized P&L tracked on sells
- ✅ Timestamps on all records
- ✅ Transaction hashes saved

### 🔒 Security
- Wallet key in environment (not in DB)
- DB is JSON (readable/auditable)
- All changes timestamped
- All trades logged with tx_hash

---

## Troubleshooting

### DB Not Updating
1. Check scout.py ran: `python scout.py`
2. Check timestamp in DB: `cat portfolio.db.json | grep last_updated`
3. Verify holdings: Should see `[DB SYNC]` message

### Missing Positions
1. Run scout: `python scout.py`
2. Check Helius RPC connection
3. Verify wallet has tokens

### Tax Data Missing
1. Check `trade-history.json` exists
2. Verify executor.py ran
3. Check `portfolio.db.json` → `tax_summary`

---

## Archive

Old Ethereum/Base files archived:
- `archive/nova_trader.py`
- `archive/aggressive_trader.py`
- `archive/auto_trader.py`
- `archive/enforced_trader.py`
- `archive/trading_loop.py`
- `archive/trading_loop_new.py`

---

**System Status:** ✅ LIVE  
**Chain:** Solana  
**DEX:** Jupiter  
**Last Sync:** Just now
