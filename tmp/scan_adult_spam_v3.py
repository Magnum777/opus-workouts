import imaplib
import email
import re
import os
import io
import sys

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Check accounts with known passwords
accounts = {}

jh_pass = os.environ.get("GMAIL_APP_PASSWORD_JHENDERSON", "")
if jh_pass:
    accounts["jhenderson87@gmail.com"] = jh_pass

adult_keywords = [
    'adult', 'dating', 'hookup', 'flirt', 'sexy', 'hot singles', 'meet women',
    'meet men', 'casual encounter', 'naughty', 'lust', 'passion', 'intimate',
    'escort', 'massage', 'adult friend', 'fuck', 'sex', 'porn', 'xxx',
    'onlyfans', 'cam', 'webcam', 'private show', 'tease', 'temptation',
    'arousing', 'desire', 'fantasy', 'pleasure', 'sensual', 'erotic',
    'single women', 'single men', 'local women', 'local singles',
    'mature', 'milf', 'cougar', 'sugar daddy', 'sugar baby'
]

for email_addr, password in accounts.items():
    print(f"\nAccount: {email_addr}")
    print("=" * 60)
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_addr, password)
        
        # Check Spam folder
        status, _ = mail.select("[Gmail]/Spam")
        if status != 'OK':
            status, _ = mail.select("Spam")
        
        if status == 'OK':
            status, messages = mail.search(None, 'ALL')
            if status == 'OK':
                msg_ids = messages[0].split()
                print(f"Spam folder: {len(msg_ids)} total messages")
                
                adult_count = 0
                checked = 0
                for msg_id in msg_ids[-50:]:  # Check last 50
                    checked += 1
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                    if status == 'OK':
                        raw = msg_data[0][1]
                        msg = email.message_from_bytes(raw)
                        
                        subject_raw = msg.get('Subject', '')
                        subject = str(subject_raw).lower()
                        
                        from_raw = msg.get('From', '')
                        from_addr = str(from_raw).lower()
                        
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    try:
                                        payload = part.get_payload(decode=True)
                                        if payload:
                                            body = payload.decode('utf-8', errors='ignore').lower()
                                            break
                                    except:
                                        pass
                        else:
                            try:
                                payload = msg.get_payload(decode=True)
                                if payload:
                                    body = payload.decode('utf-8', errors='ignore').lower()
                            except:
                                pass
                        
                        text = subject + " " + from_addr + " " + body[:1000]
                        
                        found_keywords = [k for k in adult_keywords if k in text]
                        if found_keywords:
                            adult_count += 1
                            safe_subject = subject.encode('ascii', 'replace').decode()
                            safe_from = from_addr.encode('ascii', 'replace').decode()
                            print(f"  ADULT: {safe_subject[:80]}")
                            print(f"    From: {safe_from[:80]}")
                            print(f"    Keywords: {found_keywords}")
                
                if adult_count > 0:
                    print(f"\n*** TOTAL: {adult_count} adult/spam messages in last {checked} checked ***")
                else:
                    print(f"No adult content in last {checked} checked")
            
            mail.close()
        
        mail.logout()
        
    except Exception as e:
        print(f"Error: {e}")

print("\nDone.")
