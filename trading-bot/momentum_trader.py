#!/usr/bin/env python3
"""
Momentum-Based Swing Trader
Analyzes price history to capture multiple small swings (3-5%)
instead of waiting for large 10% moves.
"""

import json
import os
import sys
import requests
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))
import portfolio_db_v2 as pdb

# Solana
from solana.rpc.api import Client
from solders.keypair import Keypair

PRIVATE_KEY = bytes.fromhex("edd8b3aa4b029112f8d55c8d5daa344bdd0b105c2809c4ddb9f1908625b0cdee5cd4608fc059d034abd87d3724de879417cc23eb7a9fe40d607de6d991cb473d")
WALLET = Keypair.from_bytes(PRIVATE_KEY)
CLIENT = Client("https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887")

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# Swing trading parameters
SWING_PROFIT_TARGET = 0.05      # Take 5% profit (not 10%)
SWING_STOP_LOSS = -0.03         # Cut at -3% (tighter than -5%)
MOMENTUM_WINDOW_MINUTES = 15    # Look at last 15 min of price action
MIN_SWING_SIZE = 0.02           # Need at least 2% move to consider it a swing
TRAILING_STOP_PCT = 0.02        # 2% trailing stop after 3% profit

PRICE_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "price_history.json")

def load_price_history():
    """Load historical price data"""
    if not os.path.exists(PRICE_HISTORY_FILE):
        return {}
    with open(PRICE_HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_price_history(history):
    """Save price history"""
    with open(PRICE_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2, default=str)

def record_price(token, price_usd):
    """Record a price point with timestamp"""
    history = load_price_history()
    
    if token not in history:
        history[token] = []
    
    history[token].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "price": price_usd
    })
    
    # Keep only last 24 hours of data
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    history[token] = [p for p in history[token] if p["timestamp"] > cutoff]
    
    save_price_history(history)

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

def calculate_momentum(token):
    """
    Calculate price momentum over the window.
    Returns: {
        'trend': 'up' | 'down' | 'flat',
        'momentum_pct': float,  # % change over window
        'volatility': float,    # price volatility
        'swing_detected': bool   # significant move detected
    }
    """
    history = load_price_history()
    
    if token not in history or len(history[token]) < 3:
        return {'trend': 'flat', 'momentum_pct': 0, 'volatility': 0, 'swing_detected': False}
    
    prices = history[token]
    
    # Get prices from last MOMENTUM_WINDOW_MINUTES
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=MOMENTUM_WINDOW_MINUTES)).isoformat()
    recent = [p for p in prices if p["timestamp"] > cutoff]
    
    if len(recent) < 2:
        return {'trend': 'flat', 'momentum_pct': 0, 'volatility': 0, 'swing_detected': False}
    
    # Calculate momentum
    start_price = recent[0]["price"]
    end_price = recent[-1]["price"]
    momentum_pct = (end_price - start_price) / start_price if start_price > 0 else 0
    
    # Calculate volatility (standard deviation of % changes)
    pct_changes = []
    for i in range(1, len(recent)):
        if recent[i-1]["price"] > 0:
            pct_changes.append((recent[i]["price"] - recent[i-1]["price"]) / recent[i-1]["price"])
    
    volatility = sum(abs(c) for c in pct_changes) / len(pct_changes) if pct_changes else 0
    
    # Detect swing (significant move)
    swing_detected = abs(momentum_pct) >= MIN_SWING_SIZE
    
    # Determine trend
    if momentum_pct > 0.01:
        trend = 'up'
    elif momentum_pct < -0.01:
        trend = 'down'
    else:
        trend = 'flat'
    
    return {
        'trend': trend,
        'momentum_pct': momentum_pct,
        'volatility': volatility,
        'swing_detected': swing_detected
    }

