import imaplib
import email
import json

with open('scripts/.gmail_accounts.json') as f:
    creds = json.load(f)

email_addr = 'jhenderson87@gmail.com'
password = creds[email_addr]

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(email_addr, password)
mail.select('INBOX', readonly=True)

# Search for emails from today
status, messages = mail.search(None, 'SINCE 10-Jul-2026')
msg_ids = messages[0].split()
print(f'INBOX today (Jul 10): {len(msg_ids)} messages')

for msg_id in msg_ids:
    status, msg_data = mail.fetch(msg_id, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
    raw_headers = msg_data[0][1]
    
    from_line = ''
    subject_line = ''
    date_line = ''
    for line in raw_headers.decode('utf-8', errors='ignore').split('\r\n'):
        if line.lower().startswith('from:'):
            from_line = line[5:].strip()
        elif line.lower().startswith('subject:'):
            subject_line = line[8:].strip()
        elif line.lower().startswith('date:'):
            date_line = line[5:].strip()
    
    # Show all emails from today
    print(f'{msg_id.decode()} | {from_line} | {subject_line}')

mail.logout()
