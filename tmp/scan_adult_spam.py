import imaplib
import email
import re
from datetime import datetime

# Check all accounts for spam/adult content
accounts = {
    "compjunkie@gmail.com": "lghh qjlc tmye qxrn",
    "jhenderson87@gmail.com": "GMAIL_APP_PASSWORD_JHENDERSON",
    "layeredmediallc@gmail.com": "GMAIL_APP_PASSWORD_LAYEREDMEDIA",
    "nova.cofounder@gmail.com": "n20CQ9aRcvQdKCFf",
}

adult_keywords = [
    'adult', 'dating', 'hookup', 'flirt', 'sexy', 'hot singles', 'meet women',
    'meet men', 'casual encounter', 'naughty', 'lust', 'passion', 'intimate',
    'escort', 'massage', 'adult friend', 'fuck', 'sex', 'porn', 'xxx',
    'onlyfans', 'cam', 'webcam', 'private show', 'tease', 'temptation',
    'arousing', 'desire', 'fantasy', 'pleasure', 'sensual', 'erotic'
]

for email_addr, password in accounts.items():
    print(f"\n{'='*60}")
    print(f"Account: {email_addr}")
    print(f"{'='*60}")
    
    # Try to get password from env if placeholder
    if password.startswith("GMAIL_APP_PASSWORD_"):
        import os
        password = os.environ.get(password, "")
    
    if not password:
        print(f"  No password available — skipping")
        continue
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_addr, password)
        
        # Check Spam folder
        for folder in ["[Gmail]/Spam", "Spam", "Junk"]:
            status, _ = mail.select(folder)
            if status == 'OK':
                # Search last 7 days
                status, messages = mail.search(None, 'SINCE', '14-Jun-2026')
                if status == 'OK':
                    msg_ids = messages[0].split()
                    print(f"  {folder}: {len(msg_ids)} messages")
                    
                    adult_count = 0
                    checked = 0
                    for msg_id in msg_ids[-20:]:  # Check last 20
                        if checked >= 10:  # Limit checks per account
                            break
                        status, msg_data = mail.fetch(msg_id, '(RFC822)')
                        if status == 'OK':
                            raw = msg_data[0][1]
                            msg = email.message_from_bytes(raw)
                            subject = msg.get('Subject', '').lower()
                            from_addr = msg.get('From', '').lower()
                            
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        try:
                                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore').lower()
                                            break
                                        except:
                                            pass
                            else:
                                try:
                                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore').lower()
                                except:
                                    pass
                            
                            text = subject + " " + from_addr + " " + body[:500]
                            
                            found_keywords = [k for k in adult_keywords if k in text]
                            if found_keywords:
                                adult_count += 1
                                print(f"    ⚠️  ADULT: {subject[:80]}")
                                print(f"       From: {from_addr[:80]}")
                                print(f"       Keywords: {found_keywords}")
                        
                        checked += 1
                    
                    if adult_count == 0:
                        print(f"    No adult content found in checked messages")
                    else:
                        print(f"    *** FOUND {adult_count} adult/spam messages ***")
                break
        
        mail.logout()
        
    except Exception as e:
        print(f"  Error: {e}")

print("\n\nScan complete.")
