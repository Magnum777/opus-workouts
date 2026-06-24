#!/usr/bin/env python3
"""
Portfolio Verification Script
==============================
Compares the portfolio DB against live on-chain data and reports discrepancies.
Can be run as a cron job or manually.

Usage:
    python verify_portfolio.py              # Quick check, report discrepancies
    python verify_portfolio.py --fix        # Auto-fix discrepancies by refreshing from on-chain
    python verify_portfolio.py --json       # Output as JSON (for programmatic use)
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

# Add trading-bot to path
sys.path.insert(0, os.path.dirname(__file__))
import portfolio_tracker as pt

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db.json")


def verify_and_report(fix=False, json_output=False):
    """Run verification and report results."""
    db = pt.load_db()
    discrepancies, onchain = pt.verify_db_against_onchain(db)

    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "onchain_total": onchain["total_value_usd"],
        "db_total": db["portfolio"]["total_value_usd"],
        "discrepancy_count": len(discrepancies),
        "discrepancies": discrepancies,
        "fixed": False
    }

    if discrepancies and fix:
        print(f"🔧 Auto-fixing {len(discrepancies)} discrepancies...")
        db = pt.refresh_from_onchain(db)
        result["fixed"] = True
        # Re-verify
        discrepancies2, onchain2 = pt.verify_db_against_onchain(db)
        result["post_fix_discrepancies"] = discrepancies2
        result["post_fix_total"] = onchain2["total_value_usd"]

    if json_output:
        print(json.dumps(result, indent=2))
        return

    # Human-readable output
    print(f"\n{'='*60}")
    print(f"  PORTFOLIO VERIFICATION REPORT")
    print(f"  {result['timestamp']}")
    print(f"{'='*60}")
    print(f"  On-chain total: ${result['onchain_total']:.2f}")
    print(f"  DB total:       ${result['db_total']:.2f}")
    diff = result['onchain_total'] - result['db_total']
    print(f"  Difference:     ${diff:+.2f}")

    if result["discrepancy_count"] == 0:
        print(f"\n  [OK] PORTFOLIO IS ACCURATE - No discrepancies found")
    else:
        print(f"\n  [WARN]  {result['discrepancy_count']} DISCREPANCIES FOUND:")
        for d in result["discrepancies"]:
            print(f"    • {d}")

    if result.get("fixed"):
        print(f"\n  🔧 Auto-fix applied. Post-fix discrepancies: {len(result.get('post_fix_discrepancies', []))}")
        if result.get("post_fix_discrepancies"):
            for d in result["post_fix_discrepancies"]:
                print(f"    • {d}")
        else:
            print(f"  [OK] All discrepancies resolved!")

    print(f"{'='*60}\n")


def main():
    args = sys.argv[1:]
    fix = "--fix" in args
    json_output = "--json" in args

    verify_and_report(fix=fix, json_output=json_output)


if __name__ == "__main__":
    main()
