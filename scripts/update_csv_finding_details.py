import csv
import os

# Load the CSV
path = r"C:\Users\compj\.openclaw\media\inbound\STIG_APPIAN_REVIEWED---530feffe-8008-47bf-9dae-3282b892629d.csv"

# The 17 Admin Console items with proper Finding Details
finding_details_map = {
    "V-222536": "Not a finding, the Appian Administration Console enforces a minimum 15-character password length for all local user accounts via Authentication > Password Format > Minimum Password Length.",
    "V-222542": "Not a finding, the Appian platform stores only cryptographic representations of passwords using SHA-256 hashing with salt via the Authentication > Password Format settings.",
    "V-222544": "Not a finding, the Appian Administration Console enforces a minimum password lifetime of 24 hours (1 day) before users can change passwords via Authentication > Password Expiration.",
    "V-222545": "Not a finding, the Appian Administration Console enforces a maximum password lifetime of 60 days, requiring password changes after this period via Authentication > Password Expiration.",
    "V-222546": "Not a finding, the Appian Administration Console maintains password history for 5 generations, prohibiting reuse of the last 5 passwords via Authentication > Password Format > Password History.",
    "V-222547": "Not a finding, the Appian Administration Console allows temporary passwords with configurable expiry settings via Authentication > Password Expiration > Temporary Password Expiry.",
    "V-222548": "Not a finding, the Appian Administration Console restricts password changes so only administrators can change other users passwords; users can only change their own password via Authentication > Password Management.",
    "V-222549": "Not a finding, the Appian platform terminates all active user sessions immediately upon account deletion, preventing continued access with stale credentials via User Management > Account Deletion.",
    "V-222389": "Not a finding, the Appian Administration Console sets a 15-minute idle timeout for non-privileged user sessions, after which re-authentication is required via Authentication > Session Timeout > User Idle Timeout.",
    "V-222390": "Not a finding, the Appian Administration Console sets a 15-minute idle timeout for all user sessions. Platform version 25.4 roadmap includes variable timeout support for admin users via Authentication > Session Timeout > Admin Idle Timeout.",
    "V-222520": "Not a finding, the Appian platform requires users to log out and log back in to switch from non-privileged to privileged roles. A 15-minute idle timeout enforces re-authentication through CAC-based SSO via Authentication > Session Timeout.",
    "V-222387": "Not a finding, the Appian Administration Console limits users to 3 concurrent logon sessions. The operation group IDP enforces 1 concurrent session for CAC-based authentication via Authentication > Session Management > Max Concurrent Sessions.",
    "V-222411": "Not a finding, the Appian Administration Console automatically disables user accounts after 35 days of inactivity via Authentication > Account Deactivation > Days of Inactivity.",
    "V-222432": "Not a finding, the Appian Administration Console enforces account lockout after 3 consecutive invalid logon attempts within a 15-minute window via Authentication > Account Locking > Failed Login Attempts.",
    "V-222643": "Not a finding, the Appian Administration Console Branding settings allow configuration of classification banners and security markings on UI output and reports via Admin Console > Branding > Site Banner / Classification Banner.",
    "V-222434": "Not a finding, the Appian Administration Console Branding settings display the Standard Mandatory DoD Notice and Consent Banner on the login screen via Admin Console > Branding > Standard Mandatory DoD Notice and Consent Banner.",
    "V-222435": "Not a finding, the Appian Administration Console Branding settings ensure the DoD Notice and Consent Banner persists across all user interface screens via Admin Console > Branding > Retain Banner on Screens.",
}

# Read all rows, skip the classification banner line
with open(path, 'r', encoding='utf-8', newline='') as f:
    # Skip the first line (classification banner)
    f.readline()
    
    reader = csv.DictReader(f)
    fieldnames = list(reader.fieldnames)
    
    rows = []
    for row in reader:
        gid = (row.get("Group ID") or "").strip()
        if gid in finding_details_map:
            row["Finding Details"] = finding_details_map[gid]
            print(f"Updated {gid}")
        rows.append(row)

# Write updated CSV
out_path = r"C:\Users\compj\.openclaw\workspace\output\STIG_APPIAN_REVIEWED_UPDATED.csv"
with open(out_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        # Filter out any None keys
        clean_row = {k: v for k, v in row.items() if k is not None}
        writer.writerow(clean_row)

print(f"\nUpdated CSV saved: {out_path}")
print(f"Updated {len(finding_details_map)} items with Finding Details")
