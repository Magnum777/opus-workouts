import re
with open(r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\publisher.py','r') as f:
    text = f.read()
text = re.sub(r"('pass': )<SCRUBBED_WORDPRESS_APP_PASSWORD>(,)", r"\1'placeholder_password'\2", text)
with open(r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\publisher.py','w') as f:
    f.write(text)
print('Fixed publisher.py')
