#!/usr/bin/env python3
"""IMAP Gmail spam sweep — batched fetches, fast."""
import imaplib, email, json, re, sys, os, time
from email.header import decode_header
from datetime import datetime, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

START_TIME = time.time()
MAX_RUNTIME = 150

def should_exit():
    return time.time() - START_TIME > MAX_RUNTIME

# Load passwords from local config file (isolated sessions don't inherit env vars)
LOCAL_CONFIG = os.path.join(os.path.dirname(__file__), ".gmail_accounts.json")

ACCOUNTS = {
    "compjunkie@gmail.com":         "GMAIL_APP_PASSWORD_COMPJUNKIE",
    "jhenderson87@gmail.com":       "GMAIL_APP_PASSWORD_JHENDERSON",
    "layeredmediallc@gmail.com":    "GMAIL_APP_PASSWORD_LAYEREDMEDIA",
    "nova.cofounder@gmail.com":     "GMAIL_APP_PASSWORD_NOVA",
}

def get_password(email_addr):
    """Get password from env var or local config file."""
    pass_var = ACCOUNTS.get(email_addr, "")
    if not pass_var:
        return ""
    # Try env var first
    env = os.environ.get(pass_var, "").strip().replace(" ", "")
    if env:
        return env
    # Fallback to config file
    try:
        with open(LOCAL_CONFIG, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get(email_addr, "").strip().replace(" ", "")
    except Exception:
        return ""


# ── Detection ──
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
    "dialuxas.ru",
    "covisianmail.com", "traveltrackerbd.com", "moe-dl.edu.my",
    "chicagoinstituteofbusiness.com", "chicagoinstituteofbusiness.online",
    "cibnotifications.com", "markethair", "fivv.pp.ua", "xqiyegt",
    "hireevonline", "open-hosted.com", "vtbrpsgnrwcdulcvpq",
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
    r"dating|night\s*alert|tabl-",
    re.IGNORECASE,
)

RE_FAKE_SENDER = re.compile(
    r"telegram|whatsapp|signal\s*<|discord\s*<|messenger\s*<|direct\s*<|"
    r"missedcall|new\s*match|iwant|naughty|tabl-|hottie|porn|xxx|naughty|"
    r"sexy|horny|booty|nibble|bedroom|scoop",
    re.IGNORECASE,
)

CORE_BAD = {"sex", "fuck", "cock", "cum", "pussy", "dick", "penis", "vagina",
            "clit", "anal", "blowjob", "handjob", "creampie", "deepthroat",
            "gangbang", "bukkake", "squirt", "threesome", "orgy", "swingers",
            "bdsm", "fetish", "kink", "kinky", "dominatrix", "nudity",
            "erotic", "erotica", "nsfw", "seductive", "passionate", "steamy",
            "breasts", "naked", "nude"}

