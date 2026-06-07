with open('scripts/gmail_spam_sweep_v2.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add new DATING patterns
old = '"wanting to party", "looking for fun",'
new = '"wanting to party", "pull me by my hair", "sexy lingerie", "dance on the pylon", "stripper", "multiple orgasms", "turns me on", "asking for more photos", "find someone special", "looking for fun",'
text = text.replace(old, new)

# Add weight loss scam patterns
old2 = '"send money", "need $", "broke and",'
new2 = '"send money", "need $", "broke and", "pounds in 15 days", "pounds in 30 days", "GLP-1", "GetThin", "3-min assessment", "Lose Weight Sooner", "medically qualif", "no insurance needed", "prescription is ready", "Get approved",'
text = text.replace(old2, new2)

# Add fake reward patterns
old3 = '"debt relief", "debt consolidation", "credit repair",'
new3 = '"debt relief", "debt consolidation", "credit repair", "Free YETI", "Free Fresh Tuna", "Free Walmart Food", "won a Bauer", "dash cam", "Free Beach Lounge", "Combo Kit",'
text = text.replace(old3, new3)

# Add fake insurance/talcum patterns
old4 = '"student loan forgiveness", "loan forgiveness",'
new4 = '"student loan forgiveness", "loan forgiveness", "Talcum Powder", "Last Reminder", "Pending Confirmation", "have you or loved one", "used Talcum",'
text = text.replace(old4, new4)

# Add to RE_SEXUAL
old5 = 'sexy man|attractive|gorgeous|beautiful|stunning|'
new5 = 'sexy man|attractive|gorgeous|beautiful|stunning|pull me by my hair|sexy lingerie|dance on the pylon|stripper|multiple orgasms|turns me on|asking for more photos|find someone special|'
text = text.replace(old5, new5)

with open('scripts/gmail_spam_sweep_v2.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Added spam dump patterns')
