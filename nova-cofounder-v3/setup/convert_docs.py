#!/usr/bin/env python3
"""Convert .md files to HTML and PDF (via pdfkit + wkhtmltopdf)."""

import markdown
import os
from pathlib import Path

BASE = Path(__file__).parent.parent / "docs"
STYLE = BASE / "nova-style.css"
WKHTML = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

def md_to_html(md_path, html_path, title="Nova AI Cofounder V3"):
    """Convert markdown to styled HTML."""
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    html_body = md.convert(md_text)
    
    css = ""
    if STYLE.exists():
        with open(STYLE, "r", encoding="utf-8") as f:
            css = f.read()
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  HTML: {md_path.name}")

def html_to_pdf(html_path, pdf_path):
    """Convert HTML to PDF via pdfkit (wkhtmltopdf) — no headers/footers."""
    try:
        import pdfkit
    except ImportError:
        print(f"  PDF skipped: Install pdfkit (`pip install pdfkit`)")
        return False
    
    options = {
        'page-size': 'A4',
        'margin-top': '20mm',
        'margin-right': '15mm',
        'margin-bottom': '20mm',
        'margin-left': '15mm',
        'encoding': 'UTF-8',
        'enable-local-file-access': None,
        'print-media-type': None,
    }
    
    config = pdfkit.configuration(wkhtmltopdf=WKHTML)
    
    try:
        pdfkit.from_file(str(html_path), str(pdf_path), options=options, configuration=config)
        if pdf_path.exists():
            print(f"  PDF:  {pdf_path.name}")
            return True
    except Exception as e:
        print(f"  PDF failed: {pdf_path.name} — {e}")
    
    return False

def main():
    print("=== Converting Markdown to HTML + PDF ===")
    
    # PDF docs
    pdf_dir = BASE / "PDF"
    if pdf_dir.exists():
        print("\nPDF Docs:")
        for md_file in sorted(pdf_dir.glob("*.md")):
            base = md_file.stem
            html_path = pdf_dir / f"{base}.html"
            pdf_path = pdf_dir / f"{base}.pdf"
            
            md_to_html(md_file, html_path)
            html_to_pdf(html_path, pdf_path)
    
    # Video scripts
    video_dir = BASE / "video-scripts"
    if video_dir.exists():
        print("\nVideo Scripts:")
        for md_file in sorted(video_dir.glob("*.md")):
            base = md_file.stem
            html_path = video_dir / f"{base}.html"
            md_to_html(md_file, html_path, title="Nova V3 Video Script")
    
    print("\nDone.")

if __name__ == "__main__":
    main()
