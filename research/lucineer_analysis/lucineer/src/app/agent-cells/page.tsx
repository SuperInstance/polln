"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import { motion } from "framer-motion";
import Head from "next/head";
import Link from "next/link";
import {
  Brain,
  Bot,
  Zap,
  Layers,
  Grid3X3,
  Table,
  Play,
  Pause,
  Swords,
  Heart,
  Shuffle,
  Lightbulb,
  Eye,
  Repeat,
  Radio,
} from "lucide-react";

// ============================================================================
// AGENT CELL SYSTEM - HIERARCHICAL REAL-TIME AI ARCHITECTURE
// ============================================================================

type CellRole = "sensor" | "bot" | "agent" | "tile" | "orchestrator" | "model" | "reflex" | "habit" | "deliberate";
type ConfidenceLevel = "green" | "yellow" | "red";
type ExecutionMode = "bot" | "agent" | "model";

interface AgentCell {
  id: string;
  name: string;
  role: CellRole;
  mode: ExecutionMode;
  confidence: number;
  confidenceLevel: ConfidenceLevel;
  isActive: boolean;
  lastUpdate: number;
  inputs: string[];
  outputs: string[];
  inferenceCount: number;
  botCycles: number;
  agentCycles: number;
  deadband: number;
  threshold: number;
  parent?: string;
  children: string[];
  monitoredValue?: number;
  simulatedPath?: number;
  deviation?: number;
}

interface Tile {
  id: string;
  name: string;
  conditions: { parameter: string; operator: string; value: number | string | [number, number] }[];
  script: string;
  confidence: number;
  usageCount: number;
  successRate: number;
}

// Confidence Gauge Component
function ConfidenceGauge({ confidence, level, size = "md" }: { confidence: number; level: ConfidenceLevel; size?: "sm" | "md" | "lg" }) {
  const sizeMap = { sm: { width: 60, height: 40 }, md: { width: 100, height: 60 }, lg: { width: 150, height: 90 } };
  const colorMap = {
    green: { bg: "bg-green-500/20", fill: "#22c55e", text: "text-green-400" },
    yellow: { bg: "bg-amber-500/20", fill: "#f59e0b", text: "text-amber-400" },
    red: { bg: "bg-red-500/20", fill: "#ef4444", text: "text-red-400" },
  };
  const colors = colorMap[level];
  const { width, height } = sizeMap[size];
  const radius = width / 2 - 10;
  const circumference = Math.PI * radius;
  const progress = (confidence / 100) * circumference;

  return (
    <div className={`relative inline-flex items-center justify-center ${colors.bg} rounded-lg`}>
      <svg width={width} height={height / 2 + 10} className="overflow-visible">
        <path d={`M 10 ${height / 2} A ${radius} ${radius} 0 0 1 ${width - 10} ${height / 2}`} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth={size === "sm" ? 4 : 6} strokeLinecap="round" />
        <motion.path d={`M 10 ${height / 2} A ${radius} ${radius} 0 0 1 ${width - 10} ${height / 2}`} fill="none" stroke={colors.fill} strokeWidth={size === "sm" ? 4 : 6} strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={circumference - progress} initial={{ strokeDashoffset: circumference }} animate={{ strokeDashoffset: circumference - progress }} transition={{ duration: 0.5 }} />
      </svg>
      <div className={`absolute bottom-0 font-mono font-bold ${colors.text}`} style={{ fontSize: size === "sm" ? "10px" : "12px" }}>{confidence.toFixed(0)}%</div>
    </div>
  );
}

// Agent Cell Card Component
function AgentCellCard({ cell, onSelect, isSelected }: { cell: AgentCell; onSelect: () => void; isSelected: boolean }) {
  const getRoleIcon = (role: CellRole) => {
    const icons: Record<CellRole, typeof Bot> = { sensor: Eye, bot: Zap, agent: Bot, tile: Grid3X3, orchestrator: Layers, model: Brain, reflex: Radio, habit: Repeat, deliberate: Brain };
    const Icon = icons[role] || Bot;
    return <Icon className="w-4 h-4" />;
  };

  const getModeColor = (mode: ExecutionMode) => ({
    bot: "text-amber-400 bg-amber-500/10 border-amber-500/30",
    agent: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
    model: "text-purple-400 bg-purple-500/10 border-purple-500/30",
  }[mode]);

  return (
    <motion.div layout onClick={onSelect} className={`relative cursor-pointer rounded-xl border p-3 transition-all ${isSelected ? "border-primary bg-primary/5 ring-2 ring-primary/20" : "border-border bg-card hover:border-primary/30"}`} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
      {cell.isActive && <motion.div className="absolute inset-0 rounded-xl bg-primary/20" animate={{ opacity: [0, 0.5, 0] }} transition={{ duration: 1, repeat: Infinity }} />}
      <div className="relative flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div className={`p-1.5 rounded-lg ${getModeColor(cell.mode)}`}>{getRoleIcon(cell.role)}</div>
          <div>
            <h4 className="font-medium text-sm">{cell.name}</h4>
            <p className="text-xs text-muted-foreground">{cell.role}</p>
          </div>
        </div>
        <ConfidenceGauge confidence={cell.confidence} level={cell.confidenceLevel} size="sm" />
      </div>
      <div className="mt-2 flex items-center gap-3 text-xs text-muted-foreground">
        <span className={`px-1.5 py-0.5 rounded ${getModeColor(cell.mode)}`}>{cell.mode}</span>
        <span>Inferences: {cell.inferenceCount}</span>
        <span>Cycles: {cell.botCycles + cell.agentCycles}</span>
      </div>
    </motion.div>
  );
}

