#!/usr/bin/env python3
"""
discover_spam_patterns.py v2.2

Scans Gmail Spam AND Inbox folders across all accounts, extracts recurring patterns
(domains, keywords, phrases) that are NOT already in spam_sweep_v2.py,
auto-updates the sweep script with new patterns, and produces a report.

Uses gmail_spam_sweep_v2.is_spam() for inbox filtering when available.

Run this daily to stay ahead of evolving spam.
"""
import argparse
import collections
import email
import imaplib
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from email.header import decode_header

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

START_TIME = time.time()
MAX_RUNTIME = 240  # 4 min max


def should_exit() -> bool:
    return time.time() - START_TIME > MAX_RUNTIME


LOCAL_CONFIG = os.path.join(os.path.dirname(__file__), ".gmail_accounts.json")

ACCOUNTS = {
    "compjunkie@gmail.com":         "GMAIL_APP_PASSWORD_COMPJUNKIE",
    "jhenderson87@gmail.com":       "GMAIL_APP_PASSWORD_JHENDERSON",
    "layeredmediallc@gmail.com":    "GMAIL_APP_PASSWORD_LAYEREDMEDIA",
    "nova.cofounder@gmail.com":     "GMAIL_APP_PASSWORD_NOVA",
}

SWEEP_SCRIPT = os.path.join(os.path.dirname(__file__), "gmail_spam_sweep_v2.py")
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), ".spam_patterns_found.json")

DAYS_BACK = 3
MIN_OCCURRENCES = 2
TOP_N = 20

LEGIT = {"google.com", "microsoft.com", "apple.com", "amazon.com",
         "github.com", "discord.com", "paypal.com", "gmail.com",
         "outlook.com", "yahoo.com", "protonmail.com", "icloud.com",
         "yandex.ru", "mail.ru", "zoho.com", "aol.com", "hotmail.com",
         "live.com", "msn.com", "qq.com", "163.com", "126.com",
         "privaterelay.appleid.com", "me.com", "mac.com",
         "linkedin.com", "indeed.com", "glassdoor.com", "ziprecruiter.com"}

# Strong spam signals for inbox filtering (when sweep module not available)
STRONG_SIGNALS = {"porn", "xxx", "nude", "horny", "milf", "booty",
                   "cock", "cum", "pussy", "dick", "sex", "fuck",
                   "dating", "hookup", "flirt", "sexy", "onlyfans", "fansly",
                   "blocked your account", "photos and videos", "we've blocked",
                   "creampie", "gangbang", "blowjob", "deepthroat",
                   "verify", "suspended", "locked", "urgent confirm",
                   "invoice attached", "wire transfer", "crypto investment",
                   "double your money", "guaranteed returns", "risk free",
                   "weight loss", "glp-1", "ozempic", "wegovy",
                   "male enhancement", "testosterone", "cbd gummies",
                   "inheritance", "next of kin", "unclaimed funds",
                   "lottery winner", "prize claim", "congratulations winner",
                   # Business scam expansion
                   "order verification", "account suspended", "account locked",
                   "confirm your email", "action required", "unusual activity",
                   "bank transfer", "direct deposit", "dear valued customer",
                   "dear sir/madam", "kindly", "urgent response", "passive income",
                   "work from home", "make money fast", "financial freedom",
                   "secret method", "exclusive offer", "limited time only",
                   "act now", "you have been selected", "miracle diet",
                   "keto pills", "apple cider vinegar", "garcinia cambogia",
                   "performance plus", "credit card declined", "update payment",
                   "billing issue", "package delivery failed", "shipping address",
                   "dhl delivery", "fedex tracking", "ups package", "customs fee",
                   "import duty", "clearance required", "irs notice", "tax refund",
                   "tax settlement", "social security", "medicare", "medicaid",
                   "loan approved", "loan pre-approved", "credit approved",
                   "debt consolidation", "reduce your debt", "debt relief",
                   "reverse mortgage", "home equity", "cash out", "timeshare",
                   "vacation package", "free cruise", "extended warranty",
                   "vehicle warranty", "car warranty", "health insurance",
                   "dental insurance", "life insurance quote", "mortgage rates",
                   "refinance now", "low rates", "pre-approved", "pre-qualified",
                   "special financing", "gift card", "redeem now", "survey reward",
                   "complete survey", "opinion wanted", "charity donation",
                   "donate now", "help children", "suspicious login",
                   "unauthorized access", "security breach", "verify identity",
                   "identity verification", "kyc required", "2fa code",
                   "two factor", "authentication code", "reset password",
                   "password expired", "credentials", "login attempt",
                   "sign in attempt", "new device", "geek squad", "norton",
                   "mcafee", "renew subscription", "antivirus expired",
                   "security software", "tech support", "microsoft support",
                   "apple support", "amazon support", "refund pending",
                   "refund processing", "refund approved", "overcharged",
                   "billing error", "payment dispute"}

