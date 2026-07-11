import imaplib
import email
import json

with open('scripts/.gmail_accounts.json') as f:
    creds = json.load(f)

# Check ALL accounts for emails from cameron
for email_addr, password in creds.items():
    print(f'\n=== Checking {email_addr} ===')
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(email_addr, password)
        mail.select('INBOX', readonly=True)
        
        # Search for emails from last 30 days
        status, messages = mail.search(None, 'SINCE 10-Jun-2026')
        msg_ids = messages[0].split()
        
        found = []
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
            
            # Look for cameron but not spam
            if 'cameron' in from_line.lower():
                if 'blisshookup' not in from_line.lower() and 'riskyheatfire' not in from_line.lower():
                    found.append((msg_id, from_line, subject_line, date_line))
        
        if found:
            for msg_id, from_line, subject_line, date_line in found:
                print(f'  FOUND: ID {msg_id.decode()} | {from_line} | {subject_line} | {date_line}')
        else:
            print(f'  No non-spam cameron emails found')
        
        mail.logout()
        
    except Exception as e:
        print(f'  Error: {e}')
