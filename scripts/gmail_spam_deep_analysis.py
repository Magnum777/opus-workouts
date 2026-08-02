#!/usr/bin/env python3
"""IMAP Gmail spam pattern analysis — READ ONLY, no deletions.
Scans INBOX and Spam for the last 7 days and categorizes patterns."""
import imaplib, email, json, re, sys, os, time
from email.header import decode_header
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load passwords from local config file
LOCAL_CONFIG = os.path.join(os.path.dirname(__file__), ".gmail_accounts.json")

ACCOUNTS = {
    "compjunkie@gmail.com":         "GMAIL_APP_PASSWORD_COMPJUNKIE",
    "jhenderson87@gmail.com":       "GMAIL_APP_PASSWORD_JHENDERSON",
    "layeredmediallc@gmail.com":    "GMAIL_APP_PASSWORD_LAYEREDMEDIA",
    "nova.cofounder@gmail.com":     "GMAIL_APP_PASSWORD_NOVA",
}

def get_password(email_addr: str) -> str:
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

def decode_field(s: str) -> str:
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

def extract_domain(sender):
    match = re.search(r'<([^>]+)>', sender)
    addr = match.group(1) if match else sender
    return addr.split('@')[-1].lower() if '@' in addr else addr.lower()

def extract_sender_name(sender):
    name = sender.split('<')[0].strip() if '<' in sender else sender
    return name

def categorize(subject, sender, domain):
    s = subject.lower()
    n = sender.lower()
    d = domain.lower()
    categories = []

    # Telegram / WhatsApp scam lures
    if re.search(r'telegram|whatsapp|signal|missed.*(message|call)|someone.*(look|search|find).*(you|for you)|new message|unread message|replied to you|direct message', s):
        categories.append("telegram_whatsapp_scam")

    # Fake reward/loyalty programs
    if re.search(r'reward.*program|rewards?\b|unitedhealthcare|loyalty|points.*expire|claim.*reward|your.*reward|cashback|gift.*card|free.*gift|redeem.*now|bonus.*point', s):
        categories.append("fake_rewards_loyalty")

    # Crypto / investment spam
    if re.search(r'crypto|bitcoin|ethereum|nft|defi|staking|airdrop|wallet|blockchain|investment.*opportunity|guaranteed.*return|double.*(money|btc)|passive.*income|trading.*signal|forex|binary.*option', s):
        categories.append("crypto_investment")

    # Fake shipping / delivery
    if re.search(r'shipp(ed|ing)|deliver(y|ed|ing)|package|track(ing)?|dhl|fedex|ups|usps|customs|import.*duty|clearance|your.*order.*(shipped|arrived|on the way)|delivery.*failed|address.*(needed|update)', s):
        categories.append("fake_shipping_delivery")

    # Subscription renewal scams
    if re.search(r'subscription.*(renew|expir|end|cancel)|renewal.*notice|membership.*(expir|renew)|auto.*renew|billing.*renew|your.*plan.*(expire|end)|mcafee|norton|geek.*squad|antivirus.*(expir|renew)', s):
        categories.append("subscription_renewal")

    # Dating / sexual spam
    if re.search(r'wants?\s+to\s+meet|someone.*meet.*you|meet\s+(me|you|her)|hookup|dtf|casual\s+sex|adult\s+dating|sexy|horny|booty|nibble|milf|onlyfans|fansly|naughty|flirty|on\s+cam|webcam', s):
        categories.append("dating_sexual")
    if re.search(r'wants?\s+to\s+meet|someone.*meet.*you|meet\s+(me|you|her)|hookup|dtf|casual\s+sex|adult\s+dating|sexy|horny|booty|nibble|milf|onlyfans|fansly|naughty|flirty|on\s+cam|webcam', n):
        categories.append("dating_sexual")

    # Phishing / credential theft
    if re.search(r'confirm\s+your\s+(email|account)|verify\s+your.*identity|unusual\s+activity|suspended|locked|blocked|sign\s+in.*(attempt|detected)|login.*(attempt|from)|new\s+device|security.*alert|password.*(expir|reset)|reset\s+your\s+password|2fa|two.factor|authentication.*code|verify.*now|action\s+required|urgent\s+confirm', s):
        categories.append("phishing_credentials")

    # Business / invoice scam
    if re.search(r'invoice\s+(attached|from|for|notice)|payment.*(receipt|reminder|overdue)|wire\s+transfer|bank\s+transfer|direct\s+deposit|dear\s+(valued|sir|madam)|kindly|urgent.*response|respond\s+immediately|order\s+verification|verification\s+notice', s):
        categories.append("business_invoice_scam")

    # Weight loss / health scam
    if re.search(r'lose\s+.*weight|weight\s+loss|ozempic|wegovy|glp-1|keto.*pill|apple\s+cider\s+vinegar|miracle\s+diet|cbd.*(gumm|oil)|male\s+enhancement|testosterone|performance|nerve\s+fresh', s):
        categories.append("health_scam")

    # Lottery / prize scam
    if re.search(r'lottery|winner|prize|congratulations.*won|you.*won|jackpot|lucky|claim\s+your|inheritance|next\s+of\s+kin|unclaimed\s+fund', s):
        categories.append("lottery_prize")

    # Survey / gift card scam
    if re.search(r'survey\s+reward|complete.*survey|gift\s+card|redeem.*now|free.*gift|special\s+offer|exclusive.*offer|limited\s*time', s):
        categories.append("survey_giftcard")

    # Newsletter / bulk marketing (only if suspicious domain)
    if re.search(r'unsubscribe|newsletter|digest|promotional|marketing|sponsored|partner\s+offer|daily\s+update|weekly\s+update', s):
        suspicious = re.search(r'\.(ru|biz|top|pp\.ua|co\.nl|org\.uk|tk|ml|cf|xyz|click|link|me|today|club)$', d)
        if suspicious or re.search(r'[0-9]', d):
            categories.append("suspicious_newsletter")

    # Emoji-heavy subjects (general spam indicator)
    emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251\u2764\U0001F48B\U0001F4A7\U0001F351\U0001F353\U0001F364\U0001F382\U0001F3B6\U0001F4AF\U0001F495\U0001F496\U0001F497\U0001F498\U0001F499\U0001F49A\U0001F49B\U0001F49C\U0001F49D\U0001F525\U0001F336\U0001F344]', s))
    if emoji_count >= 3:
        categories.append("emoji_heavy")

    # Typosquat / suspicious domains
    if re.search(r'\.(ru|biz|top|pp\.ua|co\.nl|org\.uk|tk|ml|cf|xyz|click|link|me|today|club|vip|info)$', d):
        categories.append("suspicious_tld")

    # Disposable / temp email services
    disposable_patterns = [
        r'temp(mail|email)', r'guerrillamail', r'mailinator', r'10minutemail',
        r'yopmail', r'throwaway', r'getairmail', r'fakeinbox', r'mohmal',
        r'mailnesia', r'mintemail', r'sharklasers', r'spamgourmet',
        r'trashmail', r'mail-temp', r'email-temp', r'dispostable',
        r' burner', r'tempinbox'
    ]
    for pat in disposable_patterns:
        if re.search(pat, d):
            categories.append("disposable_email_domain")

    if not categories:
        categories.append("uncategorized")

    return categories


