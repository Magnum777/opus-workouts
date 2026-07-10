from datetime import datetime, timedelta

# REAL MODEL: Monthly cash flow with credit card float

# Income
james_monthly = 4879 * 2.166  # biweekly to monthly
candace_monthly = 2375 * 2    # semi-monthly
total_income = james_monthly + candace_monthly

# Fixed bills from checking
fixed_monthly = {
    'mortgage': 1258,
    'school': 845,
    'car_loan': 217,
    'student_loan': 139,
    'electric': 305,
    'phone': 226,
    'internet': 60,
    'church': 430,
    'whitney': 110,
    'subscriptions': 340,
}

# Credit card float (what you spend on cards, then pay from checking)
cc_monthly_spend = 7500  # target variable spending on cards

# Savings
monthly_savings = 800

# Calculate
total_fixed = sum(fixed_monthly.values())
total_outflow = total_fixed + cc_monthly_spend + monthly_savings
surplus = total_income - total_outflow

print("=" * 70)
print("MONTHLY CASH FLOW (Corrected for CC Float)")
print("=" * 70)
print()
print("INCOME")
print(f"  James (biweekly ${4879:.0f}):     ${james_monthly:,.2f}/month")
print(f"  Candace (semi-monthly ${2375:.0f}): ${candace_monthly:,.2f}/month")
print(f"  TOTAL:                          ${total_income:,.2f}/month")
print()
print("CHECKING OUTFLOWS")
print(f"  Fixed bills:                    ${total_fixed:,.2f}/month")
for name, amt in fixed_monthly.items():
    print(f"    {name:25} ${amt:,.2f}")
print()
print("  CC Statement Balance (paid in full):")
print(f"    Daily spending on cards:        ${cc_monthly_spend:,.2f}/month")
print(f"    (groceries, dining, shopping, gas, travel)")
print()
print("  Savings auto-transfer:            ${monthly_savings:,.2f}/month")
print()
print(f"  TOTAL OUTFLOW:                    ${total_outflow:,.2f}/month")
print()
print("=" * 70)
print(f"SURPLUS:                            ${surplus:,.2f}/month")
print("=" * 70)
print()

if surplus > 0:
    print("GOOD: This works. You're breaking even or better.")
    print(f"Extra each month: ${surplus:,.2f} for buffer/investing")
else:
    print("PROBLEM: Spending exceeds income.")
    print("Need to cut variable spending or increase income.")

print()
print("THE ACTUAL QUESTION:")
print(f"Are you currently paying ${cc_monthly_spend:,.0f} on cards AND ${total_fixed:,.0f} in bills from ${total_income:,.0f} income?")
print()
print("If yes: You should have ${:.0f} left over each month.".format(surplus))
print("If no: The $7500 target is wrong — need real data.")
