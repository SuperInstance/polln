// ============================================================================
// LLN PLAYGROUND - MYCELIUM AGENT NETWORK
// Cooperative Intelligence & Competition Dynamics
// ============================================================================

import { motion } from "framer-motion";
import {
  Network,
  Zap,
  Target,
  ArrowRight,
  CircleDot,
  Brain,
  TreeDeciduous,
  Bot,
  MessageCircle,
  AlertTriangle,
  Heart,
  TrendingUp,
  Activity,
  Shield,
  Sparkles,
  Layers,
  GitBranch,
} from "lucide-react";

// ============================================================================
// MYCELIUM NETWORK TYPES
// ============================================================================

type SignalType = 
  | "pest-warning"      // Adversarial attack detected
  | "resource-share"    // Knowledge/energy distribution
  | "competition-alert" // Market/opportunity awareness
  | "cooperation-invite" // Partnership request
  | "stress-signal"     // Performance degradation
  | "growth-boost"      // Positive reinforcement
  | "death-signal";     // Agent retirement/replacement

interface MyceliumNode {
  id: string;
  type: "tree" | "fungi" | "agent";
  name: string;
  health: number;        // 0-1
  resources: number;     // Energy/knowledge tokens
  connections: string[];
  signalsSent: number;
  signalsReceived: number;
  position: { x: number; y: number };
}

interface MyceliumSignal {
  id: string;
  type: SignalType;
  source: string;
  targets: string[];
  payload: string;
  strength: number;      // 0-1 signal strength
  timestamp: number;
  decay: number;         // Signal decay rate
}

interface CompetitionEvent {
  id: string;
  type: "canopy-gap" | "resource-scarcity" | "pest-invasion" | "fire-reset";
  participants: string[];
  winner?: string;
  description: string;
  learningOutcomes: string[];
  timestamp: number;
}

interface CooperationEvent {
  id: string;
  type: "resource-pooling" | "defense-coordination" | "knowledge-sharing" | "joint-decision";
  participants: string[];
  benefit: number;
  description: string;
  synergyScore: number;
  timestamp: number;
}

// ============================================================================
// MYCELIUM NETWORK SIMULATION
// ============================================================================

export class MyceliumNetworkSimulation {
  private nodes: Map<string, MyceliumNode>;
  private signals: MyceliumSignal[];
  private competitionEvents: CompetitionEvent[];
  private cooperationEvents: CooperationEvent[];

  constructor() {
    this.nodes = new Map();
    this.signals = [];
    this.competitionEvents = [];
    this.cooperationEvents = [];
    this.initializeNetwork();
  }

  private initializeNetwork() {
    // Create initial network of trees and fungi
    const treeCount = 12;
    const fungiCount = 5;

    for (let i = 0; i < treeCount; i++) {
      const angle = (i / treeCount) * Math.PI * 2;
      const radius = 0.3 + Math.random() * 0.15;
      this.addNode({
        id: `tree-${i}`,
        type: "tree",
        name: `Tree ${i + 1}`,
        health: 0.7 + Math.random() * 0.3,
        resources: 50 + Math.random() * 50,
        connections: [],
        signalsSent: 0,
        signalsReceived: 0,
        position: {
          x: 0.5 + Math.cos(angle) * radius,
          y: 0.5 + Math.sin(angle) * radius
        }
      });
    }

    // Fungi nodes connect trees
    for (let i = 0; i < fungiCount; i++) {
      this.addNode({
        id: `fungi-${i}`,
        type: "fungi",
        name: `Mycelium Hub ${i + 1}`,
        health: 1,
        resources: 100,
        connections: [],
        signalsSent: 0,
        signalsReceived: 0,
        position: {
          x: 0.3 + Math.random() * 0.4,
          y: 0.3 + Math.random() * 0.4
        }
      });
    }

    // Establish connections
    this.establishConnections();
  }

