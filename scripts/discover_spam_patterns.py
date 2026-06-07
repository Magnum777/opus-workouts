#!/usr/bin/env python3
"""
discover_spam_patterns.py

Scans Gmail Spam folders across all accounts, extracts recurring patterns
(domains, keywords, phrases) that are NOT already in spam_sweep_v2.py,
auto-updates the sweep script with new patterns, and produces a report.

Run this daily to stay ahead of evolving spam.
"""
import imaplib, email, re, json, os, sys, time, collections
from email.header import decode_header
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

START_TIME = time.time()
MAX_RUNTIME = 300  # 5 min max

def should_exit():
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


def is_suspicious_domain(domain, sender_name, subject):
    """Heuristic: is this domain actually spam, or just a newsletter?"""
    if domain in LEGIT:
        return False
    # Job sites that aren't spam but end up in spam folder
    if any(d in domain for d in ["theladders", "indeed", "monster", "ziprecruiter", "glassdoor"]):
        return False
    # Must have some spam signal
    combined = (sender_name + " " + subject).lower()
    spam_signals = ["unsubscribe", "newsletter", "no-reply", "noreply",
                    "offer", "deal", "promo", "sale", "discount",
                    "free", "win", "prize", "urgent", "limited",
                    "dating", "hookup", "flirt", "sexy", "milf",
                    "booty", "horny", "porn", "xxx", "nude",
                    "verify", "confirm", "suspended", "locked",
                    "invoice", "payment", "refund", "crypto",
                    "bitcoin", "invest", "loan", "credit",
                    "weight loss", "glp-1", "ozempic", "wegovy",
                    "pill", "supplement", "medication"]
    return any(s in combined for s in spam_signals)


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


def decode_str(s):
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
    m = re.search(r'@([^\u003e\s]+)', sender)
    return m.group(1).lower() if m else ""


def extract_sender_name(sender):
    m = re.match(r'"?([^"\u003c]+)"?\s*\u003c', sender)
    return m.group(1).strip() if m else sender


def clean_subject(subj):
    return re.sub(r'[^\w\s]', ' ', subj.lower()).strip()


def extract_phrases(subject, min_len=4, max_len=12):
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


def load_existing_patterns():
    existing = {"domains": set(), "keywords": set(), "phrases": set(), "regexes": set()}
    try:
        with open(SWEEP_SCRIPT, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
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


def discover_spam(mail, existing_patterns):
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
    for uid in uids:
        if should_exit():
            break
        try:
            _, raw = mail.uid("fetch", uid, "(RFC822.HEADER)")
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

        except Exception:
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


def filter_new_patterns(data, existing):
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


def auto_update_sweep(existing, all_new):
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
            print("  📦 Committed changes to git.")
        except Exception:
            pass

    return changes


def print_report_after_update(changes):
    total = sum(len(v) for v in changes.values())
    if total == 0:
        print("  No changes applied (all patterns were already known or rejected).")
        return

    print(f"\n  🔄 AUTO-UPDATED gmail_spam_sweep_v2.py ({total} patterns added):")
    if changes["domains"]:
        print(f"    +{len(changes['domains'])} domains")
        for d in changes["domains"][:5]:
            print(f'      "{d}"')
        if len(changes["domains"]) > 5:
            print(f"      ... and {len(changes['domains'])-5} more")
    if changes["phrases"]:
        print(f"    +{len(changes['phrases'])} phrases (DATING)")
        for p in changes["phrases"][:5]:
            print(f'      "{p}"')
        if len(changes["phrases"]) > 5:
            print(f"      ... and {len(changes['phrases'])-5} more")
    if changes["words"]:
        print(f"    +{len(changes['words'])} keywords (RE_SEXUAL)")
    if changes["senders"]:
        print(f"    +{len(changes['senders'])} sender patterns (RE_FAKE_SENDER)")
    print(f"\n  Saved record to {OUTPUT_JSON}")


def print_report(account, new_patterns, data):
    print(f"\n{'='*50}")
    print(f"NEW PATTERNS: {account}")
    print(f"{'='*50}")
    print(f"Processed {data['processed']} spam messages (last {DAYS_BACK} days)")

    has_any = any(new_patterns.get(cat) for cat in ["domains", "phrases", "words", "senders"])
    if not has_any:
        print("  No new recurring patterns found. Spam signatures are up to date.")
        return

    if new_patterns.get("domains"):
        print(f"\n  📧 NEW DOMAINS (add to SPAM_DOMAINS):")
        for domain, count in sorted(new_patterns["domains"].items(), key=lambda x: -x[1]):
            print(f'    "{domain}",  # ({count}x)')

    if new_patterns.get("phrases"):
        print(f"\n  💬 NEW PHRASES (add to DATING or inline regex):")
        for phrase, count in sorted(new_patterns["phrases"].items(), key=lambda x: -x[1]):
            print(f'    "{phrase}",  # ({count}x)')

    if new_patterns.get("words"):
        print(f"\n  🔤 NEW KEYWORDS (add to CORE_BAD or RE_SEXUAL):")
        for word, count in sorted(new_patterns["words"].items(), key=lambda x: -x[1]):
            print(f'    "{word}",  # ({count}x)')

    if new_patterns.get("senders"):
        print(f"\n  👤 NEW SENDER NAMES (add to RE_FAKE_SENDER):")
        for sender, count in sorted(new_patterns["senders"].items(), key=lambda x: -x[1]):
            print(f'    {sender}  # ({count}x)')


def main():
    print(f"🔍 Spam Pattern Discovery — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Scanning last {DAYS_BACK} days of Gmail Spam folders...")

    existing = load_existing_patterns()
    print(f"Loaded {len(existing['domains'])} known domains, "
          f"{len(existing['keywords'])} keywords, "
          f"{len(existing['phrases'])} phrases.")

    all_new = {"domains": {}, "phrases": {}, "words": {}, "senders": {}}
    total_processed = 0

    for email_addr, pass_var in ACCOUNTS.items():
        if should_exit():
            print("  ⏱ Max runtime reached, stopping.")
            break

        password = get_password(email_addr)
        if not password:
            print(f"  ⚠️ No password for {email_addr}, skipping.")
            continue

        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            mail.login(email_addr, password)
            mail.select("[Gmail]/Spam", readonly=True)
        except Exception as e:
            print(f"  ❌ {email_addr}: login failed ({e})")
            continue

        data = discover_spam(mail, existing)
        mail.logout()
        total_processed += data["processed"]

        new_patterns = filter_new_patterns(data, existing)
        print_report(email_addr, new_patterns, data)

        for cat in all_new:
            for item, count in new_patterns.get(cat, {}).items():
                all_new[cat][item] = all_new[cat].get(item, 0) + count

    print(f"\n{'='*50}")
    print(f"SUMMARY: Scanned {total_processed} spam messages across all accounts.")

    has_any = any(all_new.get(cat) for cat in ["domains", "phrases", "words", "senders"])
    if has_any:
        print("✅ New patterns found!")
        print("Auto-applying to gmail_spam_sweep_v2.py...")
        changes = auto_update_sweep(existing, all_new)
        print_report_after_update(changes)
    else:
        print("✅ No new patterns. Spam filters are current.")


if __name__ == "__main__":
    main()
