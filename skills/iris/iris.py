import os, imaplib, email, re, sys
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

# Force UTF-8 on Windows pipes/subprocess
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Detect if we're running in a pipe/subprocess (no real terminal)
IS_TTY = sys.stdout.isatty()

def cprint(text):
    """Print text; strip ANSI if not a TTY."""
    if not IS_TTY:
        import re
        text = re.sub(r'\[[^\]]*\]', '', text)
    print(text)

def box_print(title, lines, border="-"):
    """Simple plain-text box for non-TTY output."""
    if IS_TTY:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
        for line in lines:
            print(line)
        print(f"{'='*60}\n")
    else:
        print(f"\n--- {title} ---")
        for line in lines:
            print(line)
        print(f"---\n")

GMAIL_ADDR = os.environ.get("GMAIL_ADDRESS", "").strip()
GMAIL_PASS = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
try:
    SCAN_COUNT = int(os.environ.get("SCAN_COUNT", "50"))
except ValueError:
    cprint("WARNING: SCAN_COUNT must be a whole number — defaulting to 50")
    SCAN_COUNT = 50
VIP_RAW    = os.environ.get("VIP_SENDERS", "")
VIP_LIST   = [v.strip().lower() for v in VIP_RAW.split(",") if v.strip()]
YOUR_NAME  = os.environ.get("YOUR_NAME", "").strip()
YOUR_ROLE  = os.environ.get("YOUR_ROLE", "").strip()

if not GMAIL_ADDR or not GMAIL_PASS:
    box_print("SETUP REQUIRED", [
        "GMAIL_ADDRESS and GMAIL_APP_PASSWORD are both required.",
        "",
        "How to create an app password:",
        "1. Go to myaccount.google.com/apppasswords",
        "2. Select Mail -> Other (Custom name)",
        "3. Copy the 16-character password",
        "4. Set GMAIL_APP_PASSWORD to that value",
    ])
    raise SystemExit(1)

URGENT_KEYWORDS = [
    "urgent", "asap", "deadline", "immediately", "action required", "time sensitive",
    "overdue", "past due", "invoice", "payment due", "legal", "lawsuit", "critical",
    "emergency", "final notice", "expires", "expiring", "last chance",
]
REPLY_KEYWORDS = [
    "?", "question", "can you", "could you", "please", "request",
    "following up", "follow-up", "reminder", "let me know", "thoughts",
]
QUESTION_KW = ["?", "question", "can you", "could you", "help", "assist"]
NOISE_PATTERNS = [
    r"unsubscribe", r"newsletter", r"no-reply@", r"noreply@",
    r"marketing@", r"notifications?@", r"donotreply@",
    r"@.*\.(mailchim|sendgrid|constantcontact|klaviyo)",
]
NOISE_SUBJECTS = [
    "sale", "% off", "deal", "offer", "promo", "subscribe", "newsletter",
    "weekly digest", "monthly update", "announcement",
]

def decode_str(s):
    if not s:
        return ""
    parts = decode_header(s)
    result = []
    for part, enc in parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(enc or "utf-8", errors="replace"))
            except Exception:
                result.append(part.decode("utf-8", errors="replace"))
        else:
            result.append(str(part))
    return " ".join(result)

def is_noise(sender: str, subject: str) -> bool:
    text = (sender + " " + subject).lower()
    for pat in NOISE_PATTERNS:
        if re.search(pat, text):
            return True
    for kw in NOISE_SUBJECTS:
        if kw in subject.lower():
            return True
    return False

def score_email(subject: str, snippet: str, sender: str, age_hours: float, has_replied: bool) -> int:
    score = 50
    subj_low = subject.lower()
    snip_low = snippet.lower()
    for kw in URGENT_KEYWORDS:
        if kw in subj_low or kw in snip_low:
            score += 20
            break
    for kw in REPLY_KEYWORDS:
        if kw in subj_low or kw in snip_low:
            score += 10
            break
    sender_low = sender.lower()
    for vip in VIP_LIST:
        if vip in sender_low:
            score += 25
            break
    if age_hours < 2:
        score += 5
    elif age_hours < 24:
        score += 0
    elif age_hours > 48:
        score -= 10
    elif age_hours > 120:
        score -= 20
    if has_replied:
        score -= 15
    return max(0, min(score, 100))

