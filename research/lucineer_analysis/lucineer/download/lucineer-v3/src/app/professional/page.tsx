"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import {
  Cpu, Layers, Box, Code, Zap, ArrowRight, Download,
  Play, Pause, RotateCcw, Settings, Maximize2, ChevronRight,
  Lightbulb, Target, Globe, FileCode, Microscope, Sparkles,
  GitBranch, BoxIcon, CircuitBoard, Binary, Gauge, Factory,
  Lock, Server, Shield, CheckCircle, AlertTriangle, Info,
  MessageSquare, Send, Bot, Sliders, Eye, RefreshCw,
  Heart, Landmark, ShieldCheck,
  Fingerprint, Key, CloudOff, WifiOff, ServerOff,
  BookOpen, Gamepad2
} from "lucide-react";

// Industry Certification Standards
const industryStandards = [
  {
    icon: Heart,
    name: "FDA 510(k)",
    industry: "Medical Devices",
    how: "Deterministic behavior, auditable inference, air-gapped data handling",
    status: "Design-ready"
  },
  {
    icon: Landmark,
    name: "SOC2 Type II",
    industry: "Financial Services",
    how: "No data exfiltration possible, full audit trail, transparent reasoning",
    status: "Architecture-certified"
  },
  {
    icon: ShieldCheck,
    name: "HIPAA",
    industry: "Healthcare",
    how: "PHI never leaves device, no network interfaces, physical security",
    status: "Inherent compliance"
  },
  {
    icon: Fingerprint,
    name: "GDPR",
    industry: "EU Data Protection",
    how: "Data processing happens locally, no cross-border transfer",
    status: "Architecture-compliant"
  }
];

// Progressive Iteration Layers
const iterationLayers = [
  {
    level: 0,
    title: "Use Case Definition",
    icon: Lightbulb,
    color: "#f59e0b",
    description: "Define your application requirements, constraints, and compliance needs",
    example: "Medical imaging device - 3B params, <5W power, FDA 510(k) path, offline operation required",
    outputs: ["Compliance mapping", "User requirements", "Environmental constraints"],
  },
  {
    level: 1,
    title: "Model Selection",
    icon: Bot,
    color: "#8b5cf6",
    description: "Choose neural architecture with licensing and certification in mind",
    example: "BitNet b1.58-2B-4T (MIT license) → INT4 quantization → 200KB model footprint",
    outputs: ["Model architecture", "License clearance", "Validation benchmarks"],
  },
  {
    level: 2,
    title: "Mask-Locked Architecture",
    icon: Lock,
    color: "#22c55e",
    description: "Design hardwired weight matrix and deterministic compute units",
    example: "Systolic array 256×256, weights in metal layers, zero memory bandwidth, timing-verified",
    outputs: ["Weight encoding", "Datapath design", "Determinism proof"],
  },
  {
    level: 3,
    title: "System Integration",
    icon: CircuitBoard,
    color: "#3b82f6",
    description: "Integrate with PCB, power domains, and I/O subsystems",
    example: "LPDDR4 512MB for KV cache, isolated power domains, USB-C data interface",
    outputs: ["PCB layout", "Power isolation", "Thermal analysis"],
  },
  {
    level: 4,
    title: "Validation & Test",
    icon: CheckCircle,
    color: "#ec4899",
    description: "Verify functionality, safety properties, and regulatory requirements",
    example: "FPGA prototype at 25 tok/s, formal verification of timing, SPICE confirms <3W",
    outputs: ["Test vectors", "Coverage report", "Compliance documentation"],
  },
  {
    level: 5,
    title: "Manufacturing Export",
    icon: Factory,
    color: "#10b981",
    description: "Generate EDA-ready files with foundry partner integration",
    example: "chip.v + constraints.sdc + GDSII for TSMC 28nm MPW shuttle",
    outputs: ["Verilog RTL", "Constraints", "Test benches"],
  },
];

