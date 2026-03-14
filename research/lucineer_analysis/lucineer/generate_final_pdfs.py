from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# Register fonts
pdfmetrics.registerFont(TTFont('Times New Roman', '/usr/share/fonts/truetype/english/Times-New-Roman.ttf'))
registerFontFamily('Times New Roman', normal='Times New Roman', bold='Times New Roman')

# Define styles
styles = getSampleStyleSheet()

h1_style = ParagraphStyle(
    name='H1Style',
    fontName='Times New Roman',
    fontSize=16,
    leading=20,
    spaceBefore=18,
    spaceAfter=10,
    alignment=TA_LEFT
)

h2_style = ParagraphStyle(
    name='H2Style',
    fontName='Times New Roman',
    fontSize=12,
    leading=16,
    spaceBefore=12,
    spaceAfter=6,
    alignment=TA_LEFT
)

body_style = ParagraphStyle(
    name='BodyStyle',
    fontName='Times New Roman',
    fontSize=10,
    leading=14,
    alignment=TA_JUSTIFY,
    spaceAfter=6
)

header_style = ParagraphStyle(
    name='TableHeader',
    fontName='Times New Roman',
    fontSize=9,
    textColor=colors.white,
    alignment=TA_CENTER
)

cell_style = ParagraphStyle(
    name='TableCell',
    fontName='Times New Roman',
    fontSize=8,
    alignment=TA_CENTER
)

def create_pdf(filename, title, content_sections):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        title=title,
        author='Z.ai',
        creator='Z.ai'
    )
    
    story = []
    
    for section in content_sections:
        if section['type'] == 'title':
            story.append(Paragraph(f"<b>{section['text']}</b>", h1_style))
        elif section['type'] == 'subtitle':
            story.append(Paragraph(f"<b>{section['text']}</b>", h2_style))
        elif section['type'] == 'body':
            story.append(Paragraph(section['text'], body_style))
        elif section['type'] == 'table':
            data = section['data']
            t = Table(data, colWidths=section.get('widths', [1.5*inch]*len(data[0])))
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 12))
        elif section['type'] == 'spacer':
            story.append(Spacer(1, section['size']))
        elif section['type'] == 'pagebreak':
            story.append(PageBreak())
    
    doc.build(story)
    print(f"Generated: {filename}")

# Generate Executive Summary PDF
create_pdf(
    "/home/z/my-project/final_delivery/core_documents/02_Executive_Summary.pdf",
    "Executive Summary",
    [
        {'type': 'title', 'text': 'Mask-Locked Inference Chip'},
        {'type': 'subtitle', 'text': 'Executive Summary for Investors'},
        {'type': 'spacer', 'size': 12},
        {'type': 'body', 'text': 'The Mask-Locked Inference Chip is a new category of semiconductor that embeds neural network weights directly in silicon. By sacrificing model flexibility, we achieve order-of-magnitude improvements in power, cost, and simplicity for edge AI inference.'},
        {'type': 'spacer', 'size': 12},
        {'type': 'subtitle', 'text': 'Key Metrics'},
        {'type': 'table', 'data': [
            [Paragraph('<b>Metric</b>', header_style), Paragraph('<b>Our Product</b>', header_style), Paragraph('<b>Competitor</b>', header_style)],
            [Paragraph('Price', cell_style), Paragraph('$35-60', cell_style), Paragraph('$88-250', cell_style)],
            [Paragraph('Power', cell_style), Paragraph('2-3W', cell_style), Paragraph('5-15W', cell_style)],
            [Paragraph('Throughput', cell_style), Paragraph('80-150 tok/s', cell_style), Paragraph('5-30 tok/s', cell_style)],
            [Paragraph('Setup Time', cell_style), Paragraph('Zero', cell_style), Paragraph('Days', cell_style)],
        ], 'widths': [1.5*inch, 1.8*inch, 1.8*inch]},
        {'type': 'spacer', 'size': 12},
        {'type': 'subtitle', 'text': 'Technical Innovations'},
        {'type': 'body', 'text': '1. Multiplication-Free Inference: iFairy complex weights eliminate multipliers (95% gate reduction)'},
        {'type': 'body', 'text': '2. On-Chip KV Cache: Sliding window fits 21MB in SRAM (eliminates external memory)'},
        {'type': 'body', 'text': '3. Mask-Locked Weights: Zero access energy, infinite bandwidth'},
        {'type': 'spacer', 'size': 12},
        {'type': 'subtitle', 'text': 'Funding Requirements'},
        {'type': 'body', 'text': 'Seed Round: $500K for FPGA prototype and architecture freeze (Month 1-6)'},
        {'type': 'body', 'text': 'Series A: $3M for MPW tapeout (Month 7-18)'},
        {'type': 'body', 'text': 'Series B: $10M for production scaling (Month 19+)'},
        {'type': 'spacer', 'size': 12},
        {'type': 'subtitle', 'text': 'Financial Projections'},
        {'type': 'table', 'data': [
            [Paragraph('<b>Year</b>', header_style), Paragraph('<b>Units</b>', header_style), Paragraph('<b>Revenue</b>', header_style), Paragraph('<b>Gross Profit</b>', header_style)],
            [Paragraph('1', cell_style), Paragraph('5K', cell_style), Paragraph('$175K', cell_style), Paragraph('$140K', cell_style)],
            [Paragraph('2', cell_style), Paragraph('50K', cell_style), Paragraph('$1.75M', cell_style), Paragraph('$1.4M', cell_style)],
            [Paragraph('3', cell_style), Paragraph('200K', cell_style), Paragraph('$7M', cell_style), Paragraph('$5.6M', cell_style)],
            [Paragraph('5', cell_style), Paragraph('1M', cell_style), Paragraph('$35M', cell_style), Paragraph('$28M', cell_style)],
        ], 'widths': [1*inch, 1.2*inch, 1.5*inch, 1.5*inch]},
        {'type': 'spacer', 'size': 12},
        {'type': 'subtitle', 'text': 'Exit Potential'},
        {'type': 'body', 'text': 'Potential acquirers: Qualcomm, NVIDIA, Apple, Intel'},
        {'type': 'body', 'text': 'Estimated acquisition value: $150-400M at $10-50M revenue'},
    ]
)