  private addNode(node: MyceliumNode) {
    this.nodes.set(node.id, node);
  }

  private establishConnections() {
    const nodes = Array.from(this.nodes.values());
    const fungi = nodes.filter(n => n.type === "fungi");
    const trees = nodes.filter(n => n.type === "tree");

    // Each tree connects to nearest fungi
    trees.forEach(tree => {
      const nearestFungi = fungi.sort((a, b) => 
        this.distance(tree.position, a.position) - 
        this.distance(tree.position, b.position)
      ).slice(0, 2);

      nearestFungi.forEach(f => {
        tree.connections.push(f.id);
        f.connections.push(tree.id);
      });
    });

    // Trees also connect to nearby trees
    trees.forEach(tree => {
      const nearbyTrees = trees
        .filter(t => t.id !== tree.id)
        .filter(t => this.distance(tree.position, t.position) < 0.2)
        .slice(0, 3);

      nearbyTrees.forEach(t => {
        if (!tree.connections.includes(t.id)) {
          tree.connections.push(t.id);
        }
      });
    });
  }

  private distance(a: { x: number; y: number }, b: { x: number; y: number }): number {
    return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2);
  }

  // Simulate signal propagation
  broadcastSignal(signal: MyceliumSignal) {
    const source = this.nodes.get(signal.source);
    if (!source) return;

    signal.targets.forEach(targetId => {
      const target = this.nodes.get(targetId);
      if (target) {
        target.signalsReceived++;
        this.processSignal(target, signal);
      }
    });

    source.signalsSent++;
    this.signals.push(signal);
  }

  private processSignal(node: MyceliumNode, signal: MyceliumSignal) {
    switch (signal.type) {
      case "pest-warning":
        // Strengthen defenses
        node.health = Math.min(1, node.health + 0.05);
        break;
      case "resource-share":
        // Accept resources if needed
        if (node.resources < 30) {
          node.resources += signal.strength * 20;
        }
        break;
      case "cooperation-invite":
        // Form cooperation event
        this.cooperationEvents.push({
          id: `coop-${Date.now()}`,
          type: "joint-decision",
          participants: [signal.source, node.id],
          benefit: signal.strength * 10,
          description: `Cooperation between ${signal.source} and ${node.id}`,
          synergyScore: signal.strength,
          timestamp: Date.now()
        });
        break;
    }
  }

  // Simulate competition for canopy gap
  simulateCanopyGap(gapPosition: { x: number; y: number }) {
    const nearbyTrees = Array.from(this.nodes.values())
      .filter(n => n.type === "tree")
      .filter(n => this.distance(n.position, gapPosition) < 0.3)
      .sort((a, b) => b.health - a.health);

    if (nearbyTrees.length < 2) return;

    const participants = nearbyTrees.slice(0, 3);
    const winner = participants[0];

    // Winner grows toward gap
    winner.resources += 30;

    this.competitionEvents.push({
      id: `comp-${Date.now()}`,
      type: "canopy-gap",
      participants: participants.map(t => t.id),
      winner: winner.id,
      description: `Competition for canopy gap at ${gapPosition.x.toFixed(2)}, ${gapPosition.y.toFixed(2)}`,
      learningOutcomes: [
        `${winner.id} won by having highest health (${(winner.health * 100).toFixed(0)}%)`,
        `Losers learned to strengthen before competition`
      ],
      timestamp: Date.now()
    });

    return { winner, participants };
  }

  // Get network statistics
  getStats() {
    const nodes = Array.from(this.nodes.values());
    const trees = nodes.filter(n => n.type === "tree");
    const fungi = nodes.filter(n => n.type === "fungi");

    return {
      totalNodes: nodes.length,
      trees: trees.length,
      fungiNodes: fungi.length,
      averageHealth: trees.reduce((sum, t) => sum + t.health, 0) / trees.length,
      totalConnections: nodes.reduce((sum, n) => sum + n.connections.length, 0) / 2,
      totalSignals: this.signals.length,
      competitionEvents: this.competitionEvents.length,
      cooperationEvents: this.cooperationEvents.length,
      signalsByType: this.countSignalsByType()
    };
  }

  private countSignalsByType(): Record<SignalType, number> {
    const counts: Record<string, number> = {};
    this.signals.forEach(s => {
      counts[s.type] = (counts[s.type] || 0) + 1;
    });
    return counts as Record<SignalType, number>;
  }
}

