import Link from "next/link";
import {
  Cpu,
  HardDrive,
  Zap,
  CheckCircle,
  ArrowRight,
  BookOpen,
  Microchip,
  CircuitBoard,
  Layers,
  Gauge,
} from "lucide-react";

export default function EngineersPage() {
  return (
    <div className="min-h-screen pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 flex items-center justify-center mx-auto mb-6">
            <Cpu className="w-8 h-8 text-amber-400" />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text-engineer">For Engineers</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            RTL source code, FPGA prototyping guides, architecture deep dives, and silicon design documentation.
          </p>
        </div>

        {/* Architecture Overview */}
        <section id="architecture" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Layers className="w-6 h-6 text-amber-400" />
            Architecture Overview
          </h2>

          <div className="code-block mb-6">
            <div className="code-header">
              <div className="code-dot bg-red-500" />
              <div className="code-dot bg-yellow-500" />
              <div className="code-dot bg-green-500" />
              <span className="ml-2 text-gray-400 text-sm">System Block Diagram</span>
            </div>
            <div className="code-content">
              <pre className="ascii-diagram">{`┌─────────────────────────────────────────────────────────────────────┐
│                    TERNARYAIR TOP-LEVEL ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐    ┌────────────────────────────────────────────┐  │
│  │   USB/UART  │───▶│            Token Input Buffer              │  │
│  │   Interface │    └────────────────────────────────────────────┘  │
│  └─────────────┘                         │                          │
│                                          ▼                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    EMBEDDING LOOKUP                         │    │
│  │    (token_id → 768-dim vector, stored in ROM)              │    │
│  └────────────────────────────────────────────────────────────┘    │
│                          │                                          │
│                          ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              TRANSFORMER LAYERS × N                         │    │
│  │  ┌──────────────────────┐  ┌──────────────────────┐        │    │
│  │  │   ATTENTION HEADS    │  │    FEED-FORWARD     │        │    │
│  │  │   (Q,K,V in ROM)     │  │    (Weights in ROM)  │        │    │
│  │  │   RAU Array × M      │  │    RAU Array × K     │        │    │
│  │  └──────────────────────┘  └──────────────────────┘        │    │
│  │              │                      │                       │    │
│  │              └──────────┬───────────┘                       │    │
│  │                         ▼                                   │    │
│  │              ┌──────────────────┐                           │    │
│  │              │  LAYER NORM      │                           │    │
│  │              │  (Fixed Point)   │                           │    │
│  │              └──────────────────┘                           │    │
│  └────────────────────────────────────────────────────────────┘    │
│                          │                                          │
│                          ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    KV CACHE (SRAM)                          │    │
│  │    (Stores K,V vectors for all previous tokens)             │    │
│  └────────────────────────────────────────────────────────────┘    │
│                          │                                          │
│                          ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    OUTPUT HEAD                              │    │
│  │    (LM Head → Softmax → Token Probabilities)               │    │
│  └────────────────────────────────────────────────────────────┘    │
│                          │                                          │
│                          ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    Token Output Buffer                      │    │
│  └────────────────────────────────────────────────────────────┘    │
│                          │                                          │
│                          ▼                                          │
│                    ┌───────────┐                                   │
│                    │ USB/UART  │────────────────────────────────▶  │
│                    │ Output    │                                   │
│                    └───────────┘                                   │
└─────────────────────────────────────────────────────────────────────┘`}</pre>
            </div>
          </div>
        </section>

        {/* RTL Source */}
        <section id="rtl" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <HardDrive className="w-6 h-6 text-amber-400" />
            RTL Source Code
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="feature-card">
              <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                <Microchip className="w-5 h-5 text-amber-400" />
                RAU (Rotation-Accumulate Unit)
              </h3>
              <p className="text-gray-400 text-sm mb-4">
                The core innovation: replaces multiply-accumulate with rotation-accumulate. 
                90% gate reduction vs traditional MAC.
              </p>
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <div className="text-gray-500">// Ternary MAC operation</div>
                  <div><span className="text-purple-400">case</span> (weight)</div>
                  <div>  W_PLUS: out = in;</div>
                  <div>  W_ZERO: out = <span className="text-amber-300">0</span>;</div>
                  <div>  W_MINUS: out = -in;</div>
                  <div><span className="text-purple-400">endcase</span></div>
                </div>
              </div>
            </div>

            <div className="feature-card">
              <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                <CircuitBoard className="w-5 h-5 text-amber-400" />
                Synaptic Array
              </h3>
              <p className="text-gray-400 text-sm mb-4">
                Parallel array of RAUs for matrix-vector multiplication. 
                Parameterized width for different model sizes.
              </p>
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <div><span className="text-purple-400">module</span> synaptic_array #(</div>
                  <div>  <span className="text-blue-300">parameter</span> WIDTH = <span className="text-amber-300">768</span>,</div>
                  <div>  <span className="text-blue-300">parameter</span> DEPTH = <span className="text-amber-300">3072</span></div>
                  <div>) (...);</div>
                </div>
              </div>
            </div>

            <div className="feature-card">
              <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                <Layers className="w-5 h-5 text-amber-400" />
                Weight ROM
              </h3>
              <p className="text-gray-400 text-sm mb-4">
                Mask-locked weight storage. Weights encoded as via patterns in metal layers. 
                Zero runtime access latency.
              </p>
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <div><span className="text-purple-400">module</span> weight_rom #(</div>
                  <div>  <span className="text-blue-300">parameter</span> WEIGHTS = <span className="text-green-400">&quot;weights.hex&quot;</span></div>
                  <div>) (</div>
                  <div>  <span className="text-blue-300">output</span> [DEPTH-1:0] weight</div>
                  <div>);</div>
                </div>
              </div>
            </div>

            <div className="feature-card">
              <h3 className="font-semibold text-lg mb-3 flex items-center gap-2">
                <Gauge className="w-5 h-5 text-amber-400" />
                KV Cache
              </h3>
              <p className="text-gray-400 text-sm mb-4">
                On-chip SRAM for key-value cache. Supports configurable context length 
                (1K, 2K, 4K tokens).
              </p>
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <div><span className="text-purple-400">module</span> kv_cache #(</div>
                  <div>  <span className="text-blue-300">parameter</span> CTX_LEN = <span className="text-amber-300">4096</span>,</div>
                  <div>  <span className="text-blue-300">parameter</span> DIM = <span className="text-amber-300">768</span></div>
                  <div>) (...);</div>
                </div>
              </div>
            </div>
          </div>

          <div className="code-block">
            <div className="code-header">
              <span className="text-gray-400 text-sm">Directory Structure</span>
            </div>
            <div className="code-content font-mono text-sm">
              <div className="text-gray-500">rtl/</div>
              <div className="ml-4">├── <span className="text-amber-300">rau.sv</span> <span className="text-gray-500"># Rotation-Accumulate Unit</span></div>
              <div className="ml-4">├── <span className="text-amber-300">synaptic_array.sv</span> <span className="text-gray-500"># Parallel RAU array</span></div>
              <div className="ml-4">├── <span className="text-amber-300">weight_rom.sv</span> <span className="text-gray-500"># Mask-locked weight storage</span></div>
              <div className="ml-4">├── <span className="text-amber-300">kv_cache.sv</span> <span className="text-gray-500"># KV cache controller</span></div>
              <div className="ml-4">├── <span className="text-amber-300">attention.sv</span> <span className="text-gray-500"># Attention computation</span></div>
              <div className="ml-4">├── <span className="text-amber-300">feedforward.sv</span> <span className="text-gray-500"># Feed-forward network</span></div>
              <div className="ml-4">├── <span className="text-amber-300">layer_norm.sv</span> <span className="text-gray-500"># Layer normalization</span></div>
              <div className="ml-4">├── <span className="text-amber-300">embedding.sv</span> <span className="text-gray-500"># Token embedding</span></div>
              <div className="ml-4">└── <span className="text-amber-300">top_level.sv</span> <span className="text-gray-500"># Inference engine</span></div>
            </div>
          </div>
        </section>

        {/* FPGA Prototyping */}
        <section id="fpga" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <CircuitBoard className="w-6 h-6 text-amber-400" />
            FPGA Prototyping
          </h2>

          <div className="feature-card mb-6">
            <h3 className="font-semibold text-lg mb-4">Recommended Platforms</h3>
            <div className="overflow-x-auto">
              <table className="comparison-table">
                <thead>
                  <tr>
                    <th className="text-left">Platform</th>
                    <th className="text-center">Device</th>
                    <th className="text-center">Est. Perf</th>
                    <th className="text-center">Price</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="text-amber-400 font-medium">Xilinx KV260</td>
                    <td className="text-center">XCZU7EV</td>
                    <td className="text-center">30-50 tok/s</td>
                    <td className="text-center">$199</td>
                  </tr>
                  <tr>
                    <td className="text-gray-300">Xilinx ZCU104</td>
                    <td className="text-center">XCZU7EV</td>
                    <td className="text-center">50-80 tok/s</td>
                    <td className="text-center">$995</td>
                  </tr>
                  <tr>
                    <td className="text-gray-300">PYNQ-Z2</td>
                    <td className="text-center">Zynq-7020</td>
                    <td className="text-center">10-20 tok/s</td>
                    <td className="text-center">$150</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div className="code-block mb-6">
            <div className="code-header">
              <span className="text-gray-400 text-sm">Quick Start - FPGA Synthesis</span>
            </div>
            <div className="code-content font-mono text-sm">
              <div className="text-gray-500"># Clone repository</div>
              <div><span className="text-green-400">$</span> git clone https://github.com/superinstance/ternaryair</div>
              <div><span className="text-green-400">$</span> cd ternaryair/fpga</div>
              <br />
              <div className="text-gray-500"># Setup environment</div>
              <div><span className="text-green-400">$</span> python scripts/setup_environment.py</div>
              <br />
              <div className="text-gray-500"># Synthesize for KV260</div>
              <div><span className="text-green-400">$</span> make synth TARGET=kv260</div>
              <br />
              <div className="text-gray-500"># Program device</div>
              <div><span className="text-green-400">$</span> make program TARGET=kv260</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="download-card text-center">
              <div className="text-2xl font-bold text-amber-400 mb-1">85K</div>
              <div className="text-sm text-gray-400">LUT Usage</div>
              <div className="text-xs text-gray-500 mt-1">37% of KV260</div>
            </div>
            <div className="download-card text-center">
              <div className="text-2xl font-bold text-amber-400 mb-1">0</div>
              <div className="text-sm text-gray-400">DSP Blocks</div>
              <div className="text-xs text-gray-500 mt-1">RAU uses no DSPs</div>
            </div>
            <div className="download-card text-center">
              <div className="text-2xl font-bold text-amber-400 mb-1">2.5W</div>
              <div className="text-sm text-gray-400">Power Target</div>
              <div className="text-xs text-gray-500 mt-1">USB powered</div>
            </div>
          </div>
        </section>

        {/* Silicon Design */}
        <section id="silicon" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Microchip className="w-6 h-6 text-amber-400" />
            Silicon Design
          </h2>

          <div className="feature-card">
            <h3 className="font-semibold text-lg mb-4">Target Specifications</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-amber-500/10 rounded-lg">
                <div className="text-xl font-bold text-amber-400">28nm</div>
                <div className="text-sm text-gray-400">Process Node</div>
              </div>
              <div className="text-center p-4 bg-amber-500/10 rounded-lg">
                <div className="text-xl font-bold text-amber-400">~120mm²</div>
                <div className="text-sm text-gray-400">Die Size</div>
              </div>
              <div className="text-center p-4 bg-amber-500/10 rounded-lg">
                <div className="text-xl font-bold text-amber-400">$99</div>
                <div className="text-sm text-gray-400">Target Price</div>
              </div>
              <div className="text-center p-4 bg-amber-500/10 rounded-lg">
                <div className="text-xl font-bold text-amber-400">3-5W</div>
                <div className="text-sm text-gray-400">Power Budget</div>
              </div>
            </div>

            <p className="text-gray-400 mb-4">
              The mask-locked architecture dramatically reduces silicon area and power consumption by 
              eliminating the need for SRAM weight storage. Weights are encoded directly in metal routing, 
              making them part of the chip&apos;s physical structure.
            </p>

            <div className="flex items-center gap-3">
              <Link href="/architecture" className="text-amber-400 text-sm hover:underline flex items-center gap-1">
                Architecture Deep Dive <ArrowRight className="w-4 h-4" />
              </Link>
              <span className="text-gray-600">|</span>
              <a href="/docs/SILICON_DESIGN.md" className="text-amber-400 text-sm hover:underline">
                Silicon Design Guide
              </a>
            </div>
          </div>
        </section>

        {/* CTA */}
        <div className="bg-gradient-to-br from-amber-500/10 to-amber-900/10 border border-amber-500/30 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">Build the Hardware</h3>
          <p className="text-gray-400 mb-6">
            Download the complete RTL source and start building your own TernaryAir device.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/download" className="btn-primary">
              Download RTL
            </Link>
            <Link href="/architecture" className="btn-secondary">
              Architecture Docs
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
