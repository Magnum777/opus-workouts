#!/usr/bin/env python3
"""Deep-dive spam sweep — 30 days, 500 msgs per account, checks Spam folders for pattern discovery."""
import imaplib, email, json, re, sys, os, time
from email.header import decode_header
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

START_TIME = time.time()
MAX_RUNTIME = 300

def should_exit():
    return time.time() - START_TIME > MAX_RUNTIME

LOCAL_CONFIG = os.path.join(os.path.dirname(__file__), ".gmail_accounts.json")

ACCOUNTS = {
    "compjunkie@gmail.com":         "GMAIL_APP_PASSWORD_COMPJUNKIE",
    "jhenderson87@gmail.com":       "GMAIL_APP_PASSWORD_JHENDERSON",
    "layeredmediallc@gmail.com":    "GMAIL_APP_PASSWORD_LAYEREDMEDIA",
    "nova.cofounder@gmail.com":     "GMAIL_APP_PASSWORD_NOVA",
}

# BROADER patterns from Opus's complaint list
NEW_PATTERNS = {
    "hot tonight", "are you single", "wants to chat", "send pics",
    "send me pics", "send nudes", "trade pics", "exchange photos",
    "meet up", "meetup", "meet tonight", "hang out", "hangout",
    "get together", "coffee sometime", "drinks sometime",
    "just moved here", "new in town", "looking for friends",
    "lonely and", "so lonely", "feel alone", "need company",
    "need a man", "need a guy", "need someone", "waiting for you",
    "waiting 4 u", "thinking of you", "thinking about you",
    "dreamed about you", "cant stop thinking", "cant get you out",
    "stuck in my head", "on my mind", "youre on my mind",
    "saw your pic", "saw ur pic", "saw your profile", "cute pic",
    "you look good", "you look cute", "handsome man", "sexy man",
    " attractive ", " gorgeous ", " beautiful ", " stunning ",
    "love your smile", "love your eyes", "nice body", "great body",
    "work out", "gym buddy", "workout partner",
    "snap me", "snapchat", "snap chat", "add me on snap",
    "kik me", "kik:", "telegram me", "whatsapp me",
    "text me", "txt me", "call me", "hit me up", "hmu",
    "dm me", "message me", "reply back", "respond asap",
    "dont be shy", "dont be scared", "u wont regret",
    "no strings", "no strings attached", "just fun", "just casual",
    "nothing serious", "not looking for serious", "keep it casual",
    "down for anything", "down 4 anything", "open minded", "open-minded",
    "try new things", "experiment", "adventurous",
    "attached female", "married but", "discreet", "secret",
    "no one will know", "our little secret", "between us",
    "age is just", "age doesnt matter", "mature woman",
    "older woman", "cougar", "milf", "dilf", "sugar",
    "sugar baby", "sugar daddy", "sugar momma",
    "allowance", "spoiled", "spoiling", "gifts", "shopping",
    " venmo ", " cashapp ", " cash app ", "paypal me", "zelle me",
    "send money", "send $", "need $", "broke and",
    "struggling", "help me out", "lend me", "borrow",
    "investment opportunity", "crypto opportunity", "forex signals",
    "binary options", "trading group", "pump group",
    "make money fast", "make money quick", "easy money", "fast cash",
    "work from home", "side hustle", "passive income", "residual income",
    "get rich", "financial freedom", "laptop lifestyle",
    "crypto investment", "bitcoin investment", "btc investment",
    "double your", "triple your", "10x your", "guaranteed return",
    "no risk", "risk free", "risk-free", "100% safe",
    "act fast", "spots filling", "limited spots", "closing soon",
    "last chance", "final call", "urgent", "time sensitive",
    "expires tonight", "expires today", "24 hours only",
    "winner selected", "youre a winner", "selected as winner",
    "claim prize", "claim reward", "claim bonus", "claim now",
    "unclaimed", "unclaimed reward", "unclaimed prize",
    "bonus expires", "reward expires", "points expire",
    "verify identity", "verify account", "confirm identity",
    "suspicious activity", "account locked", "account suspended",
    "restore access", "reinstate", "appeal required",
    "tax refund", "irs refund", "irs payment", "irs notice",
    "social security", "medicare", "medicaid",
    "debt relief", "debt consolidation", "credit repair",
    "student loan forgiveness", "loan forgiveness",
    "pre-approved", "preapproved", "you qualify", "youre approved",
    "credit line", "line of credit", "cash advance",
    "inheritance", "next of kin", "deceased relative",
    "unclaimed funds", "unclaimed property", "escheat",
    "package delayed", "package on hold", "shipping issue",
    "delivery failed", "delivery exception", "undeliverable",
    "customs fee", "import duty", "brokerage fee",
    "confirm delivery", "confirm shipment", "track package",
    "amazon order", "amazon refund", "amazon reward",
    "netflix subscription", "spotify subscription",
    "paypal transaction", "paypal dispute", "chargeback",
    "subscription renewal", "auto-renewal", "cancel now",
    "free trial ending", "trial ending", "renew today",
    "membership expiring", "membership renewal",
}

