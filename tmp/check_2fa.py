import imaplib
import email
from email.header import decode_header
import time

# Gmail IMAP settings
IMAP_SERVER = "imap.gmail.com"
EMAIL = "nova.cofounder@gmail.com"
PASSWORD = "n20CQ9aRcvQdKCFf"

print("Connecting to Gmail...")
try:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    print("Logged in successfully")
    
    # Select inbox
    mail.select("inbox")
    
    # Search for recent emails (last 5 minutes)
    # Use SINCE to find emails from today
    status, messages = mail.search(None, 'UNSEEN')
    
    if status == 'OK':
        msg_ids = messages[0].split()
        print(f"Found {len(msg_ids)} unread messages")
        
        for msg_id in msg_ids[-5:]:  # Check last 5 unread
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            if status == 'OK':
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                from_addr = msg.get("From", "")
                
                print(f"\nFrom: {from_addr}")
                print(f"Subject: {subject}")
                
                # Check if it's from UniFi
                if "unifi" in from_addr.lower() or "ui.com" in from_addr.lower() or "sso" in subject.lower() or "verification" in subject.lower() or "code" in subject.lower():
                    print("*** UNIFI/SSO EMAIL FOUND ***")
                    # Get body
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                print(f"Body: {body[:500]}")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()
                        print(f"Body: {body[:500]}")
    else:
        print("No unread messages found")
    
    mail.logout()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
