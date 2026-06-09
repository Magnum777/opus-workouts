#!/usr/bin/env python3
"""
Portfolio-Aware Research Module
Integrates portfolio holdings with market research for confidence scoring
"""

import json
import os
import requests
from datetime import datetime, timezone

# Configuration
PORTFOLIO_FILE = "positions.json"
RESEARCH_CACHE = "research-cache.json"
SIGNALS_FILE = "portfolio-signals.json"

# External APIs
COINGECKO_API = "https://api.coingecko.com/api/v3"
JUPITER_API = "https://lite-api.jup.ag/swap/v1"

# Token metadata for research
KNOWN_TOKENS = {
    "PENGU": {"mint": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv", "category": "meme"},
    "PUMP": {"mint": "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn", "category": "meme"},
    "TRUMP": {"mint": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN", "category": "political"},
    "BONK": {"mint": "DezXAZ8z7PnrnRJjz3wXBoaggixuT4Byifb9T8qbtPas", "category": "meme"},
    "WIF": {"mint": "85VBFQZC9TZkfaptBWqv14ALD9fJNUKtWA41kh69teRP", "category": "meme"},
    "POPCAT": {"mint": "7xKXtg2CW87d97TXJSDpbD5jBkheotQbM2MyWGkErQgB", "category": "meme"},
    "GIGA": {"mint": "63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9", "category": "meme"},
    "GOAT": {"mint": "CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump", "category": "meme"},
    "MOODENG": {"mint": "Moodeng5zS4Zs2Dq3bFJBjtFAY4xqKc9w1EqR4XP2S3Dq", "category": "meme"},
}

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

def get_portfolio():
    """Load current portfolio"""
    data = load_json(PORTFOLIO_FILE, {"positions": []})
    return data.get("positions", [])

def get_token_research(token_name, mint):
    """Multi-source research for a token"""
    research = {
        "token": token_name,
        "mint": mint,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sources": {},
        "confidence_score": 50,  # Base 50/100
        "recommendation": "HOLD"  # Default
    }
    
    # 1. Jupiter Price (liquidity check)
    try:
        usdc = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        r = requests.get(f"{JUPITER_API}/quote?inputMint={mint}&outputMint={usdc}&amount=1000000&slippage=1", timeout=10)
        if r.status_code == 200:
            price = float(r.json()["outAmount"]) / 1e6
            research["sources"]["jupiter"] = {"price_usd": price, "status": "active"}
            research["confidence_score"] += 10  # +10 for liquidity
        else:
            research["sources"]["jupiter"] = {"status": "error", "code": r.status_code}
            research["confidence_score"] -= 20  # -20 for no liquidity
    except Exception as e:
        research["sources"]["jupiter"] = {"status": "error", "error": str(e)}
        research["confidence_score"] -= 20
    
    # 2. CoinGecko Trending (if available)
    try:
        r = requests.get(f"{COINGECKO_API}/search/trending", timeout=10)
        if r.status_code == 200:
            trending = r.json().get("coins", [])
            token_symbols = [c["item"]["symbol"].upper() for c in trending[:20]]
            if token_name in token_symbols:
                research["sources"]["coingecko"] = {"trending": True, "rank": token_symbols.index(token_name) + 1}
                research["confidence_score"] += 15  # +15 for trending
            else:
                research["sources"]["coingecko"] = {"trending": False}
    except:
        research["sources"]["coingecko"] = {"status": "unavailable"}
    
    # 3. Category-based adjustments
    category = KNOWN_TOKENS.get(token_name, {}).get("category", "unknown")
    if category == "meme":
        research["confidence_score"] -= 5  # Memes are riskier
    
    # Clamp confidence 0-100
    research["confidence_score"] = max(0, min(100, research["confidence_score"]))
    
    # Generate recommendation based on confidence
    if research["confidence_score"] >= 70:
        research["recommendation"] = "STRONG_HOLD"
    elif research["confidence_score"] >= 50:
        research["recommendation"] = "HOLD"
    elif research["confidence_score"] >= 30:
        research["recommendation"] = "WEAK_HOLD"
    else:
        research["recommendation"] = "CONSIDER_EXIT"
    
    return research

def analyze_portfolio():
    """Analyze all portfolio positions with research"""
    portfolio = get_portfolio()
    
    if not portfolio:
        print("No portfolio positions found")
        return []
    
    print(f"Analyzing {len(portfolio)} positions...")
    
    analyses = []
    for position in portfolio:
        token = position.get("token", "UNKNOWN")
        mint = position.get("mint", "")
        value_usd = position.get("current_value_usd", 0)
        
        print(f"\n  Researching {token} (${value_usd:.2f})...")
        
        research = get_token_research(token, mint)
        
        # Combine with portfolio data
        analysis = {
            "token": token,
            "value_usd": value_usd,
            "research": research,
            "confidence": research["confidence_score"],
            "recommendation": research["recommendation"]
        }
        
        analyses.append(analysis)
        
        print(f"    Confidence: {research['confidence_score']}/100")
        print(f"    Recommendation: {research['recommendation']}")
    
    return analyses

def generate_signals(analyses):
    """Generate trading signals based on research + portfolio"""
    signals = []
    
    for analysis in analyses:
        token = analysis["token"]
        confidence = analysis["confidence"]
        rec = analysis["recommendation"]
        value = analysis["value_usd"]
        
        # Low confidence + significant value = consider exit
        if confidence < 40 and value > 10:
            signals.append({
                "token": token,
                "action": "CONSIDER_SELL",
                "reason": f"Low confidence ({confidence}/100) + ${value:.2f} value",
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # High confidence = hold/add
        elif confidence >= 70:
            signals.append({
                "token": token,
                "action": "STRONG_HOLD",
                "reason": f"High confidence ({confidence}/100)",
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
    
    return signals

def main():
    """Main research routine"""
    print(f"[{datetime.now(timezone.utc).isoformat()}] === PORTFOLIO RESEARCH ===")
    print("Integrating portfolio with market research...\n")
    
    # Analyze portfolio
    analyses = analyze_portfolio()
    
    if not analyses:
        print("No positions to analyze")
        return
    
    # Generate signals
    signals = generate_signals(analyses)
    
    # Save research
    save_json(RESEARCH_CACHE, {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "analyses": analyses,
        "signals": signals
    })
    
    # Save signals for trading system
    save_json(SIGNALS_FILE, {"signals": signals})
    
    # Summary
    print(f"\n{'='*40}")
    print(f"Portfolio Value: ${sum(a['value_usd'] for a in analyses):.2f}")
    print(f"Avg Confidence: {sum(a['confidence'] for a in analyses) / len(analyses):.1f}/100")
    print(f"Signals Generated: {len(signals)}")
    
    if signals:
        print("\nSignals:")
        for s in signals:
            print(f"  {s['action']}: {s['token']} ({s['reason']})")
    
    print("="*40)

if __name__ == "__main__":
    main()
