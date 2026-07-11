import imaplib
import email
import json

with open('scripts/.gmail_accounts.json') as f:
    creds = json.load(f)

email_addr = 'jhenderson87@gmail.com'
password = creds[email_addr]

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(email_addr, password)

# Check Work folder
for folder_name in ['Work', 'Personal', 'Sent', 'nova trade', 'Receipts']:
    try:
        status = mail.select(folder_name, readonly=True)
        if status[0] != 'OK':
            print(f'{folder_name}: not accessible')
            continue
        
        status, messages = mail.search(None, 'ALL')
        msg_ids = messages[0].split()
        print(f'{folder_name}: {len(msg_ids)} messages')
        
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
            
            # Look for cameron in work emails
            if 'cameron' in from_line.lower():
                print(f'  FOUND: ID {msg_id.decode()} | {from_line} | {subject_line}')
                
    except Exception as e:
        print(f'{folder_name}: error - {e}')

mail.logout()