// Target Configurations with Industry Focus
const targetConfigs = [
  {
    name: "PCIe Desktop",
    icon: Server,
    description: "AI accelerator for workstations and servers",
    specs: ["PCIe Gen4 x8", "Up to 13B params", "External power optional"],
    industries: ["Financial analysis", "Research", "Development workstations"],
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    name: "Edge USB",
    icon: Zap,
    description: "USB-powered edge inference device",
    specs: ["USB-C 5W", "Up to 3B params", "Plug-and-play"],
    industries: ["Medical devices", "Industrial IoT", "Portable diagnostics"],
    gradient: "from-amber-500 to-orange-500",
  },
  {
    name: "M.2 Module",
    icon: CircuitBoard,
    description: "Compact M.2 form factor for embedded systems",
    specs: ["M.2 2280", "Up to 7B params", "Low profile"],
    industries: ["Embedded systems", "Edge servers", "IoT gateways"],
    gradient: "from-purple-500 to-pink-500",
  },
  {
    name: "Custom SoC",
    icon: Cpu,
    description: "Full custom system-on-chip design",
    specs: ["Your specifications", "Any parameter size", "Custom I/O"],
    industries: ["Medical implants", "Defense systems", "Automotive"],
    gradient: "from-green-500 to-emerald-500",
  },
];

// Model Options with Licensing
const modelOptions = [
  { name: "BitNet b1.58-2B", params: "2B", license: "MIT", clearance: "Commercial-ready", efficiency: "★★★★★" },
  { name: "Gemma 2 2B", params: "2B", license: "Apache-2.0", clearance: "Commercial-ready", efficiency: "★★★★☆" },
  { name: "Qwen 2.5 3B", params: "3B", license: "Apache-2.0", clearance: "Commercial-ready", efficiency: "★★★★☆" },
  { name: "Llama 3.2 3B", params: "3B", license: "Llama License", clearance: "Review required", efficiency: "★★★☆☆" },
  { name: "Phi-3 Mini", params: "3.8B", license: "MIT", clearance: "Commercial-ready", efficiency: "★★★☆☆" },
  { name: "Custom Model", params: "Any", license: "Your choice", clearance: "Depends", efficiency: "Varies" },
];

