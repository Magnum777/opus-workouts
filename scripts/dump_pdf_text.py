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
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            print("--- Page", i + 1, "---")
            print(text)
            print()
