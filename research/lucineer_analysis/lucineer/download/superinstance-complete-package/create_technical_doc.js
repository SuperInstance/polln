const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, VerticalAlign, PageNumber,
        PageBreak, TableOfContents } = require('docx');
const fs = require('fs');

const colors = {
  primary: "#020617",
  body: "#1E293B",
  secondary: "#64748B",
  accent: "#94A3B8",
  tableBg: "#F8FAFC",
  headerBg: "#E2E8F0"
};

const tableBorder = { style: BorderStyle.SINGLE, size: 8, color: colors.primary };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 56, bold: true, color: colors.primary, font: "Times New Roman" },
        paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: colors.primary, font: "Times New Roman" },
        paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: colors.secondary, font: "Times New Roman" },
        paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: colors.body, font: "Times New Roman" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } },
      { id: "CodeBlock", name: "Code Block", basedOn: "Normal",
        run: { size: 18, font: "Courier New", color: colors.body },
        paragraph: { spacing: { before: 100, after: 100 }, shading: { fill: colors.tableBg } } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }
    ]
  },
  sections: [
    // Cover Page
    {
      properties: { page: { margin: { top: 0, right: 0, bottom: 0, left: 0 } } },
      children: [
        new Paragraph({ spacing: { before: 3000 } }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
          children: [new TextRun({ text: "TERNARYAIR", size: 72, bold: true, color: colors.primary, font: "Times New Roman" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
          children: [new TextRun({ text: "Technical Architecture Reference", size: 36, color: colors.secondary, font: "Times New Roman" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 },
          children: [new TextRun({ text: "Complete RTL Implementation Guide", size: 24, color: colors.body, font: "Times New Roman" })] }),
        new Paragraph({ spacing: { before: 2000 } }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
          children: [new TextRun({ text: "Version 1.0 | MIT License", size: 22, color: colors.accent, font: "Times New Roman" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "github.com/superinstance/ternaryair", size: 20, color: colors.accent, font: "Times New Roman" })] })
      ]
    },
    // Main Content
    {
      properties: { page: { margin: { top: 1800, right: 1440, bottom: 1440, left: 1440 } } },
      headers: {
        default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "TernaryAir Technical Architecture", size: 18, color: colors.accent, font: "Times New Roman" })] })] })
      },
      footers: {
        default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Page ", size: 18, font: "Times New Roman" }), new TextRun({ children: [PageNumber.CURRENT], size: 18 }), new TextRun({ text: " of ", size: 18 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18 })] })] })
      },
      children: [
        new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 400 },
          children: [new TextRun({ text: "Right-click and select 'Update Field' to refresh page numbers", size: 18, color: colors.accent, font: "Times New Roman", italics: true })] }),
        new Paragraph({ children: [new PageBreak()] }),

        // Section 1
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Architecture Overview")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The TernaryAir architecture implements mask-locked neural network inference through a novel Rotation-Accumulate Unit (RAU) that replaces traditional multiply-accumulate (MAC) operations. By encoding ternary weights {-1, 0, +1} directly into metal routing layers, the architecture achieves 90% gate reduction compared to conventional approaches while maintaining inference accuracy through proven quantization techniques.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 Core Principles")] }),
        new Paragraph({ spacing: { after: 100 },
          children: [new TextRun({ text: "The architecture is built on three fundamental principles that differentiate it from conventional neural network accelerators:", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, spacing: { after: 100 },
          children: [new TextRun({ text: "Weight Immutability: Neural network weights are permanently encoded in silicon during manufacturing, eliminating memory bandwidth bottlenecks entirely.", font: "Times New Roman", size: 22 })] }),
        new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, spacing: { after: 100 },
          children: [new TextRun({ text: "Multiplication-Free Compute: The Rotation-Accumulate Unit performs weight operations through data multiplexing rather than multiplication, reducing circuit complexity by an order of magnitude.", font: "Times New Roman", size: 22 })] }),
        new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, spacing: { after: 200 },
          children: [new TextRun({ text: "Sparse Activation: Ternary encoding enables natural sparsity through the zero state, allowing the hardware to skip computations entirely for inactive pathways.", font: "Times New Roman", size: 22 })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 System Block Diagram")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The system consists of five primary modules connected through a unified bus architecture. The Synaptic Array contains multiple RAU instances operating in parallel, each processing a portion of the inference computation. The Weight ROM stores activation biases and scaling factors that cannot be directly encoded in metal. The KV Cache provides temporary storage for transformer attention operations. The Controller sequences operations and manages data flow. The I/O Interface handles communication with external systems.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 2: RAU
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Rotation-Accumulate Unit (RAU)")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The RAU is the computational heart of the TernaryAir architecture. It replaces the traditional multiply-accumulate operation with a rotation-accumulate operation that exploits the mathematical properties of ternary weight encoding. For weights in the set {-1, 0, +1}, multiplication reduces to simple operations: multiply by -1 (negate), multiply by 0 (return zero), multiply by +1 (identity). These operations can be implemented with multiplexers rather than multiplication circuits.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Mathematical Foundation")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "For a ternary weight w ∈ {-1, 0, +1} and an input activation x, the product w·x can be computed as follows:", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ style: "CodeBlock", spacing: { after: 200 },
          children: [new TextRun({ text: "  if w = +1:  result = x      (identity)\n  if w =  0:  result = 0      (zero)\n  if w = -1:  result = -x     (negation)", font: "Courier New", size: 20 })] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "These three cases can be implemented with a single 3:1 multiplexer and a negation circuit. The accumulator simply sums the results across multiple weight-activation pairs. The total gate count for one RAU is approximately 15-20 gates, compared to 150+ gates for a traditional MAC unit supporting INT8 multiplication.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 Hardware Implementation")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The RAU module accepts an input activation value and a weight encoding signal, producing an output that is fed to an accumulator. The weight encoding is typically 2 bits (00=zero, 01=positive, 10=negative, 11=reserved). The input activation is typically INT8 or INT16, depending on the precision requirements of the specific layer. The accumulator must be wide enough to prevent overflow across the reduction dimension.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun("2.2.1 RAU Interface Signals")] }),
        new Paragraph({ spacing: { after: 200 } }),
        new Table({
          columnWidths: [2500, 1800, 5060],
          margins: { top: 100, bottom: 100, left: 180, right: 180 },
          rows: [
            new TableRow({ tableHeader: true, children: [
              new TableCell({ borders: cellBorders, width: { size: 2500, type: WidthType.DXA }, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Signal", bold: true, size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 1800, type: WidthType.DXA }, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Width", bold: true, size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 5060, type: WidthType.DXA }, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Description", bold: true, size: 22, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "clk", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "1", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Clock signal", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "rst_n", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "1", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Active-low reset", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "activation", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "8/16", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Input activation value (signed)", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "weight", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "2", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Ternary weight encoding", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "result", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "8/16", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Rotated activation output", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "valid", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "1", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Output valid indicator", size: 20, font: "Times New Roman" })] })] })
            ]})
          ]
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 3: Synaptic Array
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Synaptic Array")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The Synaptic Array organizes multiple RAU instances into a systolic structure for parallel computation. Each RAU processes one weight-activation pair per cycle, and the array processes multiple pairs simultaneously. The array dimension is determined by the target model's weight matrix sizes and the desired throughput.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Array Configuration")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "For a 2B parameter model with typical transformer dimensions (hidden size 2048, intermediate size 8192), the synaptic array must handle weight matrices up to 2048×8192. With INT8 activations and ternary weights, each RAU requires approximately 100μm² in 28nm technology. A 256×256 RAU array occupies roughly 6.5mm², leaving room for control logic, SRAM, and I/O on a cost-effective die.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Dataflow")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The array uses a weight-stationary dataflow: weights remain fixed in each RAU while activations flow through the array. This matches the mask-locked paradigm where weights are permanently encoded. Activations are fed from SRAM buffers at the array edges and results are collected at the opposite edges. The systolic pattern maximizes data reuse and minimizes memory access frequency.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 4: Weight ROM
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Weight Storage Architecture")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "While the ternary weights {-1, 0, +1} are mask-locked into metal routing, additional parameters require storage. These include: activation scaling factors per layer, bias values, attention scaling factors, and layer normalization parameters. These values are typically FP16 or FP32 and are stored in on-chip ROM or loaded from external flash.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 Storage Requirements")] }),
        new Paragraph({ spacing: { after: 200 } }),
        new Table({
          columnWidths: [3500, 2500, 3360],
          margins: { top: 100, bottom: 100, left: 180, right: 180 },
          rows: [
            new TableRow({ tableHeader: true, children: [
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Parameter Type", bold: true, size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Count (2B model)", bold: true, size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Storage (FP16)", bold: true, size: 22, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Layer scales", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "~25 layers", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "~50 bytes", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Bias vectors", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "~100K values", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "~200 KB", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "LayerNorm params", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "~50K values", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "~100 KB", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Total", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "-", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "<500 KB", size: 20, font: "Times New Roman" })] })] })
            ]})
          ]
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 5: KV Cache
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. KV Cache Architecture")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The KV Cache stores key and value vectors for transformer attention operations during autoregressive generation. Unlike the weights, which are mask-locked, the KV cache is dynamic and must be stored in SRAM. The cache size determines the maximum context length the chip can support.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Sizing Calculation")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "For a transformer with H attention heads, D model dimension, L layers, and context length C:", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ style: "CodeBlock", spacing: { after: 200 },
          children: [new TextRun({ text: "  KV Cache Size = 2 × L × C × H × (D/H) × bytes_per_value\n                  = 2 × L × C × D × bytes_per_value\n\n  Example (2B model, 4096 context, FP16):\n  = 2 × 24 × 4096 × 2048 × 2 bytes\n  = 768 MB", font: "Courier New", size: 20 })] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "768 MB of SRAM is economically impractical for a $99 chip. The design must either: (a) limit context length, (b) use INT4/INT8 quantization for KV cache, or (c) use external memory. Option (b) is preferred: INT4 KV cache reduces storage to 192 MB, which could be further reduced through compression techniques.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 6: Manufacturing
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Manufacturing Guidelines")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.1 Process Node Selection")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "28nm is the recommended process node for the first generation. This mature node offers: low mask costs ($2-3M vs $15-20M for 5nm), high availability with multiple foundries (TSMC, GlobalFoundries, Samsung), well-understood design rules and IP ecosystem, and sufficient density for 2B parameter models. The efficiency gains come from architectural innovation, not process technology.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.2 Estimated Costs")] }),
        new Paragraph({ spacing: { after: 200 } }),
        new Table({
          columnWidths: [4000, 2680, 2680],
          margins: { top: 100, bottom: 100, left: 180, right: 180 },
          rows: [
            new TableRow({ tableHeader: true, children: [
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Cost Component", bold: true, size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "NRE Cost", bold: true, size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Per-Unit @ 10K", bold: true, size: 22, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Mask Set (28nm)", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$2-3M", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "-", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Design & Verification", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$2-4M", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "-", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Die (25mm² @ 28nm)", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "-", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$5-8", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Packaging & Test", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "-", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$3-5", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Memory (LPDDR4)", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "-", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$10-12", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "Total COGS", bold: true, size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$4-7M NRE", bold: true, size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$20-30", bold: true, size: 20, font: "Times New Roman" })] })] })
            ]})
          ]
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 7: SDK
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Software SDK Specification")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The TernaryAir SDK provides a simple Python interface for inference. The design philosophy is \"zero configuration\": the chip appears as a serial device and inference is a single function call. No model loading, no memory management, no configuration files.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("7.1 Core API")] }),
        new Paragraph({ style: "CodeBlock", spacing: { after: 200 },
          children: [new TextRun({ text: "  import ternaryair\n\n  # Initialize device (auto-detects USB connection)\n  device = ternaryair.connect()\n\n  # Synchronous inference\n  response = device.infer(\"Your prompt here\")\n\n  # Streaming inference\n  for token in device.infer_stream(\"Your prompt here\"):\n      print(token, end='', flush=True)\n\n  # Batch inference\n  responses = device.infer_batch([\"Prompt 1\", \"Prompt 2\", \"Prompt 3\"])", font: "Courier New", size: 20 })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("7.2 Advanced Features")] }),
        new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 100 },
          children: [new TextRun({ text: "Token streaming with configurable buffer sizes", font: "Times New Roman", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 100 },
          children: [new TextRun({ text: "KV cache management for multi-turn conversations", font: "Times New Roman", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 100 },
          children: [new TextRun({ text: "Power profiling and thermal monitoring", font: "Times New Roman", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 100 },
          children: [new TextRun({ text: "Debug interface with per-layer activation inspection", font: "Times New Roman", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 200 },
          children: [new TextRun({ text: "Multi-device parallel inference", font: "Times New Roman", size: 22 })] }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 8: Conclusion
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. Implementation Roadmap")] }),
        new Paragraph({ spacing: { after: 200 } }),
        new Table({
          columnWidths: [2000, 4000, 3360],
          margins: { top: 100, bottom: 100, left: 180, right: 180 },
          rows: [
            new TableRow({ tableHeader: true, children: [
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Phase", bold: true, size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Activities", bold: true, size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, shading: { fill: colors.headerBg, type: ShadingType.CLEAR },
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Timeline", bold: true, size: 22, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Gate 0", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "FPGA prototype on KV260", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Months 1-4", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Gate 1", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "RTL freeze, verification complete", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Months 5-10", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Gate 2", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "MPW tapeout, first silicon", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Months 11-18", size: 20, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Gate 3", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun({ text: "Volume production release", size: 20, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Months 19-24", size: 20, font: "Times New Roman" })] })] })
            ]})
          ]
        }),

        new Paragraph({ spacing: { before: 400 } }),
        new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "For complete RTL source code, see the /rtl directory in this package.", size: 20, font: "Times New Roman", color: colors.secondary, italics: true })] })
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/z/my-project/download/superinstance-complete-package/docs/TernaryAir_Technical_Architecture.docx", buffer);
  console.log("Technical Architecture document created successfully");
});
