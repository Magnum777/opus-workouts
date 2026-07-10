import re, os

files = [
    r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\publisher_v3.py',
    r'C:\Users\compj\.openclaw\workspace\scripts\content-nova\featured_image.py',
]

for path in files:
    with open(path, 'r') as f:
        text = f.read()
    text = re.sub(r"('pass': )<SCRUBBED_WORDPRESS_APP_PASSWORD>(,?)", r"\1'placeholder_password'\2", text)
    with open(path, 'w') as f:
        f.write(text)
    print(f'Fixed {os.path.basename(path)}')
