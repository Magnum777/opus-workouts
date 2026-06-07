with open('scripts/gmail_spam_sweep_v2.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Throttle back to 200/100 but keep 30 days
text = text.replace('max_msgs = 500 if "compjunkie" in email_addr else 300', 'max_msgs = 200 if "compjunkie" in email_addr else 100')

with open('scripts/gmail_spam_sweep_v2.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Throttled to 200/100')
