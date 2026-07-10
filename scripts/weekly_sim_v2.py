from datetime import datetime, timedelta

# CORRECTED MODEL: You live off credit cards
# Checking only pays: fixed bills + CC statement balances + savings
# Credit cards pay: groceries, dining, shopping, travel, gas

james_pay = 4879
candace_pay = 2375
checking = 4070  # Chase checking
savings = 4179   # Regions emergency + other savings

# Credit card total balances (what gets spent on cards each month, then paid)
cc_balances = {
    'chase_8580': 8837,
    'chase_7628': 7030,
    'amex_gold': 815,
    'amex_delta': 118,
}

# Fixed bills that auto-draft from CHECKING
fixed_monthly = {
    'mortgage': 1258,      # Truist - due ~3rd
    'school': 845,         # Foundation Academy - weekly, ~$195/week
    'car_loan': 217,       # Truist - due ~22nd
    'student_loan': 139,   # Dept Ed - due ~4th
    'electric': 305,       # Flint - due ~2nd
    'phone': 226,          # Verizon - due ~6th
    'internet': 60,        # Cox - due ~15th
    'church': 430,         # Sojourn - weekly, ~$100/week
    'whitney': 110,        # Unknown - monthly
}

# Savings transfers
save_james = 250   # per paycheck
save_candace = 250  # per paycheck

# Pay dates
james_date = datetime(2026, 7, 10)  # biweekly Friday
candace_date = datetime(2026, 7, 15)  # 15th and last day

start = datetime(2026, 7, 9)

print('=' * 100)
print('6-MONTH CASH FLOW: Credit Card Float Model')
print('=' * 100)
print()
print('ASSUMPTION: You live off credit cards for daily spending.')
print('Checking only pays: fixed bills + CC statement balances + savings')
print()
print(f'Fixed bills from checking: ${sum(fixed_monthly.values()):,.0f}/month')
print(f'CC balances (monthly float): ${sum(cc_balances.values()):,.0f}')
print(f'James: ${james_pay} biweekly | Candace: ${candace_pay} semi-monthly')
print(f'Starting: Checking ${checking}, Savings ${savings}')
print()
print(f"{'Week':<6} {'Monday':<10} {'Income':<30} {'Checking Bills':<35} {'Checking':<12} {'Status':<10} {'Savings':<10}")
print('-' * 100)

# Monthly fixed allocation to weeks
fixed_per_week = sum(fixed_monthly.values()) / 4.3

negative_weeks = []
low_weeks = []

for w in range(26):
    week_start = start + timedelta(days=w*7)
    monday = week_start + timedelta(days=(1 - week_start.weekday()) % 7)
    
    income_events = []
    bill_events = []
    
    # James payday (every 14 days from 7/10)
    days_from_james = (monday - james_date).days
    if days_from_james >= 0 and days_from_james % 14 == 0:
        checking += james_pay - save_james
        savings += save_james
        income_events.append(f'James +${james_pay}')
    
    # Candace payday (15th and last day of month)
    for d in range(7):
        check = monday + timedelta(days=d)
        if check.day == 15:
            checking += candace_pay - save_candace
            savings += save_candace
            income_events.append(f'Candace +${candace_pay}')
        next_day = check + timedelta(days=1)
        if next_day.month != check.month and check.day >= 28:
            checking += candace_pay - save_candace
            savings += save_candace
            income_events.append(f'Candace +${candace_pay}')
    
    # Fixed bills drain from checking
    checking -= fixed_per_week
    bill_events.append(f'Fixed bills ~${fixed_per_week:.0f}')
    
    # CC statement due dates (you pay the full statement balance from checking)
    for d in range(7):
        check = monday + timedelta(days=d)
        if check.day == 10:  # Chase 8580
            # Pay statement balance (approx current balance / cycle)
            payment = sum(cc_balances.values()) / 4  # rough: pay ~1/4 of total monthly
            checking -= payment
            bill_events.append(f'CC Payment ${payment:.0f}')
    
    status = ''
    if checking < 0:
        status = 'NEGATIVE'
        negative_weeks.append(w+1)
    elif checking < 1000:
        status = 'LOW'
        low_weeks.append(w+1)
    
    income_str = ', '.join(income_events) if income_events else '-'
    bill_str = ', '.join(bill_events) if bill_events else '-'
    
    print(f"{w+1:<6} {monday.strftime('%m/%d'):<10} {income_str:<30} {bill_str:<35} ${checking:<11,.0f} {status:<10} ${savings:<10,.0f}")

print()
print(f"End of 6 months: Checking ${checking:,.0f}, Savings ${savings:,.0f}")
print()
if negative_weeks:
    print(f"WARNING: Negative weeks: {negative_weeks}")
if low_weeks:
    print(f"CAUTION: Low weeks: {low_weeks}")
if not negative_weeks and not low_weeks:
    print("GOOD: No negative or low weeks!")
    
print()
print("The key question: Are you paying statement balances IN FULL each month?")
print("If yes, checking needs to cover ~$11,000/month outflow.")
print("If no, you're carrying balances and paying interest.")
