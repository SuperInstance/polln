const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer, 
        AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType, ShadingType, 
        VerticalAlign, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

const colors = {
  primary: "26211F",
  body: "3D3735",
  secondary: "6B6361",
  accent: "C19A6B",
  tableBg: "FDFCFB",
  tableHeader: "F5F0EB"
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
        children: [new TextRun({ text: "SuperInstance.AI - Investment Memorandum", color: colors.secondary, size: 20 })]
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
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("INVESTMENT MEMORANDUM")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        children: [new TextRun({ text: "Mask-Locked Inference Chip", size: 28, color: colors.secondary })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: "Series Seed Investment Opportunity | March 2026", size: 22, color: colors.accent })] }),

      // Investment Summary Table
      new Table({
        columnWidths: [4680, 4680],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "Investment Score", bold: true })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "5.5/10 - CONDITIONALLY INVESTABLE", bold: true, color: colors.accent })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "Seed Round Size", bold: true })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("$2-3M")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "Pre-Money Valuation", bold: true })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("$15-22M (Recommended: $18-22M)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "Expected Exit Value", bold: true })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("$135M (3-5 year horizon)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "Risk-Adjusted IRR", bold: true })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("38-45%")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "Success Probability", bold: true })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("35-40% (typical for semiconductor startups)")] })] })
          ]})
        ]
      }),

      // Executive Summary
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Investment Thesis")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("SuperInstance.AI is developing a mask-locked inference chip that physically embeds neural network weights into silicon metal interconnect layers. This architectural innovation eliminates the memory bottleneck inherent in all conventional AI accelerators, achieving order-of-magnitude improvements in power efficiency and cost for edge AI inference. The technology has been validated through FPGA reference implementation (25 tok/s at 4.8W) and targets a clear market gap: sub-$50, sub-5W LLM inference hardware.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The investment opportunity is predicated on three key factors: (1) validated technical approach with working FPGA prototype, (2) clear market gap with 12-18 month first-mover window, and (3) strategic value to potential acquirers (Qualcomm 50-60% acquisition probability). The primary risk is execution—the founder lacks tape-out experience and must hire a VP Manufacturing with semiconductor expertise within 60 days of funding.")] }),

      // Market Opportunity
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Market Opportunity")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Total Addressable Market")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The edge AI chip market is projected to grow from $3.67 billion in 2025 to $11.54 billion by 2030, representing a 25.7% CAGR. Within this market, the specific segment for LLM inference at the edge is nascent but rapidly emerging as small language models achieve sufficient capability for edge deployment. The convergence of privacy regulations, model capability, and power constraints creates a unique market timing.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 Competitive Gap Analysis")] }),
      new Table({
        columnWidths: [2000, 1500, 1500, 1500, 2860],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Competitor", bold: true, size: 20 })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Price", bold: true, size: 20 })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Power", bold: true, size: 20 })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "LLM Perf", bold: true, size: 20 })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Gap", bold: true, size: 20 })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "NVIDIA Jetson Orin", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$250", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "7-15W", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Good", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "7x cheaper target", size: 20 })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Hailo-10H", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$88", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "2.5W", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Poor", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "5x better LLM perf", size: 20 })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Google Coral", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$70", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "2W", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "None", size: 20 })] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "No LLM support", size: 20 })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "SuperInstance (Target)", bold: true, size: 20 })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$35-60", bold: true, size: 20 })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "2-5W", bold: true, size: 20 })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Good", bold: true, size: 20 })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "MARKET GAP", bold: true, size: 20 })] })] })
          ]})
        ]
      }),

      // Unit Economics
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Unit Economics")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Cost Structure")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The cost structure analysis has been updated with confirmed LPDDR4 pricing of $10-12 per 512MB unit (not the original $5 estimate). This represents a critical input to COGS calculations and has been incorporated into the financial model. At 10K unit volume, the estimated COGS for the 3B parameter product is $19-31, with 55-65% gross margin sustainable across product variants.")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Product Line Economics")] }),
      new Table({
        columnWidths: [2000, 1800, 1800, 1800, 1960],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Product", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Model Size", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Target COGS", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Target ASP", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Gross Margin", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Nano")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("1B params")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$8-10")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$15")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("33-47%")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Micro")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3B params")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$19-31")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$35")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("55-65%")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Standard")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("7B params")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$25-35")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$60")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("58-71%")] })] })
          ]})
        ]
      }),

      // Funding Requirements
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Funding Requirements")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 Capital Roadmap")] }),
      new Table({
        columnWidths: [2000, 2000, 2000, 3360],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Stage", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Amount", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Timeline", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Key Milestones", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Seed")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$2-3M")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Months 1-12")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Team, FPGA prototype, patents, SDK")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Series A")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$6-8M")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Months 13-30")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("MPW tapeout, verification, expansion")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Series B")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$12-15M")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Months 31-48")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Volume production, sales/marketing")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "Total to Revenue", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$20-26M", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "4 years", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "Breakeven at Year 3", bold: true })] })] })
          ]})
        ]
      }),

      // Exit Analysis
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Exit Analysis")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Exit Scenarios")] }),
      new Table({
        columnWidths: [2000, 1500, 2000, 3860],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Scenario", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Probability", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Exit Value", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "IRR", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Bull Case")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("20%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$300-500M")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("85-120%")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Base Case")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("45%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$100-200M")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("35-55%")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Bear Case")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("25%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$30-80M")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("0-15%")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "Expected Value", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "-", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$135M", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "38-45%", bold: true })] })] })
          ]})
        ]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 Acquisition Targets")] }),
      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun("Based on recent M&A activity in the AI chip space, the most likely acquirers are:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Qualcomm (50-60% probability): ", bold: true }), new TextRun("Recently acquired Alphawave ($2.4B), actively building edge AI portfolio. SuperInstance complements their mobile/IoT strategy.")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "MediaTek (40-50% probability): ", bold: true }), new TextRun("Growing edge AI presence, need for differentiated LLM inference capability.")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Apple (30-40% probability): ", bold: true }), new TextRun("Secretive edge AI chip efforts, acquisition of DarwinAI ($100M) indicates interest.")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Intel/NVIDIA (20-30% probability): ", bold: true }), new TextRun("Strategic interest in edge inference, but less focused on ultra-low power segment.")] }),

      // Investment Terms
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Proposed Investment Terms")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The recommended investment structure includes staged milestones to de-risk the investment while providing sufficient capital for execution:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Round Size: ", bold: true }), new TextRun("$2-3M Seed")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Pre-Money Valuation: ", bold: true }), new TextRun("$18-22M (maximum recommended)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Security Type: ", bold: true }), new TextRun("Preferred Stock with 1x liquidation preference")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Pro-Rata Rights: ", bold: true }), new TextRun("Standard for Series A participation")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Board Seat: ", bold: true }), new TextRun("1 investor-designated board member")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Founder Vesting: ", bold: true }), new TextRun("4-year vesting with 1-year cliff")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Milestone Structure: ", bold: true }), new TextRun("Staged releases tied to VP Mfg hire, FPGA demo, patent filings")] }),

      // Critical Conditions
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Critical Investment Conditions")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("Investment is CONDITIONAL on the following milestones being achieved within specified timeframes:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "VP Manufacturing Hire (Day 60): ", bold: true }), new TextRun("MUST hire semiconductor executive with 5+ tape-out experience. $1M milestone release upon hire.")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "SDK Publication (Day 60): ", bold: true }), new TextRun("Alpha version must be published to PyPI with working inference demonstration.")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Gate 0 FPGA Demo (Day 90): ", bold: true }), new TextRun("Demonstration of 25+ tok/s at <5W on AMD KV260 platform.")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Patent Filings (Day 30): ", bold: true }), new TextRun("Three provisional patents filed for core IP protection.")] }),

      // Conclusion
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. Investment Recommendation")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun({ text: "VERDICT: CONDITIONAL INVEST ", bold: true, color: colors.accent }), new TextRun("at $18-22M pre-money valuation.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The Mask-Locked Inference Chip represents a genuine architectural innovation with clear market positioning. The technology is validated (TeLLMe FPGA reference), the market gap is real (no sub-$50 LLM edge hardware), and the strategic value to acquirers is demonstrable. The primary risk—execution capability—is addressable through the mandatory VP Manufacturing hire.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The 12-18 month first-mover window creates urgency. Investment should proceed with staged milestone structure to protect capital while enabling rapid execution.")] }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/z/my-project/download/Investment_Memorandum_v2.docx", buffer);
  console.log("Investment Memorandum created successfully!");
});
