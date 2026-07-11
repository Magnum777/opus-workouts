import imaplib
import email
import json

with open('scripts/.gmail_accounts.json') as f:
    creds = json.load(f)

email_addr = 'jhenderson87@gmail.com'
password = creds[email_addr]

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(email_addr, password)

# Check Spam folder
mail.select('[Gmail]/Spam', readonly=True)
status, messages = mail.search(None, 'SINCE 01-Jul-2026')
msg_ids = messages[0].split()
print(f'SPAM since July 1: {len(msg_ids)} messages')

# Search for non-spam-looking emails that might be from cameron
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
    
    # Skip obvious spam but check if from cameron
    if 'cameron' in from_line.lower():
        print(f'  FOUND: ID {msg_id.decode()} | {from_line} | {subject_line}')
        
        # Get body
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
        
        print(f'Body: {body[:500]}')

mail.logout()
