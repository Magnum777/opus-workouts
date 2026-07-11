import imaplib
import email
import json

with open('scripts/.gmail_accounts.json') as f:
    creds = json.load(f)

email_addr = 'jhenderson87@gmail.com'
password = creds[email_addr]

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(email_addr, password)

# Search all folders
for folder in ['INBOX', '[Gmail]/Important', '[Gmail]/Starred', '[Gmail]/All Mail']:
    try:
        status = mail.select(folder, readonly=True)
        if status[0] != 'OK':
            print(f'Could not select {folder}')
            continue
        
        # Search for emails from last 14 days with "cameron"
        status, messages = mail.search(None, 'SINCE 26-Jun-2026')
        msg_ids = messages[0].split()
        
        if not msg_ids:
            continue
            
        found = []
        for msg_id in msg_ids:
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            from_addr = msg.get('From', '')
            subject = msg.get('Subject', '')
            
            # Look for cameron but not spam domains
            if 'cameron' in from_addr.lower() and 'blisshookup' not in from_addr.lower() and 'riskyheatfire' not in from_addr.lower():
                found.append((msg_id, from_addr, subject, msg.get('Date')))
        
        if found:
            print(f'\n=== {folder}: {len(found)} matches ===')
            for msg_id, from_addr, subject, date in found:
                print(f'ID {msg_id.decode()} | From: {from_addr}')
                print(f'Subject: {subject}')
                print(f'Date: {date}')
                
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
                
    except Exception as e:
        print(f'Error with {folder}: {e}')

mail.logout()