// TTRPG Battle Tracker Component
function TTRPGTracker() {
  const [initiative, setInitiative] = useState([
    { id: "1", name: "Hero", initiative: 18, hp: 45, maxHp: 50, type: "player" },
    { id: "2", name: "Dragon", initiative: 15, hp: 120, maxHp: 150, type: "enemy" },
    { id: "3", name: "Wizard", initiative: 12, hp: 30, maxHp: 35, type: "player" },
  ]);
  const [currentTurn, setCurrentTurn] = useState(0);
  const [combatLog, setCombatLog] = useState<string[]>(["Combat started!", "Hero rolls initiative: 18"]);

  const nextTurn = () => {
    setCurrentTurn((prev) => (prev + 1) % initiative.length);
    setCombatLog((prev) => [...prev.slice(-9), `${initiative[currentTurn].name}'s turn begins...`]);
  };

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <div className="p-3 bg-muted/30 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Swords className="w-4 h-4 text-red-400" />
          <span className="font-semibold">Combat Tracker</span>
        </div>
        <button onClick={nextTurn} className="px-3 py-1 bg-primary/10 text-primary rounded text-sm font-medium hover:bg-primary/20">Next Turn</button>
      </div>
      <div className="p-3">
        <div className="mb-4">
          <h4 className="text-xs text-muted-foreground mb-2">Initiative Order</h4>
          <div className="space-y-1">
            {initiative.sort((a, b) => b.initiative - a.initiative).map((char, i) => (
              <div key={char.id} className={`flex items-center justify-between p-2 rounded ${i === currentTurn ? "bg-primary/10 border border-primary/30" : "bg-muted/20"}`}>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono w-6">{char.initiative}</span>
                  <span className={char.type === "enemy" ? "text-red-400" : "text-green-400"}>{char.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Heart className={`w-3 h-3 ${char.hp < char.maxHp * 0.3 ? "text-red-500" : "text-green-500"}`} />
                  <span className="text-xs font-mono">{char.hp}/{char.maxHp}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h4 className="text-xs text-muted-foreground mb-2">Combat Log</h4>
          <div className="bg-black/20 rounded p-2 h-20 overflow-y-auto">
            {combatLog.map((log, i) => <div key={i} className="text-xs text-muted-foreground mb-1">{log}</div>)}
          </div>
        </div>
      </div>
    </div>
  );
}

// Main Page Component
export default function AgentCellsPage() {
  const initialCells = useMemo(() => {
    const cells = new Map<string, AgentCell>();
    cells.set("model-1", { id: "model-1", name: "Frontal Cortex", role: "model", mode: "model", confidence: 95, confidenceLevel: "green", isActive: false, lastUpdate: Date.now(), inputs: [], outputs: [], inferenceCount: 0, botCycles: 0, agentCycles: 0, deadband: 5, threshold: 20, children: ["orchestrator-1"] });
    cells.set("orchestrator-1", { id: "orchestrator-1", name: "Movement Controller", role: "orchestrator", mode: "agent", confidence: 88, confidenceLevel: "green", isActive: true, lastUpdate: Date.now(), inputs: [], outputs: [], inferenceCount: 3, botCycles: 100, agentCycles: 15, deadband: 10, threshold: 25, parent: "model-1", children: ["habit-walk"] });
    cells.set("habit-walk", { id: "habit-walk", name: "Walking Pattern", role: "habit", mode: "bot", confidence: 92, confidenceLevel: "green", isActive: true, lastUpdate: Date.now(), inputs: [], outputs: [], inferenceCount: 0, botCycles: 1000, agentCycles: 0, deadband: 15, threshold: 30, parent: "orchestrator-1", children: [] });
    cells.set("sensor-foot", { id: "sensor-foot", name: "Foot Sensor", role: "sensor", mode: "bot", confidence: 99, confidenceLevel: "green", isActive: true, lastUpdate: Date.now(), inputs: [], outputs: [], inferenceCount: 0, botCycles: 2000, agentCycles: 0, deadband: 5, threshold: 10, children: [] });
    return cells;
  }, []);

  const [cells, setCells] = useState<Map<string, AgentCell>>(initialCells);
  const [selectedCellId, setSelectedCellId] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [showTTRPG, setShowTTRPG] = useState(false);

  const selectedCell = selectedCellId ? cells.get(selectedCellId) : null;

  useEffect(() => {
    if (!isRunning) return;
    const interval = setInterval(() => {
      setCells((prev) => {
        const newCells = new Map(prev);
        newCells.forEach((cell, id) => {
          if (cell.role !== "sensor" && cell.role !== "model") {
            const newConfidence = Math.max(0, Math.min(100, cell.confidence + (Math.random() - 0.5) * 2));
            const level: ConfidenceLevel = newConfidence < 50 ? "red" : newConfidence < 80 ? "yellow" : "green";
            newCells.set(id, { ...cell, confidence: newConfidence, confidenceLevel: level, botCycles: cell.mode === "bot" ? cell.botCycles + 1 : cell.botCycles, agentCycles: cell.mode === "agent" ? cell.agentCycles + 1 : cell.agentCycles, lastUpdate: Date.now() });
          }
        });
        return newCells;
      });
    }, 500);
    return () => clearInterval(interval);
  }, [isRunning]);

  const tiles: Tile[] = [
    { id: "tile-1", name: "Normal Walk", conditions: [{ parameter: "terrain", operator: "eq", value: "flat" }], script: "repeat(walk_cycle, speed=normal)", confidence: 95, usageCount: 1000, successRate: 98 },
    { id: "tile-2", name: "Stumble Recovery", conditions: [{ parameter: "foot_contact", operator: "eq", value: "lost" }], script: "arm_balance() + core_stabilize()", confidence: 92, usageCount: 50, successRate: 88 },
  ];

  return (
    <>
      <Head>
        <title>Agent Cells | Lucineer - Hierarchical Real-Time AI</title>
        <meta name="description" content="Hierarchical agent cell system with confidence-based autonomy. Bots, agents, and models working together with tile-based logic shortcuts." />
      </Head>
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-purple-500/5">
        <section className="py-8 px-4 sm:px-6 lg:px-8 border-b border-border">
          <div className="max-w-7xl mx-auto">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/30 rounded-full px-4 py-2 mb-4">
                  <Layers className="w-4 h-4 text-purple-400" />
                  <span className="text-purple-400 text-sm font-medium">Hierarchical Agent Architecture</span>
                </div>
                <h1 className="text-4xl sm:text-5xl font-bold mb-2">
                  <span className="bg-gradient-to-r from-purple-400 via-cyan-400 to-emerald-400 bg-clip-text text-transparent">Agent Cell System</span>
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl">Real-time AI through hierarchical confidence. Lower-level cells with high confidence handle autonomously—higher models only engaged when needed.</p>
              </div>
              <div className="flex gap-3">
                <button onClick={() => setIsRunning(!isRunning)} className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${isRunning ? "bg-amber-500/20 text-amber-400" : "bg-emerald-500 text-white"}`}>{isRunning ? <><Pause className="w-4 h-4" />Pause</> : <><Play className="w-4 h-4" />Start</>}</button>
                <button onClick={() => setShowTTRPG(!showTTRPG)} className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${showTTRPG ? "bg-purple-500/20 text-purple-400" : "bg-muted"}`}><Swords className="w-4 h-4" />TTRPG Mode</button>
              </div>
            </motion.div>
          </div>
        </section>

        <section className="py-6 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between"><h2 className="font-semibold">Agent Cells</h2><span className="text-sm text-muted-foreground">{cells.size} cells</span></div>
                <div className="space-y-2">
                  {Array.from(cells.values()).sort((a, b) => (["model", "orchestrator", "deliberate", "agent", "habit", "tile", "reflex", "sensor"].indexOf(a.role) - ["model", "orchestrator", "deliberate", "agent", "habit", "tile", "reflex", "sensor"].indexOf(b.role))).map((cell) => (
                    <AgentCellCard key={cell.id} cell={cell} onSelect={() => setSelectedCellId(cell.id)} isSelected={selectedCellId === cell.id} />
                  ))}
                </div>
              </div>

              <div className="space-y-6">
                <div className="relative h-64 bg-black/20 rounded-xl overflow-hidden">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center text-muted-foreground">
                      <Layers className="w-12 h-12 mx-auto mb-2 opacity-30" />
                      <p className="text-sm">Hierarchy Visualization</p>
                    </div>
                  </div>
                </div>

                {selectedCell && (
                  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-card border border-border rounded-xl p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold">{selectedCell.name}</h3>
                      <ConfidenceGauge confidence={selectedCell.confidence} level={selectedCell.confidenceLevel} size="md" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-3 bg-muted/20 rounded-lg"><div className="text-xs text-muted-foreground mb-1">Role</div><div className="font-medium capitalize">{selectedCell.role}</div></div>
                      <div className="p-3 bg-muted/20 rounded-lg"><div className="text-xs text-muted-foreground mb-1">Mode</div><div className={`font-medium capitalize ${selectedCell.mode === "bot" ? "text-amber-400" : selectedCell.mode === "agent" ? "text-cyan-400" : "text-purple-400"}`}>{selectedCell.mode}</div></div>
                    </div>
                    <div className="mt-4 p-3 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 rounded-lg border border-cyan-500/20">
                      <div className="flex items-center gap-2 mb-2"><Lightbulb className="w-4 h-4 text-cyan-400" /><span className="text-sm font-medium text-cyan-400">Key Insight</span></div>
                      <p className="text-sm text-muted-foreground">{selectedCell.mode === "bot" ? "This cell runs without inference—a pure loop. High confidence means no model calls needed." : selectedCell.mode === "agent" ? "This cell uses a small model for inference when confidence drops below threshold." : "This cell uses the full model for complex reasoning when lower cells can't handle the situation."}</p>
                    </div>
                  </motion.div>
                )}

                {showTTRPG && <TTRPGTracker />}
              </div>

              <div className="space-y-6">
                <div className="bg-card border border-border rounded-xl p-4">
                  <h3 className="font-semibold mb-3 flex items-center gap-2"><Grid3X3 className="w-4 h-4 text-emerald-400" />Tile Library</h3>
                  <p className="text-sm text-muted-foreground mb-3">Pre-computed scripts for common situations. Logic flows from the hand dealt, not probabilities.</p>
                  <div className="space-y-2">
                    {tiles.map((tile) => (
                      <div key={tile.id} className="p-3 bg-muted/20 rounded-lg cursor-pointer hover:bg-muted/30">
                        <div className="flex items-center justify-between mb-1"><span className="font-medium text-sm">{tile.name}</span><span className="text-xs text-green-400">{tile.successRate}% success</span></div>
                        <code className="text-xs bg-black/20 p-1 rounded block">{tile.script}</code>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-gradient-to-br from-amber-500/10 to-red-500/10 rounded-xl border border-amber-500/20 p-4">
                  <h3 className="font-semibold mb-3 flex items-center gap-2"><Brain className="w-4 h-4 text-amber-400" />Origin-Centric Math</h3>
                  <p className="text-sm text-muted-foreground mb-3">Attention focuses on change from simulated path, not global state. When reality deviates beyond deadband, higher systems engage.</p>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-green-500" /><span>Green: Autonomous</span></div>
                    <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-amber-500" /><span>Yellow: Monitoring</span></div>
                    <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-red-500" /><span>Red: Escalation</span></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 bg-gradient-to-r from-purple-500/10 via-cyan-500/10 to-emerald-500/10 rounded-2xl border border-purple-500/20 p-8">
              <h2 className="text-2xl font-bold mb-4">How Hierarchical Cells Create Real-Time AI</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center mb-3"><Zap className="w-6 h-6 text-amber-400" /></div>
                  <h3 className="font-semibold mb-2">Bots (No Inference)</h3>
                  <p className="text-sm text-muted-foreground">Simple loops without model calls. Walking, breathing, reflexes—all happen without thinking. High confidence means no escalation.</p>
                </div>
                <div>
                  <div className="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center mb-3"><Bot className="w-6 h-6 text-cyan-400" /></div>
                  <h3 className="font-semibold mb-2">Agents (With Inference)</h3>
                  <p className="text-sm text-muted-foreground">When confidence drops, agents engage small models to fine-tune responses. They monitor deviation and adapt scripts.</p>
                </div>
                <div>
                  <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-3"><Brain className="w-6 h-6 text-purple-400" /></div>
                  <h3 className="font-semibold mb-2">Models (Full Inference)</h3>
                  <p className="text-sm text-muted-foreground">The large frontal cortex model only engages when lower systems can't handle the situation. Fallback for novel scenarios.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
              <h2 className="text-3xl font-bold mb-4">The Universe on a Spreadsheet</h2>
              <p className="text-lg text-muted-foreground mb-8">Every cell can be an agent, every formula a computation. Watch intelligence unfold as confidence flows through the system.</p>
              <div className="flex flex-wrap justify-center gap-4">
                <Link href="/cell-builder" className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-90"><Table className="w-5 h-5" />Cell-Based Builder</Link>
                <Link href="/tile-intelligence" className="flex items-center gap-2 px-6 py-3 bg-card border border-border rounded-xl font-medium hover:border-primary/50"><Grid3X3 className="w-5 h-5" />Tile Intelligence</Link>
              </div>
            </motion.div>
          </div>
        </section>
      </div>
    </>
  );
}
