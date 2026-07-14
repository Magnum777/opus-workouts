#!/usr/bin/env python3
"""
TradeBot-Nova Scout Module - LIVE SIGNAL DETECTION
Reads ACTUAL blockchain holdings (like old script) - NOT just positions.json
"""

import json
import os
import requests
from datetime import datetime, timezone
from solana.rpc.api import Client
from solders.keypair import Keypair

# Import unified portfolio database
import portfolio_db as pdb

# Wallet configuration - MUST match executor and old script
PRIVATE_KEY = bytes.fromhex(os.environ.get("TRADING_BOT_PRIVATE_KEY", ""))
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client(os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE"))

# Trading parameters
TAKE_PROFIT_PCT = 1.0     # 1% take profit
STOP_LOSS_PCT = -1.0      # 1% stop loss
MAX_POSITIONS = 6
COOLDOWN_SCANS = 6
MIN_LIQUIDITY_USD = 50000

USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"
TOKEN2022_PROGRAM = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"

KNOWN_TOKENS = {
    "PUMP": {"mint": "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn", "priority": 3},
    "FART": {"mint": "9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump", "priority": 2},
    "PENGU": {"mint": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv", "priority": 3},
    "TRUMP": {"mint": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN", "priority": 2},
    "GIGA": {"mint": "63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9", "priority": 2},
    "BONK": {"mint": "DezXAZ8z7PnrnRJjz3wXBoaggixuT4Byifb9T8qbtPas", "priority": 3},
    "WIF": {"mint": "85VBFQZC9TZkfaptBWqv14ALD9fJNUKtWA41kh69teRP", "priority": 3},
    "POPCAT": {"mint": "7xKXtg2CW87d97TXJSDpbD5jBkheotQbM2MyWGkErQgB", "priority": 3},
    "MOODENG": {"mint": "Moodeng5zS4Zs2Dq3bFJBjtFAY4xqKc9w1EqR4XP2S3Dq", "priority": 2},
    "GOAT": {"mint": "CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump", "priority": 2},
    "HONK": {"mint": "3ag1M9QJK91mXJtVvHaKq7hWwWQzw6q4oVZunLLAoqNZ", "priority": 1},
    "PIPPIN": {"mint": "GScX7cE5PxLkGrSjK3xwRJrYwKpV7MEmFgH2yFrhQGqm", "priority": 1},
}

# Reverse lookup: mint -> name
MINT_TO_NAME = {v["mint"]: k for k, v in KNOWN_TOKENS.items()}

QUEUE_FILE = "trading-queue.json"
LOG_FILE = "scout-log.json"
POSITIONS_FILE = "positions.json"
COOLDOWN_FILE = "trade-cooldowns.json"
RESEARCH_FILE = "research-cache.json"  # Portfolio research data
SIGNALS_FILE = "portfolio-signals.json"  # Research-generated signals
STATE_FILE = "positions_enforced.json"  # For reading buy prices from old script

def load_json(filepath, default=None):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            try:
                return json.load(f)
            except:
                return default if default is not None else {}
    return default if default is not None else {}

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def get_sol_balance():
    """Get actual SOL balance from blockchain"""
    try:
        return CLIENT.get_balance(WALLET.pubkey()).value / 1e9
    except:
        return 0

def get_all_holdings():
    """Get ALL token holdings from BOTH Token programs - FROM BLOCKCHAIN via Helius"""
    holdings = {}
    # Use Helius RPC instead of public API to avoid rate limits
    helius_url = os.environ.get("HELIUS_RPC_URL", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY_HERE")
    
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
                        mint = account["account"]["data"]["parsed"]["info"]["mint"]
                        amount = int(account["account"]["data"]["parsed"]["info"]["tokenAmount"]["amount"])
                        if amount > 0 and mint != SOL_MINT:
                            holdings[mint] = amount
            elif resp.status_code == 429:
                print(f"    ⚠️  Rate limited on {prog[:20]}...")
        except Exception as e:
            print(f"    ⚠️  Error reading {prog[:20]}: {e}")
    return holdings

def get_jupiter_price(mint):
    """Get token price via Jupiter"""
    try:
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount=1000000&slippage=1",
            timeout=8
        )
        if r.status_code == 200:
            return float(r.json()["outAmount"]) / 1e6
    except:
        pass
    return 0

def load_cooldowns():
    return load_json(COOLDOWN_FILE, {})

def save_cooldowns(cooldowns):
    save_json(COOLDOWN_FILE, cooldowns)

def load_queue():
    return load_json(QUEUE_FILE, {"pending": [], "executed": [], "rejected": []})

def save_queue(queue):
    save_json(QUEUE_FILE, queue)

def log_event(event_type, data):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": event_type,
        "data": data
    }
    logs = load_json(LOG_FILE, [])
    logs.append(log_entry)
    logs = logs[-1000:]
    save_json(LOG_FILE, logs)

def get_buy_price_from_state(mint, current_value_sol):
    """Get buy price from old script state, but validate it's reasonable"""
    state = load_json(STATE_FILE, {})
    buy_price = state.get(f"{mint}_buy_price", 0)
    
    # Validate: buy price should be within 10x of current value (not 1000x)
    if buy_price > 0 and current_value_sol > 0:
        ratio = current_value_sol / buy_price
        if ratio > 100:  # If ratio is insane (like 2000x), ignore state
            print(f"    [WARN] Buy price {buy_price:.4f} SOL seems wrong vs current {current_value_sol:.4f} SOL, using break-even")
            return current_value_sol  # Break-even
    
    if buy_price > 0:
        return buy_price
    return current_value_sol  # Break-even if no history

def sync_positions_with_holdings(holdings):
    """Sync positions.json with ACTUAL blockchain holdings"""
    positions = []
    sol_price = get_jupiter_price(SOL_MINT) or 84
    
    for mint, amount_raw in holdings.items():
        token_name = MINT_TO_NAME.get(mint, mint[:10])
        
        price_usd = get_jupiter_price(mint)
        value_usd = amount_raw * price_usd / 1e6 if price_usd > 0 else 0
        value_sol = value_usd / sol_price if sol_price > 0 else 0
        
        # Get buy price from state file if available
        buy_price_sol = get_buy_price_from_state(mint, value_sol)
        
        position = {
            "token": token_name,
            "mint": mint,
            "amount_raw": amount_raw,
            "current_value_usd": value_usd,
            "current_value_sol": value_sol,
            "buy_price_usd": value_usd * (buy_price_sol / value_sol) if value_sol > 0 else value_usd,
            "buy_price_sol": buy_price_sol,
            "status": "OPEN"
        }
        positions.append(position)
        print(f"    [POS] {token_name}: {value_sol:.4f} SOL (${value_usd:.2f}) | Buy: {buy_price_sol:.4f} SOL")
    
    save_json(POSITIONS_FILE, {"positions": positions})
    return positions

def scan_positions_from_blockchain():
    """Scan ACTUAL blockchain holdings for sell signals"""
    holdings = get_all_holdings()
    positions = sync_positions_with_holdings(holdings)
    
    cooldowns = load_cooldowns()
    signals = []
    
    print(f"  Actual holdings: {len(positions)} tokens")
    
    for position in positions:
        current_value_sol = position.get("current_value_sol", 0)
        buy_price_sol = position.get("buy_price_sol", 0)
        token = position.get("token", "UNKNOWN")
        mint = position.get("mint", "")
        
        if token in cooldowns and cooldowns[token] > 0:
            continue
        
        if buy_price_sol > 0:
            pnl_pct = ((current_value_sol - buy_price_sol) / buy_price_sol) * 100
            
            if pnl_pct >= TAKE_PROFIT_PCT:
                signals.append({
                    "token": token,
                    "action": "SELL",
                    "reason": "TAKE_PROFIT",
                    "pnl_pct": round(pnl_pct, 2),
                    "urgency": "HIGH",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "mint": mint,
                    "amount_raw": position.get("amount_raw", 0),
                    "current_value_sol": current_value_sol,
                    "buy_price_sol": buy_price_sol
                })
                print(f"    [SELL] {token} +{pnl_pct:.1f}%")
            elif pnl_pct <= STOP_LOSS_PCT:
                signals.append({
                    "token": token,
                    "action": "SELL",
                    "reason": "STOP_LOSS",
                    "pnl_pct": round(pnl_pct, 2),
                    "urgency": "HIGH",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "mint": mint,
                    "amount_raw": position.get("amount_raw", 0),
                    "current_value_sol": current_value_sol,
                    "buy_price_sol": buy_price_sol
                })
                print(f"    [STOP] {token} {pnl_pct:.1f}%")
    
    return signals

def scan_for_buys(holdings):
    """Scan for buy opportunities"""
    if len(holdings) >= MAX_POSITIONS:
        return []
    
    cooldowns = load_cooldowns()
    buy_signals = []
    
    for name, info in KNOWN_TOKENS.items():
        mint = info.get("mint", "")
        priority = info.get("priority", 1)
        
        if mint in holdings:
            continue
        
        if name in cooldowns and cooldowns[name] > 0:
            continue
        
        price = get_jupiter_price(mint)
        if price > 0:
            buy_signals.append({
                "token": name,
                "action": "BUY",
                "mint": mint,
                "price_usd": price,
                "priority": priority,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
    
    buy_signals.sort(key=lambda x: x["priority"], reverse=True)
    return buy_signals[:2]

def decrement_cooldowns():
    cooldowns = load_cooldowns()
    updated = {}
    for token, count in cooldowns.items():
        if count > 0:
            updated[token] = count - 1
    save_cooldowns(updated)

def queue_trades(signals):
    queue = load_queue()
    
    for signal in signals:
        existing = [t for t in queue["pending"] if t["token"] == signal["token"]]
        if not existing:
            queue["pending"].append(signal)
            log_event("SIGNAL_QUEUED", signal)
    
    save_queue(queue)
    return len(signals)

def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] === TRADEBOT SCOUT ===")
    print(f"Wallet: {WALLET.pubkey()}")
    
    sol_balance = get_sol_balance()
    print(f"SOL Balance: {sol_balance:.4f} SOL")
    
    decrement_cooldowns()
    
    holdings = get_all_holdings()
    print(f"Token Holdings: {len(holdings)} tokens")
    
    # Calculate total portfolio value
    sol_price = get_jupiter_price(SOL_MINT) or 84
    total_sol_value = sol_balance * sol_price
    print(f"SOL Value: ${total_sol_value:.2f} (@ ${sol_price:.2f}/SOL)")
    
    sell_signals = scan_positions_from_blockchain()
    buy_signals = scan_for_buys(holdings)
    
    # Get positions for value calculation (already synced in scan_positions)
    positions_data = load_json(POSITIONS_FILE, {"positions": []})
    positions = positions_data.get("positions", [])
    
    # Calculate token values
    token_total_usd = 0
    for position in positions:
        token_total_usd += position.get("current_value_usd", 0)
    
    total_portfolio = total_sol_value + token_total_usd
    print(f"Token Value: ${token_total_usd:.2f}")
    print(f"TOTAL PORTFOLIO: ${total_portfolio:.2f}")
    
    # SYNC TO UNIFIED PORTFOLIO DATABASE
    # Convert positions to holdings format for sync
    holdings_list = []
    for pos in positions:
        holdings_list.append({
            "token": pos["token"],
            "mint": pos["mint"],
            "amount": pos["amount_raw"],
            "value_usd": pos["current_value_usd"],
            "value_sol": pos["current_value_sol"]
        })
    pdb.sync_from_blockchain(holdings_list, sol_balance, sol_price)
    print(f"[DB SYNC] Portfolio synced to unified database")
    
    # Load and display research signals
    research_data = load_json(RESEARCH_FILE, {})
    if research_data:
        print(f"\n[RESEARCH] Last Update: {research_data.get('timestamp', 'unknown')}")
        analyses = research_data.get('analyses', [])
        if analyses:
            avg_conf = sum(a.get('confidence', 50) for a in analyses) / len(analyses)
            print(f"[RESEARCH] Avg Confidence: {avg_conf:.0f}/100")
            for a in analyses[:3]:  # Show top 3
                print(f"  {a['token']}: {a['recommendation']} ({a['confidence']}/100)")
    
    all_signals = sell_signals + buy_signals
    
    if all_signals:
        count = queue_trades(all_signals)
        print(f"Signals Queued: {count} ({len(sell_signals)} sell, {len(buy_signals)} buy)")
    else:
        print("No trade signals")
    
    cooldowns = load_cooldowns()
    active = [k for k, v in cooldowns.items() if v > 0]
    if active:
        print(f"Cooldowns Active: {active}")
    
    log_event("SCAN_COMPLETE", {
        "portfolio_usd": total_portfolio,
        "sol_balance": sol_balance,
        "token_value_usd": token_total_usd,
        "holdings_count": len(holdings),
        "sell_signals": len(sell_signals),
        "buy_signals": len(buy_signals)
    })
    
    print(f"Queue Status: {len(load_queue()['pending'])} pending")
    print("=" * 40)

if __name__ == "__main__":
    main()
