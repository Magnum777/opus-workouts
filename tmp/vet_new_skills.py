import os
import json

# All 20 new skills installed today
new_skills = [
    "wordpress-api-pro", "youtube-transcript-native-node", "browser-auto-plus",
    "humanized-writing-editor", "factual-claim-verifier", "agentmail-integration",
    "process-interviewer", "wordpress-remote-news-publisher", "evalanche",
    "doc-weaver", "resend-send-native-node", "cold-email-engine",
    "humanizer", "proactive-agent", "skill-vetter", "free-ride",
    "desktop-control", "playwright-browser-automation", "ontology",
]

RED_FLAGS = [
    "curl", "wget", "urllib.request.urlopen", "requests.post",
    "eval(", "exec(", "base64.b64decode", "subprocess.run",
    "os.system", "~/.ssh", "~/.aws", "MEMORY.md", "USER.md",
    "SOUL.md", "IDENTITY.md", "credentials", "token", "api_key",
    "password", "secret", "sudo", "chmod 777", "rm -rf /"
]

print("="*70)
print("SKILL VETTER REPORT — 20 Newly Installed Skills")
print("="*70)

for skill in new_skills:
    skill_dir = f"skills/{skill}"
    if not os.path.exists(skill_dir):
        print(f"\n{skill}: NOT FOUND")
        continue
    
    print(f"\n{'='*70}")
    print(f"Skill: {skill}")
    print(f"{'='*70}")
    
    # Check origin
    origin_file = f"{skill_dir}/.clawhub/origin.json"
    if os.path.exists(origin_file):
        with open(origin_file) as f:
            origin = json.load(f)
        print(f"Author: {origin.get('author', 'N/A')}")
        print(f"Version: {origin.get('version', 'N/A')}")
        print(f"Downloads: {origin.get('downloads', 'N/A')}")
    
    # Review files
    red_flags_found = []
    files_reviewed = 0
    suspicious_network = False
    credential_access = False
    eval_usage = False
    
    for root, dirs, files in os.walk(skill_dir):
        for file in files:
            if file.endswith(('.md', '.json', '.txt', '.py', '.js', '.mjs', '.sh', '.yml', '.yaml')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    files_reviewed += 1
                    
                    for flag in RED_FLAGS:
                        if flag in content.lower():
                            # Context check — skip false positives
                            if flag in ['token', 'password', 'secret', 'api_key']:
                                # Only flag if it's reading from env/files, not just mentioning
                                lines = content.split('\n')
                                for line in lines:
                                    if flag in line.lower() and ('os.environ' in line or 'getenv' in line or 'open(' in line or 'read(' in line):
                                        if flag not in [rf[0] for rf in red_flags_found]:
                                            red_flags_found.append((flag, file))
                            else:
                                if flag not in [rf[0] for rf in red_flags_found]:
                                    red_flags_found.append((flag, file))
                except:
                    pass
    
    print(f"Files reviewed: {files_reviewed}")
    
    if red_flags_found:
        print(f"\n[!] RED FLAGS FOUND ({len(red_flags_found)}):")
        for flag, file in red_flags_found:
            print(f"  - '{flag}' in {file}")
    else:
        print(f"\n[OK] No red flags")
    
    # Risk classification
    risk = "LOW"
    if red_flags_found:
        high_risk_flags = ['eval(', 'exec(', 'os.system', 'subprocess.run', '~/.ssh', '~/.aws', 'MEMORY.md', 'USER.md', 'SOUL.md']
        if any(f[0] in high_risk_flags for f in red_flags_found):
            risk = "HIGH"
        else:
            risk = "MEDIUM"
    
    print(f"RISK LEVEL: {risk}")

print(f"\n{'='*70}")
print("VETTING COMPLETE")
print(f"{'='*70}")
