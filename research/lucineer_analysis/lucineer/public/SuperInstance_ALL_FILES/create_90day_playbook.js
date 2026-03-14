const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer, 
        AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType, ShadingType, 
        VerticalAlign, PageNumber } = require('docx');
const fs = require('fs');

const colors = {
  primary: "020617",
  body: "1E293B",
  secondary: "64748B",
  accent: "94A3B8",
  tableBg: "F8FAFC",
  tableHeader: "E2E8F0"
};

const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: colors.accent };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 24 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: colors.primary, font: "Times New Roman" },
        paragraph: { spacing: { before: 0, after: 200 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, color: colors.primary, font: "Times New Roman" },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: colors.body, font: "Times New Roman" },
        paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "checkbox-list", levels: [{ level: 0, format: LevelFormat.BULLET, text: "☐", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    properties: {
      page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } }
    },
    headers: {
      default: new Header({ children: [new Paragraph({ 
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "SuperInstance.AI - 90-Day Playbook", color: colors.secondary, size: 20 })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Page ", size: 20 }), new TextRun({ children: [PageNumber.CURRENT], size: 20 }), 
                   new TextRun({ text: " of ", size: 20 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 20 })]
      })] })
    },
    children: [
      // Title
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("90-DAY EXECUTION PLAYBOOK")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        children: [new TextRun({ text: "Phase 1: Foundation & Validation", size: 28, color: colors.secondary })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: "March - June 2026 | Budget: $500K", size: 22, color: colors.accent })] }),

      // Strategic Objectives
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Strategic Objectives")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The 90-day Phase 1 sprint focuses on five critical objectives that de-risk the venture and position the company for successful seed funding close and Series A preparation. Each objective has measurable success criteria and specific ownership.")] }),
      
      new Table({
        columnWidths: [500, 3000, 3000, 2860],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "#", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Objective", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Success Criteria", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Owner", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("1")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Team Assembly")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("VP Mfg + Arch Lead hired")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Founder")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("2")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Technical Validation")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Gate 0 FPGA demo complete")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Arch Lead")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("IP Protection")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("3 provisionals + FTO opinion")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Founder")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("4")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Supply Chain Lock")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("LPDDR4 contract secured")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("VP Mfg")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("5")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Community Foundation")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("GitHub + Discord + SDK")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Founder")] })] })
          ]})
        ]
      }),

      // Week 1-2
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Week 1-2: Critical Foundation")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Day 1 Checklist")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The following actions must be completed on Day 1 to establish momentum:")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Open VP Manufacturing job posting (LinkedIn, SemiWiki)")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Open Architecture Lead job posting (LinkedIn, IEEE)")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Engage patent counsel ($5K retainer)")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Order KV260 development board (~$300)")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Create GitHub organization (github.com/superinstance-ai)")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Create Discord server (discord.gg/superinstance)")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Reserve domain superinstance.ai (~$15)")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Email TeLLMe authors (arXiv:2510.15926)")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Email Tong Yang (PKU) - tongyang@pku.edu.cn")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Apply to Silicon Catalyst incubator")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 VP Manufacturing Hiring Sprint")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The VP Manufacturing hire is CRITICAL and NON-NEGOTIABLE. The candidate must have 5+ successful tape-outs with AI/accelerator background. Compensation: $180-220K base + 2-4% equity + $25-50K signing bonus if needed. Recruiting channels: LinkedIn Recruiter, SemiWiki, Silicon Catalyst network, IEEE Solid-State Circuits Society, direct approach to Groq/Etched/Tenstorrent alums.")] }),

      // Week 3-4
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Week 3-4: Patent Filing & Supply Chain")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Patent Filing Timeline")] }),
      new Table({
        columnWidths: [2000, 4000, 3360],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Day", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Activity", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Deliverable", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Day 8-10")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Finalize P1 claims with counsel")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Claim document")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Day 11-14")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Prepare P1 drawings")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Figure set")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Day 15")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("File P1 provisional")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("USPTO confirmation")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Day 20")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("File P2 provisional (RAU)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("USPTO confirmation")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Day 28")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("File P3 provisional (Hybrid)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("USPTO confirmation")] })] })
          ]})
        ]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 LPDDR4 Supply Contract Engagement")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("Contact strategy for LPDDR4 allocation (CRITICAL due to pricing crisis):")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Primary Target: ", bold: true }), new TextRun("Micron (US-based, CHIPS Act preference)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Secondary Target: ", bold: true }), new TextRun("Samsung (Korean, established relationship)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Contract Requirements: ", bold: true }), new TextRun("50K units committed, $8-10 per 512MB, 24-month NCNR")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Allocation Cost: ", bold: true }), new TextRun("~$500K (refundable against orders)")] }),

      // Week 5-8
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Week 5-8: FPGA Development")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 Gate 0 Milestones")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The Gate 0 FPGA demonstration is the critical technical validation milestone:")] }),
      new Table({
        columnWidths: [2000, 3680, 3680],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Week", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Milestone", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Deliverable", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Week 5")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Environment setup")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("KV260 booted, PYNQ installed")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Week 5")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Model preparation")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("BitNet b1.58-2B-4T validated")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Week 6")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("bitnet.cpp integration")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("CPU inference working")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Week 6")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("FPGA synthesis start")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("RTL targeting KV260")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Week 7")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("First synthesis")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Design compiles, timing met")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Week 7")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Bring-up begins")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Hardware running inference")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Week 8")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Performance validation")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "25+ tok/s, <5W demonstrated", bold: true })] })] })
          ]})
        ]
      }),

      // Week 9-12
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Week 9-12: SDK & Community Launch")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 SDK Alpha Release")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The SDK Alpha release targets PyPI publication with core functionality:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Package Name: ", bold: true }), new TextRun("superinstance")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Version: ", bold: true }), new TextRun("0.1.0a1 (alpha)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "License: ", bold: true }), new TextRun("Apache 2.0")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Python: ", bold: true }), new TextRun("3.8+")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Installation: ", bold: true }), new TextRun("pip install superinstance --pre")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 Community Launch Targets")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("Launch metrics targets for Month 1:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "GitHub Stars: ", bold: true }), new TextRun("500+ (Week 1)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Discord Members: ", bold: true }), new TextRun("300+ (Week 1)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "SDK Downloads: ", bold: true }), new TextRun("1,000+ (Month 1)")] }),

      // Budget
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Budget Allocation")] }),
      new Table({
        columnWidths: [4500, 2500, 2360],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Category", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Amount", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Notes", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Team (3 months)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$145K")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("VP Mfg, Arch Lead, ML Eng")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("IP (Patents + FTO)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$40K")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("3 provisionals + FTO opinion")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Hardware/Equipment")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$12K")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("KV260 boards, test equipment")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Supply Chain Deposit")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$100K")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("LPDDR4 allocation (refundable)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("EDA Tools (6 months)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$50K")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Cadence/Synopsys rental")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Other (Legal, Cloud, Travel)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$53K")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Corporate setup, compute, visits")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "TOTAL PHASE 1 BUDGET", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$500K", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "-", bold: true })] })] })
          ]})
        ]
      }),

      // Exit Criteria
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Phase 1 Exit Criteria")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The following criteria must be met to successfully complete Phase 1 and advance to Phase 2:")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("VP Manufacturing hired (Day 60 max)")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Architecture Lead hired")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("3 provisional patents filed")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("FTO opinion received from counsel")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Gate 0 FPGA demo complete (25+ tok/s, <5W)")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("SDK Alpha published to PyPI")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("LPDDR4 allocation contract secured")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("GlobalFoundries 22FDX engagement initiated")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("500+ GitHub stars")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("300+ Discord members")] }),
      new Paragraph({ numbering: { reference: "checkbox-list", level: 0 }, children: [new TextRun("Seed term sheet received")] }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/z/my-project/download/90Day_Execution_Playbook_v2.docx", buffer);
  console.log("90-Day Execution Playbook created successfully!");
});