DATING = {"wants to meet you", "likes your profile", "feels the attraction",
          "someone likes you", "private message received", "new message from",
          "desires you", "hookup", "dtf", "nsa", "fwb", "friends with benefits",
          "casual sex", "adult dating", "online flirting", "meet local",
          "local babes", "choose the girl", "start chatting",
          "waiting to connect", "new match", "private match",
          "feel your breasts", "soft for your fingers", "meet her before bed",
          "get to know you", "spice it up", "hot affair", "sexy singles",
          "i want hookups", "iflirts", "play with me", "available tonight",
          "bored and lonely", "looking for fun", "reply for pics",
          "click to see", "view profile", "claim your", "you won",
          "free gift", "act now", "missed call", "unread message",
          "instagram direct", "reply to an important message",
          "friends in private chat", "she dares you", "she checked your profile",
          "her message can't wait", "she's hoping you'll open",
          "tonight you have a choice", "instant connections", "no filters",
          "confirm your email", "urgent confirm",
          "hello compjunkie", "re: compjunkie", "i finally found you",
          "group chat", "i have a confession", "drop your pants",
          "your name came to mind", "your body can always light my fire",
          "coffee break", "sybian rides", "i'm easy to rev up",
          "wait one second before you go", "eyes only",
          "no pressure, just happy feelings", "ass fantasies",
          "my boobs are begging", "what we'd be like", "when if not now",
          "who's the boss", "size and proportions", "noble professions",
          "anything you want, i can do", "down-to-earth girl wants you",
          "don't let this mood pass you by", "i'm convinced, i love you",
          "iz it u i saw today", "what u like in bed", "friendly wink",
          "found something cool", "curious about what you'd like",
          "hey stranger", "call me", "great listener",
          "relations with alt-girl", "my heart beats faster",
          "i like men having the upper hand", "quick fix", "milf looking for",
          "got her snap after lunch", "someone wants to talk with you",
          "being sweet while you rail me", "i'm fun loving and lover of fun",
          "i'm new here", "my smile is a challenge",
          "free option and gets results", "being 40 is perfect",
          "you matter to someone", "is curious to see more of you",
          "where've you been all this time",
          "she just pinged you", "let's live a little",
          "someone is curious to know you", "i'm looking for a great time",
          "i want to experiment and enjoy life more",
          "life without love", "i wish you were here",
          "my fantasy is to be with you", "these girls have a certain pull",
          "beautiful chinese girls want to chat",
          "do you know how to have a good time",
          "want to partner up and have some fun",
          "ask me out", "message from mortar", "someone reading",
          "lisa online near", "you ready", "straight up",
          "you busy this week", "oral fixation", "me? an oral fixation? yes",
          "samara is now following you", "can we make love",
          "without any obligations", "i found you on facebook",
          "great pic", "luv69", "the deeper truth of attraction",
          "so about that site", "met her", "females show a lot of tricks",
          "online spectators", "females show", "tricks to online spectators",
          "costco meat box", "ready to ship", "your costco meat box",
          "great steaks sampler", "omaha steaks",
          "nationwide carry for military", "bill for nationwide carry",
          "order verification notice", "verification notice",
          "inquiry", "order – verification notice",
          "nerve fresh", "relief from tingling",
          "i'm having a break", "let's open up new frontiers",
          "i know you want it", "lick my", "hi, wanna chat",
          "anytime you feel like talking", "just relocated here",
          "would love some help", "here for you", "new here and",
          "shower together", "incredibly nice inside", "makes me incredibly",
          "several members are trying to reach you", "just messaged you",
          "landed in your inbox", "wondering how you look like",
          "working out in the bedroom", "real mature woman",
          "strip me", "from that site", "want to see what i'm doing",
          "she's sharing something", "she made something you should see",
          "enjoy premium access", "thanks for joining",
          "post a comment on your wall", "compjunkie hi",
          "you'll like this", "quick question before i disappear",
          "passing this to you", "photos i've kept to myself",
          "authentic platform", "did you manage to find",
          "sent you a follow request", "notification from",
          "she said yes", "said yes", "connected with",
          "a new message to read",
          "bet you're trouble", "trouble in the best way", "you're trouble",
          "wanna chat", "feel like talking", "just relocated", "love some help",
          "fast \u0026 flirty", "flirty flings", "flirty edition",
          "flirty connection", "flirty dm", "flirty note",
          "flirty photos", "flirty message", "flirty and",
          "fun and flirty", "sent a flirty",
          "is touching herself", "is touching himself", "touching myself",
          "match update:", "deletes in", "sent message",
          }

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
         "bjswholesaleclub.com",
         "homedepot.com", "nbc.com", "nbcsports.com", "twitch.tv",
         "wizards.com", "experian.com", "canva.com", "lg.com",
         "samsung.com", "disneypinnacle.com", "ifttt.com",
         "m.starbucks.com", "e.olivegarden.com", "email.chick-fil-a.com",
         "e-rewards.dominos.com", "dough.papajohns.com",
         "promo.newegg.com", "microcenter.com", "email.microcenter.com",
         "mail.scentbird.com", "updates.scentbird.com",
         "geologia.unam.mx", "unam.mx", "ptit.edu.vn",
         "stu.ptit.edu.vn", "correo.chapingo.mx",
         "cosbrizal.edu.ph", "maristascomayagua.edu.hn",
         "binus.ac.id", "moe.gov.sa", "rb.moe.gov.sa",
         "eng.zu.edu.eg", "lcps.org.uk", "notredameacademy.org",
         "an.em-net.ne.jp", "dolphin.ocn.ne.jp", "ocn.ne.jp",
         "estudiantes.uv.mx", "web.de",
         "paypal.com", "chase.com", "tiktok.com",
         }


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

    if RE_FAKE_SENDER.search(sender):
        return True
    if RE_SEXUAL.search(sender) or RE_SEXUAL.search(subject):
        return True

    combined = sender + " " + subject
    if re.search(r"anytime you feel like talking|just relocated|would love some help", combined, re.IGNORECASE):
        return True
    if re.search(r"key to your entry|entry now|click here|open this", subject, re.IGNORECASE):
        return True
    # Only flag verification codes from suspicious sources (not legit services)
    if "verification code" in subject:
        legit_code_senders = {"paypal.com", "chase.com", "google.com", "microsoft.com",
                              "amazon.com", "apple.com", "discord.com", "eveonline"}
        if not any(s in sender for s in legit_code_senders):
            return True
    if re.search(r"claim your prize|congratulations.*won|you.*won|click to claim", subject, re.IGNORECASE):
        return True
    # Prize/reward — only flag if sender is suspicious too
    if re.search(r"beach reward|your .* is here|free.*gift", subject, re.IGNORECASE):
        if not any(d in sender for d in LEGIT):
            return True

    for w in CORE_BAD:
        if w in subject:
            return True
    for w in DATING:
        if w in subject:
            return True

    # Random-name free-email with pickup lines
    if re.search(r"@(gmail|hotmail|outlook)\.com", sender) and any(w in subject for w in DATING):
        return True

    return False


