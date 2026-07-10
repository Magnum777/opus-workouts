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

_, msg_ids = MAIL.search(None, 'ALL')
all_ids = msg_ids[0].split()
recent = all_ids[-100:] if len(all_ids) > 100 else all_ids
recent = list(reversed(recent))

print(f'Last 100 emails (newest first):\n')
for uid in recent:
    _, raw = MAIL.fetch(uid, '(RFC822.HEADER)')
    if raw and raw[0]:
        msg = email.message_from_bytes(raw[0][1])
        subj = safe_decode(msg.get('Subject', ''))
        frm = safe_decode(msg.get('From', ''))
        to = safe_decode(msg.get('To', ''))
        date = msg.get('Date', '')
        print(f'{uid.decode()}: [{frm}] -> [{to}] | {subj} | {date}')

MAIL.logout()
