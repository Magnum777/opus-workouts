#!/usr/bin/env python3
"""
TradeBot V2 Scout
Research-driven portfolio scanning with risk checks
"""

import json
import os
import sys
import requests
from datetime import datetime, timezone

# Import V2 modules
sys.path.insert(0, os.path.dirname(__file__))
import portfolio_db_v2 as pdb
from risk_manager import check_stop_loss_take_profit, get_position
from risk_manager import update_trailing_stop, get_trailing_stop_info
from risk_manager import STOP_LOSS_PCT, TAKE_PROFIT_PCT, TRIM_PCT

# Solana imports
from solana.rpc.api import Client
from solders.keypair import Keypair

# Wallet
PRIVATE_KEY = bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d")
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client("https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887")

# Constants
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
TOKEN2022_PROGRAM = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"

KNOWN_TOKENS = {
    "PUMP": "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn",
    "FARTCOIN": "9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump",
    "PENGU": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv",
    "TRUMP": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
    "WIF": "EKpQGSJtjfaX4B7qfz2aWJ2wSrnKZUEJkE4B6gFuy1r",
    "JUP": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "ORCA": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",
    "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
    "HANTA": "2tXpgu2DLTsPUf9zFmuZmA4xrYxXKBTpVq9wAM7hzs9y"
}

MINT_TO_NAME = {v: k for k, v in KNOWN_TOKENS.items()}

def get_sol_balance():
    """Get SOL balance from blockchain"""
    try:
        return CLIENT.get_balance(WALLET.pubkey()).value / 1e9
    except:
        return 0

