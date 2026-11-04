import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def clean_xml_string(s):
    if not s:
        return ""
    # Filter valid XML chars: \x09, \x0A, \x0D, \x20-\uD7FF, \uE000-\uFFFD
    return re.sub(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]', '', s)

def create_rich_build_guide(md_path, docx_path):
    with open(md_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)

    NAVY = RGBColor(15, 23, 42)
    BLUE = RGBColor(2, 132, 199)
    DARK = RGBColor(30, 41, 59)

    in_code = False
    code_lines = []

    for line in content.split('\n'):
        raw = clean_xml_string(line.rstrip('\r\n'))

        if raw.strip().startswith('```'):
            if in_code:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.3)
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(5)
                run = p.add_run('\n'.join(code_lines))
                run.font.name = 'Consolas'
                run.font.size = Pt(9.5)
                run.font.color.rgb = DARK
                code_lines = []
                in_code = False
            else:
                in_code = True
                code_lines = []
            continue

        if in_code:
            code_lines.append(raw)
            continue

        if raw.strip() in ['---', '***', '___']:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(5)
            run = p.add_run('—' * 55)
            run.font.color.rgb = RGBColor(203, 213, 225)
            continue

        if raw.startswith('# '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(raw[2:].strip())
            run.font.name = 'Arial'
            run.font.size = Pt(20)
            run.font.bold = True
            run.font.color.rgb = NAVY
            continue
        elif raw.startswith('## '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(11)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(raw[3:].strip())
            run.font.name = 'Arial'
            run.font.size = Pt(15)
            run.font.bold = True
            run.font.color.rgb = BLUE
            continue
        elif raw.startswith('### '):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(9)
            p.paragraph_format.space_after = Pt(3)
            run = p.add_run(raw[4:].strip())
            run.font.name = 'Arial'
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = NAVY
            continue

        if raw.startswith('> '):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            run = p.add_run(raw[2:].strip())
            run.font.name = 'Calibri'
            run.font.size = Pt(10.5)
            run.font.italic = True
            run.font.color.rgb = DARK
            continue

        if raw.strip().startswith('- ') or raw.strip().startswith('* '):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(raw.strip()[2:])
            run.font.name = 'Calibri'
            run.font.size = Pt(10.5)
            continue

        match_num = re.match(r'^\s*(\d+)\.\s+(.*)$', raw)
        if match_num:
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(match_num.group(2))
            run.font.name = 'Calibri'
            run.font.size = Pt(10.5)
            continue

        if raw.strip():
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(raw.strip())
            run.font.name = 'Calibri'
            run.font.size = Pt(10.5)
            run.font.color.rgb = DARK

    doc.save(docx_path)
    print(f"Generated DOCX build guide at: {docx_path}")

if __name__ == '__main__':
    doc_dir = r"c:\Users\pavan\Downloads\student-job-matching-20261027T105016Z-1-001 (2)\documentation"
    create_rich_build_guide(
        os.path.join(doc_dir, "LaunchPad_App_Architecture_and_Development_Guide.md"),
        os.path.join(doc_dir, "LaunchPad_App_Architecture_and_Development_Guide.docx")
    )
