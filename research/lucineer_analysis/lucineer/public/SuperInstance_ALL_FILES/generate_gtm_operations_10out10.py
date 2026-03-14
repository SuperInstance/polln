#!/usr/bin/env python3
"""
SuperInstance.AI GTM & Operations Plan PDF Generator
World-class professional document with tables, charts, and investor-ready formatting
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import os

# Colors
PRIMARY_BLUE = colors.Color(0.13, 0.27, 0.53)  # Dark blue
ACCENT_BLUE = colors.Color(0.25, 0.47, 0.78)   # Lighter blue
LIGHT_BLUE = colors.Color(0.85, 0.90, 0.95)    # Very light blue for backgrounds
DARK_GRAY = colors.Color(0.2, 0.2, 0.2)
MED_GRAY = colors.Color(0.5, 0.5, 0.5)
LIGHT_GRAY = colors.Color(0.95, 0.95, 0.95)
GREEN = colors.Color(0.18, 0.55, 0.34)
ORANGE = colors.Color(0.85, 0.45, 0.1)

def create_styles():
    """Create custom paragraph styles"""
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(ParagraphStyle(
        name='DocTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=PRIMARY_BLUE,
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Subtitle
    styles.add(ParagraphStyle(
        name='DocSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=MED_GRAY,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))
    
    # Section Header (H1)
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=PRIMARY_BLUE,
        spaceBefore=24,
        spaceAfter=12,
        fontName='Helvetica-Bold',
        borderColor=PRIMARY_BLUE,
        borderWidth=0,
        borderPadding=0
    ))
    
    # Subsection Header (H2)
    styles.add(ParagraphStyle(
        name='SubsectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=ACCENT_BLUE,
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    ))
    
    # Body text - override existing
    styles['BodyText'].fontSize = 10
    styles['BodyText'].textColor = DARK_GRAY
    styles['BodyText'].spaceBefore = 4
    styles['BodyText'].spaceAfter = 8
    styles['BodyText'].alignment = TA_JUSTIFY
    styles['BodyText'].leading = 14
    
    # Bullet point
    styles.add(ParagraphStyle(
        name='BulletText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=DARK_GRAY,
        leftIndent=20,
        spaceBefore=2,
        spaceAfter=2,
        leading=13
    ))
    
    # Table header
    styles.add(ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER
    ))
    
    # Table cell
    styles.add(ParagraphStyle(
        name='TableCell',
        parent=styles['Normal'],
        fontSize=9,
        textColor=DARK_GRAY,
        alignment=TA_CENTER
    ))
    
    # Table cell left aligned
    styles.add(ParagraphStyle(
        name='TableCellLeft',
        parent=styles['Normal'],
        fontSize=9,
        textColor=DARK_GRAY,
        alignment=TA_LEFT
    ))
    
    # Footer
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=MED_GRAY,
        alignment=TA_CENTER
    ))
    
    return styles


def create_table(data, col_widths=None, header_rows=1):
    """Create a professionally styled table"""
    table = Table(data, colWidths=col_widths)
    
    style_commands = [
        # Header styling
        ('BACKGROUND', (0, 0), (-1, header_rows-1), PRIMARY_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, header_rows-1), colors.white),
        ('FONTNAME', (0, 0), (-1, header_rows-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, header_rows-1), 9),
        ('ALIGN', (0, 0), (-1, header_rows-1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Body styling
        ('FONTNAME', (0, header_rows), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, header_rows), (-1, -1), 9),
        ('TEXTCOLOR', (0, header_rows), (-1, -1), DARK_GRAY),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, MED_GRAY),
        ('LINEBELOW', (0, header_rows-1), (-1, header_rows-1), 1.5, PRIMARY_BLUE),
        
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]
    
    # Alternating row colors
    for i in range(header_rows, len(data)):
        if i % 2 == 0:
            style_commands.append(('BACKGROUND', (0, i), (-1, i), LIGHT_GRAY))
        else:
            style_commands.append(('BACKGROUND', (0, i), (-1, i), colors.white))
    
    table.setStyle(TableStyle(style_commands))
    return table


def add_header_footer(canvas, doc):
    """Add header and footer to each page"""
    canvas.saveState()
    
    # Header
    canvas.setFillColor(PRIMARY_BLUE)
    canvas.rect(0, letter[1] - 40, letter[0], 40, fill=1, stroke=0)
    
    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(72, letter[1] - 28, "SUPERINSTANCE.AI")
    
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(letter[0] - 72, letter[1] - 28, "Go-to-Market & Operations Plan")
    
    # Footer
    canvas.setFillColor(LIGHT_GRAY)
    canvas.rect(0, 0, letter[0], 35, fill=1, stroke=0)
    
    canvas.setFillColor(MED_GRAY)
    canvas.setFont('Helvetica', 8)
    canvas.drawString(72, 15, f"Confidential | {datetime.now().strftime('%B %Y')}")
    canvas.drawRightString(letter[0] - 72, 15, f"Page {doc.page}")
    
    canvas.restoreState()


def build_document():
    """Build the complete GTM & Operations Plan document"""
    
    output_path = "/home/z/my-project/download/SuperInstance_GTM_Operations_10out10.pdf"
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=60,
        bottomMargin=50
    )
    
    styles = create_styles()
    story = []
    
    # ========== TITLE PAGE ==========
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("SUPERINSTANCE.AI", styles['DocTitle']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Go-to-Market & Operations Plan", styles['DocSubtitle']))
    story.append(Spacer(1, 0.5*inch))
    
    # Executive summary box
    exec_summary = """
    <para align="center">
    <b>Executive Summary</b><br/><br/>
    SuperInstance.AI is positioned to capture the emerging edge AI inference market with a revolutionary 
    hardware-software solution that delivers 10x performance at half the cost of alternatives. 
    This document outlines our comprehensive go-to-market strategy, operational framework, 
    and path to $5M+ in annual revenue within 24 months.
    </para>
    """
    
    # Create a styled box for executive summary
    summary_table = Table([[Paragraph(exec_summary, styles['BodyText'])]], 
                          colWidths=[5.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE),
        ('BOX', (0, 0), (-1, -1), 2, PRIMARY_BLUE),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(summary_table)
    
    story.append(Spacer(1, 0.5*inch))
    
    # Key metrics highlight
    metrics_data = [
        ['$35', '10x', '59-77%', '$5M+'],
        ['Entry Price', 'Performance Gain', 'Target Margins', 'Y2 Revenue Target']
    ]
    metrics_table = Table(metrics_data, colWidths=[1.35*inch]*4)
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), PRIMARY_BLUE),
        ('TEXTCOLOR', (0, 1), (-1, 1), MED_GRAY),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 24),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, 1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 1, PRIMARY_BLUE),
        ('LINEBEFORE', (1, 0), (1, -1), 0.5, MED_GRAY),
        ('LINEBEFORE', (2, 0), (2, -1), 0.5, MED_GRAY),
        ('LINEBEFORE', (3, 0), (3, -1), 0.5, MED_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(metrics_table)
    
    story.append(PageBreak())
    
    # ========== SECTION 1: GTM STRATEGY OVERVIEW ==========
    story.append(Paragraph("1. GTM Strategy Overview", styles['SectionHeader']))
    
    story.append(Paragraph("1.1 Target Customer Segments", styles['SubsectionHeader']))
    story.append(Paragraph(
        "Our go-to-market strategy targets four distinct customer segments, each with unique needs, "
        "price sensitivity, and acquisition approaches. This segmentation allows for precise messaging "
        "and optimized resource allocation.",
        styles['BodyText']
    ))
    
    segments_data = [
        ['Segment', 'Size', 'Characteristics', 'Priority'],
        ['Hobbyist/Maker', '2.1M devs', 'Price-sensitive, community-driven', 'High'],
        ['Professional Edge ML', '600K devs', 'Performance-focused, willing to pay', 'High'],
        ['Enterprise', '200K orgs', 'Volume buyers, need support', 'Medium'],
        ['Education', '8,500 programs', 'Budget-constrained, curriculum needs', 'Medium']
    ]
    story.append(create_table(segments_data, col_widths=[1.4*inch, 1.1*inch, 2.5*inch, 0.9*inch]))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("1.2 Value Proposition by Segment", styles['SubsectionHeader']))
    
    value_props = [
        "<b>Hobbyist:</b> \"AI inference for $35, works in 30 seconds\" — Instant gratification, minimal friction, community support",
        "<b>Professional:</b> \"10x faster inference at half the price\" — Performance benchmarks, reliability, professional support",
        "<b>Enterprise:</b> \"Private, air-gapped LLM with zero cloud costs\" — Security, compliance, volume pricing, dedicated support",
        "<b>Education:</b> \"Complete edge AI curriculum kit\" — Curriculum resources, volume discounts, instructor training"
    ]
    
    for vp in value_props:
        story.append(Paragraph("• " + vp, styles['BulletText']))
    
    story.append(Spacer(1, 0.15*inch))
    
    # ========== SECTION 2: CHANNEL STRATEGY ==========
    story.append(Paragraph("2. Channel Strategy", styles['SectionHeader']))
    
    story.append(Paragraph("2.1 Phase 1: Direct (Months 1-12)", styles['SubsectionHeader']))
    story.append(Paragraph(
        "Initial market entry through direct channels enables maximum margin capture, direct customer feedback, "
        "and brand building. This phase establishes product-market fit and refines messaging.",
        styles['BodyText']
    ))
    
    direct_channels = [
        "<b>E-commerce website:</b> Full-featured online store with instant purchasing, technical documentation, and community forums",
        "<b>Developer community building:</b> Discord server, GitHub presence, and technical blog to build organic awareness",
        "<b>Technical content marketing:</b> Tutorials, benchmark reports, and case studies to establish thought leadership"
    ]
    for ch in direct_channels:
        story.append(Paragraph("• " + ch, styles['BulletText']))
    
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("2.2 Phase 2: Distributors (Months 13-24)", styles['SubsectionHeader']))
    story.append(Paragraph(
        "Scale distribution through established electronics distributors provides market reach and credibility "
        "while maintaining reasonable margins through volume agreements.",
        styles['BodyText']
    ))
    
    dist_data = [
        ['Distributor', 'Focus Area', 'Expected Volume', 'Margin Impact'],
        ['Digi-Key', 'Developer focus', '40% of sales', '-8% margin'],
        ['Mouser', 'Maker focus', '25% of sales', '-8% margin'],
        ['Arrow Electronics', 'Enterprise', '15% of sales', '-12% margin']
    ]
    story.append(create_table(dist_data, col_widths=[1.5*inch, 1.3*inch, 1.3*inch, 1.3*inch]))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("2.3 Phase 3: OEM Partnerships (Months 25-36)", styles['SubsectionHeader']))
    story.append(Paragraph(
        "Strategic OEM partnerships provide high-volume, high-margin revenue streams through embedded solutions.",
        styles['BodyText']
    ))
    
    oem_targets = [
        "<b>Industrial automation vendors:</b> Edge AI for predictive maintenance, quality control, and process optimization",
        "<b>Healthcare device manufacturers:</b> Private, on-device AI for patient monitoring and diagnostics",
        "<b>Robotics companies:</b> Real-time inference for autonomous navigation and manipulation"
    ]
    for target in oem_targets:
        story.append(Paragraph("• " + target, styles['BulletText']))
    
    story.append(PageBreak())
    
    # ========== SECTION 3: CUSTOMER ACQUISITION MODEL ==========
    story.append(Paragraph("3. Customer Acquisition Model", styles['SectionHeader']))
    
    story.append(Paragraph(
        "Our customer acquisition strategy is optimized for each segment's buying behavior, with clear metrics "
        "for channel effectiveness and payback periods.",
        styles['BodyText']
    ))
    
    cac_data = [
        ['Channel', 'CAC', 'Payback', 'Conversion Rate', 'Primary Segment'],
        ['Website/Direct', '$25', '1.5 mo', '1.5%', 'Hobbyist'],
        ['Developer Community', '$35', '2.0 mo', '3.0%', 'Professional'],
        ['Trade Shows', '$150', '4.5 mo', '0.5%', 'Enterprise'],
        ['Distributor Leads', '$75', '2.5 mo', '2.0%', 'All'],
        ['Enterprise Sales', '$400', '6.0 mo', '15%', 'Enterprise']
    ]
    story.append(create_table(cac_data, col_widths=[1.3*inch, 0.8*inch, 0.9*inch, 1.1*inch, 1.3*inch]))
    story.append(Spacer(1, 0.2*inch))
    
    # ========== SECTION 4: SALES CYCLE ANALYSIS ==========
    story.append(Paragraph("4. Sales Cycle Analysis", styles['SectionHeader']))
    
    story.append(Paragraph(
        "Understanding sales cycle dynamics enables accurate revenue forecasting and resource allocation. "
        "Each segment requires tailored engagement strategies.",
        styles['BodyText']
    ))
    
    sales_data = [
        ['Segment', 'Cycle Length', 'Decision Makers', 'Key Objections', 'Closing Strategy'],
        ['Hobbyist', '1-7 days', '1', 'Price, ease of use', 'Demo videos, community proof'],
        ['Professional', '2-4 weeks', '1-2', 'Performance, support', 'Benchmarks, trial program'],
        ['Enterprise', '12-24 weeks', '4-6', 'Security, compliance', 'Pilot program, NDA docs'],
        ['OEM', '18-36 weeks', '5-8', 'Qualification, supply', 'Reference designs, volume commit']
    ]
    story.append(create_table(sales_data, col_widths=[1.1*inch, 1*inch, 1.1*inch, 1.3*inch, 1.5*inch]))
    story.append(Spacer(1, 0.2*inch))
    
    # ========== SECTION 5: PRICING STRATEGY ==========
    story.append(Paragraph("5. Pricing Strategy", styles['SectionHeader']))
    
    story.append(Paragraph("5.1 Product Line Pricing", styles['SubsectionHeader']))
    
    story.append(Paragraph(
        "Our tiered pricing strategy captures maximum willingness-to-pay across segments while maintaining "
        "strong margins through hardware-software integration.",
        styles['BodyText']
    ))
    
    pricing_data = [
        ['Product', 'Model Size', 'Price', 'Target Margin', 'Target Segment'],
        ['Nano', '1B parameters', '$35', '59%', 'Hobbyist/Education'],
        ['Micro', '3B parameters', '$49', '67%', 'Hobbyist/Professional'],
        ['Standard', '7B parameters', '$79', '72%', 'Professional'],
        ['Pro', '13B parameters', '$149', '77%', 'Professional/Enterprise']
    ]
    story.append(create_table(pricing_data, col_widths=[1*inch, 1.2*inch, 0.9*inch, 1.1*inch, 1.5*inch]))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("5.2 Cartridge Pricing", styles['SubsectionHeader']))
    story.append(Paragraph(
        "Software cartridges provide recurring revenue and customer lock-in with minimal marginal cost.",
        styles['BodyText']
    ))
    
    cartridge_data = [
        ['Cartridge Type', 'Price', 'Margin', 'Content'],
        ['Basic (Llama-2-7B)', '$19', '85%', 'Pre-trained open models'],
        ['Premium (Fine-tuned)', '$49', '80%', 'Domain-optimized models'],
        ['Enterprise (Custom)', '$89+', '75%', 'Custom fine-tuned models']
    ]
    story.append(create_table(cartridge_data, col_widths=[1.5*inch, 0.9*inch, 0.9*inch, 2*inch]))
    story.append(Spacer(1, 0.2*inch))
    
    # ========== SECTION 6: MARKETING STRATEGY ==========
    story.append(Paragraph("6. Marketing Strategy", styles['SectionHeader']))
    
    story.append(Paragraph("6.1 Developer Relations", styles['SubsectionHeader']))
    
    devrel_items = [
        "<b>Technical blog and tutorials:</b> Weekly deep-dive content on edge AI deployment, optimization techniques, and use cases",
        "<b>YouTube demo channel:</b> Video tutorials, product demos, and customer success stories",
        "<b>Discord community:</b> Target 10K members for peer support, feature requests, and community building",
        "<b>Conference presence:</b> NeurIPS, TinyML Summit, Embedded World for thought leadership and lead generation"
    ]
    for item in devrel_items:
        story.append(Paragraph("• " + item, styles['BulletText']))
    
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("6.2 Content Marketing", styles['SubsectionHeader']))
    
    content_items = [
        "<b>White papers:</b> Technical deep-dives on edge AI deployment challenges and solutions",
        "<b>Case studies:</b> Early adopter success stories with quantified results",
        "<b>Benchmark comparisons:</b> Head-to-head performance data vs. Jetson, Coral, and cloud alternatives"
    ]
    for item in content_items:
        story.append(Paragraph("• " + item, styles['BulletText']))
    
    story.append(PageBreak())
    
    # ========== SECTION 7: PARTNERSHIP ROADMAP ==========
    story.append(Paragraph("7. Partnership Roadmap", styles['SectionHeader']))
    
    story.append(Paragraph(
        "Strategic partnerships accelerate market penetration and provide access to complementary technologies "
        "and distribution channels.",
        styles['BodyText']
    ))
    
    partnership_data = [
        ['Partner Type', 'Target Partners', 'Timeline', 'Strategic Value'],
        ['Model Partners', 'BitNet, iFairy', 'Q1', 'Technology access, model optimization'],
        ['Tool Partners', 'TensorFlow Lite, ONNX', 'Q2', 'Ecosystem integration, developer adoption'],
        ['Distributors', 'Digi-Key, Arrow', 'Q3-Q4', 'Scale distribution, market reach'],
        ['Cloud Partners', 'AWS IoT, Azure IoT', 'Year 2', 'Enterprise channel, hybrid solutions']
    ]
    story.append(create_table(partnership_data, col_widths=[1.2*inch, 1.5*inch, 0.9*inch, 2.1*inch]))
    story.append(Spacer(1, 0.2*inch))
    
    # ========== SECTION 8: OPERATIONS PLAN ==========
    story.append(Paragraph("8. Operations Plan", styles['SectionHeader']))
    
    story.append(Paragraph("8.1 Manufacturing Flow", styles['SubsectionHeader']))
    
    mfg_flow = [
        "<b>1. MPW Prototype (TSMC 28nm):</b> Initial silicon validation through multi-project wafer run",
        "<b>2. Volume Mask Set Production:</b> Dedicated mask set for volume manufacturing",
        "<b>3. Assembly and Test (OSAT):</b> Package assembly, wire bonding, and initial test",
        "<b>4. Quality Assurance:</b> Burn-in testing, functional verification, and reliability screening",
        "<b>5. Distribution:</b> Inventory management and fulfillment through multiple channels"
    ]
    for step in mfg_flow:
        story.append(Paragraph("• " + step, styles['BulletText']))
    
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("8.2 Supply Chain Strategy", styles['SubsectionHeader']))
    
    supply_data = [
        ['Component', 'Supplier', 'Lead Time', 'Risk Mitigation'],
        ['Wafers', 'TSMC', '12-16 weeks', 'Dual foundry qualification'],
        ['LPDDR4 Memory', 'Samsung/SK Hynix', '16-24 weeks', 'Long-term contracts'],
        ['Packaging', 'ASE/Amkor', '4-6 weeks', 'Multiple OSAT partners']
    ]
    story.append(create_table(supply_data, col_widths=[1.2*inch, 1.4*inch, 1.2*inch, 1.8*inch]))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("8.3 Quality Assurance", styles['SubsectionHeader']))
    
    qa_items = [
        "<b>Built-in self-test (BIST):</b> Integrated test circuits for rapid functional verification",
        "<b>100% functional test:</b> Comprehensive testing of all I/O and inference capabilities",
        "<b>Burn-in testing:</b> Extended stress testing for enterprise SKUs",
        "<b>RMA process:</b> Streamlined return and replacement with <48hr turnaround"
    ]
    for item in qa_items:
        story.append(Paragraph("• " + item, styles['BulletText']))
    
    story.append(Spacer(1, 0.15*inch))
    
    # ========== SECTION 9: CUSTOMER SUCCESS ==========
    story.append(Paragraph("9. Customer Success", styles['SectionHeader']))
    
    story.append(Paragraph("9.1 Support Tiers", styles['SubsectionHeader']))
    
    support_data = [
        ['Tier', 'Response Time', 'Channels', 'Price', 'Target Segment'],
        ['Community', '48 hours', 'Discord, Forum', 'Free', 'Hobbyist'],
        ['Professional', '24 hours', 'Email, Chat', '$49/mo', 'Professional'],
        ['Enterprise', '4 hours', 'Phone, Dedicated', 'Custom', 'Enterprise/OEM']
    ]
    story.append(create_table(support_data, col_widths=[1.1*inch, 1.1*inch, 1.2*inch, 1*inch, 1.3*inch]))
    story.append(Spacer(1, 0.15*inch))
    
    story.append(Paragraph("9.2 Success Metrics", styles['SubsectionHeader']))
    
    success_items = [
        "<b>Target NPS:</b> 60+ (industry-leading for hardware products)",
        "<b>Target resolution time:</b> <24 hours for all paid support tiers",
        "<b>Knowledge base coverage:</b> 90%+ of common issues with self-service solutions"
    ]
    for item in success_items:
        story.append(Paragraph("• " + item, styles['BulletText']))
    
    story.append(PageBreak())
    
    # ========== SECTION 10: KEY MILESTONES ==========
    story.append(Paragraph("10. Key Milestones", styles['SectionHeader']))
    
    story.append(Paragraph(
        "Clear milestones with measurable success criteria enable tracking and accountability. "
        "Each milestone builds toward sustainable growth and market leadership.",
        styles['BodyText']
    ))
    
    milestone_data = [
        ['Milestone', 'Timeline', 'Success Criteria', 'Investment Required'],
        ['Product Launch', 'Month 1', 'Website live, 100 waitlist signups', '$50K'],
        ['First 1K Units', 'Month 6', '$35K revenue, 50 community members', '$200K'],
        ['Channel Launch', 'Month 12', '2 distributors signed, 5K units sold', '$150K'],
        ['Enterprise Pilot', 'Month 18', '5 enterprise customers, 10K units', '$300K'],
        ['100K Units', 'Month 24', '$5M+ revenue, break-even', '$500K']
    ]
    story.append(create_table(milestone_data, col_widths=[1.3*inch, 1*inch, 2.2*inch, 1.1*inch]))
    story.append(Spacer(1, 0.3*inch))
    
    # Investment Summary Box
    investment_summary = """
    <para align="center">
    <b>Investment Summary</b><br/><br/>
    Total capital required to reach profitability: <b>$1.2M</b><br/>
    Projected Y2 annual revenue: <b>$5M+</b><br/>
    Target gross margin: <b>65-75%</b><br/>
    Expected break-even: <b>Month 24</b>
    </para>
    """
    
    invest_table = Table([[Paragraph(investment_summary, styles['BodyText'])]], 
                         colWidths=[5*inch])
    invest_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.9, 0.95, 0.9)),
        ('BOX', (0, 0), (-1, -1), 2, GREEN),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
    ]))
    story.append(invest_table)
    
    story.append(Spacer(1, 0.3*inch))
    
    # Closing statement
    story.append(Paragraph("Strategic Priorities", styles['SubsectionHeader']))
    story.append(Paragraph(
        "The SuperInstance.AI go-to-market strategy is designed for rapid market penetration while building "
        "sustainable competitive advantages through community engagement, strategic partnerships, and "
        "operational excellence. Our phased approach reduces risk while maximizing learning and adaptation "
        "opportunities. The combination of attractive pricing, strong margins, and clear market positioning "
        "positions SuperInstance.AI for category leadership in the emerging edge AI inference market.",
        styles['BodyText']
    ))
    
    # Build the document
    doc.build(story, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    
    print(f"✅ PDF generated successfully: {output_path}")
    return output_path


if __name__ == "__main__":
    build_document()