def sweep_one(email_addr):
    print(f"\n{'='*50}")
    print(f"Account: {email_addr}")
    print(f"{'='*50}")

    env_pass = get_password(email_addr)
    if not env_pass:
        print("  SKIP: password not found (env var or .gmail_accounts.json)")
        return 0, 0

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=20)
        mail.login(email_addr, env_pass)
    except Exception as e:
        print(f"  LOGIN FAILED: {e}")
        return 0, 0

    mail.select("INBOX")
    # Check last 14 days, up to 200 messages for heavy-spam accounts
    since_date = (datetime.now() - timedelta(days=14)).strftime("%d-%b-%Y")
    _, data = mail.search(None, f"(SINCE {since_date})")
    all_ids = data[0].split()
    if not all_ids:
        print("  No recent messages.")
        mail.logout()
        return 0, 0

    # Take last N UIDs -- more for compjunkie which gets heavy spam
    max_msgs = 100 if "compjunkie" in email_addr else 50
    uids = all_ids[-max_msgs:]
    uid_str = ",".join([b.decode() if isinstance(b, bytes) else b for b in uids])

    print(f"  Checking {len(uids)} messages (last 7 days)...")

    # Batch fetch headers
    _, fetched = mail.fetch(uid_str, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
    spam_ids = []
    checked = 0
    current_uid = None

    for item in fetched:
        if isinstance(item, tuple):
            # Parse UID from response
            raw_bytes = item[1]
            # Extract UID from the preceding bytes if available
            pass  # We'll map by position
        elif isinstance(item, bytes):
            # This is the UID response line: b'1 (UID 123 ...'
            m = re.search(r"UID\s+(\d+)", item.decode("ascii", "ignore"))
            if m:
                current_uid = m.group(1).encode()

    # Simpler: fetch one by one but with timeout guard
    spam_ids = []
    checked = 0
    for uid in uids:
        if should_exit():
            print("  TIMEOUT")
            break
        try:
            _, msg_data = mail.fetch(uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
            if not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            sender = decode_field(msg.get("From", ""))
            subject = decode_field(msg.get("Subject", ""))
            checked += 1
            if is_spam(sender, subject):
                spam_ids.append(uid)
                print(f"  [SPAM] {sender[:45]:<45} | {subject[:50]}")
        except Exception:
            continue

    if spam_ids:
        print(f"  Trashing {len(spam_ids)}...")
        for uid in spam_ids:
            if should_exit():
                break
            try:
                mail.copy(uid, "[Gmail]/Trash")
                mail.store(uid, "+FLAGS", "\\Deleted")
            except Exception as e:
                print(f"    ERR: {e}")
        mail.expunge()
    else:
        print("  Clean.")

    mail.close()
    mail.logout()
    return checked, len(spam_ids)


if __name__ == "__main__":
    target = os.environ.get("GMAIL_ACCOUNT", "").strip()
    total_c = 0
    total_t = 0

    if target and target in ACCOUNTS:
        c, t = sweep_one(target)
        total_c += c; total_t += t
    else:
        for email_addr in ACCOUNTS.keys():
            if should_exit():
                print("\n  GLOBAL TIMEOUT")
                break
            c, t = sweep_one(email_addr)
            total_c += c; total_t += t
            time.sleep(1)

    print(f"\n{'='*50}")
    print(f"Done. Checked ~{total_c}, trashed {total_t}. ({time.time()-START_TIME:.1f}s)")
    print(f"{'='*50}")
