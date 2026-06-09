import fpdf
from pathlib import Path

def render_markdown(pdf, md_text, header_color=(180, 40, 40), h2_color=(50, 50, 150)):
    lines = md_text.splitlines()
    in_code_block = False
    code_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                pdf.set_font("DejaVu", "", 7)
                pdf.set_fill_color(245, 245, 245)
                for cl in code_lines:
                    if cl.strip():
                        pdf.cell(0, 3.5, "  " + cl, new_x="LMARGIN", new_y="NEXT", fill=True)
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

        if stripped.startswith("# ") and not stripped.startswith("## "):
            pdf.set_font("DejaVu", "B", 16)
            pdf.set_text_color(*header_color)
            pdf.cell(0, 10, stripped[2:], new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1)
        elif stripped.startswith("## "):
            pdf.set_font("DejaVu", "B", 13)
            pdf.set_text_color(*h2_color)
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
        elif stripped.startswith("| ") and " | " in stripped:
            # Skip table formatting lines (---|---|---)
            if "---" in stripped:
                continue
            pdf.set_font("DejaVu", "", 8)
            # Simple table row rendering
            cols = [c.strip() for c in stripped.split("|")]
            cols = [c for c in cols if c]  # Remove empty
            col_width = 190 / max(len(cols), 1)
            for i, col in enumerate(cols):
                is_header = col.replace(" ", "").replace("-", "").isalpha() and len(col) < 30 and i == 0
                if is_header:
                    pdf.set_font("DejaVu", "B", 8)
                else:
                    pdf.set_font("DejaVu", "", 8)
                pdf.cell(col_width, 4, col, new_x="RIGHT", new_y="TOP", border=1)
            pdf.ln(4)
        elif "**" in stripped:
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


# Create PDF
pdf = fpdf.FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Add Unicode fonts
pdf.add_font("DejaVu", "", "C:/Windows/Fonts/arial.ttf")
pdf.add_font("DejaVu", "B", "C:/Windows/Fonts/arialbd.ttf")

# === PAGE 1: COVER ===
pdf.add_page()
pdf.set_font("DejaVu", "B", 24)
pdf.set_text_color(180, 40, 40)
pdf.cell(0, 30, "", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 15, "ABYSSAL GRASP v2", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("DejaVu", "B", 16)
pdf.set_text_color(50, 50, 150)
pdf.cell(0, 10, "T1 Cruiser Brawler Doctrine", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.cell(0, 10, "vs. Dual-Prop Armor Kikimora Fleets", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("DejaVu", "", 11)
pdf.set_text_color(80, 80, 80)
pdf.cell(0, 30, "", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, "Kybernauts Clade | Doctrine Manual", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.cell(0, 8, "Updated 2026-06-01", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_text_color(0, 0, 0)

# Add separator
pdf.set_draw_color(180, 40, 40)
pdf.set_line_width(1)
pdf.line(20, 130, 190, 130)

pdf.set_font("DejaVu", "B", 12)
pdf.cell(0, 20, "", new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 8, "CONTENTS", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.set_font("DejaVu", "", 10)
pdf.cell(0, 6, "Part I: Threat Analysis & Advanced Doctrine", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.cell(0, 6, "Part II: Newbie Edition - T1 Budget Fits", new_x="LMARGIN", new_y="NEXT", align="C")
pdf.cell(0, 6, "Fits, Tactics, Math & Training Paths", new_x="LMARGIN", new_y="NEXT", align="C")

# === PART I: Advanced Doctrine ===
pdf.add_page()
pdf.set_font("DejaVu", "B", 18)
pdf.set_text_color(180, 40, 40)
pdf.cell(0, 12, "PART I: THREAT ANALYSIS & ADVANCED DOCTRINE", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(3)

v2_path = Path("C:/Users/compj/.openclaw/workspace/docs/doctrine_abyssal_grasp_v2.md")
v2_text = v2_path.read_text(encoding="utf-8")
render_markdown(pdf, v2_text)

# === PART II: Newbie Edition ===
pdf.add_page()
pdf.set_font("DejaVu", "B", 18)
pdf.set_text_color(180, 40, 40)
pdf.cell(0, 12, "PART II: NEWBIE EDITION", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(3)

newbie_path = Path("C:/Users/compj/.openclaw/workspace/docs/doctrine_abyssal_grasp_newbie.md")
newbie_text = newbie_path.read_text(encoding="utf-8")
render_markdown(pdf, newbie_text, header_color=(40, 120, 40), h2_color=(50, 100, 50))

# Output
output_path = "C:/Users/compj/.openclaw/workspace/docs/doctrine_abyssal_grasp_complete.pdf"
pdf.output(output_path)
print(f"PDF created: {output_path}")
print(f"File size: {Path(output_path).stat().st_size:,} bytes")
