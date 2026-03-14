"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import {
  Cpu, Layers, Box, Code, Zap, ArrowRight, Download,
  Play, Pause, RotateCcw, Settings, Maximize2, ChevronRight,
  Lightbulb, Target, Globe, FileCode, Microscope, Sparkles,
  GitBranch, BoxIcon, CircuitBoard, Binary, Gauge, Factory,
  Lock, Server, Shield, CheckCircle, Bot, Eye, CloudOff
} from "lucide-react";

// Voxel Block Component
function VoxelBlock({ color, size = 40, delay = 0, active = false, onClick }: { 
  color: string; 
  size?: number; 
  delay?: number; 
  active?: boolean;
  onClick?: () => void;
}) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  return (
    <div
      onClick={onClick}
      className={`transition-all duration-500 cursor-pointer ${visible ? 'opacity-100 scale-100' : 'opacity-0 scale-75'} ${active ? 'ring-2 ring-white ring-opacity-50' : ''}`}
      style={{
        width: size,
        height: size,
        background: `linear-gradient(135deg, ${color} 0%, ${color}dd 100%)`,
        boxShadow: active 
          ? `inset -2px -2px 4px rgba(0,0,0,0.3), inset 2px 2px 4px rgba(255,255,255,0.1), 0 0 20px ${color}80`
          : `inset -2px -2px 4px rgba(0,0,0,0.3), inset 2px 2px 4px rgba(255,255,255,0.1), 0 4px 8px rgba(0,0,0,0.3)`,
        borderRadius: 4,
      }}
    />
  );
}

// Progressive Iteration Layers
const iterationLayers = [
  {
    level: 0,
    title: "Use Case Vision",
    icon: Lightbulb,
    color: "#f59e0b",
    description: "Define your application and compliance requirements",
    example: "Medical imaging device - offline inference, FDA path, <5W power",
    outputs: ["Compliance mapping", "Requirements", "Constraints"],
  },
  {
    level: 1,
    title: "Model Selection",
    icon: Bot,
    color: "#8b5cf6",
    description: "Choose architecture with licensing in mind",
    example: "BitNet b1.58-2B-4T (MIT) → INT4 → 200KB footprint",
    outputs: ["Architecture", "License", "Benchmarks"],
  },
  {
    level: 2,
    title: "Mask-Locked Design",
    icon: Lock,
    color: "#22c55e",
    description: "Design hardwired weight matrix in silicon",
    example: "Systolic array 256×256, weights as metal layers, zero bandwidth",
    outputs: ["Weight encoding", "Datapath", "Timing"],
  },
  {
    level: 3,
    title: "System Integration",
    icon: CircuitBoard,
    color: "#3b82f6",
    description: "Integrate with PCB, power, and I/O",
    example: "LPDDR4 for KV cache, USB-C, isolated power domains",
    outputs: ["PCB layout", "Power budget", "Thermal"],
  },
  {
    level: 4,
    title: "Validation & Test",
    icon: CheckCircle,
    color: "#ec4899",
    description: "Verify functionality and compliance",
    example: "FPGA prototype, formal verification, SPICE simulation",
    outputs: ["Test vectors", "Coverage", "Documentation"],
  },
  {
    level: 5,
    title: "Manufacturing",
    icon: Factory,
    color: "#10b981",
    description: "Generate EDA-ready files for fabrication",
    example: "Verilog + constraints + GDSII for TSMC 28nm",
    outputs: ["RTL", "Constraints", "Test benches"],
  },
];

// Example Projects
const exampleProjects = [
  {
    title: "Medical Imaging",
    domain: "Healthcare",
    description: "FDA-compliant diagnostic inference on device",
    components: ["BitNet 2B", "INT4", "USB-C", "3W"],
    difficulty: "Regulated",
    power: "3W",
    throughput: "80 tok/s",
  },
  {
    title: "Fraud Detection",
    domain: "Financial",
    description: "Real-time transaction analysis, air-gapped",
    components: ["Gemma 2B", "INT4", "PCIe", "On-prem"],
    difficulty: "Compliance",
    power: "5W",
    throughput: "60 tok/s",
  },
  {
    title: "Industrial Monitor",
    domain: "Manufacturing",
    description: "Anomaly detection for predictive maintenance",
    components: ["Qwen 3B", "INT4", "M.2", "Edge"],
    difficulty: "Operational",
    power: "4W",
    throughput: "50 tok/s",
  },
];

