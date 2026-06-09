#!/usr/bin/env python3
"""
TradeBot Token Safety Check - API-based
Quickly verifies a token isn't an obvious honeypot/scam before buying.
Uses DexScreener API (fast, reliable, no browser needed).
"""

import json
import sys
import requests
from datetime import datetime, timezone

def check_token_safety(mint_address, token_name=""):
    """
    Check token safety via DexScreener API.
    Returns dict with safety score and analysis.
    """
    result = {
        "mint": mint_address,
        "name": token_name,
        "safe": False,
        "score": 0,  # 0-100
        "checks": {},
        "notes": [],
        "pairs": 0,
        "top_pair": None,
        "error": None
    }
    
    try:
        # Call DexScreener API
        url = f"https://api.dexscreener.com/latest/dex/tokens/{mint_address}"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code != 200:
            result["error"] = f"DexScreener API error: {resp.status_code}"
            return result
        
        data = resp.json()
        pairs = data.get("pairs", [])
        result["pairs"] = len(pairs)
        
        if not pairs:
            result["error"] = "No pairs found on DexScreener"
            result["notes"].append("No trading pairs found — possible fake token or not yet listed")
            return result
        
        # Sort by liquidity (descending)
        pairs_sorted = sorted(pairs, key=lambda p: p.get("liquidity", {}).get("usd", 0) or 0, reverse=True)
        top = pairs_sorted[0]
        result["top_pair"] = {
            "dex": top.get("dexId"),
            "liquidity_usd": top.get("liquidity", {}).get("usd", 0),
            "volume_24h": top.get("volume", {}).get("h24", 0),
            "price_usd": top.get("priceUsd"),
            "fdv": top.get("fdv"),
            "market_cap": top.get("marketCap")
        }
        
        # Aggregate stats across all pairs
        total_liquidity = sum(p.get("liquidity", {}).get("usd", 0) or 0 for p in pairs)
        total_volume_24h = sum(p.get("volume", {}).get("h24", 0) or 0 for p in pairs)
        
        total_buys_24h = sum(p.get("txns", {}).get("h24", {}).get("buys", 0) or 0 for p in pairs)
        total_sells_24h = sum(p.get("txns", {}).get("h24", {}).get("sells", 0) or 0 for p in pairs)
        
        # Check 1: Has liquidity?
        has_liquidity = total_liquidity > 1000
        result["checks"]["has_liquidity"] = has_liquidity
        result["checks"]["liquidity_usd"] = round(total_liquidity, 2)
        
        # Check 2: Has trading volume?
        has_volume = total_volume_24h > 100
        result["checks"]["has_volume"] = has_volume
        result["checks"]["volume_24h"] = round(total_volume_24h, 2)
        
        # Check 3: Buy/sell ratio (more sells than buys = potential dump)
        if total_buys_24h + total_sells_24h > 0:
            sell_ratio = total_sells_24h / (total_buys_24h + total_sells_24h)
            result["checks"]["sell_ratio"] = round(sell_ratio, 2)
            result["checks"]["healthy_ratio"] = sell_ratio < 0.7  # Less than 70% sells
        else:
            result["checks"]["sell_ratio"] = None
            result["checks"]["healthy_ratio"] = None
        
        # Check 4: Token age (older = more established)
        oldest_pair = min(pairs, key=lambda p: p.get("pairCreatedAt", float('inf')))
        created_ms = oldest_pair.get("pairCreatedAt", 0)
        if created_ms:
            age_days = (datetime.now(timezone.utc).timestamp() * 1000 - created_ms) / (1000 * 86400)
            result["checks"]["age_days"] = round(age_days, 1)
            result["checks"]["not_brand_new"] = age_days > 7  # Older than 7 days
        else:
            result["checks"]["age_days"] = None
            result["checks"]["not_brand_new"] = None
        
        # Check 5: Multiple DEX listings?
        dexes = set(p.get("dexId") for p in pairs)
        result["checks"]["dex_count"] = len(dexes)
        result["checks"]["multi_dex"] = len(dexes) >= 2
        
        # Check 6: Has website/socials?
        info = top.get("info", {})
        has_website = bool(info.get("websites"))
        has_socials = bool(info.get("socials"))
        result["checks"]["has_website"] = has_website
        result["checks"]["has_socials"] = has_socials
        
        # Check 7: Known red flags in token name/symbol
        red_flags = ["honeypot", "scam", "rug", "blacklist", "untradeable", "fake"]
        name_lower = (token_name or "").lower()
        found_flags = [f for f in red_flags if f in name_lower]
        result["checks"]["red_flags"] = found_flags
        result["checks"]["no_name_flags"] = len(found_flags) == 0
        
        # Calculate score
        score = 0
        if has_liquidity:
            score += 25
        if has_volume:
            score += 20
        if result["checks"].get("healthy_ratio", True):
            score += 15
        if result["checks"].get("not_brand_new", False):
            score += 15
        if result["checks"].get("multi_dex", False):
            score += 10
        if has_website:
            score += 5
        if has_socials:
            score += 5
        if result["checks"].get("no_name_flags", True):
            score += 5
        
        result["score"] = min(score, 100)
        result["safe"] = result["score"] >= 60 and len(found_flags) == 0
        
        # Build notes
        if not has_liquidity:
            result["notes"].append(f"Low liquidity: ${total_liquidity:.0f}")
        if not has_volume:
            result["notes"].append(f"Low volume: ${total_volume_24h:.0f}/24h")
        if result["checks"].get("healthy_ratio") == False:
            result["notes"].append(f"Sell-heavy: {sell_ratio*100:.0f}% sells vs {100-sell_ratio*100:.0f}% buys")
        if result["checks"].get("not_brand_new") == False:
            result["notes"].append("Very new token (< 7 days old)")
        if not has_website:
            result["notes"].append("No website listed")
        if not has_socials:
            result["notes"].append("No social media listed")
        if found_flags:
            result["notes"].append(f"Name contains red flags: {', '.join(found_flags)}")
        
    except requests.exceptions.Timeout:
        result["error"] = "DexScreener API timeout"
    except Exception as e:
        result["error"] = str(e)
    
    return result

def main():
    """CLI entry point for testing."""
    if len(sys.argv) < 2:
        print("Usage: python token_safety_check.py <mint_address> [token_name]")
        print("Example: python token_safety_check.py 2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv PENGU")
        sys.exit(1)
    
    mint = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"Checking token safety for {name or mint}...")
    print(f"API: https://api.dexscreener.com/latest/dex/tokens/{mint}")
    print("-" * 50)
    
    result = check_token_safety(mint, name)
    
    print(json.dumps(result, indent=2))
    
    print("-" * 50)
    if result["safe"]:
        print(f"[SAFE] Score: {result['score']}/100")
    else:
        print(f"[NOT SAFE] Score: {result['score']}/100")
    
    if result["error"]:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()
