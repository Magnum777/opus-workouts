#!/usr/bin/env python3
"""IMAP Gmail spam sweep — batched fetches, fast. Scans INBOX and Spam."""
import imaplib, email, json, re, sys, os, time, logging
from email.header import decode_header
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

START_TIME = time.time()
MAX_RUNTIME = 240  # 4 minutes max (cron timeout is 480s, we need margin)

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

def get_password(email_addr: str) -> str:
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
    except Exception as e:
        logger.warning("Config load failed for %s: %s", email_addr, e)
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
    "henrydixonjournal.net",
    "poladina.com",
    "netboni.com",
    "pinokondo.com",
    "flirtyynights.com",
    "bestxdateofferings.com",
    "hers-love.com",
    "fckfriendfinder.com",
    "covisianmail.com", "traveltrackerbd.com", "moe-dl.edu.my",
    "chicagoinstituteofbusiness.com", "chicagoinstituteofbusiness.online",
    "cibnotifications.com", "markethair", "fivv.pp.ua", "xqiyegt",
    "hireevonline", "open-hosted.com", "vtbrpsgnrwcdulcvpq",
    "pornhub.com", "frali.org", "hohj.org", "adultcrush.com", "bilorina.com", "sarawaka.com", "qoez.org",
    "webvova.vip", "yninarow.com", "itvoly.com",
    "elalina.vip", "freesapa.com", "andavtis.com", "carmenko.com",
    "elitemarine.com.br", "mixcloudmail.com",
    "roxoweb.com", "hostroh.com",
    "cupidconnectnag.ru", "kisswisp.ru", "meetglownow.ru",
    "romanticluster.ru", "greatxdatefinder.com", "hellopromo.info",
    "soontoday.info", "freshday.info", "flirtwiththestars.com",
    "checkoutgirlsnow.com", "heytherelab.com", "thexdate.net",
    "privaterelay.appleid.com", "questionprov5129231.com", "rugcoumvlof.ru",
    "tiktokshop.com", "ubpew.qpj",
    ".ru", ".biz", ".top", ".pp.ua", ".co.nl", ".org.uk",
}

RE_SEXUAL = re.compile(
    r"pornhub|on cam|cam because|totally excited|come over to my room|"
    r"kitty owns me|until you scream|i want the way your|"
    r"something naughty|naughty i wanted|naughty i wanted to share|"
    r"requiring a sophisticated male opinion|sophisticated male opinion|"
    r"sent you a wink|fun we had|remember how much fun|"
    r"hottie|booty|nibble|bedroom|scoop|stretched|oral|fixation|"
    r"can we make love|naked|nude|horny|porn|xxx|sexy|dtf|hookup|"
    r"casual sex|adult dating|hot affair|sexy singles|play with me|"
    r"available tonight|wanting a crazy night|wants a crazy night|wanting a wild night|wants a wild night|wanting some fun|wants some fun|wants to party|wanting to party|bored and lonely|looking for fun|reply for pics|"
    r"click to see|view profile|spice it up|trouble in the best way|"
    r"bet you.*trouble|wanna chat|feel like talking|just relocated|"
    r"love some help|onlyfans|fansly|hot.*milf|iflirt|flirt|flirty|"
    r"booty shorts|flirty dm|flirty note|flirty photos|flirty message|"
    r"touching (myself|herself|himself)|is touching|"
    r"dating|night\s*alert|tabl-|hot tonight|are you single|"
    r"wants to chat|send pics|send nudes|meetup|hangout|get together|"
    r"just moved|new in town|lonely|need company|waiting for you|"
    r"thinking of you|saw your pic|cute pic|you look good|handsome man|"
    r"snap me|snapchat|kik me|telegram me|whatsapp me|text me|txt me|"
    r"call me|hit me up|hmu|dm me|dont be shy|no strings|nothing serious|"
    r"down for anything|open minded|attached female|married but|discreet|"
    r"sugar baby|sugar daddy|allowance|spoiled|send money|need \$|broke and|"
    r"ride you until we both|light up your.*firecracker|anal virgin|"
    r"someone wants to meet|wants to meet|meet me|let's meet|wanna meet|"
    r"explode|cum|blow your|rock your|turn you on|turn me on|"
    r"touch me|feel me|want you|need you|desire you|crave you|"
    r"naughty girl|bad girl|good girl|your girl|my girl|lonely girl|"
    r"mature woman|real woman|local woman|single woman|married woman|"
    r"divorced|separated|unattached|looking for love|need a man|need a guy|"
    r"younger.*older|age is just|age doesn't matter|cougar|"
    r"picks you|picked you|selected you|chose you|chosen for you",
    re.IGNORECASE,
)

