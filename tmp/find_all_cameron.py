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

# Search for ALL emails from someone with "cameron" in the from field
# Using IMAP SEARCH syntax
status, messages = mail.search(None, 'FROM cameron')
msg_ids = messages[0].split()
print(f'Total emails from "cameron": {len(msg_ids)}')

# Check all of them
for msg_id in msg_ids:
    status, msg_data = mail.fetch(msg_id, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
    raw_headers = msg_data[0][1]
    
    # Parse headers
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
    
    # Skip spam
    if 'blisshookup' in from_line.lower() or 'riskyheatfire' in from_line.lower():
        continue
    
    print(f'\n=== REAL CAMERON EMAIL ===')
    print(f'ID: {msg_id.decode()}')
    print(f'From: {from_line}')
    print(f'Subject: {subject_line}')
    print(f'Date: {date_line}')
    
    # Get full body
    status, msg_data = mail.fetch(msg_id, '(RFC822)')
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    body = str(part.get_payload())
                break
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except:
            body = str(msg.get_payload())
    
    print(f'Body:\n{body}')
    print("="*60)

mail.logout()
