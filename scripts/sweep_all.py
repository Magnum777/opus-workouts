import imaplib, email, re, os, sys
from datetime import datetime, timedelta

ACCOUNTS = ['compjunkie@gmail.com', 'jhenderson87@gmail.com', 'layeredmediallc@gmail.com', 'nova.cofounder@gmail.com']
PW_VARS = {
    'compjunkie@gmail.com': 'GMAIL_APP_PASSWORD_COMPJUNKIE',
    'jhenderson87@gmail.com': 'GMAIL_APP_PASSWORD_JHENDERSON',
    'layeredmediallc@gmail.com': 'GMAIL_APP_PASSWORD_LAYEREDMEDIA',
    'nova.cofounder@gmail.com': 'GMAIL_APP_PASSWORD_NOVA'
}

SPAM_DOMAINS = {'foxytemptation.com','arousingdates.com','vallyme.com','vovadis.vip','newpinoko.com','freepinoko.com','pirinoet.vip','iwhaa.com','iflirts.com','i-flirt-s.com','datingapphub.com','thesoberdating.com','carpetani.vip','teaseeasyx.com','freeyvenas.com','unclegus.org','somiramana.com','mydatematches.com','elfaroukegypt.com','gohoha.org','uslaka.com','truebootycall.com','wonderko.com','youlaka.com','paoloko.com','arastopi.com','toproh.com','lolyg.com','tonyxo.com','allroxo.com','tutigroup.org','rokoinfo.com','locbelowon.org','undwer.com','monloly.com','prayst.com','ynarounda.com','mybelski.org','karinsas.com','irisermita.org','hostermita.org','theermita.org','xolashop.com','roxous.com','autoroh.com','nilona.org','newdidi.top','locatedwell.com','freeynina.com','renitini.com','sepoffa.com','cuteyoungladies.com','faithfulfling.com','hotrdv.com','hornyaffairs.com','pumpyjoy.com','locataway.org','hostsoli.com','tuvovana.com','dialuxas.ru','covisianmail.com','traveltrackerbd.com','moe-dl.edu.my','chicagoinstituteofbusiness.com','chicagoinstituteofbusiness.online','cibnotifications.com','markethair','fivv.pp.ua','xqiyegt','hireevonline','open-hosted.com','vtbrpsgnrwcdulcvpq','adultcrush.com','bilorina.com','sarawaka.com','qoez.org','webvova.vip','yninarow.com','itvoly.com','elalina.vip','freesapa.com','andavtis.com','carmenko.com','elitemarine.com.br','mixcloudmail.com','roxoweb.com','hostroh.com','cupidconnectnag.ru','kisswisp.ru','meetglownow.ru','romanticluster.ru','greatxdatefinder.com','hellopromo.info','soontoday.info','freshday.info','flirtwiththestars.com','checkoutgirlsnow.com','heytherelab.com','thexdate.net'}
RE_SEXUAL = re.compile(r'hottie|booty|nibble|bedroom|scoop|stretched|oral|fixation|can we make love|naked|nude|horny|porn|xxx|sexy|dtf|hookup|casual sex|adult dating|hot affair|sexy singles|play with me|available tonight|bored and lonely|looking for fun|reply for pics|click to see|view profile|spice it up|trouble in the best way|bet you.*trouble|wanna chat|feel like talking|just relocated|love some help|onlyfans|fansly|hot.*milf|iflirt|flirt|flirty|booty shorts|flirty dm|flirty note|flirty photos|flirty message|touching (myself|herself|himself)|is touching|dating|night\s*alert|tabl-', re.I)
RE_FAKE = re.compile(r'telegram|whatsapp|signal\s*<|discord\s*<|messenger\s*<|direct\s*<|missedcall|new\s*match|iwant|naughty|tabl-|hottie|porn|xxx|naughty|sexy|horny|booty|nibble|bedroom|scoop', re.I)
CORE_BAD = {'sex','fuck','cock','cum','pussy','dick','penis','vagina','clit','anal','blowjob','handjob','creampie','deepthroat','gangbang','bukkake','squirt','threesome','orgy','swingers','bdsm','fetish','kink','kinky','dominatrix','nudity','erotic','erotica','nsfw','seductive','passionate','steamy','breasts','naked','nude'}
DATING = {'wants to meet you','likes your profile','feels the attraction','someone likes you','private message received','new message from','desires you','hookup','dtf','nsa','fwb','friends with benefits','casual sex','adult dating','online flirting','meet local','local babes','choose the girl','start chatting','waiting to connect','new match','private match','feel your breasts','soft for your fingers','meet her before bed','get to know you','spice it up','hot affair','sexy singles','i want hookups','iflirts','play with me','available tonight','bored and lonely','looking for fun','reply for pics','click to see','view profile','claim your','you won','free gift','act now','missed call','unread message','instagram direct','reply to an important message','friends in private chat','she dares you','she checked your profile','her message can\'t wait','she\'s hoping you\'ll open','tonight you have a choice','instant connections','no filters','confirm your email','urgent confirm','hello compjunkie','re: compjunkie','i finally found you','group chat','i have a confession','drop your pants','your name came to mind','your body can always light my fire','coffee break','sybian rides','i\'m easy to rev up','wait one second before you go','eyes only','no pressure, just happy feelings','ass fantasies','my boobs are begging','what we\'d be like','when if not now','who\'s the boss','size and proportions','noble professions','anything you want, i can do','down-to-earth girl wants you','don\'t let this mood pass you by','i\'m convinced, i love you','iz it u i saw today','what u like in bed','friendly wink','found something cool','curious about what you\'d like','hey stranger','call me','great listener','relations with alt-girl','my heart beats faster','i like men having the upper hand','quick fix','milf looking for','got her snap after lunch','someone wants to talk with you','being sweet while you rail me','i\'m fun loving and lover of fun','i\'m new here','my smile is a challenge','free option and gets results','being 40 is perfect','you matter to someone','is curious to see more of you','where\'ve you been all this time','she just pinged you','let\'s live a little','someone is curious to know you','i\'m looking for a great time','i want to experiment and enjoy life more','life without love','i wish you were here','my fantasy is to be with you','these girls have a certain pull','beautiful chinese girls want to chat','do you know how to have a good time','want to partner up and have some fun','ask me out','message from mortar','someone reading','lisa online near','you ready','straight up','you busy this week','oral fixation','me? an oral fixation? yes','samara is now following you','can we make love','without any obligations','i found you on facebook','great pic','luv69','the deeper truth of attraction','so about that site','met her','females show a lot of tricks','online spectators','females show','tricks to online spectators','costco meat box','ready to ship','your costco meat box','great steaks sampler','omaha steaks','nationwide carry for military','bill for nationwide carry','order verification notice','verification notice','inquiry','order - verification notice','nerve fresh','relief from tingling','i\'m having a break','let\'s open up new frontiers','i know you want it','lick my','hi, wanna chat','anytime you feel like talking','just relocated here','would love some help','here for you','new here and','shower together','incredibly nice inside','makes me incredibly','several members are trying to reach you','just messaged you','landed in your inbox','wondering how you look like','working out in the bedroom','real mature woman','strip me','from that site','want to see what i\'m doing','she\'s sharing something','she made something you should see','enjoy premium access','thanks for joining','post a comment on your wall','compjunkie hi','you\'ll like this','quick question before i disappear','passing this to you','photos i\'ve kept to myself','authentic platform','did you manage to find','sent you a follow request','notification from','she said yes','said yes','connected with','a new message to read','bet you\'re trouble','trouble in the best way','you\'re trouble','wanna chat','feel like talking','just relocated','love some help','fast & flirty','flirty flings','flirty edition','flirty connection','flirty dm','flirty note','flirty photos','flirty message','flirty and','fun and flirty','sent a flirty','is touching herself','is touching himself','touching myself','match update:','deletes in','sent message'}
LEGIT = {'discord.com','google.com','microsoft.com','apple.com','amazon.com','github.com','kickstarter.com','xbox.com','windycitycigars.com','cigarsinternational.com','olivegarden.com','krispykreme.com','audible.com','spotify.com','tubitv.com','caswellmassey.com','zennioptical.com','ulta.com','marcos.com','dunkinrewards.com','chick-fil-a.com','starbucks.com','texasroadhouse.com','regions.com','steampowered.com','borisfx.com','ubiquiti.com','plex.tv','googleplay.com','myq.com','uber.com','shoecarnival.com','limitedrungames.com','scentbird.com','sephora.com','shutterfly.com','zulily.com','empiresofeve.com','churchcenter.com','sojourn.church','georgiapacking.org','cigaraficionado.com','greentoe.com','qalo.com','vevor.com','chewy.com','dominos.com','papajohns.com','walmart.com','bestbuy.com','target.com','costco.com','lowes.com','bjswholesaleclub.com','homedepot.com','nbc.com','nbcsports.com','twitch.tv','wizards.com','experian.com','canva.com','lg.com','samsung.com','disneypinnacle.com','ifttt.com','m.starbucks.com','e.olivegarden.com','email.chick-fil-a.com','e-rewards.dominos.com','dough.papajohns.com','promo.newegg.com','microcenter.com','email.microcenter.com','mail.scentbird.com','updates.scentbird.com','geologia.unam.mx','unam.mx','ptit.edu.vn','stu.ptit.edu.vn','correo.chapingo.mx','cosbrizal.edu.ph','maristascomayagua.edu.hn','binus.ac.id','moe.gov.sa','rb.moe.gov.sa','eng.zu.edu.eg','lcps.org.uk','notredameacademy.org','an.em-net.ne.jp','dolphin.ocn.ne.jp','ocn.ne.jp','estudiantes.uv.mx','web.de','paypal.com','chase.com','tiktok.com'}

