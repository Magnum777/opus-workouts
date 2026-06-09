from pypdf import PdfReader

path = r"C:\Users\compj\.openclaw\media\inbound\STIG_APPIAN_Completed_Checklist---a6a8628a-9cd4-462c-b4c9-c289fc140ab8.pdf"
r = PdfReader(path)

# Check for form fields
fields = r.get_fields()
if fields:
    print(f"Found {len(fields)} form fields")
    for name, field in list(fields.items())[:30]:
        val = field.get("/V", "(empty)")
        print(f"  {name}: {val}")
else:
    print("No form fields found")

# Search pages for our V-IDs
targets = ["V-222411", "V-222432", "V-222520", "V-222536"]
for i, page in enumerate(r.pages):
    text = page.extract_text()
    if text and any(v in text for v in targets):
        print(f"--- Page {i+1} contains target V-IDs ---")
        # Extract a window around each V-ID
        for vid in targets:
            idx = text.find(vid)
            if idx != -1:
                start = max(0, idx - 200)
                end = min(len(text), idx + 800)
                print(f"\n>>> {vid}:\n{text[start:end]}")
        print("\n")
