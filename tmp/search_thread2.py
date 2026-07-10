import os, imaplib, email, re
from email.header import decode_header
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GMAIL_ADDR = 'jhenderson87@gmail.com'
GMAIL_PASS = 'xyuh xrhn nrpx fdlv'

MAIL = imaplib.IMAP4_SSL('imap.gmail.com', 993)
MAIL.login(GMAIL_ADDR, GMAIL_PASS)

# List all folders
print('=== FOLDERS ===')
status, folders = MAIL.list()
for f in folders:
    print(f.decode('utf-8', errors='replace'))
print('=== END FOLDERS ===')

# Try each folder
for folder_name in ['"[Gmail]/Sent Mail"', '"Sent"', '"Sent Items"']:
    try:
        status, _ = MAIL.select(folder_name, readonly=True)
        if status == 'OK':
            print('\nOpened:', folder_name)
            _, msg_ids = MAIL.search(None, 'ALL')
            all_ids = msg_ids[0].split()
            print('Total:', len(all_ids))
            # Search last 20 sent
            recent = all_ids[-20:] if len(all_ids) > 20 else all_ids
            recent = list(reversed(recent))
            for uid in recent:
                _, raw = MAIL.fetch(uid, '(RFC822.HEADER)')
                if not raw or not raw[0]:
                    continue
                raw_header = raw[0][1]
                msg = email.message_from_bytes(raw_header)
                subject = decode_header(msg.get('Subject', ''))
                subject_str = ''
                for part, enc in subject:
                    if isinstance(part, bytes):
                        subject_str += part.decode(enc or 'utf-8', errors='replace')
                    else:
                        subject_str += str(part)
                from_field = decode_header(msg.get('From', ''))
                from_str = ''
                for part, enc in from_field:
                    if isinstance(part, bytes):
                        from_str += part.decode(enc or 'utf-8', errors='replace')
                    else:
                        from_str += str(part)
                to_field = decode_header(msg.get('To', ''))
                to_str = ''
                for part, enc in to_field:
                    if isinstance(part, bytes):
                        to_str += part.decode(enc or 'utf-8', errors='replace')
                    else:
                        to_str += str(part)
                if 'highlander' in subject_str.lower() or 'five star' in to_str.lower() or 'dealerhub' in to_str.lower() or 'toyota' in to_str.lower():
                    print(f'\n--- UID {uid.decode()} ---')
                    print(f'Subject: {subject_str}')
                    print(f'From: {from_str}')
                    print(f'To: {to_str}')
            MAIL.close()
            break
    except Exception as e:
        print('Folder failed:', folder_name, str(e)[:150])

# Also search INBOX for Highlander-related recent emails
print('\n=== INBOX HIGHLANDER THREAD ===')
MAIL.select('INBOX', readonly=True)
_, msg_ids = MAIL.search(None, 'SUBJECT', 'Highlander')
ids = msg_ids[0].split()
print('Highlander subjects in inbox:', len(ids))
for uid in ids:
    _, raw = MAIL.fetch(uid, '(RFC822)')
    if not raw or not raw[0]:
        continue
    raw_msg = raw[0][1]
    msg = email.message_from_bytes(raw_msg)
    subject = decode_header(msg.get('Subject', ''))
    subject_str = ''
    for part, enc in subject:
        if isinstance(part, bytes):
            subject_str += part.decode(enc or 'utf-8', errors='replace')
        else:
            subject_str += str(part)
    from_field = decode_header(msg.get('From', ''))
    from_str = ''
    for part, enc in from_field:
        if isinstance(part, bytes):
            from_str += part.decode(enc or 'utf-8', errors='replace')
        else:
            from_str += str(part)
    to_field = decode_header(msg.get('To', ''))
    to_str = ''
    for part, enc in to_field:
        if isinstance(part, bytes):
            to_str += part.decode(enc or 'utf-8', errors='replace')
        else:
            to_str += str(part)
    date_str = msg.get('Date', '')
    
    body = ''
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == 'text/plain':
                try:
                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    break
                except:
                    pass
        if not body:
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == 'text/html':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                        break
                    except:
                        pass
    else:
        try:
            body = msg.get_payload(decode=True).decode('utf-8', errors='replace')
        except:
            pass
    
    clean = re.sub(r'<[^>]+>', ' ', body)
    clean = re.sub(r'\s+', ' ', clean)
    
    print(f'\n--- UID {uid.decode()} ---')
    print(f'Subject: {subject_str}')
    print(f'From: {from_str}')
    print(f'To: {to_str}')
    print(f'Date: {date_str}')
    print(f'Body: {clean[:800]}')

MAIL.logout()