def is_spam(sender, subject):
    sender=sender.lower(); subject=subject.lower()
    for dom in LEGIT:
        if dom in sender: return False
    for d in SPAM_DOMAINS:
        if d in sender: return True
    if RE_FAKE.search(sender): return True
    if RE_SEXUAL.search(sender) or RE_SEXUAL.search(subject): return True
    combined = sender + ' ' + subject
    if re.search(r'anytime you feel like talking|just relocated|would love some help', combined, re.I): return True
    if re.search(r'key to your entry|entry now|click here|open this', subject, re.I): return True
    if 'verification code' in subject:
        legit_code_senders = {'paypal.com','chase.com','google.com','microsoft.com','amazon.com','apple.com','discord.com','eveonline'}
        if not any(s in sender for s in legit_code_senders): return True
    if re.search(r'claim your prize|congratulations.*won|you.*won|click to claim', subject, re.I): return True
    if re.search(r'beach reward|your .* is here|free.*gift', subject, re.I):
        if not any(d in sender for d in LEGIT): return True
    for w in CORE_BAD:
        if w in subject: return True
    for w in DATING:
        if w in subject: return True
    if re.search(r'@(gmail|hotmail|outlook)\.com', sender) and any(w in subject for w in DATING): return True
    return False

results = {}
for addr in ACCOUNTS:
    pw_var = PW_VARS[addr]
    pw = os.environ.get(pw_var, '').strip()
    if not pw:
        results[addr] = (0, 0, 'no password')
        print(f'{addr}: no password')
        continue
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com', timeout=15)
        mail.login(addr, pw)
    except Exception as e:
        results[addr] = (0, 0, f'login failed: {e}')
        print(f'{addr}: login failed: {e}')
        continue
    mail.select('INBOX')
    since = (datetime.now() - timedelta(days=14)).strftime('%d-%b-%Y')
    _, data = mail.search(None, f'(SINCE {since})')
    ids = data[0].split()[-100:] if data[0] else []
    print(f'{addr}: checking {len(ids)} messages')
    spam_ids=[]; checked=0
    for uid in ids:
        try:
            _, msg_data = mail.fetch(uid, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])')
            if not msg_data or not msg_data[0]: continue
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            s = msg.get('From',''); subj = msg.get('Subject','')
            checked += 1
            if is_spam(s, subj):
                spam_ids.append(uid)
        except: pass
    if spam_ids:
        for uid in spam_ids:
            try:
                mail.copy(uid, '[Gmail]/Trash')
                mail.store(uid, '+FLAGS', '\\Deleted')
            except: pass
        mail.expunge()
    results[addr] = (checked, len(spam_ids), 'ok')
    print(f'{addr}: checked {checked}, spam {len(spam_ids)}')
    mail.close(); mail.logout()
    import time; time.sleep(1)

print()
for addr in ACCOUNTS:
    c, t, status = results[addr]
    print(f'{addr}: checked ~{c}, trashed {t}')
