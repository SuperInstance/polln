"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Cpu, Layers, Box, Zap, ArrowRight, ChevronRight,
  Play, Pause, RotateCcw, Download, Share2, Settings,
  Maximize2, Trash2, Copy, Move, Grid, Eye, Lightbulb,
  Palette, Ruler, CircuitBoard, Binary, MemoryStick
} from "lucide-react";

// Voxel block types
const blockTypes = [
  { id: "compute", name: "Compute Unit", color: "#22c55e", power: 2, area: 4 },
  { id: "memory", name: "Memory Array", color: "#8b5cf6", power: 0.5, area: 6 },
  { id: "logic", name: "Logic Gate", color: "#3b82f6", power: 0.1, area: 1 },
  { id: "io", name: "I/O Block", color: "#f59e0b", power: 0.3, area: 2 },
  { id: "clock", name: "Clock Tree", color: "#ec4899", power: 0.2, area: 1 },
  { id: "power", name: "Power Grid", color: "#ef4444", power: 0, area: 1 },
  { id: "ai", name: "AI Accelerator", color: "#06b6d4", power: 5, area: 8 },
  { id: "routing", name: "Routing Channel", color: "#64748b", power: 0.05, area: 1 },
];

// Grid configuration
const GRID_SIZE = 8;

// Single Voxel Block Component
function VoxelBlock({
  type,
  size = 40,
  onClick,
  isSelected,
  showLabel = false,
}: {
  type: typeof blockTypes[0] | null;
  size?: number;
  onClick?: () => void;
  isSelected?: boolean;
  showLabel?: boolean;
}) {
  if (!type) {
    return (
      <div
        onClick={onClick}
        className={`cursor-pointer transition-all hover:bg-dark-600/50 ${
          isSelected ? "ring-2 ring-green-500" : ""
        }`}
        style={{
          width: size,
          height: size,
          background: "rgba(30, 30, 40, 0.3)",
          border: "1px dashed rgba(100, 100, 120, 0.3)",
          borderRadius: 4,
        }}
      />
    );
  }

  return (
    <div
      onClick={onClick}
      className={`cursor-pointer transition-all hover:scale-105 ${
        isSelected ? "ring-2 ring-white" : ""
      }`}
      style={{
        width: size,
        height: size,
        background: `linear-gradient(135deg, ${type.color} 0%, ${type.color}cc 100%)`,
        boxShadow: `inset -2px -2px 4px rgba(0,0,0,0.3), inset 2px 2px 4px rgba(255,255,255,0.2), 0 2px 8px ${type.color}40`,
        borderRadius: 4,
      }}
      title={type.name}
    >
      {showLabel && (
        <div className="text-[8px] text-white/80 flex items-center justify-center h-full font-medium">
          {type.name.charAt(0)}
        </div>
      )}
    </div>
  );
}

