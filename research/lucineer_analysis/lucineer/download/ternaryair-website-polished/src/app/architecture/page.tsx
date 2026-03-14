import Link from "next/link";
import { ArrowRight, Download, Cpu, Shield, Lock } from "lucide-react";

export default function ArchitecturePage() {
  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 text-green-400 mb-4">
              <Cpu className="w-6 h-6" />
            </div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="gradient-text">Architecture Deep Dive</span>
            </h1>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              How TernaryAir works — from high-level design to silicon physics
            </p>
          </div>
        </div>
      </section>

      {/* Overview Stats */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Efficiency", value: "19.4×", note: "vs NVIDIA A100" },
              { label: "Security", value: "Air-Gapped", note: "Hardware enforced" },
              { label: "Cost", value: "$50-75", note: "BOM target" },
              { label: "Simplicity", value: "Pure Function", note: "No OS required" },
            ].map((item) => (
              <div key={item.label} className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-5 border border-dark-600 text-center">
                <div className="text-2xl font-bold text-green-400">{item.value}</div>
                <div className="text-sm text-gray-300 mt-1">{item.label}</div>
                <div className="text-xs text-gray-500 mt-1">{item.note}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Block Diagram */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Block Diagram</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              High-level system architecture showing data flow and components
            </p>
          </div>

          <div className="code-block max-w-4xl mx-auto">
            <div className="code-header">
              <div className="code-dot bg-red-500" />
              <div className="code-dot bg-yellow-500" />
              <div className="code-dot bg-green-500" />
              <span className="ml-2 text-gray-400 text-sm">System Architecture</span>
            </div>
            <div className="code-content">
              <pre className="ascii-diagram">{`┌─────────────────────────────────────────────────────────────┐
│                        TERNARYAIR CHIP                       │
│                                                              │
│  USB-In ──▶ [Protocol Handler] ──▶ [Input Buffer (SRAM)]    │
│                                           │                  │
│                                           ▼                  │
│                                    ┌─────────────┐           │
│                                    │  PE Array   │           │
│                                    │  12×8×256   │           │
│                                    │  Ternary    │           │
│                                    └─────────────┘           │
│                                           ▲                  │
│                                           │                  │
│                                    ┌─────────────┐           │
│                                    │ Weight ROM  │◀── MASK   │
│                                    │ (Immutable) │    LOCKED │
│                                    └─────────────┘           │
│                                           │                  │
│                                           ▼                  │
│  USB-Out ◀── [Protocol Handler] ◀── [Output Buffer]         │
│                                                              │
└──────────────────────────────────────────────────────────────┘`}</pre>
            </div>
          </div>
        </div>
      </section>

      {/* Key Components */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Key Components</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              The building blocks that make TernaryAir unique
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* RAU */}
            <div className="bg-dark-800/80 rounded-2xl p-8 border border-dark-600">
              <h3 className="text-xl font-semibold mb-4 text-green-400 flex items-center gap-2">
                <Cpu className="w-5 h-5" />
                RAU (Rotation-Accumulate Unit)
              </h3>
              <p className="text-sm text-gray-400 mb-4">
                The key innovation. Replaces multiply-accumulate with rotation.
              </p>
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <pre className="text-gray-300">{`// Traditional MAC: result = a × w
// Requires: multiplier (~500 gates)

// RAU: result = a ⊕ w
// Requires: MUX + sign flip (~50 gates)

case (weight)
  +1: rotated =  activation;  // Pass
   0: rotated =  0;           // Zero
  -1: rotated = -activation;  // Negate
endcase`}</pre>
                </div>
              </div>
              <div className="mt-4 text-sm text-gray-300 font-medium">
                Result: <span className="text-green-400">90% fewer gates, 85% less power</span>
              </div>
            </div>

            {/* Weight ROM */}
            <div className="bg-dark-800/80 rounded-2xl p-8 border border-dark-600">
              <h3 className="text-xl font-semibold mb-4 text-green-400 flex items-center gap-2">
                <Lock className="w-5 h-5" />
                Mask-Locked Weight ROM
              </h3>
              <p className="text-sm text-gray-400 mb-4">
                Weights stored as physical via patterns in metal layers.
              </p>
              <div className="space-y-3 text-sm mb-4">
                <div className="flex items-center gap-3">
                  <span className="w-4 h-4 rounded bg-green-500/30 border border-green-500" />
                  <span className="text-gray-300">Via present = +1</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-4 h-4 rounded bg-dark-600 border border-dark-500" />
                  <span className="text-gray-300">No via = 0</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-4 h-4 rounded bg-amber-500/30 border border-amber-500" />
                  <span className="text-gray-300">Via to VSS = -1</span>
                </div>
              </div>
              <div className="p-4 bg-dark-700 rounded-xl text-sm text-gray-400 border border-dark-500">
                Cannot be read electronically — it&apos;s geometry, not data.
                Extraction requires destructive physical analysis ($100K+).
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Specifications Table */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Specifications</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Target specifications for the production device
            </p>
          </div>

          <div className="overflow-x-auto max-w-3xl mx-auto">
            <table className="w-full text-sm">
              <tbody className="divide-y divide-dark-600">
                {[
                  ["Architecture", "Ternary inference engine"],
                  ["Process", "28nm (or any available node)"],
                  ["PE Array", "12 columns × 8 rows = 96 RAUs"],
                  ["On-chip Memory", "512KB SRAM"],
                  ["Throughput", "100+ tokens/second"],
                  ["Power", "3-5W (USB powered)"],
                  ["Interface", "USB 3.0"],
                  ["Security", "Mask-locked ROM weights"],
                  ["BOM Cost", "$50-75"],
                  ["Target Retail", "$99"],
                ].map(([label, value]) => (
                  <tr key={label} className="hover:bg-dark-800/50 transition-colors">
                    <td className="py-4 px-6 text-gray-400">{label}</td>
                    <td className="py-4 px-6 text-gray-200 font-medium">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Efficiency Comparison */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Efficiency Comparison</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              How TernaryAir compares to alternatives
            </p>
          </div>

          <div className="overflow-x-auto max-w-4xl mx-auto">
            <table className="comparison-table w-full">
              <thead>
                <tr>
                  <th className="text-left">Metric</th>
                  <th className="text-center">NVIDIA A100</th>
                  <th className="text-center">Jetson Orin</th>
                  <th className="text-center text-green-400">TernaryAir</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="text-gray-300">Power (W)</td>
                  <td className="text-center text-gray-400">300</td>
                  <td className="text-center text-gray-400">15-60</td>
                  <td className="text-center text-green-400 font-bold">3-5</td>
                </tr>
                <tr>
                  <td className="text-gray-300">Cost ($)</td>
                  <td className="text-center text-gray-400">10,000+</td>
                  <td className="text-center text-gray-400">500-2000</td>
                  <td className="text-center text-green-400 font-bold">99</td>
                </tr>
                <tr>
                  <td className="text-gray-300">Tokens/sec</td>
                  <td className="text-center text-gray-400">10,000+</td>
                  <td className="text-center text-gray-400">50-200</td>
                  <td className="text-center text-green-400 font-bold">100+</td>
                </tr>
                <tr>
                  <td className="text-gray-300">Tok/Joule</td>
                  <td className="text-center text-gray-400">~33</td>
                  <td className="text-center text-gray-400">~3</td>
                  <td className="text-center text-green-400 font-bold">~25</td>
                </tr>
                <tr>
                  <td className="text-gray-300">Air-gapped</td>
                  <td className="text-center text-red-400">No</td>
                  <td className="text-center text-red-400">No</td>
                  <td className="text-center text-green-400 font-bold">Yes</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-green-900/20 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">Explore Further</h2>
          <p className="text-gray-400 text-lg mb-10">
            Dive into specific areas of the architecture.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/engineers"
              className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-6 py-3 rounded-xl font-medium transition-all glow-green shadow-lg"
            >
              <Download className="w-4 h-4" />
              RTL Source
            </Link>
            <Link
              href="/security"
              className="flex items-center gap-2 bg-dark-700/80 hover:bg-dark-600 text-white px-6 py-3 rounded-xl font-medium transition-all border border-dark-500"
            >
              <Shield className="w-4 h-4" />
              Security Model
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
