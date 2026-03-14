import Link from "next/link";
import { Cpu, Terminal, Play, ArrowRight, Download, Zap, HardDrive, Box } from "lucide-react";

export default function EngineersPage() {
  const rtlModules = [
    { name: "top_level.sv", lines: 286, desc: "Main inference engine, state machine, I/O" },
    { name: "rau.sv", lines: 169, desc: "Rotation-Accumulate Unit — the key innovation" },
    { name: "synaptic_array.sv", lines: 150, desc: "12×8 PE array with tree adders" },
    { name: "weight_rom.sv", lines: 109, desc: "Mask-locked ternary weight storage" },
    { name: "kv_cache.sv", lines: 100, desc: "Key-value cache for attention" },
  ];

  const specs = [
    { label: "Process", value: "28nm LP" },
    { label: "Die Size", value: "100mm²" },
    { label: "Yield", value: "73.8%" },
    { label: "Die Cost", value: "$7.02" },
    { label: "Package", value: "QFN-64" },
    { label: "Power", value: "4.0W" },
    { label: "Frequency", value: "100 MHz" },
    { label: "Efficiency", value: "25 tok/J" },
  ];

  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-engineer/10 border border-engineer/30 rounded-full px-4 py-2 mb-6">
              <Cpu className="w-4 h-4 text-engineer" />
              <span className="text-engineer text-sm font-medium">For Engineers</span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-bold mb-6">
              <span className="gradient-text-engineer">Hardware Architecture</span>
            </h1>

            <p className="text-xl text-gray-300 mb-4 max-w-3xl mx-auto">
              Complete RTL source, FPGA guides, and silicon design documentation
            </p>

            <p className="text-gray-400 max-w-2xl mx-auto">
              Production-ready SystemVerilog with ~700 lines of RTL. Fully synthesizable,
              validated on FPGA, and ready for silicon implementation.
            </p>
          </div>
        </div>
      </section>

      {/* Key Innovation */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">The RAU: Key Innovation</h2>
              <p className="text-gray-300 mb-4">
                The Rotation-Accumulate Unit replaces multiplication with sign manipulation.
                Ternary weights {"{-1, 0, +1}"} mean multiplication is just switching.
              </p>

              <div className="space-y-4">
                <div className="bg-dark-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-2">Traditional MAC</div>
                  <div className="font-mono text-sm">result = activation × weight</div>
                  <div className="text-xs text-gray-500 mt-1">Gates: ~500 per bit | Power: High</div>
                </div>

                <div className="bg-engineer/10 border border-engineer/30 rounded-lg p-4">
                  <div className="text-sm text-engineer mb-2">TernaryAir RAU</div>
                  <div className="font-mono text-sm">result = activation ⊕ weight</div>
                  <div className="text-xs text-engineer/70 mt-1">Gates: ~50 total | Power: Low</div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-primary-500/10 border border-primary-500/30 rounded-lg">
                <div className="text-primary-400 font-semibold">90% gate reduction | 85% power reduction</div>
              </div>
            </div>

            <div className="code-block">
              <div className="code-header">
                <div className="code-dot bg-red-500" />
                <div className="code-dot bg-yellow-500" />
                <div className="code-dot bg-green-500" />
                <span className="ml-2 text-gray-400 text-sm">rau.sv</span>
              </div>
              <div className="code-content font-mono text-sm">
                <pre>{`// Ternary weights {-1, 0, +1}
always_comb begin
    case (weight)
        W_PLUS_ONE:  rotated = activation;
        W_ZERO:      rotated = 0;
        W_MINUS_ONE: rotated = -activation;
    endcase
end

// That's it. No multiplier.
// Just a case statement.
// ~50 gates total.`}</pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture Diagram */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Architecture</h2>
          </div>

          <div className="code-block max-w-4xl mx-auto">
            <div className="code-header">
              <div className="code-dot bg-red-500" />
              <div className="code-dot bg-yellow-500" />
              <div className="code-dot bg-green-500" />
              <span className="ml-2 text-gray-400 text-sm">Block Diagram</span>
            </div>
            <div className="code-content">
              <pre className="ascii-diagram">{`┌─────────────────────────────────────────────────┐
│              TERNARYAIR CHIP                     │
│                                                  │
│   USB ──▶ [Protocol] ──▶ [Input Buffer]        │
│                              │                   │
│                              ▼                   │
│                       ┌──────────────┐          │
│                       │  PE Array    │◀── Weight│
│                       │  12×8 RAU    │    ROM   │
│                       └──────────────┘          │
│                              │                   │
│                              ▼                   │
│                       [KV Cache] ──▶ USB        │
│                                                  │
│   Process: 28nm │ Power: 4W │ Speed: 100MHz    │
└─────────────────────────────────────────────────┘`}</pre>
            </div>
          </div>
        </div>
      </section>

      {/* RTL Modules */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">RTL Modules</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Production-ready SystemVerilog source files
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
            {rtlModules.map((file) => (
              <div key={file.name} className="bg-dark-700 rounded-lg p-4 border border-dark-500">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-sm text-engineer">{file.name}</span>
                  <span className="text-xs text-gray-500">{file.lines} lines</span>
                </div>
                <p className="text-xs text-gray-400">{file.desc}</p>
              </div>
            ))}
          </div>

          <div className="mt-8 text-center">
            <a
              href="https://github.com/superinstance/ternaryair/tree/main/hardware/rtl"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-engineer hover:text-engineer-light"
            >
              View RTL source on GitHub
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </section>

      {/* Specifications */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Physical Design Specifications</h2>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {specs.map((spec) => (
              <div key={spec.label} className="bg-dark-800 rounded-lg p-4 border border-dark-600 text-center">
                <div className="text-2xl font-bold text-engineer mb-1">{spec.value}</div>
                <div className="text-xs text-gray-400">{spec.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FPGA & Simulation */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* FPGA */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500">
              <div className="flex items-center gap-3 mb-4">
                <HardDrive className="w-6 h-6 text-engineer" />
                <h3 className="text-xl font-semibold">FPGA Prototyping</h3>
              </div>
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <pre>{`# Build bitstream for PYNQ-Z2
cd hardware/fpga
make bitstream BOARD=pynq-z2

# Program FPGA
make program BOARD=pynq-z2

# Or use pre-built
make flash-prebuilt BOARD=pynq-z2`}</pre>
                </div>
              </div>
            </div>

            {/* Simulation */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500">
              <div className="flex items-center gap-3 mb-4">
                <Play className="w-6 h-6 text-engineer" />
                <h3 className="text-xl font-semibold">RTL Simulation</h3>
              </div>
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <pre>{`# Install Icarus Verilog
sudo apt install iverilog

# Compile and run
cd hardware/rtl
iverilog -g2012 -o sim *.sv
vvp sim

# View waveforms
gtkwave dump.vcd`}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-engineer/10 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Start Building</h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Download the complete RTL source and start prototyping today.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-engineer hover:bg-engineer-dark text-white px-8 py-4 rounded-lg font-medium transition-all glow-amber"
            >
              <Download className="w-5 h-5" />
              Download RTL
            </Link>
            <Link
              href="/architecture"
              className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-8 py-4 rounded-lg font-medium transition-all border border-dark-500"
            >
              View Architecture
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
