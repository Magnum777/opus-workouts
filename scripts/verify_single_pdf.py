from pypdf import PdfReader
import os

p = r"C:\Users\compj\.openclaw\workspace\output\Appian_ASD_STIG_V6R4_4_Targets_Evidence_Package_2026-06-02.pdf"
reader = PdfReader(p)

print(f"Total pages: {len(reader.pages)}\n")
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
        print(f"{'='*60}")
        print(f"PAGE {i+1}")
        print(f"{'='*60}")
        print(text)
        print()
