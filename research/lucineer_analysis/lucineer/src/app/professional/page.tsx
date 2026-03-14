"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Cpu,
  Layers,
  Activity,
  Calculator,
  ArrowRight,
  Play,
  Zap,
  Timer,
  Gauge,
  GitBranch,
  Clock,
  Database,
  Settings,
  Download,
  ExternalLink,
} from "lucide-react";

const tools = [
  {
    id: "cdc",
    title: "CDC Visualization",
    description: "Visualize clock domain crossings and identify metastability risks",
    icon: Layers,
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    id: "pipeline",
    title: "Pipeline Designer",
    description: "Design and optimize pipeline stages for maximum throughput",
    icon: GitBranch,
    color: "text-blue-400",
    bgColor: "bg-blue-400/10",
  },
  {
    id: "analysis",
    title: "Timing Analysis",
    description: "Analyze setup/hold times and calculate timing margins",
    icon: Activity,
    color: "text-amber-400",
    bgColor: "bg-amber-400/10",
  },
  {
    id: "calculator",
    title: "Resource Calculator",
    description: "Estimate FPGA resources and power consumption",
    icon: Calculator,
    color: "text-purple-400",
    bgColor: "bg-purple-400/10",
  },
];

// CDC Visualization Component
function CDCVisualization() {
  const [sourceClock, setSourceClock] = useState(100);
  const [destClock, setDestClock] = useState(75);
  const [syncStages, setSyncStages] = useState(2);

  const mtbf = Math.pow(10, syncStages * 2) * (sourceClock * destClock) / 10000;

  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
          <Layers className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h3 className="font-semibold">Clock Domain Crossing Analyzer</h3>
          <p className="text-sm text-muted-foreground">Visualize and analyze CDC paths</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Visualization */}
        <div className="space-y-4">
          <div className="relative p-8 bg-muted/30 rounded-xl">
            {/* Source Domain */}
            <div className="cdc-domain cdc-domain-a p-4 mb-4">
              <div className="text-sm font-medium text-primary mb-2">Source Clock Domain</div>
              <div className="flex items-center gap-2">
                <div className="w-16 h-8 bg-primary/30 rounded flex items-center justify-center text-xs font-mono">
                  {sourceClock} MHz
                </div>
                <div className="flex-1 h-2 bg-primary/20 rounded">
                  <motion.div
                    className="h-full bg-primary rounded"
                    animate={{ width: ["100%", "0%", "100%"] }}
                    transition={{ duration: 1 / (sourceClock / 100), repeat: Infinity, ease: "linear" }}
                  />
                </div>
              </div>
            </div>

            {/* Synchronizer */}
            <div className="flex justify-center mb-4">
              <div className="flex items-center gap-2 px-4 py-2 bg-amber-400/10 rounded-lg border border-amber-400/30">
                <Zap className="w-4 h-4 text-amber-400" />
                <span className="text-sm font-medium text-amber-400">{syncStages}-Stage Synchronizer</span>
              </div>
            </div>

            {/* Destination Domain */}
            <div className="cdc-domain cdc-domain-b p-4">
              <div className="text-sm font-medium text-blue-400 mb-2">Destination Clock Domain</div>
              <div className="flex items-center gap-2">
                <div className="w-16 h-8 bg-blue-400/30 rounded flex items-center justify-center text-xs font-mono">
                  {destClock} MHz
                </div>
                <div className="flex-1 h-2 bg-blue-400/20 rounded">
                  <motion.div
                    className="h-full bg-blue-400 rounded"
                    animate={{ width: ["100%", "0%", "100%"] }}
                    transition={{ duration: 1 / (destClock / 100), repeat: Infinity, ease: "linear" }}
                  />
                </div>
              </div>
            </div>

            {/* Arrows */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: -1 }}>
              <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
                  <polygon points="0 0, 10 3.5, 0 7" fill="oklch(0.72 0.19 145 / 0.5)" />
                </marker>
              </defs>
            </svg>
          </div>
        </div>

        {/* Controls */}
        <div className="space-y-6">
          <div className="space-y-4">
            <div>
              <label className="text-sm text-muted-foreground mb-2 block">Source Clock (MHz)</label>
              <input
                type="range"
                min="25"
                max="400"
                value={sourceClock}
                onChange={(e) => setSourceClock(parseInt(e.target.value))}
                className="w-full"
              />
              <div className="text-right text-sm font-mono text-primary">{sourceClock} MHz</div>
            </div>

            <div>
              <label className="text-sm text-muted-foreground mb-2 block">Destination Clock (MHz)</label>
              <input
                type="range"
                min="25"
                max="400"
                value={destClock}
                onChange={(e) => setDestClock(parseInt(e.target.value))}
                className="w-full"
              />
              <div className="text-right text-sm font-mono text-blue-400">{destClock} MHz</div>
            </div>

            <div>
              <label className="text-sm text-muted-foreground mb-2 block">Synchronizer Stages</label>
              <input
                type="range"
                min="1"
                max="4"
                value={syncStages}
                onChange={(e) => setSyncStages(parseInt(e.target.value))}
                className="w-full"
              />
              <div className="text-right text-sm font-mono text-amber-400">{syncStages} stages</div>
            </div>
          </div>

          {/* MTBF Calculation */}
          <div className="p-4 bg-muted/50 rounded-xl">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Mean Time Between Failures (MTBF)</span>
              <div className={`text-lg font-mono ${mtbf > 1e9 ? "text-green-400" : mtbf > 1e6 ? "text-amber-400" : "text-red-400"}`}>
                {mtbf > 1e9 ? "> 10⁹" : mtbf > 1e6 ? "10⁶ - 10⁹" : "< 10⁶"} cycles
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              {mtbf > 1e9 
                ? "Excellent reliability - CDC is well-protected" 
                : mtbf > 1e6 
                ? "Good reliability - consider adding more stages for critical paths"
                : "Poor reliability - add synchronizer stages or use FIFO"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Pipeline Designer Component
function PipelineDesigner() {
  const [stages, setStages] = useState(4);
  const [clockFreq, setClockFreq] = useState(200);
  const [pipelineDelay, setPipelineDelay] = useState(5);

  const throughput = clockFreq * 1; // 1 result per cycle
  const latency = stages * (1000 / clockFreq); // ns

  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-blue-400/10 flex items-center justify-center">
          <GitBranch className="w-5 h-5 text-blue-400" />
        </div>
        <div>
          <h3 className="font-semibold">Pipeline Designer</h3>
          <p className="text-sm text-muted-foreground">Design and optimize pipeline stages</p>
        </div>
      </div>

      <div className="space-y-6">
        {/* Pipeline Visualization */}
        <div className="flex items-center gap-2 overflow-x-auto pb-4">
          {/* Input */}
          <div className="flex-shrink-0 w-16 h-16 bg-muted/30 rounded-lg flex items-center justify-center border border-border">
            <span className="text-xs text-muted-foreground">Input</span>
          </div>

          <ArrowRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />

          {/* Stages */}
          {Array.from({ length: stages }).map((_, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex-shrink-0"
            >
              <div className="pipeline-stage w-20 h-16 flex flex-col items-center justify-center">
                <span className="text-xs text-muted-foreground">Stage {i + 1}</span>
                <span className="text-sm font-mono">{pipelineDelay}ns</span>
              </div>
              {i < stages - 1 && <ArrowRight className="w-4 h-4 text-muted-foreground mx-2" />}
            </motion.div>
          ))}

          <ArrowRight className="w-4 h-4 text-muted-foreground flex-shrink-0" />

          {/* Output */}
          <div className="flex-shrink-0 w-16 h-16 bg-primary/10 rounded-lg flex items-center justify-center border border-primary/30">
            <span className="text-xs text-primary">Output</span>
          </div>
        </div>

        {/* Controls */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-muted/30 rounded-xl">
            <div className="text-sm text-muted-foreground mb-2">Pipeline Stages</div>
            <input
              type="range"
              min="2"
              max="10"
              value={stages}
              onChange={(e) => setStages(parseInt(e.target.value))}
              className="w-full mb-2"
            />
            <div className="text-2xl font-bold text-blue-400">{stages}</div>
          </div>

          <div className="p-4 bg-muted/30 rounded-xl">
            <div className="text-sm text-muted-foreground mb-2">Clock Frequency</div>
            <input
              type="range"
              min="50"
              max="500"
              value={clockFreq}
              onChange={(e) => setClockFreq(parseInt(e.target.value))}
              className="w-full mb-2"
            />
            <div className="text-2xl font-bold text-primary">{clockFreq} MHz</div>
          </div>

          <div className="p-4 bg-muted/30 rounded-xl">
            <div className="text-sm text-muted-foreground mb-2">Stage Delay</div>
            <input
              type="range"
              min="1"
              max="10"
              value={pipelineDelay}
              onChange={(e) => setPipelineDelay(parseInt(e.target.value))}
              className="w-full mb-2"
            />
            <div className="text-2xl font-bold text-amber-400">{pipelineDelay}ns</div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-muted/30 rounded-xl text-center">
            <div className="text-sm text-muted-foreground mb-1">Throughput</div>
            <div className="text-xl font-bold text-green-400">{throughput} Mresults/s</div>
          </div>
          <div className="p-4 bg-muted/30 rounded-xl text-center">
            <div className="text-sm text-muted-foreground mb-1">Latency</div>
            <div className="text-xl font-bold text-blue-400">{latency.toFixed(1)}ns</div>
          </div>
          <div className="p-4 bg-muted/30 rounded-xl text-center">
            <div className="text-sm text-muted-foreground mb-1">Efficiency</div>
            <div className="text-xl font-bold text-amber-400">100%</div>
          </div>
          <div className="p-4 bg-muted/30 rounded-xl text-center">
            <div className="text-sm text-muted-foreground mb-1">Cycle Time</div>
            <div className="text-xl font-bold text-purple-400">{(1000 / clockFreq).toFixed(1)}ns</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Resource Calculator Component
function ResourceCalculator() {
  const [lutCount, setLutCount] = useState(1000);
  const [regCount, setRegCount] = useState(500);
  const [bramCount, setBramCount] = useState(10);
  const [dspCount, setDspCount] = useState(8);

  const totalPower = (lutCount * 0.001) + (regCount * 0.0005) + (bramCount * 0.05) + (dspCount * 0.02);
  const utilization = {
    lut: (lutCount / 53200 * 100).toFixed(1),
    reg: (regCount / 106400 * 100).toFixed(1),
    bram: (bramCount / 140 * 100).toFixed(1),
    dsp: (dspCount / 220 * 100).toFixed(1),
  };

  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-purple-400/10 flex items-center justify-center">
          <Calculator className="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <h3 className="font-semibold">FPGA Resource Calculator</h3>
          <p className="text-sm text-muted-foreground">Estimate resources for Xilinx Artix-7</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Sliders */}
        <div className="space-y-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">LUTs</span>
              <span className="font-mono text-primary">{lutCount.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min="100"
              max="50000"
              step="100"
              value={lutCount}
              onChange={(e) => setLutCount(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="h-2 bg-muted rounded-full mt-2 overflow-hidden">
              <div 
                className="h-full bg-primary transition-all"
                style={{ width: `${utilization.lut}%` }}
              />
            </div>
            <div className="text-xs text-right text-muted-foreground mt-1">{utilization.lut}% of 53,200</div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Registers</span>
              <span className="font-mono text-blue-400">{regCount.toLocaleString()}</span>
            </div>
            <input
              type="range"
              min="100"
              max="100000"
              step="100"
              value={regCount}
              onChange={(e) => setRegCount(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="h-2 bg-muted rounded-full mt-2 overflow-hidden">
              <div 
                className="h-full bg-blue-400 transition-all"
                style={{ width: `${utilization.reg}%` }}
              />
            </div>
            <div className="text-xs text-right text-muted-foreground mt-1">{utilization.reg}% of 106,400</div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">BRAM (36Kb)</span>
              <span className="font-mono text-amber-400">{bramCount}</span>
            </div>
            <input
              type="range"
              min="0"
              max="140"
              value={bramCount}
              onChange={(e) => setBramCount(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="h-2 bg-muted rounded-full mt-2 overflow-hidden">
              <div 
                className="h-full bg-amber-400 transition-all"
                style={{ width: `${utilization.bram}%` }}
              />
            </div>
            <div className="text-xs text-right text-muted-foreground mt-1">{utilization.bram}% of 140</div>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">DSP Slices</span>
              <span className="font-mono text-purple-400">{dspCount}</span>
            </div>
            <input
              type="range"
              min="0"
              max="220"
              value={dspCount}
              onChange={(e) => setDspCount(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="h-2 bg-muted rounded-full mt-2 overflow-hidden">
              <div 
                className="h-full bg-purple-400 transition-all"
                style={{ width: `${utilization.dsp}%` }}
              />
            </div>
            <div className="text-xs text-right text-muted-foreground mt-1">{utilization.dsp}% of 220</div>
          </div>
        </div>

        {/* Summary */}
        <div className="space-y-4">
          <div className="p-6 bg-gradient-to-br from-primary/10 to-blue-400/10 rounded-xl border border-primary/20">
            <h4 className="font-semibold mb-4">Power Estimation</h4>
            <div className="text-4xl font-bold text-primary mb-2">{totalPower.toFixed(2)}W</div>
            <p className="text-sm text-muted-foreground">Estimated dynamic power consumption</p>
          </div>

          <div className="p-4 bg-muted/30 rounded-xl">
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <Gauge className="w-4 h-4" /> Resource Summary
            </h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Logic Utilization</span>
                <span className="font-mono">{Math.max(parseFloat(utilization.lut), parseFloat(utilization.reg)).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Memory Utilization</span>
                <span className="font-mono">{utilization.bram}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">DSP Utilization</span>
                <span className="font-mono">{utilization.dsp}%</span>
              </div>
            </div>
          </div>

          <div className="p-4 bg-muted/30 rounded-xl">
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <Database className="w-4 h-4" /> Memory Capacity
            </h4>
            <div className="text-2xl font-bold text-amber-400">{(bramCount * 36).toFixed(0)} Kb</div>
            <p className="text-xs text-muted-foreground mt-1">Total BRAM capacity</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ProfessionalPage() {
  const [activeTool, setActiveTool] = useState("cdc");

  return (
    <div className="animated-gradient-bg min-h-screen">
      {/* Hero Section */}
      <section className="hero-gradient pt-20 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 bg-purple-400/10 border border-purple-400/30 rounded-full px-4 py-2 mb-6">
              <Cpu className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 text-sm font-medium">Professional Hardware Tools</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="gradient-text-purple">Professional</span>
              <br />
              <span className="text-foreground">Timing Tools</span>
            </h1>

            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Advanced tools for hardware engineers: CDC analysis, pipeline optimization, 
              timing closure, and resource estimation.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Tool Selector */}
      <section className="px-4 sm:px-6 lg:px-8 pb-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-wrap justify-center gap-3">
            {tools.map((tool) => (
              <button
                key={tool.id}
                onClick={() => setActiveTool(tool.id)}
                className={`flex items-center gap-2 px-4 py-3 rounded-xl border transition-all duration-200 ${
                  activeTool === tool.id
                    ? `${tool.color} bg-current/10 border-current`
                    : "border-border text-muted-foreground hover:border-foreground/30 hover:bg-muted/30"
                }`}
              >
                <tool.icon className="w-5 h-5" />
                <span className="font-medium">{tool.title}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Active Tool */}
      <section className="px-4 sm:px-6 lg:px-8 pb-12">
        <div className="max-w-6xl mx-auto">
          <motion.div
            key={activeTool}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {activeTool === "cdc" && <CDCVisualization />}
            {activeTool === "pipeline" && <PipelineDesigner />}
            {activeTool === "calculator" && <ResourceCalculator />}
            {(activeTool === "analysis") && (
              <div className="bg-card rounded-2xl border border-border p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-10 h-10 rounded-lg bg-amber-400/10 flex items-center justify-center">
                    <Activity className="w-5 h-5 text-amber-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold">Timing Analysis Tools</h3>
                    <p className="text-sm text-muted-foreground">Advanced timing analysis and constraint management</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-6 bg-muted/30 rounded-xl">
                    <h4 className="font-medium mb-4">Static Timing Analysis</h4>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Critical Path</span>
                        <span className="font-mono text-primary">12.5ns</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Setup Slack</span>
                        <span className="font-mono text-green-400">+2.3ns</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Hold Slack</span>
                        <span className="font-mono text-green-400">+0.8ns</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Max Frequency</span>
                        <span className="font-mono text-amber-400">80 MHz</span>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 bg-muted/30 rounded-xl">
                    <h4 className="font-medium mb-4">Timing Constraints</h4>
                    <div className="code-block text-xs">
                      <div className="code-content">
                        <div><span className="text-muted-foreground"># Clock definition</span></div>
                        <div>create_clock -period 12.5 -name clk</div>
                        <br />
                        <div><span className="text-muted-foreground"># Input delay</span></div>
                        <div>set_input_delay 2.0 -clock clk [all_inputs]</div>
                        <br />
                        <div><span className="text-muted-foreground"># Output delay</span></div>
                        <div>set_output_delay 1.5 -clock clk [all_outputs]</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </section>

      {/* Quick Actions */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-2xl font-bold mb-4">Additional Resources</h2>
            <p className="text-muted-foreground">Documentation and tools for hardware design</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="bg-card rounded-2xl border border-border p-6 card-hover group"
            >
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                <Download className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">Download Tools</h3>
              <p className="text-muted-foreground text-sm mb-4">
                Get offline versions of our timing analysis tools for your projects.
              </p>
              <Link
                href="#"
                className="flex items-center gap-2 text-primary text-sm font-medium group-hover:gap-3 transition-all"
              >
                Download Now <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="bg-card rounded-2xl border border-border p-6 card-hover group"
            >
              <div className="w-12 h-12 rounded-xl bg-blue-400/10 flex items-center justify-center mb-4">
                <ExternalLink className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="font-semibold mb-2">Documentation</h3>
              <p className="text-muted-foreground text-sm mb-4">
                Comprehensive guides on FPGA timing analysis and CDC techniques.
              </p>
              <Link
                href="/learning"
                className="flex items-center gap-2 text-blue-400 text-sm font-medium group-hover:gap-3 transition-all"
              >
                View Docs <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="bg-card rounded-2xl border border-border p-6 card-hover group"
            >
              <div className="w-12 h-12 rounded-xl bg-amber-400/10 flex items-center justify-center mb-4">
                <Settings className="w-6 h-6 text-amber-400" />
              </div>
              <h3 className="font-semibold mb-2">API Access</h3>
              <p className="text-muted-foreground text-sm mb-4">
                Integrate timing analysis tools into your own design automation flows.
              </p>
              <Link
                href="/about"
                className="flex items-center gap-2 text-amber-400 text-sm font-medium group-hover:gap-3 transition-all"
              >
                Learn More <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>
          </div>
        </div>
      </section>
    </div>
  );
}