// Power/Efficiency Calculator
function PowerCalculator() {
  const [modelSize, setModelSize] = useState(3);
  const [precision, setPrecision] = useState("INT4");
  
  const estimatedPower = modelSize * (precision === "INT2" ? 0.5 : precision === "INT4" ? 0.8 : 1.5);
  const estimatedToks = Math.round(100 / (modelSize * 0.3));
  
  return (
    <div className="bg-dark-700/50 rounded-xl p-6 border border-dark-600">
      <h4 className="font-semibold mb-4 flex items-center gap-2">
        <Gauge className="w-5 h-5 text-green-400" />
        Power & Throughput Estimator
      </h4>
      
      <div className="space-y-4">
        <div>
          <label className="text-sm text-gray-400 mb-2 block">Model Size (B params)</label>
          <input
            type="range"
            min="1"
            max="13"
            value={modelSize}
            onChange={(e) => setModelSize(parseInt(e.target.value))}
            className="w-full accent-green-500"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>1B</span>
            <span className="text-green-400 font-mono">{modelSize}B</span>
            <span>13B</span>
          </div>
        </div>
        
        <div>
          <label className="text-sm text-gray-400 mb-2 block">Precision</label>
          <div className="flex gap-2">
            {["INT2", "INT4", "INT8"].map((p) => (
              <button
                key={p}
                onClick={() => setPrecision(p)}
                className={`px-4 py-2 rounded-lg text-sm transition-all ${
                  precision === p
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                    : 'bg-dark-600 text-gray-400 hover:text-white'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-dark-600">
          <div>
            <div className="text-xs text-gray-500 mb-1">Estimated Power</div>
            <div className="text-2xl font-bold text-green-400">{estimatedPower.toFixed(1)}W</div>
            <div className="text-xs text-gray-500">Continuous draw</div>
          </div>
          <div>
            <div className="text-xs text-gray-500 mb-1">Est. Throughput</div>
            <div className="text-2xl font-bold text-cyan-400">{estimatedToks} tok/s</div>
            <div className="text-xs text-gray-500">Inference speed</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Chat Message Component
function ChatMessage({ role, content }: { role: "user" | "assistant"; content: string }) {
  return (
    <div className={`flex gap-3 ${role === "user" ? "flex-row-reverse" : ""}`}>
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
        role === "user" ? "bg-blue-500/20" : "bg-green-500/20"
      }`}>
        {role === "user" ? (
          <MessageSquare className="w-4 h-4 text-blue-400" />
        ) : (
          <Bot className="w-4 h-4 text-green-400" />
        )}
      </div>
      <div className={`max-w-[80%] rounded-xl p-3 text-sm ${
        role === "user"
          ? "bg-blue-500/10 border border-blue-500/20"
          : "bg-dark-600 border border-dark-500"
      }`}>
        {content}
      </div>
    </div>
  );
}

// Security Architecture Diagram
function SecurityArchitecture() {
  return (
    <div className="bg-dark-700/30 rounded-xl p-4 border border-dark-600">
      <div className="text-xs text-gray-500 mb-3">Security Architecture</div>
      
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="p-2 rounded bg-red-500/10 border border-red-500/20">
          <CloudOff className="w-4 h-4 mx-auto mb-1 text-red-400" />
          <div className="text-xs text-red-300">No Cloud</div>
        </div>
        <div className="p-2 rounded bg-red-500/10 border border-red-500/20">
          <WifiOff className="w-4 h-4 mx-auto mb-1 text-red-400" />
          <div className="text-xs text-red-300">No Network</div>
        </div>
        <div className="p-2 rounded bg-red-500/10 border border-red-500/20">
          <ServerOff className="w-4 h-4 mx-auto mb-1 text-red-400" />
          <div className="text-xs text-red-300">No Backend</div>
        </div>
      </div>
      
      <div className="mt-3 p-3 rounded bg-green-500/10 border border-green-500/20 text-center">
        <Lock className="w-5 h-5 mx-auto mb-1 text-green-400" />
        <div className="text-xs text-green-300">Weights are silicon</div>
        <div className="text-xs text-green-400">Cannot be extracted, modified, or exfiltrated</div>
      </div>
      
      <div className="mt-3 text-xs text-gray-500 text-center">
        Security guaranteed by physics, not policies
      </div>
    </div>
  );
}

export default function ProfessionalPage() {
  const [activeLayer, setActiveLayer] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [selectedConfig, setSelectedConfig] = useState(0);
  const [chatMessages, setChatMessages] = useState<Array<{role: "user" | "assistant"; content: string}>>([
    { role: "assistant", content: "Welcome to Lucineer Professional. I'm your co-inventor for mask-locked inference chips. Tell me about your use case—medical device, financial system, industrial IoT—and I'll help you design for compliance and performance." },
  ]);
  const [chatInput, setChatInput] = useState("");

  // Auto-cycle through layers when playing
  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setActiveLayer((prev) => (prev + 1) % iterationLayers.length);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [isPlaying]);

  const sendMessage = () => {
    if (!chatInput.trim()) return;
    setChatMessages([
      ...chatMessages,
      { role: "user", content: chatInput },
      { role: "assistant", content: `I understand you're building: "${chatInput}". For mask-locked inference, I'll need to understand your compliance requirements (FDA, HIPAA, SOC2?), power budget, and deployment environment. Based on initial analysis, I'd recommend a 3B parameter model in INT4—this gives you ~80 tok/s at under 3W with deterministic timing for regulatory approval. What's your primary industry and compliance path?` },
    ]);
    setChatInput("");
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
              <span className="gradient-text">Professional Tools</span>
            </h1>
            <p className="text-sm text-gray-500">Mask-Locked Inference Chip Design Suite</p>
          </div>
        </div>

        <p className="text-xl text-gray-300 max-w-3xl">
          Design <span className="text-green-400 font-semibold">regulation-ready</span> AI inference chips. 
          Air-gapped by design. Deterministic by architecture. 
          <span className="text-amber-400"> FDA, HIPAA, SOC2, GDPR—compliance built into silicon.</span>
        </p>
      </div>

      {/* Industry Standards Banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8">
        <div className="bg-gradient-to-r from-green-900/30 via-dark-800 to-emerald-900/30 rounded-xl p-6 border border-green-500/20">
          <div className="text-center mb-4">
            <div className="text-sm text-gray-400 mb-2">Architecture-Level Compliance</div>
            <div className="text-lg font-semibold text-white">
              These aren't afterthoughts. Compliance is designed in from Layer 0.
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {industryStandards.map((standard) => (
              <div key={standard.name} className="bg-dark-700/30 rounded-lg p-3 text-center">
                <standard.icon className="w-6 h-6 mx-auto mb-2 text-green-400" />
                <div className="text-sm font-medium text-white">{standard.name}</div>
                <div className="text-xs text-gray-500">{standard.industry}</div>
                <div className="text-xs text-green-400 mt-1">{standard.status}</div>
              </div>
            ))}
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
                    <div className="text-xs text-gray-500 mb-2">Example Output:</div>
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

            {/* Target Configuration Selector */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-dark-700/50 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Server className="w-5 h-5 text-cyan-400" />
                  <span className="font-semibold">Target Configuration</span>
                </div>
              </div>

              <div className="p-6">
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {targetConfigs.map((config, index) => (
                    <button
                      key={config.name}
                      onClick={() => setSelectedConfig(index)}
                      className={`p-4 rounded-xl text-left transition-all ${
                        selectedConfig === index
                          ? 'bg-gradient-to-br ' + config.gradient + ' bg-opacity-20 border-2 border-opacity-50'
                          : 'bg-dark-700/30 border border-dark-600 hover:border-dark-500'
                      }`}
                      style={selectedConfig === index ? { borderColor: config.gradient.includes('blue') ? '#3b82f6' : config.gradient.includes('amber') ? '#f59e0b' : config.gradient.includes('purple') ? '#8b5cf6' : '#22c55e' } : {}}
                    >
                      <config.icon className={`w-8 h-8 mb-3 ${
                        selectedConfig === index ? 'text-white' : 'text-gray-400'
                      }`} />
                      <h4 className="font-medium text-sm mb-1">{config.name}</h4>
                      <p className="text-xs text-gray-500 mb-2">{config.description}</p>
                      <div className="space-y-1 mb-2">
                        {config.specs.map((spec) => (
                          <div key={spec} className="text-xs text-gray-400 flex items-center gap-1">
                            <ChevronRight className="w-3 h-3" />
                            {spec}
                          </div>
                        ))}
                      </div>
                      <div className="pt-2 border-t border-dark-600">
                        <div className="text-xs text-gray-500">Industries:</div>
                        <div className="text-xs text-green-400">
                          {config.industries.slice(0, 2).join(', ')}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Model Selection & Power Calculator */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Model Selection */}
              <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
                <div className="p-4 border-b border-dark-600 bg-dark-700/50">
                  <div className="flex items-center gap-3">
                    <Bot className="w-5 h-5 text-purple-400" />
                    <span className="font-semibold">Model Selection</span>
                  </div>
                </div>

                <div className="p-4 space-y-2">
                  {modelOptions.map((model) => (
                    <div
                      key={model.name}
                      className="p-3 rounded-lg bg-dark-700/30 hover:bg-dark-700/50 border border-dark-600 cursor-pointer transition-all"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="font-medium text-sm">{model.name}</div>
                        <div className="text-xs text-amber-400">{model.efficiency}</div>
                      </div>
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-gray-500">{model.params} params • {model.license}</div>
                        <div className={`text-xs ${model.clearance === 'Commercial-ready' ? 'text-green-400' : 'text-amber-400'}`}>
                          {model.clearance}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Power Calculator */}
              <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
                <PowerCalculator />
              </div>
            </div>

            {/* Export Options */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-green-500/30 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-gradient-to-r from-green-900/30 to-emerald-900/30">
                <div className="flex items-center gap-3">
                  <FileCode className="w-5 h-5 text-green-400" />
                  <span className="font-semibold">Export to Manufacturing</span>
                </div>
              </div>

              <div className="p-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  {[
                    { icon: Binary, label: "Verilog RTL", file: "chip.v" },
                    { icon: Sliders, label: "Constraints", file: "constraints.sdc" },
                    { icon: Eye, label: "GDSII Layout", file: "chip.gds" },
                    { icon: CheckCircle, label: "Test Bench", file: "tb_chip.v" },
                  ].map((item) => (
                    <button
                      key={item.label}
                      className="p-4 rounded-xl bg-dark-700/30 hover:bg-dark-700/50 border border-dark-600 text-center transition-all group"
                    >
                      <item.icon className="w-6 h-6 mx-auto mb-2 text-gray-400 group-hover:text-green-400 transition-colors" />
                      <div className="font-medium text-sm">{item.label}</div>
                      <div className="text-xs text-gray-500 font-mono">{item.file}</div>
                    </button>
                  ))}
                </div>

                <div className="flex flex-wrap gap-4">
                  <button className="flex-1 min-w-[200px] flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 font-medium transition-all">
                    <Download className="w-5 h-5" />
                    Export All Files
                  </button>
                  <button className="flex-1 min-w-[200px] flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-dark-600 hover:bg-dark-500 font-medium transition-all border border-dark-500">
                    <RefreshCw className="w-5 h-5" />
                    Sync with Cadence
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: AI Co-Inventor & Resources */}
          <div className="space-y-6">

            {/* AI Co-Inventor Chat */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-green-500/30 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-gradient-to-r from-green-900/30 to-emerald-900/30">
                <div className="flex items-center gap-3">
                  <Sparkles className="w-5 h-5 text-green-400" />
                  <span className="font-semibold">Lucineer Co-Inventor</span>
                </div>
              </div>

              <div className="p-4">
                {/* Chat Messages */}
                <div className="space-y-4 mb-4 max-h-80 overflow-y-auto">
                  {chatMessages.map((msg, i) => (
                    <ChatMessage key={i} role={msg.role} content={msg.content} />
                  ))}
                </div>

                {/* Chat Input */}
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Describe your use case..."
                    className="flex-1 px-4 py-3 rounded-xl bg-dark-700 border border-dark-600 text-white placeholder-gray-500 focus:outline-none focus:border-green-500/50"
                  />
                  <button
                    onClick={sendMessage}
                    className="p-3 rounded-xl bg-green-600 hover:bg-green-500 transition-colors"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Security Architecture */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-dark-700/50">
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-green-400" />
                  <span className="font-semibold">Air-Gapped Architecture</span>
                </div>
              </div>

              <div className="p-4">
                <SecurityArchitecture />
              </div>
            </div>

            {/* Why Mask-Locked? */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-dark-700/50">
                <div className="flex items-center gap-3">
                  <Lock className="w-5 h-5 text-green-400" />
                  <span className="font-semibold">Why Mask-Locked?</span>
                </div>
              </div>

              <div className="p-4 space-y-3">
                {[
                  { icon: Zap, text: "116× more efficient than GPU inference" },
                  { icon: Shield, text: "Air-gapped by design—no network possible" },
                  { icon: Eye, text: "Transparent reasoning—full audit trail" },
                  { icon: Globe, text: "Zero cloud dependency—works offline" },
                  { icon: CheckCircle, text: "Deterministic timing—regulatory-friendly" },
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

            {/* Technical Specifications */}
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-dark-700/50">
                <div className="flex items-center gap-3">
                  <Gauge className="w-5 h-5 text-amber-400" />
                  <span className="font-semibold">Target Specifications</span>
                </div>
              </div>

              <div className="p-4 space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-dark-700">
                  <span className="text-sm text-gray-400">Process Node</span>
                  <span className="text-sm font-mono text-green-400">TSMC 28nm / GF 22FDX</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-dark-700">
                  <span className="text-sm text-gray-400">Power Target</span>
                  <span className="text-sm font-mono text-green-400">2-3W (continuous)</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-dark-700">
                  <span className="text-sm text-gray-400">Throughput</span>
                  <span className="text-sm font-mono text-green-400">25-80 tok/s</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-dark-700">
                  <span className="text-sm text-gray-400">Model Size</span>
                  <span className="text-sm font-mono text-green-400">1B-7B params</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-dark-700">
                  <span className="text-sm text-gray-400">Precision</span>
                  <span className="text-sm font-mono text-green-400">INT2/INT4/INT8</span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-sm text-gray-400">Target Price</span>
                  <span className="text-sm font-mono text-green-400">$15-60 (volume)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Learning Pathway */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <div className="bg-gradient-to-r from-amber-900/20 via-dark-800 to-green-900/20 rounded-2xl p-8 border border-dark-600">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold mb-2">New to Mask-Locked Inference?</h2>
            <p className="text-gray-400">Our learning pathway takes you from fundamentals to production-ready chip design.</p>
          </div>
          
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/learning"
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-amber-600 hover:bg-amber-500 font-medium transition-all"
            >
              <BookOpen className="w-5 h-5" />
              Start Learning Path
            </Link>
            <Link
              href="/ternaryair"
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 font-medium transition-all"
            >
              <Gamepad2 className="w-5 h-5" />
              Try Voxel Playground
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
