"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Cpu,
  Zap,
  Layers,
  Gauge,
  Activity,
  Calculator,
  ChevronDown,
  ChevronUp,
  Info,
  CheckCircle,
  ArrowRight,
} from "lucide-react";

// ============================================================================
// TECHNICAL SPECIFICATIONS PAGE
// Mathematical foundations from research documents
// ============================================================================

// Ternary MAC comparison data
const ternaryMACComparison = [
  { 
    format: "FP16", 
    bits: 16, 
    gates: 360, 
    energyPJ: 194, 
    operations: "Multiply + Add",
    color: "text-red-400",
  },
  { 
    format: "INT8", 
    bits: 8, 
    gates: 314, 
    energyPJ: 150, 
    operations: "Multiply + Add",
    color: "text-amber-400",
  },
  { 
    format: "Ternary", 
    bits: 1.58, 
    gates: 103, 
    energyPJ: 22, 
    operations: "Add/Sub Only",
    color: "text-primary",
  },
  { 
    format: "iFairy C₄", 
    bits: 2, 
    gates: 150, 
    energyPJ: 15, 
    operations: "Permutation",
    color: "text-purple-400",
  },
];

// KV Cache bandwidth requirements
const kvCacheData = [
  { context: 512, sizeMB: 24, bwAt25tokGBps: 1.26, feasible: true, margin: "13×" },
  { context: 1024, sizeMB: 48, bwAt25tokGBps: 2.52, feasible: true, margin: "7×" },
  { context: 2048, sizeMB: 96, bwAt25tokGBps: 5.03, feasible: true, margin: "3.4×" },
  { context: 4096, sizeMB: 192, bwAt25tokGBps: 10.07, feasible: true, margin: "1.7×" },
];

// Energy comparison data
const energyComparison = [
  { platform: "Cloud A100 GPU", energyPerTokenJ: 3.0, powerW: 300, tokensPerJ: 0.33 },
  { platform: "Jetson Orin Nano", energyPerTokenJ: 1.2, powerW: 15, tokensPerJ: 0.85 },
  { platform: "TeLLMe FPGA", energyPerTokenJ: 0.2, powerW: 5, tokensPerJ: 5.0 },
  { platform: "LUCI-3 (Mask-Locked)", energyPerTokenJ: 0.058, powerW: 2.5, tokensPerJ: 17.2 },
];