// Voxel presets
const chipPresets = [
  { 
    name: "Mask-Locked Core", 
    blocks: 16, 
    colors: ["#22c55e", "#4ade80", "#16a34a"],
    description: "Neural network weights hardwired in metal layers"
  },
  { 
    name: "KV Cache", 
    blocks: 8, 
    colors: ["#8b5cf6", "#a78bfa", "#7c3aed"],
    description: "SRAM for attention key-value storage"
  },
  { 
    name: "Control Logic", 
    blocks: 6, 
    colors: ["#3b82f6", "#60a5fa", "#2563eb"],
    description: "Finite state machine for inference sequencing"
  },
  { 
    name: "I/O Interface", 
    blocks: 4, 
    colors: ["#f59e0b", "#fbbf24", "#d97706"],
    description: "USB/PCIe/M.2 communication blocks"
  },
];

// Architecture comparison
const architectureComparison = [
  { 
    aspect: "Weight Storage", 
    traditional: "External DRAM", 
    maskLocked: "Metal layers (hardwired)",
    advantage: "Zero bandwidth bottleneck"
  },
  { 
    aspect: "Memory Access", 
    traditional: "Required per inference", 
    maskLocked: "None (always present)",
    advantage: "100× lower latency"
  },
  { 
    aspect: "Power Draw", 
    traditional: "10-15W (memory heavy)", 
    maskLocked: "2-3W (compute only)",
    advantage: "5× more efficient"
  },
  { 
    aspect: "Security", 
    traditional: "Memory can be read", 
    maskLocked: "Weights ARE silicon",
    advantage: "Cannot be extracted"
  },
  { 
    aspect: "Compliance", 
    traditional: "Complex audit trail", 
    maskLocked: "Deterministic behavior",
    advantage: "Regulation-friendly"
  },
];

