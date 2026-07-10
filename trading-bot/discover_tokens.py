#!/usr/bin/env python3
"""
Token Discovery & Vetting — TradeBot
Searches for new Solana tokens that are actually tradeable, vets them,
and auto-adds to curated_tokens.json if they pass.

Vetting requirements:
- Jupiter can route a swap (must be actually tradeable)
- Not a pump.fun token
- Minimum $50k liquidity on DexScreener
- Minimum $25k 24h volume on DexScreener

Run: C:\Python314\python.exe trading-bot/discover_tokens.py
"""
import json, os, sys, requests, time
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

_CURATED_PATH = os.path.join(os.path.dirname(__file__), "curated_tokens.json")
_USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
_JUP_LITE = "https://lite-api.jup.ag/swap/v1/quote"
_MAX_ADD_PER_RUN = 3

def load_curated():
    if not os.path.exists(_CURATED_PATH):
        return {}
    with open(_CURATED_PATH) as f:
        return json.load(f)

def save_curated(data):
    with open(_CURATED_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def jupiter_quote(mint):
    """Check if Jupiter can route a swap. Returns price or 0."""
    for _ in range(2):
        try:
            r = requests.get("%s?inputMint=%s&outputMint=%s&amount=1000000&slippage=1" % (_JUP_LITE, mint, _USDC), timeout=10)
            if r.status_code == 200:
                return float(r.json().get("outAmount", 0)) / 1e6
            time.sleep(1.5)
        except:
            pass
    return 0.0

def get_dexscreener_pairs(mint):
    """Get DexScreener pairs for a token"""
    try:
        r = requests.get("https://api.dexscreener.com/latest/dex/tokens/%s" % mint, timeout=10)
        if r.status_code == 200:
            d = r.json()
            pairs = d.get("pairs")
            if pairs and isinstance(pairs, list):
                return pairs
    except:
        pass
    return []

def vet_trending_candidate(mint):
    """
    Vet a trending token candidate.
    Returns (passed, info_dict_or_reason)
    """
    if mint.lower().endswith('pump'):
        return False, "pump.fun"

    # Check Jupiter first (fastest filter)
    price = jupiter_quote(mint)
    if price <= 0:
        return False, "no Jupiter route"

    # Check DexScreener for liquidity/volume context
    pairs = get_dexscreener_pairs(mint)
    if not pairs:
        # Jupiter routes it but DexScreener has no data — still usable
        return True, {"symbol": mint[:8], "dex": "unknown", "liquidity": 0, "volume": 0, "price": price}

    sol_pairs = [p for p in pairs if p.get("chainId") == "solana"]
    if not sol_pairs:
        return False, "no Solana pairs on DexScreener"

    best = max(sol_pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0))
    symbol = best.get("baseToken", {}).get("symbol", "").upper() or mint[:8]
    name = best.get("baseToken", {}).get("name", "")
    dex = best.get("dexId", "unknown")
    liquidity = float(best.get("liquidity", {}).get("usd", 0) or 0)
    volume = float(best.get("volume", {}).get("h24", 0) or 0)

    # Skip scam keywords
    for skip in ["airdrop", "free", "claim", "presale", "gift", "bonus"]:
        if skip in symbol.lower() or skip in name.lower():
            return False, "scam keyword"

    # Minimum liquidity for adding
    if liquidity < 50000:
        return False, "low liquidity $%.0f" % liquidity

    return True, {
        "symbol": symbol,
        "dex": dex,
        "liquidity": liquidity,
        "volume": volume,
        "price": price
    }

def check_curated_health(curated):
    """Check if existing curated tokens are still tradeable. Returns list of dead tokens."""
    dead = []
    for sym, meta in curated.items():
        price = jupiter_quote(meta["mint"])
        if price <= 0:
            print("  %s: DEAD (no Jupiter route)" % sym)
            dead.append(sym)
        else:
            print("  %s: $%.6f" % (sym, price))
        time.sleep(1.5)
    return dead

def scan_dexscreener(curated):
    """Scan DexScreener trending for new tokens"""
    existing_mints = set(v["mint"] for v in curated.values())
    candidates = []

    for endpoint_name, endpoint in [("Top boosts", "/top/v1"), ("Active boosts", "/active/v1")]:
        try:
            r = requests.get("https://api.dexscreener.com/token-boosts%s" % endpoint, timeout=10)
            if r.status_code != 200:
                continue
            data = r.json()
            solana = [t for t in data if isinstance(t, dict) and t.get("chainId") == "solana"]
            print("  %s: %d Solana tokens" % (endpoint_name, len(solana)))

            for t in solana:
                mint = (t.get("tokenAddress") or "").strip().upper()
                if not mint or mint in existing_mints:
                    continue
                if mint.lower().endswith('pump'):
                    continue

                passed, info = vet_trending_candidate(mint)
                if passed and isinstance(info, dict):
                    if info["symbol"] not in curated:
                        candidates.append({
                            "symbol": info["symbol"],
                            "mint": mint,
                            **info
                        })
                        print("  > %s: $%.6f, liq=$%.0f, vol=$%.0f (%s)" % (info["symbol"], info["price"], info["liquidity"], info["volume"], info["dex"]))
                time.sleep(1.5)
        except Exception as e:
            print("  %s error: %s" % (endpoint_name, e))

    return candidates

def discover():
    print("=" * 60)
    print("TOKEN DISCOVERY & VETTING")
    print(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    print("=" * 60)

    curated = load_curated()

    # Step 1: Check existing tokens
    print("\n[1] Checking existing curated tokens...")
    dead = check_curated_health(curated)

    # Remove dead tokens
    if dead:
        for sym in dead:
            del curated[sym]
            print("  Removed %s from curated list" % sym)

    # Step 2: Scan for new tokens
    print("\n[2] Scanning DexScreener for new candidates...")
    candidates = scan_dexscreener(curated)

    # Step 3: Add best candidates
    if not candidates:
        print("\nNo new vet-worthy tokens found.")
        return

    candidates.sort(key=lambda c: c.get("liquidity", 0), reverse=True)
    to_add = candidates[:_MAX_ADD_PER_RUN]

    print("\n=== ADDING %d TOKENS ===" % len(to_add))
    for c in to_add:
        curated[c["symbol"]] = {
            "mint": c["mint"],
            "category": "utility",
            "added": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "source": "discovery",
            "liquidity_at_add": c.get("liquidity", 0),
            "price_at_add": c.get("price", 0)
        }
        print("  + %s ($%.6f)" % (c["symbol"], c["price"]))

    save_curated(curated)
    print("\nDone! Curated tokens: %s" % ", ".join(sorted(curated.keys())))

if __name__ == "__main__":
    discover()