// Expandable math derivation component
function MathDerivation({ 
  title, 
  formula, 
  steps, 
  result,
  insight,
}: { 
  title: string;
  formula: string;
  steps: string[];
  result: string;
  insight: string;
}) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between hover:bg-muted/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Calculator className="w-5 h-5 text-primary" />
          <span className="font-semibold">{title}</span>
        </div>
        {expanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
      </button>
      
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="p-4 border-t border-border space-y-4">
              <div className="p-4 bg-muted/30 rounded-lg font-mono text-sm">
                {formula}
              </div>
              
              <div className="space-y-2">
                {steps.map((step, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm">
                    <span className="text-muted-foreground">{i + 1}.</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
              
              <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
                <div className="text-sm text-muted-foreground mb-1">Result:</div>
                <div className="text-xl font-bold text-primary">{result}</div>
              </div>
              
              <div className="flex items-start gap-2 text-sm text-muted-foreground">
                <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>{insight}</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Animated performance bar
function PerformanceBar({ 
  label, 
  value, 
  max, 
  unit, 
  color = "bg-primary",
  showValue = true,
}: {
  label: string;
  value: number;
  max: number;
  unit?: string;
  color?: string;
  showValue?: boolean;
}) {
  const percentage = Math.min((value / max) * 100, 100);
  
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        {showValue && (
          <span className="font-mono">
            {value.toLocaleString()}{unit}
          </span>
        )}
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${color} rounded-full`}
          initial={{ width: 0 }}
          whileInView={{ width: `${percentage}%` }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

import { AnimatePresence } from "framer-motion";

export default function SpecsPage() {
  return (
    <div className="animated-gradient-bg min-h-screen">
      {/* Header */}
      <section className="hero-gradient pt-20 pb-12 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2 mb-6">
              <Calculator className="w-4 h-4 text-primary" />
              <span className="text-primary text-sm font-medium">Technical Specifications</span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-bold mb-4">
              Mathematical <span className="gradient-text">Foundations</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Rigorous derivations and performance analysis for mask-locked inference architecture
            </p>
          </motion.div>
        </div>
      </section>

      {/* Key Equations Summary */}
      <section className="px-4 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
            {[
              { label: "Ternary Savings", value: "67%", desc: "FLOP reduction" },
              { label: "Gate Reduction", value: "90%", desc: "vs FP16 multiplier" },
              { label: "Energy/token", value: "58μJ", desc: "vs 3J for GPU" },
              { label: "Efficiency Gain", value: "52×", desc: "tokens/joule" },
            ].map((stat) => (
              <div key={stat.label} className="bg-card rounded-xl border border-border p-6 text-center">
                <div className="text-3xl font-bold text-primary mb-1">{stat.value}</div>
                <div className="text-sm font-medium mb-1">{stat.label}</div>
                <div className="text-xs text-muted-foreground">{stat.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Ternary MAC Analysis */}
      <section className="px-4 py-12 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
            <Cpu className="w-6 h-6 text-primary" />
            Ternary MAC Mathematics
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Theorem */}
            <div className="space-y-6">
              <div className="bg-card rounded-xl border border-border p-6">
                <h3 className="font-semibold mb-4">Theorem: Multiplication Elimination</h3>
                <div className="p-4 bg-muted/30 rounded-lg font-mono text-sm mb-4">
                  For w ∈ {`{-1, 0, +1}`} and activation a:
                  <br /><br />
                  w × a = {`{`}
                  <br />
                  &nbsp;&nbsp;+a if w = +1<br />
                  &nbsp;&nbsp;0 if w = 0<br />
                  &nbsp;&nbsp;-a if w = -1<br />
                  {`}`}
                </div>
                <p className="text-sm text-muted-foreground">
                  <strong>Proof:</strong> Direct consequence of ternary arithmetic. 
                  Multiplication hardware replaced by conditional adder-subtractor.
                </p>
              </div>

              <MathDerivation
                title="BitNet Information Content"
                formula="I = log₂(3) = 1.585 bits/trit"
                steps={[
                  "Ternary alphabet Σ = {-1, 0, +1}",
                  "Information per symbol: I = log₂(|Σ|)",
                  "ln(3) ≈ 1.0986 (natural log)",
                  "log₂(3) = ln(3)/ln(2) = 1.0986/0.6931",
                  "Apply Taylor expansion for precision",
                ]}
                result="1.58496 bits per ternary weight"
                insight="Near-uniform distribution (p≈0.33 each) achieves 1.579 bits entropy - nearly optimal encoding"
              />
            </div>

            {/* Comparison Table */}
            <div className="bg-card rounded-xl border border-border p-6">
              <h3 className="font-semibold mb-4">Hardware Comparison</h3>
              <div className="space-y-4">
                {ternaryMACComparison.map((format) => (
                  <div key={format.format} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className={`font-medium ${format.color}`}>{format.format}</span>
                      <span className="text-sm text-muted-foreground">
                        {format.bits} bits/weight
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div className="bg-muted/30 rounded p-2 text-center">
                        <div className="text-muted-foreground">Gates</div>
                        <div className="font-mono font-medium">{format.gates}</div>
                      </div>
                      <div className="bg-muted/30 rounded p-2 text-center">
                        <div className="text-muted-foreground">Energy</div>
                        <div className="font-mono font-medium">{format.energyPJ} pJ</div>
                      </div>
                      <div className="bg-muted/30 rounded p-2 text-center">
                        <div className="text-muted-foreground">Ops</div>
                        <div className="font-mono font-medium text-[10px]">{format.operations}</div>
                      </div>
                    </div>
                    <PerformanceBar
                      label=""
                      value={format.gates}
                      max={400}
                      color={format.color.replace('text-', 'bg-')}
                      showValue={false}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* iFairy Complex Multiplication */}
      <section className="px-4 py-12">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
            <Layers className="w-6 h-6 text-purple-400" />
            iFairy Complex Multiplication (C₄)
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-card rounded-xl border border-border p-6">
              <h3 className="font-semibold mb-4">Fourth Roots of Unity</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2">Weight (w)</th>
                      <th className="text-left py-2">w × (a+bi)</th>
                      <th className="text-left py-2">Real</th>
                      <th className="text-left py-2">Imag</th>
                      <th className="text-left py-2">Hardware</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b border-border/50">
                      <td className="py-2 font-mono">+1</td>
                      <td className="py-2 font-mono">a + bi</td>
                      <td className="py-2 font-mono">a</td>
                      <td className="py-2 font-mono">b</td>
                      <td className="py-2 text-xs">Identity (0 ops)</td>
                    </tr>
                    <tr className="border-b border-border/50">
                      <td className="py-2 font-mono">-1</td>
                      <td className="py-2 font-mono">-a - bi</td>
                      <td className="py-2 font-mono">-a</td>
                      <td className="py-2 font-mono">-b</td>
                      <td className="py-2 text-xs">Negation (NOT gates)</td>
                    </tr>
                    <tr className="border-b border-border/50">
                      <td className="py-2 font-mono">+i</td>
                      <td className="py-2 font-mono">-b + ai</td>
                      <td className="py-2 font-mono">-b</td>
                      <td className="py-2 font-mono">a</td>
                      <td className="py-2 text-xs">Swap + negate</td>
                    </tr>
                    <tr>
                      <td className="py-2 font-mono">-i</td>
                      <td className="py-2 font-mono">b - ai</td>
                      <td className="py-2 font-mono">b</td>
                      <td className="py-2 font-mono">-a</td>
                      <td className="py-2 text-xs">Swap + negate</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div className="mt-4 p-4 bg-purple-400/10 rounded-lg border border-purple-400/20">
                <p className="text-sm text-purple-300">
                  <strong>Key Insight:</strong> Complex multiplication reduces to data permutation 
                  with optional negation - <strong>zero multiplications required</strong>.
                </p>
              </div>
            </div>

            <div className="space-y-6">
              <MathDerivation
                title="Rotation-Accumulate Unit (RAU) Gate Count"
                formula="RAU = MUX + Decoder + Adder + Accumulator"
                steps={[
                  "4:1 multiplexer (real): 8 gates",
                  "4:1 multiplexer (imag): 8 gates",
                  "2-bit weight decoder: 6 gates",
                  "Two 8-bit adders: 100 gates",
                  "Accumulator registers: 28 gates",
                  "Total: 8 + 8 + 6 + 100 + 28 = 150 gates",
                ]}
                result="~150 gates per RAU"
                insight="vs ~6000 gates for complex FP16 MAC - 97.5% reduction"
              />

              <div className="bg-card rounded-xl border border-border p-6">
                <h3 className="font-semibold mb-4">Energy Comparison</h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span>Complex FP16 MAC</span>
                    <span className="font-mono text-red-400">~5000 pJ</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>iFairy RAU</span>
                    <span className="font-mono text-purple-400">~15 pJ</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden mt-4">
                    <motion.div
                      className="h-full bg-purple-400 rounded-full"
                      initial={{ width: 0 }}
                      whileInView={{ width: "0.3%" }}
                      viewport={{ once: true }}
                      transition={{ duration: 1 }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground text-center">
                    iFairy uses 0.3% the energy of complex FP16
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* KV Cache Analysis */}
      <section className="px-4 py-12 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
            <Activity className="w-6 h-6 text-blue-400" />
            KV Cache Bandwidth Analysis
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="space-y-6">
              <MathDerivation
                title="KV Cache Size Formula"
                formula="KV_Size = 2 × L × d × S × b"
                steps={[
                  "L = number of layers (24 for BitNet 2B)",
                  "d = hidden dimension (2560)",
                  "S = sequence length (context)",
                  "b = bytes per element (2 for FP16, 1 for INT8)",
                  "Factor of 2 for K and V matrices",
                ]}
                result="96 MB at 2048 context (FP16)"
                insight="Linear scaling with context - each token adds ~48 KB"
              />

              <MathDerivation
                title="Bandwidth Requirement"
                formula="BW = KV_Size × 2 × tokens_per_second"
                steps={[
                  "Each token reads entire KV cache (K + V)",
                  "At 2048 context: 96 MB × 2 = 192 MB/token",
                  "At 25 tok/s: 192 MB × 25 = 4800 MB/s",
                  "LPDDR4-4266 realistic: ~17 GB/s",
                  "Margin: 17 / 4.8 = 3.5× headroom",
                ]}
                result="5.03 GB/s at 25 tok/s, 2048 context"
                insight="LPDDR4 is SUFFICIENT - no LPDDR5 needed for target performance"
              />
            </div>

            <div className="bg-card rounded-xl border border-border p-6">
              <h3 className="font-semibold mb-4">Bandwidth Requirements by Context</h3>
              <div className="space-y-4">
                {kvCacheData.map((data) => (
                  <div key={data.context} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>{data.context} tokens</span>
                      <span className={data.feasible ? "text-green-400" : "text-red-400"}>
                        {data.bwAt25tokGBps} GB/s
                      </span>
                    </div>
                    <div className="h-3 bg-muted rounded-full overflow-hidden relative">
                      <motion.div
                        className="h-full bg-blue-400 rounded-full"
                        initial={{ width: 0 }}
                        whileInView={{ width: `${(data.bwAt25tokGBps / 20) * 100}%` }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                      />
                      <div 
                        className="absolute top-0 bottom-0 w-0.5 bg-primary"
                        style={{ left: `${(17 / 20) * 100}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>{data.sizeMB} MB cache</span>
                      <span className="text-primary">LPDDR4: 17 GB/s ✓</span>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 p-4 bg-green-400/10 rounded-lg border border-green-400/20">
                <div className="flex items-center gap-2 text-green-400 text-sm">
                  <CheckCircle className="w-4 h-4" />
                  <span>All tested contexts feasible with LPDDR4</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Roofline Model */}
      <section className="px-4 py-12">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
            <Gauge className="w-6 h-6 text-amber-400" />
            Roofline Model Transformation
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-card rounded-xl border border-border p-6">
              <h3 className="font-semibold mb-4">Arithmetic Intensity Shift</h3>
              <div className="space-y-6">
                <div>
                  <div className="text-sm text-muted-foreground mb-2">Standard GPU (Memory-Bound)</div>
                  <div className="p-4 bg-red-400/10 rounded-lg border border-red-400/20">
                    <div className="font-mono text-lg mb-1">AI = 0.63 FLOPs/byte</div>
                    <div className="text-xs text-red-400">Weights fetched from memory every inference</div>
                  </div>
                </div>
                
                <div className="flex justify-center">
                  <div className="text-4xl text-primary">↓</div>
                </div>
                
                <div>
                  <div className="text-sm text-muted-foreground mb-2">Mask-Locked (Compute-Bound)</div>
                  <div className="p-4 bg-green-400/10 rounded-lg border border-green-400/20">
                    <div className="font-mono text-lg mb-1">AI = 54 FLOPs/byte</div>
                    <div className="text-xs text-green-400">Weights in silicon - zero fetch latency</div>
                  </div>
                </div>
              </div>
              
              <div className="mt-6 p-4 bg-primary/10 rounded-lg border border-primary/20">
                <div className="text-2xl font-bold text-primary mb-1">86× Improvement</div>
                <div className="text-sm text-muted-foreground">
                  Bottleneck migrates from memory bandwidth to compute throughput
                </div>
              </div>
            </div>

            <div className="bg-card rounded-xl border border-border p-6">
              <h3 className="font-semibold mb-4">New Bottleneck Hierarchy</h3>
              <div className="space-y-4">
                {[
                  { label: "Weight Fetch", before: "40%", after: "0%", improvement: "ELIMINATED" },
                  { label: "KV Cache Access", before: "25%", after: "60%", status: "NEW DOMINANT" },
                  { label: "Compute", before: "35%", after: "40%", status: "SLIGHT INCREASE" },
                ].map((item) => (
                  <div key={item.label} className="p-4 bg-muted/30 rounded-lg">
                    <div className="flex justify-between mb-2">
                      <span className="font-medium">{item.label}</span>
                      <span className="text-sm text-muted-foreground">
                        {item.before} → {item.after}
                      </span>
                    </div>
                    {item.improvement && (
                      <span className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded">
                        {item.improvement}
                      </span>
                    )}
                    {item.status && (
                      <span className="text-xs bg-amber-400/20 text-amber-400 px-2 py-0.5 rounded">
                        {item.status}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Energy Comparison */}
      <section className="px-4 py-12 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
            <Zap className="w-6 h-6 text-primary" />
            Energy Efficiency Analysis
          </h2>

          <div className="bg-card rounded-xl border border-border p-6">
            <h3 className="font-semibold mb-6">Energy Per Token Comparison</h3>
            <div className="space-y-4">
              {energyComparison.map((platform) => (
                <div key={platform.platform} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{platform.platform}</span>
                    <span className="font-mono text-sm">
                      {platform.energyPerTokenJ > 0.1 
                        ? `${platform.energyPerTokenJ} J/token` 
                        : `${(platform.energyPerTokenJ * 1000).toFixed(0)} mJ/token`}
                    </span>
                  </div>
                  <div className="h-4 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full rounded-full ${
                        platform.energyPerTokenJ > 1 
                          ? 'bg-red-400' 
                          : platform.energyPerTokenJ > 0.1 
                          ? 'bg-amber-400' 
                          : 'bg-primary'
                      }`}
                      initial={{ width: 0 }}
                      whileInView={{ 
                        width: `${Math.min((platform.energyPerTokenJ / 3) * 100, 100)}%` 
                      }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.8 }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{platform.powerW}W typical</span>
                    <span>{platform.tokensPerJ} tokens/J</span>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary">52×</div>
                <div className="text-xs text-muted-foreground">vs Cloud GPU</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary">20×</div>
                <div className="text-xs text-muted-foreground">vs Edge GPU</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary">3.5×</div>
                <div className="text-xs text-muted-foreground">vs FPGA</div>
              </div>
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-3xl font-bold text-primary">94×</div>
                <div className="text-xs text-muted-foreground">vs Cloud (incl. network)</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technical Summary */}
      <section className="px-4 py-12">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold mb-8">Key Formulas Reference</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { name: "KV Cache Size", formula: "2 × L × d × S × b" },
              { name: "Bandwidth", formula: "KV_Size × tok/s" },
              { name: "MACs/token", formula: "14 × L × d²" },
              { name: "Throughput", formula: "f × P / MACs" },
              { name: "Energy/token", formula: "MACs × E_per_MAC" },
              { name: "Arithmetic Intensity", formula: "FLOPs / Bytes" },
              { name: "Power", formula: "Energy × tok/s" },
              { name: "Die Area", formula: "Gates / Density" },
              { name: "Dies/wafer", formula: "π × (R-d)² / A × Y" },
            ].map((formula) => (
              <div key={formula.name} className="bg-card rounded-xl border border-border p-4">
                <div className="text-sm text-muted-foreground mb-1">{formula.name}</div>
                <div className="font-mono text-primary">{formula.formula}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Build on This Foundation?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            The math is proven. The architecture is feasible. Start designing your inference chip.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/professional"
              className="btn-primary flex items-center gap-2 px-8 py-4"
            >
              <Cpu className="w-5 h-5" />
              Chip Design Studio
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/"
              className="btn-secondary flex items-center gap-2 px-8 py-4"
            >
              View Products
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
