#!/usr/bin/env python3
"""Iris - Inbox Intelligence for jhenderson87@gmail.com
Monitors Gmail inbox for dealer replies and other urgent emails.
"""
import os
import sys
# Force UTF-8 for stdout on Windows to avoid UnicodeEncodeError
sys.stdout.reconfigure(encoding='utf-8')

import imaplib
import email
import re
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

GMAIL_ADDR = os.environ.get("GMAIL_ADDRESS", "jhenderson87@gmail.com").strip()
GMAIL_PASS = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
try:
    SCAN_COUNT = int(os.environ.get("SCAN_COUNT", "50"))
except ValueError:
    SCAN_COUNT = 50

VIP_RAW = os.environ.get("VIP_SENDERS", "")
VIP_LIST = [v.strip().lower() for v in VIP_RAW.split(",") if v.strip()]
YOUR_NAME = os.environ.get("YOUR_NAME", "James").strip()

DEALER_KEYWORDS = [
    "chevrolet", "chevy", "traverse", "rs", "quote", "otd", "out-the-door",
    "vehicle", "inventory", "car", "auto", "dealer", "dealership",
    "financing", "payment", "price", "discount", "rebate", "incentive",
    "appreciation", "costco", "military", "educator", "teacher",
    "gm", "general motors", "cadillac", "buick", "gmc",
]

URGENT_KEYWORDS = [
    "urgent", "asap", "deadline", "immediately", "action required", "time sensitive",
    "overdue", "past due", "invoice", "payment due", "legal", "lawsuit", "critical",
    "emergency", "final notice", "expires", "expiring", "last chance",
]

REPLY_KEYWORDS = [
    "?", "question", "can you", "could you", "please", "request",
    "following up", "follow-up", "reminder", "let me know", "thoughts",
]