def detect_reversal(token):
    """
    Detect if price is reversing direction.
    Returns: {
        'reversal_detected': bool,
        'reversal_type': 'peak' | 'dip' | None,
        'confidence': float
    }
    """
    history = load_price_history()
    
    if token not in history or len(history[token]) < 5:
        return {'reversal_detected': False, 'reversal_type': None, 'confidence': 0}
    
    prices = history[token]
    
    # Get last 10 price points
    recent = prices[-10:] if len(prices) >= 10 else prices
    
    if len(recent) < 5:
        return {'reversal_detected': False, 'reversal_type': None, 'confidence': 0}
    
    # Check for peak (was going up, now going down)
    mid = len(recent) // 2
    first_half = recent[:mid]
    second_half = recent[mid:]
    
    first_trend = (first_half[-1]["price"] - first_half[0]["price"]) / first_half[0]["price"] if first_half[0]["price"] > 0 else 0
    second_trend = (second_half[-1]["price"] - second_half[0]["price"]) / second_half[0]["price"] if second_half[0]["price"] > 0 else 0
    
    # Peak: first half up, second half down
    if first_trend > 0.02 and second_trend < -0.01:
        return {
            'reversal_detected': True,
            'reversal_type': 'peak',
            'confidence': abs(first_trend) + abs(second_trend)
        }
    
    # Dip: first half down, second half up
    if first_trend < -0.02 and second_trend > 0.01:
        return {
            'reversal_detected': True,
            'reversal_type': 'dip',
            'confidence': abs(first_trend) + abs(second_trend)
        }
    
    return {'reversal_detected': False, 'reversal_type': None, 'confidence': 0}

def get_position_trailing_stop(token, current_price):
    """Calculate trailing stop level based on position high"""
    db = pdb.load_db()
    
    for pos in db.get("positions", []):
        if pos["token"] == token and pos.get("status") == "OPEN":
            # Get highest price since entry
            high_price = pos.get("highest_price_since_entry", pos.get("entry_price", current_price))
            
            # Update high if current is higher
            if current_price > high_price:
                high_price = current_price
                pos["highest_price_since_entry"] = high_price
                pdb.save_db(db)
            
            # Trailing stop is 2% below the high
            trailing_stop = high_price * (1 - TRAILING_STOP_PCT)
            
            return {
                'trailing_stop_price': trailing_stop,
                'highest_price': high_price,
                'should_sell': current_price < trailing_stop and (high_price - current_price) / high_price >= TRAILING_STOP_PCT
            }
    
    return None

def generate_momentum_signals():
    """Generate buy/sell signals based on momentum analysis"""
    db = pdb.load_db()
    signals = []
    
    # Check open positions for sell signals
    for pos in db.get("positions", []):
        if pos.get("status") != "OPEN":
            continue
        
        token = pos["token"]
        mint = pos.get("mint", "")
        
        # Get current price
        current_price = get_jupiter_price(mint)
        if current_price <= 0:
            continue
        
        # Record price for history
        record_price(token, current_price)
        
        # Calculate momentum
        momentum = calculate_momentum(token)
        reversal = detect_reversal(token)
        
        # Get position P&L
        entry_price = pos.get("entry_price", current_price)
        pnl_pct = (current_price - entry_price) / entry_price if entry_price > 0 else 0
        
        # Get trailing stop info
        trailing = get_position_trailing_stop(token, current_price)
        
        # === SELL SIGNALS ===
        
        # 1. Take profit at 5% (not waiting for 10%)
        if pnl_pct >= SWING_PROFIT_TARGET:
            signals.append({
                "token": token,
                "mint": mint,
                "action": "SELL",
                "reason": "SWING_PROFIT_5PCT",
                "pnl_pct": pnl_pct * 100,
                "current_price": current_price,
                "entry_price": entry_price,
                "momentum": momentum
            })
            continue
        
        # 2. Sell on momentum reversal (peak detected)
        if reversal['reversal_detected'] and reversal['reversal_type'] == 'peak':
            if pnl_pct > 0.02:  # Only sell if we're profitable
                signals.append({
                    "token": token,
                    "mint": mint,
                    "action": "SELL",
                    "reason": "MOMENTUM_REVERSAL_PEAK",
                    "pnl_pct": pnl_pct * 100,
                    "current_price": current_price,
                    "reversal_confidence": reversal['confidence'],
                    "momentum": momentum
                })
                continue
        
        # 3. Trailing stop (protect gains)
        if trailing and trailing['should_sell'] and pnl_pct > 0:
            signals.append({
                "token": token,
                "mint": mint,
                "action": "SELL",
                "reason": "TRAILING_STOP",
                "pnl_pct": pnl_pct * 100,
                "current_price": current_price,
                "highest_price": trailing['highest_price'],
                "trailing_stop_price": trailing['trailing_stop_price']
            })
            continue
        
        # 4. Tight stop loss at -3%
        if pnl_pct <= SWING_STOP_LOSS:
            signals.append({
                "token": token,
                "mint": mint,
                "action": "SELL",
                "reason": "SWING_STOP_LOSS_3PCT",
                "pnl_pct": pnl_pct * 100,
                "current_price": current_price
            })
            continue
        
        # === BUY BACK SIGNAL (if we just sold) ===
        # This would be handled separately - checking for dip buying opportunities
    
    return signals

