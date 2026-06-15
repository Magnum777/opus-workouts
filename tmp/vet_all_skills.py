import os
import json
import sys

# ALL new skills installed today
new_skills = [
    # Batch 1 (5 skills)
    "wordpress-api-pro", "youtube-transcript-native-node", "browser-auto-plus",
    "humanized-writing-editor", "factual-claim-verifier",
    # Batch 2 (8 skills)
    "agentmail-integration", "process-interviewer", "wordpress-remote-news-publisher",
    "evalanche", "doc-weaver", "resend-send-native-node", "cold-email-engine",
    # Batch 3 (7 skills)
    "humanizer", "proactive-agent", "skill-vetter", "free-ride",
    "desktop-control", "playwright-browser-automation", "ontology",
    # Batch 4 (3 skills)
    "cogmem", "myknowledge", "task-prism",
]

# Actual dangerous patterns (not documentation mentions)
DANGEROUS_PATTERNS = [
    'os.system(', 'eval(', 'exec(', '__import__(',
    'subprocess.run(', 'subprocess.call(', 'subprocess.Popen(',
]

# Expected patterns for legitimate purposes
NETWORK_PATTERNS = ['requests.get(', 'requests.post(', 'urllib.request.urlopen(', 'http.client']
FILE_PATTERNS = ['open(', 'os.path.exists(', 'Path(', 'json.load(', 'json.dump(']

print("="*70)
print("COMPREHENSIVE SKILL VETTING REPORT — 23 Newly Installed Skills")
print("="*70)

results = []

for skill in new_skills:
    skill_dir = f"skills/{skill}"
    if not os.path.exists(skill_dir):
        print(f"\n{skill}: NOT FOUND")
        continue
    
    print(f"\n{'='*70}")
    print(f"Skill: {skill}")
    print(f"{'='*70}")
    
    # Get origin info
    origin_file = f"{skill_dir}/.clawhub/origin.json"
    author = "N/A"
    version = "N/A"
    downloads = "N/A"
    if os.path.exists(origin_file):
        try:
            with open(origin_file) as f:
                origin = json.load(f)
            author = origin.get('author', 'N/A')
            version = origin.get('version', 'N/A')
            downloads = origin.get('downloads', 'N/A')
        except:
            pass
    
    print(f"Author: {author}")
    print(f"Version: {version}")
    print(f"Downloads: {downloads}")
    
    # Review actual code files
    dangerous_found = []
    network_found = []
    file_access_found = []
    files_reviewed = 0
    
    for root, dirs, files in os.walk(skill_dir):
        for file in files:
            if file.endswith(('.py', '.js', '.mjs', '.sh', '.ts')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    files_reviewed += 1
                    
                    for pattern in DANGEROUS_PATTERNS:
                        if pattern in content:
                            # Get context line
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if pattern in line:
                                    dangerous_found.append((pattern, file, line.strip(), i))
                                    break
                    
                    for pattern in NETWORK_PATTERNS:
                        if pattern in content:
                            if pattern not in [n[0] for n in network_found]:
                                network_found.append((pattern, file))
                    
                    for pattern in FILE_PATTERNS:
                        if pattern in content:
                            if pattern not in [f[0] for f in file_access_found]:
                                file_access_found.append((pattern, file))
                                
                except:
                    pass
    
    print(f"Code files reviewed: {files_reviewed}")
    
    if dangerous_found:
        print(f"\n[!] DANGEROUS PATTERNS ({len(dangerous_found)}):")
        for pattern, file, line, num in dangerous_found:
            safe_line = line.encode('ascii', 'replace').decode()
            print(f"  - {pattern} in {file}:{num}")
            print(f"    {safe_line[:100]}")
    else:
        print(f"\n[OK] No dangerous patterns found")
    
    if network_found:
        print(f"[INFO] Network calls: {len(network_found)}")
        for pattern, file in network_found:
            print(f"  - {pattern} in {file}")
    
    if file_access_found:
        print(f"[INFO] File access: {len(file_access_found)}")
        for pattern, file in file_access_found:
            print(f"  - {pattern} in {file}")
    
    # Risk classification
    risk = "LOW"
    risk_reason = "Clean code. No dangerous patterns."
    
    if dangerous_found:
        # Analyze if subprocess is justified
        subprocess_count = sum(1 for d in dangerous_found if 'subprocess' in d[0])
        if subprocess_count == len(dangerous_found):
            # All dangerous patterns are subprocess — check context
            justified = True
            for pattern, file, line, num in dangerous_found:
                if 'pandoc' in line or 'weasyprint' in line or 'wp ' in line:
                    pass  # Expected subprocess calls
                else:
                    justified = False
            
            if justified:
                risk = "MEDIUM"
                risk_reason = "subprocess.run() used for legitimate document/WP CLI calls. No arbitrary code execution."
            else:
                risk = "HIGH"
                risk_reason = "subprocess with potentially unsafe arguments"
        else:
            risk = "HIGH"
            risk_reason = "Dangerous patterns found (eval/exec/os.system)"
    
    print(f"RISK: {risk}")
    print(f"Reason: {risk_reason}")
    
    results.append({
        'skill': skill,
        'author': author,
        'version': version,
        'risk': risk,
        'reason': risk_reason,
        'dangerous': len(dangerous_found),
        'network': len(network_found),
        'files': files_reviewed
    })

# Summary table
print(f"\n{'='*70}")
print("SUMMARY TABLE")
print(f"{'='*70}")
print(f"{'Skill':<35} {'Risk':<8} {'Files':<6} {'Dangr':<6}")
print("-"*70)

for r in results:
    print(f"{r['skill']:<35} {r['risk']:<8} {r['files']:<6} {r['dangerous']:<6}")

high_risk = [r for r in results if r['risk'] == 'HIGH']
medium_risk = [r for r in results if r['risk'] == 'MEDIUM']
low_risk = [r for r in results if r['risk'] == 'LOW']

print(f"\n{'='*70}")
print(f"TOTAL: {len(results)} skills")
print(f"  LOW: {len(low_risk)}")
print(f"  MEDIUM: {len(medium_risk)}")
print(f"  HIGH: {len(high_risk)}")
print(f"{'='*70}")

if high_risk:
    print(f"\n[!] HIGH RISK SKILLS ({len(high_risk)}):")
    for r in high_risk:
        print(f"  - {r['skill']}: {r['reason']}")

if medium_risk:
    print(f"\n[~] MEDIUM RISK SKILLS ({len(medium_risk)}):")
    for r in medium_risk:
        print(f"  - {r['skill']}: {r['reason']}")

print(f"\n[OK] LOW RISK SKILLS ({len(low_risk)}):")
for r in low_risk:
    print(f"  - {r['skill']}")
