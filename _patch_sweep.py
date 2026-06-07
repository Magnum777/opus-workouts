import sys

with open('scripts/gmail_spam_sweep_v2.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Widen date window and message limits
text = text.replace('timedelta(days=14)', 'timedelta(days=30)')
text = text.replace('max_msgs = 100 if "compjunkie" in email_addr else 50', 'max_msgs = 500 if "compjunkie" in email_addr else 300')
text = text.replace('(last 7 days)', '(last 30 days)')

with open('scripts/gmail_spam_sweep_v2.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Patched v2: 30 days, 500/300 msgs')
