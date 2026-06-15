import imaplib
import email
import os
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

accounts = {}

jh_pass = os.environ.get("GMAIL_APP_PASSWORD_JHENDERSON", "")
if jh_pass:
    accounts["jhenderson87@gmail.com"] = jh_pass

lm_pass = os.environ.get("GMAIL_APP_PASSWORD_LAYEREDMEDIA", "")
if lm_pass:
    accounts["layeredmediallc@gmail.com"] = lm_pass

comp_pass = os.environ.get("GMAIL_APP_PASSWORD_COMPJUNKIE", "")
if comp_pass:
    accounts["compjunkie@gmail.com"] = comp_pass

nova_pass = "n20CQ9aRcvQdKCFf"

spam_keywords = [
    'adult', 'dating', 'hookup', 'flirt', 'sexy', 'hot singles', 'meet women',
    'meet men', 'casual encounter', 'naughty', 'lust', 'passion', 'intimate',
    'escort', 'massage', 'adult friend', 'fuck', 'sex', 'porn', 'xxx',
    'onlyfans', 'cam', 'webcam', 'private show', 'tease', 'temptation',
    'arousing', 'desire', 'fantasy', 'pleasure', 'sensual', 'erotic',
    'single women', 'single men', 'local women', 'local singles',
    'mature', 'milf', 'cougar', 'sugar daddy', 'sugar baby',
    'fckfriendfinder', 'hers-love', 'bestxdate', 'flirtyynights',
    'poladina', 'henrydixonjournal', 'freepinoko', 'foxytemptation',
    'arousingdates', 'teaseeasyx', 'freeyvenas'
]

for email_addr, password in accounts.items():
    print(f"\nAccount: {email_addr}")
    print("=" * 70)
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_addr, password)
        
        # Check INBOX
        status, _ = mail.select("INBOX")
        if status == 'OK':
            status, messages = mail.search(None, 'ALL')
            if status == 'OK':
                msg_ids = messages[0].split()
                print(f"Inbox: {len(msg_ids)} total messages")
                
                spam_in_inbox = 0
                checked = 0
                for msg_id in msg_ids[-100:]:  # Check last 100 inbox messages
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
                        
                        text = subject + " " + from_addr + " " + body[:1500]
                        
                        found_keywords = [k for k in spam_keywords if k in text]
                        if found_keywords:
                            spam_in_inbox += 1
                            safe_subject = subject.encode('ascii', 'replace').decode()
                            safe_from = from_addr.encode('ascii', 'replace').decode()
                            print(f"  INBOX ADULT/SPAM: {safe_subject[:100]}")
                            print(f"    From: {safe_from[:100]}")
                
                if spam_in_inbox > 0:
                    print(f"\n*** FOUND {spam_in_inbox} adult/spam messages in INBOX (last {checked} checked) ***")
                else:
                    print(f"No adult/spam in last {checked} inbox messages")
            
            mail.close()
        
        mail.logout()
        
    except Exception as e:
        print(f"Error: {e}")

print("\nDone.")
