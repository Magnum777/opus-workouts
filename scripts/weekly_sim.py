from datetime import datetime, timedelta

james_pay = 4879
candace_pay = 2375
checking = 4070
savings = 4179
spend_target = 7500
save_james = 250
save_candace = 250

james_date = datetime(2026, 7, 10)
candace_date = datetime(2026, 7, 15)

cards = [
    {'name': 'Chase ****8580', 'due': 10, 'bal': 8837},
    {'name': 'Chase ****7628', 'due': 24, 'bal': 7030},
    {'name': 'Chase ****9993', 'due': 22, 'bal': 0},
    {'name': 'AMEX Gold', 'due': 12, 'bal': 815},
    {'name': 'AMEX Delta', 'due': 15, 'bal': 118},
    {'name': 'Regions ****0121', 'due': 18, 'bal': 0},
]

start = datetime(2026, 7, 9)

print('=' * 100)
print('6-MONTH WEEKLY CASH FLOW SIMULATION')
print(f'James: ${james_pay} biweekly starting {james_date.strftime("%m/%d")}')
print(f'Candace: ${candace_pay} semi-monthly (15th + EOM)')
print(f'Starting: Checking ${checking}, Savings ${savings}')
print(f'Weekly spend: ${spend_target/4.3:.0f}')
print('=' * 100)
print()
print(f"{'Week':<6} {'Monday':<10} {'Income':<35} {'Bills Due':<30} {'Checking':<12} {'Status':<10} {'Savings':<10}")
print('-' * 100)

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
        # End of month
        next_day = check + timedelta(days=1)
        if next_day.month != check.month and check.day >= 28:
            checking += candace_pay - save_candace
            savings += save_candace
            income_events.append(f'Candace +${candace_pay}')
    
    # Weekly spending
    weekly_spend = spend_target / 4.3
    checking -= weekly_spend
    
    # Bills due
    for card in cards:
        if card['bal'] <= 0:
            continue
        for d in range(7):
            check = monday + timedelta(days=d)
            if check.day == card['due']:
                min_pay = max(25, card['bal'] * 0.01)
                bill_events.append(f"{card['name']} ${min_pay:.0f}")
    
    status = ''
    if checking < 0:
        status = 'NEGATIVE'
        negative_weeks.append(w+1)
    elif checking < 500:
        status = 'LOW'
        low_weeks.append(w+1)
    
    income_str = ', '.join(income_events) if income_events else '-'
    bill_str = ', '.join(bill_events) if bill_events else '-'
    
    print(f"{w+1:<6} {monday.strftime('%m/%d'):<10} {income_str:<35} {bill_str:<30} ${checking:<11,.0f} {status:<10} ${savings:<10,.0f}")

print()
print(f"End of 6 months: Checking ${checking:,.0f}, Savings ${savings:,.0f}")
print()
if negative_weeks:
    print(f"WARNING: Checking went NEGATIVE in weeks: {negative_weeks}")
    print("This means the plan needs adjustment - either:")
    print("  - Reduce initial paydown (keep more cash)")
    print("  - Lower weekly spending target")
    print("  - Add starting buffer from Regions savings")
if low_weeks:
    print(f"CAUTION: Checking went below $500 in weeks: {low_weeks}")
    print("These are tight weeks - watch spending carefully.")
if not negative_weeks and not low_weeks:
    print("GOOD: Checking never went negative or low. Plan is viable.")