RE_SEXUAL = re.compile(
    r"hottie|booty|nibble|bedroom|scoop|stretched|oral|fixation|"
    r"can we make love|naked|nude|horny|porn|xxx|sexy|dtf|hookup|"
    r"casual sex|adult dating|hot affair|sexy singles|play with me|"
    r"available tonight|bored and lonely|looking for fun|reply for pics|"
    r"click to see|view profile|spice it up|trouble in the best way|"
    r"bet you.*trouble|wanna chat|feel like talking|just relocated|"
    r"love some help|onlyfans|fansly|hot.*milf|iflirt|flirt|flirty|"
    r"booty shorts|flirty dm|flirty note|flirty photos|flirty message|"
    r"touching (myself|herself|himself)|is touching|"
    r"dating|night\s*alert|tabl-|hot tonight|are you single|"
    r"wants to chat|send pics|send nudes|meetup|meet up|hangout|"
    r"get together|just moved|new in town|lonely|need company|"
    r"waiting for you|thinking of you|dreamed about|stuck in my head|"
    r"on my mind|saw your pic|cute pic|you look good|you look cute|"
    r"handsome man|sexy man|attractive|gorgeous|beautiful|stunning|"
    r"love your smile|nice body|great body|snap me|snapchat|kik me|"
    r"telegram me|whatsapp me|text me|txt me|call me|hit me up|hmu|"
    r"dm me|dont be shy|no strings|nothing serious|down for anything|"
    r"open minded|attached female|married but|discreet|sugar baby|"
    r"sugar daddy|allowance|spoiled|send money|need \$|broke and",
    re.IGNORECASE,
)

LEGIT = {"discord.com", "google.com", "microsoft.com", "apple.com", "amazon.com",
         "github.com", "kickstarter.com", "xbox.com", "windycitycigars.com",
         "cigarsinternational.com", "olivegarden.com", "krispykreme.com",
         "audible.com", "spotify.com", "tubitv.com", "caswellmassey.com",
         "zennioptical.com", "ulta.com", "marcos.com", "dunkinrewards.com",
         "chick-fil-a.com", "starbucks.com", "texasroadhouse.com",
         "regions.com", "steampowered.com", "borisfx.com", "ubiquiti.com",
         "plex.tv", "googleplay.com", "myq.com", "uber.com",
         "shoecarnival.com", "limitedrungames.com", "scentbird.com",
         "sephora.com", "shutterfly.com", "zulily.com", "empiresofeve.com",
         "churchcenter.com", "sojourn.church", "georgiapacking.org",
         "cigaraficionado.com", "greentoe.com", "qalo.com", "vevor.com",
         "chewy.com", "dominos.com", "papajohns.com", "walmart.com",
         "bestbuy.com", "target.com", "costco.com", "lowes.com",
         "bjswholesaleclub.com", "homedepot.com", "nbc.com", "nbcsports.com",
         "twitch.tv", "wizards.com", "experian.com", "canva.com", "lg.com",
         "samsung.com", "disneypinnacle.com", "ifttt.com",
         "m.starbucks.com", "e.olivegarden.com", "email.chick-fil-a.com",
         "e-rewards.dominos.com", "dough.papajohns.com",
         "promo.newegg.com", "microcenter.com", "email.microcenter.com",
         "mail.scentbird.com", "updates.scentbird.com",
         "geologia.unam.mx", "unam.mx", "ptit.edu.vn", "stu.ptit.edu.vn",
         "correo.chapingo.mx", "cosbrizal.edu.ph", "maristascomayagua.edu.hn",
         "binus.ac.id", "moe.gov.sa", "rb.moe.gov.sa", "eng.zu.edu.eg",
         "lcps.org.uk", "notredameacademy.org", "an.em-net.ne.jp",
         "dolphin.ocn.ne.jp", "ocn.ne.jp", "estudiantes.uv.mx", "web.de",
         "paypal.com", "chase.com", "tiktok.com",
         }