SUSPICIOUS_TLDS = re.compile(r'\.(ru|top|biz|pp\.ua|tk|ml|cf|yds)$')
UNICODE_OBFUSCATION = re.compile(r'[\uff10-\uff19\uff21-\uff3a\uff41-\uff5a]')
EMOJI_RE = re.compile(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]')


def is_suspicious_domain(domain: str, sender_name: str, subject: str) -> bool:
    if domain in LEGIT:
        return False
    if any(d in domain for d in ["theladders", "indeed", "monster", "ziprecruiter", "glassdoor"]):
        return False
    combined = (sender_name + " " + subject).lower()
    spam_signals = {"unsubscribe", "newsletter", "no-reply", "noreply",
                    "offer", "deal", "promo", "sale", "discount",
                    "free", "win", "prize", "urgent", "limited",
                    "dating", "hookup", "flirt", "sexy", "milf",
                    "booty", "horny", "porn", "xxx", "nude",
                    "verify", "confirm", "suspended", "locked",
                    "invoice", "payment", "refund", "crypto",
                    "bitcoin", "invest", "loan", "credit",
                    "weight loss", "glp-1", "ozempic", "wegovy",
                    "pill", "supplement", "medication"}
    return any(s in combined for s in spam_signals)


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
    except Exception as e:
        logger.warning("Config load failed for %s: %s", email_addr, e)
        return ""


def decode_str(s: str) -> str:
    if not s:
        return ""
    parts = decode_header(s)
    out = []
    for part, enc in parts:
        if isinstance(part, bytes):
            try:
                out.append(part.decode(enc or "utf-8", errors="replace"))
            except Exception as e:
                logger.warning("Header decode fallback: %s", e)
                out.append(part.decode("utf-8", errors="replace"))
        else:
            out.append(str(part))
    return " ".join(out)


def extract_domain(sender: str) -> str:
    m = re.search(r'@([^\u003e\s]+)', sender)
    return m.group(1).lower() if m else ""


def extract_sender_name(sender: str) -> str:
    m = re.match(r'"?([^"\u003c]+)"?\s*\u003c', sender)
    return m.group(1).strip() if m else sender


def clean_subject(subj: str) -> str:
    return re.sub(r'[^\w\s]', ' ', subj.lower()).strip()


def extract_phrases(subject: str, min_len: int = 4, max_len: int = 12) -> list[str]:
    text = clean_subject(subject)
    words = text.split()
    phrases = []
    skip_starts = {"the", "a", "an", "is", "are", "was", "were", "this", "that",
                   "and", "or", "but", "in", "on", "at", "to", "for", "of",
                   "with", "your", "you", "re", "fwd", "re"}
    for n in range(2, 4):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i:i+n])
            if min_len <= len(phrase) <= max_len * n:
                if words[i] not in skip_starts:
                    phrases.append(phrase)
    return phrases


