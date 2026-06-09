import os, imaplib, email, re, json, sys
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

GMAIL_ADDR = os.environ.get('GMAIL_ADDRESS', '')
GMAIL_PASS = os.environ.get('GMAIL_APP_PASSWORD', '')

NOISE_PATTERNS = [
    r'unsubscribe', r'newsletter', r'no-reply@', r'noreply@',
    r'marketing@', r'notifications?@', r'donotreply@',
    r'@.*\.(mailchim|sendgrid|constantcontact|klaviyo)',
]
NOISE_SUBJECTS = ['sale', '% off', 'deal', 'offer', 'promo', 'subscribe', 'newsletter',
    'weekly digest', 'monthly update', 'announcement']
URGENT_KW = ['urgent', 'asap', 'deadline', 'immediately', 'action required', 'time sensitive',
    'overdue', 'past due', 'invoice', 'payment due', 'legal', 'lawsuit', 'critical',
    'emergency', 'final notice', 'expires', 'expiring', 'last chance']
REPLY_KW = ['?', 'question', 'can you', 'could you', 'please', 'request',
    'following up', 'follow-up', 'reminder', 'let me know', 'thoughts']

def decode_str(s):
    if not s: return ''
    r = []
    for part, enc in decode_header(s):
        if isinstance(part, bytes):
            try: r.append(part.decode(enc or 'utf-8', errors='replace'))
            except: r.append(part.decode('utf-8', errors='replace'))
        else: r.append(str(part))
    return ' '.join(r)

def is_noise(sender, subject):
    text = (sender + ' ' + subject).lower()
    for pat in NOISE_PATTERNS:
        if re.search(pat, text): return True
    for kw in NOISE_SUBJECTS:
        if kw in subject.lower(): return True
    return False

def score_email(subject, snippet, sender, age_hours, has_replied):
    score = 50
    s_low = subject.lower(); sn_low = snippet.lower()
    for kw in URGENT_KW:
        if kw in s_low or kw in sn_low: score += 20; break
    for kw in REPLY_KW:
        if kw in s_low or kw in sn_low: score += 10; break
    if age_hours < 2: score += 5
    elif age_hours > 48: score -= 10
    elif age_hours > 120: score -= 20
    if has_replied: score -= 15
    return max(0, min(score, 100))

mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
mail.login(GMAIL_ADDR, GMAIL_PASS)
mail.select('INBOX', readonly=True)

since_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%d-%b-%Y')
_, msg_ids = mail.search(None, f'SINCE {since_date}')
all_ids = msg_ids[0].split() if msg_ids and msg_ids[0] else []

if len(all_ids) < 5:
    _, all_msg_ids = mail.search(None, 'ALL')
    all_id_list = all_msg_ids[0].split() if all_msg_ids and all_msg_ids[0] else []
    all_ids = all_id_list[-50:] if len(all_id_list) > 50 else all_id_list

recent_ids = list(reversed(all_ids[-50:] if len(all_ids) > 50 else all_ids))
emails_data = []
now = datetime.now(timezone.utc)

for uid in recent_ids:
    try:
        _, raw = mail.fetch(uid, '(RFC822.HEADER FLAGS)')
        if not raw or not raw[0]: continue
        rh = raw[0][1] if isinstance(raw[0], tuple) else raw[0]
        msg = email.message_from_bytes(rh)
        subject = decode_str(msg.get('Subject', '(no subject)'))
        sender = decode_str(msg.get('From', ''))
        date_str = msg.get('Date', '')
        flags_raw = raw[0][0] if isinstance(raw[0], tuple) else b''
        has_replied = b'\\Answered' in flags_raw
        try:
            sent_dt = parsedate_to_datetime(date_str)
            if sent_dt:
                if sent_dt.tzinfo is None: sent_dt = sent_dt.replace(tzinfo=timezone.utc)
                age_hours = (now - sent_dt).total_seconds() / 3600
            else: age_hours = 0
        except: age_hours = 0
        body_snippet = ''
        try:
            _, rb = mail.fetch(uid, '(BODY[TEXT]<0.300>)')
            if rb and rb[0] and isinstance(rb[0], tuple) and rb[0][1]:
                body_snippet = rb[0][1].decode('utf-8', errors='replace').strip()[:200]
        except: pass
        noise = is_noise(sender, subject)
        urgency = score_email(subject, body_snippet, sender, age_hours, has_replied)
        sm = re.search(r'"?([^"<]+)"?\s*<([^>]+)>', sender)
        sender_name = sm.group(1).strip() if sm else sender
        sender_email = sm.group(2).strip() if sm else sender
        emails_data.append({
            'subject': subject, 'sender': sender_name, 'sender_email': sender_email,
            'age_hours': round(age_hours, 1), 'urgency': urgency,
            'is_noise': noise, 'replied': has_replied
        })
    except: continue

mail.logout()
actionable = [e for e in emails_data if not e['is_noise']]
noise_items = [e for e in emails_data if e['is_noise']]
actionable.sort(key=lambda e: -e['urgency'])
high_prio = [e for e in actionable if e['urgency'] >= 70]
spam_leaked = [e for e in noise_items if e['urgency'] >= 50]

result = {
    'total': len(emails_data),
    'actionable': len(actionable),
    'noise': len(noise_items),
    'replied': sum(1 for e in actionable if e['replied']),
    'high_priority': len(high_prio),
    'spam_leaked_count': len(spam_leaked),
    'items': [{
        'subject': e['subject'][:80], 'from': e['sender'][:40],
        'age_h': e['age_hours'], 'urgency': e['urgency'], 'replied': e['replied']
    } for e in actionable[:15]]
}
print(json.dumps(result))
