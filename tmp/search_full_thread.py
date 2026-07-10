import os, imaplib, email, re
from email.header import decode_header
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GMAIL_ADDR = 'jhenderson87@gmail.com'
GMAIL_PASS = 'xyuh xrhn nrpx fdlv'

MAIL = imaplib.IMAP4_SSL('imap.gmail.com', 993)
MAIL.login(GMAIL_ADDR, GMAIL_PASS)

# Search "Sent" for emails to Toyota/Five Star
def get_headers(folder):
    results = []
    try:
        status, _ = MAIL.select(f'"{folder}"', readonly=True)
        if status != 'OK':
            return results
        _, msg_ids = MAIL.search(None, 'ALL')
        all_ids = msg_ids[0].split()
        recent = all_ids[-50:] if len(all_ids) > 50 else all_ids
        recent = list(reversed(recent))
        for uid in recent:
            try:
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
                clean = re.sub(r'\s+', ' ', body)[:500]
                full = (subject_str + from_str + to_str + body).lower()
                results.append({
                    'uid': uid.decode(),
                    'folder': folder,
                    'subject': subject_str,
                    'from': from_str,
                    'to': to_str,
                    'date': date_str,
                    'body_preview': clean,
                    'full': full
                })
            except Exception as e:
                pass
        MAIL.close()
    except Exception as e:
        print(f'Error with folder {folder}: {e}')
    return results

all_sent = []
for folder in ['[Gmail]/Sent Mail', 'Sent', 'Sent Messages']:
    all_sent.extend(get_headers(folder))

print('=== SEARCHING FOR TOYOTA/FIVE STAR EMAILS IN SENT ===')
for r in all_sent:
    if 'toyota' in r['full'] or 'five star' in r['full'] or 'highlander' in r['full'] or 'dealerhub' in r['full'] or 'milledgeville' in r['full']:
        print(f"\n--- {r['folder']} UID {r['uid']} ---")
        print(f"Subject: {r['subject']}")
        print(f"To: {r['to']}")
        print(f"Date: {r['date']}")
        print(f"Body preview: {r['body_preview']}")

# Also check INBOX for emails about issues/service/wheel/paint from Toyota
print('\n=== INBOX: SEARCH FOR TOYOTA/ISSUES THREADS ===')
MAIL.select('INBOX', readonly=True)

for term in ['wheel', 'paint', 'service', 'issue', 'fix']:
    _, msg_ids = MAIL.search(None, 'FROM', 'FiveStarToyotaMilledgeville.eDealerhub.com')
    ids = msg_ids[0].split()
    print(f'From FiveStarToyota: {len(ids)} emails')
    # Get last 10
    for uid in ids[-10:]:
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
        date_str = msg.get('Date', '')
        print(f"\n--- UID {uid.decode()} ---")
        print(f"Subject: {subject_str}")
        print(f"From: {from_str}")
        print(f"Date: {date_str}")
        break  # just print count
    break

# Let's get ALL emails from FiveStarToyota in inbox (last 20)
print('\n=== ALL RECENT FIVE STAR TOYOTA EMAILS ===')
_, msg_ids = MAIL.search(None, 'FROM', 'FiveStarToyotaMilledgeville.eDealerhub.com')
ids = msg_ids[0].split()
ids = ids[-20:] if len(ids) > 20 else ids
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
    date_str = msg.get('Date', '')
    print(f"UID {uid.decode()}: [{from_str}] {subject_str} - {date_str}")

MAIL.logout()
