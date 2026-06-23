#!/usr/bin/env python3
"""Daily Gmail cleanup — empty Spam and Trash folders."""
import imaplib, json, os, sys, time
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

START_TIME = time.time()
MAX_RUNTIME = 180

def should_exit():
    return time.time() - START_TIME > MAX_RUNTIME

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


def empty_folder(mail, folder_name, max_msgs=500):
    """Empty a folder using bulk UID operations."""
    if should_exit():
        return None
    try:
        status, _ = mail.select(folder_name)
        if status != "OK":
            return None

        # Use UID search for reliability
        _, data = mail.uid("search", None, "ALL")
        msg_uids = data[0].split()
        if not msg_uids:
            return 0

        # Limit to avoid timeouts
        if len(msg_uids) > max_msgs:
            msg_uids = msg_uids[:max_msgs]

        count = len(msg_uids)
        uid_str = b",".join(msg_uids).decode()

        # Bulk store + expunge (much faster than one-by-one)
        mail.uid("store", uid_str, "+FLAGS", "(\\Deleted)")
        mail.expunge()
        return count
    except Exception as e:
        print(f"    ERR: {e}")
        return None


def cleanup_account(email_addr):
    if should_exit():
        print("  GLOBAL TIMEOUT")
        return None, None

    print(f"\n{'='*50}")
    print(f"Account: {email_addr}")
    print(f"{'='*50}")

    password = get_password(email_addr)
    if not password:
        print("  SKIP: password not found")
        return None, None

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=15)
        mail.login(email_addr, password)
    except Exception as e:
        print(f"  LOGIN FAILED: {e}")
        return None, None

    # Empty Spam
    spam_deleted = empty_folder(mail, "[Gmail]/Spam")
    spam_status = f"{spam_deleted} deleted" if spam_deleted is not None else "folder missing"
    print(f"  Spam: {spam_status}")

    # Empty Trash
    trash_deleted = empty_folder(mail, "[Gmail]/Trash")
    trash_status = f"{trash_deleted} deleted" if trash_deleted is not None else "folder missing"
    print(f"  Trash: {trash_status}")

    # Also check for "Deleted Messages" (Apple Mail alternate)
    apple_deleted = empty_folder(mail, "Deleted Messages")
    if apple_deleted is not None and apple_deleted > 0:
        print(f"  Deleted Messages (Apple): {apple_deleted} deleted")

    mail.logout()
    return spam_deleted or 0, trash_deleted or 0


if __name__ == "__main__":
    print(f"🗑 Gmail Cleanup — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("Emptying Spam and Trash folders...")

    total_spam = 0
    total_trash = 0

    for email_addr in ACCOUNTS.keys():
        s, t = cleanup_account(email_addr)
        if s is not None:
            total_spam += s
            total_trash += t
        time.sleep(0.5)

    print(f"\n{'='*50}")
    print(f"Done. Spam deleted: {total_spam} | Trash deleted: {total_trash}")
    print(f"{'='*50}")
