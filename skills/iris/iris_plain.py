import os, imaplib, email, re, sys
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

GMAIL_ADDR = os.environ.get("GMAIL_ADDRESS", "").strip()
GMAIL_PASS = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
SCAN_COUNT = 50

URGENT_KW = ["urgent","asap","deadline","immediately","action required","time sensitive",
    "overdue","past due","invoice","payment due","legal","lawsuit","critical",
    "emergency","final notice","expires","expiring","last chance"]
REPLY_KW = ["?","question","can you","could you","please","request",
    "following up","follow-up","reminder","let me know","thoughts"]
NOISE_PATTERNS = [r"unsubscribe",r"newsletter",r"no-reply@",r"noreply@",
    r"marketing@",r"notifications?@",r"donotreply@",
    r"@.*\.(mailchim|sendgrid|constantcontact|klaviyo)"]
NOISE_SUBJECTS = ["sale","% off","deal","offer","promo","subscribe","newsletter",
    "weekly digest","monthly update","announcement"]

def decode_str(s):
    if not s: return ""
    parts = decode_header(s)
    r = []
    for part,enc in parts:
        if isinstance(part,bytes):
            try: r.append(part.decode(enc or "utf-8",errors="replace"))
            except: r.append(part.decode("utf-8",errors="replace"))
        else: r.append(str(part))
    return " ".join(r)

def is_noise(sender,subject):
    text = (sender + " " + subject).lower()
    for p in NOISE_PATTERNS:
        if re.search(p,text): return True
    for kw in NOISE_SUBJECTS:
        if kw in subject.lower(): return True
    return False

def score(subject,snippet,sender,age_hours,has_replied):
    s=50
    subj_low=subject.lower(); snip_low=snippet.lower()
    for kw in URGENT_KW:
        if kw in subj_low or kw in snip_low: s+=20; break
    for kw in REPLY_KW:
        if kw in subj_low or kw in snip_low: s+=10; break
    if age_hours<2: s+=5
    elif age_hours>120: s-=20
    elif age_hours>48: s-=10
    if has_replied: s-=15
    return max(0,min(s,100))

mail = imaplib.IMAP4_SSL("imap.gmail.com",993)
try:
    mail.login(GMAIL_ADDR,GMAIL_PASS)
except Exception as e:
    print(f"ERROR: Login failed for {GMAIL_ADDR}: {e}")
    sys.exit(1)
mail.select("INBOX",readonly=True)

_,msg_ids = mail.search(None,"ALL")
all_ids = msg_ids[0].split() if msg_ids and msg_ids[0] else []
if not all_ids:
    print("Inbox empty")
    sys.exit(0)

recent_ids = all_ids[-SCAN_COUNT:] if len(all_ids)>SCAN_COUNT else all_ids
recent_ids = list(reversed(recent_ids))

emails = []
now = datetime.now(timezone.utc)

for uid in recent_ids:
    try:
        _,raw = mail.fetch(uid,"(RFC822.HEADER FLAGS)")
        if not raw or not raw[0]: continue
        raw_header = raw[0][1] if isinstance(raw[0],tuple) else raw[0]
        msg = email.message_from_bytes(raw_header)
        subject = decode_str(msg.get("Subject","(no subject)"))
        sender = decode_str(msg.get("From",""))
        date_str = msg.get("Date","")
        flags_raw = raw[0][0] if isinstance(raw[0],tuple) else b""
        has_replied = b"\\Answered" in flags_raw
        try:
            sent_dt = parsedate_to_datetime(date_str)
            if sent_dt.tzinfo is None: sent_dt=sent_dt.replace(tzinfo=timezone.utc)
            age_hours = (now-sent_dt).total_seconds()/3600
        except: age_hours=0
        body=""
        try:
            _,raw_body = mail.fetch(uid,"(BODY[TEXT]<0.300>)")
            if raw_body and raw_body[0] and isinstance(raw_body[0],tuple):
                raw_b=raw_body[0][1]
                if raw_b: body=raw_b.decode("utf-8",errors="replace").strip()[:200]
        except: pass
        noise=is_noise(sender,subject)
        urgency=score(subject,body,sender,age_hours,has_replied)
        sm = re.search(r'"?([^"<]+)"?\s*<([^>]+)>',sender)
        sname = sm.group(1).strip() if sm else sender
        semail = sm.group(2).strip() if sm else sender
        emails.append({"uid":uid,"subject":subject,"sender":sname,"sender_email":semail,
            "age_hours":age_hours,"urgency":urgency,"is_noise":noise,"replied":has_replied})
    except: continue

mail.logout()

actionable=[e for e in emails if not e["is_noise"]]
noise=[e for e in emails if e["is_noise"]]
actionable.sort(key=lambda e:-e["urgency"])

# Output compact digest
total=len(emails)
act=len(actionable)
noi=len(noise)
high=sum(1 for e in actionable if e["urgency"]>=70)
replied=sum(1 for e in actionable if e["replied"])

print(f"INBOX:{GMAIL_ADDR}")
print(f"Scanned:{total} Actionable:{act} Noise:{noi} HighPrio:{high} Replied:{replied}")
if actionable:
    for e in actionable[:10]:
        age = f"{int(e['age_hours'])}h" if e['age_hours']<48 else f"{int(e['age_hours']//24)}d"
        r = " [replied]" if e['replied'] else ""
        print(f"  [{e['urgency']:3d}] {e['sender'][:20]:20s} | {e['subject'][:50]:50s} | {age}{r}")