// ============================================================================
// MYCELIUM NETWORK COMPONENT
// ============================================================================

interface MyceliumNetworkProps {
  simulation: MyceliumNetworkSimulation;
}

export function MyceliumNetwork({ simulation }: MyceliumNetworkProps) {
  const stats = simulation.getStats();

  return (
    <div className="space-y-6">
      {/* Network Overview */}
      <div className="bg-gradient-to-br from-purple-900/30 via-slate-800/50 to-emerald-900/30 rounded-2xl p-6 border border-purple-500/30">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
              <TreeDeciduous className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Mycelium Agent Network</h3>
              <p className="text-sm text-purple-300">Cooperative Intelligence & Competition Dynamics</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-purple-400">{stats.totalNodes}</div>
            <div className="text-xs text-slate-500">Network Nodes</div>
          </div>
        </div>

        {/* Network Stats Grid */}
        <div className="grid grid-cols-4 gap-4">
          <div className="p-4 bg-emerald-500/10 rounded-xl border border-emerald-500/30 text-center">
            <TreeDeciduous className="w-6 h-6 text-emerald-400 mx-auto mb-1" />
            <div className="text-xl font-bold text-white">{stats.trees}</div>
            <div className="text-xs text-slate-500">Agent Trees</div>
          </div>
          <div className="p-4 bg-purple-500/10 rounded-xl border border-purple-500/30 text-center">
            <TreeDeciduous className="w-6 h-6 text-purple-400 mx-auto mb-1" />
            <div className="text-xl font-bold text-white">{stats.fungiNodes}</div>
            <div className="text-xs text-slate-500">Hub Nodes</div>
          </div>
          <div className="p-4 bg-cyan-500/10 rounded-xl border border-cyan-500/30 text-center">
            <Network className="w-6 h-6 text-cyan-400 mx-auto mb-1" />
            <div className="text-xl font-bold text-white">{stats.totalConnections}</div>
            <div className="text-xs text-slate-500">Connections</div>
          </div>
          <div className="p-4 bg-amber-500/10 rounded-xl border border-amber-500/30 text-center">
            <Activity className="w-6 h-6 text-amber-400 mx-auto mb-1" />
            <div className="text-xl font-bold text-white">{(stats.averageHealth * 100).toFixed(0)}%</div>
            <div className="text-xs text-slate-500">Avg Health</div>
          </div>
        </div>
      </div>

      {/* Signal Types */}
      <SignalTypesDisplay />

      {/* Competition & Cooperation */}
      <div className="grid grid-cols-2 gap-6">
        <CompetitionDisplay events={[]} />
        <CooperationDisplay events={[]} />
      </div>

      {/* Network Visualization */}
      <NetworkVisualization />
    </div>
  );
}

