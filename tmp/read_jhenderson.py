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

# Search for emails from cameron
status, messages = mail.search(None, '(FROM cameron)')
msg_ids = messages[0].split()
print(f'Found {len(msg_ids)} messages from cameron')

for msg_id in msg_ids[-5:]:  # Last 5
    status, msg_data = mail.fetch(msg_id, '(RFC822)')
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    print(f'\n--- ID: {msg_id.decode()} ---')
    print(f'From: {msg.get("From")}')
    print(f'Subject: {msg.get("Subject")}')
    print(f'Date: {msg.get("Date")}')
    
    # Get body
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
    
    print(f'Body preview: {body[:800]}')

mail.logout()
