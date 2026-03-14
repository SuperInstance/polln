import Link from "next/link";
import { ArrowRight, Download } from "lucide-react";

export default function ArchitecturePage() {
  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl sm:text-5xl font-bold mb-6">
              <span className="gradient-text">Architecture Deep Dive</span>
            </h1>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              How TernaryAir works — from high-level design to silicon physics
            </p>
          </div>
        </div>
      </section>

      {/* Overview */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-12">
            {[
              { label: "Efficiency", value: "19.4×", note: "vs NVIDIA A100" },
              { label: "Security", value: "Air-Gapped", note: "Hardware enforced" },
              { label: "Cost", value: "$50-75", note: "BOM target" },
              { label: "Simplicity", value: "Pure Function", note: "No OS required" },
            ].map((item) => (
              <div key={item.label} className="bg-dark-700 rounded-lg p-4 border border-dark-500 text-center">
                <div className="text-2xl font-bold text-primary-400">{item.value}</div>
                <div className="text-sm text-gray-300">{item.label}</div>
                <div className="text-xs text-gray-500">{item.note}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Block Diagram */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4">Block Diagram</h2>
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
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Key Components</h2>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* RAU */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500">
              <h3 className="text-xl font-semibold mb-4 text-primary-400">
                RAU (Rotation-Accumulate Unit)
              </h3>
              <p className="text-sm text-gray-400 mb-4">
                The key innovation. Replaces multiply-accumulate with rotation.
              </p>
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <pre>{`// Traditional MAC: result = a × w
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
              <div className="mt-4 text-sm text-gray-300">
                <strong>Result:</strong> 90% fewer gates, 85% less power
              </div>
            </div>

            {/* Weight ROM */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500">
              <h3 className="text-xl font-semibold mb-4 text-primary-400">
                Mask-Locked Weight ROM
              </h3>
              <p className="text-sm text-gray-400 mb-4">
                Weights stored as physical via patterns in metal layers.
              </p>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-primary-400">✓</span>
                  <span className="text-gray-300">Via present = +1</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">○</span>
                  <span className="text-gray-300">No via = 0</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-developer">◐</span>
                  <span className="text-gray-300">Via to VSS = -1</span>
                </div>
              </div>
              <div className="mt-4 p-3 bg-dark-600 rounded text-xs text-gray-400">
                Cannot be read electronically — it&apos;s geometry, not data
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Specifications Table */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Specifications</h2>
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
                  <tr key={label} className="hover:bg-dark-800">
                    <td className="py-3 px-4 text-gray-400">{label}</td>
                    <td className="py-3 px-4 text-gray-200 font-medium">{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-primary-900/20 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Explore Further</h2>
          <p className="text-gray-400 mb-8">
            Dive into specific areas of the architecture.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/engineers"
              className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-6 py-3 rounded-lg font-medium transition-all"
            >
              <Download className="w-4 h-4" />
              RTL Source
            </Link>
            <Link
              href="/security"
              className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-6 py-3 rounded-lg font-medium transition-all border border-dark-500"
            >
              Security Model
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
