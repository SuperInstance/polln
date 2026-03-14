"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Atom, Network, GitMerge, Plus, Minus, Clock, Activity, 
  Cpu, Zap, Database, RefreshCw, Play, Pause, RotateCcw,
  BookOpen, Lightbulb, ChevronRight, Users
} from "lucide-react";

// ==================== CRDT Type Definitions ====================

interface GCounterState {
  [replicaId: string]: number;
}

interface PNCounterState {
  p: GCounterState; // positive increments
  n: GCounterState; // negative increments
}

interface ORSetState<T> {
  elements: Map<T, Set<string>>; // element -> set of unique tags
  tombstones: Set<string>;       // removed tags
}

interface LWWRegisterState<T> {
  value: T | null;
  timestamp: number;
  replicaId: string;
}

// ==================== G-Counter CRDT ====================

function gCounterIncrement(state: GCounterState, replicaId: string): GCounterState {
  return {
    ...state,
    [replicaId]: (state[replicaId] || 0) + 1
  };
}

function gCounterValue(state: GCounterState | undefined | null): number {
  if (!state) return 0;
  return Object.values(state).reduce((sum, count) => sum + count, 0);
}

function gCounterMerge(state1: GCounterState, state2: GCounterState): GCounterState {
  const result = { ...state1 };
  for (const [replica, count] of Object.entries(state2)) {
    result[replica] = Math.max(result[replica] || 0, count);
  }
  return result;
}

// ==================== PN-Counter CRDT ====================

function pnCounterIncrement(state: PNCounterState, replicaId: string): PNCounterState {
  return {
    p: gCounterIncrement(state.p, replicaId),
    n: state.n
  };
}

function pnCounterDecrement(state: PNCounterState, replicaId: string): PNCounterState {
  return {
    p: state.p,
    n: gCounterIncrement(state.n, replicaId)
  };
}

function pnCounterValue(state: PNCounterState | undefined | null): number {
  if (!state) return 0;
  return gCounterValue(state.p) - gCounterValue(state.n);
}

function pnCounterMerge(state1: PNCounterState, state2: PNCounterState): PNCounterState {
  return {
    p: gCounterMerge(state1.p, state2.p),
    n: gCounterMerge(state1.n, state2.n)
  };
}

// ==================== OR-Set CRDT ====================

