"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Cpu, Layers, Box, Zap, ArrowRight, ChevronRight,
  Thermometer, Gauge, Ruler, Power, Activity, Fan,
  Play, Pause, RotateCcw, Download, Share2, Lock, Unlock,
  Check, AlertTriangle, Info, Eye, Settings, Maximize2
} from "lucide-react";

// PCIe specifications
const pcieSpecs = [
  { gen: "Gen 3", bandwidth: "8 GT/s", x1: "1 GB/s", x4: "4 GB/s", x8: "8 GB/s", x16: "16 GB/s" },
  { gen: "Gen 4", bandwidth: "16 GT/s", x1: "2 GB/s", x4: "8 GB/s", x8: "16 GB/s", x16: "32 GB/s" },
  { gen: "Gen 5", bandwidth: "32 GT/s", x1: "4 GB/s", x4: "16 GB/s", x8: "32 GB/s", x16: "64 GB/s" },
];

// Form factor options
const formFactors = [
  { id: "hhhl", name: "Half-Height Half-Length", width: 167.65, height: 68.90, power: 75, desc: "Low profile server" },
  { id: "fhfl", name: "Full-Height Full-Length", width: 312, height: 111.15, power: 300, desc: "Full-size workstation" },
  { id: "ocu", name: "OCuLink", width: 58, height: 45, power: 25, desc: "Compact external" },
];

