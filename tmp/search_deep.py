import imaplib, email, re
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

# Search for "car repairs" in body
print('=== BODY SEARCH: "repairs" ===')
_, msg_ids = MAIL.search(None, 'BODY', 'repairs')
ids = msg_ids[0].split()
print(f'Found {len(ids)}\n')
for uid in ids:
    _, raw = MAIL.fetch(uid, '(RFC822.HEADER)')
    if raw and raw[0]:
        msg = email.message_from_bytes(raw[0][1])
        subj = safe_decode(msg.get('Subject', ''))
        frm = safe_decode(msg.get('From', ''))
        to = safe_decode(msg.get('To', ''))
        date = msg.get('Date', '')
        print(f'UID {uid.decode()}: [{frm}] -> [{to}] Subj: {subj} | {date}')

# Search for "repairs" in body
print('\n=== BODY SEARCH: "repairs" ===')
_, msg_ids = MAIL.search(None, 'BODY', 'repairs')
ids = msg_ids[0].split()
print(f'Found {len(ids)} total with "repairs"\n')
# Show last 20 that are Toyota/Five Star related
for uid in ids[-20:]:
    _, raw = MAIL.fetch(uid, '(RFC822)')
    if raw and raw[0]:
        msg = email.message_from_bytes(raw[0][1])
        subj = safe_decode(msg.get('Subject', ''))
        frm = safe_decode(msg.get('From', ''))
        to = safe_decode(msg.get('To', ''))
        date = msg.get('Date', '')
        full = (subj + frm + to).lower()
        if 'toyota' in full or 'highlander' in full or 'five star' in full or 'dealerhub' in full or 'crosby' in full or 'milledgeville' in full:
            print(f'UID {uid.decode()}: [{frm}] Subj: {subj} | {date}')

# Search for Candace as sender in all emails
print('\n=== FROM "Candace" ===')
_, msg_ids = MAIL.search(None, 'FROM', 'Candace')
ids = msg_ids[0].split()
print(f'Found {len(ids)}\n')
for uid in ids:
    _, raw = MAIL.fetch(uid, '(RFC822.HEADER)')
    if raw and raw[0]:
        msg = email.message_from_bytes(raw[0][1])
        subj = safe_decode(msg.get('Subject', ''))
        frm = safe_decode(msg.get('From', ''))
        to = safe_decode(msg.get('To', ''))
        date = msg.get('Date', '')
        print(f'UID {uid.decode()}: [{frm}] -> [{to}] Subj: {subj} | {date}')

# Also search for "Candace" anywhere in recent 200
print('\n=== RECENT 200 EMAILS WITH "Candace" ===')
_, msg_ids = MAIL.search(None, 'ALL')
all_ids = msg_ids[0].split()
recent = all_ids[-200:] if len(all_ids) > 200 else all_ids
recent = list(reversed(recent))
for uid in recent:
    _, raw = MAIL.fetch(uid, '(RFC822)')
    if raw and raw[0]:
        msg = email.message_from_bytes(raw[0][1])
        subj = safe_decode(msg.get('Subject', ''))
        frm = safe_decode(msg.get('From', ''))
        to = safe_decode(msg.get('To', ''))
        date = msg.get('Date', '')
        
        body_text = ''
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
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
        
        full = (subj + frm + to + body_text).lower()
        if 'candace' in full and ('toyota' in full or 'highlander' in full or 'dealerhub' in full or 'five star' in full or 'milledgeville' in full):
            print(f'\nUID {uid.decode()}: [{frm}] -> [{to}]')
            print(f'Subj: {subj} | Date: {date}')
            clean = re.sub(r'\s+', ' ', body_text)
            print(f'Body: {clean[:800]}')

MAIL.logout()
