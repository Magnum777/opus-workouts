#!/usr/bin/env python3
"""Search Gmail for specific messages."""
import imaplib, json, os, sys, email
from email.header import decode_header

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

LOCAL_CONFIG = os.path.join(os.path.dirname(__file__), ".gmail_accounts.json")

def get_password(email_addr):
    with open(LOCAL_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config.get(email_addr, "").strip().replace(" ", "")

def search_gmail(account, query, max_results=10):
    password = get_password(account)
    if not password:
        print(f"ERROR: No password for {account}")
        return

    mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=15)
    mail.login(account, password)
    mail.select("INBOX")

    # IMAP search
    status, data = mail.search(None, query)
    if status != "OK":
        print(f"Search failed: {status}")
        mail.logout()
        return

    msg_ids = data[0].split()
    print(f"Found {len(msg_ids)} messages")

    # Get last N
    for mid in msg_ids[-max_results:]:
        _, msg_data = mail.fetch(mid, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        subj = str(email.header.make_header(email.header.decode_header(msg["Subject"] or "")))
        from_addr = str(email.header.make_header(email.header.decode_header(msg["From"] or "")))
        date = msg["Date"] or ""

        # Get body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                if ct == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        try:
                            body = payload.decode(charset, errors="replace")
                        except:
                            body = payload.decode("utf-8", errors="replace")
                        break
                elif ct == "text/html" and not body:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        try:
                            body = payload.decode(charset, errors="replace")
                        except:
                            body = payload.decode("utf-8", errors="replace")
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                try:
                    body = payload.decode(charset, errors="replace")
                except:
                    body = payload.decode("utf-8", errors="replace")

        print(f"\n{'='*60}")
        print(f"Date: {date}")
        print(f"From: {from_addr}")
        print(f"Subject: {subj}")
        print(f"{'='*60}")
        # Print first 2000 chars of body
        if body:
            print(body[:2000])
        else:
            print("[No plain text body found]")

    mail.logout()

if __name__ == "__main__":
    account = sys.argv[1] if len(sys.argv) > 1 else "jhenderson87@gmail.com"
    query = sys.argv[2] if len(sys.argv) > 2 else '(OR (FROM "delta") (SUBJECT "Delta"))'
    max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    search_gmail(account, query, max_results)