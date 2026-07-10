import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from vault_helper import get_credential

files = [
    r"C:\Users\compj\.openclaw\workspace\scripts\content-nova\publisher_v3.py",
    r"C:\Users\compj\.openclaw\workspace\scripts\content-nova\publisher.py",
    r"C:\Users\compj\.openclaw\workspace\scripts\content-nova\featured_image.py",
]

aitool_pass = get_credential('wordpress', 'aitoolalliance_pass')
aibi_pass = get_credential('wordpress', 'aibusinessinsider_pass')

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
                lines[i] = line.replace("'placeholder_password'", repr(aitool_pass))
                print(f"Fixed aitoolalliance pass in {os.path.basename(path)}")
            elif in_aibusinessinsider:
                lines[i] = line.replace("'placeholder_password'", repr(aibi_pass))
                print(f"Fixed aibusinessinsider pass in {os.path.basename(path)}")
    
    with open(path, 'w') as f:
        f.writelines(lines)

print("Done.")
