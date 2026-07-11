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

# Get all emails from July 9-10
status, messages = mail.search(None, 'SINCE 09-Jul-2026')
msg_ids = messages[0].split()
print(f'INBOX since July 9: {len(msg_ids)} messages')

for msg_id in msg_ids:
    status, msg_data = mail.fetch(msg_id, '(RFC822)')
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    
    from_addr = msg.get('From', '')
    subject = msg.get('Subject', '')
    
    # Search for "cameron" anywhere in the email
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
    
    full_text = (from_addr + subject + body).lower()
    if 'cameron' in full_text and 'blisshookup' not in full_text and 'riskyheatfire' not in full_text:
        print(f'\n=== FOUND ===')
        print(f'ID: {msg_id.decode()}')
        print(f'From: {from_addr}')
        print(f'Subject: {subject}')
        print(f'Date: {msg.get("Date")}')
        print(f'Body:\n{body[:1000]}')

mail.logout()
