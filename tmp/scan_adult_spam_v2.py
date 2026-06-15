import imaplib
import email
import re
import os

# Check accounts with known passwords
accounts = {}

# jhenderson87 - this one works (Iris uses it)
jh_pass = os.environ.get("GMAIL_APP_PASSWORD_JHENDERSON", "")
if jh_pass:
    accounts["jhenderson87@gmail.com"] = jh_pass

# layeredmedia
lm_pass = os.environ.get("GMAIL_APP_PASSWORD_LAYEREDMEDIA", "")
if lm_pass:
    accounts["layeredmediallc@gmail.com"] = lm_pass

# compjunkie
comp_pass = os.environ.get("GMAIL_APP_PASSWORD_COMPJUNKIE", "")
if comp_pass:
    accounts["compjunkie@gmail.com"] = comp_pass

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
    print(f"\n{'='*60}")
    print(f"Account: {email_addr}")
    print(f"{'='*60}")
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_addr, password)
        
        # Check Spam folder
        spam_found = False
        for folder in ["[Gmail]/Spam", "Spam", "Junk"]:
            status, _ = mail.select(folder)
            if status == 'OK':
                # Search ALL spam (not just recent)
                status, messages = mail.search(None, 'ALL')
                if status == 'OK':
                    msg_ids = messages[0].split()
                    print(f"  {folder}: {len(msg_ids)} total messages")
                    
                    adult_count = 0
                    for msg_id in msg_ids[-30:]:  # Check last 30
                        status, msg_data = mail.fetch(msg_id, '(RFC822)')
                        if status == 'OK':
                            raw = msg_data[0][1]
                            msg = email.message_from_bytes(raw)
                            
                            # Get subject safely
                            subject_raw = msg.get('Subject', '')
                            if isinstance(subject_raw, str):
                                subject = subject_raw.lower()
                            else:
                                subject = str(subject_raw).lower()
                            
                            from_raw = msg.get('From', '')
                            if isinstance(from_raw, str):
                                from_addr = from_raw.lower()
                            else:
                                from_addr = str(from_raw).lower()
                            
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
                                    payload = msg.get_payload(decode=True)
                                    if payload:
                                        body = payload.decode('utf-8', errors='ignore').lower()
                                except:
                                    pass
                            
                            text = subject + " " + from_addr + " " + body[:800]
                            
                            found_keywords = [k for k in adult_keywords if k in text]
                            if found_keywords:
                                adult_count += 1
                                spam_found = True
                                print(f"    ⚠️  MATCH: {subject[:100]}")
                                print(f"       From: {from_addr[:100]}")
                    
                    if adult_count > 0:
                        print(f"    *** FOUND {adult_count} adult/spam messages ***")
                    else:
                        print(f"    No adult content in last 30 checked")
                
                mail.close()
                break
        
        if not spam_found:
            print(f"  Spam folder empty or no adult content found")
        
        mail.logout()
        
    except Exception as e:
        print(f"  Error: {e}")

print("\n\nScan complete.")
