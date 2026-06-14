import imaplib
import email
from email.header import decode_header
import re

IMAP_SERVER = "imap.gmail.com"
EMAIL = "nova.cofounder@gmail.com"
PASSWORD = "n20CQ9aRcvQdKCFf"

print("Connecting to Gmail IMAP...")
try:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    print("Logged in!")
    
    mail.select("inbox")
    
    # Search ALL emails (not just unread — MFA might already be read)
    status, messages = mail.search(None, 'ALL')
    
    if status == 'OK':
        msg_ids = messages[0].split()
        print(f"Total messages: {len(msg_ids)}")
        
        # Check last 20 messages
        for msg_id in msg_ids[-20:]:
            status, msg_data = mail.fetch(msg_id, '(RFC822)')
            if status == 'OK':
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                from_addr = msg.get("From", "").lower()
                date = msg.get("Date", "")
                
                # Look for UniFi / SSO / MFA / verification emails
                keywords = ['unifi', 'sso', 'verification', 'code', 'mfa', '2fa', 'token', 'security', 'login']
                if any(k in from_addr or k in subject.lower() for k in keywords):
                    print(f"\n*** FOUND: {subject} ***")
                    print(f"From: {from_addr}")
                    print(f"Date: {date}")
                    
                    # Get body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body = part.get_payload(decode=True).decode()
                                    break
                                except:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except:
                            pass
                    
                    print(f"Body preview: {body[:800]}")
                    
                    # Look for 6-digit code
                    codes = re.findall(r'\b\d{6}\b', body)
                    if codes:
                        print(f"*** CODES FOUND: {codes} ***")
    
    mail.logout()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