// Power budget calculator
function PowerBudgetCalculator() {
  const [aiPower, setAiPower] = useState(15);
  const [memoryPower, setMemoryPower] = useState(8);
  const [ioPower, setIoPower] = useState(5);
  const [thermal, setThermal] = useState("passive");

  const totalPower = aiPower + memoryPower + ioPower;
  const maxSlot = 75;
  const needsExternal = totalPower > maxSlot;

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Power className="w-5 h-5 text-amber-400" />
          <span className="font-semibold">Power Budget Calculator</span>
        </div>
      </div>

      <div className="p-6">
        {/* Power Bars */}
        <div className="space-y-4 mb-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">AI Core</span>
              <span className="text-sm font-mono text-green-400">{aiPower}W</span>
            </div>
            <input
              type="range"
              min="5"
              max="50"
              value={aiPower}
              onChange={(e) => setAiPower(parseInt(e.target.value))}
              className="w-full accent-green-500"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Memory</span>
              <span className="text-sm font-mono text-blue-400">{memoryPower}W</span>
            </div>
            <input
              type="range"
              min="2"
              max="30"
              value={memoryPower}
              onChange={(e) => setMemoryPower(parseInt(e.target.value))}
              className="w-full accent-blue-500"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">I/O & Control</span>
              <span className="text-sm font-mono text-purple-400">{ioPower}W</span>
            </div>
            <input
              type="range"
              min="2"
              max="20"
              value={ioPower}
              onChange={(e) => setIoPower(parseInt(e.target.value))}
              className="w-full accent-purple-500"
            />
          </div>
        </div>

        {/* Total Power Display */}
        <div className="bg-dark-700/50 rounded-xl p-4 mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Total Power</span>
            <span className={`text-2xl font-bold font-mono ${needsExternal ? "text-amber-400" : "text-green-400"}`}>
              {totalPower}W
            </span>
          </div>

          {/* Visual Power Bar */}
          <div className="h-4 bg-dark-600 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                needsExternal ? "bg-gradient-to-r from-green-500 via-amber-500 to-red-500" : "bg-green-500"
              }`}
              style={{ width: `${Math.min(100, (totalPower / 300) * 100)}%` }}
            />
            <div
              className="h-full bg-dark-600"
              style={{ marginLeft: `${(maxSlot / 300) * 100}%`, width: 2 }}
            />
          </div>

          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>0W</span>
            <span className="text-amber-400">Slot: 75W</span>
            <span>300W</span>
          </div>
        </div>

        {/* Power Source Recommendation */}
        <div className={`p-4 rounded-xl ${needsExternal ? "bg-amber-500/10 border border-amber-500/30" : "bg-green-500/10 border border-green-500/30"}`}>
          <div className="flex items-center gap-2 mb-2">
            {needsExternal ? <AlertTriangle className="w-4 h-4 text-amber-400" /> : <Check className="w-4 h-4 text-green-400" />}
            <span className={`font-medium ${needsExternal ? "text-amber-400" : "text-green-400"}`}>
              {needsExternal ? "External Power Required" : "Slot Power Sufficient"}
            </span>
          </div>
          <p className="text-sm text-gray-400">
            {needsExternal
              ? `Your design needs ${totalPower - maxSlot}W additional power via 6-pin or 8-pin connector.`
              : "Your design can draw all power from the PCIe slot."}
          </p>
        </div>

        {/* Thermal Selection */}
        <div className="mt-4">
          <span className="text-sm text-gray-400 mb-2 block">Thermal Solution</span>
          <div className="flex gap-3">
            <button
              onClick={() => setThermal("passive")}
              className={`flex-1 p-3 rounded-xl text-sm transition-all ${
                thermal === "passive"
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "bg-dark-700/50 text-gray-400 border border-dark-600"
              }`}
            >
              <Fan className="w-4 h-4 mx-auto mb-1" />
              Passive
            </button>
            <button
              onClick={() => setThermal("active")}
              className={`flex-1 p-3 rounded-xl text-sm transition-all ${
                thermal === "active"
                  ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                  : "bg-dark-700/50 text-gray-400 border border-dark-600"
              }`}
            >
              <Activity className="w-4 h-4 mx-auto mb-1" />
              Active Fan
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// PCIe Lane Visualizer
function LaneVisualizer() {
  const [lanes, setLanes] = useState(4);
  const [gen, setGen] = useState(4);

  const bandwidth = lanes * Math.pow(2, gen - 3);

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Activity className="w-5 h-5 text-blue-400" />
          <span className="font-semibold">PCIe Lane Configuration</span>
        </div>
      </div>

      <div className="p-6">
        {/* Lane Selector */}
        <div className="mb-6">
          <span className="text-sm text-gray-400 mb-3 block">Lane Count</span>
          <div className="flex gap-2">
            {[1, 2, 4, 8, 16].map((lane) => (
              <button
                key={lane}
                onClick={() => setLanes(lane)}
                className={`flex-1 py-3 rounded-xl font-mono text-lg transition-all ${
                  lanes === lane
                    ? "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                    : "bg-dark-700/50 text-gray-400 border border-dark-600 hover:border-dark-500"
                }`}
              >
                ×{lane}
              </button>
            ))}
          </div>
        </div>

        {/* Lane Visualization */}
        <div className="mb-6">
          <div className="flex gap-1 justify-center mb-4">
            {Array.from({ length: lanes }).map((_, i) => (
              <div
                key={i}
                className="w-2 h-16 rounded-full bg-blue-500 animate-pulse"
                style={{ animationDelay: `${i * 100}ms` }}
              />
            ))}
          </div>
          <p className="text-center text-sm text-gray-500">
            {lanes} lane{lanes > 1 ? 's' : ''} active
          </p>
        </div>

        {/* Generation Selector */}
        <div className="mb-6">
          <span className="text-sm text-gray-400 mb-3 block">PCIe Generation</span>
          <div className="flex gap-2">
            {[3, 4, 5].map((g) => (
              <button
                key={g}
                onClick={() => setGen(g)}
                className={`flex-1 py-3 rounded-xl transition-all ${
                  gen === g
                    ? "bg-green-500/20 text-green-400 border border-green-500/30"
                    : "bg-dark-700/50 text-gray-400 border border-dark-600 hover:border-dark-500"
                }`}
              >
                Gen {g}
              </button>
            ))}
          </div>
        </div>

        {/* Bandwidth Display */}
        <div className="bg-dark-700/50 rounded-xl p-4 text-center">
          <span className="text-sm text-gray-400">Maximum Bandwidth</span>
          <div className="text-3xl font-bold font-mono text-green-400 mt-1">
            {bandwidth} GB/s
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Sufficient for {bandwidth >= 16 ? "high-throughput" : bandwidth >= 8 ? "medium" : "light"} AI workloads
          </p>
        </div>
      </div>
    </div>
  );
}

// Thermal Simulator
function ThermalSimulator() {
  const [power, setPower] = useState(25);
  const [ambientTemp, setAmbientTemp] = useState(25);
  const [heatsinkSize, setHeatsinkSize] = useState("medium");

  const heatsinkThermal = { small: 0.8, medium: 0.5, large: 0.3 };
  const chipTemp = ambientTemp + power * heatsinkThermal[heatsinkSize as keyof typeof heatsinkThermal];
  const isSafe = chipTemp < 85;
  const isWarning = chipTemp >= 70 && chipTemp < 85;

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Thermometer className="w-5 h-5 text-red-400" />
          <span className="font-semibold">Thermal Simulator</span>
        </div>
      </div>

      <div className="p-6">
        {/* Temperature Gauge */}
        <div className="mb-6">
          <div className="flex items-center justify-center mb-4">
            <div className="relative w-32 h-32">
              <svg viewBox="0 0 100 100" className="w-full h-full">
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#2d2d3d"
                  strokeWidth="8"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke={isSafe ? "#22c55e" : isWarning ? "#f59e0b" : "#ef4444"}
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={`${(chipTemp / 120) * 283} 283`}
                  transform="rotate(-90 50 50)"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center flex-col">
                <span className={`text-2xl font-bold font-mono ${isSafe ? "text-green-400" : isWarning ? "text-amber-400" : "text-red-400"}`}>
                  {Math.round(chipTemp)}°C
                </span>
                <span className="text-xs text-gray-500">Chip Temp</span>
              </div>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="space-y-4">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm text-gray-400">Power Dissipation</span>
              <span className="text-sm font-mono text-amber-400">{power}W</span>
            </div>
            <input
              type="range"
              min="5"
              max="75"
              value={power}
              onChange={(e) => setPower(parseInt(e.target.value))}
              className="w-full accent-amber-500"
            />
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm text-gray-400">Ambient Temperature</span>
              <span className="text-sm font-mono text-blue-400">{ambientTemp}°C</span>
            </div>
            <input
              type="range"
              min="15"
              max="45"
              value={ambientTemp}
              onChange={(e) => setAmbientTemp(parseInt(e.target.value))}
              className="w-full accent-blue-500"
            />
          </div>

          <div>
            <span className="text-sm text-gray-400 mb-2 block">Heatsink Size</span>
            <div className="flex gap-2">
              {["small", "medium", "large"].map((size) => (
                <button
                  key={size}
                  onClick={() => setHeatsinkSize(size)}
                  className={`flex-1 py-2 rounded-lg text-sm capitalize transition-all ${
                    heatsinkSize === size
                      ? "bg-green-500/20 text-green-400 border border-green-500/30"
                      : "bg-dark-700/50 text-gray-400 border border-dark-600"
                  }`}
                >
                  {size}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Status */}
        <div className={`mt-4 p-3 rounded-xl ${isSafe ? "bg-green-500/10 border border-green-500/30" : isWarning ? "bg-amber-500/10 border border-amber-500/30" : "bg-red-500/10 border border-red-500/30"}`}>
          <div className="flex items-center gap-2">
            {isSafe ? <Check className="w-4 h-4 text-green-400" /> : isWarning ? <AlertTriangle className="w-4 h-4 text-amber-400" /> : <AlertTriangle className="w-4 h-4 text-red-400" />}
            <span className={`text-sm ${isSafe ? "text-green-400" : isWarning ? "text-amber-400" : "text-red-400"}`}>
              {isSafe ? "Thermal design OK" : isWarning ? "Approaching thermal limit" : "Thermal throttling likely"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

// 3D Card Visualizer
function CardVisualizer() {
  const [rotation, setRotation] = useState(0);
  const [formFactor, setFormFactor] = useState("fhfl");

  useEffect(() => {
    const interval = setInterval(() => {
      setRotation((prev) => (prev + 0.5) % 360);
    }, 50);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Box className="w-5 h-5 text-purple-400" />
            <span className="font-semibold">3D Card Preview</span>
          </div>
          <div className="flex gap-2">
            <button className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors">
              <RotateCcw className="w-4 h-4" />
            </button>
            <button className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors">
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Form Factor Selector */}
        <div className="flex gap-2 mb-6">
          {formFactors.map((ff) => (
            <button
              key={ff.id}
              onClick={() => setFormFactor(ff.id)}
              className={`flex-1 py-2 rounded-lg text-sm transition-all ${
                formFactor === ff.id
                  ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                  : "bg-dark-700/50 text-gray-400 border border-dark-600"
              }`}
            >
              {ff.name}
            </button>
          ))}
        </div>

        {/* 3D Card Representation */}
        <div className="relative h-64 mb-6" style={{ perspective: 1000 }}>
          <div
            className="absolute inset-0 flex items-center justify-center"
            style={{
              transform: `rotateY(${rotation}deg)`,
              transformStyle: "preserve-3d",
            }}
          >
            {/* Card body */}
            <div
              className="relative bg-gradient-to-br from-dark-600 to-dark-700 rounded-xl border border-dark-500"
              style={{
                width: formFactor === "fhfl" ? 200 : 120,
                height: formFactor === "fhfl" ? 80 : 55,
                boxShadow: "0 20px 40px rgba(0,0,0,0.4)",
              }}
            >
              {/* Chip */}
              <div className="absolute top-1/2 left-1/3 -translate-y-1/2 w-12 h-12 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-green-500/30">
                <Cpu className="w-6 h-6 text-white" />
              </div>

              {/* Memory */}
              <div className="absolute top-2 right-4 w-6 h-6 rounded bg-purple-500/30" />
              <div className="absolute bottom-2 right-4 w-6 h-6 rounded bg-purple-500/30" />
              <div className="absolute top-2 right-12 w-6 h-6 rounded bg-purple-500/30" />
              <div className="absolute bottom-2 right-12 w-6 h-6 rounded bg-purple-500/30" />

              {/* PCIe Connector */}
              <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-16 h-4 bg-amber-600/50 rounded-t" />

              {/* Power Connector */}
              {formFactor === "fhfl" && (
                <div className="absolute top-0 right-4 w-8 h-3 bg-red-500/50 rounded-b" />
              )}
            </div>
          </div>
        </div>

        {/* Dimensions */}
        <div className="grid grid-cols-2 gap-4 text-center">
          <div className="bg-dark-700/50 rounded-xl p-3">
            <div className="text-lg font-mono text-green-400">
              {formFactors.find(f => f.id === formFactor)?.width}mm
            </div>
            <div className="text-xs text-gray-500">Length</div>
          </div>
          <div className="bg-dark-700/50 rounded-xl p-3">
            <div className="text-lg font-mono text-blue-400">
              {formFactors.find(f => f.id === formFactor)?.height}mm
            </div>
            <div className="text-xs text-gray-500">Height</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function PCIeExplorerPage() {
  return (
    <div className="animated-bg min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/ternaryair/tutorials"
            className="flex items-center gap-2 text-gray-400 hover:text-white text-sm mb-4"
          >
            <ChevronRight className="w-4 h-4 rotate-180" />
            Back to Tutorials
          </Link>

          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold">PCIe AI Accelerator Card</h1>
              <p className="text-sm text-gray-500">Interactive design explorer</p>
            </div>
          </div>

          <p className="text-lg text-gray-300 max-w-3xl">
            Design a desktop AI accelerator card. Configure power, lanes, thermal solution, 
            and form factor. Export a complete specification ready for manufacturing.
          </p>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PowerBudgetCalculator />
          <LaneVisualizer />
          <ThermalSimulator />
          <CardVisualizer />
        </div>

        {/* Export Section */}
        <div className="mt-8 bg-dark-800/60 rounded-2xl p-6 border border-dark-600">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <Download className="w-5 h-5 text-green-400" />
              Export Design Specification
            </h3>
            <Link
              href="/ternaryair/manufacturing"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm transition-colors"
            >
              Continue to Manufacturing <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-300 text-sm border border-dark-500">
              <Download className="w-4 h-4" />
              PDF Spec Sheet
            </button>
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-300 text-sm border border-dark-500">
              <Download className="w-4 h-4" />
              JSON Config
            </button>
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-300 text-sm border border-dark-500">
              <Share2 className="w-4 h-4" />
              Share Design
            </button>
          </div>
        </div>

        {/* PCIe Reference Table */}
        <div className="mt-8 bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
          <div className="p-4 border-b border-dark-600 bg-dark-700/50">
            <span className="font-semibold">PCIe Bandwidth Reference</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-dark-700/50">
                <tr>
                  <th className="px-4 py-3 text-left text-gray-400">Generation</th>
                  <th className="px-4 py-3 text-left text-gray-400">Transfer Rate</th>
                  <th className="px-4 py-3 text-center text-gray-400">×1</th>
                  <th className="px-4 py-3 text-center text-gray-400">×4</th>
                  <th className="px-4 py-3 text-center text-gray-400">×8</th>
                  <th className="px-4 py-3 text-center text-gray-400">×16</th>
                </tr>
              </thead>
              <tbody>
                {pcieSpecs.map((spec) => (
                  <tr key={spec.gen} className="border-t border-dark-600">
                    <td className="px-4 py-3 text-green-400 font-medium">{spec.gen}</td>
                    <td className="px-4 py-3 text-gray-300">{spec.bandwidth}</td>
                    <td className="px-4 py-3 text-center font-mono text-gray-400">{spec.x1}</td>
                    <td className="px-4 py-3 text-center font-mono text-gray-400">{spec.x4}</td>
                    <td className="px-4 py-3 text-center font-mono text-gray-400">{spec.x8}</td>
                    <td className="px-4 py-3 text-center font-mono text-gray-400">{spec.x16}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