def analyze_folder(email_addr, password, folder_name, label, max_msgs=80):
    results = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=20)
        mail.login(email_addr, password)
    except Exception as e:
        print(f"  LOGIN FAILED for {email_addr}: {e}", flush=True)
        return results

    status, _ = mail.select(folder_name)
    if status != "OK":
        print(f"  SELECT FAILED for {folder_name}", flush=True)
        mail.logout()
        return results

    since_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
    _, data = mail.search(None, f"(SINCE {since_date})")
    all_ids = data[0].split()
    if not all_ids:
        print(f"  {label}: No messages in last 7 days.", flush=True)
        mail.close()
        mail.logout()
        return results

    uids = all_ids[-min(len(all_ids), max_msgs):]
    print(f"  {label}: Fetching {len(uids)} messages...", flush=True)

    for uid in uids:
        try:
            _, msg_data = mail.fetch(uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
            if not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            sender_raw = decode_field(msg.get("From", ""))
            subject_raw = decode_field(msg.get("Subject", ""))
            date_raw = decode_field(msg.get("Date", ""))

            domain = extract_domain(sender_raw)
            sender_name = extract_sender_name(sender_raw)
            categories = categorize(subject_raw, sender_raw, domain)

            results.append({
                "account": email_addr,
                "folder": label,
                "sender_raw": sender_raw,
                "sender_name": sender_name,
                "domain": domain,
                "subject": subject_raw,
                "date": date_raw,
                "categories": categories,
            })
        except Exception as e:
            print(f"    Fetch error: {e}", flush=True)
            continue

    mail.close()
    mail.logout()
    return results


def main():
    all_emails = []
    for email_addr in ACCOUNTS.keys():
        password = get_password(email_addr)
        if not password:
            print(f"SKIP: no password for {email_addr}")
            continue
        print(f"\n{'='*60}")
        print(f"Account: {email_addr}")
        print(f"{'='*60}")

        inbox_results = analyze_folder(email_addr, password, "INBOX", "INBOX", 80)
        time.sleep(0.5)
        spam_results = analyze_folder(email_addr, password, "[Gmail]/Spam", "Spam", 80)

        all_emails.extend(inbox_results)
        all_emails.extend(spam_results)

        print(f"  -> Inbox: {len(inbox_results)} | Spam: {len(spam_results)}")
        time.sleep(1)

    # Write raw data
    with open("spam_analysis_raw_2026-07-24.json", "w", encoding="utf-8") as f:
        json.dump(all_emails, f, indent=2, ensure_ascii=False)
    print(f"\n{'='*60}")
    print(f"Raw data written to spam_analysis_raw_2026-07-24.json")
    print(f"Total emails analyzed: {len(all_emails)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