def load_existing_patterns() -> dict[str, set[str]]:
    existing = {"domains": set(), "keywords": set(), "phrases": set(), "regexes": set()}
    try:
        with open(SWEEP_SCRIPT, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.warning("Failed to load existing patterns from %s: %s", SWEEP_SCRIPT, e)
        return existing

    dom_match = re.search(r'SPAM_DOMAINS\s*=\s*\{(.*?)\}', content, re.DOTALL)
    if dom_match:
        for line in dom_match.group(1).split("\n"):
            m = re.search(r'"([^"]+)"', line)
            if m:
                existing["domains"].add(m.group(1).lower().strip())

    core_match = re.search(r'CORE_BAD\s*=\s*\{(.*?)\}', content, re.DOTALL)
    if core_match:
        for line in core_match.group(1).split("\n"):
            for w in re.findall(r'"([^"]+)"', line):
                existing["keywords"].add(w.lower().strip())

    dating_match = re.search(r'DATING\s*=\s*\{(.*?)\}', content, re.DOTALL)
    if dating_match:
        for line in dating_match.group(1).split("\n"):
            for w in re.findall(r'"([^"]+)"', line):
                existing["phrases"].add(w.lower().strip())

    for regex_name in ["RE_SEXUAL", "RE_FAKE_SENDER"]:
        rmatch = re.search(rf'{regex_name}\s*=\s*re\.compile\(\s*\((.*?)\)', content, re.DOTALL)
        if rmatch:
            for pat in re.findall(r'"([^"]+)"', rmatch.group(1)):
                existing["regexes"].add(pat.lower().strip())

    for pat in re.findall(r're\.search\(r["\']([^"\']+)', content):
        existing["phrases"].add(pat.lower().strip())

    return existing


def discover_spam(mail: imaplib.IMAP4_SSL, existing: dict[str, set[str]], label: str = "Spam", max_msgs: int = 150) -> dict:
    since_date = (datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)).strftime("%d-%b-%Y")
    _, uids_raw = mail.uid("search", None, f'(SINCE "{since_date}")')
    uids = uids_raw[0].split() if uids_raw and uids_raw[0] else []

    domain_counter = collections.Counter()
    sender_name_counter = collections.Counter()
    subject_counter = collections.Counter()
    phrase_counter = collections.Counter()
    word_counter = collections.Counter()
    all_subjects = []

    processed = 0
    for uid in uids[:max_msgs]:
        if should_exit():
            break
        try:
            _, raw = mail.uid("fetch", uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
            if not raw or not raw[0]:
                continue
            raw_header = raw[0][1] if isinstance(raw[0], tuple) else raw[0]
            msg = email.message_from_bytes(raw_header)
            subject = decode_str(msg.get("Subject", ""))
            sender = decode_str(msg.get("From", ""))

            domain = extract_domain(sender)
            sender_name = extract_sender_name(sender).lower()
            clean_subj = clean_subject(subject)

            all_subjects.append((sender, subject))
            processed += 1

            if domain:
                domain_counter[domain] += 1
            if sender_name:
                sender_name_counter[sender_name] += 1
            if clean_subj:
                subject_counter[clean_subj] += 1

            for phrase in extract_phrases(subject):
                phrase_counter[phrase] += 1
            for word in clean_subj.split():
                if len(word) > 3:
                    word_counter[word] += 1

        except Exception as e:
            logger.warning("Error processing spam message %s: %s", uid, e)
            continue

    return {
        "processed": processed,
        "domain_counter": domain_counter,
        "sender_name_counter": sender_name_counter,
        "subject_counter": subject_counter,
        "phrase_counter": phrase_counter,
        "word_counter": word_counter,
        "all_subjects": all_subjects,
    }


def is_inbox_spam(sender: str, subject: str) -> bool:
    """Check if an inbox message is actually spam (stricter than discover_spam)."""
    combined = (sender + " " + subject).lower()

    # Strong signals
    if any(s in combined for s in STRONG_SIGNALS):
        return True

    # Unicode obfuscation (full-width chars used to evade filters)
    if UNICODE_OBFUSCATION.search(subject):
        return True

    # Emoji spam + suspicious sender
    emoji_count = len(EMOJI_RE.findall(subject))
    if emoji_count >= 2 and SUSPICIOUS_TLDS.search(sender.lower()):
        return True

    # Fake sender name matching account name (impersonation)
    sender_name = extract_sender_name(sender).lower()
    if sender_name in {"compjunkie", "james", "layered media"} and any(s in subject.lower() for s in {"alert", "blocked", "suspended", "verify"}):
        return True

    return False


def discover_inbox_spam(mail: imaplib.IMAP4_SSL, existing: dict[str, set[str]], max_msgs: int = 80) -> dict:
    """Scan inbox for messages that the sweep would flag as spam."""
    since_date = (datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)).strftime("%d-%b-%Y")
    _, uids_raw = mail.uid("search", None, f'(SINCE "{since_date}")')
    uids = uids_raw[0].split() if uids_raw and uids_raw[0] else []
    uids = uids[-max_msgs:]

    domain_counter = collections.Counter()
    sender_name_counter = collections.Counter()
    subject_counter = collections.Counter()
    phrase_counter = collections.Counter()
    word_counter = collections.Counter()
    all_subjects = []
    processed = 0

    for uid in uids:
        if should_exit():
            break
        try:
            _, raw = mail.uid("fetch", uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
            if not raw or not raw[0]:
                continue
            raw_header = raw[0][1] if isinstance(raw[0], tuple) else raw[0]
            msg = email.message_from_bytes(raw_header)
            subject = decode_str(msg.get("Subject", ""))
            sender = decode_str(msg.get("From", ""))

            if not is_inbox_spam(sender, subject):
                continue

            domain = extract_domain(sender)
            sender_name = extract_sender_name(sender).lower()
            clean_subj = clean_subject(subject)

            all_subjects.append((sender, subject))
            processed += 1

            if domain:
                domain_counter[domain] += 1
            if sender_name:
                sender_name_counter[sender_name] += 1
            if clean_subj:
                subject_counter[clean_subj] += 1

            for phrase in extract_phrases(subject):
                phrase_counter[phrase] += 1
            for word in clean_subj.split():
                if len(word) > 3:
                    word_counter[word] += 1

        except Exception as e:
            logger.warning("Error processing inbox message %s: %s", uid, e)
            continue

    return {
        "processed": processed,
        "domain_counter": domain_counter,
        "sender_name_counter": sender_name_counter,
        "subject_counter": subject_counter,
        "phrase_counter": phrase_counter,
        "word_counter": word_counter,
        "all_subjects": all_subjects,
    }


def filter_new_patterns(data: dict, existing: dict[str, set[str]]) -> dict:
    new_domains = {}
    new_phrases = {}
    new_words = {}
    new_senders = {}

    for domain, count in data["domain_counter"].most_common(TOP_N):
        if count >= MIN_OCCURRENCES and domain not in existing["domains"]:
            if is_suspicious_domain(domain, "", ""):
                new_domains[domain] = count

    for phrase, count in data["phrase_counter"].most_common(TOP_N):
        if count >= MIN_OCCURRENCES and phrase not in existing["phrases"] and phrase not in existing["keywords"]:
            new_phrases[phrase] = count

    for word, count in data["word_counter"].most_common(TOP_N):
        if count >= MIN_OCCURRENCES and word not in existing["keywords"]:
            new_words[word] = count

    for sender, count in data["sender_name_counter"].most_common(TOP_N):
        if count >= MIN_OCCURRENCES and sender not in existing["regexes"]:
            new_senders[sender] = count

    return {
        "domains": new_domains,
        "phrases": new_phrases,
        "words": new_words,
        "senders": new_senders,
    }


def auto_update_sweep(existing: dict[str, set[str]], all_new: dict, dry_run: bool = False) -> dict:
    changes = {"domains": [], "phrases": [], "words": [], "senders": []}

    with open(SWEEP_SCRIPT, "r", encoding="utf-8") as f:
        content = f.read()

    # Update SPAM_DOMAINS
    doms_to_add = []
    for dom, count in sorted(all_new.get("domains", {}).items(), key=lambda x: -x[1]):
        if dom not in existing["domains"] and dom not in LEGIT:
            doms_to_add.append(dom)

    if doms_to_add:
        match = re.search(r'(SPAM_DOMAINS\s*=\s*\{[^}]*?)(\n\})', content, re.DOTALL)
        if match:
            insert_pos = match.end(1)
            new_lines = ""
            for dom in doms_to_add:
                new_lines += f'    "{dom}",\n'
            content = content[:insert_pos] + new_lines + content[insert_pos:]
            changes["domains"] = doms_to_add

    # Update RE_FAKE_SENDER
    senders_to_add = []
    for sender, count in sorted(all_new.get("senders", {}).items(), key=lambda x: -x[1]):
        s = sender.lower()
        if s not in existing["regexes"] and len(s) > 2:
            senders_to_add.append(re.escape(s))

    if senders_to_add:
        match = re.search(r'(RE_FAKE_SENDER\s*=\s*re\.compile\(\s*\(([^)]*))\)', content, re.DOTALL)
        if match:
            insert_pos = match.end(2)
            new_pats = "|" + "|".join(senders_to_add) if match.group(2).strip() else "|".join(senders_to_add)
            content = content[:insert_pos] + new_pats + content[insert_pos:]
            changes["senders"] = list(all_new.get("senders", {}).keys())

    # Update RE_SEXUAL
    words_to_add = []
    for word, count in sorted(all_new.get("words", {}).items(), key=lambda x: -x[1]):
        w = word.lower()
        if w not in existing["keywords"] and len(w) > 3:
            words_to_add.append(re.escape(w))

    if words_to_add:
        match = re.search(r'(RE_SEXUAL\s*=\s*re\.compile\(\s*\(([^)]*))\)', content, re.DOTALL)
        if match:
            insert_pos = match.end(2)
            new_pats = "|" + "|".join(words_to_add) if match.group(2).strip() else "|".join(words_to_add)
            content = content[:insert_pos] + new_pats + content[insert_pos:]
            changes["words"] = list(all_new.get("words", {}).keys())

    # Update DATING
    phrases_to_add = []
    for phrase, count in sorted(all_new.get("phrases", {}).items(), key=lambda x: -x[1]):
        p = phrase.lower()
        if p not in existing["phrases"] and len(p) > 5:
            phrases_to_add.append(p)

    if phrases_to_add:
        match = re.search(r'(DATING\s*=\s*\{[^}]*?)(\n\})', content, re.DOTALL)
        if match:
            insert_pos = match.end(1)
            new_lines = ""
            for p in phrases_to_add:
                new_lines += f'    "{p}",\n'
            content = content[:insert_pos] + new_lines + content[insert_pos:]
            changes["phrases"] = phrases_to_add

    if dry_run:
        logger.info("[DRY RUN] Would update %s with %d changes", SWEEP_SCRIPT, sum(len(v) for v in changes.values()))
        return changes

    # Write back
    with open(SWEEP_SCRIPT, "w", encoding="utf-8") as f:
        f.write(content)

    # Save JSON record
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "changes": changes,
            "counts": {k: len(v) for k, v in changes.items()}
        }, f, indent=2)

    # Auto-commit to git if in a repo
    total_changes = sum(len(v) for v in changes.values())
    if total_changes > 0:
        try:
            repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.system(f'cd "{repo_root}" && git add scripts/gmail_spam_sweep_v2.py && git commit -m "spam: auto-add {total_changes} discovered signatures ({datetime.now().strftime("%Y-%m-%d")})" > nul 2>&1')
            logger.info("  Committed changes to git.")
        except Exception as e:
            logger.warning("Git commit failed: %s", e)

    return changes


