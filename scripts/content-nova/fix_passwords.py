import os

files = [
    r"C:\Users\compj\.openclaw\workspace\scripts\content-nova\publisher_v3.py",
    r"C:\Users\compj\.openclaw\workspace\scripts\content-nova\publisher.py",
    r"C:\Users\compj\.openclaw\workspace\scripts\content-nova\featured_image.py",
]

for path in files:
    with open(path, 'r') as f:
        lines = f.readlines()
    
    in_aitoolalliance = False
    in_aibusinessinsider = False
    
    for i, line in enumerate(lines):
        if "'aitoolalliance.com':" in line:
            in_aitoolalliance = True
            in_aibusinessinsider = False
        elif "'aibusinessinsider.org':" in line:
            in_aitoolalliance = False
            in_aibusinessinsider = True
        elif "'aicofounderstack.com':" in line:
            in_aitoolalliance = False
            in_aibusinessinsider = False
        elif "'pass': 'placeholder_password'" in line:
            if in_aitoolalliance:
                lines[i] = line.replace("'placeholder_password'", "'PXop SzVQ b6wX IAyr FSig 8ZfL'")
                print(f"Fixed aitoolalliance pass in {os.path.basename(path)}")
            elif in_aibusinessinsider:
                lines[i] = line.replace("'placeholder_password'", "'sDLx Ja22 YxcI QAok gu8u xRXI'")
                print(f"Fixed aibusinessinsider pass in {os.path.basename(path)}")
    
    with open(path, 'w') as f:
        f.writelines(lines)

print("Done.")