export default function TernaryAirPage() {
  const [activeLayer, setActiveLayer] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState(0);
  const [activeVoxels, setActiveVoxels] = useState<number[]>([]);

  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setActiveLayer((prev) => (prev + 1) % iterationLayers.length);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [isPlaying]);

  const toggleVoxel = (index: number) => {
    setActiveVoxels(prev => 
      prev.includes(index) 
        ? prev.filter(i => i !== index)
        : [...prev, index]
    );
  };

  return (
    <div className="animated-bg min-h-screen pt-24 pb-16">
      {/* Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-12">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
            <Lock className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold">
              <span className="gradient-text">TernaryAir</span>
            </h1>
            <p className="text-sm text-gray-500">Mask-Locked Inference Chip Design</p>
          </div>
        </div>

        <p className="text-xl text-gray-300 max-w-3xl mb-4">
          <span className="text-green-400 font-semibold">Our killer app is the chip itself.</span>
          Neural network weights become permanent silicon—no memory bottleneck, 
          no extraction possible, complete air-gapped security.
        </p>
        
        <p className="text-gray-400 max-w-2xl">
          Everything else—learning, tutorials, playgrounds—exists because most people 
          don't understand why they'd want this technology yet. We teach to create informed users.
        </p>
      </div>

      {/* Architecture Comparison */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-12">
        <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
          <div className="p-4 border-b border-dark-600 bg-dark-700/50">
            <div className="flex items-center gap-3">
              <Cpu className="w-5 h-5 text-green-400" />
              <span className="font-semibold">Architecture Comparison</span>
              <span className="text-xs text-gray-500 ml-2">Why mask-locked wins</span>
            </div>
          </div>

          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
              {/* Traditional */}
              <div>
                <div className="text-xs text-red-400 mb-3 uppercase tracking-wide flex items-center gap-2">
                  <CloudOff className="w-4 h-4" />
                  Traditional GPU/NPU
                </div>
                <div className="bg-dark-700/30 rounded-xl p-4 space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-20 h-8 rounded bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400 text-xs">Model</div>
                    <ArrowRight className="w-4 h-4 text-gray-500" />
                    <div className="w-20 h-8 rounded bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 text-xs">DRAM</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-20 h-8 rounded bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-400 text-xs">DRAM</div>
                    <ArrowRight className="w-4 h-4 text-gray-500" />
                    <div className="w-20 h-8 rounded bg-green-500/20 border border-green-500/30 flex items-center justify-center text-green-400 text-xs">GPU</div>
                  </div>
                  <div className="text-red-400 text-xs">⚠ Memory bandwidth bottleneck</div>
                  <div className="text-red-400 text-xs">⚡ 10-15W power consumption</div>
                  <div className="text-red-400 text-xs">🔓 Weights can be extracted</div>
                </div>
              </div>
              
              {/* Mask-Locked */}
              <div>
                <div className="text-xs text-green-400 mb-3 uppercase tracking-wide flex items-center gap-2">
                  <Lock className="w-4 h-4" />
                  Mask-Locked Inference
                </div>
                <div className="bg-dark-700/30 rounded-xl p-4 space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-44 h-8 rounded bg-gradient-to-r from-green-500/30 to-emerald-500/30 border border-green-500/50 flex items-center justify-center text-green-300 text-xs font-bold">Weights = Silicon (Permanent)</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-44 h-8 rounded bg-green-500/20 border border-green-500/30 flex items-center justify-center text-green-400 text-xs">Direct Compute (No Fetch)</div>
                  </div>
                  <div className="text-green-400 text-xs">✓ Zero memory bandwidth</div>
                  <div className="text-green-400 text-xs">⚡ 2-3W power consumption</div>
                  <div className="text-green-400 text-xs">🔒 Weights cannot be extracted</div>
                </div>
              </div>
            </div>

            {/* Comparison Table */}
            <div className="grid grid-cols-4 gap-4 text-sm">
              <div className="text-gray-500 font-medium">Aspect</div>
              <div className="text-gray-500 font-medium">Traditional</div>
              <div className="text-gray-500 font-medium">Mask-Locked</div>
              <div className="text-gray-500 font-medium">Advantage</div>
              
              {architectureComparison.map((row) => (
                <>
                  <div key={row.aspect} className="text-gray-300 py-2 border-t border-dark-700">{row.aspect}</div>
                  <div key={`${row.aspect}-trad`} className="text-red-400/80 py-2 border-t border-dark-700">{row.traditional}</div>
                  <div key={`${row.aspect}-mask`} className="text-green-400 py-2 border-t border-dark-700">{row.maskLocked}</div>
                  <div key={`${row.aspect}-adv`} className="text-cyan-400 py-2 border-t border-dark-700">{row.advantage}</div>
                </>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Left Column: Progressive Iteration */}
          <div className="lg:col-span-2 space-y-6">

            {/* Iteration Layers */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-dark-700/50 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Microscope className="w-5 h-5 text-green-400" />
                  <span className="font-semibold">Progressive Iteration Engine</span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors"
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => setActiveLayer(0)}
                    className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="p-6">
                {/* Layer Navigation */}
                <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-2">
                  {iterationLayers.map((layer, index) => (
                    <button
                      key={layer.level}
                      onClick={() => setActiveLayer(index)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
                        activeLayer === index
                          ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                          : 'bg-dark-700/50 text-gray-400 hover:text-white'
                      }`}
                    >
                      <span className="w-5 h-5 rounded-full flex items-center justify-center text-xs font-mono"
                        style={{ background: activeLayer === index ? layer.color : '#40414f' }}>
                        {layer.level}
                      </span>
                      <span className="hidden sm:inline">{layer.title}</span>
                    </button>
                  ))}
                </div>

                {/* Active Layer Detail */}
                <div className="bg-dark-700/50 rounded-xl p-6 border border-dark-600">
                  <div className="flex items-start gap-4 mb-4">
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center"
                      style={{ background: `linear-gradient(135deg, ${iterationLayers[activeLayer].color}40 0%, ${iterationLayers[activeLayer].color}20 100%)` }}
                    >
                      {(() => {
                        const IconComponent = iterationLayers[activeLayer].icon;
                        return <IconComponent className="w-6 h-6" style={{ color: iterationLayers[activeLayer].color }} />;
                      })()}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold mb-1">
                        {iterationLayers[activeLayer].title}
                      </h3>
                      <p className="text-gray-400 text-sm">
                        {iterationLayers[activeLayer].description}
                      </p>
                    </div>
                  </div>

                  <div className="bg-dark-800/50 rounded-lg p-4 mb-4">
                    <div className="text-xs text-gray-500 mb-2">Example:</div>
                    <code className="text-green-400 text-sm font-mono">
                      {iterationLayers[activeLayer].example}
                    </code>
                  </div>

                  <div className="space-y-2">
                    <div className="text-xs text-gray-500 mb-2">Deliverables:</div>
                    <div className="flex flex-wrap gap-2">
                      {iterationLayers[activeLayer].outputs.map((output) => (
                        <span
                          key={output}
                          className="px-3 py-1 rounded-full text-xs bg-dark-600 text-gray-300 border border-dark-500"
                        >
                          {output}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Voxel Playground */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-dark-700/50 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <BoxIcon className="w-5 h-5 text-purple-400" />
                  <span className="font-semibold">Voxel Playground</span>
                  <span className="text-xs text-gray-500">Visual chip architecture</span>
                </div>
                <div className="flex items-center gap-2">
                  <button className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors">
                    <Settings className="w-4 h-4" />
                  </button>
                  <button className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors">
                    <Maximize2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="p-6">
                {/* Preset Selector */}
                <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-2">
                  {chipPresets.map((preset, index) => (
                    <button
                      key={preset.name}
                      onClick={() => {
                        setSelectedPreset(index);
                        setActiveVoxels([]);
                      }}
                      className={`px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
                        selectedPreset === index
                          ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                          : 'bg-dark-700/50 text-gray-400 hover:text-white'
                      }`}
                    >
                      {preset.name}
                    </button>
                  ))}
                </div>

                {/* Preset Description */}
                <div className="text-sm text-gray-400 mb-4">
                  {chipPresets[selectedPreset].description}
                </div>

                {/* Voxel Grid */}
                <div className="bg-dark-700/30 rounded-xl p-8 border border-dark-600">
                  <div className="flex flex-wrap justify-center gap-2">
                    {Array.from({ length: chipPresets[selectedPreset].blocks }).map((_, i) => (
                      <VoxelBlock
                        key={i}
                        color={activeVoxels.includes(i) 
                          ? "#22c55e" 
                          : chipPresets[selectedPreset].colors[i % 3]}
                        size={36}
                        delay={i * 50}
                        active={activeVoxels.includes(i)}
                        onClick={() => toggleVoxel(i)}
                      />
                    ))}
                  </div>

                  <div className="text-center mt-6">
                    <p className="text-gray-400 text-sm">
                      {chipPresets[selectedPreset].name} • {chipPresets[selectedPreset].blocks} units
                      {activeVoxels.length > 0 && ` • ${activeVoxels.length} selected`}
                    </p>
                  </div>
                </div>

                {/* Controls */}
                <div className="mt-6 flex items-center justify-center gap-4">
                  <button 
                    onClick={() => setActiveVoxels([])}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-600 hover:bg-dark-500 text-sm transition-colors"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Reset
                  </button>
                  <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-600 hover:bg-dark-500 text-sm transition-colors">
                    <Binary className="w-4 h-4" />
                    Export Verilog
                  </button>
                  <Link
                    href="/professional"
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-sm transition-colors"
                  >
                    <FileCode className="w-4 h-4" />
                    Full Tools
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="space-y-6">

            {/* Quick Start */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-dark-700/50">
                <div className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-amber-400" />
                  <span className="font-semibold">Quick Start</span>
                </div>
              </div>

              <div className="p-4 space-y-3">
                <Link
                  href="/professional"
                  className="flex items-center gap-3 p-3 rounded-xl bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 transition-all"
                >
                  <Lock className="w-5 h-5" />
                  <div>
                    <div className="font-medium">Design Chip</div>
                    <div className="text-xs text-green-100">Professional tools</div>
                  </div>
                  <ArrowRight className="w-4 h-4 ml-auto" />
                </Link>

                <Link
                  href="/learning"
                  className="flex items-center gap-3 p-3 rounded-xl bg-dark-700/50 hover:bg-dark-600 border border-dark-600 transition-all"
                >
                  <Lightbulb className="w-5 h-5 text-amber-400" />
                  <div>
                    <div className="font-medium">Start Learning</div>
                    <div className="text-xs text-gray-500">Why this matters</div>
                  </div>
                  <ArrowRight className="w-4 h-4 ml-auto text-gray-500" />
                </Link>
              </div>
            </div>

            {/* Example Projects */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-dark-700/50">
                <div className="flex items-center gap-3">
                  <Target className="w-5 h-5 text-cyan-400" />
                  <span className="font-semibold">Example Projects</span>
                </div>
              </div>

              <div className="p-4 space-y-3">
                {exampleProjects.map((project) => (
                  <div
                    key={project.title}
                    className="p-3 rounded-xl bg-dark-700/30 hover:bg-dark-700/50 border border-dark-600 cursor-pointer transition-all"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium text-sm">{project.title}</h4>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        project.difficulty === 'Regulated' ? 'bg-blue-500/20 text-blue-400' :
                        project.difficulty === 'Compliance' ? 'bg-green-500/20 text-green-400' :
                        'bg-amber-500/20 text-amber-400'
                      }`}>
                        {project.difficulty}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mb-1">{project.domain}</p>
                    <p className="text-xs text-gray-400 mb-2">{project.description}</p>
                    <div className="flex items-center gap-4 text-xs">
                      <span className="text-green-400">{project.power}</span>
                      <span className="text-cyan-400">{project.throughput}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Why Mask-Locked */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-dark-700/50">
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-green-400" />
                  <span className="font-semibold">Why Mask-Locked?</span>
                </div>
              </div>

              <div className="p-4 space-y-3">
                {[
                  { icon: Zap, text: "116× more efficient than GPU" },
                  { icon: Lock, text: "Weights cannot be extracted" },
                  { icon: Eye, text: "Full reasoning transparency" },
                  { icon: Shield, text: "Air-gapped by design" },
                  { icon: CheckCircle, text: "Deterministic for compliance" },
                ].map((item) => (
                  <div key={item.text} className="flex items-center gap-3 p-2 rounded-lg hover:bg-dark-700/50 transition-colors">
                    <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
                      <item.icon className="w-4 h-4 text-green-400" />
                    </div>
                    <span className="text-sm text-gray-300">{item.text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Specs */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-dark-700/50">
                <div className="flex items-center gap-3">
                  <Gauge className="w-5 h-5 text-amber-400" />
                  <span className="font-semibold">Target Specs</span>
                </div>
              </div>

              <div className="p-4 space-y-2 text-sm">
                <div className="flex justify-between py-1 border-b border-dark-700">
                  <span className="text-gray-400">Process</span>
                  <span className="text-green-400 font-mono">TSMC 28nm</span>
                </div>
                <div className="flex justify-between py-1 border-b border-dark-700">
                  <span className="text-gray-400">Power</span>
                  <span className="text-green-400 font-mono">2-3W</span>
                </div>
                <div className="flex justify-between py-1 border-b border-dark-700">
                  <span className="text-gray-400">Throughput</span>
                  <span className="text-green-400 font-mono">25-80 tok/s</span>
                </div>
                <div className="flex justify-between py-1 border-b border-dark-700">
                  <span className="text-gray-400">Model Size</span>
                  <span className="text-green-400 font-mono">1B-7B</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-gray-400">Price Target</span>
                  <span className="text-green-400 font-mono">$15-60</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <div className="bg-gradient-to-r from-green-900/30 via-dark-800 to-emerald-900/30 rounded-2xl p-8 border border-green-500/20 text-center">
          <h2 className="text-2xl font-bold mb-4">The Chip Is Our Product. Everything Else Is Education.</h2>
          <p className="text-gray-400 mb-6 max-w-xl mx-auto">
            We teach because the industry needs to understand why local inference matters.
            When you're ready to build, our professional tools are here.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/professional"
              className="inline-flex items-center gap-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-lg"
            >
              <Lock className="w-5 h-5" />
              Design Your Chip
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/learning"
              className="inline-flex items-center gap-3 bg-dark-700 hover:bg-dark-600 text-white px-8 py-4 rounded-xl font-semibold transition-all border border-dark-500"
            >
              <Lightbulb className="w-5 h-5" />
              Learn Why It Matters
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
