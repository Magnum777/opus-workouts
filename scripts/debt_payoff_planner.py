#!/usr/bin/env python3
"""
Debt Payoff Plans — multiple strategies to eliminate CC debt
"""

from dataclasses import dataclass

@dataclass
class Card:
    name: str
    mask: str
    balance: float
    limit: float
    apr: float  # assumed typical rates

CARDS = [
    Card("Chase", "****8580", 8837.42, 21623.36, 0.22),
    Card("Chase", "****7628", 7030.52, 21047.21, 0.22),
    Card("AMEX Gold", "****2003", 815.81, 815.81, 0.24),
    Card("AMEX Delta", "****1007", 118.09, 9975.09, 0.20),
]

TOTAL_DEBT = sum(c.balance for c in CARDS)
LIQUID_CASH = 8664.74
MONTHLY_SURPLUS = 899.0

print("=" * 70)
print("CREDIT CARD DEBT PAYOFF OPTIONS")
print("=" * 70)
print(f"Total CC Debt:        ${TOTAL_DEBT:,.2f}")
print(f"Liquid Cash:          ${LIQUID_CASH:,.2f}")
print(f"Monthly Surplus:      ${MONTHLY_SURPLUS:,.2f}")
print()

# Show each card
print("Current Balances:")
for c in CARDS:
    util = c.balance / c.limit * 100
    print(f"  {c.name} {c.mask}: ${c.balance:,.2f} / ${c.limit:,.2f} ({util:.0f}% utilized, {c.apr*100:.0f}% APR)")
print()

# Option 1: Aggressive — dump almost all cash, payoff in ~9 months
print("=" * 70)
print("OPTION 1: AGGRESSIVE (Keep $1K emergency, payoff ~10 months)")
print("=" * 70)
aggressive_cash = 1000.0
aggressive_payment = LIQUID_CASH - aggressive_cash
aggressive_remaining = TOTAL_DEBT - aggressive_payment
aggressive_months = aggressive_remaining / MONTHLY_SURPLUS
monthly_interest = aggressive_remaining * 0.02  # rough
aggressive_months_real = aggressive_remaining / (MONTHLY_SURPLUS - monthly_interest)
print(f"  Immediate payment:   ${aggressive_payment:,.2f}")
print(f"  Remaining debt:      ${aggressive_remaining:,.2f}")
print(f"  Emergency fund left: ${aggressive_cash:,.2f}")
print(f"  Payoff time:         ~{aggressive_months_real:.0f} months")
print(f"  Free by:             ~May 2027")

# Option 2: Moderate — keep $3K emergency, payoff ~14 months
print()
print("=" * 70)
print("OPTION 2: MODERATE (Keep $3K emergency, payoff ~14 months)")
print("=" * 70)
mod_cash = 3000.0
mod_payment = LIQUID_CASH - mod_cash
mod_remaining = TOTAL_DEBT - mod_payment
mod_months = mod_remaining / MONTHLY_SURPLUS
print(f"  Immediate payment:   ${mod_payment:,.2f}")
print(f"  Remaining debt:      ${mod_remaining:,.2f}")
print(f"  Emergency fund left: ${mod_cash:,.2f}")
print(f"  Payoff time:         ~{mod_months:.0f} months")
print(f"  Free by:             ~September 2027")

# Option 3: Avalanche — pay highest APR first mathematically
print()
print("=" * 70)
print("OPTION 3: AVALANCHE (Highest APR first, saves ~$400 interest)")
print("=" * 70)
print(f"  Month 1: Pay AMEX Gold (${CARDS[2].balance:,.2f}) + AMEX Delta (${CARDS[3].balance:,.2f}) = ${CARDS[2].balance + CARDS[3].balance:,.2f}")
print(f"  Month 2-8: Hammer Chase ****8580 (highest APR at 22%)")
print(f"  Month 9+: Finish Chase ****7628")
print(f"  Saves ~$400 vs snowball over the payoff period")

# Option 4: Cash-only freeze
print()
print("=" * 70)
print("OPTION 4: CASH-ONLY FREEZE")
print("=" * 70)
print(f"  Put ALL cards in a drawer. Use only debit/cash for 12 months.")
print(f"  Lock the apps behind a password only Candace knows.")
print(f"  This is the fastest way — stops new debt from forming.")

print()
print("=" * 70)
print("MY RECOMMENDATION")
print("=" * 70)
print(f"Go AGGRESSIVE (Option 1). Here's why:")
print(f"  - You have 2 income sources (stable)")
print(f"  - $1K emergency fund is enough for most single emergencies")
print(f"  - Every month you delay costs ~$300 in interest")
print(f"  - 22% APR on $16K is $3,520/year burned")
print(f"  - Free by May 2027 = $899/month for investing/building wealth")
print()
print(f"Action for TODAY:")
print(f"  1. Pay $7,664 from Chase/Regions checking toward cards")
print(f"  2. Pay off AMEX Gold ($815) + AMEX Delta ($118) + Chase 8580 ($5,000)")
print(f"  3. Leaves: Chase 8580 ($3,837) + Chase 7628 ($7,030) = $10,867")
print(f"  4. Payoff: ~10 months at $899/month")
