import os, imaplib, email, re
from email.header import decode_header
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GMAIL_ADDR = 'jhenderson87@gmail.com'
GMAIL_PASS = 'xyuh xrhn nrpx fdlv'

MAIL = imaplib.IMAP4_SSL('imap.gmail.com', 993)
MAIL.login(GMAIL_ADDR, GMAIL_PASS)
MAIL.select('INBOX', readonly=True)

def safe_decode_header(hdr):
    result = ''
    try:
        parts = decode_header(hdr)
        for part, enc in parts:
            if isinstance(part, bytes):
                try:
                    if enc and enc.lower() == 'unknown-8bit':
                        result += part.decode('utf-8', errors='replace')
                    else:
                        result += part.decode(enc or 'utf-8', errors='replace')
                except:
                    result += part.decode('utf-8', errors='replace')
            else:
                result += str(part)
    except:
        try:
            result = hdr.decode('utf-8', errors='replace')
        except:
            result = str(hdr)
    return result

# Check recent 100 emails for Toyota/Five Star/Highlander
print('=== LAST 100 EMAILS IN INBOX ===')
_, msg_ids = MAIL.search(None, 'ALL')
all_ids = msg_ids[0].split()
recent = all_ids[-100:] if len(all_ids) > 100 else all_ids
recent = list(reversed(recent))
for uid in recent:
    try:
        _, raw = MAIL.fetch(uid, '(RFC822.HEADER)')
        if not raw or not raw[0]:
            continue
        raw_header = raw[0][1]
        msg = email.message_from_bytes(raw_header)
        subject_str = safe_decode_header(msg.get('Subject', ''))
        from_str = safe_decode_header(msg.get('From', ''))
        to_str = safe_decode_header(msg.get('To', ''))
        date_str = msg.get('Date', '')
        
        full = (subject_str + from_str + to_str).lower()
        if 'highlander' in full or 'toyota' in full or 'five star' in full or 'dealerhub' in full or 'crosby' in full:
            print(f'UID {uid.decode()}: [{from_str}] {subject_str} - {date_str}')
    except Exception as e:
        pass

# Now fetch the Highlander-related emails with full bodies
print('\n=== FETCHING HIGHLANDER EMAIL BODIES ===')
toyota_ids = []
for uid in recent:
    try:
        _, raw = MAIL.fetch(uid, '(RFC822.HEADER)')
        if not raw or not raw[0]:
            continue
        raw_header = raw[0][1]
        msg = email.message_from_bytes(raw_header)
        subject_str = safe_decode_header(msg.get('Subject', ''))
        from_str = safe_decode_header(msg.get('From', ''))
        to_str = safe_decode_header(msg.get('To', ''))
        full = (subject_str + from_str + to_str).lower()
        if 'highlander' in full or 'toyota' in full or 'five star' in full or 'dealerhub' in full or 'crosby' in full:
            toyota_ids.append(uid)
    except:
        pass

for uid in toyota_ids:
    try:
        _, raw = MAIL.fetch(uid, '(RFC822)')
        if not raw or not raw[0]:
            continue
        raw_msg = raw[0][1]
        msg = email.message_from_bytes(raw_msg)
        subject_str = safe_decode_header(msg.get('Subject', ''))
        from_str = safe_decode_header(msg.get('From', ''))
        to_str = safe_decode_header(msg.get('To', ''))
        date_str = msg.get('Date', '')
        
        body_text = ''
        body_html = ''
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == 'text/plain' and not body_text:
                    try:
                        body_text = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    except:
                        pass
                if ctype == 'text/html' and not body_html:
                    try:
                        body_html = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    except:
                        pass
        else:
            try:
                body_text = msg.get_payload(decode=True).decode('utf-8', errors='replace')
            except:
                pass
        
        body = body_text if body_text else body_html
        clean = re.sub(r'\s+', ' ', body)
        
        print(f'\n--- UID {uid.decode()} ---')
        print(f'Subject: {subject_str}')
        print(f'From: {from_str}')
        print(f'To: {to_str}')
        print(f'Date: {date_str}')
        print(f'Body: {clean[:3000]}')
        print('---')
    except Exception as e:
        pass

MAIL.logout()
