import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def md_to_docx(md_path, docx_path, doc_title):
    doc = docx.Document()

    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Style colors
    NAVY = RGBColor(15, 23, 42)
    BLUE = RGBColor(2, 132, 199)
    DARK = RGBColor(30, 41, 59)

    with open(md_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    in_code_block = False
    code_lines = []

    for line in lines:
        raw = line.rstrip('\r\n')

        # Code block handling
        if raw.strip().startswith('```'):
            if in_code_block:
                # End code block
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.3)
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(6)
                run = p.add_run('\n'.join(code_lines))
                run.font.name = 'Consolas'
                run.font.size = Pt(9.5)
                run.font.color.rgb = DARK
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(raw)
            continue

        # Skip horizontal rules
        if raw.strip() in ['---', '***', '___']:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run('—' * 55)
            run.font.color.rgb = RGBColor(203, 213, 225)
            continue

        # Headings
        if raw.startswith('# '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(raw[2:].strip())
            run.font.name = 'Arial'
            run.font.size = Pt(22)
            run.font.bold = True
            run.font.color.rgb = NAVY
            continue
        elif raw.startswith('## '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(raw[3:].strip())
            run.font.name = 'Arial'
            run.font.size = Pt(16)
            run.font.bold = True
            run.font.color.rgb = BLUE
            continue
        elif raw.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            run = p.add_run(raw[4:].strip())
            run.font.name = 'Arial'
            run.font.size = Pt(13)
            run.font.bold = True
            run.font.color.rgb = NAVY
            continue
        elif raw.startswith('#### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(raw[5:].strip())
            run.font.name = 'Arial'
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = DARK
            continue

        # Blockquote / Alert
        if raw.startswith('> '):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            text_val = raw[2:].strip()
            run = p.add_run(text_val)
            run.font.name = 'Calibri'
            run.font.size = Pt(10.5)
            run.font.italic = True
            run.font.color.rgb = DARK
            continue

        # Bullet list
        if raw.strip().startswith('- ') or raw.strip().startswith('* '):
            indent_level = (len(raw) - len(raw.lstrip())) // 2
            text_val = raw.strip()[2:]
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.left_indent = Inches(0.25 * (indent_level + 1))
            run = p.add_run(text_val)
            run.font.name = 'Calibri'
            run.font.size = Pt(10.5)
            continue

        # Numbered list
        match_num = re.match(r'^\s*(\d+)\.\s+(.*)$', raw)
        if match_num:
            text_val = match_num.group(2)
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(text_val)
            run.font.name = 'Calibri'
            run.font.size = Pt(10.5)
            continue

        # Normal text paragraph
        if raw.strip():
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(raw.strip())
            run.font.name = 'Calibri'
            run.font.size = Pt(11)
            run.font.color.rgb = DARK

    doc.save(docx_path)
    print(f"Generated DOCX at: {docx_path}")

if __name__ == '__main__':
    base_dir = r"c:\Users\pavan\Downloads\student-job-matching-20261027T105016Z-1-001 (2)\documentation"
    md_to_docx(
        os.path.join(base_dir, "LaunchPad_Presentation_Script_and_Guide.md"),
        os.path.join(base_dir, "LaunchPad_Presentation_Script_and_Guide.docx"),
        "LaunchPad Presentation Script and Guide"
    )
    md_to_docx(
        os.path.join(base_dir, "LaunchPad_App_Architecture_and_Development_Guide.md"),
        os.path.join(base_dir, "LaunchPad_App_Architecture_and_Development_Guide.docx"),
        "LaunchPad Full Architecture and Implementation Manual"
    )
