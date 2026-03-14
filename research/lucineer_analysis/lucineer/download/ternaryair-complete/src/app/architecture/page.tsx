import Link from "next/link";
import {
  Layers,
  Cpu,
  Zap,
  ArrowRight,
  BookOpen,
  GitBranch,
  Box,
  Database,
} from "lucide-react";

export default function ArchitecturePage() {
  return (
    <div className="min-h-screen pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">Architecture Deep Dive</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Understanding the TernaryAir architecture: RAU, mask-locked weights, and the complete inference pipeline.
          </p>
        </div>

        {/* Core Innovation */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Zap className="w-6 h-6 text-green-400" />
            Core Innovation: The RAU
          </h2>

          <div className="feature-card mb-8">
            <p className="text-gray-300 text-lg mb-6">
              The Rotation-Accumulate Unit (RAU) is the key innovation that makes TernaryAir possible. 
              By using ternary weights {-1, 0, +1}, we replace expensive multiplication operations 
              with simple sign manipulation—a 90% reduction in gates and 85% reduction in power.
            </p>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              <div>
                <h3 className="font-semibold text-lg mb-4 text-red-400">Traditional MAC</h3>
                <div className="code-block">
                  <div className="code-content font-mono text-sm">
                    <div className="text-gray-500">// Multiply-Accumulate</div>
                    <div><span className="text-purple-400">always_ff</span> @(posedge clk)</div>
                    <div>  acc &lt;= acc + (a * w);</div>
                    <br />
                    <div className="text-gray-500">// 8-bit × 8-bit multiplier</div>
                    <div className="text-gray-500">// ~2000 gates per multiplier</div>
                    <div className="text-gray-500">// Power: ~0.2 pJ per operation</div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-lg mb-4 text-green-400">TernaryAir RAU</h3>
                <div className="code-block">
                  <div className="code-content font-mono text-sm">
                    <div className="text-gray-500">// Rotate-Accumulate</div>
                    <div><span className="text-purple-400">always_ff</span> @(posedge clk)</div>
                    <div>  <span className="text-purple-400">case</span> (w)</div>
                    <div>    +1: acc &lt;= acc + a;</div>
                    <div>     0: acc &lt;= acc;</div>
                    <div>    -1: acc &lt;= acc - a;</div>
                    <div>  <span className="text-purple-400">endcase</span></div>
                    <br />
                    <div className="text-green-400/70">// ~50 gates total</div>
                    <div className="text-green-400/70">// Power: ~0.03 pJ per operation</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6">
              <h3 className="font-semibold text-green-400 mb-3">Why This Works</h3>
              <p className="text-gray-300 text-sm leading-relaxed">
                Recent research (BitNet, iFairy) has shown that neural networks can maintain high accuracy 
                with ternary weights. By restricting weights to {-1, 0, +1}, we eliminate the need for 
                multiplication entirely. The weight simply determines whether to add, subtract, or ignore 
                the input. This insight, combined with mask-locking, enables extreme efficiency gains.
              </p>
            </div>
          </div>
        </section>

        {/* Mask-Locked Weights */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Database className="w-6 h-6 text-green-400" />
            Mask-Locked Weights
          </h2>

          <div className="feature-card mb-6">
            <p className="text-gray-300 text-lg mb-6">
              In traditional chips, weights are stored in memory (SRAM/DRAM) and fetched during inference. 
              TernaryAir takes a different approach: weights are encoded directly in the chip&apos;s metal 
              interconnect layers. They become permanent physical structures, not data.
            </p>

            <div className="code-block mb-6">
              <div className="code-header">
                <span className="text-gray-400 text-sm">Via Encoding for Ternary Weights</span>
              </div>
              <div className="code-content">
                <pre className="ascii-diagram">{`Metal Layer Cross-Section:
                        
    ┌────────────────────────────────────────┐
    │           METAL 3 (Signal)              │
    │   ────────┬───────────────┬────────    │
    │           │               │            │
    │     ┌─────┴─────┐   ┌─────┴─────┐      │
    │     │   VIA     │   │   VIA     │      │  ← Via present = weight +1
    │     │  (+1)     │   │   (-1)    │      │  ← Via to complement rail = -1
    │     └─────┬─────┘   └─────┬─────┘      │  ← No via = weight 0
    │           │               │            │
    │   ────────┼───────────────┼────────    │
    │           │               │            │
    │   ────────┴───────────────┴───────    │
    │           METAL 2 (Complement)         │
    └────────────────────────────────────────┘

Benefits:
  • Zero access latency (weights always "present")
  • Zero access energy (no memory read)
  • Infinite bandwidth (all weights available simultaneously)
  • Immutable (cannot be modified by software)`}</pre>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-green-500/10 rounded-lg">
                <div className="text-2xl font-bold text-green-400">0 pJ</div>
                <div className="text-sm text-gray-400">Weight Access Energy</div>
              </div>
              <div className="text-center p-4 bg-green-500/10 rounded-lg">
                <div className="text-2xl font-bold text-green-400">∞</div>
                <div className="text-sm text-gray-400">Weight Bandwidth</div>
              </div>
              <div className="text-center p-4 bg-green-500/10 rounded-lg">
                <div className="text-2xl font-bold text-green-400">0 ns</div>
                <div className="text-sm text-gray-400">Access Latency</div>
              </div>
            </div>
          </div>
        </section>

        {/* System Architecture */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Layers className="w-6 h-6 text-green-400" />
            System Architecture
          </h2>

          <div className="code-block mb-6">
            <div className="code-header">
              <span className="text-gray-400 text-sm">Complete Inference Pipeline</span>
            </div>
            <div className="code-content">
              <pre className="ascii-diagram">{`┌─────────────────────────────────────────────────────────────────────────┐
│                        TERNARYAIR SYSTEM ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   USB                                                                    │
│    │                                                                     │
│    ▼                                                                     │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                        INPUT PROCESSING                            │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │  │
│  │  │  UART/USB   │───▶│  Tokenizer  │───▶│  Embedding  │           │  │
│  │  │  Interface  │    │  (BPE)      │    │  Lookup     │           │  │
│  │  └─────────────┘    └─────────────┘    └─────────────┘           │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                              │                                           │
│                              ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      TRANSFORMER BLOCK × N                         │  │
│  │                                                                     │  │
│  │    ┌─────────────────────────────────────────────────────┐        │  │
│  │    │                    ATTENTION                         │        │  │
│  │    │  ┌─────────┐  ┌─────────┐  ┌─────────┐              │        │  │
│  │    │  │  Q ROM  │  │  K ROM  │  │  V ROM  │              │        │  │
│  │    │  └────┬────┘  └────┬────┘  └────┬────┘              │        │  │
│  │    │       │            │            │                    │        │  │
│  │    │       ▼            ▼            ▼                    │        │  │
│  │    │  ┌────────────────────────────────────────┐         │        │  │
│  │    │  │         RAU ARRAY (Attention)          │         │        │  │
│  │    │  │    [RAU] [RAU] [RAU] ... [RAU]         │         │        │  │
│  │    │  └────────────────────────────────────────┘         │        │  │
│  │    │                      │                              │        │  │
│  │    │                      ▼                              │        │  │
│  │    │              ┌──────────────┐                       │        │  │
│  │    │              │   SOFTMAX    │                       │        │  │
│  │    │              └──────────────┘                       │        │  │
│  │    └─────────────────────────────────────────────────────┘        │  │
│  │                              │                                     │  │
│  │                              ▼                                     │  │
│  │    ┌─────────────────────────────────────────────────────┐        │  │
│  │    │                  FEED-FORWARD                        │        │  │
│  │    │  ┌────────────────┐    ┌────────────────┐           │        │  │
│  │    │  │   W1 ROM       │    │   W2 ROM       │           │        │  │
│  │    │  └───────┬────────┘    └───────┬────────┘           │        │  │
│  │    │          │                      │                    │        │  │
│  │    │          ▼                      ▼                    │        │  │
│  │    │  ┌────────────────────────────────────────┐         │        │  │
│  │    │  │         RAU ARRAY (FFN)                │         │        │  │
│  │    │  └────────────────────────────────────────┘         │        │  │
│  │    └─────────────────────────────────────────────────────┘        │  │
│  │                              │                                     │  │
│  │                              ▼                                     │  │
│  │    ┌─────────────────────────────────────────────────────┐        │  │
│  │    │              KV CACHE (SRAM)                         │        │  │
│  │    │     Store K, V vectors for context                   │        │  │
│  │    └─────────────────────────────────────────────────────┘        │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                              │                                           │
│                              ▼                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                       OUTPUT HEAD                                  │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐           │  │
│  │  │   LM Head   │───▶│   Softmax   │───▶│  Sampling   │───▶ USB   │  │
│  │  │   (RAU)     │    │             │    │             │           │  │
│  │  └─────────────┘    └─────────────┘    └─────────────┘           │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘`}</pre>
            </div>
          </div>
        </section>

        {/* Key Components */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Box className="w-6 h-6 text-green-400" />
            Key Components
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="feature-card">
              <Cpu className="w-8 h-8 text-green-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">RAU Array</h3>
              <p className="text-gray-400 text-sm mb-4">
                Parallel array of Rotation-Accumulate Units. Each RAU handles one weight-element 
                multiplication (as sign manipulation). Arrays are sized per layer dimensions.
              </p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• 768 RAUs per attention head</li>
                <li>• 3072 RAUs per FFN layer</li>
                <li>• 1-cycle latency per operation</li>
              </ul>
            </div>

            <div className="feature-card">
              <Database className="w-8 h-8 text-green-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">Weight ROM</h3>
              <p className="text-gray-400 text-sm mb-4">
                Mask-locked weight storage using via encoding. Zero access latency, infinite bandwidth. 
                Different model variants use different mask sets.
              </p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• 1.5GB for 3B model (INT4)</li>
                <li>• Via-encoded in metal layers</li>
                <li>• 2-metal customization for new models</li>
              </ul>
            </div>

            <div className="feature-card">
              <GitBranch className="w-8 h-8 text-green-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">KV Cache</h3>
              <p className="text-gray-400 text-sm mb-4">
                On-chip SRAM for key-value cache. Stores context for autoregressive generation. 
                Configurable context length.
              </p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• 768MB SRAM for 4K context</li>
                <li>• 192MB for 1K context</li>
                <li>• Banked architecture for parallel access</li>
              </ul>
            </div>

            <div className="feature-card">
              <BookOpen className="w-8 h-8 text-green-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">Control Logic</h3>
              <p className="text-gray-400 text-sm mb-4">
                Hardwired finite state machine for inference sequencing. No CPU, no OS, no software. 
                Fixed-function execution.
              </p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• 12 inference states</li>
                <li>• Single-cycle state transitions</li>
                <li>• No instruction fetch overhead</li>
              </ul>
            </div>
          </div>
        </section>

        {/* CTA */}
        <div className="bg-gradient-to-br from-green-500/10 to-green-900/10 border border-green-500/30 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">Explore the Source</h3>
          <p className="text-gray-400 mb-6">
            View the complete RTL implementation on GitHub or download the full package.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/download" className="btn-primary">
              Download RTL
            </Link>
            <Link href="/engineers" className="btn-secondary">
              Engineer Docs
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
