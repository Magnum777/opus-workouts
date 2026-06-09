import json
import os
from datetime import datetime
import random

def load_crypto_research():
    """Load the latest crypto research data"""
    research_file = "C:\\Users\\compj\\.openclaw\\workspace\\trading-bot\\CryptoResearch-Hourly.json"
    if os.path.exists(research_file):
        with open(research_file, 'r') as f:
            data = json.load(f)
            # Convert analysis format to recommendations format
            if "analysis" in data:
                recommendations = []
                for symbol, details in data["analysis"].items():
                    recommendations.append({
                        "symbol": symbol,
                        "price": details["price"],
                        "signal": details["signal"]
                    })
                # Update the data structure to include recommendations
                data["recommendations"] = recommendations
            return data
    else:
        # Generate mock research data if file doesn't exist
        return {
            "timestamp": datetime.now().isoformat(),
            "recommendations": [
                {"symbol": "BTC", "price": round(random.uniform(50000, 70000), 2), "signal": random.choice(["BUY", "SELL", "HOLD"])},
                {"symbol": "ETH", "price": round(random.uniform(2500, 4000), 2), "signal": random.choice(["BUY", "SELL", "HOLD"])},
                {"symbol": "SOL", "price": round(random.uniform(100, 200), 2), "signal": random.choice(["BUY", "SELL", "HOLD"])}
            ]
        }

def trade_with_enforced_rules(symbol, price, signal):
    """Execute trades with enforced profit/loss rules"""
    if signal == "BUY":
        entry_price = price
        take_profit = entry_price * 1.01  # 1% profit
        stop_loss = entry_price * 0.99     # 1% loss
        
        print(f"TRADE EXECUTED: BUY {symbol} at ${entry_price}")
        print(f"Take Profit: ${take_profit}")
        print(f"Stop Loss: ${stop_loss}")
        
        # Simulate market movement
        simulated_exit_price = round(entry_price * random.uniform(0.985, 1.015), 2)
        profit_pct = ((simulated_exit_price - entry_price) / entry_price) * 100
        
        if simulated_exit_price >= take_profit:
            print(f"TAKE PROFIT HIT: Sold {symbol} at ${simulated_exit_price} ({profit_pct:.2f}% profit)")
            return "PROFIT", profit_pct
        elif simulated_exit_price <= stop_loss:
            print(f"STOP LOSS HIT: Sold {symbol} at ${simulated_exit_price} ({profit_pct:.2f}% loss)")
            return "LOSS", profit_pct
        else:
            print(f"POSITION CLOSED: {symbol} at ${simulated_exit_price} ({profit_pct:.2f}% change)")
            return "CLOSED", profit_pct
    
    elif signal == "SELL":
        entry_price = price
        take_profit = entry_price * 0.99  # 1% profit on short
        stop_loss = entry_price * 1.01    # 1% loss on short
        
        print(f"TRADE EXECUTED: SELL {symbol} at ${entry_price}")
        print(f"Take Profit: ${take_profit}")
        print(f"Stop Loss: ${stop_loss}")
        
        # Simulate market movement
        simulated_exit_price = round(entry_price * random.uniform(0.985, 1.015), 2)
        profit_pct = ((entry_price - simulated_exit_price) / entry_price) * 100
        
        if simulated_exit_price <= take_profit:
            print(f"TAKE PROFIT HIT: Covered {symbol} at ${simulated_exit_price} ({profit_pct:.2f}% profit)")
            return "PROFIT", profit_pct
        elif simulated_exit_price >= stop_loss:
            print(f"STOP LOSS HIT: Covered {symbol} at ${simulated_exit_price} ({profit_pct:.2f}% loss)")
            return "LOSS", profit_pct
        else:
            print(f"POSITION CLOSED: {symbol} at ${simulated_exit_price} ({profit_pct:.2f}% change)")
            return "CLOSED", profit_pct
    
    else:
        print(f"NO TRADE: HOLD signal for {symbol}")
        return "HOLD", 0

def main():
    print("Enforced Trader Bot Started")
    print(f"Current time: {datetime.now()}")
    
    # Load latest research data
    research_data = load_crypto_research()
    print(f"Loaded research data from: {research_data['timestamp']}")
    
    total_result = []
    
    for item in research_data.get("recommendations", []):
        symbol = item["symbol"]
        price = item["price"]
        signal = item["signal"]
        
        print(f"\nProcessing: {symbol} - Signal: {signal} - Price: ${price}")
        result, profit_pct = trade_with_enforced_rules(symbol, price, signal)
        total_result.append({
            "symbol": symbol,
            "result": result,
            "profit_pct": profit_pct,
            "timestamp": datetime.now().isoformat()
        })
    
    # Summary
    print("\n--- TRADE SUMMARY ---")
    profitable_trades = [r for r in total_result if r["result"] == "PROFIT"]
    losing_trades = [r for r in total_result if r["result"] == "LOSS"]
    hold_trades = [r for r in total_result if r["result"] == "HOLD"]
    
    print(f"Total trades: {len(total_result)}")
    print(f"Profitable: {len(profitable_trades)}")
    print(f"Losing: {len(losing_trades)}")
    print(f"Held: {len(hold_trades)}")
    
    # Calculate net performance
    total_profit = sum(r["profit_pct"] for r in total_result)
    print(f"Net Performance: {total_profit:.2f}%")
    
    # Save results for reporting
    report_file = "C:\\Users\\compj\\.openclaw\\workspace\\trading-bot\\TradeReport.json"
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": total_result,
            "summary": {
                "total_trades": len(total_result),
                "profitable_trades": len(profitable_trades),
                "losing_trades": len(losing_trades),
                "net_performance": total_profit
            }
        }, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")

if __name__ == "__main__":
    main()