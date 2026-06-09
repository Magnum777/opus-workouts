import fpdf
from pathlib import Path

pdf = fpdf.FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Add Unicode font
pdf.add_font("DejaVu", "", "C:/Windows/Fonts/arial.ttf", uni=True)
pdf.add_font("DejaVu", "B", "C:/Windows/Fonts/arialbd.ttf", uni=True)

md_path = Path("C:/Users/compj/.openclaw/workspace/docs/doctrine_abyssal_grasp_newbie.md")
lines = md_path.read_text(encoding="utf-8").splitlines()

in_code_block = False
code_lines = []

for line in lines:
    stripped = line.strip()

    if stripped.startswith("```"):
        if in_code_block:
            pdf.set_font("DejaVu", "", 8)
            pdf.set_fill_color(245, 245, 245)
            for cl in code_lines:
                if cl.strip():
                    pdf.cell(0, 4, "  " + cl, new_x="LMARGIN", new_y="NEXT", fill=True)
            pdf.ln(1)
            code_lines = []
            in_code_block = False
        else:
            in_code_block = True
        continue

    if in_code_block:
        code_lines.append(line.rstrip())
        continue

    if not stripped:
        pdf.ln(1)
        continue

    if stripped.startswith("# "):
        pdf.set_font("DejaVu", "B", 16)
        pdf.set_text_color(180, 40, 40)
        pdf.cell(0, 10, stripped[2:], new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)
    elif stripped.startswith("## "):
        pdf.set_font("DejaVu", "B", 13)
        pdf.set_text_color(50, 50, 150)
        pdf.cell(0, 7, stripped[3:], new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1)
    elif stripped.startswith("### "):
        pdf.set_font("DejaVu", "B", 11)
        pdf.cell(0, 6, stripped[4:], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    elif stripped.startswith("- ") or stripped.startswith("* "):
        pdf.set_font("DejaVu", "", 9)
        pdf.cell(5, 4, "", new_x="RIGHT", new_y="TOP")
        pdf.cell(0, 4, "- " + stripped[2:], new_x="LMARGIN", new_y="NEXT")
    elif "**" in stripped:
        pdf.set_font("DejaVu", "", 9)
        parts = stripped.split("**")
        for i, part in enumerate(parts):
            if i % 2 == 1:
                pdf.set_font("DejaVu", "B", 9)
            else:
                pdf.set_font("DejaVu", "", 9)
            is_last = (i == len(parts) - 1)
            pdf.cell(0, 4, part, new_x="LMARGIN" if is_last else "RIGHT", new_y="NEXT" if is_last else "TOP")
    else:
        pdf.set_font("DejaVu", "", 9)
        pdf.cell(0, 4, stripped, new_x="LMARGIN", new_y="NEXT")

output_path = "C:/Users/compj/.openclaw/workspace/docs/doctrine_abyssal_grasp_newbie.pdf"
pdf.output(output_path)
print(f"PDF created: {output_path}")
print(f"File size: {Path(output_path).stat().st_size} bytes")
