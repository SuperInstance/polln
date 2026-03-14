const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle, 
        WidthType, ShadingType, VerticalAlign, PageNumber } = require('docx');
const fs = require('fs');

const colors = {
  primary: "020617",
  body: "1E293B",
  secondary: "64748B",
  accent: "94A3B8",
  tableBg: "F8FAFC",
  tableHeader: "E2E8F0",
  speculative: "7C3AED"  // Purple for speculative concepts
};

const tableBorder = { style: BorderStyle.SINGLE, size: 8, color: colors.secondary };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };
const headerBorders = { top: tableBorder, bottom: tableBorder, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } };

function createCell(text: string, options: any = {}) {
  const { bold = false, width = 2340, header = false, align = AlignmentType.LEFT, color = null } = options;
  return new TableCell({
    borders: header ? headerBorders : cellBorders,
    width: { size: width, type: WidthType.DXA },
    shading: header ? { fill: colors.tableHeader, type: ShadingType.CLEAR } : { fill: colors.tableBg, type: ShadingType.CLEAR },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: align,
      spacing: { before: 60, after: 60 },
      children: [new TextRun({ text, bold: bold || header, size: 20, color: color || (bold || header ? colors.primary : colors.body) })]
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
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [{
    properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "Fracturable Wafer Architecture | Research & Development", size: 18, color: colors.secondary })]
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
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("Fracturable Wafer Architecture")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
        children: [new TextRun({ text: "Multi-Agent Silicon with Configurable Post-Manufacturing Dicing", size: 28, color: colors.body })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
        children: [new TextRun({ text: "\"CrewAI at the Metal\" - Conceptual Architecture Analysis", size: 22, italics: true, color: colors.secondary })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: "Research Document | January 2025", size: 20, color: colors.secondary })] }),

      // EXECUTIVE SUMMARY
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Executive Summary")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "This document analyzes a novel concept: designing semiconductor wafers with multiple mask-locked neural network models arranged in configurable tiles that can be either kept together as a unified multi-model accelerator or separated into individual chips through selective dicing. The approach would enable a single wafer design to serve multiple product configurations: a unified \"swarm\" chip with multiple specialized models (vision, reasoning, language), separate individual chips for each model, or defect-tolerant configurations that disable problematic tiles.", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "This concept draws parallels to software multi-agent frameworks like CrewAI and AutoGen, but implements the orchestration at the silicon level. A single wafer could contain SmolVLM for vision, multiple FunctionGemma instances for tool calling, and specialized reasoning models\u2014all configurable through post-manufacturing dicing decisions.", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Assessment: ", bold: true, color: colors.primary }),
        new TextRun({ text: "The concept is technically feasible but requires significant architectural innovation. No existing product implements this exact approach. Key enabling technologies (UCIe chiplet interconnects, wafer-scale integration, defect-tolerant design) are verified, but their combination into a \"fracturable\" architecture is novel and requires further research. This document clearly distinguishes between verified technologies and speculative extensions.", color: colors.body })
      ]}),

      // CONCEPT DEFINITION
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Concept Definition")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 Core Idea")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The \"Fracturable Wafer\" concept proposes designing a single photomask set that produces wafers containing multiple neural network inference engines, each mask-locked to a specific model. The key innovation is that these engines can be configured post-manufacturing through selective dicing:", color: colors.body })
      ]}),

      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-1", level: 0 },
        children: [new TextRun({ text: "Unified Configuration: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Keep the wafer section intact as a single multi-model accelerator with multiple specialized models communicating on-chip", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-1", level: 0 },
        children: [new TextRun({ text: "Distributed Configuration: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Dice the wafer into separate chips, each containing one model, for deployment across multiple devices", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-1", level: 0 },
        children: [new TextRun({ text: "Swarm Configuration: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Dice into multiple instances of the same model plus an orchestrator for parallel processing", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "numbered-1", level: 0 },
        children: [new TextRun({ text: "Defect-Tolerant Configuration: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Disable tiles that fail wafer-level testing, dicing around defects to salvage functional models", color: colors.body })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 Example Multi-Agent Tile Layout")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "A conceptual wafer tile arrangement for multi-agent AI:", color: colors.body })
      ]}),

      // Tile Layout Table
      new Table({
        columnWidths: [2200, 2200, 2200, 2760],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Tile", { header: true, width: 2200, align: AlignmentType.CENTER }),
            createCell("Model", { header: true, width: 2200, align: AlignmentType.CENTER }),
            createCell("Parameters", { header: true, width: 2200, align: AlignmentType.CENTER }),
            createCell("Function", { header: true, width: 2760, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("Tile A", { width: 2200, bold: true }),
            createCell("SmolVLM", { width: 2200 }),
            createCell("2B (INT4)", { width: 2200, align: AlignmentType.CENTER }),
            createCell("Vision understanding, VQA", { width: 2760 })
          ]}),
          new TableRow({ children: [
            createCell("Tile B", { width: 2200, bold: true }),
            createCell("FunctionGemma x3", { width: 2200 }),
            createCell("270M x 3 (INT4)", { width: 2200, align: AlignmentType.CENTER }),
            createCell("Tool calling, API invocation", { width: 2760 })
          ]}),
          new TableRow({ children: [
            createCell("Tile C", { width: 2200, bold: true }),
            createCell("Reasoner Model", { width: 2200 }),
            createCell("1B (INT4)", { width: 2200, align: AlignmentType.CENTER }),
            createCell("Chain-of-thought reasoning", { width: 2760 })
          ]}),
          new TableRow({ children: [
            createCell("Tile D", { width: 2200, bold: true }),
            createCell("Orchestrator", { width: 2200 }),
            createCell("500M (INT4)", { width: 2200, align: AlignmentType.CENTER }),
            createCell("Agent routing, task dispatch", { width: 2760 })
          ]}),
          new TableRow({ children: [
            createCell("Tile E", { width: 2200, bold: true }),
            createCell("Conversationalist", { width: 2200 }),
            createCell("1B (INT4)", { width: 2200, align: AlignmentType.CENTER }),
            createCell("Natural language output", { width: 2760 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 1: Example tile layout for multi-agent silicon configuration", size: 18, italics: true, color: colors.secondary })] }),

      // ENABLING TECHNOLOGIES
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Verified Enabling Technologies")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The fracturable wafer concept builds on several verified technologies. The following sections document what exists today versus what would require innovation.", color: colors.body })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 UCIe Chiplet Interconnect (VERIFIED)")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The Universal Chiplet Interconnect Express (UCIe) standard provides die-to-die connectivity that could enable communication between separated tiles:", color: colors.body })
      ]}),

      // UCIe Specs Table
      new Table({
        columnWidths: [3000, 3200, 3160],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Specification", { header: true, width: 3000, align: AlignmentType.CENTER }),
            createCell("UCIe 2.0", { header: true, width: 3200, align: AlignmentType.CENTER }),
            createCell("UCIe 3.0", { header: true, width: 3160, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("Data Rate", { width: 3000, bold: true }),
            createCell("Up to 32 GT/s", { width: 3200 }),
            createCell("48 GT/s and 64 GT/s", { width: 3160 })
          ]}),
          new TableRow({ children: [
            createCell("Bandwidth", { width: 3000, bold: true }),
            createCell("Up to 2 Tbps", { width: 3200 }),
            createCell("Up to 4 Tbps (64 lanes)", { width: 3160 })
          ]}),
          new TableRow({ children: [
            createCell("Source", { width: 3000, bold: true }),
            createCell("Wikipedia; UCIe Consortium", { width: 3200 }),
            createCell("UCIe 3.0 Specification (2025)", { width: 3160 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 2: UCIe interconnect specifications (verified from uciexpress.org)", size: 18, italics: true, color: colors.secondary })] }),

      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Relevance: ", bold: true, color: colors.primary }),
        new TextRun({ text: "UCIe could enable tiles diced apart to communicate when packaged together on an interposer. However, UCIe requires specific packaging (2.5D or 3D) that adds cost. Standard dicing streets do not include UCIe pads\u2014this would require architectural innovation.", color: colors.body })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 Wafer-Scale Integration (VERIFIED)")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Cerebras Systems demonstrates that keeping an entire wafer functional is possible:", color: colors.body })
      ]}),

      // Cerebras Table
      new Table({
        columnWidths: [3500, 5860],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Attribute", { header: true, width: 3500, align: AlignmentType.CENTER }),
            createCell("Cerebras WSE-3 (2024)", { header: true, width: 5860, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("Die Size", { width: 3500, bold: true }),
            createCell("46,255 mm\u00b2 (entire wafer)", { width: 5860 })
          ]}),
          new TableRow({ children: [
            createCell("Transistors", { width: 3500, bold: true }),
            createCell("4 trillion", { width: 5860 })
          ]}),
          new TableRow({ children: [
            createCell("AI Compute", { width: 3500, bold: true }),
            createCell("125 petaflops", { width: 5860 })
          ]}),
          new TableRow({ children: [
            createCell("On-Chip Memory", { width: 3500, bold: true }),
            createCell("44 GB", { width: 5860 })
          ]}),
          new TableRow({ children: [
            createCell("Cores", { width: 3500, bold: true }),
            createCell("900,000", { width: 5860 })
          ]}),
          new TableRow({ children: [
            createCell("Source", { width: 3500, bold: true }),
            createCell("cerebras.ai; arXiv:2503.11698 (March 2025)", { width: 5860 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 3: Cerebras WSE-3 specifications (verified from official sources)", size: 18, italics: true, color: colors.secondary })] }),

      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Key Insight: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Cerebras solves the reticle limit problem by stitching across reticle boundaries using specialized interconnect. They do NOT dice the wafer. The fracturable wafer concept would need similar inter-stitch capability but with the ability to sever connections cleanly.", color: colors.body })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.3 Known Good Die and Wafer-Level Testing (VERIFIED)")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Semiconductor manufacturing uses wafer-level testing to identify functional die before packaging:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Wafer Probe Testing: Electrical tests performed on each die while still on the wafer", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Known Good Die (KGD): Die that pass all tests before packaging, critical for multi-chip modules", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Defect Mapping: Failed die are mapped and excluded from packaging (Source: FormFactor, Feb 2025; IEEE EPS Best-Known-Methods)", color: colors.body })] }),

      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Relevance: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Wafer-level testing could identify which tiles are functional. The fracturable wafer would need test infrastructure per tile, enabling decisions about which dicing pattern to use based on defect map.", color: colors.body })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.4 Defect-Tolerant Architecture (VERIFIED)")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Academic research demonstrates redundancy techniques for yield improvement:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "N+M Redundancy: Provide M spare cores for N-core processors (ScienceDirect, 2007, 39 citations)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Core-Level Redundancy: Spare cores replace defective ones at boot time (UT Austin ICCD 2003, 212 citations)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Self-Organizing Arrays: Chip self-organization for fault tolerance (LAAS Toulouse, 53 citations)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Yield Improvement Framework: ACM DAC 2022 framework for synthesizing defect-tolerant netlists", color: colors.body })] }),

      // SPECULATIVE INNOVATION
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Speculative Innovation Requirements")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The following sections identify what would need to be invented or significantly adapted to realize the fracturable wafer concept. These are ", color: colors.body }),
        new TextRun({ text: "NOT verified technologies", bold: true, color: colors.speculative }),
        new TextRun({ text: " but rather research directions requiring investigation.", color: colors.body })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Active Scribe Lines (SPECULATIVE)")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Current State: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Dicing streets (scribe lines) between chips are passive areas, typically 30-150\u00b5m wide, containing no active circuitry. They exist solely for the saw blade or laser to cut through.", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Required Innovation: ", bold: true, color: colors.speculative }),
        new TextRun({ text: "Design scribe lines that contain interconnect traces connecting adjacent tiles. These traces would need to:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-2", level: 0 },
        children: [new TextRun({ text: "Function when intact (unified configuration)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-2", level: 0 },
        children: [new TextRun({ text: "Sever cleanly without damaging adjacent tiles (diced configuration)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "numbered-2", level: 0 },
        children: [new TextRun({ text: "Potentially reconnect through packaging (separate chips on interposer)", color: colors.body })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Per-Tile Power Domains (SPECULATIVE)")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Current State: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Power distribution typically spans entire die. Power gates exist at macro-block level but not typically at tile boundaries designed for physical separation.", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Required Innovation: ", bold: true, color: colors.speculative }),
        new TextRun({ text: "Independent power domains per tile with power pads accessible from multiple edges. When diced, each tile would need its own power connection capability. This requires power grid redesign with isolation at scribe lines.", color: colors.body })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 Reconfigurable Interconnect Fabric (SPECULATIVE)")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Current State: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Cerebras uses a fixed mesh network across the wafer. Chiplets use UCIe for communication, but UCIe connections are fixed at design time.", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Required Innovation: ", bold: true, color: colors.speculative }),
        new TextRun({ text: "A routing fabric that adapts to tile configuration. If tiles are kept together, the fabric routes internally. If tiles are separated, the fabric provides external I/O for package-level interconnect. This could draw inspiration from FPGA programmable interconnect, but for post-manufacturing physical configuration.", color: colors.body })
      ]}),

      // MULTI-AGENT SILICON PATTERNS
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Multi-Agent Silicon Patterns")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The fracturable wafer concept draws inspiration from software multi-agent frameworks. The following patterns map software concepts to silicon implementation:", color: colors.body })
      ]}),

      // Pattern Table
      new Table({
        columnWidths: [2200, 3300, 3860],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Pattern", { header: true, width: 2200, align: AlignmentType.CENTER }),
            createCell("Software (CrewAI/AutoGen)", { header: true, width: 3300, align: AlignmentType.CENTER }),
            createCell("Silicon Implementation", { header: true, width: 3860, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("Orchestrator-Worker", { width: 2200, bold: true }),
            createCell("Central agent dispatches tasks to workers", { width: 3300 }),
            createCell("Orchestrator tile routes to multiple identical worker tiles", { width: 3860 })
          ]}),
          new TableRow({ children: [
            createCell("Specialist Team", { width: 2200, bold: true }),
            createCell("Agents with different skills collaborate", { width: 3300 }),
            createCell("Vision + Reasoner + Linguist tiles with inter-tile communication", { width: 3860 })
          ]}),
          new TableRow({ children: [
            createCell("Hierarchical", { width: 2200, bold: true }),
            createCell("Manager agents oversee worker agents", { width: 3300 }),
            createCell("Multi-level tile hierarchy with routing fabric", { width: 3860 })
          ]}),
          new TableRow({ children: [
            createCell("Peer-to-Peer", { width: 2200, bold: true }),
            createCell("Agents negotiate without central controller", { width: 3300 }),
            createCell("Mesh-connected tiles with distributed routing", { width: 3860 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 4: Software multi-agent patterns mapped to silicon architecture", size: 18, italics: true, color: colors.secondary })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 Example: Orchestrator-Worker Configuration")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Configuration: One orchestrator tile (500M params, INT4) + 4-8 worker tiles (1B params each, INT4, identical model).", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Unified: All tiles on single chip, orchestrator routes tasks to workers via on-chip network", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Distributed: Each worker diced into separate chip, connected via UCIe on interposer or Thunderbolt cable", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Defect Tolerance: If worker tile 3 fails testing, dice around it; system operates with 3 workers", color: colors.body })] }),

      // VERIFIED MODEL OPTIONS
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Verified Model Options for Tiles")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The following open models are suitable for mask-locked tile implementation:", color: colors.body })
      ]}),

      // Models Table
      new Table({
        columnWidths: [2200, 1800, 2000, 3360],
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            createCell("Model", { header: true, width: 2200, align: AlignmentType.CENTER }),
            createCell("Params", { header: true, width: 1800, align: AlignmentType.CENTER }),
            createCell("INT4 Size", { header: true, width: 2000, align: AlignmentType.CENTER }),
            createCell("Function / Source", { header: true, width: 3360, align: AlignmentType.CENTER })
          ]}),
          new TableRow({ children: [
            createCell("SmolVLM", { width: 2200, bold: true }),
            createCell("2B", { width: 1800, align: AlignmentType.CENTER }),
            createCell("~500 MB", { width: 2000, align: AlignmentType.CENTER }),
            createCell("Vision-Language; Hugging Face Nov 2024", { width: 3360 })
          ]}),
          new TableRow({ children: [
            createCell("FunctionGemma", { width: 2200, bold: true }),
            createCell("270M", { width: 1800, align: AlignmentType.CENTER }),
            createCell("~70 MB", { width: 2000, align: AlignmentType.CENTER }),
            createCell("Function calling; Google Dec 2025", { width: 3360 })
          ]}),
          new TableRow({ children: [
            createCell("Gemma 3n", { width: 2200, bold: true }),
            createCell("Varies", { width: 1800, align: AlignmentType.CENTER }),
            createCell("Varies", { width: 2000, align: AlignmentType.CENTER }),
            createCell("Multimodal edge; Google May 2025", { width: 3360 })
          ]}),
          new TableRow({ children: [
            createCell("Qwen2.5-0.5B", { width: 2200, bold: true }),
            createCell("500M", { width: 1800, align: AlignmentType.CENTER }),
            createCell("~125 MB", { width: 2000, align: AlignmentType.CENTER }),
            createCell("General purpose; open weights", { width: 3360 })
          ]}),
          new TableRow({ children: [
            createCell("Phi-3 Mini", { width: 2200, bold: true }),
            createCell("3.8B", { width: 1800, align: AlignmentType.CENTER }),
            createCell("~1 GB", { width: 2000, align: AlignmentType.CENTER }),
            createCell("Reasoning; Microsoft", { width: 3360 })
          ]})
        ]
      }),
      new Paragraph({ spacing: { before: 120, after: 200 }, alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Table 5: Open models suitable for mask-locked tile implementation (verified from official sources)", size: 18, italics: true, color: colors.secondary })] }),

      // TECHNICAL CHALLENGES
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Technical Challenges and Open Questions")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.1 Manufacturing Challenges")] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-3", level: 0 },
        children: [new TextRun({ text: "Scribe Line Integrity: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Active interconnects in scribe lines may not survive dicing cleanly. Research needed on \"breakaway\" interconnect designs.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-3", level: 0 },
        children: [new TextRun({ text: "Power Grid Redesign: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Per-tile power domains require redesign of traditional power distribution networks.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "numbered-3", level: 0 },
        children: [new TextRun({ text: "Testing Complexity: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Each tile needs independent test access, plus inter-tile communication testing for unified configurations.", color: colors.body })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.2 Architecture Challenges")] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-4", level: 0 },
        children: [new TextRun({ text: "Inter-Tile Communication Bandwidth: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Multi-agent collaboration requires high-bandwidth communication. UCIe 3.0 provides up to 4 Tbps, but is this sufficient for token-level collaboration?", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "numbered-4", level: 0 },
        children: [new TextRun({ text: "Latency for Agent Orchestration: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Software agents typically communicate with millisecond latency. On-chip communication is nanosecond scale, but package-level communication (for diced configurations) may introduce bottlenecks.", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "numbered-4", level: 0 },
        children: [new TextRun({ text: "Memory Sharing: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Should tiles share activation memory or maintain separate memory pools? Shared memory is efficient but creates dicing complexity.", color: colors.body })] }),

      // PATENT LANDSCAPE
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Related Patent Landscape")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "A relevant patent exists in this space:", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "US Patent 5,107,146 (1992): \"Mixed Mode Analog/Digital Programmable Interconnect Architecture\" (Actel Corporation)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Field Programmable Platform Array: Patent describing wafer-level programmable interconnect (Google Patents reference)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Note: ", bold: true, color: colors.primary }),
        new TextRun({ text: "The fracturable wafer concept differs from existing patents in that it combines: (1) mask-locked neural network weights, (2) multiple different models per wafer, (3) selective dicing for configuration. A patent search by qualified counsel would be required before filing.", color: colors.body })
      ]}),

      // RESEARCH ROADMAP
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. Research Roadmap")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "To validate the fracturable wafer concept, the following research steps are recommended:", color: colors.body })
      ]}),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 1: Architecture Feasibility (Months 1-3)")] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Design tile architecture with UCIe-compatible edge pads", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Simulate inter-tile communication bandwidth requirements for multi-agent patterns", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Survey packaging options for post-dice reconnection (interposer, multi-chip module)", color: colors.body })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 2: Physical Design Exploration (Months 4-6)")] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Engage with packaging vendors on scribe-line interconnect feasibility", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Design per-tile power domain architecture", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Evaluate OpenROAD for tile-based design flow", color: colors.body })] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 3: Prototype Implementation (Months 7-12)")] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Design 2-tile test chip with configurable interconnect", color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Submit to MPW shuttle (TinyTapeout or similar)", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Validate dicing and post-dice communication", color: colors.body })] }),

      // VERIFICATION APPENDIX
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Appendix: Source Verification Index")] }),

      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "UCIe Specifications:", bold: true, color: colors.primary })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "UCIe Consortium: uciexpress.org/specifications (UCIe 3.0: 48/64 GT/s)", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "IEEE Micro 2024: \"UCIe: Standard for an Open Chiplet Ecosystem\"", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 120 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Synopsys: \"The Road to 64G UCIe IP\" (4 Tbps bandwidth claim)", size: 18, color: colors.body })] }),

      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Cerebras WSE-3:", bold: true, color: colors.primary })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Official: cerebras.ai/chip (46,255 mm\u00b2, 4T transistors, 125 PF)", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "arXiv:2503.11698 (March 2025): WSE-3 comparison study", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 120 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Hot Chips 2024: Cerebras presentation slides", size: 18, color: colors.body })] }),

      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Edge AI Models:", bold: true, color: colors.primary })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "SmolVLM: Hugging Face blog (Nov 26, 2024), arXiv:2504.05299", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "FunctionGemma: Google AI blog (Dec 18, 2025), ai.google.dev/gemma", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 120 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "Gemma 3n: Google Developers Blog (May 20, 2025)", size: 18, color: colors.body })] }),

      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "Defect Tolerance Research:", bold: true, color: colors.primary })
      ]}),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "UT Austin ICCD 2003: \"Exploiting Microarchitectural Redundancy\" (212 citations)", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 60 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "ACM DAC 2022: \"A defect tolerance framework for improving yield\"", size: 18, color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun({ text: "IEEE TDSC: \"Chip Self-Organization and Fault-Tolerance\" (53 citations)", size: 18, color: colors.body })] }),

      // CONCLUSION
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Conclusion")] }),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The fracturable wafer concept represents a potentially novel approach to semiconductor architecture for multi-agent AI. It combines verified technologies (UCIe chiplet interconnects, wafer-scale integration, defect-tolerant design) with speculative innovations (active scribe lines, per-tile power domains, reconfigurable interconnect fabric).", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 120 }, children: [
        new TextRun({ text: "The concept aligns with current industry trends toward chiplet-based design and multi-agent AI systems. If feasible, it would enable a single wafer design to serve multiple product configurations\u2014unified multi-model accelerators, distributed agent swarms, or defect-tolerant configurations\u2014while sharing a common mask set.", color: colors.body })
      ]}),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "Next Steps: ", bold: true, color: colors.primary }),
        new TextRun({ text: "Engage with semiconductor packaging vendors to assess feasibility of active scribe lines and post-dice interconnect options. Begin architecture simulation for inter-tile communication patterns. Consider filing provisional patent application given novelty of the combined approach.", color: colors.body })
      ]})
    ]
  }]
});

Packer.toBuffer(doc).then((buffer: Buffer) => {
  fs.writeFileSync("/home/z/my-project/download/Fracturable_Wafer_Architecture_Research.docx", buffer);
  console.log("Document generated: /home/z/my-project/download/Fracturable_Wafer_Architecture_Research.docx");
});
