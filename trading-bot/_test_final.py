"""Test trending scanner + buy sizing"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

os.chdir(r"C:\Users\compj\.openclaw\workspace\trading-bot")

print("=== TEST 1: Trending Candidates ===")
try:
    import research_v2
    candidates = research_v2.fetch_trending_solana_candidates(count=5)
    print(f"Found {len(candidates)} trending Solana candidates:")
    for c in candidates:
        print(f"  {c['token']:10s} ${c['current_price']:<10.6f} liq=${c.get('liquidity_usd',0):<10.2f} vol24h=${c.get('volume_24h',0):<10.2f} mint={c['mint'][:12]}...")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()

print("\n=== TEST 2: Research Portfolio ===")
try:
    result = research_v2.research_portfolio()
    print(f"Analyses: {len(result['analyses'])}")
    for a in result['analyses']:
        print(f"  {a['token']:12s} {a['recommendation']:15s} (conf={a['confidence']}) {'TRENDING' if a.get('is_trending') else ''}")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()

print("\n=== TEST 3: Buy Sizing ===")
try:
    import executor_v2
    # Simulate $84 balance
    test_sigs = [
        ("STANDARD", {"recommendation": "BUY", "confidence": 50, "momentum": {"trend": "flat", "momentum_pct": 0}}),
        ("MEDIUM", {"recommendation": "BUY", "confidence": 58, "momentum": {"trend": "up", "momentum_pct": 0.01}}),
        ("STRONG", {"recommendation": "BUY", "confidence": 65, "momentum": {"trend": "up", "momentum_pct": 0.03}}),
        ("MAX", {"recommendation": "STRONG_BUY", "confidence": 70, "momentum": {"trend": "up", "momentum_pct": 0.05}}),
    ]
    for name, sig in test_sigs:
        size = executor_v2.determine_buy_size(sig)
        print(f"  {name:10s} -> ${size:.2f}")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()