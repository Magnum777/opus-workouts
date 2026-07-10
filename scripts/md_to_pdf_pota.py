import re
from fpdf import FPDF
import sys

class MarkdownPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font('Arial', '', 11)
        self.in_code_block = False
        self.in_table = False
        self.table_data = []
        self.table_headers = []

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Ham Radio / POTA Promotion Strategy', 0, 0, 'C')
        self.ln(5)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def clean_markdown(text):
    # Remove markdown links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove bold/italic markers
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    # Remove inline code backticks
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Replace unicode dashes/quotes with ASCII
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2022', '*').replace('\u2026', '...')
    # Strip emojis and other unicode symbols
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text.strip()

def convert_md_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pdf = MarkdownPDF()

    # Title page
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 20, 'Ham Radio / POTA', 0, 1, 'C')
    pdf.cell(0, 15, 'YouTube Channel', 0, 1, 'C')
    pdf.cell(0, 15, 'Promotion Strategy', 0, 1, 'C')
    pdf.ln(20)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Prepared: June 28, 2026', 0, 1, 'C')
    pdf.cell(0, 10, 'For: MGRA/CGARC Ham Radio Channel', 0, 1, 'C')
    pdf.add_page()

    lines = content.split('\n')
    i = 0
    in_table = False
    table_rows = []

    while i < len(lines):
        line = lines[i].rstrip()

        # Skip YAML frontmatter
        if i == 0 and line.startswith('---'):
            i += 1
            while i < len(lines) and not lines[i].startswith('---'):
                i += 1
            i += 1
            continue

        # Skip image lines
        if line.startswith('!['):
            i += 1
            continue

        # Horizontal rule
        if line.startswith('---') and len(line.strip()) == 3:
            if in_table:
                render_table(pdf, table_rows)
                in_table = False
                table_rows = []
            pdf.set_draw_color(150, 150, 150)
            pdf.line(15, pdf.get_y() + 3, 195, pdf.get_y() + 3)
            pdf.ln(6)
            i += 1
            continue

        # Code blocks
        if line.startswith('```'):
            if in_table:
                render_table(pdf, table_rows)
                in_table = False
                table_rows = []
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1
            if code_lines:
                pdf.set_font('Courier', '', 9)
                pdf.set_fill_color(245, 245, 245)
                for cl in code_lines:
                    pdf.cell(0, 5, cl[:100], 0, 1, 'L', fill=True)
                pdf.ln(3)
                pdf.set_font('Arial', '', 11)
            continue

        # Tables
        if '|' in line:
            if not in_table:
                in_table = True
                table_rows = []
            # Check if it's a separator line
            if re.match(r'^[\s\-\|]+$', line.replace(' ', '')):
                i += 1
                continue
            cells = [c.strip() for c in line.split('|')]
            cells = [c for c in cells if c]
            if cells:
                table_rows.append(cells)
            i += 1
            # Check if next line is not a table
            if i < len(lines) and '|' not in lines[i]:
                render_table(pdf, table_rows)
                in_table = False
                table_rows = []
            continue
        elif in_table:
            render_table(pdf, table_rows)
            in_table = False
            table_rows = []

        # Headers
        if line.startswith('# ') and not line.startswith('## '):
            pdf.set_font('Arial', 'B', 18)
            pdf.set_text_color(44, 62, 80)
            pdf.ln(5)
            pdf.cell(0, 10, clean_markdown(line[2:]), 0, 1, 'L')
            pdf.set_draw_color(52, 152, 219)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 11)
            i += 1
            continue

        if line.startswith('## '):
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(52, 73, 94)
            pdf.ln(5)
            pdf.cell(0, 8, clean_markdown(line[3:]), 0, 1, 'L')
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 11)
            i += 1
            continue

        if line.startswith('### '):
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(70, 70, 70)
            pdf.ln(3)
            pdf.cell(0, 7, clean_markdown(line[4:]), 0, 1, 'L')
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 11)
            i += 1
            continue

        if line.startswith('#### '):
            pdf.set_font('Arial', 'B', 11)
            pdf.set_text_color(90, 90, 90)
            pdf.cell(0, 6, clean_markdown(line[5:]), 0, 1, 'L')
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 11)
            i += 1
            continue

        # Blockquotes
        if line.startswith('>'):
            if in_table:
                render_table(pdf, table_rows)
                in_table = False
                table_rows = []
            pdf.set_text_color(100, 100, 100)
            pdf.set_font('Arial', 'I', 10)
            quote_text = clean_markdown(line[1:].strip())
            if quote_text:
                pdf.set_x(20)
                pdf.multi_cell(170, 6, quote_text)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Arial', '', 11)
            i += 1
            continue

        # List items
        list_match = re.match(r'^(\s*)[-*]\s+(.*)', line)
        if list_match:
            if in_table:
                render_table(pdf, table_rows)
                in_table = False
                table_rows = []
            indent = len(list_match.group(1))
            text = clean_markdown(list_match.group(2))
            if text:
                pdf.set_x(15 + indent * 3)
                pdf.set_font('Arial', '', 11)
                pdf.cell(5, 6, chr(149), 0, 0)
                pdf.multi_cell(0, 6, text)
            i += 1
            continue

        # Numbered lists
        num_match = re.match(r'^(\s*)\d+\.\s+(.*)', line)
        if num_match:
            if in_table:
                render_table(pdf, table_rows)
                in_table = False
                table_rows = []
            indent = len(num_match.group(1))
            text = clean_markdown(num_match.group(2))
            if text:
                pdf.set_x(15 + indent * 3)
                pdf.multi_cell(0, 6, text)
            i += 1
            continue

        # Regular text
        if line.strip():
            if in_table:
                render_table(pdf, table_rows)
                in_table = False
                table_rows = []
            text = clean_markdown(line)
            pdf.set_x(10)
            pdf.multi_cell(0, 6, text)
        else:
            pdf.ln(3)

        i += 1

    if in_table:
        render_table(pdf, table_rows)

    pdf.output(pdf_path)
    print(f"PDF created: {pdf_path}")

def render_table(pdf, rows):
    if not rows:
        return

    # Determine max columns
    max_cols = max(len(r) for r in rows)

    # Calculate column widths
    col_width = 180 / max_cols

    # First row as headers if it looks like headers
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(240, 240, 240)

    for j, cell in enumerate(rows[0]):
        pdf.cell(col_width, 7, clean_markdown(cell)[:30], 1, 0, 'C', fill=True)
    pdf.ln()

    pdf.set_font('Arial', '', 9)
    pdf.set_fill_color(255, 255, 255)

    for row in rows[1:]:
        for j, cell in enumerate(row):
            if j < max_cols:
                pdf.cell(col_width, 6, clean_markdown(cell)[:35], 1, 0, 'L')
        pdf.ln()
    pdf.ln(5)

if __name__ == '__main__':
    md_path = r'C:\Users\compj\.openclaw\workspace\pota-ham-radio-promotion-strategy.md'
    pdf_path = r'C:\Users\compj\.openclaw\workspace\pota-ham-radio-promotion-strategy.pdf'
    convert_md_to_pdf(md_path, pdf_path)