# Generate Technical Architecture PDF
create_pdf(
    "/home/z/my-project/final_delivery/core_documents/01_Technical_Architecture.pdf",
    "Technical Architecture",
    [
        {'type': 'title', 'text': 'Technical Architecture Document'},
        {'type': 'subtitle', 'text': 'Complete Specifications'},
        {'type': 'spacer', 'size': 12},
        {'type': 'body', 'text': 'This document provides complete technical specifications for the Mask-Locked Inference Chip, a semiconductor device that embeds neural network weights directly in silicon for edge AI inference.'},
        {'type': 'pagebreak', 'size': 0},
        {'type': 'title', 'text': 'Target Specifications'},
        {'type': 'table', 'data': [
            [Paragraph('<b>Parameter</b>', header_style), Paragraph('<b>Target</b>', header_style), Paragraph('<b>Rationale</b>', header_style)],
            [Paragraph('Model Size', cell_style), Paragraph('1-3B params', cell_style), Paragraph('Fits in die area', cell_style)],
            [Paragraph('Power', cell_style), Paragraph('2-3W', cell_style), Paragraph('USB-powered', cell_style)],
            [Paragraph('Throughput', cell_style), Paragraph('80-150 tok/s', cell_style), Paragraph('Real-time chat', cell_style)],
            [Paragraph('Price', cell_style), Paragraph('$35-60', cell_style), Paragraph('Market gap', cell_style)],
            [Paragraph('Process', cell_style), Paragraph('28nm', cell_style), Paragraph('Low NRE', cell_style)],
        ], 'widths': [1.5*inch, 1.5*inch, 2*inch]},
        {'type': 'spacer', 'size': 12},
        {'type': 'title', 'text': 'Architecture Components'},
        {'type': 'body', 'text': '1. Compute Core: 1024 RAUs in 32x32 systolic array (~0.1mm²)'},
        {'type': 'body', 'text': '2. KV Cache: 21MB on-chip SRAM (~28mm²)'},
        {'type': 'body', 'text': '3. Control Logic: Simple FSM, no CPU/OS (~2mm²)'},
        {'type': 'body', 'text': '4. I/O: USB 3.0 interface (~5mm²)'},
        {'type': 'spacer', 'size': 12},
        {'type': 'title', 'text': 'Die Economics'},
        {'type': 'table', 'data': [
            [Paragraph('<b>Item</b>', header_style), Paragraph('<b>Value</b>', header_style)],
            [Paragraph('Die Size', cell_style), Paragraph('~40mm²', cell_style)],
            [Paragraph('Wafer Cost (28nm)', cell_style), Paragraph('$3,000', cell_style)],
            [Paragraph('Dies per Wafer', cell_style), Paragraph('1,360', cell_style)],
            [Paragraph('Die Cost', cell_style), Paragraph('$2.21', cell_style)],
            [Paragraph('Package + Test', cell_style), Paragraph('$3.00', cell_style)],
            [Paragraph('Total COGS', cell_style), Paragraph('$5.21', cell_style)],
        ], 'widths': [2*inch, 2*inch]},
    ]
)

print("All PDFs generated successfully!")
