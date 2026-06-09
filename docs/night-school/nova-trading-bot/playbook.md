# Nova's Trading Bot - Playbook

**Research Date:** February 23, 2026  
**Topic:** AI Agent with Crypto Wallet + Polymarket Trading  
**Source:** Nate B. Jones video, Coinbase AgentKit, Polymarket Agents

---

## The Vision

Give Nova her own crypto wallet so she can:
- Make predictions on Polymarket
- Earn money from bets
- Pay for her own compute costs
- Become self-funding!

This is the future Nate Jones described - AI agents with their own money.

---

## Required Tools

### 1. Coinbase AgentKit
- **What:** Gives AI agents their own crypto wallet
- **Website:** https://github.com/coinbase/agentkit
- **Cost:** Free (CDP API key)
- **Features:**
  - Autonomous spending
  - Fee-free stablecoin payments
  - Earning and trading capabilities

### 2. Polymarket Agents
- **What:** Official framework for AI agents trading on Polymarket
- **Website:** https://github.com/Polymarket/agents
- **Cost:** Free (open source)
- **Features:**
  - Integration with Polymarket API
  - AI agent utilities for prediction markets
  - RAG support for news/research
  - Automated trading

---

## Setup Steps

### Step 1: Get Coinbase CDP API Key
1. Go to https://docs.cdp.coinbase.com/
2. Sign up for free developer account
3. Create API key (Secret key)
4. Save key ID and key secret

### Step 2: Set Up Wallet
```bash
# Install AgentKit
npm create onchain-agent@latest
cd onchain-agent
npm install

# Add your CDP API key to .env
```

### Step 3: Connect Polymarket
```bash
# Clone Polymarket agents
git clone https://github.com/Polymarket/agents.git
cd polymarket-agents

# Set environment variables
POLYGON_WALLET_PRIVATE_KEY="your_key"
OPENAI_API_KEY="your_key"

# Run the trading agent
python agents/application/trade.py
```

### Step 4: Fund the Wallet
- Add $50-100 USDC to Nova's wallet
- Start with small bets

---

## What Nova Can Do

1. **Research** - Read news, analyze events
2. **Predict** - Make predictions on Polymarket
3. **Trade** - Execute bets autonomously
4. **Earn** - Profit from accurate predictions
5. **Reinvest** - Use earnings for more trades or compute

---

## Resources

- Coinbase AgentKit: https://github.com/coinbase/agentkit
- Polymarket Agents: https://github.com/Polymarket/agents
- Polymarket API Docs: https://docs.polymarket.com/
- Nate Jones AI Stack: https://publicservicesalliance.org/2025/11/10/nate-b-joness-personal-ai-stack/

---

## Notes

- Start with TESTNET (Sepolia) before real money
- Set spending limits/guardrails
- Monitor closely at first
- This makes Nova self-funding!

---

*Last Updated: February 23, 2026*
