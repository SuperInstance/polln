"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Cpu, Layers, Box, Zap, ArrowRight, ChevronRight,
  Thermometer, Gauge, Power, Activity, Wifi, Battery,
  Play, Pause, RotateCcw, Download, Share2, Settings,
  Check, AlertTriangle, Info, Sun, Droplets, Wind,
  Radio, Satellite, Camera, Mic, Watch, Smartphone
} from "lucide-react";

// Edge deployment scenarios
const deploymentScenarios = [
  {
    id: "drone",
    name: "Autonomous Drone",
    icon: "🚁",
    power: "Battery 15W",
    environment: "Outdoor",
    constraints: ["Weight <50g", "Low power", "Vibration"],
    tempRange: [-20, 50],
    humidity: [0, 100],
  },
  {
    id: "marine",
    name: "Marine Sensor",
    icon: "🌊",
    power: "Solar + Battery 5W",
    environment: "Underwater",
    constraints: ["IP68", "Corrosion resistant", "Long battery"],
    tempRange: [-5, 35],
    humidity: [95, 100],
  },
  {
    id: "factory",
    name: "Factory Robot",
    icon: "🤖",
    power: "24V DC 25W",
    environment: "Industrial",
    constraints: ["EMI shielding", "Dust sealed", "Real-time"],
    tempRange: [0, 60],
    humidity: [10, 90],
  },
  {
    id: "agriculture",
    name: "Agricultural IoT",
    icon: "🌾",
    power: "Solar 10W",
    environment: "Outdoor Field",
    constraints: ["Weatherproof", "LoRa connectivity", "Seasonal"],
    tempRange: [-30, 55],
    humidity: [0, 100],
  },
  {
    id: "medical",
    name: "Medical Wearable",
    icon: "⌚",
    power: "Battery 2W",
    environment: "Body-worn",
    constraints: ["Skin safe", "FDA Class II", "All-day comfort"],
    tempRange: [20, 40],
    humidity: [30, 90],
  },
  {
    id: "space",
    name: "Satellite Payload",
    icon: "🛰️",
    power: "Solar 20W",
    environment: "Space",
    constraints: ["Radiation hardened", "Vacuum rated", "No service"],
    tempRange: [-40, 85],
    humidity: [0, 0],
  },
];

// Sensor inputs
const sensorTypes = [
  { id: "camera", name: "Camera", icon: Camera, power: 2, bandwidth: 400 },
  { id: "mic", name: "Microphone Array", icon: Mic, power: 0.5, bandwidth: 10 },
  { id: "imu", name: "IMU (Accel/Gyro)", icon: Activity, power: 0.1, bandwidth: 1 },
  { id: "gps", name: "GPS Module", icon: Satellite, power: 0.3, bandwidth: 0.1 },
  { id: "env", name: "Environmental", icon: Thermometer, power: 0.05, bandwidth: 0.01 },
  { id: "radio", name: "Radio/SDR", icon: Radio, power: 1.5, bandwidth: 50 },
];

// AI workloads
const aiWorkloads = [
  { id: "object", name: "Object Detection", tokens: 50, latency: 20, power: 3 },
  { id: "speech", name: "Speech Recognition", tokens: 100, latency: 100, power: 2 },
  { id: "nlp", name: "NLP/Chat", tokens: 200, latency: 500, power: 4 },
  { id: "anomaly", name: "Anomaly Detection", tokens: 30, latency: 10, power: 1.5 },
  { id: "slam", name: "SLAM/Navigation", tokens: 80, latency: 30, power: 5 },
  { id: "predict", name: "Predictive Model", tokens: 40, latency: 15, power: 2 },
];

