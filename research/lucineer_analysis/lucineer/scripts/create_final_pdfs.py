#!/usr/bin/env python3
import os, re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

pdfmetrics.registerFont(TTFont('Times New Roman', '/usr/share/fonts/truetype/english/Times-New-Roman.ttf'))
registerFontFamily('Times New Roman', normal='Times New Roman', bold='Times New Roman')

PRIMARY = colors.HexColor('#1F4E79')
HEADER_BG = colors.HexColor('#1F4E79')
ROW_ODD = colors.HexColor('#F5F5F5')

def get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='DocTitle', fontName='Times New Roman', fontSize=28, leading=34, alignment=TA_CENTER, spaceAfter=20, textColor=PRIMARY))
    styles.add(ParagraphStyle(name='DocSub', fontName='Times New Roman', fontSize=14, leading=18, alignment=TA_CENTER, spaceAfter=30, textColor=colors.HexColor('#666666')))
    styles.add(ParagraphStyle(name='DocH1', fontName='Times New Roman', fontSize=18, leading=24, alignment=TA_LEFT, spaceBefore=20, spaceAfter=10, textColor=PRIMARY))
    styles.add(ParagraphStyle(name='DocH2', fontName='Times New Roman', fontSize=14, leading=18, alignment=TA_LEFT, spaceBefore=14, spaceAfter=8, textColor=colors.HexColor('#333333')))
    styles.add(ParagraphStyle(name='DocH3', fontName='Times New Roman', fontSize=12, leading=16, alignment=TA_LEFT, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor('#444444')))
    styles.add(ParagraphStyle(name='DocBody', fontName='Times New Roman', fontSize=10.5, leading=15, alignment=TA_JUSTIFY, spaceAfter=8))
    styles.add(ParagraphStyle(name='DocBullet', fontName='Times New Roman', fontSize=10, leading=14, alignment=TA_LEFT, leftIndent=20, spaceAfter=4))
    return styles

def clean_text(text):
    # Remove code blocks and complex formatting
    text = re.sub(r'```.*?```', '[CODE BLOCK]', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'<b>\1</b>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Remove box drawing characters
    text = re.sub(r'[┌┐└┘│─├┤┬┴┼╭╮╯╰═║╔╗╚╝╠╣╦╩╬]', '', text)
    return text

def parse_md(content):
    lines = content.split('\n')
    elements = []
    current = []
    table_data = []
    in_table = False
    
    for line in lines:
        s = line.strip()
        if s.startswith('# ') and not s.startswith('## '):
            if current: elements.append(('body', '\n'.join(current)))
            current = []
            elements.append(('h1', s[2:]))
        elif s.startswith('## '):
            if current: elements.append(('body', '\n'.join(current)))
            current = []
            elements.append(('h2', s[3:]))
        elif s.startswith('### '):
            if current: elements.append(('body', '\n'.join(current)))
            current = []
            elements.append(('h3', s[4:]))
        elif s.startswith('|'):
            if not in_table:
                if current: elements.append(('body', '\n'.join(current)))
                current = []
                in_table = True
                table_data = []
            cells = [c.strip() for c in s.split('|')[1:-1]]
            if cells: table_data.append(cells)
        elif in_table and not s.startswith('|'):
            if table_data: elements.append(('table', table_data))
            table_data = []
            in_table = False
            if s and not s.startswith('---'): current.append(s)
        elif s.startswith('- ') or s.startswith('* '):
            if current: elements.append(('body', '\n'.join(current)))
            current = []
            elements.append(('bullet', s[2:]))
        elif s.startswith('---'): pass
        elif s: current.append(s)
    
    if current: elements.append(('body', '\n'.join(current)))
    if table_data: elements.append(('table', table_data))
    return elements

def create_pdf(md_file, pdf_file, title):
    with open(md_file, 'r') as f: content = f.read()
    elements = parse_md(content)
    styles = get_styles()
    doc = SimpleDocTemplate(pdf_file, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch, title=title, author="Z.ai", creator="Z.ai")
    story = [Paragraph(title, styles['DocTitle']), Paragraph("SuperInstance.AI | Production Document", styles['DocSub']), Spacer(1, 20)]
    
    for t, c in elements:
        try:
            if t == 'h1': story.extend([PageBreak(), Paragraph(clean_text(c), styles['DocH1'])])
            elif t == 'h2': story.extend([Spacer(1, 10), Paragraph(clean_text(c), styles['DocH2'])])
            elif t == 'h3': story.append(Paragraph(clean_text(c), styles['DocH3']))
            elif t == 'body':
                txt = clean_text(c)
                if txt.strip() and len(txt) < 5000: story.append(Paragraph(txt, styles['DocBody']))
            elif t == 'bullet': story.append(Paragraph("* " + clean_text(c), styles['DocBullet']))
            elif t == 'table' and len(c) > 1:
                cols = len(c[0])
                w = (6.5*inch) / cols
                tbl = Table(c, colWidths=[w]*cols)
                tbl.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), HEADER_BG), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white), ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('FONTNAME', (0, 0), (-1, -1), 'Times New Roman'), ('FONTSIZE', (0, 0), (-1, -1), 8), ('BOTTOMPADDING', (0, 0), (-1, -1), 5), ('TOPPADDING', (0, 0), (-1, -1), 5), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
                for i in range(1, len(c)):
                    if i % 2 == 0: tbl.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), ROW_ODD)]))
                story.extend([Spacer(1, 8), tbl, Spacer(1, 8)])
        except Exception as e:
            print(f"Skip element: {str(e)[:50]}")
            continue
    
    doc.build(story)
    print(f"Created: {pdf_file}")

def main():
    production = "/home/z/my-project/final_delivery/production"
    output = "/home/z/my-project/download"
    docs = [
        ("SuperInstance_Executive_Summary_FINAL.md", "SuperInstance_Executive_Summary_FINAL.pdf", "Executive Summary"),
        ("SuperInstance_Investor_Pitch_FINAL.md", "SuperInstance_Investor_Pitch_FINAL.pdf", "Investor Pitch Deck"),
        ("SuperInstance_Technical_Specification_FINAL.md", "SuperInstance_Technical_Specification_FINAL.pdf", "Technical Specification"),
        ("SuperInstance_Business_Model_FINAL.md", "SuperInstance_Business_Model_FINAL.pdf", "Business Model"),
        ("SuperInstance_Competitive_Analysis_FINAL.md", "SuperInstance_Competitive_Analysis_FINAL.pdf", "Competitive Analysis"),
        ("SuperInstance_GTM_Operations_FINAL.md", "SuperInstance_GTM_Operations_FINAL.pdf", "GTM Operations Plan"),
    ]
    for md, pdf, title in docs:
        mp, pp = os.path.join(production, md), os.path.join(output, pdf)
        if os.path.exists(mp): create_pdf(mp, pp, title)
        else: print(f"Missing: {mp}")

if __name__ == '__main__': main()
