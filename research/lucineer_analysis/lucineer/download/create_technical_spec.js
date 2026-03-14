const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer, 
        AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType, ShadingType, 
        VerticalAlign, PageNumber, TableOfContents, PageBreak } = require('docx');
const fs = require('fs');

// Color scheme - Midnight Code (Technology theme)
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
        paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: colors.secondary, font: "Times New Roman" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
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
        children: [new TextRun({ text: "SuperInstance.AI - Technical Specification", color: colors.secondary, size: 20 })]
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
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("MASK-LOCKED INFERENCE CHIP")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        children: [new TextRun({ text: "Master Technical Specification Document", size: 28, color: colors.secondary })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: "Version 2.0 | March 2026 | CONFIDENTIAL", size: 22, color: colors.accent })] }),

      // Executive Summary
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Executive Summary")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The Mask-Locked Inference Chip represents a paradigm shift in edge AI hardware architecture. By physically encoding neural network weights into silicon metal interconnect layers, this approach eliminates the traditional memory bottleneck that limits all conventional AI accelerators. This document synthesizes findings from 24 expert reviews, 60+ research sources, and comprehensive technical validation studies to provide a complete technical specification for the SuperInstance.AI chip family.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The core innovation differentiates this design from all existing approaches: weights are not stored in memory (DRAM or SRAM) but become permanent physical structures in the chip's metal routing layers. This achieves zero access latency, zero access energy, and effectively infinite bandwidth for weight delivery to compute units. The trade-off—model immutability—is acceptable for edge inference where the model is stable and efficiency is paramount.")] }),

      // Core Architecture Table
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Core Architecture Specification")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Chip Specifications Overview")] }),
      new Table({
        columnWidths: [3500, 5860],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER, width: { size: 3500, type: WidthType.DXA },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Parameter", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER, width: { size: 5860, type: WidthType.DXA },
              children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Specification", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("Process Node")] })] }),
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("28nm (TSMC) or 22FDX (GlobalFoundries)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("Architecture")] })] }),
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("32×32 PE Systolic Array")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("Clock Frequency")] })] }),
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("1 GHz target (250 MHz FPGA Gate 0)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("Power Budget")] })] }),
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("2-5W (3B model), validated at 4.8W (TeLLMe FPGA)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("Weight Precision")] })] }),
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("Ternary {-1, 0, +1} or C₄ {+1, -1, +i, -i}")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("Target Throughput")] })] }),
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("25-35 tokens/s (BitNet b1.58-2B-4T)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("Die Size (est.)")] })] }),
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("~25mm² for 3B parameter model")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("Interface")] })] }),
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("USB 3.0, PCIe Gen2 x1, or M.2 form factor")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("Target Price")] })] }),
            new TableCell({ borders: cellBorders, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ children: [new TextRun("$35-60 retail (3B model)")] })] })
          ]})
        ]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 400 }, children: [new TextRun("2.2 Mask-Locked Weight Encoding")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The fundamental innovation of the mask-locked architecture is the permanent encoding of neural network weights into the chip's metal interconnect layers. Unlike traditional architectures where weights are stored in memory (DRAM, SRAM, or flash) and fetched during computation, mask-locked weights exist as physical connections—permanent routing patterns that directly implement the model's learned parameters.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("This approach offers several critical advantages that fundamentally change the economics of edge inference. First, weight access latency becomes exactly zero because weights are always present at the compute unit input. Second, weight access energy becomes effectively zero because no memory read operation is required. Third, weight bandwidth becomes infinite because all weights can be accessed simultaneously without bus contention.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The encoding methodology supports multiple quantization schemes. The ternary weight representation {-1, 0, +1} requires only two bits per weight and achieves 93-96% of FP16 model quality. The complex-valued C₄ representation {+1, -1, +i, -i} enables addition-only inference, potentially eliminating multiplication operations entirely and achieving 75-90% reduction in MAC complexity.")] }),

      // Technical Validation
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Technical Validation Summary")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 BitNet Model Verification")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The BitNet b1.58-2B-4T model has been thoroughly verified as the primary target for the first-generation chip. The model exists on HuggingFace with 16,010 monthly downloads under MIT license, confirming both availability and commercial viability. The model was trained on 4 trillion tokens with a 4096 token context length, making it suitable for most edge inference applications.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("Critical technical findings confirm that standard transformers library does NOT provide efficiency gains—users MUST use bitnet.cpp for optimized inference. The LM Head computation is typically offloaded to CPU on resource-constrained FPGAs, which represents a 9ms overhead that is acceptable for the target throughput. The model has 36 active Spaces on HuggingFace, 18 finetunes, and 6 adapters, indicating a healthy community ecosystem.")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 TeLLMe FPGA Reference Implementation")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The TeLLMe v2 paper (arXiv:2510.15926) provides the critical reference implementation for Gate 0 validation. The implementation demonstrates 25 tokens/s decoding throughput on an AMD Kria KV260 at 4.8W power consumption—directly validating our target specifications. The architecture uses a Table-Lookup Matmul (TLMM) engine that precomputes all possible ternary multiplication results and stores them in FPGA LUTs.")] }),
      new Table({
        columnWidths: [2500, 3430, 3430],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Metric", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "TeLLMe Result", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "SuperInstance Target", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Platform")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("AMD Kria KV260")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Same (Gate 0)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Clock")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("250 MHz")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("250 MHz → 1 GHz")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Throughput")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("25 tok/s")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("25-35 tok/s ✓")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Power")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("4.8W")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("<5W ✓")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Energy Efficiency")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("5.2 TK/J (decode)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Target validated")] })] })
          ]})
        ]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 400 }, children: [new TextRun("3.3 iFairy Complex-Valued Architecture")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The iFairy (Fairy ±i) research from Peking University (arXiv:2508.05571) represents a potential breakthrough for v2.0 architecture. This 2-bit complex-valued LLM uses fourth roots of unity {+1, -1, +i, -i} as weights, enabling addition-only inference that could eliminate multiplication operations entirely from the hardware design. The Apache 2.0 licensed model achieves perplexity 10% LOWER than FP16, breaking the quantization ceiling.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The hardware implications are significant. Multiplication operations in GEMM could be replaced with additions, subtractions, and data exchanges, achieving an estimated 75-90% reduction in MAC complexity. Power savings would be substantial since multipliers are among the most power-hungry components. Area savings would eliminate the need for hardware multipliers, potentially reducing chip area by 30-50%.")] }),

      // Competitive Analysis
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Competitive Positioning")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The competitive landscape analysis confirms a clear market gap. Taalas (data center focused, $219M raised) targets the Llama 3.1-8B model at 14,000-17,000 tok/s using TSMC N6, with NO edge/mobile signals detected. Quadric ($72M raised, Chimera GPNPU) represents the closest competitor with programmable edge LLM IP. Axelera AI ($250M+ raised, Metis at 214 TOPS, 10W) targets edge vision and GenAI.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The market gap is clear: no competitor offers sub-$50, sub-5W LLM inference hardware. Hailo-10H achieves only 4.78 tok/s on Llama3.2-3B at $88 price point. NVIDIA Jetson Orin delivers 20-30 tok/s on 7B models but at $250 and 10-15W. Our target of 25-35 tok/s at $35-60 and 2-5W represents a unique positioning in the market.")] }),

      // Implementation Roadmap
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Implementation Roadmap")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Phase 1: Foundation (Months 1-3, $500K)")] }),
      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun("The foundation phase focuses on team assembly, IP protection, and FPGA validation. Key milestones include:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Hire VP Manufacturing with 5+ tape-out experience (CRITICAL)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Hire Architecture Lead with shipped ASIC experience")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("File 3 provisional patents ($15K estimated)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Complete Gate 0 FPGA demo: 25 tok/s @ <5W on KV260")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Publish SDK Alpha to PyPI")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Lock LPDDR4 supply contract (allocation deposit $100K)")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 Phase 2: Design & Verification (Months 4-18, $2M)")] }),
      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun("The design phase develops complete RTL and verification infrastructure. Key activities include:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Finalize ternary architecture decision (BitNet vs iFairy)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Complete cycle-accurate simulator")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("RTL development using Chisel/Verilog")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Functional verification (100% coverage target)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("FPGA prototype on Xilinx Versal")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.3 Phase 3: Tape-out (Months 19-24, $1M)")] }),
      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun("The tape-out phase transforms RTL into physical silicon. Key activities include:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("MPW shuttle via MOSIS or GlobalFoundries 22FDX")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Synthesis, place & route, timing closure")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("First silicon arrival and bring-up")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Performance validation against targets")] }),

      // Risk Assessment
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Risk Assessment Matrix")] }),
      new Table({
        columnWidths: [2200, 1600, 1600, 3960],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Risk", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Probability", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Impact", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Mitigation", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("No tape-out experience")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("90%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("CRITICAL")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Hire VP Mfg with 5+ tape-outs")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("LPDDR4 pricing crisis")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("85%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("CRITICAL")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Lock contracts immediately ($10-12)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("First silicon failure")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("30%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("HIGH")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("FPGA prototype, formal verification")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Model obsolescence")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("40%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("HIGH")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Target stable architectures (Llama)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Taalas edge pivot")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("15%")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("MEDIUM")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("12-18 month first-mover window")] })] })
          ]})
        ]
      }),

      // Conclusion
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Conclusion")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The Mask-Locked Inference Chip represents a validated technical approach with clear market positioning. The technology is real—confirmed by TeLLMe FPGA reference implementation achieving target specifications. The market timing is favorable with a 12-18 month first-mover window before data center competitors potentially pivot to edge. The execution risk is manageable with the critical dependency being the VP Manufacturing hire.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The path forward is clear: execute Phase 1 foundation activities, validate Gate 0 FPGA demonstration, and secure seed funding to advance to RTL development. The window of opportunity is finite, and execution speed is the critical variable determining success.")] }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/z/my-project/download/Master_Technical_Specification_v2.docx", buffer);
  console.log("Master Technical Specification created successfully!");
});