try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(GMAIL_ADDR, GMAIL_PASS)
    mail.select("INBOX", readonly=True)
except imaplib.IMAP4.error as e:
    box_print("LOGIN ERROR", [
        f"IMAP login failed: {e}",
        "",
        "Checklist:",
        "- Is GMAIL_ADDRESS correct? (full email, not just username)",
        "- Is GMAIL_APP_PASSWORD a 16-char app password?",
        "- Did you enable IMAP in Gmail Settings?",
    ])
    raise SystemExit(1)
except Exception as e:
    cprint(f"Connection error: {e}")
    raise SystemExit(1)

_, msg_ids = mail.search(None, "ALL")
all_ids = msg_ids[0].split() if msg_ids and msg_ids[0] else []
if not all_ids:
    cprint("Inbox is empty — nothing to triage.")
    raise SystemExit(0)

recent_ids = all_ids[-SCAN_COUNT:] if len(all_ids) > SCAN_COUNT else all_ids
recent_ids = list(reversed(recent_ids))

emails_data = []
now = datetime.now(timezone.utc)

cprint(f"Fetching {len(recent_ids)} emails...")
for uid in recent_ids:
    try:
        _, raw = mail.fetch(uid, "(RFC822.HEADER FLAGS)")
        if not raw or not raw[0]:
            continue
        raw_header = raw[0][1] if isinstance(raw[0], tuple) else raw[0]
        msg = email.message_from_bytes(raw_header)
        subject = decode_str(msg.get("Subject", "(no subject)"))
        sender  = decode_str(msg.get("From", ""))
        date_str = msg.get("Date", "")
        flags_raw = raw[0][0] if isinstance(raw[0], tuple) else b""
        has_replied = b"\\Answered" in flags_raw

        try:
            sent_dt = parsedate_to_datetime(date_str)
            if sent_dt.tzinfo is None:
                sent_dt = sent_dt.replace(tzinfo=timezone.utc)
            age_hours = (now - sent_dt).total_seconds() / 3600
        except Exception:
            age_hours = 0

        body_snippet = ""
        try:
            _, raw_body = mail.fetch(uid, "(BODY[TEXT]<0.300>)")
            if raw_body and raw_body[0] and isinstance(raw_body[0], tuple):
                raw_b = raw_body[0][1]
                if raw_b:
                    body_snippet = raw_b.decode("utf-8", errors="replace").strip()[:200]
        except Exception:
            pass

        noise = is_noise(sender, subject)
        urgency = score_email(subject, body_snippet, sender, age_hours, has_replied)

        sender_match = re.search(r'"?([^"<]+)"?\s*<([^>]+)>', sender)
        if sender_match:
            sender_name  = sender_match.group(1).strip()
            sender_email = sender_match.group(2).strip()
        else:
            sender_name  = sender
            sender_email = sender

        emails_data.append({
            "uid":          uid.decode() if isinstance(uid, bytes) else str(uid),
            "subject":      subject,
            "sender":       sender_name,
            "sender_email": sender_email,
            "age_hours":    age_hours,
            "snippet":      body_snippet,
            "urgency":      urgency,
            "is_noise":     noise,
            "replied":      has_replied,
        })
    except Exception:
        continue

mail.logout()

actionable = [e for e in emails_data if not e["is_noise"]]
noise      = [e for e in emails_data if e["is_noise"]]
actionable.sort(key=lambda e: -e["urgency"])