RE_FAKE_SENDER = re.compile(
    r"telegram|whatsapp|signal\s*<|discord\s*<|messenger\s*<|direct\s*<|"
    r"missedcall|new\s*match|iwant|naughty|tabl-|hottie|porn|xxx|naughty|"
    r"sexy|horny|booty|nibble|bedroom|scoop|hot tonight|wanting a crazy night|wants a crazy night|are you single|"
    r"wants to chat|send pics|meetup|snapchat|kik|onlyfans|fansly|"
    r"milf|cam|sophisticated male|wink|fun we had|eharmony|"
    r"foxytemptation|i want hookups|faithful fling|hot.*milf|"
    r"someone wants to meet|wants to meet|meet you|meet me|let's meet|"
    r"localtemptation|temptation|wet emoji|wet emojis|gucciluci|"
    r"truebootycall|true booty call",    # True Booty Call spam
    re.IGNORECASE,
)

RE_BUSINESS_SCAM = re.compile(
    r"order verification notice|verification notice|order verification|verification required|"
    r"your account has been|account suspended|account locked|blocked all your|confirm your email|urgent confirm|action required|"
    r"suspended due to|unusual activity detected|invoice attached|invoice from|payment receipt|"
    r"wire transfer|bank transfer|direct deposit|dear valued customer|dear sir/madam|"
    r"kindly|urgent response needed|respond immediately|crypto investment|bitcoin investment|"
    r"investment opportunity|double your money|guaranteed returns|risk free|earn daily|"
    r"passive income|work from home|make money fast|financial freedom|secret method|"
    r"exclusive offer|limited time only|act now|you have been selected|congratulations winner|"
    r"weight loss guaranteed|lose pounds fast|miracle diet|ozempic|wegovy|glp-1|weight loss pills|"
    r"cbd gummies|cbd oil|hemp extract|keto pills|apple cider vinegar|garcinia cambogia|"
    r"male enhancement|testosterone booster|performance plus|credit card declined|"
    r"update payment info|billing issue|package delivery failed|shipping address needed|"
    r"dhl delivery|fedex tracking|ups package|customs fee|import duty|clearance required|"
    r"irs notice|tax refund|tax settlement|social security|medicare|medicaid|"
    r"loan approved|loan pre-approved|credit approved|debt consolidation|reduce your debt|"
    r"debt relief|reverse mortgage|home equity|cash out|timeshare|vacation package|free cruise|"
    r"extended warranty|vehicle warranty|car warranty|health insurance|dental insurance|"
    r"life insurance quote|mortgage rates|refinance now|low rates|pre-approved|pre-qualified|"
    r"special financing|gift card|free gift card|redeem now|survey reward|complete survey|"
    r"opinion wanted|charity donation|donate now|help children|inheritance|next of kin|"
    r"unclaimed funds|lottery winner|lucky winner|prize claim|bank of america alert|"
    r"wells fargo alert|chase alert|suspicious login|unauthorized access|security breach|"
    r"verify identity|identity verification|kyc required|2fa code|two factor|authentication code|"
    r"reset password|password expired|credentials|login attempt|sign in attempt|new device|"
    r"geek squad|norton|mcafee|renew subscription|antivirus expired|security software|tech support|"
    r"microsoft support|apple support|amazon support|refund pending|refund processing|"
    r"refund approved|overcharged|billing error|payment dispute",
    re.IGNORECASE,
)

RE_NEWSLETTER_BULK = re.compile(
    r"unsubscribe|no-reply|noreply|newsletter|digest|daily update|weekly update|"
    r"promotional|promo|marketing|advertisement|sponsored|partner offer|"
    r"you might like|recommended for you|based on your|personalized|tailored",
    re.IGNORECASE,
)

