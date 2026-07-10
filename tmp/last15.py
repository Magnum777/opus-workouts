import imaplib, email
from email.header import decode_header
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GMAIL_ADDR = 'jhenderson87@gmail.com'
GMAIL_PASS = 'xyuh xrhn nrpx fdlv'

MAIL = imaplib.IMAP4_SSL('imap.gmail.com', 993)
MAIL.login(GMAIL_ADDR, GMAIL_PASS)
MAIL.select('INBOX', readonly=True)

def safe_decode(hdr):
    result = ''
    try:
        for part, enc in decode_header(hdr):
            if isinstance(part, bytes):
                result += part.decode(enc or 'utf-8', errors='replace')
            else:
                result += str(part)
    except:
        result = str(hdr)
    return result

# Get last 15 email IDs
_, msg_ids = MAIL.search(None, 'ALL')
all_ids = msg_ids[0].split()
recent = all_ids[-15:]
recent = list(reversed(recent))

print(f'Last 15 emails:\n')
for uid in recent:
    try:
        _, raw = MAIL.fetch(uid, '(RFC822)')
        if not raw or not raw[0]:
            continue
        raw_msg = raw[0][1]
        msg = email.message_from_bytes(raw_msg)
        
        subj = safe_decode(msg.get('Subject', ''))
        frm = safe_decode(msg.get('From', ''))
        to = safe_decode(msg.get('To', ''))
        date = msg.get('Date', '')
        
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                        break
                    except:
                        pass
            if not body:
                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
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
        
        import re
        clean = re.sub(r'\s+', ' ', body[:4000])
        
        print(f'UID: {uid.decode()}')
        print(f'From: {frm}')
        print(f'To: {to}')
        print(f'Subject: {subj}')
        print(f'Date: {date}')
        print(f'Body: {clean}')
        print('---\n')
    except Exception as e:
        print(f'Error uid {uid}: {e}')

MAIL.logout()