# Print priority table
print(f"\nPRIORITY INBOX — {len(actionable)} actionable emails")
print("-" * 85)
print(f"{'Score':<7} {'From':<24} {'Subject':<35} {'Age':<8} {'Status':<10}")
print("-" * 85)
for e in actionable[:20]:
    age_str = f"{int(e['age_hours'])}h" if e["age_hours"] < 48 else f"{int(e['age_hours'] // 24)}d"
    status = "replied" if e["replied"] else ""
    print(f"{e['urgency']:<7} {e['sender'][:23]:<24} {e['subject'][:34]:<35} {age_str:<8} {status:<10}")
print("-" * 85)

# Draft replies for top 5 unreplied
sig = f"\n\n—\n{YOUR_NAME or 'Best'}{', ' + YOUR_ROLE if YOUR_ROLE else ''}"
top5 = [e for e in actionable if not e["replied"]][:5]

if top5:
    print("\n--- DRAFT REPLIES ---")
    for e in top5:
        subj_low = e["subject"].lower()
        snip_low = e["snippet"].lower()
        greeting = f"Hi {e['sender'].split()[0]},"
        if any(k in subj_low or k in snip_low for k in ["urgent", "asap", "deadline", "overdue"]):
            body = "Thank you for flagging this — I'll look into it right away and get back to you shortly."
        elif any(k in subj_low or k in snip_low for k in QUESTION_KW):
            body = "Thanks for your message. To answer your question: [your answer here]\n\nLet me know if you need anything else."
        elif "re:" in subj_low or "fwd:" in subj_low:
            body = "Thanks for the follow-up. Here's where things stand: [brief update]\n\nHappy to jump on a call if that's easier."
        else:
            body = "Thanks for reaching out. I've reviewed your message and [your response here]."
        draft = f"{greeting}\n\n{body}{sig}"
        print(f"\n>> DRAFT: Re: {e['subject'][:50]} (urgency: {e['urgency']})")
        print(draft)
        print("-" * 50)

# Summary
print(f"\n{'='*60}")
print(f"  SUMMARY")
print(f"{'='*60}")
print(f"Scanned:    {len(emails_data)} emails")
print(f"Actionable: {len(actionable)}  |  Noise: {len(noise)}")
print(f"Already replied: {sum(1 for e in actionable if e['replied'])}")
print(f"High priority (70+): {sum(1 for e in actionable if e['urgency'] >= 70)}")
print(f"{'='*60}")

# Save report
if os.environ.get("IRIS_NO_REPORT") != "1":
    date_str    = datetime.now().strftime("%Y-%m-%d")
    report_file = f"inbox_report_{date_str}.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# Iris — Inbox Report — {date_str}\n\n")
        f.write(f"**Scanned:** {len(emails_data)}  **Actionable:** {len(actionable)}  **Noise:** {len(noise)}\n\n")
        f.write("## Priority Emails\n\n| Score | From | Subject | Age |\n|-------|------|---------|-----|\n")
        for e in actionable[:20]:
            age_str = f"{int(e['age_hours'])}h" if e["age_hours"] < 48 else f"{int(e['age_hours']//24)}d"
            f.write(f"| {e['urgency']} | {e['sender']} | {e['subject']} | {age_str} |\n")
        f.write("\n## Draft Replies\n\n")
        for e in top5:
            subj_low = e["subject"].lower()
            snip_low = e["snippet"].lower()
            greeting = f"Hi {e['sender'].split()[0]},"
            if any(k in subj_low or k in snip_low for k in ["urgent", "asap", "deadline"]):
                body = "Thank you for flagging this — I'll look into it right away."
            elif any(k in subj_low or k in snip_low for k in QUESTION_KW):
                body = "Thanks for your message. To answer your question: [your answer here]"
            else:
                body = "Thanks for reaching out. [your response here]"
            f.write(f"### Re: {e['subject']}\n\n```\n{greeting}\n\n{body}{sig}\n```\n\n")
    cprint(f"Done! Report saved to {report_file}")
else:
    cprint("Done! (report suppressed by IRIS_NO_REPORT)")