CORE_BAD = {"pornhub", "sex", "fuck", "cock", "cum", "pussy", "dick", "penis", "vagina",
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
          "hot tonight", "are you single", "wants to chat", "send pics",
          "send nudes", "trade pics", "meet up", "meetup", "hangout",
          "get together", "just moved", "new in town", "lonely and",
          "so lonely", "need company", "waiting for you", "thinking of you",
          "saw your pic", "cute pic", "you look good", "handsome man",
          "snap me", "snapchat", "kik me", "telegram me", "whatsapp me",
          "text me", "txt me", "call me", "hit me up", "hmu", "dm me",
          "dont be shy", "no strings", "nothing serious", "down for anything",
          "open minded", "attached female", "married but", "discreet",
          "sugar baby", "sugar daddy", "allowance", "spoiled",
          "send money", "need $", "broke and", "pounds in 15 days", "pounds in 30 days", "GLP-1", "GetThin", "3-min assessment", "Lose Weight Sooner", "medically qualif", "no insurance needed", "prescription is ready", "Get approved",
          "bored and lonely", "wanting a crazy night", "wants a crazy night", "wanting a wild night", "wants a wild night", "wanting some fun", "wants some fun", "wants to party", "wanting to party", "pull me by my hair", "sexy lingerie", "dance on the pylon", "stripper", "multiple orgasms", "turns me on", "asking for more photos", "find someone special", "looking for fun", "reply for pics",
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
          "inquiry", "order \u2013 verification notice",
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
          "fast & flirty", "flirty flings", "flirty edition",
          "flirty connection", "flirty dm", "flirty note",
          "flirty photos", "flirty message", "flirty and",
          "fun and flirty", "sent a flirty",
          "is touching herself", "is touching himself", "touching myself",
          "photos i've kept to myself",
          "authentic platform", "did you manage to find",
          "sent you a follow request", "notification from",
          "she said yes", "said yes", "connected with",
          "a new message to read",
          "bet you're trouble", "trouble in the best way", "you're trouble",
          "wanna chat", "feel like talking", "just relocated", "love some help",
          "fast & flirty", "flirty flings", "flirty edition",
          "flirty connection", "flirty dm", "flirty note",
          "flirty photos", "flirty message", "flirty and",
          "fun and flirty", "sent a flirty",
          "is touching herself", "is touching himself", "touching myself",
          "match update:", "deletes in", "sent message",
          "local singles live", "mysterious gift", "private content",
          "someone anonymous", "unlock to reveal",
          "requiring a sophisticated male opinion", "sophisticated male opinion",
          "attire for a quiet social gathering", "caught you looking",
          "she wants your eyes on this", "sent you a private request",
          "accept click any button",
          "sent you a wink", "fun we had", "remember how much fun",
          "how much fun we had", "you remind me of someone",
          "would like to see you on cam", "see you on cam",
          "come over to my room baby", "totally excited",
          "one call with you is never enough", "irresistibly yours to nibble tonight",
          "nibble tonight", "afternoon compjunkie", "compjunkie - afternoon",
          "quick idea about our plan", "something naughty i wanted to share",
          "naughty i wanted to share", "saved it private just for now",
          "hot milf", "h o t m i l f",
          "added you to private group", "private group",
          "end-to-end encrypted", "mutual contacts",
          "people in this chat",
          "blocked your account", "photos and videos will be deleted",
          "we've blocked your account",
          "uncovered something weird", "what makes someone memorable",
          "compjunkie?", "unexpected excitement is right around the corner",
          "someone wants to meet you", "someone wants to meet", "wants to meet",
          "meet you", "meet me", "let's meet", "wanna meet", "down to meet",
          "ride you until we both", "light up your", "firecracker of",
          "explode", "cum", "blow your", "rock your",
          "naughty girl", "bad girl", "good girl", "your girl", "my girl", "lonely girl",
          "mature woman", "real woman", "local woman", "single woman", "married woman",
          "divorced", "separated", "unattached", "looking for love", "need a man", "need a guy",
          "age is just", "age doesn't matter", "cougar",
          "picks you", "picked you", "selected you", "chose you", "chosen for you",
          "i adore the way your body", "our adventure together", "deeply fascinated",
          "cherish me", "i honestly laughed waiting", "my day got better because",
          "i need your cock", "satisfy me", "your cock to satisfy",
          "long fors me", "body long fors",
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
         "paypal.com", "chase.com", "tiktok.com", "tiktokshop.com",
         "rakuten.com", "ladders.com",
         }


def decode_field(s: str) -> str:
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


