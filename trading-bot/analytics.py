#!/usr/bin/env python3
"""
TradeBot Analytics - Weekly Performance Report
Reads portfolio DB and generates key metrics.
"""

import json
import os
from datetime import datetime, timezone, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db.json")

def load_db():
    if not os.path.exists(DB_PATH):
        return None
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def generate_report():
    db = load_db()
    if not db:
        return {"error": "No portfolio database found"}
    
    positions = db.get("positions", [])
    trades = db.get("trades", [])
    perf = db.get("performance", {})
    portfolio = db.get("portfolio", {})
    
    # Separate open/closed
    open_positions = [p for p in positions if p.get("status") == "OPEN"]
    closed_positions = [p for p in positions if p.get("status") == "CLOSED"]
    
    # Win rate from closed trades
    profitable = [p for p in closed_positions if p.get("realized_pnl_usd", 0) > 0]
    losing = [p for p in closed_positions if p.get("realized_pnl_usd", 0) <= 0]
    win_rate = (len(profitable) / len(closed_positions) * 100) if closed_positions else 0
    
    # PnL stats
    total_rpnl = sum(p.get("realized_pnl_usd", 0) for p in closed_positions)
    total_upnl = sum(p.get("unrealized_pnl_usd", 0) for p in open_positions)
    
    best_trade = max(closed_positions, key=lambda p: p.get("realized_pnl_usd", 0), default=None)
    worst_trade = min(closed_positions, key=lambda p: p.get("realized_pnl_usd", 0), default=None)
    
    # Streaks — use closed positions sorted by close time
    streaks = {"current": 0, "best_win": 0, "best_loss": 0, "current_type": None}
    if closed_positions:
        sorted_closed = sorted(
            closed_positions,
            key=lambda p: p.get("closed_at", p.get("updated_at", p.get("created_at", ""))) or ""
        )
        
        current_streak = 0
        current_type = None
        max_win_streak = 0
        max_loss_streak = 0
        
        for p in sorted_closed:
            pnl = p.get("realized_pnl_usd", 0)
            ttype = "win" if pnl > 0 else "loss"
            
            if ttype == current_type:
                current_streak += 1
            else:
                current_type = ttype
                current_streak = 1
            
            if ttype == "win":
                max_win_streak = max(max_win_streak, current_streak)
            else:
                max_loss_streak = max(max_loss_streak, current_streak)
        
        streaks["current"] = current_streak
        streaks["current_type"] = current_type
        streaks["best_win"] = max_win_streak
        streaks["best_loss"] = max_loss_streak
    
    # Portfolio value breakdown
    total_value = portfolio.get("total_value_usd", 0)
    usdc = portfolio.get("usdc_balance", 0)
    sol = portfolio.get("sol_balance", 0)
    sol_price = portfolio.get("sol_price_usd", 0)
    
    # Build report
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_value_usd": round(total_value, 2),
            "usdc_balance": round(usdc, 2),
            "sol_balance": round(sol, 4),
            "sol_price": round(sol_price, 2),
            "open_positions": len(open_positions),
            "closed_trades": len(closed_positions),
        },
        "performance": {
            "total_realized_pnl": round(total_rpnl, 2),
            "total_unrealized_pnl": round(total_upnl, 2),
            "win_rate": round(win_rate, 1),
            "profitable_trades": len(profitable),
            "losing_trades": len(losing),
        },
        "streaks": streaks,
        "best_trade": {
            "token": best_trade.get("token") if best_trade else None,
            "pnl": round(best_trade.get("realized_pnl_usd", 0), 2) if best_trade else 0
        },
        "worst_trade": {
            "token": worst_trade.get("token") if worst_trade else None,
            "pnl": round(worst_trade.get("realized_pnl_usd", 0), 2) if worst_trade else 0
        },
        "open_positions_detail": [
            {
                "token": p.get("token"),
                "value_usd": round(p.get("current_value_usd", 0), 2),
                "unrealized_pnl": round(p.get("unrealized_pnl", 0), 2),
                "pnl_pct": round(p.get("pnl_pct", 0), 1)
            }
            for p in open_positions
        ]
    }
    
    return report

def format_discord(report):
    """Format report for Discord."""
    lines = []
    lines.append("**TradeBot Weekly Analytics**")
    lines.append("")
    
    s = report["summary"]
    lines.append(f"Portfolio: **${s['total_value_usd']:.2f}** | USDC: ${s['usdc_balance']:.2f} | SOL: {s['sol_balance']:.4f} (${s['sol_balance']*s['sol_price']:.2f})")
    lines.append(f"Open: {s['open_positions']} | Closed: {s['closed_trades']}")
    lines.append("")
    
    p = report["performance"]
    lines.append(f"Realized PnL: **${p['total_realized_pnl']:.2f}** | Unrealized: ${p['total_unrealized_pnl']:.2f}")
    lines.append(f"Win Rate: **{p['win_rate']:.0f}%** ({p['profitable_trades']}W/{p['losing_trades']}L)")
    lines.append("")
    
    streak = report["streaks"]
    if streak.get("current_type"):
        emoji = "[WIN]" if streak["current_type"] == "win" else "[LOSS]"
        lines.append(f"Current Streak: {emoji} {streak['current']} {streak['current_type']}s")
    lines.append(f"Best Win Streak: {streak['best_win']} | Worst Loss Streak: {streak['best_loss']}")
    lines.append("")
    
    if report["best_trade"]["token"]:
        lines.append(f"Best: {report['best_trade']['token']} +${report['best_trade']['pnl']:.2f}")
    if report["worst_trade"]["token"]:
        lines.append(f"Worst: {report['worst_trade']['token']} ${report['worst_trade']['pnl']:.2f}")
    
    if report["open_positions_detail"]:
        lines.append("")
        lines.append("**Open Positions:**")
        for pos in report["open_positions_detail"]:
            emoji = "[+]" if pos["unrealized_pnl"] >= 0 else "[-]"
            lines.append(f"{emoji} {pos['token']}: ${pos['value_usd']:.2f} ({pos['pnl_pct']:+.1f}%)")
    
    return "\n".join(lines)

def main():
    import sys
    report = generate_report()
    
    if "error" in report:
        print(report["error"])
        sys.exit(1)
    
    if "--json" in sys.argv:
        print(json.dumps(report, indent=2))
    else:
        print(format_discord(report))

if __name__ == "__main__":
    main()