// Power Source Simulator
function PowerSimulator() {
  const [source, setSource] = useState("battery");
  const [capacity, setCapacity] = useState(5000);
  const [solarPower, setSolarPower] = useState(10);
  const [consumption, setConsumption] = useState(5);
  const [dutyCycle, setDutyCycle] = useState(20);

  const batteryLife = source === "battery" 
    ? (capacity * dutyCycle / 100 / consumption).toFixed(1)
    : "∞";
  
  const solarNet = source === "solar" 
    ? solarPower - consumption * dutyCycle / 100 
    : 0;

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Battery className="w-5 h-5 text-green-400" />
          <span className="font-semibold">Power Source Simulator</span>
        </div>
      </div>

      <div className="p-6">
        {/* Source Selection */}
        <div className="grid grid-cols-3 gap-2 mb-6">
          {[
            { id: "battery", label: "Battery", icon: Battery },
            { id: "solar", label: "Solar + Battery", icon: Sun },
            { id: "wired", label: "Wired Power", icon: Power },
          ].map((s) => (
            <button
              key={s.id}
              onClick={() => setSource(s.id)}
              className={`p-3 rounded-xl text-sm transition-all ${
                source === s.id
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "bg-dark-700/50 text-gray-400 border border-dark-600"
              }`}
            >
              <s.icon className="w-5 h-5 mx-auto mb-1" />
              {s.label}
            </button>
          ))}
        </div>

        {/* Battery Settings */}
        {source === "battery" && (
          <div className="space-y-4 mb-6">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-400">Battery Capacity</span>
                <span className="text-sm font-mono text-amber-400">{capacity} mAh</span>
              </div>
              <input
                type="range"
                min="500"
                max="20000"
                step="500"
                value={capacity}
                onChange={(e) => setCapacity(parseInt(e.target.value))}
                className="w-full accent-amber-500"
              />
            </div>
          </div>
        )}

        {/* Solar Settings */}
        {source === "solar" && (
          <div className="space-y-4 mb-6">
            <div>
              <div className="flex justify-between mb-2">
                <span className="text-sm text-gray-400">Solar Panel Output</span>
                <span className="text-sm font-mono text-yellow-400">{solarPower}W</span>
              </div>
              <input
                type="range"
                min="1"
                max="50"
                value={solarPower}
                onChange={(e) => setSolarPower(parseInt(e.target.value))}
                className="w-full accent-yellow-500"
              />
            </div>

            <div className={`p-3 rounded-xl ${solarNet >= 0 ? "bg-green-500/10 border border-green-500/30" : "bg-red-500/10 border border-red-500/30"}`}>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Net Power</span>
                <span className={`font-mono ${solarNet >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {solarNet >= 0 ? "+" : ""}{solarNet.toFixed(1)}W
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Consumption Settings */}
        <div className="space-y-4">
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm text-gray-400">Active Consumption</span>
              <span className="text-sm font-mono text-red-400">{consumption}W</span>
            </div>
            <input
              type="range"
              min="1"
              max="25"
              value={consumption}
              onChange={(e) => setConsumption(parseInt(e.target.value))}
              className="w-full accent-red-500"
            />
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <span className="text-sm text-gray-400">Duty Cycle</span>
              <span className="text-sm font-mono text-blue-400">{dutyCycle}%</span>
            </div>
            <input
              type="range"
              min="1"
              max="100"
              value={dutyCycle}
              onChange={(e) => setDutyCycle(parseInt(e.target.value))}
              className="w-full accent-blue-500"
            />
          </div>
        </div>

        {/* Result */}
        <div className="mt-6 bg-dark-700/50 rounded-xl p-4 text-center">
          <span className="text-sm text-gray-400">Estimated Runtime</span>
          <div className="text-3xl font-bold font-mono text-green-400 mt-1">
            {batteryLife} {source !== "wired" ? "hours" : "(unlimited)"}
          </div>
        </div>
      </div>
    </div>
  );
}

// Environment Simulator
function EnvironmentSimulator() {
  const [temperature, setTemperature] = useState(25);
  const [humidity, setHumidity] = useState(50);
  const [vibration, setVibration] = useState(false);
  const [salt, setSalt] = useState(false);
  const [radiation, setRadiation] = useState(false);

  const getRating = () => {
    let rating = 10;
    if (temperature < -10 || temperature > 50) rating -= 2;
    if (temperature < -20 || temperature > 60) rating -= 2;
    if (humidity > 80) rating -= 1;
    if (humidity > 95) rating -= 1;
    if (vibration) rating -= 1;
    if (salt) rating -= 1;
    if (radiation) rating -= 3;
    return Math.max(1, rating);
  };

  const rating = getRating();

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Thermometer className="w-5 h-5 text-red-400" />
          <span className="font-semibold">Environment Simulator</span>
        </div>
      </div>

      <div className="p-6">
        {/* Temperature */}
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            <span className="text-sm text-gray-400">Operating Temperature</span>
            <span className="text-sm font-mono text-amber-400">{temperature}°C</span>
          </div>
          <input
            type="range"
            min="-40"
            max="85"
            value={temperature}
            onChange={(e) => setTemperature(parseInt(e.target.value))}
            className="w-full accent-amber-500"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>-40°C</span>
            <span className="text-green-400">0-50°C typical</span>
            <span>85°C</span>
          </div>
        </div>

        {/* Humidity */}
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            <span className="text-sm text-gray-400">Relative Humidity</span>
            <span className="text-sm font-mono text-blue-400">{humidity}%</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={humidity}
            onChange={(e) => setHumidity(parseInt(e.target.value))}
            className="w-full accent-blue-500"
          />
        </div>

        {/* Environmental Hazards */}
        <div className="space-y-3 mb-6">
          {[
            { id: "vibration", label: "Vibration/Shock", icon: Activity, state: vibration, setState: setVibration },
            { id: "salt", label: "Salt/Corrosion", icon: Droplets, state: salt, setState: setSalt },
            { id: "radiation", label: "Ionizing Radiation", icon: Radio, state: radiation, setState: setRadiation },
          ].map((hazard) => (
            <button
              key={hazard.id}
              onClick={() => hazard.setState(!hazard.state)}
              className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all ${
                hazard.state
                  ? "bg-red-500/10 text-red-400 border border-red-500/30"
                  : "bg-dark-700/50 text-gray-400 border border-dark-600"
              }`}
            >
              <hazard.icon className="w-5 h-5" />
              <span className="flex-1 text-left text-sm">{hazard.label}</span>
              {hazard.state && <AlertTriangle className="w-4 h-4" />}
            </button>
          ))}
        </div>

        {/* Rating */}
        <div className="bg-dark-700/50 rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Enclosure Rating Required</span>
            <span className={`text-2xl font-bold ${
              rating >= 8 ? "text-green-400" : rating >= 5 ? "text-amber-400" : "text-red-400"
            }`}>
              IP{rating >= 8 ? "68" : rating >= 6 ? "67" : rating >= 4 ? "65" : "54"}
            </span>
          </div>
          <div className="h-2 bg-dark-600 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                rating >= 8 ? "bg-green-500" : rating >= 5 ? "bg-amber-500" : "bg-red-500"
              }`}
              style={{ width: `${rating * 10}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

