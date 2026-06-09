from pypdf import PdfReader
import os

paths = [
    r"C:\Users\compj\.openclaw\workspace\output\Appian_ASD_STIG_V6R4_4_Targets_Evidence_Package_2026-06-02.pdf",
    r"C:\Users\compj\.openclaw\workspace\output\Appian_ASD_STIG_V6R4_All_NAF_Evidence_Package_2026-06-02.pdf",
]

for p in paths:
    print("=" * 80)
    print("FILE:", os.path.basename(p))
    print("=" * 80)
    print()
    
    reader = PdfReader(p)
    
    # Check first few pages for HTML tags
    has_html = False
    for i, page in enumerate(reader.pages[:5]):
        text = page.extract_text()
        if text:
            print(f"--- Page {i+1} ---")
            print(text[:1200])
            print()
            if any(tag in text for tag in ["<b>", "</b>", "<br/>", "<i>", "&lt;", "&gt;"]):
                has_html = True
    
    if has_html:
        print("WARNING: HTML tags still present!")
    else:
        print("OK: No HTML tags detected in sample pages.")
    
    print(f"\nTotal pages: {len(reader.pages)}")
    print()
