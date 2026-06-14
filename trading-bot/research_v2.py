"""
Research Module V2
Portfolio-aware research with confidence scoring + momentum analysis
"""

import json
import os
import requests
from datetime import datetime, timezone, timedelta

import portfolio_db_v2 as pdb

# Token metadata
TOKENS = {
    # Meme tokens (existing)
    "PENGU": {"mint": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv", "category": "meme"},
    "PUMP": {"mint": "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn", "category": "meme"},
    "TRUMP": {"mint": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN", "category": "political_meme"},
    "HANTA": {"mint": "2tXpgu2DLTsPUf9zFmuZmA4xrYxXKBTpVq9wAM7hzs9y", "category": "meme"},
    # Utility/DEX tokens (existing)
    "JUP": {"mint": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN", "category": "utility"},
    "ORCA": {"mint": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE", "category": "dex"},
    "RAY": {"mint": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R", "category": "utility"},
    # AI tokens (NEW - based on research)
    "TAO": {"mint": "taoC6xyv2v8tDLcev4uaGUgV4vdQsWJrGft2kcBRrBY", "category": "ai"},
}

USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOL_MINT = "So11111111111111111111111111111111111111112"
PRICE_HISTORY_FILE = os.path.join(os.path.dirname(__file__), "price_history.json")

# Momentum parameters
MOMENTUM_WINDOW_MINUTES = 15
SWING_PROFIT_TARGET = 0.15      # 15% (was 5% — memes need room to run)
SWING_STOP_LOSS = -0.03         # -3%
TRAILING_STOP_PCT = 0.02       # 2%

def get_jupiter_price(mint, decimals=None):
    """Get token price via Jupiter. Returns price per 1 full token in USD.
    Respects shared 429 cooldown. Returns 0 if rate-limited."""
    import time as _t
    
    # Check shared 429 cooldown first
    _429 = os.path.join(os.path.dirname(__file__), ".jupiter_429_cooldown.json")
    try:
        with open(_429) as _f:
            _d = json.load(_f)
        if _d.get("expires_at", 0) > _t.time():
            return 0  # Silent fail - 429 active
    except:
        pass
    
    _t.sleep(1.5)
    try:
        if decimals is None:
            decimals = 9 if mint == SOL_MINT else 6
        amount = 10 ** decimals
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount={amount}&slippage=1",
            timeout=10,
            headers={"User-Agent": "TradeBot/1.0", "Accept": "application/json"}
        )
        if r.status_code == 200:
            return float(r.json()["outAmount"]) / 1e6
        elif r.status_code == 429:
            # Persist 429 cooldown so other modules also back off
            try:
                with open(_429, "w") as _f:
                    json.dump({"expires_at": _t.time() + 600}, _f)
            except:
                pass
            _t.sleep(5)
            r2 = requests.get(
                f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount={amount}&slippage=1",
                timeout=10,
                headers={"User-Agent": "TradeBot/1.0", "Accept": "application/json"}
            )
            if r2.status_code == 200:
                return float(r2.json()["outAmount"]) / 1e6
    except:
        pass
    return 0

def load_price_history():
    """Load historical price data. Recovers from corruption gracefully."""
    if not os.path.exists(PRICE_HISTORY_FILE):
        return {}
    try:
        with open(PRICE_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        print(f"[WARN] price_history.json corrupted — resetting")
        backup = PRICE_HISTORY_FILE + ".bak"
        try:
            os.replace(PRICE_HISTORY_FILE, backup)
        except:
            pass
        return {}

def save_price_history(history):
    """Save price history atomically (write to temp, rename)"""
    import tempfile
    tmp = PRICE_HISTORY_FILE + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(history, f, indent=2, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, PRICE_HISTORY_FILE)

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

def calculate_momentum(token):
    """
    Calculate price momentum and detect swings.
    Returns momentum dict with trend, reversal signals.
    """
    history = load_price_history()

    if token not in history or len(history[token]) < 3:
        return {
            'trend': 'flat',
            'momentum_pct': 0,
            'swing_detected': False,
            'reversal_type': None,
            'reversal_confidence': 0
        }

    prices = history[token]

    # Get prices from last MOMENTUM_WINDOW_MINUTES
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=MOMENTUM_WINDOW_MINUTES)).isoformat()
    recent = [p for p in prices if p["timestamp"] > cutoff]

    if len(recent) < 2:
        return {
            'trend': 'flat',
            'momentum_pct': 0,
            'swing_detected': False,
            'reversal_type': None,
            'reversal_confidence': 0
        }

    # Calculate momentum
    start_price = recent[0]["price"]
    end_price = recent[-1]["price"]
    momentum_pct = (end_price - start_price) / start_price if start_price > 0 else 0

    # Detect trend
    if momentum_pct > 0.01:
        trend = 'up'
    elif momentum_pct < -0.01:
        trend = 'down'
    else:
        trend = 'flat'

    # Detect reversal (need at least 5 points)
    reversal_type = None
    reversal_confidence = 0

    if len(recent) >= 5:
        mid = len(recent) // 2
        first_half = recent[:mid]
        second_half = recent[mid:]

        first_trend = (first_half[-1]["price"] - first_half[0]["price"]) / first_half[0]["price"] if first_half[0]["price"] > 0 else 0
        second_trend = (second_half[-1]["price"] - second_half[0]["price"]) / second_half[0]["price"] if second_half[0]["price"] > 0 else 0

        # Peak: first half up, second half down
        if first_trend > 0.02 and second_trend < -0.01:
            reversal_type = 'peak'
            reversal_confidence = abs(first_trend) + abs(second_trend)
        # Dip: first half down, second half up
        elif first_trend < -0.02 and second_trend > 0.01:
            reversal_type = 'dip'
            reversal_confidence = abs(first_trend) + abs(second_trend)

    return {
        'trend': trend,
        'momentum_pct': momentum_pct,
        'swing_detected': abs(momentum_pct) >= 0.02,
        'reversal_type': reversal_type,
        'reversal_confidence': reversal_confidence
    }

def get_position_pnl(token, current_price):
    """Calculate current P&L for a position"""
    db = pdb.load_db()

    for pos in db.get("positions", []):
        if pos.get("token") == token and pos.get("status") == "OPEN":
            entry_price = pos.get("entry_price", current_price)
            if entry_price > 0:
                pnl_pct = (current_price - entry_price) / entry_price
                return pnl_pct
    return 0

def get_trailing_stop_status(token, current_price):
    """Check if trailing stop should trigger"""
    db = pdb.load_db()

    for pos in db.get("positions", []):
        if pos.get("token") == token and pos.get("status") == "OPEN":
            entry_price = pos.get("entry_price", current_price)
            highest_price = pos.get("highest_price_since_entry", entry_price)

            # Update highest price if current is higher
            if current_price > highest_price:
                highest_price = current_price
                pos["highest_price_since_entry"] = highest_price
                pdb.save_db(db)

            # Check trailing stop (2% below highest)
            trailing_stop_price = highest_price * (1 - TRAILING_STOP_PCT)

            return {
                'highest_price': highest_price,
                'trailing_stop_price': trailing_stop_price,
                'should_trigger': current_price < trailing_stop_price,
                'pnl_pct': (current_price - entry_price) / entry_price if entry_price > 0 else 0
            }
    return None

def get_jupiter_liquidity(mint):
    """Check token liquidity on Jupiter"""
    try:
        r = requests.get(
            f"https://lite-api.jup.ag/swap/v1/quote?inputMint={mint}&outputMint={USDC}&amount=1000000&slippage=1",
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            # High liquidity if large trades possible
            out_amount = float(data.get("outAmount", 0)) / 1e6
            return out_amount > 0.1  # $0.10+ liquidity
    except:
        pass
    return False

def check_coingecko_trending():
    """Check which token mints are trending via DexScreener boosts"""
    try:
        r = requests.get(
            "https://api.dexscreener.com/token-boosts/top/v1",
            timeout=10
        )
        if r.status_code == 200:
            trending = r.json()
            return [t.get("tokenAddress", "").upper() for t in trending if isinstance(t, dict) and t.get("chainId") == "solana"]
    except Exception:
        pass
    return []


def fetch_trending_solana_candidates(count=10):
    """
    Fetch new trending Solana token candidates via DexScreener.
    Uses DexScreener's own pairs data for price + liquidity (works for pump.fun tokens).
    Filters out tokens on cooldown, requires minimum liquidity.
    Returns list of dicts with token info ready for analysis.
    """
    # Load cooldowns
    cooldown_path = os.path.join(os.path.dirname(__file__), "rebuy_cooldowns.json")
    cooldowns = {}
    if os.path.exists(cooldown_path):
        with open(cooldown_path) as f:
            cooldowns = json.load(f)

    now_utc = datetime.now(timezone.utc).isoformat()

    try:
        r = requests.get(
            "https://api.dexscreener.com/token-boosts/top/v1",
            timeout=10
        )
        if r.status_code != 200:
            return []

        data = r.json()

        # Filter to Solana chain only
        sol_candidates = [
            t for t in data
            if isinstance(t, dict) and t.get("chainId") == "solana"
        ]

        if not sol_candidates:
            return []

        # Skip tokens already in our TOKENS dict
        already_tracked_mints = set(meta["mint"].upper() for meta in TOKENS.values())

        candidates = []
        for item in sol_candidates:
            mint = (item.get("tokenAddress") or "").strip()
            if not mint:
                continue
            mint_upper = mint.upper()

            # Skip our already-tracked tokens
            if mint_upper in already_tracked_mints:
                continue

            # Skip tokens on cooldown
            if mint_upper in cooldowns:
                cd_entry = cooldowns[mint_upper]
                if now_utc < cd_entry.get("cooldown_until", now_utc):
                    continue

            # Get price + liquidity from DexScreener pairs API
            try:
                import time as _dts
                _dts.sleep(0.5)
                pairs_resp = requests.get(
                    f"https://api.dexscreener.com/latest/dex/tokens/{mint}",
                    timeout=5
                )
                if pairs_resp.status_code != 200:
                    continue
                pairs_data = pairs_resp.json()
                pairs_list = pairs_data.get("pairs", [])
                if not pairs_list:
                    continue

                # Use the first valid pair on Solana
                pair = pairs_list[0]
                if pair.get("chainId") != "solana":
                    continue

                price_str = pair.get("priceUsd", "0")
                price = float(price_str) if price_str.replace('.', '', 1).isdigit() else 0
                liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0) or 0)
                volume_24h = float(pair.get("volume", {}).get("h24", 0) or 0)
                symbol = pair.get("baseToken", {}).get("symbol", "").upper() or mint[:8].upper()
                fdv = float(pair.get("fdv", 0) or 0)

                # Skip if no real price or < $10k liquidity
                if price <= 0 or liquidity_usd < 10000:
                    continue

                # Trending score combines boost position + liquidity
                trending_score = max(1, len(candidates) + 1)

                candidates.append({
                    "token": symbol,
                    "mint": mint,
                    "category": "meme",
                    "is_trending": True,
                    "trending_score": trending_score,
                    "current_price": price,
                    "liquidity_usd": liquidity_usd,
                    "volume_24h": volume_24h,
                    "fdv": fdv
                })
            except Exception:
                continue

            if len(candidates) >= count:
                break

        # Sort by liquidity (most liquid first = safer)
        candidates.sort(key=lambda x: x.get("liquidity_usd", 0), reverse=True)

        return candidates

    except Exception as e:
        print(f"Failed to fetch trending Solana candidates: {e}")
        return []


def get_usdc_balance():
    """Get USDC balance from blockchain via Helius RPC (no solders dependency)"""
    try:
        wallet = "7FNLUAQQd2NY88mG1ZqU8EDuNBVwvf2cWufxSnjwcgqA"
        helius_url = "https://mainnet.helius-rpc.com/?api-key=2e3fb808-0c5f-4101-8c2b-82b4c4aa0887"
        data = {
            "jsonrpc": "2.0", "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                wallet,
                {"mint": USDC},
                {"encoding": "jsonParsed"}
            ]
        }
        resp = requests.post(helius_url, json=data, headers={"Content-Type": "application/json"}, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            accounts = result.get("result", {}).get("value", [])
            if accounts:
                amount = float(accounts[0]["account"]["data"]["parsed"]["info"]["tokenAmount"]["uiAmount"] or 0)
                return amount
    except Exception as e:
        print(f"Failed to get USDC balance: {e}")
    return 0


def calculate_confidence(token, category, in_portfolio, momentum=None, pnl_pct=0, trailing_stop=None, mint_override=None, is_trending=False, trending_liquidity_usd=0):
    """Calculate confidence score 0-100 with momentum integration"""
    score = 50  # Base score

    mint = mint_override or TOKENS.get(token, {}).get("mint", "")

    # 1. Liquidity check (+10 if liquid) - use DexScreener data for trending tokens
    if is_trending and trending_liquidity_usd >= 10000:
        score += 10  # Confirmed liquid via DexScreener
    elif mint and get_jupiter_liquidity(mint):
        score += 10

    # 2. Trending status (+15 if trending on DexScreener)
    if is_trending:
        score += 15
    else:
        trending = check_coingecko_trending()
        if mint.upper() in trending:
            score += 15

    # 3. Bonus for strong volume on trending tokens (+5 if >100k volume)
    if is_trending and trending_liquidity_usd >= 50000:
        score += 5

    # 3. Category adjustment
    if category == "meme":
        score -= 5  # Higher risk
    elif category == "political_meme":
        score -= 10  # Even higher risk

    # 4. Momentum-based adjustments (NEW)
    if momentum:
        # Strong upward momentum = +15 confidence
        if momentum['trend'] == 'up' and momentum['momentum_pct'] > 0.03:
            score += 15
        # Moderate upward momentum = +10
        elif momentum['trend'] == 'up' and momentum['momentum_pct'] > 0.01:
            score += 10
        # Downward momentum = -15 confidence
        elif momentum['trend'] == 'down' and momentum['momentum_pct'] < -0.03:
            score -= 15
        # Moderate downward = -10
        elif momentum['trend'] == 'down' and momentum['momentum_pct'] < -0.01:
            score -= 10

        # Dip reversal detected = strong buy signal
        if momentum['reversal_type'] == 'dip' and momentum['reversal_confidence'] > 0.03:
            score += 20
        # Peak reversal detected = strong sell signal
        elif momentum['reversal_type'] == 'peak' and momentum['reversal_confidence'] > 0.03:
            score -= 20

    # 5. P&L-based adjustments for positions (NEW)
    if in_portfolio:
        # Profitable position = +5
        if pnl_pct > 0.05:
            score += 5
        # Highly profitable = +10
        if pnl_pct > 0.10:
            score += 10
        # Losing position = -10
        if pnl_pct < -0.03:
            score -= 10
        # Stop loss approaching = -20
        if pnl_pct < -0.05:
            score -= 20

        # Trailing stop triggered = major sell signal
        if trailing_stop and trailing_stop['should_trigger'] and pnl_pct > 0:
            score -= 30  # Strong sell signal

    # Clamp 0-100
    return max(0, min(100, score))

def get_recommendation(confidence, momentum=None, pnl_pct=0, trailing_stop=None):
    """Get trading recommendation based on confidence + momentum signals"""

    # Check for explicit momentum-based signals first
    if momentum:
        # Strong buy on dip reversal
        if momentum.get('reversal_type') == 'dip' and momentum.get('reversal_confidence', 0) > 0.03:
            return "STRONG_BUY"

        # Strong sell on peak reversal (if profitable)
        if momentum.get('reversal_type') == 'peak' and pnl_pct > 0.02:
            return "STRONG_SELL"

        # Sell on downward momentum
        if momentum.get('trend') == 'down' and momentum.get('momentum_pct', 0) < -0.03 and pnl_pct > 0:
            return "SELL"

    # Check trailing stop
    if trailing_stop and trailing_stop.get('should_trigger') and pnl_pct > 0:
        return "TRAILING_STOP_SELL"

    # Check P&L targets — but skip TP if momentum is still climbing
    if pnl_pct >= 0.15:  # 15% profit target
        # Momentum override: if still trending up >3% in last 15min, let it ride
        if momentum and momentum.get('trend') == 'up' and momentum.get('momentum_pct', 0) > 0.03:
            pass  # Skip TP — momentum is still strong
        else:
            return "TAKE_PROFIT"
    if pnl_pct <= -0.06:  # 6% stop loss
        return "STOP_LOSS"

    # Confidence-based recommendations
    if confidence >= 70:
        return "STRONG_BUY"
    elif confidence >= 50:
        return "BUY"
    elif confidence >= 30:
        return "HOLD"
    else:
        return "CONSIDER_EXIT"

def research_portfolio():
    """Research all portfolio positions with momentum analysis"""
    db = pdb.load_db()
    positions = [p for p in db.get("positions", []) if p.get("status") == "OPEN"]

    analyses = []

    for token, meta in TOKENS.items():
        in_portfolio = any(p.get("token") == token for p in positions)
        mint = meta.get("mint", "")

        # Get current price and record it
        current_price = get_jupiter_price(mint) if mint else 0
        if current_price > 0:
            record_price(token, current_price)

        # Calculate momentum
        momentum = calculate_momentum(token)

        # Get P&L if in portfolio
        pnl_pct = get_position_pnl(token, current_price) if in_portfolio else 0

        # Get trailing stop status if in portfolio
        trailing_stop = get_trailing_stop_status(token, current_price) if in_portfolio else None

        # Calculate confidence with all signals
        confidence = calculate_confidence(
            token=token,
            category=meta.get("category", "unknown"),
            in_portfolio=in_portfolio,
            momentum=momentum,
            pnl_pct=pnl_pct,
            trailing_stop=trailing_stop
        )

        # Get recommendation
        recommendation = get_recommendation(confidence, momentum, pnl_pct, trailing_stop)

        analysis = {
            "token": token,
            "mint": mint,
            "category": meta.get("category"),
            "confidence": confidence,
            "recommendation": recommendation,
            "in_portfolio": in_portfolio,
            "current_price": current_price,
            "momentum": momentum,
            "pnl_pct": pnl_pct * 100 if in_portfolio else 0,
            "trailing_stop": trailing_stop,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        analyses.append(analysis)

        # Update position with research data if in portfolio
        if in_portfolio:
            for i, pos in enumerate(db["positions"]):
                if pos.get("token") == token and pos.get("status") == "OPEN":
                    pos["research_confidence"] = confidence
                    pos["research_recommendation"] = recommendation
                    pos["current_price"] = current_price
                    pos["momentum"] = momentum
                    pos["pnl_pct"] = pnl_pct * 100
                    db["positions"][i] = pos

    # Analyze trending candidates alongside TOKENS
    trending_candidates = fetch_trending_solana_candidates(count=10)
    for tc in trending_candidates:
        token = tc["token"]
        mint = tc["mint"]

        in_portfolio = any(p.get("token") == token or p.get("mint") == mint for p in positions)
        current_price = tc.get("current_price", 0)
        if current_price > 0:
            record_price(token, current_price)

        momentum = calculate_momentum(token)
        pnl_pct = get_position_pnl(token, current_price) if in_portfolio else 0
        trailing_stop = get_trailing_stop_status(token, current_price) if in_portfolio else None

        confidence = calculate_confidence(
            token=token,
            category=tc.get("category", "meme"),
            in_portfolio=in_portfolio,
            momentum=momentum,
            pnl_pct=pnl_pct,
            trailing_stop=trailing_stop,
            mint_override=mint,
            is_trending=True,
            trending_liquidity_usd=tc.get("liquidity_usd", 0)
        )

        recommendation = get_recommendation(confidence, momentum, pnl_pct, trailing_stop)

        analysis = {
            "token": token,
            "mint": mint,
            "category": tc.get("category", "meme"),
            "confidence": confidence,
            "recommendation": recommendation,
            "in_portfolio": in_portfolio,
            "current_price": current_price,
            "momentum": momentum,
            "pnl_pct": pnl_pct * 100 if in_portfolio else 0,
            "trailing_stop": trailing_stop,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_trending": True,
            "trending_score": tc.get("trending_score", 1)
        }

        analyses.append(analysis)

        if in_portfolio:
            for i, pos in enumerate(db["positions"]):
                if pos.get("token") == token and pos.get("status") == "OPEN":
                    pos["research_confidence"] = confidence
                    pos["research_recommendation"] = recommendation
                    pos["current_price"] = current_price
                    pos["momentum"] = momentum
                    pos["pnl_pct"] = pnl_pct * 100
                    db["positions"][i] = pos

    # Save signals to DB
    db["signals"] = analyses
    pdb.save_db(db)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "analyses": analyses,
        "avg_confidence": sum(a["confidence"] for a in analyses) / len(analyses) if analyses else 0
    }

def get_buy_signals(min_confidence=50):
    """Get tokens with BUY/STRONG_BUY recommendation (excluding cooldown tokens)"""
    db = pdb.load_db()
    signals = db.get("signals", [])

    buy_recommendations = ["BUY", "STRONG_BUY"]

    # Load cooldowns - don't generate buy signals for recently sold tokens
    cooldown_path = os.path.join(os.path.dirname(__file__), "rebuy_cooldowns.json")
    cooldowns = {}
    if os.path.exists(cooldown_path):
        import json as _json
        with open(cooldown_path) as f:
            cooldowns = _json.load(f)

    now_utc = datetime.now(timezone.utc).isoformat()

    buy_signals = []
    for s in signals:
        if s.get("recommendation") not in buy_recommendations:
            continue
        if s.get("in_portfolio", False):
            continue  # already holding it
        if s.get("confidence", 0) < min_confidence:
            continue  # below confidence threshold

        mint = s.get("mint", "")
        # Check cooldown - skip tokens recently sold
        if mint in cooldowns:
            cooldown_entry = cooldowns[mint]
            if now_utc < cooldown_entry.get("cooldown_until", now_utc):
                continue  # still on cooldown

        buy_signals.append(s)

    # Sort by confidence (highest first)
    buy_signals.sort(key=lambda x: x.get("confidence", 0), reverse=True)

    return buy_signals

def get_sell_signals():
    """Get portfolio tokens with sell signals (momentum, P&L, trailing stop)"""
    db = pdb.load_db()
    signals = db.get("signals", [])

    sell_recommendations = [
        "STRONG_SELL", "SELL", "TAKE_PROFIT", "STOP_LOSS",
        "TRAILING_STOP_SELL", "CONSIDER_EXIT"
    ]

    sell_signals = [
        s for s in signals
        if s.get("recommendation") in sell_recommendations
        and s.get("in_portfolio", False)
    ]

    # Sort by urgency (trailing stop and stop loss first)
    def urgency(s):
        rec = s.get("recommendation", "")
        if rec in ["TRAILING_STOP_SELL", "STOP_LOSS"]:
            return 0  # Highest urgency
        elif rec in ["STRONG_SELL", "TAKE_PROFIT"]:
            return 1
        elif rec == "SELL":
            return 2
        else:
            return 3

    sell_signals.sort(key=urgency)

    return sell_signals

def get_swing_opportunities():
    """
    Get tokens with clear swing signals:
    - Buy: dip reversal detected
    - Sell: peak reversal detected or trailing stop triggered
    """
    db = pdb.load_db()
    signals = db.get("signals", [])

    swings = []

    for s in signals:
        momentum = s.get("momentum", {})

        # Buy opportunity: dip reversal
        if momentum.get("reversal_type") == "dip" and not s.get("in_portfolio"):
            swings.append({
                "token": s["token"],
                "action": "BUY",
                "reason": "DIP_REVERSAL",
                "confidence": s.get("confidence", 0),
                "momentum": momentum
            })

        # Sell opportunity: peak reversal (if holding)
        elif momentum.get("reversal_type") == "peak" and s.get("in_portfolio"):
            pnl = s.get("pnl_pct", 0)
            if pnl > 0:  # Only sell if profitable
                swings.append({
                    "token": s["token"],
                    "action": "SELL",
                    "reason": "PEAK_REVERSAL",
                    "confidence": s.get("confidence", 0),
                    "pnl_pct": pnl,
                    "momentum": momentum
                })

        # Trailing stop
        elif s.get("recommendation") == "TRAILING_STOP_SELL":
            swings.append({
                "token": s["token"],
                "action": "SELL",
                "reason": "TRAILING_STOP",
                "confidence": s.get("confidence", 0),
                "pnl_pct": s.get("pnl_pct", 0)
            })

    return swings

if __name__ == "__main__":
    result = research_portfolio()
    print(f"Research Complete: {result['timestamp']}")
    print(f"Avg Confidence: {result['avg_confidence']:.0f}/100")
    print("\nAll Analyses:")
    for a in result["analyses"]:
        portfolio_marker = " [PORTFOLIO]" if a["in_portfolio"] else ""
        momentum_info = ""
        if a.get("momentum"):
            mom = a["momentum"]
            momentum_info = f" | Momentum: {mom.get('trend', 'flat')} ({mom.get('momentum_pct', 0)*100:+.1f}%)"
            if mom.get("reversal_type"):
                momentum_info += f" | REVERSAL: {mom['reversal_type']}"
        if a.get("pnl_pct"):
            momentum_info += f" | P&L: {a['pnl_pct']:+.1f}%"
        print(f"  {a['token']}: {a['recommendation']} ({a['confidence']}/100){portfolio_marker}{momentum_info}")

    # Show swing opportunities
    swings = get_swing_opportunities()
    if swings:
        print(f"\n[SWING] OPPORTUNITIES: {len(swings)}")
        for s in swings:
            print(f"  {s['action']} {s['token']}: {s['reason']} (conf: {s['confidence']})")

    buy_signals = get_buy_signals()
    if buy_signals:
        print(f"\n[BUY] Signals: {[s['token'] for s in buy_signals]}")

    sell_signals = get_sell_signals()
    if sell_signals:
        print(f"\n[SELL] Signals: {[s['token'] for s in sell_signals]}")