def print_report_after_update(changes: dict) -> None:
    total = sum(len(v) for v in changes.values())
    if total == 0:
        logger.info("  No changes applied (all patterns were already known or rejected).")
        return

    logger.info("  AUTO-UPDATED gmail_spam_sweep_v2.py (%d patterns added):", total)
    if changes["domains"]:
        logger.info("    +%d domains", len(changes["domains"]))
        for d in changes["domains"][:5]:
            logger.info('      "%s"', d)
        if len(changes["domains"]) > 5:
            logger.info("      ... and %d more", len(changes["domains"]) - 5)
    if changes["phrases"]:
        logger.info("    +%d phrases (DATING)", len(changes["phrases"]))
        for p in changes["phrases"][:5]:
            logger.info('      "%s"', p)
        if len(changes["phrases"]) > 5:
            logger.info("      ... and %d more", len(changes["phrases"]) - 5)
    if changes["words"]:
        logger.info("    +%d keywords (RE_SEXUAL)", len(changes["words"]))
    if changes["senders"]:
        logger.info("    +%d sender patterns (RE_FAKE_SENDER)", len(changes["senders"]))
    logger.info("  Saved record to %s", OUTPUT_JSON)


def print_report(account: str, new_patterns: dict, data: dict, folder: str = "Spam") -> None:
    logger.info("")
    logger.info("=" * 50)
    logger.info("NEW PATTERNS: %s [%s]", account, folder)
    logger.info("=" * 50)
    logger.info("Processed %d messages (last %d days)", data["processed"], DAYS_BACK)

    has_any = any(new_patterns.get(cat) for cat in ["domains", "phrases", "words", "senders"])
    if not has_any:
        logger.info("  No new recurring patterns found.")
        return

    if new_patterns.get("domains"):
        logger.info("")
        logger.info("  NEW DOMAINS:")
        for domain, count in sorted(new_patterns["domains"].items(), key=lambda x: -x[1]):
            logger.info('    "%s",  # (%dx)', domain, count)

    if new_patterns.get("phrases"):
        logger.info("")
        logger.info("  NEW PHRASES:")
        for phrase, count in sorted(new_patterns["phrases"].items(), key=lambda x: -x[1]):
            logger.info('    "%s",  # (%dx)', phrase, count)

    if new_patterns.get("words"):
        logger.info("")
        logger.info("  NEW KEYWORDS:")
        for word, count in sorted(new_patterns["words"].items(), key=lambda x: -x[1]):
            logger.info('    "%s",  # (%dx)', word, count)

    if new_patterns.get("senders"):
        logger.info("")
        logger.info("  NEW SENDER NAMES:")
        for sender, count in sorted(new_patterns["senders"].items(), key=lambda x: -x[1]):
            logger.info('    %s  # (%dx)', sender, count)