// 3D Grid Visualization
function VoxelGrid({
  grid,
  selectedBlock,
  onPlaceBlock,
  onDeleteBlock,
}: {
  grid: (typeof blockTypes[0] | null)[][];
  selectedBlock: typeof blockTypes[0];
  onPlaceBlock: (x: number, y: number) => void;
  onDeleteBlock: (x: number, y: number) => void;
}) {
  const [rotation, setRotation] = useState(0);

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Box className="w-5 h-5 text-purple-400" />
          <span className="font-semibold">Chip Canvas</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setRotation((r) => (r + 45) % 360)}
            className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors">
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="p-6">
        {/* Grid */}
        <div
          className="grid gap-1 mx-auto"
          style={{
            gridTemplateColumns: `repeat(${GRID_SIZE}, 40px)`,
            transform: `rotate(${rotation}deg)`,
            transition: "transform 0.5s ease",
          }}
        >
          {grid.map((row, y) =>
            row.map((block, x) => (
              <VoxelBlock
                key={`${x}-${y}`}
                type={block}
                onClick={() => {
                  if (block) {
                    onDeleteBlock(x, y);
                  } else if (selectedBlock) {
                    onPlaceBlock(x, y);
                  }
                }}
              />
            ))
          )}
        </div>

        {/* Legend */}
        <div className="mt-6 flex flex-wrap gap-2 justify-center">
          {blockTypes.slice(0, 4).map((type) => (
            <div
              key={type.id}
              className="flex items-center gap-2 px-2 py-1 rounded-lg bg-dark-700/50"
            >
              <div
                className="w-3 h-3 rounded"
                style={{ background: type.color }}
              />
              <span className="text-xs text-gray-400">{type.name}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Block Palette
function BlockPalette({
  selectedBlock,
  onSelectBlock,
}: {
  selectedBlock: typeof blockTypes[0];
  onSelectBlock: (block: typeof blockTypes[0]) => void;
}) {
  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Palette className="w-5 h-5 text-cyan-400" />
          <span className="font-semibold">Block Palette</span>
        </div>
      </div>

      <div className="p-4">
        <div className="grid grid-cols-2 gap-2">
          {blockTypes.map((block) => (
            <button
              key={block.id}
              onClick={() => onSelectBlock(block)}
              className={`p-3 rounded-xl text-left transition-all ${
                selectedBlock?.id === block.id
                  ? "bg-cyan-500/20 text-white border border-cyan-500/30"
                  : "bg-dark-700/50 text-gray-400 border border-dark-600 hover:border-dark-500"
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <div
                  className="w-4 h-4 rounded"
                  style={{ background: block.color }}
                />
                <span className="text-sm font-medium">{block.name}</span>
              </div>
              <div className="text-xs text-gray-500">
                {block.power}W • {block.area}mm²
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// Design Statistics
function DesignStats({ grid }: { grid: (typeof blockTypes[0] | null)[][] }) {
  const stats = {
    totalBlocks: 0,
    totalPower: 0,
    totalArea: 0,
    computeUnits: 0,
    memoryBlocks: 0,
    aiAccelerators: 0,
  };

  grid.forEach((row) => {
    row.forEach((block) => {
      if (block) {
        stats.totalBlocks++;
        stats.totalPower += block.power;
        stats.totalArea += block.area;
        if (block.id === "compute") stats.computeUnits++;
        if (block.id === "memory") stats.memoryBlocks++;
        if (block.id === "ai") stats.aiAccelerators++;
      }
    });
  });

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Ruler className="w-5 h-5 text-amber-400" />
          <span className="font-semibold">Design Statistics</span>
        </div>
      </div>

      <div className="p-4">
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-dark-700/50 rounded-xl p-3 text-center">
            <div className="text-2xl font-mono text-green-400">{stats.totalBlocks}</div>
            <div className="text-xs text-gray-500">Blocks Placed</div>
          </div>
          <div className="bg-dark-700/50 rounded-xl p-3 text-center">
            <div className="text-2xl font-mono text-amber-400">{stats.totalPower.toFixed(1)}W</div>
            <div className="text-xs text-gray-500">Total Power</div>
          </div>
          <div className="bg-dark-700/50 rounded-xl p-3 text-center">
            <div className="text-2xl font-mono text-purple-400">{stats.totalArea}mm²</div>
            <div className="text-xs text-gray-500">Die Area</div>
          </div>
          <div className="bg-dark-700/50 rounded-xl p-3 text-center">
            <div className="text-2xl font-mono text-blue-400">{stats.computeUnits}</div>
            <div className="text-xs text-gray-500">Compute Units</div>
          </div>
        </div>

        {/* Component Breakdown */}
        <div className="mt-4 space-y-2">
          <div className="text-xs text-gray-400 mb-2">Component Breakdown</div>
          {[
            { name: "Compute", count: stats.computeUnits, color: "#22c55e" },
            { name: "Memory", count: stats.memoryBlocks, color: "#8b5cf6" },
            { name: "AI Accel", count: stats.aiAccelerators, color: "#06b6d4" },
          ].map((comp) => (
            <div key={comp.name} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded"
                  style={{ background: comp.color }}
                />
                <span className="text-sm text-gray-400">{comp.name}</span>
              </div>
              <span className="text-sm font-mono text-gray-300">{comp.count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Template Gallery
function TemplateGallery({ onSelectTemplate }: { onSelectTemplate: (template: string) => void }) {
  const templates = [
    { id: "mcu", name: "Basic MCU", desc: "Simple microcontroller layout" },
    { id: "ai-edge", name: "AI Edge Chip", desc: "AI accelerator for edge devices" },
    { id: "memory-heavy", name: "Memory-Intensive", desc: "Large memory arrays" },
    { id: "balanced", name: "Balanced SoC", desc: "Mixed compute and memory" },
  ];

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Layers className="w-5 h-5 text-pink-400" />
          <span className="font-semibold">Quick Templates</span>
        </div>
      </div>

      <div className="p-4">
        <div className="grid grid-cols-2 gap-2">
          {templates.map((template) => (
            <button
              key={template.id}
              onClick={() => onSelectTemplate(template.id)}
              className="p-3 rounded-xl bg-dark-700/50 border border-dark-600 hover:border-green-500/30 text-left transition-all"
            >
              <div className="font-medium text-sm text-gray-300">{template.name}</div>
              <div className="text-xs text-gray-500 mt-1">{template.desc}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// Visual Learning Mode
function VisualLearningMode() {
  const [currentLesson, setCurrentLesson] = useState(0);

  const lessons = [
    {
      title: "Chip Layers",
      description: "Chips are built in layers, like a sandwich",
      visual: (
        <div className="flex flex-col items-center gap-2">
          {["#f59e0b", "#3b82f6", "#8b5cf6", "#22c55e", "#64748b"].map((color, i) => (
            <div
              key={i}
              className="w-32 h-6 rounded transition-all hover:scale-105"
              style={{
                background: `linear-gradient(90deg, ${color}40, ${color})`,
                transform: `translateX(${i * 5}px)`,
              }}
            />
          ))}
        </div>
      ),
    },
    {
      title: "Data Flow",
      description: "Information flows through the chip",
      visual: (
        <div className="flex items-center justify-center gap-4">
          <div className="w-16 h-16 rounded-xl bg-green-500/30 flex items-center justify-center">
            <span className="text-2xl">📥</span>
          </div>
          <div className="flex items-center gap-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-2 h-2 rounded-full bg-green-400 animate-pulse"
                style={{ animationDelay: `${i * 200}ms` }}
              />
            ))}
          </div>
          <div className="w-16 h-16 rounded-xl bg-purple-500/30 flex items-center justify-center">
            <span className="text-2xl">⚡</span>
          </div>
          <div className="flex items-center gap-1">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-2 h-2 rounded-full bg-purple-400 animate-pulse"
                style={{ animationDelay: `${i * 200}ms` }}
              />
            ))}
          </div>
          <div className="w-16 h-16 rounded-xl bg-blue-500/30 flex items-center justify-center">
            <span className="text-2xl">📤</span>
          </div>
        </div>
      ),
    },
    {
      title: "Timing",
      description: "Everything happens at the right moment",
      visual: (
        <div className="flex items-center gap-4">
          <div className="flex flex-col gap-2">
            {[0, 1, 2, 3].map((i) => (
              <div
                key={i}
                className="w-4 h-4 rounded-full bg-green-500"
                style={{
                  opacity: i === Math.floor(Date.now() / 500) % 4 ? 1 : 0.3,
                }}
              />
            ))}
          </div>
          <div className="w-24 h-1 bg-dark-600 relative overflow-hidden rounded">
            <div
              className="absolute h-full bg-green-500 rounded transition-all"
              style={{
                width: "25%",
                left: `${((Math.floor(Date.now() / 500) % 4) / 4) * 100}%`,
              }}
            />
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Lightbulb className="w-5 h-5 text-yellow-400" />
          <span className="font-semibold">Visual Learning</span>
        </div>
      </div>

      <div className="p-6">
        {/* Lesson Navigation */}
        <div className="flex gap-2 mb-4">
          {lessons.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrentLesson(i)}
              className={`w-8 h-8 rounded-full transition-all ${
                currentLesson === i
                  ? "bg-yellow-500 text-black"
                  : "bg-dark-700 text-gray-400 hover:bg-dark-600"
              }`}
            >
              {i + 1}
            </button>
          ))}
        </div>

        {/* Current Lesson */}
        <div className="text-center">
          <h3 className="text-lg font-semibold mb-2">{lessons[currentLesson].title}</h3>
          <p className="text-sm text-gray-400 mb-6">{lessons[currentLesson].description}</p>
          <div className="flex justify-center py-8">
            {lessons[currentLesson].visual}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between mt-4">
          <button
            onClick={() => setCurrentLesson((c) => Math.max(0, c - 1))}
            disabled={currentLesson === 0}
            className="px-4 py-2 rounded-lg bg-dark-700 text-gray-400 disabled:opacity-50"
          >
            Previous
          </button>
          <button
            onClick={() => setCurrentLesson((c) => Math.min(lessons.length - 1, c + 1))}
            disabled={currentLesson === lessons.length - 1}
            className="px-4 py-2 rounded-lg bg-green-600 text-white disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

export default function VoxelLabPage() {
  // Initialize empty grid
  const [grid, setGrid] = useState<(typeof blockTypes[0] | null)[][]>(() =>
    Array(GRID_SIZE)
      .fill(null)
      .map(() => Array(GRID_SIZE).fill(null))
  );

  const [selectedBlock, setSelectedBlock] = useState(blockTypes[0]);

  const handlePlaceBlock = useCallback((x: number, y: number) => {
    setGrid((prev) => {
      const newGrid = prev.map((row) => [...row]);
      newGrid[y][x] = selectedBlock;
      return newGrid;
    });
  }, [selectedBlock]);

  const handleDeleteBlock = useCallback((x: number, y: number) => {
    setGrid((prev) => {
      const newGrid = prev.map((row) => [...row]);
      newGrid[y][x] = null;
      return newGrid;
    });
  }, []);

  const handleClearGrid = () => {
    setGrid(
      Array(GRID_SIZE)
        .fill(null)
        .map(() => Array(GRID_SIZE).fill(null))
    );
  };

  const handleSelectTemplate = (templateId: string) => {
    const newGrid = Array(GRID_SIZE)
      .fill(null)
      .map(() => Array(GRID_SIZE).fill(null));

    if (templateId === "mcu") {
      // Simple MCU template
      newGrid[3][3] = blockTypes[0]; // Compute
      newGrid[3][4] = blockTypes[1]; // Memory
      newGrid[4][3] = blockTypes[2]; // Logic
      newGrid[4][4] = blockTypes[3]; // I/O
    } else if (templateId === "ai-edge") {
      // AI Edge template
      newGrid[2][3] = blockTypes[6]; // AI
      newGrid[2][4] = blockTypes[6]; // AI
      newGrid[3][2] = blockTypes[1]; // Memory
      newGrid[3][5] = blockTypes[1]; // Memory
      newGrid[4][3] = blockTypes[0]; // Compute
      newGrid[4][4] = blockTypes[0]; // Compute
    } else if (templateId === "memory-heavy") {
      // Memory intensive
      for (let i = 2; i < 6; i++) {
        for (let j = 2; j < 6; j++) {
          newGrid[i][j] = blockTypes[1]; // Memory
        }
      }
      newGrid[3][3] = blockTypes[0]; // Compute center
    } else if (templateId === "balanced") {
      // Balanced SoC
      newGrid[2][2] = blockTypes[0];
      newGrid[2][5] = blockTypes[0];
      newGrid[5][2] = blockTypes[0];
      newGrid[5][5] = blockTypes[0];
      newGrid[3][3] = blockTypes[1];
      newGrid[3][4] = blockTypes[1];
      newGrid[4][3] = blockTypes[1];
      newGrid[4][4] = blockTypes[1];
      newGrid[2][3] = blockTypes[6];
      newGrid[3][2] = blockTypes[3];
      newGrid[4][5] = blockTypes[3];
      newGrid[5][4] = blockTypes[3];
    }

    setGrid(newGrid);
  };

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
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Box className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold">Voxel Chip Lab</h1>
              <p className="text-sm text-gray-500">Build chips like building blocks</p>
            </div>
          </div>

          <p className="text-lg text-gray-300 max-w-3xl">
            Design chips visually by placing blocks. Each color represents a different component. 
            Watch your design statistics update in real-time. No prior experience needed.
          </p>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <VoxelGrid
              grid={grid}
              selectedBlock={selectedBlock}
              onPlaceBlock={handlePlaceBlock}
              onDeleteBlock={handleDeleteBlock}
            />
          </div>
          <div className="space-y-6">
            <BlockPalette
              selectedBlock={selectedBlock}
              onSelectBlock={setSelectedBlock}
            />
            <TemplateGallery onSelectTemplate={handleSelectTemplate} />
          </div>
        </div>

        {/* Statistics and Learning */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <DesignStats grid={grid} />
          <VisualLearningMode />
        </div>

        {/* Action Bar */}
        <div className="bg-dark-800/60 rounded-2xl p-6 border border-dark-600">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <Settings className="w-5 h-5 text-green-400" />
              Design Actions
            </h3>
            <Link
              href="/ternaryair/manufacturing"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm transition-colors"
            >
              Export for Manufacturing <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleClearGrid}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600/20 hover:bg-red-600/30 text-red-400 text-sm border border-red-500/30"
            >
              <Trash2 className="w-4 h-4" />
              Clear Canvas
            </button>
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-300 text-sm border border-dark-500">
              <Copy className="w-4 h-4" />
              Duplicate
            </button>
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-300 text-sm border border-dark-500">
              <Download className="w-4 h-4" />
              Export PNG
            </button>
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-300 text-sm border border-dark-500">
              <Binary className="w-4 h-4" />
              Generate Verilog
            </button>
            <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-300 text-sm border border-dark-500">
              <Share2 className="w-4 h-4" />
              Share Design
            </button>
          </div>
        </div>

        {/* Wordless Visual Guide */}
        <div className="mt-8 bg-gradient-to-r from-purple-900/30 via-dark-800 to-pink-900/30 rounded-2xl p-8 border border-purple-500/20">
          <h3 className="text-xl font-bold mb-6 text-center">How It Works</h3>
          <div className="flex flex-wrap justify-center items-center gap-8">
            <div className="flex flex-col items-center">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded bg-dark-700 border border-dashed border-gray-500" />
                <span className="text-2xl">→</span>
                <div className="w-8 h-8 rounded bg-green-500" />
              </div>
              <span className="text-xs text-gray-400">Click to place</span>
            </div>
            <div className="flex flex-col items-center">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded bg-green-500" />
                <span className="text-2xl">→</span>
                <div className="w-8 h-8 rounded bg-dark-700 border border-dashed border-gray-500" />
              </div>
              <span className="text-xs text-gray-400">Click to remove</span>
            </div>
            <div className="flex flex-col items-center">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded bg-green-500" />
                <div className="w-8 h-8 rounded bg-purple-500" />
                <div className="w-8 h-8 rounded bg-blue-500" />
              </div>
              <span className="text-xs text-gray-400">Different types</span>
            </div>
            <div className="flex flex-col items-center">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded bg-dark-600 flex items-center justify-center text-xs text-green-400">
                  5W
                </div>
                <span className="text-2xl">=</span>
                <div className="w-8 h-8 rounded bg-amber-500/50 flex items-center justify-center text-xs">
                  ⚡
                </div>
              </div>
              <span className="text-xs text-gray-400">Power budget</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
