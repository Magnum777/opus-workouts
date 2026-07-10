import os, imaplib, email, re, sys
from email.header import decode_header

# Set stdout to utf-8
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

GMAIL_ADDR = 'jhenderson87@gmail.com'
GMAIL_PASS = 'xyuh xrhn nrpx fdlv'

MAIL = imaplib.IMAP4_SSL('imap.gmail.com', 993)
MAIL.login(GMAIL_ADDR, GMAIL_PASS)
MAIL.select('INBOX', readonly=True)

results = []

_, msg_ids = MAIL.search(None, 'FROM', 'FiveStarToyotaMilledgeville.eDealerhub.com')
ids = msg_ids[0].split()
results.extend(ids)

for field in ['FROM', 'TO', 'CC', 'SUBJECT']:
    _, msg_ids = MAIL.search(None, field, 'Alyssa')
    ids = msg_ids[0].split()
    results.extend(ids)

for field in ['FROM', 'TO', 'CC', 'SUBJECT']:
    _, msg_ids = MAIL.search(None, field, 'Crosby')
    ids = msg_ids[0].split()
    results.extend(ids)

_, msg_ids = MAIL.search(None, 'BODY', 'Alyssa')
results.extend(msg_ids[0].split())

_, msg_ids = MAIL.search(None, 'BODY', 'Crosby')
results.extend(msg_ids[0].split())

unique_ids = list(set(results))
unique_ids = sorted(unique_ids, key=lambda x: int(x.decode()))
unique_ids = list(reversed(unique_ids))

found = []
for uid in unique_ids:
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
                try:
                    subject_str += part.decode(enc or 'utf-8', errors='replace')
                except:
                    subject_str += part.decode('utf-8', errors='replace')
            else:
                subject_str += str(part)

        from_field = decode_header(msg.get('From', ''))
        from_str = ''
        for part, enc in from_field:
            if isinstance(part, bytes):
                try:
                    from_str += part.decode(enc or 'utf-8', errors='replace')
                except:
                    from_str += part.decode('utf-8', errors='replace')
            else:
                from_str += str(part)

        to_field = decode_header(msg.get('To', ''))
        to_str = ''
        for part, enc in to_field:
            if isinstance(part, bytes):
                try:
                    to_str += part.decode(enc or 'utf-8', errors='replace')
                except:
                    to_str += part.decode('utf-8', errors='replace')
            else:
                to_str += str(part)

        date_str = msg.get('Date', '')
        msg_id = msg.get('Message-ID', '')
        in_reply_to = msg.get('In-Reply-To', '')

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

        full_text = (subject_str + ' ' + from_str + ' ' + to_str + ' ' + body).lower()

        if 'crosby' in full_text or 'alyssa' in full_text or 'five star toyota' in full_text or 'dealerhub' in full_text:
            clean = re.sub(r'\s+', ' ', body)
            found.append({
                'uid': uid.decode(),
                'subject': subject_str,
                'from': from_str,
                'to': to_str,
                'date': date_str,
                'msg_id': msg_id,
                'in_reply_to': in_reply_to,
                'body': clean.strip(),
                'is_html': bool(body_html)
            })
    except Exception as e:
        pass

MAIL.logout()

found.sort(key=lambda x: x['date'])

print('Found', len(found), 'messages\n')
for f in found:
    print('========================================')
    print('UID:', f['uid'])
    print('From:', f['from'])
    print('To:', f['to'])
    print('Subject:', f['subject'])
    print('Date:', f['date'])
    print('In-Reply-To:', f['in_reply_to'])
    print('--- BODY ---')
    # Safe print for unicode
    try:
        print(f['body'][:3000])
    except:
        print(f['body'].encode('ascii', 'replace').decode('ascii')[:3000])
    print('========================================\n')
