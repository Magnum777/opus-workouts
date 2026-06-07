import imaplib, email, json, os
from email.header import decode_header
from datetime import datetime, timedelta

LOCAL_CONFIG = os.path.join(os.path.dirname(__file__), ".gmail_accounts.json")

ACCOUNTS = {
    "compjunkie@gmail.com":         "GMAIL_APP_PASSWORD_COMPJUNKIE",
    "jhenderson87@gmail.com":       "GMAIL_APP_PASSWORD_JHENDERSON",
    "layeredmediallc@gmail.com":    "GMAIL_APP_PASSWORD_LAYEREDMEDIA",
    "nova.cofounder@gmail.com":     "GMAIL_APP_PASSWORD_NOVA",
}

def get_password(email_addr):
    pass_var = ACCOUNTS.get(email_addr, "")
    if not pass_var:
        return ""
    env = os.environ.get(pass_var, "").strip().replace(" ", "")
    if env:
        return env
    try:
        with open(LOCAL_CONFIG, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get(email_addr, "").strip().replace(" ", "")
    except Exception:
        return ""

def decode_field(s):
    if not s:
        return ""
    parts = decode_header(s)
    out = []
    for part, enc in parts:
        if isinstance(part, bytes):
            try:
                out.append(part.decode(enc or "utf-8", errors="replace"))
            except Exception:
                out.append(part.decode("utf-8", errors="replace"))
        else:
            out.append(str(part))
    return " ".join(out)

all_spam = []

for email_addr in ACCOUNTS:
    env_pass = get_password(email_addr)
    if not env_pass:
        print(f"SKIP: {email_addr} (no password)")
        continue
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=30)
        mail.login(email_addr, env_pass)
    except Exception as e:
        print(f"LOGIN FAILED: {email_addr}: {e}")
        continue
    try:
        mail.select("[Gmail]/Spam")
    except Exception:
        mail.logout()
        continue
    since_date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
    _, data = mail.search(None, f"(SINCE {since_date})")
    all_ids = data[0].split()
    if not all_ids:
        print(f"{email_addr}: Spam folder empty (last 30 days)")
        mail.logout()
        continue
    max_msgs = 200 if "compjunkie" in email_addr else 100
    uids = all_ids[-max_msgs:]
    print(f"\n{'='*60}")
    print(f"{email_addr}: {len(uids)} spam messages (last 30 days)")
    print(f"{'='*60}")
    count = 0
    for uid in uids:
        try:
            _, fetched = mail.fetch(uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
            for item in fetched:
                if isinstance(item, tuple):
                    try:
                        msg = email.message_from_bytes(item[1])
                    except Exception:
                        continue
                    sender = decode_field(msg.get("From", ""))
                    subject = decode_field(msg.get("Subject", ""))
                    date = decode_field(msg.get("Date", ""))
                    count += 1
                    print(f"  {count}. [{sender[:45]}] {subject[:60]}")
                    all_spam.append({
                        "account": email_addr,
                        "sender": sender,
                        "subject": subject,
                        "date": date
                    })
        except Exception:
            continue
    mail.logout()

print(f"\n{'='*60}")
print(f"TOTAL spam messages scanned: {len(all_spam)}")
print(f"{'='*60}")

# Save for pattern analysis
with open("spam_dump_2026-06-07.json", "w", encoding="utf-8") as f:
    json.dump(all_spam, f, indent=2)
print("Saved to spam_dump_2026-06-07.json")