function SignalTypesDisplay() {
  const signalTypes: { type: SignalType; icon: string; color: string; description: string }[] = [
    { type: "pest-warning", icon: "🐛", color: "red", description: "Adversarial attack detected" },
    { type: "resource-share", icon: "💧", color: "cyan", description: "Knowledge/energy distribution" },
    { type: "competition-alert", icon: "⚔️", color: "amber", description: "Market/opportunity awareness" },
    { type: "cooperation-invite", icon: "🤝", color: "emerald", description: "Partnership request" },
    { type: "stress-signal", icon: "⚠️", color: "orange", description: "Performance degradation" },
    { type: "growth-boost", icon: "🌱", color: "green", description: "Positive reinforcement" },
    { type: "death-signal", icon: "💀", color: "slate", description: "Agent retirement/replacement" }
  ];

  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
      <div className="flex items-center gap-2 mb-4">
        <MessageCircle className="w-5 h-5 text-cyan-400" />
        <h3 className="text-lg font-semibold text-white">Signal Types</h3>
      </div>

      <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
        {signalTypes.map(({ type, icon, color, description }) => (
          <motion.div
            key={type}
            className={`p-3 bg-${color}-500/10 rounded-xl border border-${color}-500/30`}
            whileHover={{ scale: 1.02 }}
          >
            <div className="text-2xl mb-1">{icon}</div>
            <div className="text-white text-sm font-medium capitalize">{type.replace("-", " ")}</div>
            <div className="text-xs text-slate-500 mt-1">{description}</div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function CompetitionDisplay({ events }: { events: CompetitionEvent[] }) {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-amber-500/30">
      <div className="flex items-center gap-2 mb-4">
        <Target className="w-5 h-5 text-amber-400" />
        <h3 className="text-lg font-semibold text-white">Competition Events</h3>
      </div>

      <div className="space-y-3">
        <div className="p-4 bg-slate-900/50 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">🌳</span>
            <span className="text-amber-400 font-medium">Canopy Gap Competition</span>
          </div>
          <p className="text-sm text-slate-400 mb-3">
            When an old tree falls, adolescent trees compete for the light. One wins and is shaped by the competition.
          </p>
          <div className="flex items-center gap-4">
            <div className="text-xs text-emerald-400">
              Winner: Strongest health (85%+)
            </div>
            <div className="text-xs text-slate-500">
              Learning: Strengthen before competition
            </div>
          </div>
        </div>

        <div className="p-4 bg-slate-900/50 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">🔥</span>
            <span className="text-amber-400 font-medium">Fire Reset Event</span>
          </div>
          <p className="text-sm text-slate-400 mb-3">
            Catastrophic reset clears the board. Some seeds require fire to germinate. Destruction enables rebirth.
          </p>
          <div className="text-xs text-slate-500">
            Learning: Resilience through redundancy, distributed knowledge
          </div>
        </div>
      </div>

      <div className="mt-4 p-3 bg-amber-500/10 rounded-lg">
        <div className="text-xs text-amber-400 font-medium mb-1">Competition Principle</div>
        <p className="text-xs text-slate-400">
          "Life is competition. Trees fight for light. The winner is shaped by the struggle, 
          not despite it. In AI systems, agents compete for resources, attention, and decision authority."
        </p>
      </div>
    </div>
  );
}

function CooperationDisplay({ events }: { events: CooperationEvent[] }) {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-emerald-500/30">
      <div className="flex items-center gap-2 mb-4">
        <Heart className="w-5 h-5 text-emerald-400" />
        <h3 className="text-lg font-semibold text-white">Cooperation Events</h3>
      </div>

      <div className="space-y-3">
        <div className="p-4 bg-slate-900/50 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">🍄</span>
            <span className="text-emerald-400 font-medium">Mycelium Resource Sharing</span>
          </div>
          <p className="text-sm text-slate-400 mb-3">
            Trees warn each other of invading pests through mycelium networks. Others thicken their leaves in response.
          </p>
          <div className="flex items-center gap-4">
            <div className="text-xs text-purple-400">
              Hub: Fungi network nodes
            </div>
            <div className="text-xs text-slate-500">
              Benefit: Distributed early warning
            </div>
          </div>
        </div>

        <div className="p-4 bg-slate-900/50 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-2xl">🤝</span>
            <span className="text-emerald-400 font-medium">Joint Decision Making</span>
          </div>
          <p className="text-sm text-slate-400 mb-3">
            Multiple agents pool confidence and knowledge for better decisions than any single agent could make.
          </p>
          <div className="text-xs text-slate-500">
            Synergy: Combined confidence &gt; sum of parts
          </div>
        </div>
      </div>

      <div className="mt-4 p-3 bg-emerald-500/10 rounded-lg">
        <div className="text-xs text-emerald-400 font-medium mb-1">Cooperation Principle</div>
        <p className="text-xs text-slate-400">
          "Life is cooperation. Mycelium connects trees into a network of mutual aid. 
          In AI systems, agents share knowledge, warn of adversarial attacks, and pool resources for complex decisions."
        </p>
      </div>
    </div>
  );
}

function NetworkVisualization() {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-purple-500/30">
      <div className="flex items-center gap-2 mb-4">
        <Network className="w-5 h-5 text-purple-400" />
        <h3 className="text-lg font-semibold text-white">Network Visualization</h3>
      </div>

      <div className="relative h-80 bg-slate-900/50 rounded-xl overflow-hidden">
        {/* Trees in circle */}
        {Array.from({ length: 12 }).map((_, i) => {
          const angle = (i / 12) * Math.PI * 2;
          const radius = 35;
          const x = 50 + Math.cos(angle) * radius;
          const y = 50 + Math.sin(angle) * radius;
          return (
            <motion.div
              key={i}
              className="absolute text-2xl cursor-pointer"
              style={{ left: `${x}%`, top: `${y}%`, transform: "translate(-50%, -50%)" }}
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: i * 0.1 }}
            >
              🌳
            </motion.div>
          );
        })}

        {/* Fungi hubs */}
        {[
          { x: 30, y: 30 },
          { x: 70, y: 30 },
          { x: 50, y: 50 },
          { x: 30, y: 70 },
          { x: 70, y: 70 }
        ].map((pos, i) => (
          <motion.div
            key={i}
            className="absolute text-xl"
            style={{ left: `${pos.x}%`, top: `${pos.y}%`, transform: "translate(-50%, -50%)" }}
          >
            🍄
          </motion.div>
        ))}

        {/* Mycelium connections */}
        <svg className="absolute inset-0 w-full h-full opacity-50">
          {/* Draw connections between trees and fungi */}
          {Array.from({ length: 20 }).map((_, i) => {
            const angle = (i / 20) * Math.PI * 2;
            const x1 = 50 + Math.cos(angle) * 35;
            const y1 = 50 + Math.sin(angle) * 35;
            const hubIndex = Math.floor(i / 4);
            const hubs = [
              { x: 30, y: 30 },
              { x: 70, y: 30 },
              { x: 50, y: 50 },
              { x: 30, y: 70 },
              { x: 70, y: 70 }
            ];
            const hub = hubs[hubIndex % 5];
            return (
              <motion.line
                key={i}
                x1={`${x1}%`}
                y1={`${y1}%`}
                x2={`${hub.x}%`}
                y2={`${hub.y}%`}
                stroke="rgba(147, 51, 234, 0.3)"
                strokeWidth="1"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 2, delay: i * 0.05, repeat: Infinity }}
              />
            );
          })}
        </svg>

        {/* Signals */}
        <motion.div
          className="absolute px-2 py-1 rounded-full bg-red-500/20 text-red-300 text-xs border border-red-500/30"
          style={{ left: "35%", top: "40%" }}
          animate={{ x: [0, 30, 0], opacity: [0, 1, 0] }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          🐛 Pest warning!
        </motion.div>

        <motion.div
          className="absolute px-2 py-1 rounded-full bg-cyan-500/20 text-cyan-300 text-xs border border-cyan-500/30"
          style={{ left: "55%", top: "60%" }}
          animate={{ x: [0, -30, 0], opacity: [0, 1, 0] }}
          transition={{ duration: 3, delay: 1, repeat: Infinity }}
        >
          💧 Resource share
        </motion.div>

        <motion.div
          className="absolute px-2 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs border border-emerald-500/30"
          style={{ left: "45%", top: "35%" }}
          animate={{ scale: [1, 1.2, 1], opacity: [0, 1, 0] }}
          transition={{ duration: 3, delay: 2, repeat: Infinity }}
        >
          🤝 Cooperation invite
        </motion.div>
      </div>
    </div>
  );
}