// Sensor Selector
function SensorSelector() {
  const [selectedSensors, setSelectedSensors] = useState<string[]>(["camera", "imu"]);

  const toggleSensor = (id: string) => {
    setSelectedSensors((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const totalPower = selectedSensors.reduce((sum, id) => {
    const sensor = sensorTypes.find((s) => s.id === id);
    return sum + (sensor?.power || 0);
  }, 0);

  const totalBandwidth = selectedSensors.reduce((sum, id) => {
    const sensor = sensorTypes.find((s) => s.id === id);
    return sum + (sensor?.bandwidth || 0);
  }, 0);

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Camera className="w-5 h-5 text-purple-400" />
          <span className="font-semibold">Sensor Configuration</span>
        </div>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-2 gap-3 mb-6">
          {sensorTypes.map((sensor) => {
            const isSelected = selectedSensors.includes(sensor.id);
            return (
              <button
                key={sensor.id}
                onClick={() => toggleSensor(sensor.id)}
                className={`p-3 rounded-xl text-sm transition-all ${
                  isSelected
                    ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                    : "bg-dark-700/50 text-gray-400 border border-dark-600"
                }`}
              >
                <sensor.icon className="w-5 h-5 mx-auto mb-1" />
                <div className="font-medium">{sensor.name}</div>
                <div className="text-xs text-gray-500 mt-1">{sensor.power}W</div>
              </button>
            );
          })}
        </div>

        {/* Totals */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-dark-700/50 rounded-xl p-3 text-center">
            <div className="text-xl font-mono text-amber-400">{totalPower.toFixed(1)}W</div>
            <div className="text-xs text-gray-500">Sensor Power</div>
          </div>
          <div className="bg-dark-700/50 rounded-xl p-3 text-center">
            <div className="text-xl font-mono text-blue-400">{totalBandwidth}MB/s</div>
            <div className="text-xs text-gray-500">Data Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// AI Workload Selector
function AIWorkloadSelector() {
  const [selectedWorkloads, setSelectedWorkloads] = useState<string[]>(["object"]);
  const [inferenceRate, setInferenceRate] = useState(10);

  const toggleWorkload = (id: string) => {
    setSelectedWorkloads((prev) =>
      prev.includes(id) ? prev.filter((w) => w !== id) : [...prev, id]
    );
  };

  const avgPower = selectedWorkloads.reduce((sum, id) => {
    const workload = aiWorkloads.find((w) => w.id === id);
    return sum + (workload?.power || 0);
  }, 0) / selectedWorkloads.length || 0;

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Cpu className="w-5 h-5 text-green-400" />
          <span className="font-semibold">AI Workload Configuration</span>
        </div>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-2 gap-3 mb-6">
          {aiWorkloads.map((workload) => {
            const isSelected = selectedWorkloads.includes(workload.id);
            return (
              <button
                key={workload.id}
                onClick={() => toggleWorkload(workload.id)}
                className={`p-3 rounded-xl text-sm transition-all ${
                  isSelected
                    ? "bg-green-500/20 text-green-400 border border-green-500/30"
                    : "bg-dark-700/50 text-gray-400 border border-dark-600"
                }`}
              >
                <div className="font-medium">{workload.name}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {workload.latency}ms latency
                </div>
              </button>
            );
          })}
        </div>

        {/* Inference Rate */}
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            <span className="text-sm text-gray-400">Inferences per Second</span>
            <span className="text-sm font-mono text-green-400">{inferenceRate}</span>
          </div>
          <input
            type="range"
            min="1"
            max="60"
            value={inferenceRate}
            onChange={(e) => setInferenceRate(parseInt(e.target.value))}
            className="w-full accent-green-500"
          />
        </div>

        {/* Results */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-dark-700/50 rounded-xl p-3 text-center">
            <div className="text-xl font-mono text-green-400">{(avgPower * inferenceRate / 10).toFixed(1)}W</div>
            <div className="text-xs text-gray-500">AI Power</div>
          </div>
          <div className="bg-dark-700/50 rounded-xl p-3 text-center">
            <div className="text-xl font-mono text-purple-400">{inferenceRate * 60}</div>
            <div className="text-xs text-gray-500">Inferences/min</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Deployment Scenario Cards
function DeploymentSelector({ selected, onSelect }: { selected: string; onSelect: (id: string) => void }) {
  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Box className="w-5 h-5 text-cyan-400" />
          <span className="font-semibold">Deployment Scenario</span>
        </div>
      </div>

      <div className="p-4">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {deploymentScenarios.map((scenario) => (
            <button
              key={scenario.id}
              onClick={() => onSelect(scenario.id)}
              className={`p-4 rounded-xl text-left transition-all ${
                selected === scenario.id
                  ? "bg-cyan-500/20 text-white border border-cyan-500/30"
                  : "bg-dark-700/50 text-gray-400 border border-dark-600 hover:border-dark-500"
              }`}
            >
              <div className="text-2xl mb-2">{scenario.icon}</div>
              <div className="font-medium text-sm">{scenario.name}</div>
              <div className="text-xs text-gray-500 mt-1">{scenario.power}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function EdgeSimulatorPage() {
  const [deployment, setDeployment] = useState("drone");

  const scenario = deploymentScenarios.find((s) => s.id === deployment);

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
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold">Edge Device Simulator</h1>
              <p className="text-sm text-gray-500">Design AI-powered edge devices</p>
            </div>
          </div>

          <p className="text-lg text-gray-300 max-w-3xl">
            Configure sensors, AI workloads, power sources, and environmental constraints. 
            Validate your design against real-world conditions before manufacturing.
          </p>
        </div>

        {/* Deployment Selector */}
        <div className="mb-6">
          <DeploymentSelector selected={deployment} onSelect={setDeployment} />
        </div>

        {/* Scenario Info */}
        {scenario && (
          <div className="mb-6 bg-cyan-500/10 border border-cyan-500/30 rounded-xl p-4">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-2xl">{scenario.icon}</span>
              <div>
                <h3 className="font-semibold">{scenario.name}</h3>
                <p className="text-sm text-gray-400">{scenario.environment} environment</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              {scenario.constraints.map((c) => (
                <span key={c} className="px-2 py-1 rounded-full bg-dark-700/50 text-xs text-gray-400">
                  {c}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PowerSimulator />
          <EnvironmentSimulator />
          <SensorSelector />
          <AIWorkloadSelector />
        </div>

        {/* Export Section */}
        <div className="mt-8 bg-dark-800/60 rounded-2xl p-6 border border-dark-600">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <Download className="w-5 h-5 text-green-400" />
              Export Edge Device Specification
            </h3>
            <Link
              href="/ternaryair/manufacturing"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm transition-colors"
            >
              Continue to Manufacturing <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <p className="text-sm text-gray-400 mb-4">
            Your edge device configuration includes all sensors, AI workloads, power requirements, 
            and environmental specifications needed for manufacturing review.
          </p>

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
      </div>
    </div>
  );
}
