import json
import os
import re
import requests
from datetime import datetime

STATE_PATH = "trading-bot/state.json"
TRADES_LOG_PATH = "trading-bot/trades.json"
DECISION_PATH = "trading-bot/latest_decision.json"

LOCAL_LLM_URL = "http://192.168.68.50:11434/api/chat"
LOCAL_LLM_MODEL = "qwen2.5:7b"

TRADING_PAIRS = {
    "ETH-USD": {"name": "Ethereum", "min_order": 0.001, "volatility": "medium"},
    "BTC-USD": {"name": "Bitcoin", "min_order": 0.0001, "volatility": "low"},
    "SOL-USD": {"name": "Solana", "min_order": 0.01, "volatility": "high"},
    "DOGE-USD": {"name": "Dogecoin", "min_order": 100, "volatility": "very_high"},
    "AVAX-USD": {"name": "Avalanche", "min_order": 0.1, "volatility": "high"},
}


def get_price_from_coinbase(product_id):
    try:
        url = f"https://api.coinbase.com/v2/prices/{product_id}/spot"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return float(data["data"]["amount"])
    except:
        return None


def calculate_momentum(prices, periods=[3, 5, 10]):
    if len(prices) < 2:
        return {"trend": "neutral", "strength": 0, "signal": "HOLD"}
    
    current = prices[-1]
    momentum = {}
    
    for p in periods:
        if len(prices) >= p:
            past = prices[-p]
            change = ((current - past) / past) * 100
            momentum[f"momentum_{p}"] = change
    
    avg_momentum = sum(momentum.values()) / len(momentum) if momentum else 0
    
    # More aggressive thresholds for "hot" trading
    if avg_momentum > 3:
        trend = "bullish_hot"
        signal = "BUY"
    elif avg_momentum > 1.5:
        trend = "bullish"
        signal = "BUY"
    elif avg_momentum < -3:
        trend = "bearish_hot"
        signal = "SELL"
    elif avg_momentum < -1.5:
        trend = "bearish"
        signal = "SELL"
    else:
        trend = "neutral"
        signal = "HOLD"
    
    return {
        "trend": trend,
        "strength": abs(avg_momentum),
        "signal": signal,
        "momentum": momentum
    }


def load_state():
    if not os.path.exists(STATE_PATH):
        prices = {}
        positions = {}
        history_prices = {}
        for pair in TRADING_PAIRS:
            prices[pair] = 1000.0
            positions[pair] = {"size": 0.0, "avg_entry": 0.0}
            history_prices[pair] = [1000.0]
        
        return {
            "capital_usd": 100.0,
            "prices": prices,
            "positions": positions,
            "config": {
                "max_position_pct": 0.5,
                "max_trade_pct": 0.2,
                "stop_loss_pct": 0.05,
                "take_profit_pct": 0.10,
                "mode": "paper",
                "hot_threshold": 2.0  # Only trade if momentum > 2%
            },
            "history": {
                "recent_prices": history_prices,
                "recent_trades": []
            },
            "time": {"timestamp": datetime.now().isoformat()}
        }
    
    with open(STATE_PATH, "r") as f:
        return json.load(f)


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def apply_decision_to_state(state, decision, pair):
    price = state["prices"].get(pair, 1000.0)
    capital = state["capital_usd"]
    position = state["positions"].get(pair, {"size": 0.0, "avg_entry": 0.0})
    pos_size = position.get("size", 0.0)
    avg_entry = position.get("avg_entry", 0.0)
    
    action = decision.get("action", "HOLD")
    size = float(decision.get("size", 0.0))
    
    trade_record = {
        "timestamp": datetime.now().isoformat(),
        "pair": pair,
        "action": action,
        "size": size,
        "price": price,
        "reason": decision.get("reason", ""),
    }
    
    if action == "BUY" and size > 0:
        cost = size * price
        if cost > capital:
            trade_record["note"] = "Rejected: insufficient capital"
        else:
            if pos_size <= 0:
                new_avg = price
            else:
                new_avg = (pos_size * avg_entry + size * price) / (pos_size + size)
            state["capital_usd"] = capital - cost
            position["size"] = pos_size + size
            position["avg_entry"] = new_avg
            trade_record["note"] = f"Executed BUY {pair}"
    elif action == "SELL" and size > 0:
        if size > pos_size:
            size = pos_size
            trade_record["size"] = size
        proceeds = size * price
        state["capital_usd"] = capital + proceeds
        position["size"] = pos_size - size
        if position["size"] <= 1e-8:
            position["size"] = 0.0
            position["avg_entry"] = 0.0
        trade_record["note"] = f"Executed SELL {pair}"
    else:
        trade_record["note"] = "HOLD - no changes"
    
    state["positions"][pair] = position
    
    if pair not in state["history"]["recent_prices"]:
        state["history"]["recent_prices"][pair] = []
    state["history"]["recent_prices"][pair] = state["history"]["recent_prices"][pair][-50:]
    state["history"]["recent_prices"][pair].append(price)
    
    state["history"]["recent_trades"] = state["history"]["recent_trades"][-100:]
    state["history"]["recent_trades"].append(trade_record)
    state["time"]["timestamp"] = datetime.now().isoformat()
    
    return state, trade_record


