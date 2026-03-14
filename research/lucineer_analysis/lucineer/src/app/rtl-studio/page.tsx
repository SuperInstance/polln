"use client";

import { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Head from "next/head";
import Link from "next/link";
import {
  Code2,
  Cpu,
  GitBranch,
  Layers,
  Zap,
  Clock,
  Crosshair,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Play,
  Square,
  FileCode,
  Microchip,
  Route,
  Box,
  Sparkles,
  Gauge,
  Eye,
  Settings,
} from "lucide-react";

// RTL to GDSII Flow Stages
const designStages = [
  {
    id: "rtl-design",
    name: "RTL Design",
    icon: Code2,
    color: "from-blue-500 to-cyan-600",
    description: "Write Verilog/SystemVerilog describing the digital logic",
    inputs: ["Specification", "Architecture Doc"],
    outputs: ["RTL Files (.v, .sv)"],
    tools: ["Vim/VSCode", "Verilator (lint)", "SVLinter"],
    timeEstimate: "2-6 months",
    keyConcepts: [
      { name: "Combinational Logic", formula: "y = f(x)", desc: "Output depends only on current inputs" },
      { name: "Sequential Logic", formula: "Q(t+1) = f(D, clk)", desc: "State depends on clock edges" },
      { name: "FSM Design", formula: "S_next = f(S_curr, inputs)", desc: "Finite State Machine encoding" },
    ],
  },
  {
    id: "synthesis",
    name: "Logic Synthesis",
    icon: Zap,
    color: "from-amber-500 to-orange-600",
    description: "Transform RTL into gate-level netlist using technology library",
    inputs: ["RTL Files", "Constraints (.sdc)", "Tech Library (.lib)"],
    outputs: ["Gate Netlist (.v)", "Timing Reports"],
    tools: ["Yosys (open)", "Synopsys DC", "Cadence Genus"],
    timeEstimate: "1-4 weeks",
    keyConcepts: [
      { name: "Technology Mapping", formula: "RTL → Gates", desc: "Map behavioral to structural" },
      { name: "Optimization", formula: "Minimize Area/Delay", desc: "Boolean simplification" },
      { name: "Timing Constraints", formula: "create_clock -period", desc: "SDC commands" },
    ],
  },
  {
    id: "floorplanning",
    name: "Floorplanning",
    icon: Layers,
    color: "from-purple-500 to-violet-600",
    description: "Define chip area, pin placement, and macro positions",
    inputs: ["Gate Netlist", "Die Size", "I/O Constraints"],
    outputs: ["Floorplan DEF", "Macro Placements"],
    tools: ["OpenROAD", "Cadence Innovus", "Synopsys ICC2"],
    timeEstimate: "1-2 weeks",
    keyConcepts: [
      { name: "Die Area", formula: "A = width × height", desc: "Target chip dimensions" },
      { name: "Aspect Ratio", formula: "AR = H/W", desc: "Shape optimization" },
      { name: "Utilization", formula: "U = Cell_Area / Total_Area", desc: "Target ~70-80%" },
    ],
  },
  {
    id: "placement",
    name: "Placement",
    icon: Crosshair,
    color: "from-green-500 to-emerald-600",
    description: "Position standard cells within rows, optimize wirelength",
    inputs: ["Floorplan DEF", "Netlist", "Constraints"],
    outputs: ["Placed DEF", "Congestion Map"],
    tools: ["OpenROAD", "Cadence Innovus", "Synopsys ICC2"],
    timeEstimate: "1-3 days",
    keyConcepts: [
      { name: "Global Placement", formula: "Min Σ wirelength", desc: "Rough positioning" },
      { name: "Legalization", formula: "Snap to rows", desc: "Align to grid" },
      { name: "HPWL", formula: "HPWL = Σ|x_i - x_j| + |y_i - y_j|", desc: "Half-perimeter wirelength" },
    ],
  },
  {
    id: "cts",
    name: "Clock Tree Synthesis",
    icon: Clock,
    color: "from-cyan-500 to-blue-600",
    description: "Build balanced clock distribution network",
    inputs: ["Placed DEF", "Clock Constraints"],
    outputs: ["Clock Tree DEF", "Skew Report"],
    tools: ["OpenROAD", "Cadence CTS", "Synopsys CTS"],
    timeEstimate: "1-2 days",
    keyConcepts: [
      { name: "Clock Skew", formula: "skew = max(Δt) - min(Δt)", desc: "Arrival time difference" },
      { name: "Insertion Delay", formula: "t_insert = t_sink - t_source", desc: "Clock latency" },
      { name: "Buffer Tree", formula: "H-tree / fishbone", desc: "Balanced distribution" },
    ],
  },
  {
    id: "routing",
    name: "Routing",
    icon: Route,
    color: "from-pink-500 to-rose-600",
    description: "Connect all nets through metal layers",
    inputs: ["Placed DEF", "Design Rules"],
    outputs: ["Routed DEF", "DRC Clean"],
    tools: ["OpenROAD", "Cadence NanoRoute", "Synopsys ICC2"],
    timeEstimate: "2-5 days",
    keyConcepts: [
      { name: "Global Routing", formula: "Channel assignment", desc: "Coarse path planning" },
      { name: "Detailed Routing", formula: "Track assignment", desc: "Exact wire paths" },
      { name: "Via Stacks", formula: "M1→M2→M3...", desc: "Layer transitions" },
    ],
  },
  {
    id: "timing-signoff",
    name: "Timing Signoff",
    icon: Gauge,
    color: "from-red-500 to-orange-600",
    description: "Static timing analysis to verify all paths meet constraints",
    inputs: ["Routed DEF", "SPEF (parasitics)", "Constraints"],
    outputs: ["Timing Reports", "Violations"],
    tools: ["OpenSTA", "Synopsys PrimeTime", "Cadence Tempus"],
    timeEstimate: "1-2 weeks",
    keyConcepts: [
      { name: "Setup Time", formula: "t_arrival + margin < t_capture", desc: "Must arrive before edge" },
      { name: "Hold Time", formula: "t_arrival > t_capture + hold", desc: "Must not arrive too early" },
      { name: "Slack", formula: "S = required - arrival", desc: "Positive = good" },
    ],
  },
  {
    id: "physical-verification",
    name: "Physical Verification",
    icon: CheckCircle2,
    color: "from-emerald-500 to-green-600",
    description: "DRC, LVS, and antenna checks",
    inputs: ["GDSII", "Layout Rules", "Schematic"],
    outputs: ["Clean DRC", "Clean LVS"],
    tools: ["KLayout (DRC)", "Calibre", "Cadence PVS"],
    timeEstimate: "1 week",
    keyConcepts: [
      { name: "DRC", formula: "Design Rule Check", desc: "Min width, spacing, enclosure" },
      { name: "LVS", formula: "Layout vs Schematic", desc: "Netlist equivalence" },
      { name: "Antenna", formula: "Charge accumulation", desc: "Process damage prevention" },
    ],
  },
  {
    id: "tapeout",
    name: "Tapeout",
    icon: Microchip,
    color: "from-indigo-500 to-purple-600",
    description: "Final GDSII export and foundry submission",
    inputs: ["Verified GDSII", "Test Patterns", "Documentation"],
    outputs: ["GDSII to Fab", "Mask Data"],
    tools: ["KLayout", "Calibre DRV", "Internal Scripts"],
    timeEstimate: "1 week",
    keyConcepts: [
      { name: "GDSII Format", formula: "Binary layout data", desc: "Industry standard" },
      { name: "Mask Generation", formula: "GDSII → Photomasks", desc: "One per layer" },
      { name: "MPW vs Full Mask", formula: "Shared vs Dedicated", desc: "Cost tradeoff" },
    ],
  },
];

// Code Editor Component
function CodeEditor() {
  const [code, setCode] = useState(`// Ternary MAC Unit for Mask-Locked Weights
module ternary_mac #(
    parameter WIDTH = 8
)(
    input  wire clk,
    input  wire rst_n,
    input  wire signed [WIDTH-1:0] activation,
    input  wire [1:0] weight,  // 00=0, 01=+1, 10=-1
    output reg  signed [WIDTH+7:0] accumulator
);

    // Ternary weight decode: {-1, 0, +1}
    wire signed [WIDTH-1:0] weight_val;
    assign weight_val = (weight == 2'b01) ? activation :
                       (weight == 2'b10) ? -activation :
                       {WIDTH{1'b0}};

    // Accumulate with saturation
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            accumulator <= 0;
        else
            accumulator <= accumulator + weight_val;
    end

endmodule`);

  return (
    <div className="bg-gray-900 rounded-xl overflow-hidden border border-border">
      <div className="flex items-center gap-2 px-4 py-2 bg-gray-800 border-b border-border">
        <FileCode className="w-4 h-4 text-cyan-400" />
        <span className="text-sm text-gray-400">ternary_mac.v</span>
        <span className="ml-auto text-xs text-gray-500">Verilog</span>
      </div>
      <pre className="p-4 text-sm text-gray-300 overflow-x-auto font-mono leading-relaxed">
        {code.split('\n').map((line, i) => (
          <div key={i} className="flex">
            <span className="w-8 text-gray-600 select-none">{i + 1}</span>
            <span className={
              line.includes('module') ? 'text-purple-400' :
              line.includes('input') || line.includes('output') ? 'text-cyan-400' :
              line.includes('wire') || line.includes('reg') ? 'text-blue-400' :
              line.includes('//') ? 'text-gray-500' :
              line.includes('assign') ? 'text-yellow-400' :
              line.includes('always') ? 'text-pink-400' :
              'text-gray-300'
            }>{line}</span>
          </div>
        ))}
      </pre>
    </div>
  );
}

// Stage Card Component
function StageCard({ stage, index, isActive, onClick }: { 
  stage: typeof designStages[0]; 
  index: number;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      onClick={onClick}
      className={`cursor-pointer group transition-all duration-300 ${
        isActive ? 'scale-105' : 'hover:scale-102'
      }`}
    >
      <div className={`relative bg-card rounded-xl border-2 overflow-hidden transition-colors ${
        isActive ? 'border-emerald-500 shadow-lg shadow-emerald-500/20' : 'border-border hover:border-emerald-500/30'
      }`}>
        {isActive && (
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 to-cyan-400" />
        )}
        <div className="p-4">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${stage.color} flex items-center justify-center ${
              isActive ? 'ring-2 ring-white/30' : ''
            }`}>
              <stage.icon className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono bg-muted px-2 py-0.5 rounded">{index + 1}</span>
                <h3 className="font-semibold text-sm">{stage.name}</h3>
              </div>
              <p className="text-xs text-muted-foreground">{stage.timeEstimate}</p>
            </div>
            <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-emerald-400 transition-colors" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Stage Detail View
function StageDetail({ stage }: { stage: typeof designStages[0] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card rounded-2xl border border-border p-6"
    >
      <div className="flex items-center gap-4 mb-6">
        <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${stage.color} flex items-center justify-center`}>
          <stage.icon className="w-7 h-7 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold">{stage.name}</h2>
          <p className="text-muted-foreground">{stage.description}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h4 className="text-sm font-semibold text-muted-foreground mb-2">INPUTS</h4>
          <div className="space-y-2">
            {stage.inputs.map((input, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <div className="w-2 h-2 rounded-full bg-cyan-400" />
                {input}
              </div>
            ))}
          </div>
        </div>
        <div>
          <h4 className="text-sm font-semibold text-muted-foreground mb-2">OUTPUTS</h4>
          <div className="space-y-2">
            {stage.outputs.map((output, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <div className="w-2 h-2 rounded-full bg-emerald-400" />
                {output}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mb-6">
        <h4 className="text-sm font-semibold text-muted-foreground mb-3">KEY CONCEPTS</h4>
        <div className="grid gap-3">
          {stage.keyConcepts.map((concept, i) => (
            <div key={i} className="bg-black/30 rounded-lg p-4 border border-white/10">
              <div className="flex justify-between items-start mb-1">
                <span className="font-medium text-emerald-400">{concept.name}</span>
                <code className="text-xs bg-muted px-2 py-1 rounded">{concept.formula}</code>
              </div>
              <p className="text-sm text-muted-foreground">{concept.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {stage.tools.map((tool, i) => (
          <span key={i} className="px-3 py-1 bg-muted rounded-full text-xs">
            {tool}
          </span>
        ))}
      </div>
    </motion.div>
  );
}

// Flow Visualization
function FlowVisualization({ currentStage }: { currentStage: number }) {
  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <GitBranch className="w-5 h-5 text-purple-400" />
        Design Flow Progress
      </h3>

      <div className="relative">
        {/* Progress Line */}
        <div className="absolute top-6 left-6 right-6 h-1 bg-muted rounded-full">
          <motion.div
            className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${((currentStage + 1) / designStages.length) * 100}%` }}
          />
        </div>

        {/* Stage Nodes */}
        <div className="relative flex justify-between">
          {designStages.map((stage, i) => (
            <div key={stage.id} className="flex flex-col items-center">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center z-10 transition-all ${
                i <= currentStage 
                  ? `bg-gradient-to-br ${stage.color} ring-2 ring-white/30` 
                  : 'bg-muted'
              }`}>
                <stage.icon className={`w-5 h-5 ${i <= currentStage ? 'text-white' : 'text-muted-foreground'}`} />
              </div>
              <span className={`text-xs mt-2 text-center max-w-[60px] ${
                i === currentStage ? 'font-bold text-emerald-400' : 'text-muted-foreground'
              }`}>
                {stage.name.split(' ')[0]}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function RTLStudioPage() {
  const [activeStage, setActiveStage] = useState(0);
  const currentStage = designStages[activeStage];

  return (
    <>
      <Head>
        <title>RTL Studio | Lucineer - Chip Design Flow</title>
        <meta name="description" content="Interactive RTL-to-GDSII design flow visualization for mask-locked inference chips" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-background via-background to-indigo-500/5 pt-20">
        <section className="py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-12"
            >
              <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/30 rounded-full px-4 py-2 mb-6">
                <Code2 className="w-4 h-4 text-indigo-400" />
                <span className="text-indigo-400 text-sm font-medium">Digital Design Studio</span>
              </div>

              <h1 className="text-4xl sm:text-5xl font-bold mb-4">
                <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  RTL to GDSII
                </span>
              </h1>

              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Walk through 9 stages of chip design, from Verilog code to manufacturing-ready layout
              </p>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Stage Selector */}
              <div className="space-y-3">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold">Design Stages</h3>
                  <span className="text-xs text-muted-foreground">{designStages.length} steps</span>
                </div>
                {designStages.map((stage, index) => (
                  <StageCard
                    key={stage.id}
                    stage={stage}
                    index={index}
                    isActive={index === activeStage}
                    onClick={() => setActiveStage(index)}
                  />
                ))}
              </div>

              {/* Main Content */}
              <div className="lg:col-span-2 space-y-6">
                <StageDetail stage={currentStage} />
                <FlowVisualization currentStage={activeStage} />
              </div>
            </div>

            {/* Code Example */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mt-8"
            >
              <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <FileCode className="w-5 h-5 text-cyan-400" />
                Example: Ternary MAC Unit
              </h3>
              <CodeEditor />
            </motion.div>

            {/* Navigation */}
            <div className="mt-12 flex flex-wrap gap-4 justify-center">
              <Link
                href="/manufacturing"
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-card border border-border hover:border-emerald-500/50 transition-colors"
              >
                <Layers className="w-5 h-5 text-emerald-400" />
                Manufacturing Process
              </Link>
              <Link
                href="/math-universe"
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-card border border-border hover:border-purple-500/50 transition-colors"
              >
                <Box className="w-5 h-5 text-purple-400" />
                Math Universe
              </Link>
              <Link
                href="/professional"
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-black font-medium"
              >
                <Cpu className="w-5 h-5" />
                Open Design Studio
              </Link>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