function orSetAdd<T>(state: ORSetState<T>, element: T, replicaId: string): ORSetState<T> {
  const tag = `${replicaId}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  const newElements = new Map(state.elements);
  const tags = new Set(newElements.get(element) || []);
  tags.add(tag);
  newElements.set(element, tags);
  return { ...state, elements: newElements };
}

function orSetRemove<T>(state: ORSetState<T>, element: T): ORSetState<T> {
  const tags = state.elements.get(element);
  if (!tags) return state;
  const newTombstones = new Set(state.tombstones);
  tags.forEach(tag => newTombstones.add(tag));
  const newElements = new Map(state.elements);
  newElements.delete(element);
  return { elements: newElements, tombstones: newTombstones };
}

function orSetHas<T>(state: ORSetState<T>, element: T): boolean {
  return state.elements.has(element);
}

function orSetElements<T>(state: ORSetState<T> | undefined | null): T[] {
  if (!state || !state.elements) return [];
  return Array.from(state.elements.keys());
}

function orSetMerge<T>(state1: ORSetState<T>, state2: ORSetState<T>): ORSetState<T> {
  const newElements = new Map(state1.elements);
  const newTombstones = new Set(state1.tombstones);
  
  // Merge tombstones
  state2.tombstones.forEach(tag => newTombstones.add(tag));
  
  // Merge elements
  for (const [element, tags] of state2.elements) {
    const existingTags = newElements.get(element) || new Set<string>();
    const mergedTags = new Set<string>();
    
    existingTags.forEach(tag => {
      if (!newTombstones.has(tag)) mergedTags.add(tag);
    });
    tags.forEach(tag => {
      if (!newTombstones.has(tag)) mergedTags.add(tag);
    });
    
    if (mergedTags.size > 0) {
      newElements.set(element, mergedTags);
    } else {
      newElements.delete(element);
    }
  }
  
  return { elements: newElements, tombstones: newTombstones };
}

// ==================== LWW-Register CRDT ====================

function lwwRegisterSet<T>(state: LWWRegisterState<T>, value: T, replicaId: string): LWWRegisterState<T> {
  const now = Date.now();
  if (now > state.timestamp) {
    return { value, timestamp: now, replicaId };
  }
  return state;
}

function lwwRegisterMerge<T>(state1: LWWRegisterState<T>, state2: LWWRegisterState<T>): LWWRegisterState<T> {
  if (state2.timestamp > state1.timestamp) return state2;
  if (state1.timestamp > state2.timestamp) return state1;
  // Tie-breaker: higher replica ID wins
  if (state2.replicaId > state1.replicaId) return state2;
  return state1;
}

// ==================== Core Simulator Component ====================

interface CoreProps {
  id: number;
  state: any;
  onIncrement?: () => void;
  onDecrement?: () => void;
  onSet?: (value: any) => void;
  onAdd?: (element: string) => void;
  onRemove?: (element: string) => void;
  type: 'gcounter' | 'pncounter' | 'orset' | 'lww';
  isSelected: boolean;
  onSelect: () => void;
}

function CoreSimulator({ id, state, onIncrement, onDecrement, onSet, onAdd, onRemove, type, isSelected, onSelect }: CoreProps) {
  const getValue = () => {
    switch (type) {
      case 'gcounter': return gCounterValue(state as GCounterState);
      case 'pncounter': return pnCounterValue(state as PNCounterState);
      case 'orset': return orSetElements(state as ORSetState<string>).join(', ') || '∅';
      case 'lww': return (state as LWWRegisterState<string>).value || 'null';
      default: return 'N/A';
    }
  };

  return (
    <motion.div
      className={`relative p-4 rounded-xl border-2 cursor-pointer transition-all ${
        isSelected 
          ? 'border-primary bg-primary/10 shadow-lg shadow-primary/20' 
          : 'border-border bg-card hover:border-primary/50'
      }`}
      onClick={onSelect}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* Core Avatar */}
      <div className="absolute -top-3 -left-3 w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center text-primary-foreground font-bold text-sm shadow-lg">
        {id}
      </div>
      
      {/* Robot Character */}
      <motion.div
        className="absolute -top-2 -right-2"
        animate={{ y: [0, -3, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="text-2xl">🤖</div>
      </motion.div>
      
      {/* State Display */}
      <div className="mt-4 text-center">
        <div className="text-xs text-muted-foreground mb-1">Core {id}</div>
        <div className="text-2xl font-bold font-mono">{getValue()}</div>
        <div className="text-xs text-muted-foreground mt-1">
          {type === 'gcounter' && 'G-Counter'}
          {type === 'pncounter' && 'PN-Counter'}
          {type === 'orset' && 'OR-Set'}
          {type === 'lww' && 'LWW-Register'}
        </div>
      </div>
      
      {/* Controls */}
      <div className="mt-3 flex gap-1 justify-center">
        {type === 'gcounter' && onIncrement && (
          <Button size="sm" onClick={(e) => { e.stopPropagation(); onIncrement(); }}>
            <Plus className="w-3 h-3" />
          </Button>
        )}
        {type === 'pncounter' && (
          <>
            {onIncrement && (
              <Button size="sm" onClick={(e) => { e.stopPropagation(); onIncrement(); }} variant="default">
                <Plus className="w-3 h-3" />
              </Button>
            )}
            {onDecrement && (
              <Button size="sm" onClick={(e) => { e.stopPropagation(); onDecrement(); }} variant="destructive">
                <Minus className="w-3 h-3" />
              </Button>
            )}
          </>
        )}
        {type === 'orset' && onAdd && (
          <Button size="sm" onClick={(e) => { e.stopPropagation(); onAdd(`item-${Date.now() % 100}`); }}>
            <Plus className="w-3 h-3" />
          </Button>
        )}
        {type === 'lww' && onSet && (
          <Button size="sm" onClick={(e) => { e.stopPropagation(); onSet(`val-${Date.now() % 1000}`); }}>
            Set
          </Button>
        )}
      </div>
    </motion.div>
  );
}

// ==================== Network Visualization ====================

function NetworkGraph({ cores, onMerge, mergeAnimations }: { 
  cores: number[]; 
  onMerge: (core1: number, core2: number) => void;
  mergeAnimations: { from: number; to: number; progress: number }[];
}) {
  const positions = cores.map((id, i) => {
    const angle = (i / cores.length) * 2 * Math.PI - Math.PI / 2;
    const radius = 120;
    return {
      id,
      x: 150 + radius * Math.cos(angle),
      y: 150 + radius * Math.sin(angle),
    };
  });

  return (
    <svg viewBox="0 0 300 300" className="w-full h-full">
      {/* Connections */}
      {positions.map((p1, i) => 
        positions.map((p2, j) => 
          j > i && (
            <motion.line
              key={`${i}-${j}`}
              x1={p1.x}
              y1={p1.y}
              x2={p2.x}
              y2={p2.y}
              stroke="hsl(var(--muted-foreground))"
              strokeWidth="1"
              strokeOpacity="0.3"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
            />
          )
        )
      )}
      
      {/* Merge Animations */}
      <AnimatePresence>
        {mergeAnimations.map((anim, i) => {
          const from = positions.find(p => p.id === anim.from)!;
          const to = positions.find(p => p.id === anim.to)!;
          const midX = from.x + (to.x - from.x) * anim.progress;
          const midY = from.y + (to.y - from.y) * anim.progress;
          return (
            <motion.circle
              key={i}
              cx={midX}
              cy={midY}
              r="8"
              fill="hsl(var(--primary))"
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
            />
          );
        })}
      </AnimatePresence>
      
      {/* Core Nodes */}
      {positions.map((pos, i) => (
        <motion.g
          key={pos.id}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.1 }}
        >
          <circle
            cx={pos.x}
            cy={pos.y}
            r="25"
            fill="hsl(var(--card))"
            stroke="hsl(var(--primary))"
            strokeWidth="2"
            className="cursor-pointer hover:stroke-[3px] transition-all"
          />
          <text
            x={pos.x}
            y={pos.y + 5}
            textAnchor="middle"
            fill="hsl(var(--foreground))"
            fontSize="14"
            fontWeight="bold"
          >
            C{pos.id}
          </text>
        </motion.g>
      ))}
    </svg>
  );
}

// ==================== Metrics Display ====================

function MetricsDisplay({ metrics }: { metrics: { ops: number; merges: number; latency: number; bandwidth: number } }) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Activity className="w-4 h-4 text-primary" />
            Operations/sec
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.ops.toLocaleString()}</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <GitMerge className="w-4 h-4 text-primary" />
            Merge Count
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.merges}</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Clock className="w-4 h-4 text-primary" />
            Avg Latency (cycles)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.latency}</div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Database className="w-4 h-4 text-primary" />
            Bandwidth Used
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.bandwidth}%</div>
        </CardContent>
      </Card>
    </div>
  );
}

// ==================== Educational Panel ====================

function EducationalPanel({ type }: { type: string }) {
  const content = {
    gcounter: {
      title: "G-Counter (Grow-only Counter)",
      description: "A counter that can only increment. Each replica tracks its own count, and the total is the sum of all replica counts.",
      properties: ["Commutative: max(a, b) = max(b, a)", "Idempotent: max(a, a) = a", "Monotonic: values only increase"],
      useCase: "Tracking total queries, cache hits, or any monotonic metric across distributed systems.",
      character: { name: "Counter-Bot", emoji: "🤖", saying: "I only go UP! Each core counts its own work, then we merge by taking the maximum per core!" }
    },
    pncounter: {
      title: "PN-Counter (Positive-Negative Counter)",
      description: "A counter supporting both increment and decrement using two G-Counters.",
      properties: ["Supports positive and negative operations", "Result = positive counter - negative counter", "Preserves all CRDT properties"],
      useCase: "Bank account balances, inventory management, or any counter that can go up or down.",
      character: { name: "Balance-Bot", emoji: "⚖️", saying: "I track pluses AND minuses! Two G-Counters work together to give you net change!" }
    },
    orset: {
      title: "OR-Set (Observed-Remove Set)",
      description: "A set that supports both add and remove operations. Each element has unique tags, and removes only affect observed elements.",
      properties: ["Add wins over remove", "Each add creates unique tag", "Remove only removes observed tags"],
      useCase: "Shopping carts, collaborative editing, or any collection where items can be added and removed.",
      character: { name: "Set-Squirrel", emoji: "🐿️", saying: "I remember what I've seen! When I remove something, I only remove what I know about!" }
    },
    lww: {
      title: "LWW-Register (Last-Writer-Wins)",
      description: "A register where the most recent write wins. Timestamps determine the winner.",
      properties: ["Highest timestamp wins", "Tie-breaker: replica ID", "Simple and efficient"],
      useCase: "User profile updates, configuration settings, or any value where recency matters.",
      character: { name: "Time-Keeper", emoji: "⏰", saying: "The last one to write wins! I check timestamps and pick the newest value!" }
    }
  };

  const info = content[type as keyof typeof content] || content.gcounter;

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-primary" />
          {info.title}
        </CardTitle>
        <CardDescription>{info.description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Character */}
        <div className="flex items-start gap-3 p-3 bg-primary/5 rounded-lg">
          <motion.div
            animate={{ rotate: [0, 10, -10, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="text-4xl"
          >
            {info.character.emoji}
          </motion.div>
          <div>
            <div className="font-medium">{info.character.name}</div>
            <div className="text-sm text-muted-foreground italic">"{info.character.saying}"</div>
          </div>
        </div>
        
        {/* Properties */}
        <div>
          <div className="font-medium mb-2 flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-yellow-500" />
            Key Properties
          </div>
          <ul className="space-y-1">
            {info.properties.map((prop, i) => (
              <li key={i} className="text-sm flex items-start gap-2">
                <ChevronRight className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                {prop}
              </li>
            ))}
          </ul>
        </div>
        
        {/* Use Case */}
        <div className="p-3 bg-muted rounded-lg">
          <div className="text-sm font-medium mb-1">Use Case</div>
          <div className="text-sm text-muted-foreground">{info.useCase}</div>
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== Main Page ====================

export default function CRDTLabPage() {
  const [activeTab, setActiveTab] = useState('gcounter');
  const [coreCount, setCoreCount] = useState(4);
  const [selectedCore, setSelectedCore] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [mergeAnimations, setMergeAnimations] = useState<{ from: number; to: number; progress: number }[]>([]);
  
  // CRDT States
  const [gCounterStates, setGCounterStates] = useState<GCounterState[]>([]);
  const [pnCounterStates, setPnCounterStates] = useState<PNCounterState[]>([]);
  const [orSetStates, setOrSetStates] = useState<ORSetState<string>[]>([]);
  const [lwwStates, setLwwStates] = useState<LWWRegisterState<string>[]>([]);
  
  // Metrics
  const [metrics, setMetrics] = useState({ ops: 0, merges: 0, latency: 34, bandwidth: 7 });

  // Initialize states
  useEffect(() => {
    setGCounterStates(Array(coreCount).fill(null).map(() => ({})));
    setPnCounterStates(Array(coreCount).fill(null).map(() => ({ p: {}, n: {} })));
    setOrSetStates(Array(coreCount).fill(null).map(() => ({ elements: new Map(), tombstones: new Set() })));
    setLwwStates(Array(coreCount).fill(null).map((_, i) => ({ value: null, timestamp: 0, replicaId: `core-${i}` })));
  }, [coreCount]);

  // Auto-simulation
  useEffect(() => {
    if (!isRunning) return;
    const interval = setInterval(() => {
      const coreId = Math.floor(Math.random() * coreCount);
      if (activeTab === 'gcounter') {
        setGCounterStates(prev => {
          const newStates = [...prev];
          newStates[coreId] = gCounterIncrement(newStates[coreId], `core-${coreId}`);
          return newStates;
        });
      } else if (activeTab === 'pncounter') {
        setPnCounterStates(prev => {
          const newStates = [...prev];
          if (Math.random() > 0.3) {
            newStates[coreId] = pnCounterIncrement(newStates[coreId], `core-${coreId}`);
          } else {
            newStates[coreId] = pnCounterDecrement(newStates[coreId], `core-${coreId}`);
          }
          return newStates;
        });
      }
      setMetrics(prev => ({ ...prev, ops: prev.ops + 1 }));
    }, 200);
    return () => clearInterval(interval);
  }, [isRunning, coreCount, activeTab]);

  // Periodic merge
  useEffect(() => {
    if (!isRunning) return;
    const interval = setInterval(() => {
      const core1 = Math.floor(Math.random() * coreCount);
      let core2 = Math.floor(Math.random() * coreCount);
      while (core2 === core1) core2 = Math.floor(Math.random() * coreCount);
      
      // Animate merge
      setMergeAnimations(prev => [...prev, { from: core1, to: core2, progress: 0 }]);
      
      setTimeout(() => {
        setMergeAnimations(prev => prev.slice(1));
        if (activeTab === 'gcounter') {
          setGCounterStates(prev => {
            const merged = gCounterMerge(prev[core1], prev[core2]);
            return prev.map((s, i) => i === core1 || i === core2 ? merged : s);
          });
        } else if (activeTab === 'pncounter') {
          setPnCounterStates(prev => {
            const merged = pnCounterMerge(prev[core1], prev[core2]);
            return prev.map((s, i) => i === core1 || i === core2 ? merged : s);
          });
        }
        setMetrics(prev => ({ ...prev, merges: prev.merges + 1 }));
      }, 500);
    }, 1000);
    return () => clearInterval(interval);
  }, [isRunning, coreCount, activeTab]);

  // Manual operations
  const handleGCounterIncrement = (coreId: number) => {
    setGCounterStates(prev => {
      const newStates = [...prev];
      newStates[coreId] = gCounterIncrement(newStates[coreId], `core-${coreId}`);
      return newStates;
    });
    setMetrics(prev => ({ ...prev, ops: prev.ops + 1 }));
  };

  const handlePNCounterIncrement = (coreId: number) => {
    setPnCounterStates(prev => {
      const newStates = [...prev];
      newStates[coreId] = pnCounterIncrement(newStates[coreId], `core-${coreId}`);
      return newStates;
    });
    setMetrics(prev => ({ ...prev, ops: prev.ops + 1 }));
  };

  const handlePNCounterDecrement = (coreId: number) => {
    setPnCounterStates(prev => {
      const newStates = [...prev];
      newStates[coreId] = pnCounterDecrement(newStates[coreId], `core-${coreId}`);
      return newStates;
    });
    setMetrics(prev => ({ ...prev, ops: prev.ops + 1 }));
  };

  const handleOrSetAdd = (coreId: number, element: string) => {
    setOrSetStates(prev => {
      const newStates = [...prev];
      newStates[coreId] = orSetAdd(newStates[coreId], element, `core-${coreId}`);
      return newStates;
    });
    setMetrics(prev => ({ ...prev, ops: prev.ops + 1 }));
  };

  const handleLwwSet = (coreId: number, value: string) => {
    setLwwStates(prev => {
      const newStates = [...prev];
      newStates[coreId] = lwwRegisterSet(newStates[coreId], value, `core-${coreId}`);
      return newStates;
    });
    setMetrics(prev => ({ ...prev, ops: prev.ops + 1 }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-background/95 pt-20 pb-10">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary via-primary/80 to-primary/60 bg-clip-text text-transparent">
            CRDT Simulation Laboratory
          </h1>
          <p className="text-muted-foreground mt-2">
            Explore Conflict-free Replicated Data Types for Intra-Chip Communication
          </p>
          <div className="flex items-center justify-center gap-4 mt-4">
            <Badge variant="outline" className="flex items-center gap-1">
              <Atom className="w-3 h-3" />
              Strong Eventual Consistency
            </Badge>
            <Badge variant="outline" className="flex items-center gap-1">
              <Network className="w-3 h-3" />
              Distributed
            </Badge>
            <Badge variant="outline" className="flex items-center gap-1">
              <Zap className="w-3 h-3" />
              Lock-Free
            </Badge>
          </div>
        </motion.div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="gcounter">G-Counter</TabsTrigger>
            <TabsTrigger value="pncounter">PN-Counter</TabsTrigger>
            <TabsTrigger value="orset">OR-Set</TabsTrigger>
            <TabsTrigger value="lww">LWW-Register</TabsTrigger>
          </TabsList>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Simulation Area */}
            <div className="lg:col-span-2 space-y-6">
              {/* Controls */}
              <Card>
                <CardContent className="pt-6">
                  <div className="flex flex-wrap items-center gap-4">
                    <div className="flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm">Cores:</span>
                      <Slider
                        value={[coreCount]}
                        onValueChange={([v]) => setCoreCount(v)}
                        min={2}
                        max={16}
                        step={2}
                        className="w-32"
                      />
                      <span className="font-mono w-8">{coreCount}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant={isRunning ? "destructive" : "default"}
                        onClick={() => setIsRunning(!isRunning)}
                      >
                        {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        {isRunning ? 'Pause' : 'Simulate'}
                      </Button>
                      <Button variant="outline" onClick={() => {
                        setMetrics({ ops: 0, merges: 0, latency: 34, bandwidth: 7 });
                        setGCounterStates(Array(coreCount).fill(null).map(() => ({})));
                        setPnCounterStates(Array(coreCount).fill(null).map(() => ({ p: {}, n: {} })));
                      }}>
                        <RotateCcw className="w-4 h-4" />
                        Reset
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Core Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Array(coreCount).fill(null).map((_, i) => (
                  <CoreSimulator
                    key={i}
                    id={i}
                    type={activeTab as any}
                    state={
                      activeTab === 'gcounter' ? gCounterStates[i] :
                      activeTab === 'pncounter' ? pnCounterStates[i] :
                      activeTab === 'orset' ? orSetStates[i] :
                      lwwStates[i]
                    }
                    onIncrement={() => activeTab === 'gcounter' ? handleGCounterIncrement(i) : handlePNCounterIncrement(i)}
                    onDecrement={() => handlePNCounterDecrement(i)}
                    onSet={(v) => handleLwwSet(i, v)}
                    onAdd={(e) => handleOrSetAdd(i, e)}
                    isSelected={selectedCore === i}
                    onSelect={() => setSelectedCore(i)}
                  />
                ))}
              </div>

              {/* Network Visualization */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Network className="w-5 h-5 text-primary" />
                    Core Network
                  </CardTitle>
                  <CardDescription>
                    Click two cores to merge their states
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="w-full h-64">
                    <NetworkGraph
                      cores={Array(coreCount).fill(null).map((_, i) => i)}
                      onMerge={() => {}}
                      mergeAnimations={mergeAnimations}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Metrics */}
              <MetricsDisplay metrics={metrics} />
            </div>

            {/* Educational Panel */}
            <div className="lg:col-span-1">
              <EducationalPanel type={activeTab} />
              
              {/* Comparison Card */}
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle className="text-lg">CRDT vs MESI</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Average Latency</div>
                      <div className="flex items-center gap-4 mt-1">
                        <div className="flex-1">
                          <div className="text-xs text-muted-foreground mb-1">MESI</div>
                          <div className="h-4 bg-muted rounded-full overflow-hidden">
                            <div className="h-full bg-red-500 w-[80%]" />
                          </div>
                          <div className="text-xs mt-1">~127 cycles</div>
                        </div>
                        <div className="flex-1">
                          <div className="text-xs text-muted-foreground mb-1">CRDT</div>
                          <div className="h-4 bg-muted rounded-full overflow-hidden">
                            <div className="h-full bg-green-500 w-[20%]" />
                          </div>
                          <div className="text-xs mt-1">~34 cycles</div>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-sm text-muted-foreground">Coherence Traffic</div>
                      <div className="flex items-center gap-4 mt-1">
                        <div className="flex-1">
                          <div className="text-xs text-muted-foreground mb-1">MESI</div>
                          <div className="h-4 bg-muted rounded-full overflow-hidden">
                            <div className="h-full bg-red-500 w-[23%]" />
                          </div>
                          <div className="text-xs mt-1">23% bandwidth</div>
                        </div>
                        <div className="flex-1">
                          <div className="text-xs text-muted-foreground mb-1">CRDT</div>
                          <div className="h-4 bg-muted rounded-full overflow-hidden">
                            <div className="h-full bg-green-500 w-[7%]" />
                          </div>
                          <div className="text-xs mt-1">7% bandwidth</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </Tabs>
      </div>
    </div>
  );
}