def get_usdc_balance():
    """Get USDC balance from blockchain"""
    try:
        helius_url = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
        data = {
            "jsonrpc": "2.0", "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                str(WALLET.pubkey()),
                {"mint": USDC},
                {"encoding": "jsonParsed"}
            ]
        }
        resp = requests.post(helius_url, json=data, headers={"Content-Type": "application/json"}, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            accounts = result.get("result", {}).get("value", [])
            if accounts:
                return float(accounts[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"] or 0)
    except:
        pass
    return 0

def get_jupiter_price(mint, decimals=None):
    """Get token price via Jupiter. Returns price per 1 full token in USD.
    Respects shared 429 cooldown."""
    # Check shared 429 cooldown
    _429 = os.path.join(os.path.dirname(__file__), ".jupiter_429_cooldown.json")
    try:
        with open(_429) as _f:
            _d = json.load(_f)
        if _d.get("expires_at", 0) > __import__('time').time():
            return 0
    except:
        pass
    try:
        if decimals is None:
            decimals = 9 if mint == SOL_MINT else 6
        amount = 10 ** decimals
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount={amount}&slippage=1",
            timeout=8
        )
        if r.status_code == 200:
            return float(r.json()["outAmount"]) / 1e6
        elif r.status_code == 429:
            with open(_429, "w") as _f:
                json.dump({"expires_at": __import__('time').time() + 600}, _f)
    except:
        pass
    return 0

def get_all_holdings():
    """Get token holdings from blockchain"""
    holdings = {}  # mint -> {"raw": int, "amount": float, "decimals": int}
    helius_url = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
    
    for prog in ["TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA", TOKEN2022_PROGRAM]:
        try:
            data = {
                "jsonrpc": "2.0", "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [str(WALLET.pubkey()), {"programId": prog}, {"encoding": "jsonParsed"}]
            }
            resp = requests.post(helius_url, json=data, headers={"Content-Type": "application/json"}, timeout=15)
            if resp.status_code == 200:
                result = resp.json()
                if "result" in result and result["result"]:
                    for account in result["result"]["value"]:
                        info = account["account"]["data"]["parsed"]["info"]
                        mint = info["mint"]
                        ta = info["tokenAmount"]
                        raw = int(ta["amount"])
                        ui_amount = float(ta.get("uiAmount") or 0)
                        decimals = int(ta.get("decimals") or 0)
                        if raw > 0 and mint != SOL_MINT:
                            holdings[mint] = {"raw": raw, "amount": ui_amount, "decimals": decimals}
        except:
            pass
    return holdings

def scan_for_signals():
    """Scan for buy/sell signals with research integration"""
    db = pdb.load_db()
    sol_price = get_jupiter_price(SOL_MINT) or 84
    sol_balance = get_sol_balance()
    
    signals = []
    
    # Check open positions for sell signals
    for pos in db.get("positions", []):
        if pos.get("status") != "OPEN":
            continue
        
        token = pos["token"]
        mint = pos.get("mint", KNOWN_TOKENS.get(token, ""))
        
        # Get current price (per token in USDC)
        pos_decimals = pos.get("decimals", 6 if mint != SOL_MINT else 9)
        current_price_per_token = get_jupiter_price(mint, decimals=pos_decimals)
        if current_price_per_token <= 0:
            continue
        
        # Get position details
        amount_raw = pos.get("amount_raw", 0)
        if amount_raw <= 0:
            continue
        
        # Calculate current total value
        current_value_usd = current_price_per_token * amount_raw / 1e6
        
        # Get cost basis
        cost_basis_usd = pos.get("cost_basis_usd", pos.get("buy_price_usd", 0))
        if cost_basis_usd <= 0:
            continue
        
        # Calculate P&L percentage
        pnl_usd = current_value_usd - cost_basis_usd
        pnl_pct = (pnl_usd / cost_basis_usd) if cost_basis_usd > 0 else 0
        
        # Update position with current values
        pos["current_price_usd"] = current_price_per_token
        pos["current_value_usd"] = current_value_usd
        pos["unrealized_pnl_usd"] = pnl_usd
        pos["unrealized_pnl_pct"] = pnl_pct * 100
        
        # Update trailing stop high watermark
        pos["current_price_usd"] = current_price_per_token
        update_trailing_stop(pos, current_price_per_token)
        
        # Check trailing stop first
        trail_info = get_trailing_stop_info(pos)
        if trail_info and trail_info.get("active"):
            trail_stop = trail_info["trail_stop_price"]
            if current_price_per_token <= trail_stop:
                signals.append({
                    "token": token,
                    "mint": mint,
                    "action": "SELL",
                    "reason": "TRAILING_STOP",
                    "pnl_pct": pnl_pct * 100,
                    "current_value_usd": current_value_usd
                })
                continue
        
        # Stop loss at -8% (hard floor)
        if pnl_pct <= STOP_LOSS_PCT:
            signals.append({
                "token": token,
                "mint": mint,
                "action": "SELL",
                "reason": "STOP_LOSS",
                "pnl_pct": pnl_pct * 100,
                "current_value_usd": current_value_usd
            })
        # Take profit at +25%
        elif pnl_pct >= TAKE_PROFIT_PCT:
            signals.append({
                "token": token,
                "mint": mint,
                "action": "SELL",
                "reason": "TAKE_PROFIT",
                "pnl_pct": pnl_pct * 100,
                "current_price": current_price_per_token,
                "current_value_usd": pos.get("current_value_usd", 0)
            })
        # Trim at +12%
        elif pnl_pct >= TRIM_PCT:
            signals.append({
                "token": token,
                "mint": mint,
                "action": "TRIM",
                "reason": "TRIM_THRESHOLD",
                "pnl_pct": pnl_pct * 100,
                "current_value_usd": current_value_usd
            })
    
    return signals

def get_latest_research_guidance():
    """Read latest research brief for scout context"""
    research_dir = os.path.join(os.path.dirname(__file__), "research")
    try:
        files = sorted([f for f in os.listdir(research_dir) if f.endswith('.md')], reverse=True)
        if not files:
            return None
        latest = os.path.join(research_dir, files[0])
        with open(latest, 'r') as f:
            content = f.read()
        # Extract Scout Guidance section
        if "## Scout Guidance" in content:
            section = content.split("## Scout Guidance")[1].split("##")[0].strip()
            return section
        return None
    except:
        return None


def main():
    """Main scout routine"""
    print(f"[{datetime.now(timezone.utc).isoformat()}] === V2 SCOUT ===")
    print(f"Wallet: {WALLET.pubkey()}")
    
    # Load research context
    research = get_latest_research_guidance()
    if research:
        print(f"\n[RESEARCH CONTEXT] Latest briefing:")
        for line in research.split('\n')[:8]:  # First 8 lines
            if line.strip():
                print(f"  {line.strip()}")
    else:
        print(f"\n[RESEARCH CONTEXT] No briefing available")
    
    # Get blockchain data
    sol_balance = get_sol_balance()
    sol_price = get_jupiter_price(SOL_MINT) or 84
    holdings = get_all_holdings()
    usdc_balance = get_usdc_balance()
    
    print(f"SOL Balance: {sol_balance:.4f} SOL (${sol_balance * sol_price:.2f})")
    print(f"USDC Balance: ${usdc_balance:.2f}")
    print(f"Token Holdings: {len(holdings)} tokens")
    
    # Add USDC to holdings for sync (DB will track as cash, not trade position)
    holdings_list = []
    for mint, h in holdings.items():
        token = MINT_TO_NAME.get(mint, mint[:10])
        token_decimals = h["decimals"]
        price = get_jupiter_price(mint, decimals=token_decimals)  # USDC per token (6 decimals)
        ui_amount = h["amount"]
        raw = h["raw"]
        decimals = token_decimals
        value_usd = ui_amount * price if price > 0 else 0
        value_sol = value_usd / sol_price if sol_price > 0 else 0
        
        holdings_list.append({
            "token": token,
            "mint": mint,
            "amount": ui_amount,
            "amount_raw": raw,
            "decimals": decimals,
            "value_usd": value_usd,
            "value_sol": value_sol
        })
        print(f"  {token}: {ui_amount:,.4f} (${value_usd:.2f})")
    
    # Sync to V2 database
    pdb.sync_from_blockchain(holdings_list, sol_balance, sol_price)
    print(f"[V2 DB SYNC] Complete")
    
    # Scan for signals
    signals = scan_for_signals()
    
    if signals:
        print(f"\n[SIGNALS] {len(signals)} found:")
        for sig in signals:
            print(f"  {sig['action']} {sig['token']}: {sig['reason']} ({sig['pnl_pct']:+.1f}%)")
        
        # Write signals to queue for executor
        queue_path = os.path.join(os.path.dirname(__file__), "trading-queue.json")
        try:
            queue = {"pending": signals, "executed": []}
            with open(queue_path, "w") as f:
                json.dump(queue, f, indent=2)
            print(f"[QUEUE] {len(signals)} signal(s) written to trading-queue.json")
        except Exception as e:
            print(f"[QUEUE] Failed to write signals: {e}")
    else:
        print("\n[SIGNALS] No signals")
    
    # Show portfolio summary
    db = pdb.load_db()
    perf = db.get("performance", {})
    print(f"\n[PERFORMANCE]")
    print(f"  Total Value: ${db['portfolio']['total_value_usd']:.2f}")
    print(f"  Realized P&L: ${perf.get('total_realized_pnl', 0):.2f}")
    print(f"  Unrealized P&L: ${perf.get('total_unrealized_pnl', 0):.2f}")
    print(f"  Days to $1000: ~{perf.get('projected_days_to_1000', 999):.0f}")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