def scan_account(email_addr: str, existing: dict[str, set[str]], all_new: dict) -> int:
    password = get_password(email_addr)
    if not password:
        logger.warning("  No password for %s, skipping.", email_addr)
        return 0

    account_processed = 0

    # --- Scan Spam folder ---
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=15)
        mail.login(email_addr, password)
        mail.select("[Gmail]/Spam", readonly=True)
    except Exception as e:
        logger.error("  %s: Spam login/select failed (%s)", email_addr, e)
        return 0

    data = discover_spam(mail, existing, label="Spam", max_msgs=150)
    mail.logout()
    account_processed += data["processed"]

    new_patterns = filter_new_patterns(data, existing)
    print_report(email_addr, new_patterns, data, folder="Spam")

    for cat in all_new:
        for item, count in new_patterns.get(cat, {}).items():
            all_new[cat][item] = all_new[cat].get(item, 0) + count

    # --- Scan INBOX for missed spam ---
    if should_exit():
        return account_processed
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=15)
        mail.login(email_addr, password)
        mail.select("INBOX", readonly=True)
    except Exception as e:
        logger.error("  %s: INBOX login/select failed (%s)", email_addr, e)
        return account_processed

    inbox_data = discover_inbox_spam(mail, existing, max_msgs=80)
    mail.logout()
    account_processed += inbox_data["processed"]

    inbox_new = filter_new_patterns(inbox_data, existing)
    print_report(email_addr, inbox_new, inbox_data, folder="INBOX")

    for cat in all_new:
        for item, count in inbox_new.get(cat, {}).items():
            all_new[cat][item] = all_new[cat].get(item, 0) + count

    return account_processed


