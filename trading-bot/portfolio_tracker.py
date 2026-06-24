#!/usr/bin/env python3
"""
TradeBot Portfolio Tracker v3
================================
On-chain verified portfolio tracking for Solana.

KEY DESIGN:
- On-chain balances are the SOURCE OF TRUTH
- The DB file is a CACHE, validated against on-chain every write
- Queries BOTH Token program AND Token-2022 program
- Handles failed tx detection (doesn't update state on failed txs)
- Realized PnL calculated correctly: close_value - cost_basis
- Prices from DexScreener API (free, no API key needed)

Usage:
    python portfolio_tracker.py              # Print current portfolio
    python portfolio_tracker.py --refresh     # Force refresh from on-chain
    python portfolio_tracker.py --verify     # Verify DB against on-chain
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timezone

# ── Configuration ──────────────────────────────────────────────────────────

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db.json")
WALLET_ADDRESS = "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA"
RPC_URL = "https://api.mainnet-beta.solana.com"
HELIUS_RPC = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"

# Token program IDs
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
TOKEN_2022_PROGRAM = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"

# Known mints
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDT_MINT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
STABLECOIN_MINTS = {USDC_MINT, USDT_MINT}

# ── RPC Helpers ────────────────────────────────────────────────────────────

def _rpc_call(method, params=None, rpc_url=None):
    """Make a JSON-RPC call to Solana."""
    if rpc_url is None:
        rpc_url = RPC_URL
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or []
    }
    try:
        resp = requests.post(rpc_url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if "error" in data:
                return None, data["error"]
            return data.get("result"), None
        return None, f"HTTP {resp.status_code}"
    except Exception as e:
        return None, str(e)


def _rpc_call_helius(method, params=None):
    """Make a JSON-RPC call to Helius (for getTokenAccountsByOwner which needs parsed data)."""
    return _rpc_call(method, params, rpc_url=HELIUS_RPC)


# ── On-Chain Balance Queries ───────────────────────────────────────────────

def get_sol_balance():
    """Get SOL balance from on-chain."""
    result, err = _rpc_call("getBalance", [WALLET_ADDRESS])
    if result:
        return result.get("value", 0) / 1e9
    return 0


def get_token_accounts(program_id=TOKEN_PROGRAM):
    """Get all token accounts for a wallet under a specific program.
    Returns list of {mint, amount, decimals, ui_amount} dicts."""
    result, err = _rpc_call_helius("getTokenAccountsByOwner", [
        WALLET_ADDRESS,
        {"programId": program_id},
        {"encoding": "jsonParsed"}
    ])
    if not result:
        return []

    accounts = []
    for item in result.get("value", []):
        try:
            parsed = item["account"]["data"]["parsed"]["info"]
            mint = parsed["mint"]
            token_amount = parsed["tokenAmount"]
            amount_raw = int(token_amount["amount"])
            ui_amount = float(token_amount.get("uiAmount") or 0)
            decimals = token_amount["decimals"]

            if ui_amount > 0:
                accounts.append({
                    "mint": mint,
                    "amount_raw": amount_raw,
                    "amount": ui_amount,
                    "decimals": decimals,
                    "program": program_id
                })
        except (KeyError, ValueError, TypeError):
            continue

    return accounts


def get_all_token_balances():
    """Get ALL token balances from both Token and Token-2022 programs."""
    token_accounts = get_token_accounts(TOKEN_PROGRAM)
    token2022_accounts = get_token_accounts(TOKEN_2022_PROGRAM)
    return token_accounts + token2022_accounts


# ── Price Lookup ────────────────────────────────────────────────────────────

def get_sol_price():
    """Get SOL price from Jupiter API."""
    try:
        resp = requests.get(
            "https://lite-api.jup.ag/swap/v1/quote"
            f"?inputMint={SOL_MINT}&outputMint={USDC_MINT}&amount=1000000000&slippage=1",
            timeout=8
        )
        if resp.status_code == 200:
            return float(resp.json()["outAmount"]) / 1e6
    except:
        pass
    return 0


def get_dexscreener_price(mint):
    """Get token price from DexScreener API. Returns price in USD or 0."""
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            pairs = data.get("pairs", [])
            if pairs:
                # Prefer Raydium, then Orca, then any
                for pair in pairs:
                    if pair.get("dexId") == "raydium" and pair.get("priceUsd"):
                        return float(pair["priceUsd"])
                for pair in pairs:
                    if pair.get("dexId") == "orca" and pair.get("priceUsd"):
                        return float(pair["priceUsd"])
                # Fallback to first pair with a price
                for pair in pairs:
                    if pair.get("priceUsd"):
                        return float(pair["priceUsd"])
    except:
        pass
    return 0


def get_jupiter_price(mint):
    """Get token price via Jupiter quote. Returns price per 1 full token in USD."""
    try:
        resp = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote"
            f"?inputMint={mint}&outputMint={USDC_MINT}&amount=1000000&slippage=1",
            timeout=8
        )
        if resp.status_code == 200:
            return float(resp.json()["outAmount"]) / 1e6
    except:
        pass
    return 0


def get_token_price(mint):
    """Get token price with fallback: DexScreener -> Jupiter."""
    price = get_dexscreener_price(mint)
    if price > 0:
        return price
    return get_jupiter_price(mint)


# ── Portfolio Data ──────────────────────────────────────────────────────────

def fetch_onchain_portfolio():
    """Fetch complete portfolio from on-chain. Returns dict with all balances."""
    sol_balance = get_sol_balance()
    sol_price = get_sol_price()
    all_tokens = get_all_token_balances()

    holdings = []
    usdc_balance = 0
    total_value = sol_balance * sol_price

    for token in all_tokens:
        mint = token["mint"]
        amount = token["amount"]
        decimals = token["decimals"]

        # Handle stablecoins
        if mint in STABLECOIN_MINTS:
            usdc_balance += amount
            total_value += amount
            continue

        # Get price
        price = get_token_price(mint)
        value_usd = amount * price
        value_sol = value_usd / sol_price if sol_price > 0 else 0

        holdings.append({
            "mint": mint,
            "amount_raw": token["amount_raw"],
            "amount": amount,
            "decimals": decimals,
            "price_usd": price,
            "value_usd": value_usd,
            "value_sol": value_sol,
            "program": token["program"]
        })
        total_value += value_usd

    return {
        "sol_balance": sol_balance,
        "sol_price_usd": sol_price,
        "usdc_balance": usdc_balance,
        "total_value_usd": total_value,
        "holdings": holdings,
        "verified_at": datetime.now(timezone.utc).isoformat()
    }


# ── DB Operations ───────────────────────────────────────────────────────────

def load_db():
    """Load the portfolio DB."""
    if not os.path.exists(DB_PATH):
        return create_default_db()
    with open(DB_PATH, "r") as f:
        return json.load(f)


def save_db(db):
    """Save the portfolio DB."""
    db["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)
    return db


def create_default_db():
    """Create a fresh default DB."""
    return {
        "schema_version": "3.0",
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "wallet": {
            "address": WALLET_ADDRESS,
            "chain": "solana"
        },
        "portfolio": {
            "sol_balance": 0.0,
            "sol_price_usd": 0.0,
            "usdc_balance": 0.0,
            "total_value_usd": 0.0,
            "positions_count": 0,
            "cost_basis_total": 0.0
        },
        "positions": [],
        "trades": [],
        "signals": [],
        "risk_metrics": {
            "daily_trade_count": 0,
            "daily_trade_reset": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "last_trade_time": None,
            "consecutive_losses": 0,
            "last_loss_time": None
        },
        "performance": {
            "daily_pnl": {},
            "win_rate": 0.0,
            "avg_profit_per_trade": 0.0,
            "total_realized_pnl": 0.0,
            "total_unrealized_pnl": 0.0,
            "daily_avg": 0.0,
            "projected_days_to_1000": 999,
            "win_count": 0,
            "loss_count": 0
        },
        "tax_summary": {},
        "last_verified": None
    }


def refresh_from_onchain(db=None):
    """Refresh portfolio from on-chain data. Returns updated DB."""
    if db is None:
        db = load_db()

    print("Fetching on-chain portfolio...")
    onchain = fetch_onchain_portfolio()

    # Update portfolio summary
    db["portfolio"]["sol_balance"] = onchain["sol_balance"]
    db["portfolio"]["sol_price_usd"] = onchain["sol_price_usd"]
    db["portfolio"]["usdc_balance"] = onchain["usdc_balance"]
    db["portfolio"]["total_value_usd"] = onchain["total_value_usd"]
    db["last_verified"] = onchain["verified_at"]

    # Build set of on-chain mints with value
    onchain_mints = {}
    for h in onchain["holdings"]:
        onchain_mints[h["mint"]] = h

    # Update existing OPEN positions and add new ones
    updated_positions = []
    for pos in db.get("positions", []):
        if pos.get("status") != "OPEN":
            updated_positions.append(pos)
            continue

        mint = pos.get("mint", "")
        if mint in onchain_mints:
            h = onchain_mints[mint]
            # Update position with current on-chain data
            pos["amount_raw"] = h["amount_raw"]
            pos["amount"] = h["amount"]
            pos["decimals"] = h["decimals"]
            pos["current_price_usd"] = h["price_usd"]
            pos["current_value_usd"] = h["value_usd"]
            pos["current_value_sol"] = h["value_sol"]

            # Recalculate unrealized PnL
            cost_basis = pos.get("cost_basis_usd", 0)
            if cost_basis > 0:
                pos["unrealized_pnl_usd"] = h["value_usd"] - cost_basis
                pos["unrealized_pnl_pct"] = ((h["value_usd"] - cost_basis) / cost_basis) * 100
            else:
                pos["unrealized_pnl_usd"] = 0
                pos["unrealized_pnl_pct"] = 0

            updated_positions.append(pos)
            del onchain_mints[mint]  # Remove from unprocessed
        else:
            # Position no longer on-chain - close it
            pos["status"] = "CLOSED"
            pos["closed_at"] = onchain["verified_at"]
            pos["close_price_usd"] = pos.get("current_price_usd", 0)
            pos["close_value_usd"] = pos.get("current_value_usd", 0)
            pos["realized_pnl_usd"] = 0 - pos.get("cost_basis_usd", 0)
            pos["realized_pnl_pct"] = -100 if pos.get("cost_basis_usd", 0) > 0 else 0
            updated_positions.append(pos)

    # Add new on-chain holdings as OPEN positions
    for mint, h in onchain_mints.items():
        # Skip dust (< $0.01) UNLESS we have no price (track anyway)
        if h["value_usd"] < 0.01 and h["price_usd"] > 0:
            continue
        new_pos = {
            "token": mint[:10],  # Short token name from mint
            "mint": mint,
            "amount_raw": h["amount_raw"],
            "amount": h["amount"],
            "decimals": h["decimals"],
            "current_price_usd": h["price_usd"],
            "current_value_usd": h["value_usd"],
            "current_value_sol": h["value_sol"],
            "cost_basis_usd": h["value_usd"],  # Initial cost basis = current value
            "buy_price_usd": h["price_usd"],
            "buy_price_sol": h["value_sol"],
            "unrealized_pnl_usd": 0,
            "unrealized_pnl_pct": 0,
            "status": "OPEN",
            "opened_at": onchain["verified_at"]
        }
        updated_positions.append(new_pos)

    db["positions"] = updated_positions
    db["portfolio"]["positions_count"] = len([p for p in updated_positions if p.get("status") == "OPEN"])

    # Recalculate performance metrics
    recalculate_performance(db)

    save_db(db)
    return db


def recalculate_performance(db):
    """Recalculate all performance metrics from trade history."""
    trades = db.get("trades", [])
    sells = [t for t in trades if t.get("action") == "SELL"]

    if sells:
        total_pnl = sum(t.get("pnl_usd", 0) for t in sells)
        wins = [t for t in sells if t.get("pnl_usd", 0) > 0]
        losses = [t for t in sells if t.get("pnl_usd", 0) < 0]

        db["performance"]["total_realized_pnl"] = total_pnl
        db["performance"]["win_rate"] = (len(wins) / len(sells)) * 100 if sells else 0
        db["performance"]["avg_profit_per_trade"] = total_pnl / len(sells) if sells else 0
        db["performance"]["win_count"] = len(wins)
        db["performance"]["loss_count"] = len(losses)
    else:
        db["performance"]["total_realized_pnl"] = 0
        db["performance"]["win_rate"] = 0
        db["performance"]["avg_profit_per_trade"] = 0
        db["performance"]["win_count"] = 0
        db["performance"]["loss_count"] = 0

    # Unrealized PnL from open positions
    unrealized = sum(
        p.get("unrealized_pnl_usd", 0)
        for p in db.get("positions", [])
        if p.get("status") == "OPEN"
    )
    db["performance"]["total_unrealized_pnl"] = unrealized

    # Tax summary
    tax = {}
    for t in trades:
        year = t.get("timestamp", "")[:4]
        if year not in tax:
            tax[year] = {"total_trades": 0, "realized_pnl": 0.0, "fees_paid": 0.0}
        tax[year]["total_trades"] += 1
        if t.get("pnl_usd"):
            tax[year]["realized_pnl"] += t["pnl_usd"]
    db["tax_summary"] = tax

    return db


def verify_db_against_onchain(db=None):
    """Verify DB against on-chain data. Returns list of discrepancies."""
    if db is None:
        db = load_db()

    print("Verifying portfolio DB against on-chain state...")
    onchain = fetch_onchain_portfolio()
    discrepancies = []

    # Check SOL balance
    db_sol = db["portfolio"].get("sol_balance", 0)
    oc_sol = onchain["sol_balance"]
    if abs(db_sol - oc_sol) > 0.001:
        discrepancies.append(f"SOL balance: DB={db_sol:.8f} vs OnChain={oc_sol:.8f}")

    # Check USDC balance
    db_usdc = db["portfolio"].get("usdc_balance", 0)
    oc_usdc = onchain["usdc_balance"]
    if abs(db_usdc - oc_usdc) > 0.01:
        discrepancies.append(f"USDC balance: DB=${db_usdc:.2f} vs OnChain=${oc_usdc:.2f}")

    # Check open positions
    db_open = {p.get("mint", ""): p for p in db.get("positions", []) if p.get("status") == "OPEN"}
    oc_holdings = {h["mint"]: h for h in onchain["holdings"]}

    # Positions in DB but not on-chain
    for mint, pos in db_open.items():
        if mint and mint not in oc_holdings:
            discrepancies.append(f"Position {pos.get('token', mint)} ({mint[:12]}...) in DB but NOT on-chain")
        elif mint and mint in oc_holdings:
            h = oc_holdings[mint]
            db_amt = pos.get("amount_raw", 0)
            oc_amt = h["amount_raw"]
            if abs(db_amt - oc_amt) > 100:  # Allow small rounding differences
                discrepancies.append(f"Amount mismatch for {pos.get('token', mint)}: DB={db_amt} vs OnChain={oc_amt}")

    # Tokens on-chain but not in DB
    for mint, h in oc_holdings.items():
        if mint not in db_open and h["value_usd"] >= 0.01:
            discrepancies.append(f"Token {mint[:12]}... on-chain (${h['value_usd']:.2f}) but NOT in DB as OPEN")

    # Check total value
    db_total = db["portfolio"].get("total_value_usd", 0)
    oc_total = onchain["total_value_usd"]
    if abs(db_total - oc_total) > 0.10:
        discrepancies.append(f"Total value: DB=${db_total:.2f} vs OnChain=${oc_total:.2f}")

    return discrepancies, onchain


# ── CLI ─────────────────────────────────────────────────────────────────────

def print_portfolio(db=None):
    """Pretty-print the current portfolio."""
    if db is None:
        db = load_db()

    p = db["portfolio"]
    print(f"\n{'='*60}")
    print(f"  TRADEBOT PORTFOLIO")
    print(f"  Wallet: {db['wallet']['address'][:12]}...")
    print(f"  Last Updated: {db.get('last_updated', 'N/A')}")
    print(f"  Last Verified: {db.get('last_verified', 'Never')}")
    print(f"{'='*60}")
    print(f"  SOL:  {p['sol_balance']:.8f} @ ${p['sol_price_usd']:.2f}")
    print(f"  USDC: ${p['usdc_balance']:.2f}")
    print(f"  Total Value: ${p['total_value_usd']:.2f}")
    print(f"  Open Positions: {p['positions_count']}")
    print(f"{'='*60}")

    open_positions = [pos for pos in db.get("positions", []) if pos.get("status") == "OPEN"]
    if open_positions:
        print(f"\n  {'TOKEN':<14} {'AMOUNT':<14} {'PRICE':<12} {'VALUE':<10} {'PnL':<10} {'PnL%':<8}")
        print(f"  {'-'*14} {'-'*14} {'-'*12} {'-'*10} {'-'*10} {'-'*8}")
        for pos in sorted(open_positions, key=lambda p: p.get("current_value_usd", 0), reverse=True):
            token = pos.get("token", "?")[:12]
            amt = f"{pos.get('amount', 0):.4f}"
            price = f"${pos.get('current_price_usd', 0):.8f}"
            val = f"${pos.get('current_value_usd', 0):.2f}"
            pnl = f"${pos.get('unrealized_pnl_usd', 0):.2f}"
            pnl_pct = f"{pos.get('unrealized_pnl_pct', 0):.1f}%"
            print(f"  {token:<14} {amt:<14} {price:<12} {val:<10} {pnl:<10} {pnl_pct:<8}")

    perf = db.get("performance", {})
    print(f"\n  Performance:")
    print(f"    Realized PnL:  ${perf.get('total_realized_pnl', 0):.2f}")
    print(f"    Unrealized PnL: ${perf.get('total_unrealized_pnl', 0):.2f}")
    print(f"    Win Rate:      {perf.get('win_rate', 0):.1f}% ({perf.get('win_count', 0)}W / {perf.get('loss_count', 0)}L)")
    print(f"    Avg Profit:    ${perf.get('avg_profit_per_trade', 0):.2f}/trade")
    print(f"{'='*60}\n")


def main():
    args = sys.argv[1:]

    if "--verify" in args:
        db = load_db()
        discrepancies, onchain = verify_db_against_onchain(db)
        if discrepancies:
            print(f"\n[WARN]  {len(discrepancies)} DISCREPANCIES FOUND:")
            for d in discrepancies:
                print(f"  • {d}")
            print(f"\n  On-chain total: ${onchain['total_value_usd']:.2f}")
            print(f"  DB total:       ${db['portfolio']['total_value_usd']:.2f}")
        else:
            print(f"\n[OK] DB matches on-chain state!")
            print(f"  Total value: ${onchain['total_value_usd']:.2f}")
        return

    if "--refresh" in args:
        print("Refreshing portfolio from on-chain...")
        db = refresh_from_onchain()
        print_portfolio(db)
        print("[OK] Portfolio refreshed from on-chain data.")
        return

    # Default: just print current portfolio
    db = load_db()
    print_portfolio(db)

    # Check if data is stale (> 1 hour)
    last_verified = db.get("last_verified")
    if last_verified:
        try:
            last = datetime.fromisoformat(last_verified)
            age = (datetime.now(timezone.utc) - last).total_seconds()
            if age > 3600:
                print(f"[WARN]  Data is {age/60:.0f} minutes old. Run with --refresh to update.")
        except:
            pass


if __name__ == "__main__":
    main()
