"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Box,
  Cube,
  Layers,
  Grid3X3,
  RotateCcw,
  ZoomIn,
  ZoomOut,
  Play,
  Pause,
  Sparkles,
  Brain,
  Lightbulb,
  Target,
  Trophy,
  Star,
  Zap,
  ChevronRight,
  ChevronLeft,
  Info,
  Eye,
  EyeOff,
} from "lucide-react";

// ============================================================================
// VOXEL GAME INTEGRATOR
// Integrates voxel engine into games, education, and UX design
// ============================================================================

type VoxelModule = "transistor" | "cpu" | "memory" | "led" | "circuit";
type ViewMode = "explore" | "game" | "learn";
type AgeLevel = "elementary" | "middle" | "high";

interface VoxelCell {
  id: string;
  x: number;
  y: number;
  z: number;
  color: string;
  type: "conductor" | "insulator" | "semiconductor" | "active";
  label?: string;
}

interface VoxelLayer {
  id: string;
  name: string;
  z: number;
  cells: VoxelCell[];
  visible: boolean;
}

interface VoxelModel {
  id: string;
  name: string;
  description: string;
  icon: typeof Cube;
  color: string;
  layers: VoxelLayer[];
  ageAdaptation: Record<AgeLevel, { title: string; description: string }>;
  funFacts: Record<AgeLevel, string[]>;
}

// Voxel Models Data
const VOXEL_MODELS: VoxelModel[] = [
  {
    id: "transistor",
    name: "Transistor",
    description: "The tiny switch that powers everything",
    icon: Zap,
    color: "yellow",
    layers: [
      {
        id: "gate",
        name: "Gate",
        z: 0,
        visible: true,
        cells: [
          { id: "g1", x: 2, y: 2, z: 0, color: "#60A5FA", type: "conductor", label: "G" },
          { id: "g2", x: 2, y: 3, z: 0, color: "#60A5FA", type: "conductor" },
          { id: "g3", x: 3, y: 2, z: 0, color: "#60A5FA", type: "conductor" },
          { id: "g4", x: 3, y: 3, z: 0, color: "#60A5FA", type: "conductor" },
        ],
      },
      {
        id: "channel",
        name: "Channel",
        z: 1,
        visible: true,
        cells: [
          { id: "c1", x: 1, y: 2, z: 1, color: "#10B981", type: "semiconductor", label: "S" },
          { id: "c2", x: 2, y: 2, z: 1, color: "#34D399", type: "semiconductor" },
          { id: "c3", x: 3, y: 2, z: 1, color: "#34D399", type: "semiconductor" },
          { id: "c4", x: 4, y: 2, z: 1, color: "#F59E0B", type: "semiconductor", label: "D" },
        ],
      },
    ],
    ageAdaptation: {
      elementary: { title: "The Tiny Switch", description: "A transistor is like a tiny light switch that turns things on and off super fast!" },
      middle: { title: "Electronic Gate", description: "A transistor uses voltage on the gate to control current flow between source and drain." },
      high: { title: "Field-Effect Transistor", description: "A MOSFET uses an electric field to control the conductivity of a channel." },
    },
    funFacts: {
      elementary: ["Your phone has BILLIONS of transistors!", "They switch faster than you can blink!", "Each one is smaller than a virus!"],
      middle: ["Modern transistors are only 5 nanometers wide!", "A human hair is about 80,000 nanometers thick!", "Moore's Law: transistors double every 2 years!"],
      high: ["FinFETs use 3D fins for better gate control", "Gate-all-around transistors are the next generation", "Quantum tunneling limits below 1nm scaling"],
    },
  },
  {
    id: "cpu",
    name: "CPU Core",
    description: "The brain of your computer",
    icon: Brain,
    color: "blue",
    layers: [
      {
        id: "cores",
        name: "Cores",
        z: 0,
        visible: true,
        cells: [
          { id: "co1", x: 1, y: 1, z: 0, color: "#6366F1", type: "active", label: "C1" },
          { id: "co2", x: 3, y: 1, z: 0, color: "#6366F1", type: "active", label: "C2" },
          { id: "co3", x: 1, y: 3, z: 0, color: "#6366F1", type: "active", label: "C3" },
          { id: "co4", x: 3, y: 3, z: 0, color: "#6366F1", type: "active", label: "C4" },
        ],
      },
      {
        id: "cache",
        name: "Cache",
        z: 1,
        visible: true,
        cells: [
          { id: "ca1", x: 0, y: 0, z: 1, color: "#22C55E", type: "conductor" },
          { id: "ca2", x: 4, y: 0, z: 1, color: "#22C55E", type: "conductor" },
          { id: "ca3", x: 0, y: 4, z: 1, color: "#22C55E", type: "conductor" },
          { id: "ca4", x: 4, y: 4, z: 1, color: "#22C55E", type: "conductor" },
        ],
      },
    ],
    ageAdaptation: {
      elementary: { title: "The Brain", description: "The CPU is like the brain of your computer - it does all the thinking!" },
      middle: { title: "Central Processing Unit", description: "The CPU executes instructions and processes data at billions of operations per second." },
      high: { title: "Multi-Core Architecture", description: "Modern CPUs have multiple cores for parallel processing, shared cache hierarchy, and out-of-order execution." },
    },
    funFacts: {
      elementary: ["CPU stands for Central Processing Unit!", "Modern CPUs have billions of parts!", "They can do billions of math problems per second!"],
      middle: ["CPU clock speeds are measured in GHz (billions per second!)", "The first CPU had only 2,300 transistors", "CPUs generate heat and need cooling fans"],
      high: ["Modern CPUs have 10+ billion transistors", "TDP ranges from 15W to 250W+", "Instruction-level parallelism: 4-8 ops per cycle"],
    },
  },
];

