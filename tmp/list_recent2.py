import imaplib
import email
import json

with open('scripts/.gmail_accounts.json') as f:
    creds = json.load(f)

email_addr = 'jhenderson87@gmail.com'
password = creds[email_addr]

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(email_addr, password)

# Check recent emails in INBOX
mail.select('INBOX', readonly=True)
status, messages = mail.search(None, 'SINCE 01-Jul-2026')
msg_ids = messages[0].split()
print(f'INBOX since July 1: {len(msg_ids)} messages')

for msg_id in msg_ids[-30:]:
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
    
    # Show all recent emails
    print(f'{msg_id.decode()} | {from_line[:50]:<50} | {subject_line[:60]}')

mail.logout()
