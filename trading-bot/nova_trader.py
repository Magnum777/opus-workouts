"""
Nova's Trading Bot - Complete Edition
Features: Notion, Price Alerts, Portfolio, Strategies, Stop Loss, Take Profit, Daily Reports
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from web3 import Web3
from eth_account import Account
import requests
import time

# Configuration
RPC_URL = "https://base.llamarpc.com"
WALLET_ADDRESS = os.environ.get("BASE_WALLET_ADDRESS", "")
PRIVATE_KEY = os.environ.get("BASE_PRIVATE_KEY", "")

# Trading config
TRADE_SIZE_ETH = 0.001
TRADE_SIZE_USDC = 10  # $10 worth
NOTION_DB_ID = "31035ead-c48d-81c7-87b2-f9b70d9c91b5"

# USDC on Base (Wrapped USDC)
USDC_ADDRESS = "0x4ed4e862860bed51a9570b96d89af5e1b0efefed"  # Wrapped USDC on Base

# Initialize
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = Account.from_key(PRIVATE_KEY)

class NovaTrader:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        self.account = Account.from_key(PRIVATE_KEY)
        self.wallet = self.account.address
        self.trades = []
        self.is_paper = True
        self.portfolio = {}
        self.price_alerts = []
        self.strategy = "dca"  # dca, momentum, mean_reversion
        self.stop_loss_pct = 0.05  # 5%
        self.take_profit_pct = 0.10  # 10%
        
    # ============ CORE FUNCTIONS ============
    
    def get_balance(self):
        """Get ETH balance"""
        balance = self.w3.eth.get_balance(self.wallet)
        return float(self.w3.from_wei(balance, 'ether'))
    
    def get_usdc_balance(self):
        """Get USDC balance"""
        # Simplified - would need proper ERC-20 call
        return 0.0  # Would query USDC contract
    
    def get_eth_price(self):
        """Get ETH price in USD"""
        try:
            resp = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": "ethereum", "vs_currencies": "usd"},
                timeout=10
            )
            return resp.json()["ethereum"]["usd"]
        except:
            return 2500
    
    def get_portfolio_value(self):
        """Get total portfolio value"""
        eth_balance = self.get_balance()
        usdc_balance = self.get_usdc_balance()
        eth_price = self.get_eth_price()
        
        return {
            "eth": eth_balance,
            "usdc": usdc_balance,
            "usd": (eth_balance * eth_price) + usdc_balance,
            "eth_price": eth_price
        }
    
    # ============ TRADING STRATEGIES ============
    
    def strategy_dca(self, price):
        """Dollar Cost Average - buy small amounts regularly"""
        return {
            "action": "buy",
            "amount": TRADE_SIZE_ETH,
            "reason": "DCA buy - regular investment"
        }
    
    def strategy_momentum(self, price, history):
        """Buy on momentum - price going up"""
        if len(history) < 2:
            return {"action": "hold", "amount": 0, "reason": "Need more data"}
        
        if history[-1] > history[-2]:
            return {
                "action": "buy",
                "amount": TRADE_SIZE_ETH,
                "reason": "Momentum bullish"
            }
        return {"action": "hold", "amount": 0, "reason": "Momentum bearish"}
    
    def strategy_mean_reversion(self, price, history):
        """Buy when price is below average"""
        if len(history) < 10:
            return {"action": "hold", "amount": 0, "reason": "Need more data"}
        
        avg = sum(history) / len(history)
        if price < avg * 0.95:
            return {
                "action": "buy",
                "amount": TRADE_SIZE_ETH,
                "reason": f"Price ${price:.2f} below avg ${avg:.2f}"
            }
        return {"action": "hold", "amount": 0, "reason": "Price near average"}
    
    # ============ RISK MANAGEMENT ============
    
    def check_stop_loss(self, entry_price, current_price):
        """Check if stop loss triggered"""
        loss_pct = (current_price - entry_price) / entry_price
        if loss_pct <= -self.stop_loss_pct:
            return True, "STOP LOSS"
        return False, None
    
    def check_take_profit(self, entry_price, current_price):
        """Check if take profit triggered"""
        profit_pct = (current_price - entry_price) / entry_price
        if profit_pct >= self.take_profit_pct:
            return True, "TAKE PROFIT"
        return False, None
    
    # ============ PRICE ALERTS ============
    
    def add_alert(self, target_price, direction, message=""):
        """Add a price alert"""
        alert = {
            "target": target_price,
            "direction": direction,  # "above" or "below"
            "message": message,
            "created": datetime.now().isoformat(),
            "triggered": False
        }
        self.price_alerts.append(alert)
        return alert
    
    def check_alerts(self, current_price):
        """Check if any alerts triggered"""
        triggered = []
        for alert in self.price_alerts:
            if alert["triggered"]:
                continue
            
            if alert["direction"] == "above" and current_price >= alert["target"]:
                alert["triggered"] = True
                triggered.append(alert)
            elif alert["direction"] == "below" and current_price <= alert["target"]:
                alert["triggered"] = True
                triggered.append(alert)
        
        return triggered
    
    # ============ NOTION INTEGRATION ============
    
    def log_to_notion(self, trade_data):
        """Log trade to Notion (simulated)"""
        # In production, use Notion API
        print(f"[NOTION] Trade logged: {trade_data}")
        return {"status": "logged", "data": trade_data}
    
    def log_to_file(self, trade_data):
        """Log to local file"""
        filename = "trading-bot/trades.json"
        os.makedirs("trading-bot", exist_ok=True)
        
        # Load existing
        trades = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                trades = json.load(f)
        
        trades.append(trade_data)
        
        with open(filename, 'w') as f:
            json.dump(trades, f, indent=2)
        
        return {"status": "saved", "file": filename}
    
    # ============ TRADING ============
    
    def execute_trade(self, action, amount, price, reason=""):
        """Execute a trade"""
        if self.is_paper:
            result = {
                "status": "paper",
                "action": action,
                "amount": amount,
                "price": price,
                "value": amount * price,
                "reason": reason
            }
        else:
            # Real trading would go here
            result = {
                "status": "live",
                "action": action,
                "amount": amount,
                "price": price,
                "value": amount * price,
                "reason": reason,
                "note": "Live trading not implemented yet"
            }
        
        # Always log
        self.log_to_file(result)
        
        return result
    
    # ============ ANALYSIS ============
    
    async def analyze_and_trade(self):
        """Main analysis and trading logic"""
        price = self.get_eth_price()
        portfolio = self.get_portfolio_value()
        
        # Check price alerts
        alerts_triggered = self.check_alerts(price)
        
        # Get recommendation based on strategy
        history = []  # Would fetch from API in production
        
        if self.strategy == "dca":
            signal = self.strategy_dca(price)
        elif self.strategy == "momentum":
            signal = self.strategy_momentum(price, history)
        elif self.strategy == "mean_reversion":
            signal = self.strategy_mean_reversion(price, history)
        else:
            signal = {"action": "hold", "amount": 0, "reason": "Unknown strategy"}
        
        # Execute if signal says buy and we have balance
        if signal["action"] == "buy" and portfolio["eth"] > TRADE_SIZE_ETH:
            result = self.execute_trade("buy", signal["amount"], price, signal["reason"])
        elif signal["action"] == "sell":
            result = self.execute_trade("sell", signal["amount"], price, signal["reason"])
        else:
            result = {"action": "hold", "reason": signal.get("reason", "No signal")}
        
        return {
            "price": price,
            "portfolio": portfolio,
            "signal": signal,
            "trade": result,
            "alerts": alerts_triggered
        }
    
    # ============ DAILY REPORT ============
    
    def daily_report(self):
        """Generate daily report"""
        portfolio = self.get_portfolio_value()
        
        report = {
            "date": datetime.now().isoformat(),
            "portfolio": portfolio,
            "trades_today": len([t for t in self.trades if 
                t.get("date", "").startswith(datetime.now().strftime("%Y-%m-%d"))]),
            "alerts": len(self.price_alerts),
            "alerts_triggered": len([a for a in self.price_alerts if a["triggered"]]),
            "strategy": self.strategy,
            "mode": "paper" if self.is_paper else "live"
        }
        
        return report


async def main():
    bot = NovaTrader()
    
    print("=" * 60)
    print("Nova's Trading Bot - Complete Edition")
    print("=" * 60)
    
    # Portfolio
    portfolio = bot.get_portfolio_value()
    print("\nPortfolio:")
    print(f"   ETH: {portfolio['eth']:.4f}")
    print(f"   USDC: ${portfolio['usdc']:.2f}")
    print(f"   Total USD: ${portfolio['usd']:.2f}")
    print(f"   ETH Price: ${portfolio['eth_price']:.2f}")
    
    # Strategy
    print(f"\nStrategy: {bot.strategy.upper()}")
    print(f"   Stop Loss: {bot.stop_loss_pct*100}%")
    print(f"   Take Profit: {bot.take_profit_pct*100}%")
    
    # Test alerts
    bot.add_alert(2000, "above", "Take some profit")
    bot.add_alert(1800, "below", "Buy more")
    print(f"\nPrice Alerts: {len(bot.price_alerts)}")
    
    # Test analysis
    print(f"\nRunning analysis...")
    result = await bot.analyze_and_trade()
    print(f"   Signal: {result['signal']['action']}")
    print(f"   Reason: {result['signal'].get('reason', 'N/A')}")
    print(f"   Trade: {result['trade']}")
    
    # Daily report
    report = bot.daily_report()
    print(f"\nDaily Report:")
    print(f"   Trades today: {report['trades_today']}")
    print(f"   Mode: {report['mode']}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