def call_local_llm(state: dict, best_pair: str, momentum_data: dict) -> dict:
    system_prompt = f"""You are a CRYPTO HOT MOMENTUM DAY-TRADER in PAPER MODE.

You trade these pairs: ETH-USD, BTC-USD, SOL-USD, DOGE-USD, AVAX-USD

TODAY'S HOTTEST PAIR: {best_pair} (momentum: {momentum_data.get('strength', 0):.1f}%)

STRATEGY - TRADE WHAT'S HOT:
- Only BUY the hottest pair (strongest upward momentum)
- Only SELL if momentum turns bearish
- HOLD if nothing is clearly moving

RISK RULES:
- Max 50% of capital in one position
- Max 20% per trade
- Stop-loss at 5%
- Take profit at 10%

Respond ONLY with valid JSON:
{{
  "action": "BUY" or "SELL" or "HOLD",
  "pair": "PAIR-USD",
  "size": 0.01,
  "reason": "why this pair is hot..."
}}"""
    
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(state)}
        ],
        "stream": False,
    }

    try:
        resp = requests.post(LOCAL_LLM_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["message"]["content"].strip()
        
        match = re.search(r'\{.+\}', content, re.DOTALL)
        if match:
            decision = json.loads(match.group())
        else:
            decision = {"action": "HOLD", "pair": best_pair, "size": 0.0, "reason": "No valid JSON"}
    except Exception as e:
        return {"action": "HOLD", "pair": best_pair, "size": 0.0, "reason": f"LLM error: {str(e)[:40]}"}

    decision.setdefault("action", "HOLD")
    decision.setdefault("pair", best_pair)
    decision.setdefault("size", 0.0)
    decision.setdefault("reason", "")
    return decision


def validate_decision(state, decision):
    action = decision.get("action", "HOLD")
    pair = decision.get("pair", "ETH-USD")
    size = float(decision.get("size", 0.0))
    price = state["prices"].get(pair, 1000.0)
    capital = state["capital_usd"]
    position = state["positions"].get(pair, {"size": 0.0})
    pos_size = position.get("size", 0.0)
    config = state.get("config", {})
    max_pos_pct = float(config.get("max_position_pct", 0.5))
    max_trade_pct = float(config.get("max_trade_pct", 0.2))
    
    equity = capital + pos_size * price
    max_pos_value = equity * max_pos_pct
    max_trade_value = equity * max_trade_pct
    
    if action == "BUY" and size > 0:
        new_pos_value = (pos_size * price) + (size * price)
        if new_pos_value > max_pos_value:
            decision["action"] = "HOLD"
            decision["size"] = 0.0
            decision["reason"] += " [risk: position limit]"
        elif (size * price) > max_trade_value:
            decision["action"] = "HOLD"
            decision["size"] = 0.0
            decision["reason"] += " [risk: trade limit]"
    elif action == "SELL" and size > 0:
        if size > pos_size:
            decision["size"] = pos_size
    
    return decision


def main():
    state = load_state()
    
    print("Fetching current prices...")
    for pair in TRADING_PAIRS:
        price = get_price_from_coinbase(pair)
        if price:
            state["prices"][pair] = price
    
    print("\n" + "="*60)
    print("HOT MOMENTUM SCANNER")
    print("="*60)
    
    print(f"\nCapital: ${state['capital_usd']:.2f}\n")
    
    # Calculate momentum for ALL pairs
    momentum_results = {}
    for pair in TRADING_PAIRS:
        price = state["prices"].get(pair, 0)
        info = TRADING_PAIRS[pair]
        prices = state["history"]["recent_prices"].get(pair, [price])
        
        mom = calculate_momentum(prices)
        momentum_results[pair] = mom
        
        # Color coding
        if mom["trend"] == "bullish_hot":
        elif mom["trend"] == "bullish":
        elif mom["trend"] == "bearish_hot":
        elif mom["trend"] == "bearish":
        else:
        
    
    # Find the HOTTEST pair (highest positive momentum)
    hot_pairs = [(p, m) for p, m in momentum_results.items() if m["trend"] in ["bullish_hot", "bullish"]]
    hot_pairs.sort(key=lambda x: x[1]["strength"], reverse=True)
    
    if hot_pairs:
        best_pair, best_momentum = hot_pairs[0]
    else:
        best_pair = "ETH-USD"
        best_momentum = {"strength": 0}
    
    print(f"\n🔥 HOTTEST PAIR: {best_pair} ({best_momentum['strength']:.1f}% momentum)")
    
    # Get LLM decision
    decision = call_local_llm(state, best_pair, best_momentum)
    decision = validate_decision(state, decision)
    
    # Save decision
    with open(DECISION_PATH, "w") as f:
        json.dump(decision, f, indent=2)
    
    print(f"\n=== LLM DECISION ===")
    print(json.dumps(decision, indent=2))
    
    # Apply
    pair = decision.get("pair", best_pair)
    new_state, trade_record = apply_decision_to_state(state, decision, pair)
    save_state(new_state)
    
    print(f"\n=== TRADE RECORD ===")
    print(json.dumps(trade_record, indent=2))


if __name__ == "__main__":
    main()