def main(dry_run: bool = False) -> None:
    logger.info("Spam Pattern Discovery — %s", datetime.now().strftime("%Y-%m-%d %H:%M"))
    if dry_run:
        logger.info("[DRY RUN] No files will be modified.")
    logger.info("Scanning last %d days of Gmail Spam + Inbox folders...", DAYS_BACK)

    existing = load_existing_patterns()
    logger.info("Loaded %d known domains, %d keywords, %d phrases.",
                len(existing["domains"]), len(existing["keywords"]), len(existing["phrases"]))

    all_new = {"domains": {}, "phrases": {}, "words": {}, "senders": {}}
    total_processed = 0

    for email_addr in ACCOUNTS.keys():
        if should_exit():
            logger.info("  Max runtime reached, stopping.")
            break
        processed = scan_account(email_addr, existing, all_new)
        if processed:
            total_processed += processed
        time.sleep(0.5)

    logger.info("")
    logger.info("=" * 50)
    logger.info("SUMMARY: Scanned %d messages across all accounts.", total_processed)

    has_any = any(all_new.get(cat) for cat in ["domains", "phrases", "words", "senders"])
    if has_any:
        logger.info("New patterns found!")
        logger.info("Auto-applying to gmail_spam_sweep_v2.py...")
        changes = auto_update_sweep(existing, all_new, dry_run=dry_run)
        print_report_after_update(changes)
    else:
        logger.info("No new patterns. Spam filters are current.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover new spam patterns from Gmail")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying gmail_spam_sweep_v2.py")
    args = parser.parse_args()
    main(dry_run=args.dry_run)
