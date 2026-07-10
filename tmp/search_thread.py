import os, imaplib, email, re
from email.header import decode_header
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GMAIL_ADDR = 'jhenderson87@gmail.com'
GMAIL_PASS = 'xyuh xrhn nrpx fdlv'

MAIL = imaplib.IMAP4_SSL('imap.gmail.com', 993)
MAIL.login(GMAIL_ADDR, GMAIL_PASS)

# Try sent folder first
for folder in ['[Gmail]/Sent Mail', 'Sent', 'INBOX.Sent', '[Gmail]/Sent']:
    try:
        status, _ = MAIL.select(folder, readonly=True)
        if status == 'OK':
            print('Opened folder:', folder)
            _, msg_ids = MAIL.search(None, 'ALL')
            sent_ids = msg_ids[0].split()
            print('Sent folder has', len(sent_ids), 'messages')
            # Search last 30 sent for "Grand Highlander"
            recent = sent_ids[-30:] if len(sent_ids) > 30 else sent_ids
            for uid in recent:
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
                if 'highlander' in subject_str.lower():
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
                    print('\n--- SENT EMAIL ---')
                    print('Subject:', subject_str)
                    print('From:', from_str)
                    print('To:', to_str)
                    print('Date:', date_str)
            MAIL.close()
            break
    except Exception as e:
        print('Folder', folder, 'failed:', str(e)[:100])

# Also search INBOX for all Grand Highlander emails
MAIL.select('INBOX', readonly=True)
_, msg_ids = MAIL.search(None, 'SUBJECT', 'Highlander')
print('\nInbox has', len(msg_ids[0].split()), 'Highlander emails')

for uid in msg_ids[0].split():
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
    if 'highlander' in subject_str.lower():
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
        
        body_text = ''
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == 'text/plain':
                    try:
                        body_text = part.get_payload(decode=True).decode('utf-8', errors='replace')
                        break
                    except:
                        pass
        else:
            try:
                body_text = msg.get_payload(decode=True).decode('utf-8', errors='replace')
            except:
                pass
        
        print('\n--- INBOX EMAIL ---')
        print('Subject:', subject_str)
        print('From:', from_str)
        print('To:', to_str)
        print('Date:', date_str)
        print('Body:', body_text[:800])
        print('---')

MAIL.logout()