def is_spam(sender_raw: str, subject_raw: str) -> bool:
    sender = sender_raw.lower()
    subject = subject_raw.lower()

    # Subject whitelist: never flag legitimate hotel/travel agreements
    SAFE_SUBJECTS = ["guest agreement", "reservation confirmed", "booking confirmed", "check-in instructions", "welcome to"]
    for safe in SAFE_SUBJECTS:
        if safe in subject:
            return False

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

    # Business scam detection
    if RE_BUSINESS_SCAM.search(subject) and not any(d in sender for d in LEGIT):
        return True

    # Newsletter bulk with no legit domain
    if RE_NEWSLETTER_BULK.search(subject) and not any(d in sender for d in LEGIT):
        # Only flag if sender looks suspicious (random domain, not a known service)
        suspicious_tld = re.search(r'\.(ru|biz|top|pp\.ua|co\.nl|org\.uk|tk|ml|cf)$', sender)
        if suspicious_tld or re.search(r'[0-9]', sender.split('@')[-1] if '@' in sender else sender):
            return True

    # Aggressive subject-line keyword matches (catch evolving dating spam fast)
    AGGRESSIVE_PATTERNS = [
        r"someone wants to meet",
        r"wants to meet you",
        r"ride you until we both",
        r"light up your.*(firecracker|4th)",
        r"anal virgin",
        r"explode",
        r"cum\b",
        r"blow your",
        r"rock your",
        r"turn (you|me) on",
        r"touch (me|you)",
        r"desire you",
        r"crave you",
        r"naughty girl",
        r"bad girl",
        r"lonely girl",
        r"mature woman",
        r"real woman",
        r"local woman",
        r"single woman",
        r"married woman",
        r"divorced",
        r"separated",
        r"unattached",
        r"looking for love",
        r"need a (man|guy)",
        r"age is just",
        r"age doesn't matter",
        r"cougar",
        r"picks you",
        r"picked you",
        r"selected you",
        r"chosen for you",
        # True Booty Call signature subjects (they rotate domains)
        r"let you in on her fantasy",
        r"wants to let you in",
        r"her fantasy",
        r"truebootycall",
        r"true booty call",
        # Modern dating spam patterns
        r"get inside",
        r"before the stream",
        r"stream ends",
        r"pull my hair",
        r"make me yours",
    ]
    for pattern in AGGRESSIVE_PATTERNS:
        if re.search(pattern, subject, re.IGNORECASE):
            return True

    # Emoji-heavy sender name detection (fake "first name + emoji" dating spam)
    # Pattern: name with emoji in sender field + dating/sexual subject
    sender_name_only = sender.split("<")[0].strip() if "<" in sender else sender
    emoji_count = len(re.findall(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251\u2764\U0001F48B\U0001F4A7\U0001F351\U0001F353\U0001F364\U0001F382\U0001F3B6\U0001F4AF\U0001F495\U0001F496\U0001F497\U0001F498\U0001F499\U0001F49A\U0001F49B\U0001F49C\U0001F49D\U0001F525\U0001F336\U0001F344]", sender_name_only))
    if emoji_count >= 1 and any(w in subject for w in DATING):
        return True
    # Also catch if sender name itself has heavy dating signals with emojis
    if emoji_count >= 1 and re.search(r"adore|cherish|fascinated|laugh|waiting|body|cock|satisfy", subject, re.IGNORECASE):
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
    # Prize/reward -- only flag if sender is suspicious too
    if re.search(r"beach reward|your .* is here|free.*gift", subject, re.IGNORECASE):
        if not any(d in sender for d in LEGIT):
            return True

    for w in CORE_BAD:
        if w in subject:
            return True
    for w in DATING:
        if w in subject:
            return True

    # Fake sender names (just first name + dating subject)
    fake_sender_names = {"karen", "linda", "dorothy", "mary",
                         "h o t m i l f", "hot milf", "adultcrush"}
    sender_name = sender.split("<")[0].strip().lower() if "<" in sender else sender.lower()
    if any(name in sender_name for name in fake_sender_names) and any(w in subject for w in DATING):
        return True

    # Fake person names with dating/sexual keywords
    fake_names = {"kyree", "kyree owen", "md mahtab", "chadeb", "amber",
                  "allen kimberly", "nancy", "camilla", "kimberly clark", "sarah",
                  "linda moore", "dorothy young", "karen perez"}
    if any(name in sender_name for name in fake_names) and any(w in subject for w in DATING):
        return True

    # Random-name free-email with pickup lines
    if re.search(r"@(gmail|hotmail|outlook)\.(com|co\.\w+)", sender) and any(w in subject for w in DATING):
        return True

    return False


def sweep_folder(email_addr: str, password: str, folder: str, label: str, max_msgs: int = 100) -> tuple[int, int, list]:
    """Sweep a single folder. Returns (checked, trashed, details)."""
    if should_exit():
        return 0, 0, []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", timeout=15)
        mail.login(email_addr, password)
    except Exception as e:
        logger.error("  LOGIN FAILED: %s", e)
        return 0, 0, []

    status, _ = mail.select(folder)
    if status != "OK":
        logger.warning("  SELECT FAILED for %s", folder)
        mail.logout()
        return 0, 0, []

    # Check last 7 days for spam folder, 14 days for inbox (tighter = faster)
    days = 14 if "INBOX" in folder else 7
    since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
    _, data = mail.search(None, f"(SINCE {since_date})")
    all_ids = data[0].split()
    if not all_ids:
        logger.info("  %s: No recent messages.", label)
        mail.close()
        mail.logout()
        return 0, 0, []

    # Take last N UIDs - keep it lean to stay under cron timeout
    if "INBOX" in folder:
        max_msgs = 60 if "compjunkie" in email_addr else 40
    else:
        max_msgs = 40
    uids = all_ids[-max_msgs:]

    logger.info("  %s: Checking %d messages (last %d days)...", label, len(uids), days)

    spam_ids = []
    checked = 0
    trashed_details = []
    for uid in uids:
        if should_exit():
            logger.warning("  TIMEOUT")
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
                trashed_details.append(f"{sender} | {subject}")
                logger.info("  [SPAM] %-45s | %s", sender[:45], subject[:50])
        except Exception as e:
            logger.warning("Message fetch error: %s", e)
            continue

    trashed = 0
    if spam_ids:
        logger.info("  Trashing %d...", len(spam_ids))
        for uid in spam_ids:
            if should_exit():
                break
            try:
                mail.copy(uid, "[Gmail]/Trash")
                mail.store(uid, "+FLAGS", "\\Deleted")
                trashed += 1
            except Exception as e:
                logger.error("    ERR: %s", e)
        mail.expunge()
    else:
        logger.info("  %s: Clean.", label)

    mail.close()
    mail.logout()
    return checked, trashed, trashed_details


def sweep_one(email_addr: str) -> tuple[int, int, int, int, list]:
    if should_exit():
        logger.warning("  GLOBAL TIMEOUT - skipping account")
        return 0, 0, 0, 0, []
    logger.info("\n%s\nAccount: %s\n%s", "="*50, email_addr, "="*50)

    env_pass = get_password(email_addr)
    if not env_pass:
        logger.warning("  SKIP: password not found (env var or .gmail_accounts.json)")
        return 0, 0, 0, 0, []

    # Inbox: tight limits to stay under cron timeout (8 min max)
    inbox_max = 60 if "compjunkie" in email_addr else 40
    c_inbox, t_inbox, inbox_details = sweep_folder(email_addr, env_pass, "INBOX", "INBOX", inbox_max)
    time.sleep(0.5)

    # Spam folder: smaller cap since Spam is already filtered by Gmail
    c_spam, t_spam, spam_details = sweep_folder(email_addr, env_pass, "[Gmail]/Spam", "Spam", 40)

    # Tag details with account
    details = [{"account": email_addr, "sender": d.split(" | ")[0], "subject": d.split(" | ", 1)[1]} for d in (inbox_details + spam_details)]

    return c_inbox, t_inbox, c_spam, t_spam, details


if __name__ == "__main__":
    target = os.environ.get("GMAIL_ACCOUNT", "").strip()
    total_c_inbox = 0
    total_t_inbox = 0
    total_c_spam = 0
    total_t_spam = 0
    all_trashed = []  # List of dicts: {account, sender, subject}

    if target and target in ACCOUNTS:
        ci, ti, cs, ts, details = sweep_one(target)
        total_c_inbox += ci; total_t_inbox += ti
        total_c_spam += cs; total_t_spam += ts
        all_trashed.extend(details)
    else:
        for email_addr in ACCOUNTS.keys():
            if should_exit():
                logger.warning("\n  GLOBAL TIMEOUT")
                break
            ci, ti, cs, ts, details = sweep_one(email_addr)
            total_c_inbox += ci; total_t_inbox += ti
            total_c_spam += cs; total_t_spam += ts
            all_trashed.extend(details)
            time.sleep(1)

    # Write trashed details to persistent log
    LOG_FILE = os.path.join(os.path.dirname(__file__), ".spam_sweep_trashed.json")
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "trashed_count": total_t_inbox + total_t_spam,
                "trashed": all_trashed
            }, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning("Could not write trashed log: %s", e)

    logger.info("\n%s\nDone. Inbox: checked ~%d, trashed %d.\n      Spam:  checked ~%d, trashed %d.\n      (%.1fs)\n%s",
        "="*50, total_c_inbox, total_t_inbox, total_c_spam, total_t_spam,
        time.time()-START_TIME, "="*50)
