const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer, 
        AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType, ShadingType, 
        VerticalAlign, PageNumber } = require('docx');
const fs = require('fs');

const colors = {
  primary: "1A1F16",
  body: "2D3329",
  secondary: "4A5548",
  accent: "94A3B8",
  tableBg: "F8FAF7",
  tableHeader: "EEF1ED"
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
        children: [new TextRun({ text: "SuperInstance.AI - Patent Portfolio", color: colors.secondary, size: 20 })]
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
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("PATENT PORTFOLIO")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
        children: [new TextRun({ text: "Mask-Locked Inference Chip Technology", size: 28, color: colors.secondary })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 },
        children: [new TextRun({ text: "Comprehensive IP Strategy | March 2026", size: 22, color: colors.accent })] }),

      // Executive Summary
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Executive Summary")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("This document outlines the comprehensive patent portfolio strategy for SuperInstance.AI's mask-locked inference chip technology. The analysis identifies 10 specific patent opportunities across the core technology, architecture innovations, and implementation details. The overall IP risk assessment is MODERATE-LOW, with no blocking prior art identified for the core mask-locked weight encoding concept.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The immediate priority is filing three provisional patent applications covering: (1) Mask-Locked Neural Network Weight Encoding, (2) Rotation-Accumulate Unit (RAU) Architecture, and (3) Hybrid Adapter Architecture for Model Upgradeability. These patents represent estimated $50-250M in potential IP value depending on market adoption and portfolio strength.")] }),

      // Prior Art Analysis
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Prior Art Analysis")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Key Prior Art References")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("A comprehensive prior art search has identified the following key references, none of which block the core mask-locked weight encoding concept:")] }),
      
      new Table({
        columnWidths: [2500, 3500, 3360],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Reference", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Description", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Blocking Risk", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("US10540588B2")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("NVIDIA: Weights in memory, not metal-encoded")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "LOW", color: "22C55E" })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("US11150234B2")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Google TPU: Systolic array, weights from memory")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "LOW", color: "22C55E" })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("arXiv:2508.05571")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("iFairy: Fourth roots of unity quantization")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "LOW (Apache 2.0)", color: "22C55E" })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("arXiv:2508.16151")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("HNLPU: Hardwired-Neurons validation")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "LOW (Academic)", color: "22C55E" })] })] })
          ]})
        ]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 Freedom to Operate Assessment")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The Freedom to Operate (FTO) analysis concludes MODERATE-LOW risk with clear paths identified for all potential blocking scenarios. The key differentiator is that prior art references describe weights stored in memory (SRAM, DRAM, flash) and fetched during computation, whereas the mask-locked approach permanently encodes weights in metal interconnect layers. This fundamental architectural difference provides strong novelty position.")] }),

      // Patent 1
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Patent 1: Mask-Locked Weight Encoding")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Title and Abstract")] }),
      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun({ text: "Title: ", bold: true }), new TextRun("Mask-Locked Neural Network Weight Encoding in Semiconductor Devices")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun({ text: "Abstract: ", bold: true }), new TextRun("A semiconductor device and method for permanently encoding neural network weights into metal interconnect layers, eliminating memory access latency and energy consumption for weight retrieval during inference operations. The device comprises a systolic array of processing elements where weights are implemented as permanent routing connections rather than stored data values.")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 Key Claims")] }),
      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun("The patent includes 30 claims covering device, method, system, and use case aspects:")] }),
      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [new TextRun({ text: "Claim 1 (Device): ", bold: true }), new TextRun("A semiconductor device comprising a substrate, metal interconnect layers, and a neural network with weights permanently encoded in the metal interconnect layers, wherein each weight is represented by a physical routing connection that directly couples a first node to a second node according to the weight value.")] }),
      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [new TextRun({ text: "Claim 2 (Method): ", bold: true }), new TextRun("A method of manufacturing a semiconductor device comprising: receiving a trained neural network model with quantized weights; generating photomask patterns that encode the weights as metal routing connections; and fabricating the semiconductor device using the photomask patterns.")] }),
      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [new TextRun({ text: "Claim 3 (System): ", bold: true }), new TextRun("A device-native artificial intelligence system comprising a semiconductor device with weights permanently encoded in metal interconnect layers, an input interface for receiving inference requests, and an output interface for providing inference results, wherein no memory loading operation is required to access the weights.")] }),
      new Paragraph({ numbering: { reference: "numbered-list", level: 0 }, children: [new TextRun({ text: "Claim 4 (Use Case): ", bold: true }), new TextRun("A privacy-preserving inference method using a semiconductor device with immutable weights permanently encoded in metal interconnect layers, the method comprising receiving input data at an input interface, performing inference using the permanently encoded weights, and providing output data at an output interface, wherein the weights cannot be modified or extracted.")] }),

      // Patent 2
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Patent 2: RAU Architecture")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 Title and Abstract")] }),
      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun({ text: "Title: ", bold: true }), new TextRun("Rotation-Accumulate Unit for Ternary and Complex-Valued Neural Network Computation")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun({ text: "Abstract: ", bold: true }), new TextRun("A computation unit for neural network inference that replaces traditional multiply-accumulate operations with rotation-accumulate operations, achieving significant reduction in gate count and power consumption. The unit is optimized for ternary weight values {-1, 0, +1} and complex-valued weight values {+1, -1, +i, -i}.")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 Key Innovation")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The RAU architecture achieves 85% gate count reduction compared to traditional MAC units by exploiting the properties of ternary and C₄ quantized weights. For ternary weights, multiplication operations are replaced with conditional addition, subtraction, or bypass operations. For C₄ weights, multiplication becomes simple phase rotation implemented through multiplexer-based selection circuits.")] }),

      // Patent 3
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Patent 3: Hybrid Adapter Architecture")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Title and Abstract")] }),
      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun({ text: "Title: ", bold: true }), new TextRun("Hybrid Mask-Locked and Adapter Architecture for Updatable Neural Network Inference")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun({ text: "Abstract: ", bold: true }), new TextRun("A semiconductor device architecture that combines mask-locked base model weights with programmable adapter slots, enabling model capability updates without full chip respin. The architecture addresses model obsolescence concerns while maintaining the efficiency benefits of mask-locked weight encoding.")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 Key Innovation")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The hybrid architecture reserves a configurable percentage (typically 5-15%) of model weights in SRAM-based adapter slots while the majority (85-95%) remain mask-locked. This enables LoRA-style fine-tuning for domain adaptation or model updates while preserving the efficiency benefits of mask-locking for the majority of computations.")] }),

      // Filing Strategy
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Filing Strategy and Timeline")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.1 Immediate Filings (Week 1-4)")] }),
      new Table({
        columnWidths: [4000, 2500, 2860],
        margins: { top: 100, bottom: 100, left: 180, right: 180 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Patent", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Timeline", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableHeader, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Estimated Cost", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("P1: Mask-Locked Weight Encoding")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Day 7")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$5,000")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("P2: RAU Architecture")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Day 10")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$5,000")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("P3: Hybrid Adapter Architecture")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("Day 14")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("$5,000")] })] })
          ]})
        ]
      }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6.2 5-Year Patent Budget")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("The total 5-year patent budget is estimated at $455,000-500,000, covering provisional filings, non-provisional conversions, international filings, and prosecution costs. This represents a strategic investment in IP protection that could yield $50-250M in value at exit.")] }),

      // Third-Party IP
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Third-Party IP Assessment")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("7.1 BitNet Model Licensing")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("BitNet b1.58-2B-4T is released under MIT license, which grants broad commercial use rights including hardware embedding. The license does not include an explicit patent grant, but Microsoft's published research indicates intention for open use. Legal review confirms LOW licensing risk for commercial deployment.")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("7.2 iFairy Model Licensing")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("iFairy (Fairy ±i) is released under Apache 2.0 license, which includes an explicit patent grant. The license permits commercial use, modification, and distribution with appropriate attribution. Legal review confirms LOW licensing risk with clear path for hardware embedding.")] }),

      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("7.3 Taalas Competitive Monitoring")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun("Taalas ($219M funded) has filed patents related to mask ROM-based AI inference, but no patents have been identified that block the specific mask-locked weight encoding approach. Weekly patent monitoring is recommended with an annual budget of $5,000 for competitive intelligence services.")] }),

      // Conclusion
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. Conclusion and Recommendations")] }),
      new Paragraph({ spacing: { after: 100, line: 360 },
        children: [new TextRun("The IP position is strong with the following key conclusions:")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Prior Art: ", bold: true }), new TextRun("No blocking patents identified for core mask-locked weight encoding concept.")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Freedom to Operate: ", bold: true }), new TextRun("MODERATE-LOW risk with clear design-around options if needed.")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Third-Party IP: ", bold: true }), new TextRun("LOW risk from BitNet (MIT) and iFairy (Apache 2.0) licenses.")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Patentability: ", bold: true }), new TextRun("HIGH novelty position with 10+ patentable claims identified.")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "IP Valuation: ", bold: true }), new TextRun("$50-250M potential depending on market adoption.")] }),
      new Paragraph({ spacing: { after: 200, line: 360 },
        children: [new TextRun({ text: "Immediate Action: ", bold: true }), new TextRun("Engage patent counsel ($5K retainer) and file P1-P3 provisionals within Week 1-2 ($15K total).")] }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/z/my-project/download/Patent_Portfolio_v2.docx", buffer);
  console.log("Patent Portfolio created successfully!");
});