// ============================================================================
// LIFE PRINCIPLES DISPLAY
// ============================================================================

export function LifePrinciplesDisplay() {
  return (
    <div className="bg-gradient-to-br from-emerald-900/30 via-purple-900/20 to-amber-900/30 rounded-2xl p-6 border border-emerald-500/30">
      <div className="flex items-center gap-2 mb-6">
        <Sparkles className="w-5 h-5 text-amber-400" />
        <h3 className="text-lg font-semibold text-white">Life Principles for AI Systems</h3>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Competition Principles */}
        <div className="space-y-4">
          <h4 className="text-amber-400 font-medium flex items-center gap-2">
            <Target className="w-4 h-4" />
            Competition
          </h4>
          <div className="space-y-3">
            <div className="p-3 bg-slate-900/50 rounded-lg">
              <div className="text-white text-sm mb-1">Canopy Gap Dynamics</div>
              <p className="text-xs text-slate-400">
                When one fails, others compete for the space. The winner is shaped 
                by the competition, not despite it.
              </p>
            </div>
            <div className="p-3 bg-slate-900/50 rounded-lg">
              <div className="text-white text-sm mb-1">Light Competition</div>
              <p className="text-xs text-slate-400">
                Trees grow toward light. The tallest get the most. Those that 
                don't compete adapt to shade or die.
              </p>
            </div>
            <div className="p-3 bg-slate-900/50 rounded-lg">
              <div className="text-white text-sm mb-1">Resource Scarcity</div>
              <p className="text-xs text-slate-400">
                Limited water, nutrients, space create competition. Efficient 
                resource use wins.
              </p>
            </div>
          </div>
        </div>

        {/* Cooperation Principles */}
        <div className="space-y-4">
          <h4 className="text-emerald-400 font-medium flex items-center gap-2">
            <Heart className="w-4 h-4" />
            Cooperation
          </h4>
          <div className="space-y-3">
            <div className="p-3 bg-slate-900/50 rounded-lg">
              <div className="text-white text-sm mb-1">Mycelium Network</div>
              <p className="text-xs text-slate-400">
                Underground fungal networks connect trees. They share resources, 
                warn of threats, enable mutual aid.
              </p>
            </div>
            <div className="p-3 bg-slate-900/50 rounded-lg">
              <div className="text-white text-sm mb-1">Pest Warning System</div>
              <p className="text-xs text-slate-400">
                When one tree is attacked, it signals others through the network. 
                Neighbors strengthen defenses before attack arrives.
              </p>
            </div>
            <div className="p-3 bg-slate-900/50 rounded-lg">
              <div className="text-white text-sm mb-1">Resource Redistribution</div>
              <p className="text-xs text-slate-400">
                Trees with excess resources share with those in need through 
                mycelium. The forest is stronger together.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Synthesis Principle */}
      <div className="mt-6 p-4 bg-gradient-to-r from-amber-500/10 via-purple-500/10 to-emerald-500/10 rounded-xl border border-purple-500/30">
        <div className="text-center">
          <div className="text-white font-medium mb-2">The Synthesis Principle</div>
          <p className="text-slate-300 text-sm max-w-2xl mx-auto">
            "Life is competition AND cooperation. Trees fight for light while sharing 
            resources through mycelium. In AI systems, agents compete for decision 
            authority while sharing knowledge through networks. The balance creates 
            resilient, adaptive intelligence."
          </p>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  MyceliumNetwork,
  MyceliumNetworkSimulation,
  LifePrinciplesDisplay
};
