const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, PageOrientation, LevelFormat, 
        HeadingLevel, BorderStyle, WidthType, ShadingType, VerticalAlign, PageNumber,
        PageBreak, TableOfContents } = require('docx');
const fs = require('fs');

// Color palette - Ocean/Industrial
const colors = {
  primary: "#1A1F16",      // Deep Forest Ink
  body: "#2D3329",         // Dark Moss Gray  
  secondary: "#4A5548",    // Neutral Olive
  accent: "#94A3B8",       // Steady Silver
  tableBg: "#F8FAF7",      // Ultra-Pale Mint White
  headerBg: "#E8EDE9"
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
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list-1",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-list-2",
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
          children: [new TextRun({ text: "Open Source Mask-Locked Inference Chip", size: 32, color: colors.secondary, font: "Times New Roman" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 },
          children: [new TextRun({ text: "$99 Retail | 100+ tok/s | 3-5W USB Power | MIT License", size: 24, color: colors.body, font: "Times New Roman" })] }),
        new Paragraph({ spacing: { before: 1500 } }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
          children: [new TextRun({ text: "FOUNDATIONAL MANIFESTO", size: 40, bold: true, color: colors.primary, font: "Times New Roman" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 },
          children: [new TextRun({ text: "Intelligence Without Internet", size: 28, color: colors.secondary, font: "Times New Roman" })] }),
        new Paragraph({ spacing: { before: 2000 } }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
          children: [new TextRun({ text: "Casey DiGennaro", size: 24, bold: true, color: colors.primary, font: "Times New Roman" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 },
          children: [new TextRun({ text: "Commercial Fisherman | Edge Hardware Designer", size: 22, color: colors.secondary, font: "Times New Roman" })] }),
        new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "github.com/superinstance/ternaryair", size: 20, color: colors.accent, font: "Times New Roman" })] })
      ]
    },
    // Main Content
    {
      properties: { page: { margin: { top: 1800, right: 1440, bottom: 1440, left: 1440 } } },
      headers: {
        default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
          children: [new TextRun({ text: "TernaryAir Manifesto", size: 18, color: colors.accent, font: "Times New Roman" })] })] })
      },
      footers: {
        default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Page ", size: 18, font: "Times New Roman" }), new TextRun({ children: [PageNumber.CURRENT], size: 18 }), new TextRun({ text: " of ", size: 18 }), new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18 })] })] })
      },
      children: [
        // TOC
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Table of Contents")] }),
        new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200, after: 400 },
          children: [new TextRun({ text: "Right-click and select 'Update Field' to refresh page numbers", size: 18, color: colors.accent, font: "Times New Roman", italics: true })] }),
        new Paragraph({ children: [new PageBreak()] }),

        // Section 1: Origin Story
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Origin Story: Why This Exists")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 The Fisherman's Problem")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "I commercial fish for a living. Out on the water, miles from cell towers and WiFi, I need intelligence that works without the internet. This isn't a hypothetical use case dreamed up in a Silicon Valley boardroom. This is my life. I've stood on the deck of my boat at 4 AM, staring at weather patterns I couldn't analyze, catch data I couldn't process, and safety decisions I had to make with gut instinct because the cloud was 50 miles away. That frustration led to TernaryAir.", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The edge AI industry talks about \"edge\" as if it means a coffee shop WiFi connection. Real edge is offshore. Real edge is a construction site in rural Wyoming. Real edge is a research station in Antarctica. Real edge is a dozen places where I need intelligence, and the internet simply doesn't exist. The current solutions assume connectivity. I'm building for the assumption that connectivity will never exist.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 The Technology Development Philosophy")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The foundational toolkits to make affordable, open-source inference chips must never be closed off to anyone wanting to further the science and design. This isn't just business philosophy—it's survival philosophy. When you're building technology for environments where proprietary lock-in could mean the difference between life and death, open standards aren't optional. They're essential infrastructure, like lighthouses and GPS.", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "I want credit for this work—it belongs in my portfolio of mathematics I've helped keep public. But more importantly, I want this technology to develop quickly. Open source creates the fastest path from concept to silicon. Every barrier removed accelerates the timeline from \"someone should build this\" to \"I can buy this for $99 and use it tomorrow.\"", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.3 The POLLN Connection")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "This project connects to my broader work at github.com/superinstance/POLLN—a project awaiting chips like these to become reality. POLLN represents a different approach to inference architecture, one that could benefit from hardware specifically designed for its computational patterns. TernaryAir isn't just a standalone chip; it's part of an ecosystem of open hardware that enables new approaches to machine intelligence that proprietary solutions will never support.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 2: Technical Vision
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Technical Vision: Mask-Locked Inference")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 The Core Innovation")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "Traditional AI chips are computers that run AI software. TernaryAir is AI embodied in silicon. The weights aren't loaded from memory—they're hardwired into the metal interconnect layers. This is the difference between a book you read and a sculpture you touch. The inference IS the hardware. There's no abstraction layer between the model and the physics of computation.", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The Rotation-Accumulate Unit (RAU) is our core innovation. By using ternary weights {-1, 0, +1} encoded directly into metal routing patterns, we eliminate 90% of the gate count of traditional MAC (multiply-accumulate) units. A multiplication circuit requires dozens of gates. A rotation circuit requires multiplexers. The math is identical. The physics is dramatically simpler. The power consumption drops by orders of magnitude.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 Why Ternary, Not Binary")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "Binary quantization (1-bit) loses too much information. INT4/INT8 quantization requires multiplication hardware. Ternary {−1, 0, +1} hits a sweet spot: enough precision for meaningful inference, simple enough for addition-only hardware. The zero state is crucial—it allows sparse computation, skipping unnecessary operations entirely. This isn't just quantization; it's architectural simplification that propagates through every level of the design.", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "Recent research validates this approach. Microsoft's BitNet b1.58 uses 1.58-bit ternary quantization with results competitive with full-precision models. Peking University's iFairy (Fairy±i) extends this to complex-valued {+1, −1, +i, −i} weights, enabling addition-only inference that eliminates multiplication operations entirely. These aren't theoretical papers—they're running models on HuggingFace right now.", font: "Times New Roman", size: 22, color: colors.body })] }),

        // Key specifications table
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.3 Target Specifications")] }),
        new Paragraph({ spacing: { after: 200 } }),
        new Table({
          columnWidths: [3500, 5860],
          margins: { top: 100, bottom: 100, left: 180, right: 180 },
          rows: [
            new TableRow({ tableHeader: true, children: [
              new TableCell({ borders: cellBorders, width: { size: 3500, type: WidthType.DXA }, shading: { fill: colors.headerBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Parameter", bold: true, size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 5860, type: WidthType.DXA }, shading: { fill: colors.headerBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER,
                children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Target Specification", bold: true, size: 22, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, width: { size: 3500, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Retail Price", size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 5860, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "$99 (Maker Edition $79)", size: 22, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, width: { size: 3500, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Inference Speed", size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 5860, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "100+ tokens/second", size: 22, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, width: { size: 3500, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Power Consumption", size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 5860, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "3-5W USB power", size: 22, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, width: { size: 3500, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Process Node", size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 5860, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "28nm (mature, affordable)", size: 22, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, width: { size: 3500, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "License", size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 5860, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "MIT (fully open source)", size: 22, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, width: { size: 3500, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Form Factor", size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 5860, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "USB-C dongle / M.2 module", size: 22, font: "Times New Roman" })] })] })
            ]}),
            new TableRow({ children: [
              new TableCell({ borders: cellBorders, width: { size: 3500, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Model Support", size: 22, font: "Times New Roman" })] })] }),
              new TableCell({ borders: cellBorders, width: { size: 5860, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "BitNet b1.58-2B-4T, iFairy variants", size: 22, font: "Times New Roman" })] })] })
            ]})
          ]
        }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 3: LOG Architecture
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Second Generation: LOG Architecture")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Logic-Orientation-Geometry")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The second-generation architecture is called LOG: Logic-Orientation-Geometry. The name is intentional—it describes how the system reasons about the world. LOG inverts the traditional model-prompt-stabilization architecture into a code-first architecture that more closely mirrors how humans actually think.", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "In current transformer architectures, the model generates predictions based on statistical patterns in training data, guided by prompts that try to steer those predictions toward desired outputs. This is induction over patterns. It works, but it's computationally expensive and difficult to control. LOG proposes a different approach: deduction over logical structures.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 The Origin Principle")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "In LOG, the origin (all zeros) represents the simulated state. Input information is processed to find what's congruent—what matches the expected pattern. The inference output matches the input stream, but the attention mechanism generates a vector of what's different, expressed in a geometric base-12 coordinate system.", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "This sounds abstract, but it has concrete hardware implications. Instead of storing attention weights for every possible relationship, LOG builds an induction engine parallel to the CPU's deduction system. The CPU handles explicit logical operations (code-first). The inference engine handles pattern matching and anomaly detection (attention-as-difference). Together, they form a complete reasoning system that can be efficiently implemented in silicon.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.3 Geometric Base-12 Computation")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "Why base-12? It's not arbitrary. Base-12 (duodecimal) has superior divisibility—divisible by 2, 3, 4, and 6—which creates natural symmetry breaking in attention patterns. Binary forces all distinctions into even/odd. Base-12 allows the hardware to naturally express relationships like \"one-third\" and \"one-quarter\" without approximation.", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "In hardware terms, a base-12 attention mechanism could use phase-shifted clock signals to represent geometric coordinates. The attention vector becomes a position in a 12-dimensional space, computed through interference patterns rather than matrix multiplication. This is speculative but grounded in physical principles—it's how RF circuits have done signal processing for decades.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 4: Open Source Commitment
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Open Source Commitment")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 Why MIT License")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The MIT License is the most permissive practical open-source license. Anyone can use, modify, distribute, and sell derivative works with minimal restrictions. This is intentional. I'm not building a moat; I'm building a foundation. The goal isn't to capture value—it's to accelerate development of affordable inference hardware for the edge cases the industry ignores.", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "Proprietary AI hardware follows market incentives: target data centers with billion-dollar budgets, optimize for maximum throughput regardless of power consumption, lock customers into software ecosystems. These incentives don't serve the fisherman on a boat, the researcher in Antarctica, or the humanitarian in a conflict zone. Open source is the only way these use cases get served.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 What's Being Released")] }),
        new Paragraph({ spacing: { after: 100 },
          children: [new TextRun({ text: "This package includes everything needed to understand, reproduce, and extend the TernaryAir architecture:", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 100 },
          children: [new TextRun({ text: "Complete RTL source code in SystemVerilog (RAU, Synaptic Array, Weight ROM, KV Cache, Top Level)", font: "Times New Roman", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 100 },
          children: [new TextRun({ text: "Architecture documentation with block diagrams and timing specifications", font: "Times New Roman", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 100 },
          children: [new TextRun({ text: "Software SDK specification (Python API, streaming interface, profiling tools)", font: "Times New Roman", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 100 },
          children: [new TextRun({ text: "Manufacturing guidelines (process selection, packaging, test procedures)", font: "Times New Roman", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 100 },
          children: [new TextRun({ text: "Business model analysis (cost structures, pricing, market positioning)", font: "Times New Roman", size: 22 })] }),
        new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, spacing: { after: 200 },
          children: [new TextRun({ text: "LOG architecture whitepaper for second-generation development", font: "Times New Roman", size: 22 })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.3 How to Contribute")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The project lives at github.com/superinstance/ternaryair. Contributions are welcome in any form: RTL improvements, verification testbenches, tooling, documentation, applications, even critiques that identify flaws in the approach. The goal is the best possible open inference hardware, not credit for the original design.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ children: [new PageBreak()] }),

        // Section 5: Call to Action
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Call to Action")] }),
        
        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 For Hardware Engineers")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The RTL is ready for synthesis. Target platforms: FPGA prototypes (Xilinx KV260, Intel Cyclone) for Gate 0 validation; MPW shuttles (MOSIS, Europractice) for first silicon. The architecture is deliberately simple—a good engineer could tape out a variant in 6-12 months with a small team. I'm not hoarding IP; I'm publishing a starting point.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 For ML Researchers")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The ternary quantization space is wide open. BitNet b1.58 and iFairy prove the concept works, but there's enormous room for improvement: better training methods for ternary models, architectural modifications that exploit the sparse zero state, hybrid approaches that combine ternary base with higher-precision adapters. The hardware is constrained; the algorithms are not. Push the boundaries.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.3 For Edge Developers")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The SDK specification defines a simple interface: send text in, get text out. No CUDA, no model loading, no memory management. Just inference. The challenge is building applications that work within the constraints: fixed model, limited context, no fine-tuning. These constraints aren't bugs—they're features that force creativity.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.4 For Investors and Manufacturers")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "The $99 price point isn't charity—it's economics. Mask-locked chips have ~90% lower COGS than programmable alternatives. A 28nm process with hardwired weights can achieve 60-70% gross margins at $99 retail. The market is fragmented and underserved. The technology is proven. The execution risk is real but manageable. This isn't a science project; it's a business plan waiting for someone to execute it.", font: "Times New Roman", size: 22, color: colors.body })] }),

        new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.5 The Bottom Line")] }),
        new Paragraph({ spacing: { after: 200 },
          children: [new TextRun({ text: "I built this because I needed it. Out on the water, at 4 AM, making decisions that keep my crew safe, I need intelligence that doesn't depend on Silicon Valley servers or coastal cell towers. I'm releasing it openly because I believe the fastest path to better hardware is more people working on the problem. If this manifesto resonates with you—whether you're an engineer, researcher, investor, or just someone who needs offline AI—there's a place for you in this project.", font: "Times New Roman", size: 22, color: colors.body })] }),
        new Paragraph({ spacing: { after: 400 },
          children: [new TextRun({ text: "Intelligence without internet isn't a luxury. It's infrastructure. Let's build it together.", font: "Times New Roman", size: 22, color: colors.body, bold: true })] }),

        // Signature
        new Paragraph({ spacing: { before: 600 } }),
        new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Casey DiGennaro", size: 24, bold: true, font: "Times New Roman", color: colors.primary })] }),
        new Paragraph({ alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Commercial Fisherman | Edge Hardware Designer | github.com/superinstance", size: 20, font: "Times New Roman", color: colors.secondary })] })
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/z/my-project/download/superinstance-complete-package/docs/TernaryAir_Manifesto.docx", buffer);
  console.log("Manifesto created successfully");
});
