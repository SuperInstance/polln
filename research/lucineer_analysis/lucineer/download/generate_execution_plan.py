#!/usr/bin/env python3
"""
Mask-Locked Inference Chip - MVP Execution Plan Generator
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register fonts
pdfmetrics.registerFont(TTFont('Times New Roman', '/usr/share/fonts/truetype/english/Times-New-Roman.ttf'))

# Color scheme
PRIMARY = colors.HexColor('#0B1220')
SECONDARY = colors.HexColor('#2B2B2B')
ACCENT = colors.HexColor('#1F4E79')
TABLE_HEADER = colors.HexColor('#1F4E79')
TABLE_ROW_ODD = colors.HexColor('#F5F5F5')

def create_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontName='Times New Roman',
        fontSize=36,
        leading=44,
        alignment=TA_CENTER,
        textColor=PRIMARY,
        spaceAfter=24
    ))
    
    styles.add(ParagraphStyle(
        name='CoverSubtitle',
        fontName='Times New Roman',
        fontSize=18,
        leading=24,
        alignment=TA_CENTER,
        textColor=SECONDARY,
        spaceAfter=12
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontName='Times New Roman',
        fontSize=18,
        leading=24,
        alignment=TA_LEFT,
        textColor=PRIMARY,
        spaceBefore=24,
        spaceAfter=12
    ))
    
    styles.add(ParagraphStyle(
        name='SubsectionHeading',
        fontName='Times New Roman',
        fontSize=14,
        leading=18,
        alignment=TA_LEFT,
        textColor=ACCENT,
        spaceBefore=18,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='BodyPara',
        fontName='Times New Roman',
        fontSize=11,
        leading=16,
        alignment=TA_LEFT,
        textColor=SECONDARY,
        spaceBefore=4,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='Times New Roman',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=SECONDARY
    ))
    
    styles.add(ParagraphStyle(
        name='TableHeader',
        fontName='Times New Roman',
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.white
    ))
    
    styles.add(ParagraphStyle(
        name='CaptionText',
        fontName='Times New Roman',
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#666666'),
        spaceBefore=4,
        spaceAfter=12
    ))
    
    return styles

def create_table(data, col_widths, header=True):
    table = Table(data, colWidths=col_widths)
    style_commands = [
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]
    if header:
        style_commands.append(('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER))
        for i in range(1, len(data)):
            if i % 2 == 0:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), TABLE_ROW_ODD))
    table.setStyle(TableStyle(style_commands))
    return table

def build_document():
    output_path = '/home/z/my-project/download/Mask_Locked_Chip_MVP_Execution_Plan.pdf'
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title='Mask-Locked Chip MVP Execution Plan',
        author='Z.ai',
        creator='Z.ai',
        subject='Strategic execution plan for mask-locked inference chip MVP'
    )
    
    styles = create_styles()
    story = []
    
    # Cover page
    story.append(Spacer(1, 100))
    story.append(Paragraph('MASK-LOCKED INFERENCE CHIP', styles['CoverTitle']))
    story.append(Spacer(1, 12))
    story.append(Paragraph('MVP Execution Plan', styles['CoverSubtitle']))
    story.append(Spacer(1, 24))
    story.append(Paragraph('The TI Calculator Strategy', styles['CoverSubtitle']))
    story.append(Spacer(1, 48))
    story.append(Paragraph('One Perfect Product. One Killer App.', styles['BodyPara']))
    story.append(Spacer(1, 80))
    story.append(Paragraph(f'Version 5.0 - {datetime.now().strftime("%B %Y")}', styles['BodyPara']))
    story.append(Paragraph('CONFIDENTIAL - FOR INTERNAL USE ONLY', styles['BodyPara']))
    story.append(PageBreak())
    
    # Executive Summary
    story.append(Paragraph('EXECUTIVE SUMMARY', styles['SectionHeading']))
    story.append(Paragraph(
        'This document synthesizes comprehensive research into a focused MVP execution strategy for the Mask-Locked Inference Chip. '
        'Following extensive competitive analysis, market research, and verification of all technical claims, we propose a stripped-down '
        'approach: the "TI Calculator Strategy" - building one perfect product for one specific use case, rather than a complex multi-tier platform.',
        styles['BodyPara']
    ))
    
    story.append(Paragraph('Key Research Findings', styles['SubsectionHeading']))
    
    findings_data = [
        [Paragraph('<b>Finding</b>', styles['TableHeader']), Paragraph('<b>Status</b>', styles['TableHeader']), Paragraph('<b>Source</b>', styles['TableHeader'])],
        [Paragraph('Groq-NVIDIA Deal', styles['TableCell']), Paragraph('$20B licensing + acquihire (NOT pure acquisition)', styles['TableCell']), Paragraph('CNBC, Reuters, Dec 2025', styles['TableCell'])],
        [Paragraph('SD Card Power Limit', styles['TableCell']), Paragraph('Max 200mA per SDIO spec; design for 1W max', styles['TableCell']), Paragraph('SD Association Spec v6.0', styles['TableCell'])],
        [Paragraph('Raspberry Pi Installed Base', styles['TableCell']), Paragraph('70+ million units shipped by 2025', styles['TableCell']), Paragraph('Wikipedia, HackMD Feb 2026', styles['TableCell'])],
        [Paragraph('Edge AI Chip Market', styles['TableCell']), Paragraph('$3.67B (2025) to $11.54B (2030) CAGR 25.7%', styles['TableCell']), Paragraph('Mordor Intelligence', styles['TableCell'])],
        [Paragraph('Hailo-8L on Pi', styles['TableCell']), Paragraph('13 TOPS, ~$70, already shipping as official Pi AI Kit', styles['TableCell']), Paragraph('RaspberryPi.com', styles['TableCell'])],
        [Paragraph('Etched Sohu', styles['TableCell']), Paragraph('$120M to $500M raised, TSMC 4nm, transformer-only ASIC', styles['TableCell']), Paragraph('TechCrunch, ByteIota', styles['TableCell'])],
    ]
    story.append(Spacer(1, 12))
    story.append(create_table(findings_data, [4*cm, 6*cm, 5*cm]))
    story.append(Paragraph('Table 1: Verified Research Findings', styles['CaptionText']))
    
    story.append(Paragraph('Strategic Pivot', styles['SubsectionHeading']))
    story.append(Paragraph(
        'Based on competitive analysis, we recommend a fundamental pivot from the original multi-tier strategy (SD card + Thunderbolt 5) '
        'to a focused single-product approach: a Raspberry Pi HAT delivering offline LLM inference for coding assistance. This "TI Calculator Strategy" '
        'emulates Texas Instruments approach: build one chip, find one killer app, dominate that niche before expanding.',
        styles['BodyPara']
    ))
    
    # Competitive Landscape
    story.append(Paragraph('COMPETITIVE LANDSCAPE ANALYSIS', styles['SectionHeading']))
    story.append(Paragraph('The edge AI inference market has evolved significantly. Here is the verified competitive positioning:', styles['BodyPara']))
    
    comp_data = [
        [Paragraph('<b>Product</b>', styles['TableHeader']), Paragraph('<b>Price</b>', styles['TableHeader']), Paragraph('<b>Power</b>', styles['TableHeader']), Paragraph('<b>Performance</b>', styles['TableHeader']), Paragraph('<b>Target</b>', styles['TableHeader'])],
        [Paragraph('NVIDIA Jetson Orin Nano Super', styles['TableCell']), Paragraph('$299', styles['TableCell']), Paragraph('7-25W', styles['TableCell']), Paragraph('67 TOPS', styles['TableCell']), Paragraph('General-purpose edge AI', styles['TableCell'])],
        [Paragraph('Raspberry Pi AI Kit (Hailo-8L)', styles['TableCell']), Paragraph('~$70', styles['TableCell']), Paragraph('2.5W', styles['TableCell']), Paragraph('13 TOPS', styles['TableCell']), Paragraph('Vision/CNN only (no LLM)', styles['TableCell'])],
        [Paragraph('Google Coral Edge TPU', styles['TableCell']), Paragraph('$60-75', styles['TableCell']), Paragraph('2W', styles['TableCell']), Paragraph('4 TOPS', styles['TableCell']), Paragraph('Vision only (INT8)', styles['TableCell'])],
        [Paragraph('<b>Your Mask-Locked Pi HAT</b>', styles['TableCell']), Paragraph('<b>$69</b>', styles['TableCell']), Paragraph('<b>5W</b>', styles['TableCell']), Paragraph('<b>80 tok/s (2B INT4)</b>', styles['TableCell']), Paragraph('<b>Offline LLM inference</b>', styles['TableCell'])],
        [Paragraph('Etched Sohu', styles['TableCell']), Paragraph('Enterprise pricing', styles['TableCell']), Paragraph('300W+', styles['TableCell']), Paragraph('500K+ tok/s', styles['TableCell']), Paragraph('Datacenter transformers', styles['TableCell'])],
    ]
    story.append(Spacer(1, 12))
    story.append(create_table(comp_data, [4.5*cm, 2*cm, 2*cm, 3*cm, 4*cm]))
    story.append(Paragraph('Table 2: Competitive Positioning Matrix', styles['CaptionText']))
    
    story.append(Paragraph('The Gap in the Market', styles['SubsectionHeading']))
    story.append(Paragraph(
        'Critical insight: No current product offers meaningful LLM inference (2B+ parameters) at sub-$100 price points with sub-5W power consumption. '
        'The Hailo-8L ships 13 TOPS but only for CNNs - it cannot run transformer models. The Coral TPU is INT8-only for vision tasks. '
        'NVIDIA Jetson can run LLMs but at 7-25W and $299+ price point. This creates a clear market gap for a dedicated LLM inference accelerator '
        'targeting the maker/hobbyist segment.',
        styles['BodyPara']
    ))
    
    # TI Calculator Strategy
    story.append(Paragraph('THE TI CALCULATOR STRATEGY', styles['SectionHeading']))
    story.append(Paragraph(
        'Texas Instruments calculator business offers a masterclass in hardware product strategy. Despite calculators representing less than 3% of TIs '
        'revenue, the TI-84 Plus has maintained a monopoly in education for over 30 years. The key lessons:',
        styles['BodyPara']
    ))
    
    ti_data = [
        [Paragraph('<b>TI Strategy Element</b>', styles['TableHeader']), Paragraph('<b>What TI Did</b>', styles['TableHeader']), Paragraph('<b>Your Application</b>', styles['TableHeader'])],
        [Paragraph('Chip-first approach', styles['TableCell']), Paragraph('Built TMS 1000 microcontroller, then found uses', styles['TableCell']), Paragraph('Build mask-locked architecture, then find ONE perfect use', styles['TableCell'])],
        [Paragraph('Education lock-in', styles['TableCell']), Paragraph('TI-81 (1990) + College Board standardization', styles['TableCell']), Paragraph('Target Pi developer community with standardized tooling', styles['TableCell'])],
        [Paragraph('Premium pricing', styles['TableCell']), Paragraph('$100 in 1990 (~$175 today), never discounted', styles['TableCell']), Paragraph('$69 price point for perceived value, not cost-plus', styles['TableCell'])],
        [Paragraph('Decades-long lifecycle', styles['TableCell']), Paragraph('TI-84 still selling 30+ years later', styles['TableCell']), Paragraph('Build for longevity, model stability', styles['TableCell'])],
        [Paragraph('Manufacturing cost', styles['TableCell']), Paragraph('<$5 manufacturing cost per unit', styles['TableCell']), Paragraph('Target ~$20 COGS for healthy margins', styles['TableCell'])],
    ]
    story.append(Spacer(1, 12))
    story.append(create_table(ti_data, [4*cm, 5*cm, 5.5*cm]))
    story.append(Paragraph('Table 3: TI Calculator Strategy Analysis', styles['CaptionText']))
    
    # The One Killer App
    story.append(Paragraph('THE ONE KILLER APP: PI-LLM', styles['SectionHeading']))
    story.append(Paragraph(
        'Do not build a generic "AI accelerator." Build the specific thing people want. After analyzing the Pi ecosystem and viral hardware patterns '
        '(Flipper Zero, Analogue Pocket), we recommend:',
        styles['BodyPara']
    ))
    
    spec_data = [
        [Paragraph('<b>Attribute</b>', styles['TableHeader']), Paragraph('<b>Specification</b>', styles['TableHeader'])],
        [Paragraph('Form Factor', styles['TableCell']), Paragraph('Raspberry Pi HAT (40-pin GPIO)', styles['TableCell'])],
        [Paragraph('Model', styles['TableCell']), Paragraph('2B parameters, INT4 quantized (CodeLlama-2B or Gemma-2B)', styles['TableCell'])],
        [Paragraph('Power', styles['TableCell']), Paragraph('5W from Pi 5V rail', styles['TableCell'])],
        [Paragraph('Performance', styles['TableCell']), Paragraph('50-80 tokens/second', styles['TableCell'])],
        [Paragraph('Price', styles['TableCell']), Paragraph('$69 (matches Pi 5 pricing tier)', styles['TableCell'])],
        [Paragraph('Use Case', styles['TableCell']), Paragraph('Offline coding assistant', styles['TableCell'])],
        [Paragraph('Viral Demo', styles['TableCell']), Paragraph('"I wrote Python on my Pi in a parking lot with no WiFi"', styles['TableCell'])],
    ]
    story.append(Spacer(1, 12))
    story.append(create_table(spec_data, [4*cm, 10*cm]))
    story.append(Paragraph('Table 4: Pi-LLM HAT Product Specification', styles['CaptionText']))
    
    # Technical Architecture
    story.append(Paragraph('TECHNICAL ARCHITECTURE', styles['SectionHeading']))
    
    bom_data = [
        [Paragraph('<b>Component</b>', styles['TableHeader']), Paragraph('<b>Specification</b>', styles['TableHeader']), Paragraph('<b>Est. Cost</b>', styles['TableHeader'])],
        [Paragraph('Die', styles['TableCell']), Paragraph('28nm, 2B params, INT4 weights hardwired', styles['TableCell']), Paragraph('$8', styles['TableCell'])],
        [Paragraph('Package', styles['TableCell']), Paragraph('HAT-compatible PCB, 40-pin header', styles['TableCell']), Paragraph('$3', styles['TableCell'])],
        [Paragraph('SRAM (KV Cache)', styles['TableCell']), Paragraph('512MB for 4K context', styles['TableCell']), Paragraph('$4', styles['TableCell'])],
        [Paragraph('Passives', styles['TableCell']), Paragraph('LEDs, regulators, capacitors', styles['TableCell']), Paragraph('$2', styles['TableCell'])],
        [Paragraph('Assembly', styles['TableCell']), Paragraph('Automated SMT', styles['TableCell']), Paragraph('$3', styles['TableCell'])],
        [Paragraph('<b>Total COGS</b>', styles['TableCell']), Paragraph('', styles['TableCell']), Paragraph('<b>~$20</b>', styles['TableCell'])],
        [Paragraph('<b>Target Price</b>', styles['TableCell']), Paragraph('', styles['TableCell']), Paragraph('<b>$69</b>', styles['TableCell'])],
        [Paragraph('<b>Gross Margin</b>', styles['TableCell']), Paragraph('', styles['TableCell']), Paragraph('<b>71%</b>', styles['TableCell'])],
    ]
    story.append(Spacer(1, 12))
    story.append(create_table(bom_data, [4*cm, 7*cm, 3*cm]))
    story.append(Paragraph('Table 5: Hardware Bill of Materials Estimate', styles['CaptionText']))
    
    # Software Ecosystem
    story.append(Paragraph('SOFTWARE ECOSYSTEM PLAN', styles['SectionHeading']))
    story.append(Paragraph('The Pi-LLM must "just work" out of the box:', styles['BodyPara']))
    
    sw_data = [
        [Paragraph('<b>Component</b>', styles['TableHeader']), Paragraph('<b>Description</b>', styles['TableHeader']), Paragraph('<b>License</b>', styles['TableHeader'])],
        [Paragraph('Python SDK', styles['TableCell']), Paragraph('pip install pi-llm - auto-detects HAT', styles['TableCell']), Paragraph('MIT', styles['TableCell'])],
        [Paragraph('VS Code Extension', styles['TableCell']), Paragraph('One-click install, integrates with Continue.dev', styles['TableCell']), Paragraph('MIT', styles['TableCell'])],
        [Paragraph('CLI Tool', styles['TableCell']), Paragraph('pi-llm chat "Write a function..." - terminal interface', styles['TableCell']), Paragraph('MIT', styles['TableCell'])],
        [Paragraph('Driver', styles['TableCell']), Paragraph('Kernel module for GPIO communication', styles['TableCell']), Paragraph('GPL v2', styles['TableCell'])],
    ]
    story.append(Spacer(1, 12))
    story.append(create_table(sw_data, [3.5*cm, 7.5*cm, 3*cm]))
    story.append(Paragraph('Table 6: Software Ecosystem Components', styles['CaptionText']))
    
    # Go-to-Market
    story.append(Paragraph('GO-TO-MARKET STRATEGY', styles['SectionHeading']))
    
    gtm_data = [
        [Paragraph('<b>Phase</b>', styles['TableHeader']), Paragraph('<b>Duration</b>', styles['TableHeader']), Paragraph('<b>Key Activities</b>', styles['TableHeader']), Paragraph('<b>Target</b>', styles['TableHeader'])],
        [Paragraph('Stealth', styles['TableCell']), Paragraph('Months 1-6', styles['TableCell']), Paragraph('FPGA prototype, quantization, VS Code extension', styles['TableCell']), Paragraph('50 tok/s demo', styles['TableCell'])],
        [Paragraph('Hype', styles['TableCell']), Paragraph('Months 6-9', styles['TableCell']), Paragraph('Landing page, viral videos, pre-orders', styles['TableCell']), Paragraph('500 units sold', styles['TableCell'])],
        [Paragraph('Ship', styles['TableCell']), Paragraph('Months 9-12', styles['TableCell']), Paragraph('MPW tapeout, fulfill orders, open-source SDK', styles['TableCell']), Paragraph('All 500 shipped', styles['TableCell'])],
        [Paragraph('Scale', styles['TableCell']), Paragraph('Year 2', styles['TableCell']), Paragraph('Full production, retail partnerships', styles['TableCell']), Paragraph('5,000 units', styles['TableCell'])],
    ]
    story.append(Spacer(1, 12))
    story.append(create_table(gtm_data, [3*cm, 2.5*cm, 5.5*cm, 4*cm]))
    story.append(Paragraph('Table 7: Go-to-Market Phases', styles['CaptionText']))
    
    # Capital Requirements
    story.append(Paragraph('CAPITAL REQUIREMENTS', styles['SectionHeading']))
    
    cap_data = [
        [Paragraph('<b>Phase</b>', styles['TableHeader']), Paragraph('<b>Duration</b>', styles['TableHeader']), Paragraph('<b>Capital Required</b>', styles['TableHeader']), Paragraph('<b>Key Expenses</b>', styles['TableHeader'])],
        [Paragraph('Feasibility', styles['TableCell']), Paragraph('Months 1-6', styles['TableCell']), Paragraph('$500K', styles['TableCell']), Paragraph('FPGA prototype, ML engineers, quantization', styles['TableCell'])],
        [Paragraph('Design', styles['TableCell']), Paragraph('Months 7-18', styles['TableCell']), Paragraph('$1.5M', styles['TableCell']), Paragraph('RTL design, verification, physical design', styles['TableCell'])],
        [Paragraph('Prototype', styles['TableCell']), Paragraph('Months 19-24', styles['TableCell']), Paragraph('$800K', styles['TableCell']), Paragraph('MPW shuttle, test chips, validation', styles['TableCell'])],
        [Paragraph('Production', styles['TableCell']), Paragraph('Months 25-30', styles['TableCell']), Paragraph('$1.2M', styles['TableCell']), Paragraph('Mask set, initial production, assembly', styles['TableCell'])],
        [Paragraph('<b>Total</b>', styles['TableCell']), Paragraph('<b>30 months</b>', styles['TableCell']), Paragraph('<b>$4M</b>', styles['TableCell']), Paragraph('', styles['TableCell'])],
    ]
    story.append(Spacer(1, 12))
    story.append(create_table(cap_data, [3*cm, 2.5*cm, 2.5*cm, 6*cm]))
    story.append(Paragraph('Table 8: Capital Requirements by Phase', styles['CaptionText']))
    
    # Risk Analysis
    story.append(Paragraph('RISK ANALYSIS', styles['SectionHeading']))
    
    risk_data = [
        [Paragraph('<b>Risk</b>', styles['TableHeader']), Paragraph('<b>Probability</b>', styles['TableHeader']), Paragraph('<b>Impact</b>', styles['TableHeader']), Paragraph('<b>Mitigation</b>', styles['TableHeader'])],
        [Paragraph('Model obsolescence', styles['TableCell']), Paragraph('High (40%)', styles['TableCell']), Paragraph('Critical', styles['TableCell']), Paragraph('Target stable architectures (Llama/Gemma)', styles['TableCell'])],
        [Paragraph('Quantization quality loss', styles['TableCell']), Paragraph('Medium (25%)', styles['TableCell']), Paragraph('High', styles['TableCell']), Paragraph('Hybrid INT4/INT8 for critical layers', styles['TableCell'])],
        [Paragraph('First-silicon bugs', styles['TableCell']), Paragraph('Medium (30%)', styles['TableCell']), Paragraph('High', styles['TableCell']), Paragraph('Comprehensive FPGA prototyping', styles['TableCell'])],
        [Paragraph('Competitive response', styles['TableCell']), Paragraph('High (50%)', styles['TableCell']), Paragraph('Medium', styles['TableCell']), Paragraph('First-mover in sub-$70 LLM segment', styles['TableCell'])],
        [Paragraph('Hailo expands to LLM', styles['TableCell']), Paragraph('Medium (35%)', styles['TableCell']), Paragraph('High', styles['TableCell']), Paragraph('Focus on developer ecosystem lock-in', styles['TableCell'])],
    ]
    story.append(Spacer(1, 12))
    story.append(create_table(risk_data, [3.5*cm, 2.5*cm, 2*cm, 6*cm]))
    story.append(Paragraph('Table 9: Risk Analysis Matrix', styles['CaptionText']))
    
    # What Not to Build
    story.append(Paragraph('WHAT NOT TO BUILD (YET)', styles['SectionHeading']))
    
    nobuild_data = [
        [Paragraph('<b>Feature</b>', styles['TableHeader']), Paragraph('<b>Why Delay</b>', styles['TableHeader']), Paragraph('<b>When to Revisit</b>', styles['TableHeader'])],
        [Paragraph('Thunderbolt 5 tier', styles['TableCell']), Paragraph('Too expensive, too complex, no proven demand', styles['TableCell']), Paragraph('Year 3, if Pi-HAT hits $1M revenue', styles['TableCell'])],
        [Paragraph('SD card version', styles['TableCell']), Paragraph('Lower power = lower capability, harder UX', styles['TableCell']), Paragraph('Year 2, as "Pi-LLM Nano"', styles['TableCell'])],
        [Paragraph('Custom ASIC licensing', styles['TableCell']), Paragraph('No credibility without shipping product', styles['TableCell']), Paragraph('Year 2, after 10K units shipped', styles['TableCell'])],
        [Paragraph('7B+ parameter models', styles['TableCell']), Paragraph('5W power budget insufficient', styles['TableCell']), Paragraph('Future node shrink (22nm)', styles['TableCell'])],
    ]
    story.append(Spacer(1, 12))
    story.append(create_table(nobuild_data, [4*cm, 5.5*cm, 5*cm]))
    story.append(Paragraph('Table 10: Deferred Features', styles['CaptionText']))
    
    # Success Metrics
    story.append(Paragraph('SUCCESS METRICS', styles['SectionHeading']))
    
    metrics_data = [
        [Paragraph('<b>Milestone</b>', styles['TableHeader']), Paragraph('<b>Target</b>', styles['TableHeader']), Paragraph('<b>Timeline</b>', styles['TableHeader'])],
        [Paragraph('FPGA prototype working', styles['TableCell']), Paragraph('50 tok/s on INT4 model', styles['TableCell']), Paragraph('Month 6', styles['TableCell'])],
        [Paragraph('Pre-order signups', styles['TableCell']), Paragraph('500 units sold out', styles['TableCell']), Paragraph('Month 9', styles['TableCell'])],
        [Paragraph('First silicon received', styles['TableCell']), Paragraph('Functional chips from MPW', styles['TableCell']), Paragraph('Month 18', styles['TableCell'])],
        [Paragraph('Units shipped', styles['TableCell']), Paragraph('500 pre-orders fulfilled', styles['TableCell']), Paragraph('Month 24', styles['TableCell'])],
        [Paragraph('Revenue Year 1', styles['TableCell']), Paragraph('$35K (500 units)', styles['TableCell']), Paragraph('End of Year 2', styles['TableCell'])],
        [Paragraph('Revenue Year 2', styles['TableCell']), Paragraph('$350K (5,000 units)', styles['TableCell']), Paragraph('End of Year 3', styles['TableCell'])],
        [Paragraph('Break-even', styles['TableCell']), Paragraph('~130K units cumulative', styles['TableCell']), Paragraph('Year 4-5', styles['TableCell'])],
    ]
    story.append(Spacer(1, 12))
    story.append(create_table(metrics_data, [5*cm, 5*cm, 4.5*cm]))
    story.append(Paragraph('Table 11: Success Metrics and Timeline', styles['CaptionText']))
    
    # Conclusion
    story.append(Paragraph('CONCLUSION', styles['SectionHeading']))
    story.append(Paragraph(
        'The mask-locked inference chip represents a genuine architectural innovation with a clear market gap. The competitive landscape analysis confirms '
        'that no existing product offers meaningful LLM inference at sub-$100 price points with sub-5W power consumption. The Pi-LLM HAT MVP targets this gap '
        'with a focused "one product, one use case" approach modeled on Texas Instruments calculator strategy.',
        styles['BodyPara']
    ))
    story.append(Paragraph(
        'Success probability: 35-40% (typical for semiconductor startups). The window is 18-24 months before competitors adapt their architectures for edge LLM inference. '
        'First-mover advantage in the "sub-$70 offline LLM" category is defensible if you ship within that timeline.',
        styles['BodyPara']
    ))
    story.append(Paragraph(
        'Recommended next step: Proceed with Phase 1 feasibility study ($500K) while simultaneously applying to Silicon Catalyst incubator. '
        'Validate the quantization approach on FPGA before committing to silicon.',
        styles['BodyPara']
    ))
    
    # Build PDF
    doc.build(story)
    print(f"PDF generated: {output_path}")
    return output_path

if __name__ == '__main__':
    build_document()