def generate_dip_buy_signals():
    """Generate buy signals for tokens we don't hold - buy the dip"""
    db = pdb.load_db()
    signals = []
    
    # Check known tokens for dip opportunities
    from scout_v2 import KNOWN_TOKENS, get_jupiter_price
    
    for token, mint in KNOWN_TOKENS.items():
        # Skip if we already hold this token
        already_hold = any(
            p.get("token") == token and p.get("status") == "OPEN" 
            for p in db.get("positions", [])
        )
        if already_hold:
            continue
        
        # Get price and record it
        price = get_jupiter_price(mint)
        if price <= 0:
            continue
        
        record_price(token, price)
        
        # Check for dip reversal
        reversal = detect_reversal(token)
        momentum = calculate_momentum(token)
        
        # Buy signal: dip reversal detected + momentum turning up
        if reversal['reversal_detected'] and reversal['reversal_type'] == 'dip':
            if momentum['trend'] == 'up' or momentum['momentum_pct'] > 0:
                signals.append({
                    "token": token,
                    "mint": mint,
                    "action": "BUY",
                    "reason": "DIP_BUY_MOMENTUM_REVERSAL",
                    "current_price": price,
                    "reversal_confidence": reversal['confidence'],
                    "momentum": momentum
                })
    
    return signals

def main():
    """Main momentum trader routine"""
    print(f"[{datetime.now(timezone.utc).isoformat()}] === MOMENTUM SWING TRADER ===")
    
    # Generate sell signals (capture swings)
    sell_signals = generate_momentum_signals()
    
    # Generate buy signals (buy dips)
    buy_signals = generate_dip_buy_signals()
    
    all_signals = sell_signals + buy_signals
    
    if all_signals:
        print(f"\n[SWING SIGNALS] {len(all_signals)} found:")
        for sig in all_signals:
            print(f"  {sig['action']} {sig['token']}: {sig['reason']}")
            if 'pnl_pct' in sig:
                print(f"    P&L: {sig['pnl_pct']:+.2f}% | Price: ${sig['current_price']:.6f}")
            if 'momentum' in sig:
                print(f"    Momentum: {sig['momentum']['trend']} ({sig['momentum']['momentum_pct']*100:+.2f}%)")
    else:
        print("\n[SWING SIGNALS] No momentum signals")
    
    # Save signals to queue for executor
    if all_signals:
        queue_file = os.path.join(os.path.dirname(__file__), "swing_signals.json")
        with open(queue_file, 'w') as f:
            json.dump(all_signals, f, indent=2)
        print(f"\n[QUEUE] {len(all_signals)} signals saved to swing_signals.json")
    
    return all_signals

if __name__ == "__main__":
    main()
