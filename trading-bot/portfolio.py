#!/usr/bin/env python3
"""
portfolio.py — Single source of truth for TradeBot portfolio data.

On every call, queries on-chain balances for BOTH Token program AND Token-2022
program, gets prices from DexScreener (fallback Jupiter), and returns a clean
portfolio dict. This is the REPORTING layer — the bot's internal trading logic
still uses portfolio.db.json for position tracking.

Usage:
    from portfolio import get_portfolio
    p = get_portfolio()
    print(p["total_value_usd"])
"""

import json
import os
import time
import requests
from datetime import datetime, timezone

# ── Configuration ──────────────────────────────────────────────────────────

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
        resp = requests.post(rpc_url, json=payload,
                             headers={"Content-Type": "application/json"},
                             timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if "error" in data:
                return None, data["error"]
            return data.get("result"), None
        return None, f"HTTP {resp.status_code}"
    except Exception as e:
        return None, str(e)


def _rpc_call_helius(method, params=None):
    """Make a JSON-RPC call to Helius (for getTokenAccountsByOwner)."""
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
    Returns list of {mint, amount, decimals, amount_raw, program} dicts."""
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

def get_portfolio():
    """Fetch complete portfolio from on-chain. Returns a clean dict.

    Returns:
        {
            "sol_balance": float,
            "sol_price_usd": float,
            "usdc_balance": float,
            "total_value_usd": float,
            "positions": [
                {
                    "mint": str,
                    "amount": float,
                    "amount_raw": int,
                    "decimals": int,
                    "price_usd": float,
                    "value_usd": float,
                    "program": str,
                    "has_price_feed": bool
                }
            ],
            "last_verified": str (ISO timestamp)
        }
    """
    sol_balance = get_sol_balance()
    sol_price = get_sol_price()
    all_tokens = get_all_token_balances()

    positions = []
    usdc_balance = 0.0
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
        has_price_feed = price > 0
        value_usd = amount * price

        positions.append({
            "mint": mint,
            "amount_raw": token["amount_raw"],
            "amount": amount,
            "decimals": decimals,
            "price_usd": price,
            "value_usd": value_usd,
            "program": token["program"],
            "has_price_feed": has_price_feed
        })
        total_value += value_usd

    return {
        "sol_balance": sol_balance,
        "sol_price_usd": sol_price,
        "usdc_balance": usdc_balance,
        "total_value_usd": total_value,
        "positions": positions,
        "last_verified": datetime.now(timezone.utc).isoformat()
    }


def format_portfolio_report(p=None):
    """Format portfolio as a human-readable string (Discord-friendly)."""
    if p is None:
        p = get_portfolio()

    lines = []
    lines.append(f"**TradeBot Portfolio**")
    lines.append(f"SOL: {p['sol_balance']:.4f} @ ${p['sol_price_usd']:.2f}")
    lines.append(f"USDC: ${p['usdc_balance']:.2f}")
    lines.append(f"**Total: ${p['total_value_usd']:.2f}**")

    # Open positions (non-stablecoin, non-zero value)
    open_positions = [pos for pos in p["positions"]
                      if pos["value_usd"] >= 0.01]
    if open_positions:
        lines.append(f"\n**Positions ({len(open_positions)}):**")
        for pos in sorted(open_positions,
                          key=lambda x: x["value_usd"], reverse=True):
            mint_short = pos["mint"][:10]
            if pos["has_price_feed"]:
                lines.append(
                    f"• {mint_short}: {pos['amount']:,.2f} @ ${pos['price_usd']:.8f} = ${pos['value_usd']:.2f}"
                )
            else:
                lines.append(
                    f"• {mint_short}: {pos['amount']:,.2f} (no price feed) = $0.00"
                )

    # Tokens with no price feed
    no_price = [pos for pos in p["positions"]
                if not pos["has_price_feed"] and pos["value_usd"] < 0.01]
    if no_price:
        lines.append(f"\n*{len(no_price)} token(s) without price feed (tracked as $0)*")

    lines.append(f"\n_Last verified: {p['last_verified']}_")
    return "\n".join(lines)


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if "--json" in sys.argv:
        p = get_portfolio()
        print(json.dumps(p, indent=2, default=str))
    else:
        p = get_portfolio()
        print(format_portfolio_report(p))
