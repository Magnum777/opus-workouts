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
    "ETH-USD": {"name": "Ethereum", "min_order": 0.001},
    "BTC-USD": {"name": "Bitcoin", "min_order": 0.0001},
    "SOL-USD": {"name": "Solana", "min_order": 0.01},
    "DOGE-USD": {"name": "Dogecoin", "min_order": 100},
    "AVAX-USD": {"name": "Avalanche", "min_order": 0.1},
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
    
    if avg_momentum > 3:
        trend = "bullish_hot"
    elif avg_momentum > 1.5:
        trend = "bullish"
    elif avg_momentum < -3:
        trend = "bearish_hot"
    elif avg_momentum < -1.5:
        trend = "bearish"
    else:
        trend = "neutral"
    
    return {"trend": trend, "strength": abs(avg_momentum)}


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
            "config": {"max_position_pct": 0.5, "max_trade_pct": 0.2, "stop_loss_pct": 0.05, "take_profit_pct": 0.10, "mode": "paper"},
            "history": {"recent_prices": history_prices, "recent_trades": []},
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
            new_avg = price if pos_size <= 0 else (pos_size * avg_entry + size * price) / (pos_size + size)
            state["capital_usd"] = capital - cost
            position["size"] = pos_size + size
            position["avg_entry"] = new_avg
            trade_record["note"] = f"Executed BUY {pair}"
    elif action == "SELL" and size > 0:
        size = min(size, pos_size)
        proceeds = size * price
        state["capital_usd"] = capital + proceeds
        position["size"] = pos_size - size
        if position["size"] <= 1e-8:
            position["size"] = 0.0
            position["avg_entry"] = 0.0
        trade_record["note"] = f"Executed SELL {pair}"
    else:
        trade_record["note"] = "HOLD"
    
    state["positions"][pair] = position
    
    if pair not in state["history"]["recent_prices"]:
        state["history"]["recent_prices"][pair] = []
    state["history"]["recent_prices"][pair] = state["history"]["recent_prices"][pair][-50:] + [price]
    state["history"]["recent_trades"] = state["history"]["recent_trades"][-100:] + [trade_record]
    state["time"]["timestamp"] = datetime.now().isoformat()
    
    return state, trade_record


def call_local_llm(state: dict, best_pair: str, strength: float) -> dict:
    system_prompt = f"""You are a CRYPTO HOT MOMENTUM DAY-TRADER in PAPER MODE.

Trade: ETH-USD, BTC-USD, SOL-USD, DOGE-USD, AVAX-USD

HOTTEST: {best_pair} (momentum: {strength:.1f}%)

RULES:
- Only BUY hottest pair
- Sell if momentum turns bearish
- HOLD if unclear

Risk: max 50% position, 20% trade, 5% stop, 10% profit

JSON: {{"action":"BUY"/"SELL"/"HOLD", "pair":"PAIR-USD", "size":0.01, "reason":"..."}}"""
    
    payload = {"model": LOCAL_LLM_MODEL, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": json.dumps(state)}], "stream": False}

    try:
        resp = requests.post(LOCAL_LLM_URL, json=payload, timeout=60)
        data = resp.json()
        content = data["message"]["content"].strip()
        match = re.search(r'\{.+\}', content, re.DOTALL)
        decision = json.loads(match.group()) if match else {"action": "HOLD", "pair": best_pair, "size": 0.0, "reason": "No JSON"}
    except Exception as e:
        decision = {"action": "HOLD", "pair": best_pair, "size": 0.0, "reason": f"Error: {str(e)[:30]}"}

    decision.setdefault("action", "HOLD")
    decision.setdefault("pair", best_pair)
    decision.setdefault("size", 0.0)
    decision.setdefault("reason", "")
    return decision


def main():
    state = load_state()
    
    print("Fetching current prices...")
    for pair in TRADING_PAIRS:
        price = get_price_from_coinbase(pair)
        if price:
            state["prices"][pair] = price
    
    print("\n" + "="*50)
    print("HOT MOMENTUM SCANNER")
    print("="*50)
    print(f"\nCapital: ${state['capital_usd']:.2f}\n")
    
    # Calculate momentum for all pairs
    momentum_results = {}
    for pair in TRADING_PAIRS:
        price = state["prices"].get(pair, 0)
        prices = state["history"]["recent_prices"].get(pair, [price])
        mom = calculate_momentum(prices)
        momentum_results[pair] = mom
        
        trend = mom["trend"]
        if trend == "bullish_hot":
            marker = "[HOT]"
        elif trend == "bullish":
            marker = "[UP]"
        elif trend == "bearish_hot":
            marker = "[DWN]"
        elif trend == "bearish":
            marker = "[DROP]"
        else:
            marker = "[FLAT]"
        
        print(f"{marker} {pair:12} ${price:>10.2f} | {trend:12} | {mom['strength']:>5.1f}%")
    
    # Find hottest pair
    hot_pairs = [(p, m) for p, m in momentum_results.items() if m["trend"] in ["bullish_hot", "bullish"]]
    hot_pairs.sort(key=lambda x: x[1]["strength"], reverse=True)
    
    best_pair = hot_pairs[0][0] if hot_pairs else "ETH-USD"
    best_strength = hot_pairs[0][1]["strength"] if hot_pairs else 0
    
    print(f"\nHOTTEST: {best_pair} ({best_strength:.1f}% momentum)")
    
    # Get LLM decision
    decision = call_local_llm(state, best_pair, best_strength)
    
    print(f"\n=== LLM DECISION ===")
    print(json.dumps(decision, indent=2))
    
    # Apply
    pair = decision.get("pair", best_pair)
    new_state, trade_record = apply_decision_to_state(state, decision, pair)
    save_state(new_state)
    
    print(f"\n=== TRADE ===")
    print(json.dumps(trade_record, indent=2))


if __name__ == "__main__":
    main()
