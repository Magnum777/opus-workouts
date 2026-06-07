with open('scripts/gmail_spam_sweep_v2.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add Tonya patterns to DATING set
old = '"bored and lonely", "looking for fun",'
new = '"bored and lonely", "wanting a crazy night", "wants a crazy night", "wanting a wild night", "wants a wild night", "wanting some fun", "wants some fun", "wants to party", "wanting to party", "looking for fun",'
text = text.replace(old, new)

# Add to RE_SEXUAL regex
old2 = 'available tonight|bored and lonely|looking for fun|reply for pics|'
new2 = 'available tonight|wanting a crazy night|wants a crazy night|wanting a wild night|wants a wild night|wanting some fun|wants some fun|wants to party|wanting to party|bored and lonely|looking for fun|reply for pics|'
text = text.replace(old2, new2)

# Also add to RE_FAKE_SENDER
old3 = 'sexy|horny|booty|nibble|bedroom|scoop|hot tonight|are you single|'
new3 = 'sexy|horny|booty|nibble|bedroom|scoop|hot tonight|wanting a crazy night|wants a crazy night|are you single|'
text = text.replace(old3, new3)

with open('scripts/gmail_spam_sweep_v2.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Tonya patterns added')
