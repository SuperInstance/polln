const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer, 
        AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType, ShadingType, 
        VerticalAlign, PageNumber } = require('docx');
const fs = require('fs');

const colors = {
  primary: "0B1220",
  body: "0F172A",
  secondary: "2B2B2B",
  accent: "9AA6B2",
  tableBg: "F1F5F9",
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
        children: [new TextRun({ text: "SuperInstance.AI - FPGA Development Guide", color: colors.secondary, size: 20 })]
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
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("FPGA DEVELOPMENT GUIDE")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        children: [new TextRun({ text: "Gate 0 Implementation Reference", size: 28, color: colors.secondary })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: "AMD Kria KV260 Platform | March 2026", size: 22, color: colors.accent })] }),

      // Overview
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Overview")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("This guide provides the complete implementation reference for the Gate 0 FPGA demonstration on the AMD Kria KV260 platform. The target is to achieve 25+ tokens/s throughput at less than 5W power consumption using the BitNet b1.58-2B-4T model. The implementation is based on the validated TeLLMe v2 reference design (arXiv:2510.15926) which has demonstrated these specifications on the same hardware platform.")] }),

      // Hardware Setup
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Hardware Setup")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Required Equipment")] }),
      new Table({
        columnWidths: [3500, 2500, 3360],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Item", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Quantity", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Est. Cost", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("AMD Kria KV260 Starter Kit")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$300 each = $900")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("USB-C Power Supply (5V/4A)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$20 each = $60")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("microSD Cards (64GB)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$15 each = $45")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("USB-UART Cable")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("3")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$15 each = $45")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Power Meter (USB)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("1")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$50")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ children: [new TextRun({ text: "Total Hardware Budget", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "-", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "$1,100", bold: true })] })] })
          ]})
        ]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 Platform Specifications")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The AMD Kria KV260 features a Zynq UltraScale+ XCK26 MPSoC with dual-core ARM Cortex-A53 processor, dual-core ARM Cortex-R5 real-time processor, and programmable logic with 246K system logic cells, 368 DSP slices, and 14.4Mb block RAM. The onboard 4GB LPDDR4 memory provides sufficient capacity for KV cache and activation storage during inference operations.")] }),

      // Development Environment
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Development Environment")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Software Requirements")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Vitis Unified IDE 2023.2 or later (free WebPACK license)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Vivado Design Suite 2023.2 or later")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("PYNQ framework v3.0.1 for KV260")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Python 3.10+ with NumPy, PyTorch, transformers")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Git for version control")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("bitnet.cpp repository (Microsoft)")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Environment Setup Steps")] }),
      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [new TextRun("Download and install Vitis/Vivado from AMD Xilinx website (requires free account)")] }),
      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [new TextRun("Flash KV260 with PYNQ 3.0.1 image from official repository")] }),
      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [new TextRun("Clone bitnet.cpp: git clone https://github.com/microsoft/BitNet.git")] }),
      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [new TextRun("Download BitNet b1.58-2B-4T weights from HuggingFace")] }),
      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [new TextRun("Build bitnet.cpp for ARM: cmake -DLLAMA_CUBLAS=OFF && make")] }),

      // Implementation Architecture
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Implementation Architecture")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 TeLLMe Reference Architecture")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The implementation follows the TeLLMe v2 architecture which achieves 25 tok/s at 4.8W on the KV260 platform. The core innovation is the Table-Lookup Matmul (TLMM) engine that precomputes all possible ternary multiplication results and stores them in FPGA LUTs as lookup tables. This approach eliminates the need for hardware multipliers, significantly reducing resource utilization and power consumption.")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 Resource Requirements")] }),
      new Table({
        columnWidths: [3500, 3000, 2860],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Resource", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Utilization", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Available", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("LUTs")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("98K (40%)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("246K")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("DSP Slices")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("610 (166%)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("368")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Block RAM")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("60 URAM")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("14.4Mb")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Clock")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("250 MHz")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Target")] })] })
          ]})
        ]
      }),

      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun({ text: "Note: ", bold: true }), new TextRun("DSP slice utilization exceeds available resources on the KV260 for the full 2B model. The TeLLMe implementation uses LUT-based multiplication for overflow, accepting slight performance reduction.")] }),

      // Performance Targets
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Performance Targets and Validation")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Gate 0 Success Criteria")] }),
      new Table({
        columnWidths: [3500, 3000, 2860],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Metric", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Target", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Validation Method", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Decoding Throughput")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("≥25 tok/s")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Benchmark script")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Power Consumption")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("≤5W")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("USB power meter")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Model Accuracy")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("≤5% degradation")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("MMLU benchmark")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Latency (first token)")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("<100ms")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Timing measurement")] })] })
          ]})
        ]
      }),

      // Timeline
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Development Timeline")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.1 Week-by-Week Plan")] }),
      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun({ text: "Week 5: ", bold: true }), new TextRun("Environment Setup and Model Preparation")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Unbox and configure KV260 boards")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Install Vitis/Vivado development environment")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Download and verify BitNet b1.58-2B-4T weights")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Build bitnet.cpp and validate CPU inference")] }),

      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun({ text: "Week 6: ", bold: true }), new TextRun("RTL Development and Initial Synthesis")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Implement TLMM engine in Verilog/SystemVerilog")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Create systolic array structure")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Initial synthesis targeting KV260")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Resolve timing violations")] }),

      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun({ text: "Week 7: ", bold: true }), new TextRun("Integration and Debugging")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Integrate RTL with ARM PS software stack")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Implement KV cache management")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Debug timing and functional issues")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("First inference run")] }),

      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun({ text: "Week 8: ", bold: true }), new TextRun("Optimization and Validation")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Performance optimization for 25 tok/s target")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Power measurement and optimization")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Accuracy benchmarking (MMLU)")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun("Documentation and demo preparation")] }),

      // Key Contacts
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Key Resources and Contacts")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "TeLLMe Authors: ", bold: true }), new TextRun("Contact via arXiv:2510.15926 for implementation details")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Tong Yang (PKU): ", bold: true }), new TextRun("tongyang@pku.edu.cn - iFairy hardware collaboration")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "KAIST HPIC Lab: ", bold: true }), new TextRun("https://hpic-lab.github.io - 2T1C DRAM research")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "BitNet GitHub: ", bold: true }), new TextRun("https://github.com/microsoft/BitNet")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "KV260 Documentation: ", bold: true }), new TextRun("https://docs.xilinx.com/r/en-US/ug1089-kv260-starter-kit")] }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/z/my-project/download/FPGA_Development_Guide_v2.docx", buffer);
  console.log("FPGA Development Guide created successfully!");
});
