const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType, 
        ShadingType, VerticalAlign, PageNumber, LevelFormat, TableOfContents, PageBreak } = require('docx');
const fs = require('fs');

// Color palette - Midnight Code (technology-focused)
const colors = {
  primary: "020617",      // Midnight Black
  body: "1E293B",         // Deep Slate Blue
  secondary: "64748B",    // Cool Blue-Gray
  accent: "94A3B8",       // Steady Silver
  tableBg: "F8FAFC"       // Glacial Blue-White
};

// Table styling
const tableBorder = { style: BorderStyle.SINGLE, size: 1, color: colors.secondary };
const cellBorders = { top: tableBorder, bottom: tableBorder, left: tableBorder, right: tableBorder };

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Times New Roman", size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal",
        run: { size: 48, bold: true, color: colors.primary, font: "Times New Roman" },
        paragraph: { spacing: { before: 0, after: 200 }, alignment: AlignmentType.CENTER } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: colors.primary, font: "Times New Roman" },
        paragraph: { spacing: { before: 300, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: colors.body, font: "Times New Roman" },
        paragraph: { spacing: { before: 200, after: 150 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, color: colors.secondary, font: "Times New Roman" },
        paragraph: { spacing: { before: 150, after: 100 }, outlineLevel: 2 } },
      { id: "CodeBlock", name: "Code Block", basedOn: "Normal",
        run: { size: 20, font: "Courier New", color: colors.body },
        paragraph: { spacing: { before: 100, after: 100 }, indent: { left: 360 } } }
    ]
  },
  numbering: {
    config: [
      { reference: "bullet-list",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbered-api",
        levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
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
        children: [new TextRun({ text: "SuperInstance.AI SDK Specification v1.0", color: colors.secondary, size: 18 })]
      })] })
    },
    footers: {
      default: new Footer({ children: [new Paragraph({ 
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Page ", color: colors.secondary }), new TextRun({ children: [PageNumber.CURRENT], color: colors.secondary }), new TextRun({ text: " of ", color: colors.secondary }), new TextRun({ children: [PageNumber.TOTAL_PAGES], color: colors.secondary })]
      })] })
    },
    children: [
      // Title
      new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun("SuperInstance.AI SDK Specification")] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [
        new TextRun({ text: "Version 1.0 | March 2026 | Apache 2.0 License", color: colors.secondary, size: 20 })
      ]}),
      
      // TOC
      new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [
        new TextRun({ text: "Note: Right-click TOC and select \"Update Field\" to refresh page numbers", color: "999999", size: 18, italics: true })
      ]}),
      new Paragraph({ children: [new PageBreak()] }),
      
      // Section 1: Overview
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Overview")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "The SuperInstance SDK provides a simple, powerful interface for running large language model (LLM) inference on SuperInstance mask-locked inference hardware. This specification defines the public API that developers can rely on across all SuperInstance product variants (Nano, Standard, Pro, Maker Edition).", color: colors.body })
      ]}),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.1 Design Principles")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Zero-setup: Auto-detect and auto-connect to devices with no configuration required", color: colors.body })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Streaming-first: All generation APIs support token streaming for real-time applications", color: colors.body })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Debuggable: Built-in profiling, inspection, and error handling at every layer", color: colors.body })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Multi-language: Python (P0), C/C++ (P0), Rust (P1), JavaScript (P1) bindings", color: colors.body })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Open: Apache 2.0 licensed with open cartridge format specification", color: colors.body })] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1.2 Quick Start")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("from superinstance import Device, Model")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Zero-setup: auto-detect and connect")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("device = Device()  # Finds first available device")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("model = device.load_cartridge()  # Use inserted model module")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Stream tokens in real-time")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun('for token in model.generate_stream("Hello, I am"):')] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun('    print(token, end="", flush=True)')] }),
      
      // Section 2: Device API
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Device API")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "The Device class represents a physical SuperInstance hardware device. It handles device detection, connection management, and provides access to loaded models.", color: colors.body })
      ]}),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.1 Device Class")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("class Device:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    \"\"\"Represents a SuperInstance inference device.\"\"\"")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    @staticmethod")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    def list_devices() -> List[str]:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("        \"\"\"List available device paths.\"\"\"")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    def __init__(self, device_path: Optional[str] = None):")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("        \"\"\"Connect to device (auto-detect if path not specified).\"\"\"")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    def info(self) -> DeviceInfo:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("        \"\"\"Get device information including type, firmware, temperature.\"\"\"")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    def load_cartridge(self) -> Model:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("        \"\"\"Load model from inserted module.\"\"\"")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    def load_model(self, path: str) -> Model:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("        \"\"\"Load model from file path (Pro/Maker Edition only).\"\"\"")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    def reset(self) -> None:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("        \"\"\"Reset device to initial state.\"\"\"")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2.2 DeviceInfo Data Structure")] }),
      new Table({
        columnWidths: [2340, 2340, 4680],
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Field", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Type", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, verticalAlign: VerticalAlign.CENTER, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Description", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("device_type")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("DeviceType")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("NANO, STANDARD, PRO, or MAKER_EDITION")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("firmware_version")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("str")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Firmware version string (e.g., \"1.2.3\")")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("cartridge_inserted")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("bool")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("True if a model module is inserted")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("cartridge_model")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Optional[str]")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Name of inserted model, or None")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("temperature_celsius")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("float")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Current chip temperature")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("power_watts")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("float")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Current power consumption")] })] })
          ]})
        ]
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 200 }, children: [new TextRun({ text: "Table 1: DeviceInfo Fields", italics: true, color: colors.secondary, size: 18 })] }),
      
      // Section 3: Model API
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Model API")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "The Model class represents a loaded language model and provides methods for text generation, tokenization, and configuration.", color: colors.body })
      ]}),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.1 Generation Methods")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("class Model:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> GenerationResult:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("        \"\"\"Generate complete response for prompt.\"\"\"")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    def generate_stream(self, prompt: str, config: Optional[GenerationConfig] = None) -> Iterator[str]:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("        \"\"\"Stream tokens as they are generated (real-time output).\"\"\"")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    def chat(self, messages: List[dict], config: Optional[GenerationConfig] = None) -> GenerationResult:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("        \"\"\"Chat-style generation with message history.\"\"\"")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3.2 GenerationConfig Parameters")] }),
      new Table({
        columnWidths: [2000, 1500, 1500, 4360],
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Parameter", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Type", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Default", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Description", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("max_tokens")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("int")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("256")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Maximum tokens to generate")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("temperature")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("float")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("0.7")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Sampling temperature (0.0-2.0)")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("top_p")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("float")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("0.9")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Nucleus sampling threshold")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("top_k")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("int")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("40")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Top-k sampling parameter")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("stop_sequences")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("List[str]")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("None")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Stop generation on these sequences")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("seed")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Optional[int]")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("None")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Random seed for reproducibility")] })] })
          ]})
        ]
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 200 }, children: [new TextRun({ text: "Table 2: GenerationConfig Parameters", italics: true, color: colors.secondary, size: 18 })] }),
      
      // Section 4: Profiling API
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Profiling and Debug API")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "The SDK includes built-in profiling and debugging capabilities to help developers optimize their applications and troubleshoot issues.", color: colors.body })
      ]}),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.1 Profiler Class")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("from superinstance import Profiler")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("with Profiler() as p:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    output = model.generate(\"Hello\")")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("report = p.report()")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("print(f\"Tokens/sec: {report.throughput_tok_per_s}\")")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("print(f\"Energy: {report.total_energy_mj} mJ\")")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("print(f\"First token latency: {report.first_token_ms} ms\")")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4.2 Inspector Class (Layer-by-Layer Debug)")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("from superinstance.debug import Inspector")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("inspector = Inspector(device)")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("inspector.set_breakpoint(layer=12)  # Pause at layer 12")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("activations = inspector.get_activations(layer=12)")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("attention = inspector.get_attention_weights(layer=12, head=0)")] }),
      
      // Section 5: Model Module Format
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Open Model Module Format")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "SuperInstance uses an open model module format that allows the community to create and share models. The specification is Apache 2.0 licensed and documented publicly.", color: colors.body })
      ]}),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.1 Module Manifest (module.yaml)")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("apiVersion: superinstance.io/v1")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("kind: ModelModule")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("metadata:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("  name: bitnet-2b-chat")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("  version: \"1.0.0\"")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("  license: MIT")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("  author: microsoft")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("spec:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("  model:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    architecture: transformer")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    parameters: 2000000000")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    precision: ternary  # Values: ternary, c4_complex")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    context_length: 4096")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("  compatibility:")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    min_firmware: \"1.0.0\"")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("    devices: [nano, standard, pro, maker_edition]")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5.2 Community Compiler Tools")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "The SDK includes free command-line tools for compiling models to module format:", color: colors.body })
      ]}),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Compile PyTorch model to module format")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("sic-compile model.pt --output model.simod --optimize O2")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Validate module before writing to flash")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("sic-validate model.simod --device /dev/superinstance0")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Write module to flash (Maker Edition)")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("sic-write model.simod --device /dev/superinstance0")] }),
      
      // Section 6: Error Handling
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Error Handling")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "The SDK provides comprehensive error handling with specific exception types for different failure modes:", color: colors.body })
      ]}),
      
      new Table({
        columnWidths: [3000, 6360],
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Exception", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Description", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("DeviceNotFoundError")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("No SuperInstance device detected")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("DeviceBusyError")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Device is in use by another process")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("NoCartridgeError")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("No model module inserted")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("IncompatibleModelError")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Model requires newer firmware or different device")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("ThermalThrottlingError")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Device temperature exceeded safe limit")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("ContextLengthExceededError")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Input exceeds model context length")] })] })
          ]})
        ]
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 200 }, children: [new TextRun({ text: "Table 3: SDK Exception Types", italics: true, color: colors.secondary, size: 18 })] }),
      
      // Section 7: Language Bindings
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Language Bindings")] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "The SDK is available in multiple programming languages with consistent API semantics:", color: colors.body })
      ]}),
      
      new Table({
        columnWidths: [2000, 1500, 5860],
        margins: { top: 100, bottom: 100, left: 150, right: 150 },
        rows: [
          new TableRow({ tableHeader: true, children: [
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Language", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Priority", bold: true })] })] }),
            new TableCell({ borders: cellBorders, shading: { fill: colors.tableBg, type: ShadingType.CLEAR }, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Use Cases", bold: true })] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Python")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("P0")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Data scientists, rapid prototyping, ML integration")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("C/C++")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("P0")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Embedded integration, performance-critical applications")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Rust")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("P1")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Systems programming, WebAssembly deployment")] })] })
          ]}),
          new TableRow({ children: [
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("JavaScript")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun("P1")] })] }),
            new TableCell({ borders: cellBorders, children: [new Paragraph({ children: [new TextRun("Web integration, Node.js backends, Electron apps")] })] })
          ]})
        ]
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 200 }, children: [new TextRun({ text: "Table 4: SDK Language Binding Priorities", italics: true, color: colors.secondary, size: 18 })] }),
      
      // Section 8: Installation
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. Installation")] }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("8.1 Python")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("pip install superinstance-sdk")] }),
      
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("8.2 C/C++")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Include header")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("#include <superinstance/superinstance.h>")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("# Link library")] }),
      new Paragraph({ style: "CodeBlock", children: [new TextRun("gcc -lsuperinstance my_app.c -o my_app")] }),
      
      // Section 9: Support
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("9. Community and Support")] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "GitHub: github.com/superinstance-ai/superinstance-sdk", color: colors.body })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Documentation: docs.superinstance.ai", color: colors.body })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "Discord: discord.gg/superinstance", color: colors.body })] }),
      new Paragraph({ numbering: { reference: "bullet-list", level: 0 }, children: [new TextRun({ text: "License: Apache 2.0", color: colors.body })] }),
      new Paragraph({ spacing: { after: 200 }, children: [
        new TextRun({ text: "The SuperInstance SDK is open source and community-driven. We welcome contributions, bug reports, and feature requests through our GitHub repository.", color: colors.body })
      ]})
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/home/z/my-project/download/SuperInstance_SDK_Specification_v1.0.docx", buffer);
  console.log("SDK Specification document created successfully!");
});