SPAM_DOMAINS = {
    "foxytemptation.com", "arousingdates.com", "vallyme.com", "vovadis.vip",
    "newpinoko.com", "freepinoko.com", "pirinoet.vip",
    "iwhaa.com", "iflirts.com", "i-flirt-s.com",
    "datingapphub.com", "thesoberdating.com", "carpetani.vip",
    "teaseeasyx.com", "freeyvenas.com", "unclegus.org",
    "somiramana.com", "mydatematches.com", "elfaroukegypt.com",
    "gohoha.org", "uslaka.com", "truebootycall.com",
    "wonderko.com", "youlaka.com", "paoloko.com", "arastopi.com",
    "toproh.com", "lolyg.com", "tonyxo.com", "allroxo.com",
    "tutigroup.org", "rokoinfo.com", "locbelowon.org", "undwer.com",
    "monloly.com", "prayst.com", "ynarounda.com", "mybelski.org",
    "karinsas.com", "irisermita.org", "hostermita.org", "theermita.org",
    "xolashop.com", "roxous.com", "autoroh.com", "nilona.org",
    "newdidi.top", "locatedwell.com", "freeynina.com",
    "renitini.com", "sepoffa.com", "cuteyoungladies.com",
    "faithfulfling.com", "hotrdv.com", "hornyaffairs.com",
    "pumpyjoy.com", "locataway.org", "hostsoli.com", "tuvovana.com",
    "dialuxas.ru", "covisianmail.com", "traveltrackerbd.com",
    "moe-dl.edu.my", "chicagoinstituteofbusiness.com",
    "chicagoinstituteofbusiness.online", "cibnotifications.com",
    "markethair", "fivv.pp.ua", "xqiyegt", "hireevonline",
    "open-hosted.com", "vtbrpsgnrwcdulcvpq",
    "adultcrush.com", "bilorina.com", "sarawaka.com", "qoez.org",
    "webvova.vip", "yninarow.com", "itvoly.com",
    "elalina.vip", "freesapa.com", "andavtis.com", "carmenko.com",
    "elitemarine.com.br", "mixcloudmail.com",
    "roxoweb.com", "hostroh.com",
    "cupidconnectnag.ru", "kisswisp.ru", "meetglownow.ru",
    "romanticluster.ru", "greatxdatefinder.com", "hellopromo.info",
    "soontoday.info", "freshday.info", "flirtwiththestars.com",
    "checkoutgirlsnow.com", "heytherelab.com", "thexdate.net",
    ".ru", ".biz", ".top", ".pp.ua", ".co.nl", ".org.uk",
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

def decode_field(s):
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

def is_spam(sender_raw, subject_raw):
    sender = sender_raw.lower()
    subject = subject_raw.lower()

    for dom in LEGIT:
        if dom in sender:
            return False

    for d in SPAM_DOMAINS:
        if d in sender:
            return True

    if RE_SEXUAL.search(sender) or RE_SEXUAL.search(subject):
        return True

    for phrase in NEW_PATTERNS:
        if phrase in subject:
            return True

    return False


def sweep_account(email_addr, folder="INBOX"):
    print(f"\n{'='*50}")
    print(f"Account: {email_addr} | Folder: {folder}")
    print(f"{'='*50}")

    env_pass = get_password(email_addr)
    if not env_pass:
        print("  SKIP: password not found")
        return 0, 0, []

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=30)
        mail.login(email_addr, env_pass)
    except Exception as e:
        print(f"  LOGIN FAILED: {e}")
        return 0, 0, []

    try:
        mail.select(folder)
    except Exception as e:
        print(f"  SELECT FAILED: {e}")
        mail.logout()
        return 0, 0, []

    since_date = (datetime.now() - timedelta(days=30)).strftime("%d-%b-%Y")
    _, data = mail.search(None, f"(SINCE {since_date})")
    all_ids = data[0].split()
    if not all_ids:
        print("  No recent messages.")
        mail.logout()
        return 0, 0, []

    max_msgs = 500 if "compjunkie" in email_addr else 300
    uids = all_ids[-max_msgs:]

    print(f"  Checking {len(uids)} messages (last 30 days)...")

    spam_ids = []
    checked = 0
    found_patterns = []

    for uid in uids:
        if should_exit():
            print("  TIMEOUT — breaking")
            break
        try:
            _, fetched = mail.fetch(uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
            checked += 1
            for item in fetched:
                if isinstance(item, tuple):
                    raw = item[1]
                    try:
                        msg = email.message_from_bytes(raw)
                    except Exception:
                        continue
                    sender = decode_field(msg.get("From", ""))
                    subject = decode_field(msg.get("Subject", ""))
                    if is_spam(sender, subject):
                        spam_ids.append(uid)
                        matched = []
                        for phrase in NEW_PATTERNS:
                            if phrase in subject.lower():
                                matched.append(phrase)
                        found_patterns.append({
                            "sender": sender,
                            "subject": subject,
                            "matched": matched
                        })
                        break
        except Exception:
            continue

    trashed = 0
    if spam_ids and folder == "INBOX":
        batch = ",".join([b.decode() if isinstance(b, bytes) else b for b in spam_ids])
        try:
            mail.copy(batch, "[Gmail]/Spam")
            for uid in spam_ids:
                mail.store(uid, "+FLAGS", "\\Deleted")
            mail.expunge()
            trashed = len(spam_ids)
            print(f"  Trashed {trashed} spam messages")
        except Exception as e:
            print(f"  MOVE FAILED: {e}")

    mail.logout()

    if found_patterns:
        print(f"\n  === PATTERNS FOUND ({len(found_patterns)}) ===")
        for p in found_patterns[:20]:
            print(f"    [{p['sender'][:40]}] {p['subject'][:60]}")
            if p['matched']:
                print(f"      -> matched: {', '.join(p['matched'])}")

    return checked, trashed, found_patterns


def discover_spam_patterns(email_addr):
    """Scan Spam folder to discover new sender domains and subject patterns."""
    print(f"\n  [DISCOVER] Scanning [Gmail]/Spam for new patterns...")
    env_pass = get_password(email_addr)
    if not env_pass:
        return [], []

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=30)
        mail.login(email_addr, env_pass)
    except Exception as e:
        print(f"    LOGIN FAILED: {e}")
        return [], []

    try:
        mail.select("[Gmail]/Spam")
    except Exception as e:
        print(f"    SELECT FAILED: {e}")
        mail.logout()
        return [], []

    since_date = (datetime.now() - timedelta(days=14)).strftime("%d-%b-%Y")
    _, data = mail.search(None, f"(SINCE {since_date})")
    all_ids = data[0].split()
    if not all_ids:
        mail.logout()
        return [], []

    max_msgs = 200 if "compjunkie" in email_addr else 100
    uids = all_ids[-max_msgs:]

    new_domains = set()
    new_phrases = set()

    for uid in uids:
        if should_exit():
            break
        try:
            _, fetched = mail.fetch(uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
            for item in fetched:
                if isinstance(item, tuple):
                    try:
                        msg = email.message_from_bytes(item[1])
                    except Exception:
                        continue
                    sender = decode_field(msg.get("From", ""))
                    subject = decode_field(msg.get("Subject", ""))

                    # Extract domain from sender
                    m = re.search(r'@([^\s>]+)', sender)
                    if m:
                        domain = m.group(1).lower()
                        if domain not in SPAM_DOMAINS and not any(d in domain for d in LEGIT):
                            new_domains.add(domain)

                    # Check for new phrases not in existing patterns
                    subj_lower = subject.lower()
                    for phrase in NEW_PATTERNS:
                        if phrase in subj_lower:
                            pass  # Already known
                    else:
                        # Extract candidate spammy words/phrases
                        words = re.findall(r'\b[a-z]{4,}\b', subj_lower)
                        for w in words:
                            if w in {"tonight", "single", "lonely", "bored", "horny",
                                     "sexy", "naughty", "flirty", "booty", "hottie",
                                     "milf", "cougar", "sugar", "discreet", "attached",
                                     "married", "cheating", "affair", "hookup", "dtf",
                                     "nsa", "fwb", "casual", "adult", "dating", "meet",
                                     "chat", "pics", "nudes", "snap", "kik", "onlyfans",
                                     "fansly", "venmo", "cashapp", "crypto", "invest",
                                     "inheritance", "refund", "irs", "debt", "loan",
                                     "prize", "winner", "reward", "bonus", "claim",
                                     "verify", "suspended", "locked", "expired",
                                     "urgent", "act now", "limited", "expires"}:
                                new_phrases.add(w)
        except Exception:
            continue

    mail.logout()
    return list(new_domains)[:20], list(new_phrases)[:20]


if __name__ == "__main__":
    total_checked = 0
    total_trashed = 0
    all_patterns = []

    for email_addr in ACCOUNTS:
        checked, trashed, patterns = sweep_account(email_addr, "INBOX")
        total_checked += checked
        total_trashed += trashed
        all_patterns.extend(patterns)

        # Discovery pass on Spam folder
        new_doms, new_phrases = discover_spam_patterns(email_addr)
        if new_doms:
            print(f"    New domains found: {', '.join(new_doms[:10])}")
        if new_phrases:
            print(f"    New phrases found: {', '.join(new_phrases[:10])}")

        if should_exit():
            print("  GLOBAL TIMEOUT — stopping")
            break

    print(f"\n{'='*50}")
    print(f"TOTAL: Checked {total_checked}, Trashed {total_trashed}")
    print(f"Unique spam patterns hit: {len(set(p['subject'] for p in all_patterns))}")
    print(f"{'='*50}")