NOISE_PATTERNS = [
    r"unsubscribe", r"newsletter", r"no-reply@", r"noreply@",
    r"marketing@", r"notifications?@", r"donotreply@",
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


def is_noise(sender, subject):
    text = (sender + " " + subject).lower()
    for pat in NOISE_PATTERNS:
        if re.search(pat, text):
            return True
    for kw in NOISE_SUBJECTS:
        if kw in subject.lower():
            return True
    return False


def score_email(subject, snippet, sender, age_hours, has_replied):
    score = 50
    subj_low = subject.lower()
    snip_low = snippet.lower()
    sender_low = sender.lower()

    for kw in URGENT_KEYWORDS:
        if kw in subj_low or kw in snip_low:
            score += 20
            break

    for kw in REPLY_KEYWORDS:
        if kw in subj_low or kw in snip_low:
            score += 10
            break

    for vip in VIP_LIST:
        if vip in sender_low:
            score += 25
            break

    for kw in DEALER_KEYWORDS:
        if kw in subj_low or kw in snip_low:
            score += 15
            break

    if age_hours < 2:
        score += 10
    elif age_hours < 24:
        score += 5
    elif age_hours > 48:
        score -= 10
    elif age_hours > 120:
        score -= 20

    if has_replied:
        score -= 15

    return max(0, min(score, 100))


def scan_inbox():
    if not GMAIL_PASS:
        print("ERROR: GMAIL_APP_PASSWORD not set.")
        print("Set it: setx GMAIL_APP_PASSWORD 'your_app_password'")
        raise SystemExit(1)

    print(f"Iris - Monitoring {GMAIL_ADDR}")
    print(f"Scanning {SCAN_COUNT} recent emails...")

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(GMAIL_ADDR, GMAIL_PASS)
        mail.select("INBOX", readonly=True)
    except imaplib.IMAP4.error as e:
        print(f"IMAP login failed: {e}")
        raise SystemExit(1)
    except Exception as e:
        print(f"Connection error: {e}")
        raise SystemExit(1)

    _, msg_ids = mail.search(None, "ALL")
    all_ids = msg_ids[0].split() if msg_ids and msg_ids[0] else []
    if not all_ids:
        print("Inbox empty.")
        return [], [], []

    recent_ids = all_ids[-SCAN_COUNT:] if len(all_ids) > SCAN_COUNT else all_ids
    recent_ids = list(reversed(recent_ids))

    emails_data = []
    now = datetime.now(timezone.utc)

    print(f"Fetching {len(recent_ids)} emails...")
    for uid in recent_ids:
        try:
            _, raw = mail.fetch(uid, "(RFC822.HEADER FLAGS)")
            if not raw or not raw[0]:
                continue
            raw_header = raw[0][1] if isinstance(raw[0], tuple) else raw[0]
            msg = email.message_from_bytes(raw_header)
            subject = decode_str(msg.get("Subject", "(no subject)"))
            sender = decode_str(msg.get("From", ""))
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
                sender_name = sender_match.group(1).strip()
                sender_email = sender_match.group(2).strip()
            else:
                sender_name = sender
                sender_email = sender

            emails_data.append({
                "uid": uid,
                "subject": subject,
                "sender": sender_name,
                "sender_email": sender_email,
                "age_hours": age_hours,
                "snippet": body_snippet,
                "urgency": urgency,
                "is_noise": noise,
                "replied": has_replied,
            })
        except Exception:
            continue

    mail.logout()

    actionable = [e for e in emails_data if not e["is_noise"]]
    noise = [e for e in emails_data if e["is_noise"]]
    actionable.sort(key=lambda e: -e["urgency"])

    return actionable, noise, emails_data


def print_report(actionable, noise, emails_data):
    print(f"\n{'='*70}")
    print(f"PRIORITY INBOX - {len(actionable)} actionable emails")
    print(f"{'='*70}")
    print(f"{'Score':<7} {'From':<22} {'Subject':<45} {'Age':<8}")
    print("-" * 80)

    for e in actionable[:20]:
        age_str = f"{int(e['age_hours'])}h" if e["age_hours"] < 48 else f"{int(e['age_hours'] // 24)}d"
        print(f"{e['urgency']:<7} {e['sender'][:20]:<22} {e['subject'][:43]:<45} {age_str:<8}")

    top5 = [e for e in actionable if not e["replied"]][:5]
    if top5:
        print(f"\nTOP 5 UNREPLIED:")
        for e in top5:
            print(f"  [{e['urgency']:>2}] {e['sender']:<20} | {e['subject'][:40]}")

    print(f"\n{'='*70}")
    print(f"SUMMARY: Scanned={len(emails_data)} Actionable={len(actionable)} Noise={len(noise)} Replied={sum(1 for e in actionable if e['replied'])}")
    print(f"High priority (70+): {sum(1 for e in actionable if e['urgency'] >= 70)}")
    print(f"{'='*70}")


def save_report(actionable, emails_data):
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H%M")
    report_dir = "C:/Users/compj/.openclaw/workspace/car-search/sessions/2026-06-10-traverse-rs-georgia"
    os.makedirs(report_dir, exist_ok=True)
    report_file = f"{report_dir}/inbox_report_{date_str}_{time_str}.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"# Iris Report - {date_str}\n\n")
        f.write(f"Account: jhenderson87@gmail.com\n")
        f.write(f"Scanned: {len(emails_data)} | Actionable: {len(actionable)}\n\n")
        f.write("## Priority Emails\n\n")
        f.write("| Score | From | Subject | Age |\n")
        f.write("|-------|------|---------|-----|\n")
        for e in actionable[:20]:
            age_str = f"{int(e['age_hours'])}h" if e["age_hours"] < 48 else f"{int(e['age_hours']//24)}d"
            f.write(f"| {e['urgency']} | {e['sender']} | {e['subject']} | {age_str} |\n")

        dealer_emails = [e for e in actionable if any(
            kw in e['subject'].lower() or kw in e['sender_email'].lower()
            for kw in ['chevrolet', 'chevy', 'vaden', 'days', 'cunningham', 'five star', 'butler']
        )]
        if dealer_emails:
            f.write("\n## Dealer Replies\n\n")
            for e in dealer_emails:
                age_str = f"{int(e['age_hours'])}h" if e["age_hours"] < 48 else f"{int(e['age_hours']//24)}d"
                f.write(f"- **[{e['urgency']}]** {e['sender']} ({e['sender_email']}) - {e['subject']} - {age_str} ago\n")
                if e['snippet']:
                    f.write(f"  > {e['snippet'][:150]}...\n")

    print(f"\nReport saved to: {report_file}")
    return report_file


def main():
    actionable, noise, emails_data = scan_inbox()
    print_report(actionable, noise, emails_data)
    report_path = save_report(actionable, emails_data)

    dealer_replies = [e for e in actionable if any(
        kw in e['subject'].lower() or kw in e['sender_email'].lower()
        for kw in ['chevrolet', 'chevy', 'vaden', 'days', 'cunningham', 'five star', 'butler', 'traverse']
    ) and not e['replied'] and e['age_hours'] < 24]

    if dealer_replies:
        print(f"\n*** NEW DEALER REPLIES DETECTED ***")
        for e in dealer_replies:
            print(f"  EMAIL: {e['sender']}: {e['subject']}")

        flag_file = "C:/Users/compj/.openclaw/workspace/car-search/dealer_reply_detected.flag"
        with open(flag_file, "w") as f:
            f.write(f"Dealer replies detected at {datetime.now().isoformat()}\n")
            for e in dealer_replies:
                f.write(f"- {e['sender']}: {e['subject']}\n")

    return dealer_replies


if __name__ == "__main__":
    main()
