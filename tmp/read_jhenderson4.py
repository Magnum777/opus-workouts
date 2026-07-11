import imaplib
import email
import json
from datetime import datetime, timedelta

with open('scripts/.gmail_accounts.json') as f:
    creds = json.load(f)

email_addr = 'jhenderson87@gmail.com'
password = creds[email_addr]

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(email_addr, password)

# Check all folders for recent emails
for folder in ['INBOX', '[Gmail]/Important', '[Gmail]/Starred']:
    try:
        status = mail.select(folder)
        if status[0] != 'OK':
            continue
        
        # Search for emails from last 7 days
        status, messages = mail.search(None, 'SINCE 05-Jul-2026')
        msg_ids = messages[0].split()
        
        if not msg_ids:
            continue
            
        print(f'\n=== {folder}: {len(msg_ids)} messages since Jul 5 ===')
        
        for msg_id in msg_ids:
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            from_addr = msg.get('From', '')
            subject = msg.get('Subject', '')
            
            # Skip spam
            spam_domains = ['blisshookup.com', 'riskyheatfire.com', 'verify', 'noreply', 'no-reply']
            if any(d in from_addr.lower() for d in spam_domains):
                continue
            
            print(f'\nID {msg_id.decode()} | From: {from_addr[:60]}')
            print(f'Subject: {subject[:80]}')
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
            
            if body.strip():
                print(f'Body: {body[:500].strip()}')
                
    except Exception as e:
        print(f'Error with {folder}: {e}')

mail.logout()
