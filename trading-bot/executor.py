#!/usr/bin/env python3
"""
Nova Trading Executor - Coinbase Advanced Trade
Takes LLM decision, shows to user for confirmation, executes on Coinbase
WITH PROPER RISK MANAGEMENT
"""

import json
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from datetime import datetime
from pathlib import Path

# Load .env file
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

STATE_PATH = "trading-bot/state.json"
DECISION_PATH = "trading-bot/latest_decision.json"
TRADES_LOG_PATH = "trading-bot/trades.json"

PRODUCT_ID = "ETH-USD"

COINBASE_API_KEY = os.getenv("COINBASE_API_KEY", "")
COINBASE_API_SECRET = os.getenv("COINBASE_API_SECRET", "")


def load_state():
    with open(STATE_PATH, "r") as f:
        return json.load(f)


def load_latest_decision():
    if not os.path.exists(DECISION_PATH):
        return None
    with open(DECISION_PATH, "r") as f:
        return json.load(f)


def get_eth_price():
    if not COINBASE_API_KEY:
        return None
    
    import requests
    url = "https://api.coinbase.com/v2/prices/ETH-USD/spot"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return float(data["data"]["amount"])
    except:
        return None


def place_limit_order(side, size_eth, limit_price, stop_price=None):
    """Place a limit order with optional stop-loss"""
    if not COINBASE_API_KEY:
        return None
    
    import requests
    import base64
    import hmac
    import hashlib
    import time
    
    timestamp = str(int(time.time()))
    method = "POST"
    path = "/api/v3/brokerage/orders"
    
    # Build order config
    order_config = {
        "limit_limit_gtc": {
            "base_size": str(size_eth),
            "limit_price": str(limit_price),
            "post_only": True  # Don't cross the spread
        }
    }
    
    # Add stop loss if provided
    if stop_price and side.upper() == "BUY":
        order_config["stop_loss"] = {
            "stop_price": str(stop_price),
            "stop_direction": "DOWN"
        }
    
    body = json.dumps({
        "client_order_id": f"nova_{int(time.time())}",
        "product_id": PRODUCT_ID,
        "side": side.upper(),
        "order_configuration": order_config
    })
    
    message = timestamp + method + path + body
    signature = base64.b64encode(
        hmac.new(
            COINBASE_API_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    ).decode()
    
    headers = {
        "CB-ACCESS-KEY": COINBASE_API_KEY,
        "CB-ACCESS-SIGN": signature,
        "CB-ACCESS-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }
    
    url = f"https://api.coinbase.com{path}"
    try:
        resp = requests.post(url, headers=headers, data=body, timeout=30)
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    print("=" * 60)
    print("NOVA TRADING EXECUTOR - WITH RISK MANAGEMENT")
    print("=" * 60)
    
    print(f"\n[API Status]")
    if COINBASE_API_KEY:
        print(f"   API Key: {COINBASE_API_KEY[:20]}...")
    else:
        print("   [!] No API key found")
    
    state = load_state()
    
    # Get current ETH price
    current_price = get_eth_price()
    if not current_price:
        current_price = state["price_usd"]
        print(f"\n   Using cached price: ${current_price}")
    else:
        print(f"\n   Current ETH price: ${current_price}")
    
    config = state.get("config", {})
    
    print(f"\n[Current State]")
    print(f"   Capital: ${state['capital_usd']:.2f}")
    print(f"   ETH Price: ${current_price:.2f}")
    print(f"   Position: {state['position']['size_eth']:.6f} ETH")
    print(f"   Avg Entry: ${state['position'].get('avg_entry_usd', 0):.2f}")
    print(f"   Mode: {config.get('mode', 'paper')}")
    
    # Risk settings
    stop_pct = float(config.get("stop_loss_pct", 0.05))
    tp_pct = float(config.get("take_profit_pct", 0.10))
    
    print(f"\n[Risk Settings]")
    print(f"   Stop Loss: {stop_pct*100:.0f}%")
    print(f"   Take Profit: {tp_pct*100:.0f}%")
    
    decision = load_latest_decision()
    
    if not decision:
        print("\n[!] No decision. Run trading_loop.py first.")
        return
    
    action = decision.get("action", "HOLD")
    size = float(decision.get("size_eth", 0))
    
    print(f"\n[LLM Decision]")
    print(f"   Action: {action}")
    print(f"   Size: {size:.6f} ETH")
    print(f"   Reason: {decision.get('reason', 'N/A')}")
    
    if action == "HOLD":
        print("\n[HOLD - no action needed]")
        return
    
    # Calculate prices
    value = size * current_price
    
    # Set limit price (0.5% better than current for buying, worse for selling)
    if action.upper() == "BUY":
        limit_price = current_price * 0.995  # 0.5% below current (safer entry)
        stop_price = current_price * (1 - stop_pct)  # Stop loss 5% below entry
    else:  # SELL
        limit_price = current_price * 1.005  # 0.5% above current
        stop_price = None  # No stop needed when taking profit
    
    print(f"\n[Order with Risk Management]")
    print(f"   Type: LIMIT ORDER (not market)")
    print(f"   Limit Price: ${limit_price:.2f}")
    print(f"   Stop Loss: ${stop_price:.2f}" if stop_price else "   Stop Loss: None")
    print(f"   Est. Value: ${value:.2f}")
    
    # Show risk
    if action.upper() == "BUY":
        potential_loss = value * stop_pct
        potential_gain = value * tp_pct
        print(f"\n[Risk Analysis]")
        print(f"   Max Loss: ${potential_loss:.2f} ({stop_pct*100:.0f}%)")
        print(f"   Target Gain: ${potential_gain:.2f} ({tp_pct*100:.0f}%)")
        print(f"   Risk/Reward: 1:{tp_pct/stop_pct:.1f}")
    
    print("\n" + "=" * 60)
    print("CONFIRMATION REQUIRED")
    print("=" * 60)
    print(f"\nExecute this {action} order with risk controls? (yes/no): ", end="")
    response = input().strip().lower()
    
    if response != "yes":
        print("\n[!] Cancelled.")
        return
    
    print(f"\n[*] Placing {action} limit order...")
    
    result = place_limit_order(action, size, limit_price, stop_price)
    
    if result:
        print(f"\n[+] ORDER PLACED!")
        print(f"    Response: {json.dumps(result, indent=2)[:800]}")
    else:
        print("\n[!] Order failed")


if __name__ == "__main__":
    main()
