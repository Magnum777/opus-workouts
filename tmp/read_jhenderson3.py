import imaplib
import email
import json

with open('scripts/.gmail_accounts.json') as f:
    creds = json.load(f)

email_addr = 'jhenderson87@gmail.com'
password = creds[email_addr]

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(email_addr, password)
mail.select('INBOX')

# Get last 50 emails
status, messages = mail.search(None, 'ALL')
msg_ids = messages[0].split()
print(f'Total messages: {len(msg_ids)}')

# Look for recent emails from cameron that aren't spam
for msg_id in msg_ids[-50:]:
    status, msg_data = mail.fetch(msg_id, '(RFC822)')
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    
    from_addr = msg.get('From', '')
    subject = msg.get('Subject', '')
    
    # Filter spam
    if 'blisshookup.com' in from_addr or 'riskyheatfire.com' in from_addr:
        continue
        
    if 'cameron' in from_addr.lower():
        print(f'\n=== ID: {msg_id.decode()} ===')
        print(f'From: {from_addr}')
        print(f'Subject: {subject}')
        print(f'Date: {msg.get("Date")}')
        
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