interface VoxelGameIntegratorProps {
  ageLevel?: AgeLevel;
  onModuleSelect?: (module: VoxelModule) => void;
  onScoreUpdate?: (score: number) => void;
}

export function VoxelGameIntegrator({ 
  ageLevel = "middle", 
  onModuleSelect,
  onScoreUpdate 
}: VoxelGameIntegratorProps) {
  const [currentModelIndex, setCurrentModelIndex] = useState(0);
  const [viewMode, setViewMode] = useState<ViewMode>("explore");
  const [selectedCell, setSelectedCell] = useState<VoxelCell | null>(null);
  const [rotation, setRotation] = useState({ x: 25, y: -35 });
  const [zoom, setZoom] = useState(1);
  const [isAnimating, setIsAnimating] = useState(false);
  const [gameScore, setGameScore] = useState(0);
  const [signalPath, setSignalPath] = useState<string[]>([]);

  const currentModel = VOXEL_MODELS[currentModelIndex];
  const adaptation = currentModel.ageAdaptation[ageLevel];
  const funFacts = currentModel.funFacts[ageLevel];

  const toggleLayerVisibility = useCallback((layerId: string) => {
    // This would update layer visibility in a real implementation
  }, []);

  const animateSignalPath = useCallback(() => {
    setIsAnimating(true);
    setSignalPath([]);
    
    // Simulate signal flow animation
    const allCells = currentModel.layers.flatMap(l => l.cells);
    let index = 0;
    
    const interval = setInterval(() => {
      if (index < allCells.length) {
        setSignalPath(prev => [...prev, allCells[index].id]);
        if (viewMode === "game") {
          setGameScore(prev => prev + 10);
          onScoreUpdate?.(gameScore + 10);
        }
        index++;
      } else {
        clearInterval(interval);
        setIsAnimating(false);
      }
    }, 200);
  }, [currentModel, viewMode, gameScore, onScoreUpdate]);

  const nextModel = useCallback(() => {
    setCurrentModelIndex((prev) => (prev + 1) % VOXEL_MODELS.length);
    setSelectedCell(null);
    setSignalPath([]);
  }, []);

  const prevModel = useCallback(() => {
    setCurrentModelIndex((prev) => (prev - 1 + VOXEL_MODELS.length) % VOXEL_MODELS.length);
    setSelectedCell(null);
    setSignalPath([]);
  }, []);

  return (
    <div className="bg-gradient-to-br from-slate-900 via-indigo-900/20 to-slate-900 rounded-2xl border border-indigo-500/30 overflow-hidden">
      {/* Header */}
      <div className="bg-slate-800/50 px-4 py-3 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Box className="w-5 h-5 text-indigo-400" />
            <span className="font-bold text-white">Voxel Explorer</span>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center gap-1 bg-slate-900/50 rounded-lg p-1">
            {[
              { id: "explore" as ViewMode, label: "Explore", icon: Eye },
              { id: "game" as ViewMode, label: "Game", icon: Target },
              { id: "learn" as ViewMode, label: "Learn", icon: Brain },
            ].map(mode => (
              <button
                key={mode.id}
                onClick={() => setViewMode(mode.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all ${
                  viewMode === mode.id
                    ? "bg-indigo-500 text-white"
                    : "text-slate-400 hover:text-white hover:bg-slate-700"
                }`}
              >
                <mode.icon className="w-4 h-4" />
                {mode.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex">
        {/* Main Voxel View */}
        <div className="flex-1 p-4 min-h-[350px] relative">
          {/* Title */}
          <div className="mb-4">
            <h3 className="text-lg font-bold text-white">{adaptation.title}</h3>
            <p className="text-sm text-slate-400">{adaptation.description}</p>
          </div>

          {/* Voxel Grid */}
          <div 
            className="relative mx-auto"
            style={{ 
              width: 240,
              height: 240,
              perspective: "800px",
              transform: `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg) scale(${zoom})`,
            }}
          >
            <AnimatePresence>
              {currentModel.layers.map((layer, layerIndex) => (
                layer.visible && (
                  <div
                    key={layer.id}
                    className="absolute inset-0"
                    style={{ transform: `translateZ(${layerIndex * 20}px)` }}
                  >
                    {layer.cells.map((cell) => (
                      <motion.div
                        key={cell.id}
                        className={`absolute w-10 h-10 rounded-lg cursor-pointer flex items-center justify-center text-xs font-bold text-white transition-all ${
                          signalPath.includes(cell.id) ? "ring-2 ring-yellow-400 shadow-lg shadow-yellow-400/50" : ""
                        }`}
                        style={{
                          left: cell.x * 44,
                          top: cell.y * 44,
                          backgroundColor: cell.color,
                          opacity: signalPath.length > 0 && !signalPath.includes(cell.id) ? 0.5 : 1,
                        }}
                        onClick={() => setSelectedCell(cell)}
                        whileHover={{ scale: 1.1, zIndex: 10 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        {cell.label}
                      </motion.div>
                    ))}
                  </div>
                )
              ))}
            </AnimatePresence>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-center gap-4 mt-4">
            <button
              onClick={prevModel}
              className="p-2 bg-slate-800 rounded-lg text-slate-400 hover:text-white"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            
            <button
              onClick={animateSignalPath}
              disabled={isAnimating}
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg text-white text-sm"
            >
              {isAnimating ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              Animate
            </button>
            
            <button
              onClick={nextModel}
              className="p-2 bg-slate-800 rounded-lg text-slate-400 hover:text-white"
            >
              <ChevronRight className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-1 ml-4">
              <button
                onClick={() => setZoom(z => Math.max(0.5, z - 0.1))}
                className="p-2 bg-slate-800 rounded-lg text-slate-400 hover:text-white"
              >
                <ZoomOut className="w-4 h-4" />
              </button>
              <span className="text-xs text-slate-400 w-8 text-center">{(zoom * 100).toFixed(0)}%</span>
              <button
                onClick={() => setZoom(z => Math.min(2, z + 0.1))}
                className="p-2 bg-slate-800 rounded-lg text-slate-400 hover:text-white"
              >
                <ZoomIn className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Game Score */}
          {viewMode === "game" && (
            <div className="absolute top-4 right-4 bg-slate-800/80 rounded-lg px-3 py-2">
              <div className="flex items-center gap-2">
                <Star className="w-4 h-4 text-yellow-400" />
                <span className="font-bold text-yellow-400">{gameScore}</span>
              </div>
            </div>
          )}
        </div>

        {/* Right Panel */}
        <div className="w-56 border-l border-slate-700 p-3">
          {/* Layers */}
          <div className="mb-4">
            <h4 className="text-xs font-medium text-slate-400 mb-2">Layers</h4>
            <div className="space-y-1">
              {currentModel.layers.map((layer) => (
                <button
                  key={layer.id}
                  onClick={() => toggleLayerVisibility(layer.id)}
                  className={`w-full p-2 rounded-lg flex items-center justify-between text-sm transition-all ${
                    layer.visible ? "bg-slate-800/50 text-white" : "bg-slate-900/50 text-slate-500"
                  }`}
                >
                  <span>{layer.name}</span>
                  {layer.visible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                </button>
              ))}
            </div>
          </div>

          {/* Fun Facts */}
          <div>
            <h4 className="text-xs font-medium text-slate-400 mb-2 flex items-center gap-1">
              <Lightbulb className="w-3 h-3 text-yellow-400" />
              Fun Facts
            </h4>
            <div className="space-y-2">
              {funFacts.map((fact, index) => (
                <div key={index} className="p-2 bg-slate-800/30 rounded-lg text-xs text-slate-300">
                  {fact}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VoxelGameIntegrator;
