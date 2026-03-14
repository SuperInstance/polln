"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Head from "next/head";
import Link from "next/link";
import {
  Table,
  Brain,
  Sparkles,
  Play,
  Pause,
  Settings,
  Layers,
  Network,
  Zap,
  Target,
  Lightbulb,
  Code,
  Eye,
  GitBranch,
  Cpu,
  Database,
  ArrowRight,
  Plus,
  Minus,
  RefreshCw,
  Copy,
  Download,
  Upload,
  Trash2,
  Edit3,
  CheckCircle,
  AlertCircle,
  Info,
  BookOpen,
  GraduationCap,
  Bot,
  Box,
  Workflow,
  SquareStack,
  BoxSelect,
  Calculator,
  TrendingUp,
  PieChart,
  BarChart3,
  LineChart,
  Activity,
  Grid3X3,
  MousePointer,
  Move,
  Link2,
  X,
  ChevronRight,
  ChevronDown,
  Search,
  Filter,
  SortAsc,
  Maximize2,
  Minimize2,
  RotateCcw,
  FastForward,
  Rewind,
  Volume2,
  VolumeX,
  Sun,
  Moon,
  Monitor,
  Save,
  FileCode,
  FileSpreadsheet,
  Binary,
  Hash,
  Type,
  ToggleLeft,
  ToggleRight,
  Shuffle,
  Repeat,
  Split,
  Merge,
  Wand2,
  Magic,
  Atom,
  CircleDot,
  Signal,
  Radio,
  Radar,
} from "lucide-react";

// ============================================================================
// CELL-BASED AI BUILDER - COMPREHENSIVE SPREADSHEET AI PLATFORM
// ============================================================================

// Cell Types for the Spreadsheet AI
type CellType = 
  | "input" 
  | "hidden" 
  | "output" 
  | "formula" 
  | "neuron" 
  | "weight" 
  | "bias"
  | "activation"
  | "loss"
  | "gradient"
  | "data"
  | "code";

interface Cell {
  id: string;
  row: number;
  col: number;
  type: CellType;
  value: string | number;
  formula?: string;
  dependencies?: string[];
  computed?: number;
  active?: boolean;
  error?: string;
  gradient?: number;
  weight?: number;
  bias?: number;
}

interface NeuralLayer {
  id: string;
  name: string;
  type: "input" | "hidden" | "output";
  cells: string[];
  activation: "relu" | "sigmoid" | "tanh" | "softmax" | "linear";
}

interface AIFunction {
  name: string;
  category: string;
  syntax: string;
  description: string;
  example: string;
  complexity: "basic" | "intermediate" | "advanced";
}

// AI Functions available in the spreadsheet
const AI_FUNCTIONS: AIFunction[] = [
  // Basic Neural Operations
  {
    name: "NEURON",
    category: "Neural",
    syntax: "=NEURON(inputs, weights, bias)",
    description: "Computes a single neuron output: σ(Σ(wi*xi) + b)",
    example: "=NEURON(A1:A4, B1:B4, C1)",
    complexity: "basic",
  },
  {
    name: "RELU",
    category: "Activation",
    syntax: "=RELU(value)",
    description: "Rectified Linear Unit: max(0, x)",
    example: "=RELU(A1)",
    complexity: "basic",
  },
  {
    name: "SIGMOID",
    category: "Activation",
    syntax: "=SIGMOID(value)",
    description: "Sigmoid activation: 1 / (1 + e^(-x))",
    example: "=SIGMOID(A1)",
    complexity: "basic",
  },
  {
    name: "TANH",
    category: "Activation",
    syntax: "=TANH(value)",
    description: "Hyperbolic tangent activation",
    example: "=TANH(A1)",
    complexity: "basic",
  },
  {
    name: "SOFTMAX",
    category: "Activation",
    syntax: "=SOFTMAX(range)",
    description: "Softmax probability distribution over range",
    example: "=SOFTMAX(A1:A10)",
    complexity: "intermediate",
  },
  // Layer Operations
  {
    name: "DENSE",
    category: "Layers",
    syntax: "=DENSE(inputs, weights_matrix, bias_vector)",
    description: "Dense (fully connected) layer computation",
    example: "=DENSE(A1:A10, B1:K10, L1:L10)",
    complexity: "intermediate",
  },
  {
    name: "CONV2D",
    category: "Layers",
    syntax: "=CONV2D(input_range, kernel_range, stride)",
    description: "2D convolution operation for image data",
    example: "=CONV2D(A1:E5, F1:H3, 1)",
    complexity: "advanced",
  },
  {
    name: "POOL",
    category: "Layers",
    syntax: "=POOL(input_range, size, type)",
    description: "Pooling operation (max or average)",
    example: "=POOL(A1:E5, 2, 'max')",
    complexity: "intermediate",
  },
  // Loss Functions
  {
    name: "MSE",
    category: "Loss",
    syntax: "=MSE(predictions, targets)",
    description: "Mean Squared Error loss",
    example: "=MSE(A1:A10, B1:B10)",
    complexity: "basic",
  },
  {
    name: "CROSSENTROPY",
    category: "Loss",
    syntax: "=CROSSENTROPY(predictions, targets)",
    description: "Cross-entropy loss for classification",
    example: "=CROSSENTROPY(A1:A10, B1:B10)",
    complexity: "intermediate",
  },
  // Training Operations
  {
    name: "GRADIENT",
    category: "Training",
    syntax: "=GRADIENT(loss_cell, weight_cell)",
    description: "Computes gradient of loss w.r.t. weight",
    example: "=GRADIENT(Z1, B5)",
    complexity: "advanced",
  },
  {
    name: "BACKPROP",
    category: "Training",
    syntax: "=BACKPROP(loss_cell, layer_range)",
    description: "Backpropagation through a layer",
    example: "=BACKPROP(Z1, A1:M10)",
    complexity: "advanced",
  },
  {
    name: "SGD_STEP",
    category: "Training",
    syntax: "=SGD_STEP(weight, gradient, learning_rate)",
    description: "Stochastic Gradient Descent update step",
    example: "=SGD_STEP(B5, C5, 0.01)",
    complexity: "intermediate",
  },
  // Attention Mechanisms
  {
    name: "ATTENTION",
    category: "Attention",
    syntax: "=ATTENTION(Q, K, V)",
    description: "Scaled dot-product attention mechanism",
    example: "=ATTENTION(A1:D4, E1:H4, I1:L4)",
    complexity: "advanced",
  },
  {
    name: "SELF_ATTENTION",
    category: "Attention",
    syntax: "=SELF_ATTENTION(input_range, heads)",
    description: "Multi-head self-attention layer",
    example: "=SELF_ATTENTION(A1:D10, 4)",
    complexity: "advanced",
  },
  // Data Processing
  {
    name: "EMBED",
    category: "Data",
    syntax: "=EMBED(text, dimension)",
    description: "Generate embedding vector for text",
    example: '=EMBED("hello world", 128)',
    complexity: "intermediate",
  },
  {
    name: "TOKENIZE",
    category: "Data",
    syntax: "=TOKENIZE(text, vocab_size)",
    description: "Tokenize text into token IDs",
    example: '=TOKENIZE(A1, 32000)',
    complexity: "intermediate",
  },
  // Quantization (for Mask-Locked Chips)
  {
    name: "TERNARY",
    category: "Quantize",
    syntax: "=TERNARY(value)",
    description: "Convert to ternary {-1, 0, +1} (BitNet)",
    example: "=TERNARY(A1)",
    complexity: "intermediate",
  },
  {
    name: "INT4",
    category: "Quantize",
    syntax: "=INT4(value)",
    description: "Quantize to 4-bit integer [-8, +7]",
    example: "=INT4(A1)",
    complexity: "basic",
  },
  {
    name: "DEQUANTIZE",
    category: "Quantize",
    syntax: "=DEQUANTIZE(quantized, scale, zero_point)",
    description: "Dequantize back to floating point",
    example: "=DEQUANTIZE(A1, 0.1, 0)",
    complexity: "basic",
  },
];

// Learning Modules
const LEARNING_MODULES = [
  {
    id: "intro-neurons",
    title: "Introduction to Neurons",
    description: "Learn how individual neurons process information",
    age: "5-10",
    difficulty: "Beginner",
    icon: Lightbulb,
    lessons: 5,
    duration: "15 min",
    topics: ["What is a neuron?", "Inputs and outputs", "Simple calculations"],
  },
  {
    id: "cell-formulas",
    title: "AI Formulas in Cells",
    description: "Write your first AI formula in a spreadsheet cell",
    age: "11-14",
    difficulty: "Beginner",
    icon: Code,
    lessons: 8,
    duration: "25 min",
    topics: ["Formula syntax", "Cell references", "Neural functions"],
  },
  {
    id: "build-network",
    title: "Build a Neural Network",
    description: "Connect cells to create a working neural network",
    age: "15-18",
    difficulty: "Intermediate",
    icon: Network,
    lessons: 12,
    duration: "45 min",
    topics: ["Layer design", "Forward pass", "Activation functions"],
  },
  {
    id: "train-model",
    title: "Train Your Model",
    description: "Implement backpropagation in cells",
    age: "18+",
    difficulty: "Advanced",
    icon: Target,
    lessons: 15,
    duration: "60 min",
    topics: ["Gradient descent", "Loss functions", "Weight updates"],
  },
  {
    id: "attention-transformer",
    title: "Attention & Transformers",
    description: "Build attention mechanisms with cell formulas",
    age: "18+",
    difficulty: "Advanced",
    icon: Eye,
    lessons: 10,
    duration: "50 min",
    topics: ["Self-attention", "Multi-head attention", "Transformer blocks"],
  },
  {
    id: "quantization-chips",
    title: "Quantization for Chips",
    description: "Prepare models for mask-locked inference",
    age: "Professional",
    difficulty: "Expert",
    icon: Cpu,
    lessons: 8,
    duration: "40 min",
    topics: ["Ternary weights", "INT4 quantization", "Hardware mapping"],
  },
];

// Example Networks
const EXAMPLE_NETWORKS = [
  {
    id: "simple-perceptron",
    name: "Simple Perceptron",
    description: "Single neuron with 2 inputs",
    cells: [
      { id: "A1", row: 0, col: 0, type: "input" as CellType, value: 0.5 },
      { id: "A2", row: 1, col: 0, type: "input" as CellType, value: 0.3 },
      { id: "B1", row: 0, col: 1, type: "weight" as CellType, value: 0.8 },
      { id: "B2", row: 1, col: 1, type: "weight" as CellType, value: -0.2 },
      { id: "C1", row: 0, col: 2, type: "bias" as CellType, value: 0.1 },
      { id: "D1", row: 0, col: 3, type: "neuron" as CellType, value: "", formula: "=NEURON(A1:A2,B1:B2,C1)" },
    ],
  },
  {
    id: "xor-network",
    name: "XOR Network",
    description: "2-layer network to solve XOR problem",
    cells: [],
  },
  {
    id: "image-classifier",
    name: "Simple Image Classifier",
    description: "Small CNN for digit recognition",
    cells: [],
  },
];

// ============================================================================
// COMPONENT: Spreadsheet Grid
// ============================================================================
interface SpreadsheetGridProps {
  cells: Map<string, Cell>;
  selectedCell: string | null;
  onSelectCell: (id: string | null) => void;
  onUpdateCell: (id: string, updates: Partial<Cell>) => void;
  rows: number;
  cols: number;
  showGradients: boolean;
  animationPhase: number;
}

function SpreadsheetGrid({
  cells,
  selectedCell,
  onSelectCell,
  onUpdateCell,
  rows,
  cols,
  showGradients,
  animationPhase,
}: SpreadsheetGridProps) {
  const colLabels = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

  const getCellColor = (cell: Cell | undefined) => {
    if (!cell) return "bg-muted/30";
    switch (cell.type) {
      case "input":
        return "bg-blue-500/20 border-blue-500/50";
      case "hidden":
        return "bg-purple-500/20 border-purple-500/50";
      case "output":
        return "bg-green-500/20 border-green-500/50";
      case "neuron":
        return "bg-cyan-500/20 border-cyan-500/50";
      case "weight":
        return "bg-amber-500/20 border-amber-500/50";
      case "bias":
        return "bg-orange-500/20 border-orange-500/50";
      case "activation":
        return "bg-pink-500/20 border-pink-500/50";
      case "loss":
        return "bg-red-500/20 border-red-500/50";
      case "gradient":
        return "bg-rose-500/20 border-rose-500/50";
      case "formula":
        return "bg-emerald-500/20 border-emerald-500/50";
      default:
        return "bg-card";
    }
  };

  const getCellIcon = (cell: Cell | undefined) => {
    if (!cell) return null;
    switch (cell.type) {
      case "input":
        return <Database className="w-3 h-3 text-blue-400" />;
      case "neuron":
        return <Brain className="w-3 h-3 text-cyan-400" />;
      case "weight":
        return <Hash className="w-3 h-3 text-amber-400" />;
      case "bias":
        return <Plus className="w-3 h-3 text-orange-400" />;
      case "activation":
        return <Zap className="w-3 h-3 text-pink-400" />;
      case "output":
        return <Target className="w-3 h-3 text-green-400" />;
      default:
        return null;
    }
  };

  return (
    <div className="overflow-auto rounded-xl border border-border bg-card">
      <table className="border-collapse">
        <thead>
          <tr>
            <th className="sticky left-0 z-10 bg-muted/50 border border-border p-2 min-w-[60px] text-xs font-medium text-muted-foreground">
              <Grid3X3 className="w-4 h-4 mx-auto" />
            </th>
            {Array.from({ length: cols }).map((_, col) => (
              <th
                key={col}
                className="bg-muted/50 border border-border p-2 min-w-[100px] text-xs font-medium text-muted-foreground"
              >
                {colLabels[col]}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, row) => (
            <tr key={row}>
              <td className="sticky left-0 z-10 bg-muted/50 border border-border p-2 text-xs font-medium text-muted-foreground text-center">
                {row + 1}
              </td>
              {Array.from({ length: cols }).map((_, col) => {
                const cellId = `${colLabels[col]}${row + 1}`;
                const cell = cells.get(cellId);
                const isSelected = selectedCell === cellId;

                return (
                  <td
                    key={cellId}
                    className={`border border-border p-0 relative ${
                      isSelected ? "ring-2 ring-primary ring-inset" : ""
                    }`}
                  >
                    <div
                      className={`min-h-[40px] p-2 cursor-pointer transition-all ${getCellColor(cell)}`}
                      onClick={() => onSelectCell(cellId)}
                    >
                      {/* Cell icon indicator */}
                      <div className="absolute top-1 right-1 opacity-50">
                        {getCellIcon(cell)}
                      </div>

                      {/* Cell value display */}
                      <div className="text-sm font-mono truncate">
                        {cell?.formula ? (
                          <span className="text-emerald-400">
                            {cell.computed !== undefined
                              ? cell.computed.toFixed(4)
                              : cell.formula}
                          </span>
                        ) : cell?.value !== undefined ? (
                          <span>{cell.value}</span>
                        ) : (
                          <span className="text-muted-foreground/30">empty</span>
                        )}
                      </div>

                      {/* Gradient visualization */}
                      {showGradients && cell?.gradient !== undefined && (
                        <motion.div
                          className="absolute bottom-0 left-0 h-1 bg-rose-500"
                          initial={{ width: 0 }}
                          animate={{
                            width: `${Math.min(Math.abs(cell.gradient) * 100, 100)}%`,
                          }}
                          transition={{ duration: 0.5 }}
                        />
                      )}

                      {/* Data flow animation */}
                      {cell?.active && (
                        <motion.div
                          className="absolute inset-0 bg-primary/20"
                          animate={{ opacity: [0, 0.5, 0] }}
                          transition={{ duration: 0.5, repeat: Infinity }}
                        />
                      )}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ============================================================================
// COMPONENT: Network Visualizer
// ============================================================================
interface NetworkVisualizerProps {
  cells: Map<string, Cell>;
  animationPhase: number;
}

function NetworkVisualizer({ cells, animationPhase }: NetworkVisualizerProps) {
  // Group cells by type for visualization
  const layers = useMemo(() => {
    const inputCells: Cell[] = [];
    const hiddenCells: Cell[] = [];
    const outputCells: Cell[] = [];

    cells.forEach((cell) => {
      if (cell.type === "input") inputCells.push(cell);
      else if (cell.type === "output") outputCells.push(cell);
      else if (cell.type === "neuron" || cell.type === "hidden") hiddenCells.push(cell);
    });

    return { input: inputCells, hidden: hiddenCells, output: outputCells };
  }, [cells]);

  return (
    <div className="relative h-64 bg-black/20 rounded-xl overflow-hidden">
      <svg className="absolute inset-0 w-full h-full">
        {/* Draw connections */}
        {layers.input.map((input, i) =>
          layers.hidden.map((hidden, j) => (
            <motion.line
              key={`conn-${i}-${j}`}
              x1={50}
              y1={30 + i * 50}
              x2={150}
              y2={20 + j * 40}
              stroke="rgba(16, 185, 129, 0.3)"
              strokeWidth={1}
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.5, delay: (i + j) * 0.1 }}
            />
          ))
        )}

        {/* Data flow particles */}
        {animationPhase > 0 &&
          layers.input.map((_, i) => (
            <motion.circle
              key={`particle-${i}`}
              r={3}
              fill="#10b981"
              initial={{ cx: 50, cy: 30 + i * 50 }}
              animate={{
                cx: [50, 150, 250],
                cy: [30 + i * 50, 50, 80],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.3,
              }}
            />
          ))}
      </svg>

      {/* Input Layer */}
      <div className="absolute left-4 top-1/2 -translate-y-1/2 flex flex-col gap-4">
        {layers.input.map((cell, i) => (
          <motion.div
            key={cell.id}
            className="w-12 h-12 rounded-full bg-blue-500/30 border-2 border-blue-500 flex items-center justify-center"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: i * 0.1 }}
          >
            <Database className="w-5 h-5 text-blue-400" />
          </motion.div>
        ))}
      </div>

      {/* Hidden Layer */}
      <div className="absolute left-1/3 top-1/2 -translate-y-1/2 flex flex-col gap-3">
        {layers.hidden.map((cell, i) => (
          <motion.div
            key={cell.id}
            className="w-10 h-10 rounded-full bg-purple-500/30 border-2 border-purple-500 flex items-center justify-center"
            animate={{
              scale: animationPhase > 0 ? [1, 1.2, 1] : 1,
            }}
            transition={{
              duration: 0.5,
              repeat: animationPhase > 0 ? Infinity : 0,
            }}
          >
            <Brain className="w-4 h-4 text-purple-400" />
          </motion.div>
        ))}
      </div>

      {/* Output Layer */}
      <div className="absolute right-4 top-1/2 -translate-y-1/2 flex flex-col gap-6">
        {layers.output.map((cell, i) => (
          <motion.div
            key={cell.id}
            className="w-14 h-14 rounded-full bg-green-500/30 border-2 border-green-500 flex items-center justify-center"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5 + i * 0.1 }}
          >
            <Target className="w-6 h-6 text-green-400" />
          </motion.div>
        ))}
      </div>

      {/* Layer Labels */}
      <div className="absolute bottom-2 left-0 right-0 flex justify-around text-xs text-muted-foreground">
        <span>Input</span>
        <span>Hidden</span>
        <span>Output</span>
      </div>
    </div>
  );
}

// ============================================================================
// COMPONENT: Formula Bar
// ============================================================================
interface FormulaBarProps {
  selectedCell: string | null;
  cell: Cell | undefined;
  onUpdateFormula: (formula: string) => void;
  onUpdateValue: (value: string) => void;
  onChangeType: (type: CellType) => void;
}

function FormulaBar({
  selectedCell,
  cell,
  onUpdateFormula,
  onUpdateValue,
  onChangeType,
}: FormulaBarProps) {
  const [editMode, setEditMode] = useState<"value" | "formula">("value");

  if (!selectedCell) {
    return (
      <div className="bg-card border border-border rounded-lg p-3 text-muted-foreground text-sm">
        Select a cell to edit its value or formula
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-lg p-3 space-y-3">
      {/* Cell Reference */}
      <div className="flex items-center gap-3">
        <div className="bg-primary/10 px-3 py-1 rounded font-mono font-bold text-primary">
          {selectedCell}
        </div>
        <div className="flex gap-2 flex-wrap">
          {(
            [
              "input",
              "neuron",
              "weight",
              "bias",
              "activation",
              "output",
            ] as CellType[]
          ).map((type) => (
            <button
              key={type}
              onClick={() => onChangeType(type)}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                cell?.type === type
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted hover:bg-muted/80"
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Value Input */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground w-16">Value:</span>
        <input
          type="text"
          value={(cell?.value as string) || ""}
          onChange={(e) => onUpdateValue(e.target.value)}
          className="flex-1 bg-background border border-border rounded px-3 py-2 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="Enter value..."
        />
      </div>

      {/* Formula Input */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground w-16">Formula:</span>
        <div className="flex-1 flex items-center gap-2">
          <span className="text-emerald-400 font-bold">fx</span>
          <input
            type="text"
            value={cell?.formula || ""}
            onChange={(e) => onUpdateFormula(e.target.value)}
            className="flex-1 bg-background border border-border rounded px-3 py-2 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            placeholder="=NEURON(A1:A4, B1:B4, C1)"
          />
        </div>
      </div>

      {/* Computed Value */}
      {cell?.computed !== undefined && (
        <div className="flex items-center gap-2 text-sm">
          <span className="text-muted-foreground">Computed:</span>
          <span className="font-mono text-cyan-400">
            {cell.computed.toFixed(6)}
          </span>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// COMPONENT: AI Function Reference
// ============================================================================
interface FunctionReferenceProps {
  searchTerm: string;
  onSelectFunction: (fn: AIFunction) => void;
}

function FunctionReference({ searchTerm, onSelectFunction }: FunctionReferenceProps) {
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);

  const filteredFunctions = AI_FUNCTIONS.filter(
    (fn) =>
      fn.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      fn.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const categories = [...new Set(filteredFunctions.map((fn) => fn.category))];

  return (
    <div className="space-y-2">
      {categories.map((category) => (
        <div key={category} className="border border-border rounded-lg overflow-hidden">
          <button
            onClick={() =>
              setExpandedCategory(expandedCategory === category ? null : category)
            }
            className="w-full flex items-center justify-between p-3 bg-muted/30 hover:bg-muted/50 transition-colors"
          >
            <span className="font-medium">{category}</span>
            {expandedCategory === category ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </button>

          {expandedCategory === category && (
            <div className="p-2 space-y-2">
              {filteredFunctions
                .filter((fn) => fn.category === category)
                .map((fn) => (
                  <div
                    key={fn.name}
                    onClick={() => onSelectFunction(fn)}
                    className="p-3 bg-card hover:bg-muted/30 rounded-lg cursor-pointer transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <code className="text-emerald-400 font-mono">{fn.name}</code>
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${
                          fn.complexity === "basic"
                            ? "bg-green-500/10 text-green-400"
                            : fn.complexity === "intermediate"
                            ? "bg-amber-500/10 text-amber-400"
                            : "bg-purple-500/10 text-purple-400"
                        }`}
                      >
                        {fn.complexity}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {fn.description}
                    </p>
                    <code className="text-xs bg-muted p-1 rounded block">
                      {fn.example}
                    </code>
                  </div>
                ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ============================================================================
// COMPONENT: Learning Module Card
// ============================================================================
function LearningModuleCard({
  module,
  index,
}: {
  module: (typeof LEARNING_MODULES)[0];
  index: number;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-card rounded-2xl border border-border overflow-hidden"
    >
      <div
        className="p-4 cursor-pointer hover:bg-muted/30 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                module.difficulty === "Beginner"
                  ? "bg-green-500/10"
                  : module.difficulty === "Intermediate"
                  ? "bg-amber-500/10"
                  : module.difficulty === "Advanced"
                  ? "bg-purple-500/10"
                  : "bg-rose-500/10"
              }`}
            >
              <module.icon
                className={`w-6 h-6 ${
                  module.difficulty === "Beginner"
                    ? "text-green-400"
                    : module.difficulty === "Intermediate"
                    ? "text-amber-400"
                    : module.difficulty === "Advanced"
                    ? "text-purple-400"
                    : "text-rose-400"
                }`}
              />
            </div>
            <div>
              <h3 className="font-semibold">{module.title}</h3>
              <p className="text-sm text-muted-foreground">{module.description}</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-muted-foreground">{module.age}</div>
            <div className="text-xs text-muted-foreground">{module.duration}</div>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-2 border-t border-border">
              <div className="flex flex-wrap gap-2 mb-3">
                {module.topics.map((topic) => (
                  <span
                    key={topic}
                    className="text-xs px-2 py-1 bg-muted rounded"
                  >
                    {topic}
                  </span>
                ))}
              </div>
              <button className="w-full py-2 bg-primary/10 text-primary rounded-lg font-medium hover:bg-primary/20 transition-colors">
                Start Module ({module.lessons} lessons)
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ============================================================================
// MAIN PAGE COMPONENT
// ============================================================================
export default function CellBuilderPage() {
  // Initial cells value - using useMemo for initialization
  const initialCells = useMemo(() => {
    const cells = new Map<string, Cell>();
    // Add some example cells
    cells.set("A1", {
      id: "A1",
      row: 0,
      col: 0,
      type: "input",
      value: 0.5,
    });
    cells.set("A2", {
      id: "A2",
      row: 1,
      col: 0,
      type: "input",
      value: 0.8,
    });
    cells.set("B1", {
      id: "B1",
      row: 0,
      col: 1,
      type: "weight",
      value: 0.7,
    });
    cells.set("B2", {
      id: "B2",
      row: 1,
      col: 1,
      type: "weight",
      value: -0.3,
    });
    cells.set("C1", {
      id: "C1",
      row: 0,
      col: 2,
      type: "bias",
      value: 0.1,
    });
    cells.set("D1", {
      id: "D1",
      row: 0,
      col: 3,
      type: "neuron",
      value: "",
      formula: "=NEURON(A1:A2,B1:B2,C1)",
      computed: 0.5 * 0.7 + 0.8 * -0.3 + 0.1,
    });
    return cells;
  }, []);

  // Initialize state with initial cells
  const [cells, setCells] = useState<Map<string, Cell>>(initialCells);
  const [selectedCell, setSelectedCell] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [animationPhase, setAnimationPhase] = useState(0);
  const [showGradients, setShowGradients] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState<"spreadsheet" | "visual" | "learn">("spreadsheet");
  const [rows, setRows] = useState(10);
  const [cols, setCols] = useState(8);

  // Handlers
  const handleSelectCell = useCallback((id: string | null) => {
    setSelectedCell(id);
  }, []);

  const handleUpdateCell = useCallback(
    (id: string, updates: Partial<Cell>) => {
      setCells((prev) => {
        const newCells = new Map(prev);
        const existing = newCells.get(id) || {
          id,
          row: parseInt(id.slice(1)) - 1,
          col: id.charCodeAt(0) - 65,
          type: "input" as CellType,
          value: "",
        };
        newCells.set(id, { ...existing, ...updates });
        return newCells;
      });
    },
    []
  );

  const handleUpdateFormula = useCallback(
    (formula: string) => {
      if (!selectedCell) return;
      handleUpdateCell(selectedCell, { formula, type: "formula" });
    },
    [selectedCell, handleUpdateCell]
  );

  const handleUpdateValue = useCallback(
    (value: string) => {
      if (!selectedCell) return;
      const numValue = parseFloat(value);
      handleUpdateCell(selectedCell, {
        value: isNaN(numValue) ? value : numValue,
      });
    },
    [selectedCell, handleUpdateCell]
  );

  const handleChangeType = useCallback(
    (type: CellType) => {
      if (!selectedCell) return;
      handleUpdateCell(selectedCell, { type });
    },
    [selectedCell, handleUpdateCell]
  );

  const handleSelectFunction = useCallback((fn: AIFunction) => {
    if (selectedCell) {
      handleUpdateCell(selectedCell, {
        formula: fn.example,
        type: "formula",
      });
    }
  }, [selectedCell, handleUpdateCell]);

  const handleRun = useCallback(() => {
    setIsRunning(true);
    setAnimationPhase(1);

    // Simulate forward pass
    setTimeout(() => {
      setAnimationPhase(2);
    }, 1000);

    setTimeout(() => {
      setAnimationPhase(3);
      setIsRunning(false);
    }, 2000);
  }, []);

  const handleReset = useCallback(() => {
    setAnimationPhase(0);
    setIsRunning(false);
  }, []);

  const selectedCellData = selectedCell ? cells.get(selectedCell) : undefined;

  return (
    <>
      <Head>
        <title>Cell-Based AI Builder | Lucineer - Spreadsheet AI Platform</title>
        <meta
          name="description"
          content="Build AI models in a spreadsheet. Write neural network formulas in cells, visualize data flow, and learn AI from basics to advanced."
        />
        <meta
          name="keywords"
          content="spreadsheet AI, neural network builder, cell-based AI, visual programming, AI education, formula-based AI"
        />
        <meta property="og:type" content="website" />
        <meta property="og:title" content="Cell-Based AI Builder - Spreadsheet AI Platform" />
        <meta
          property="og:description"
          content="Build neural networks with spreadsheet formulas. Visual programming for AI."
        />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-background via-background to-cyan-500/5">
        {/* Hero Section */}
        <section className="py-12 px-4 sm:px-6 lg:px-8 border-b border-border">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div>
                <div className="inline-flex items-center gap-2 bg-cyan-500/10 border border-cyan-500/30 rounded-full px-4 py-2 mb-4">
                  <Table className="w-4 h-4 text-cyan-400" />
                  <span className="text-cyan-400 text-sm font-medium">
                    Spreadsheet AI Platform
                  </span>
                </div>
                <h1 className="text-4xl sm:text-5xl font-bold mb-2">
                  <span className="bg-gradient-to-r from-cyan-400 via-emerald-400 to-purple-400 bg-clip-text text-transparent">
                    Cell-Based AI Builder
                  </span>
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl">
                  Build neural networks with spreadsheet formulas. Every cell can be a neuron,
                  every formula a computation. Visual programming meets AI.
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleRun}
                  disabled={isRunning}
                  className="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-white rounded-lg font-medium hover:bg-emerald-600 transition-colors disabled:opacity-50"
                >
                  {isRunning ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      Run Network
                    </>
                  )}
                </button>
                <button
                  onClick={handleReset}
                  className="flex items-center gap-2 px-4 py-2 bg-muted hover:bg-muted/80 rounded-lg font-medium transition-colors"
                >
                  <RotateCcw className="w-4 h-4" />
                  Reset
                </button>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Main Content */}
        <section className="py-6 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            {/* Tab Navigation */}
            <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
              {[
                { id: "spreadsheet", label: "Spreadsheet", icon: Table },
                { id: "visual", label: "Network Visual", icon: Network },
                { id: "learn", label: "Learn AI", icon: GraduationCap },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${
                    activeTab === tab.id
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted hover:bg-muted/80"
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Spreadsheet View */}
            {activeTab === "spreadsheet" && (
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Main Spreadsheet */}
                <div className="lg:col-span-3 space-y-4">
                  {/* Formula Bar */}
                  <FormulaBar
                    selectedCell={selectedCell}
                    cell={selectedCellData}
                    onUpdateFormula={handleUpdateFormula}
                    onUpdateValue={handleUpdateValue}
                    onChangeType={handleChangeType}
                  />

                  {/* Toolbar */}
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex gap-2 flex-wrap">
                      <button
                        onClick={() => setShowGradients(!showGradients)}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition-colors ${
                          showGradients
                            ? "bg-rose-500/10 text-rose-400"
                            : "bg-muted hover:bg-muted/80"
                        }`}
                      >
                        <Signal className="w-4 h-4" />
                        Show Gradients
                      </button>
                      <button className="flex items-center gap-2 px-3 py-1.5 bg-muted hover:bg-muted/80 rounded text-sm transition-colors">
                        <Plus className="w-4 h-4" />
                        Add Row
                      </button>
                      <button className="flex items-center gap-2 px-3 py-1.5 bg-muted hover:bg-muted/80 rounded text-sm transition-colors">
                        <Plus className="w-4 h-4" />
                        Add Column
                      </button>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-sm text-muted-foreground">
                        {cells.size} cells
                      </span>
                      <span className="text-sm text-muted-foreground">
                        Phase: {animationPhase}
                      </span>
                    </div>
                  </div>

                  {/* Spreadsheet Grid */}
                  <SpreadsheetGrid
                    cells={cells}
                    selectedCell={selectedCell}
                    onSelectCell={handleSelectCell}
                    onUpdateCell={handleUpdateCell}
                    rows={rows}
                    cols={cols}
                    showGradients={showGradients}
                    animationPhase={animationPhase}
                  />
                </div>

                {/* Sidebar: Function Reference */}
                <div className="space-y-4">
                  <div className="bg-card border border-border rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <BookOpen className="w-4 h-4 text-emerald-400" />
                      <h3 className="font-semibold">AI Functions</h3>
                    </div>
                    <div className="relative mb-3">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Search functions..."
                        className="w-full pl-9 pr-3 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                      />
                    </div>
                    <div className="max-h-[400px] overflow-y-auto">
                      <FunctionReference
                        searchTerm={searchTerm}
                        onSelectFunction={handleSelectFunction}
                      />
                    </div>
                  </div>

                  {/* Quick Stats */}
                  <div className="bg-card border border-border rounded-xl p-4">
                    <h3 className="font-semibold mb-3">Network Stats</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Input Cells</span>
                        <span className="font-mono">
                          {Array.from(cells.values()).filter((c) => c.type === "input").length}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Neurons</span>
                        <span className="font-mono">
                          {Array.from(cells.values()).filter((c) => c.type === "neuron").length}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Weights</span>
                        <span className="font-mono">
                          {Array.from(cells.values()).filter((c) => c.type === "weight").length}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Formulas</span>
                        <span className="font-mono">
                          {Array.from(cells.values()).filter((c) => c.formula).length}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Network Visual View */}
            {activeTab === "visual" && (
              <div className="space-y-6">
                <NetworkVisualizer cells={cells} animationPhase={animationPhase} />

                {/* Layer Configuration */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-card border border-border rounded-xl p-4">
                    <h3 className="font-semibold mb-3 flex items-center gap-2">
                      <Database className="w-4 h-4 text-blue-400" />
                      Input Layer
                    </h3>
                    <div className="space-y-2">
                      {Array.from(cells.values())
                        .filter((c) => c.type === "input")
                        .map((cell) => (
                          <div
                            key={cell.id}
                            className="flex items-center justify-between p-2 bg-blue-500/10 rounded"
                          >
                            <span className="font-mono text-sm">{cell.id}</span>
                            <span className="font-mono text-blue-400">
                              {cell.value}
                            </span>
                          </div>
                        ))}
                    </div>
                  </div>

                  <div className="bg-card border border-border rounded-xl p-4">
                    <h3 className="font-semibold mb-3 flex items-center gap-2">
                      <Brain className="w-4 h-4 text-purple-400" />
                      Hidden Layer
                    </h3>
                    <div className="space-y-2">
                      {Array.from(cells.values())
                        .filter((c) => c.type === "neuron" || c.type === "hidden")
                        .map((cell) => (
                          <div
                            key={cell.id}
                            className="flex items-center justify-between p-2 bg-purple-500/10 rounded"
                          >
                            <span className="font-mono text-sm">{cell.id}</span>
                            <span className="font-mono text-purple-400">
                              {cell.computed?.toFixed(4) || "—"}
                            </span>
                          </div>
                        ))}
                    </div>
                  </div>

                  <div className="bg-card border border-border rounded-xl p-4">
                    <h3 className="font-semibold mb-3 flex items-center gap-2">
                      <Target className="w-4 h-4 text-green-400" />
                      Output Layer
                    </h3>
                    <div className="space-y-2">
                      {Array.from(cells.values())
                        .filter((c) => c.type === "output")
                        .map((cell) => (
                          <div
                            key={cell.id}
                            className="flex items-center justify-between p-2 bg-green-500/10 rounded"
                          >
                            <span className="font-mono text-sm">{cell.id}</span>
                            <span className="font-mono text-green-400">
                              {cell.computed?.toFixed(4) || "—"}
                            </span>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Learn AI View */}
            {activeTab === "learn" && (
              <div className="space-y-8">
                {/* Age Group Filter */}
                <div className="flex flex-wrap gap-3">
                  {["5-10", "11-14", "15-18", "18+", "Professional"].map((age) => (
                    <button
                      key={age}
                      className="px-4 py-2 bg-muted hover:bg-muted/80 rounded-full text-sm font-medium transition-colors"
                    >
                      Ages {age}
                    </button>
                  ))}
                </div>

                {/* Module Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {LEARNING_MODULES.map((module, index) => (
                    <LearningModuleCard key={module.id} module={module} index={index} />
                  ))}
                </div>

                {/* Concept Explanation */}
                <div className="bg-gradient-to-r from-cyan-500/10 via-emerald-500/10 to-purple-500/10 rounded-2xl border border-cyan-500/20 p-8">
                  <h2 className="text-2xl font-bold mb-4">
                    How Cell-Based AI Works
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center mb-3">
                        <Database className="w-6 h-6 text-blue-400" />
                      </div>
                      <h3 className="font-semibold mb-2">1. Data in Cells</h3>
                      <p className="text-sm text-muted-foreground">
                        Every spreadsheet cell can hold data: numbers, text, or
                        even tensors. Input your data like a normal spreadsheet.
                      </p>
                    </div>
                    <div>
                      <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center mb-3">
                        <Code className="w-6 h-6 text-emerald-400" />
                      </div>
                      <h3 className="font-semibold mb-2">2. AI Formulas</h3>
                      <p className="text-sm text-muted-foreground">
                        Write AI functions in cells: =NEURON(), =RELU(),
                        =SOFTMAX(). Each formula computes part of the neural
                        network.
                      </p>
                    </div>
                    <div>
                      <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-3">
                        <Network className="w-6 h-6 text-purple-400" />
                      </div>
                      <h3 className="font-semibold mb-2">3. Visual Network</h3>
                      <p className="text-sm text-muted-foreground">
                        Watch your network compute in real-time. See data flow
                        through neurons, gradients propagate backward.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Feature Section */}
        <section className="py-12 px-4 sm:px-6 lg:px-8 bg-card/30">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Spreadsheet AI Capabilities
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                A complete toolkit for building, training, and deploying AI models
                using familiar spreadsheet concepts
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                {
                  icon: Brain,
                  title: "Neural Networks",
                  description:
                    "Build perceptrons, MLPs, CNNs, and transformers using cell formulas",
                  color: "text-purple-400",
                  bgColor: "bg-purple-500/10",
                },
                {
                  icon: Zap,
                  title: "Real-time Execution",
                  description:
                    "Watch your network compute live with animated data flow",
                  color: "text-amber-400",
                  bgColor: "bg-amber-500/10",
                },
                {
                  icon: Target,
                  title: "Training & Gradients",
                  description:
                    "Implement backpropagation with gradient formulas in cells",
                  color: "text-rose-400",
                  bgColor: "bg-rose-500/10",
                },
                {
                  icon: Cpu,
                  title: "Chip Export",
                  description:
                    "Export trained models to mask-locked inference chips",
                  color: "text-cyan-400",
                  bgColor: "bg-cyan-500/10",
                },
                {
                  icon: Eye,
                  title: "Attention Mechanisms",
                  description:
                    "Build self-attention and multi-head attention with formulas",
                  color: "text-emerald-400",
                  bgColor: "bg-emerald-500/10",
                },
                {
                  icon: Binary,
                  title: "Quantization",
                  description:
                    "Convert to ternary, INT4, INT8 for edge deployment",
                  color: "text-indigo-400",
                  bgColor: "bg-indigo-500/10",
                },
                {
                  icon: GraduationCap,
                  title: "AI Education",
                  description:
                    "Learn AI from basics to advanced with interactive modules",
                  color: "text-blue-400",
                  bgColor: "bg-blue-500/10",
                },
                {
                  icon: Bot,
                  title: "A2A Interface",
                  description:
                    "AI agents can read, modify, and learn from your networks",
                  color: "text-pink-400",
                  bgColor: "bg-pink-500/10",
                },
              ].map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-card rounded-2xl border border-border p-6"
                >
                  <div
                    className={`w-12 h-12 rounded-xl ${feature.bgColor} flex items-center justify-center mb-4`}
                  >
                    <feature.icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                  <h3 className="font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Start Building AI in Spreadsheets
              </h2>
              <p className="text-lg text-muted-foreground mb-8">
                From beginners learning what a neuron is, to engineers designing
                custom architectures, the Cell-Based AI Builder makes AI
                accessible to everyone.
              </p>
              <div className="flex flex-wrap justify-center gap-4">
                <Link
                  href="/math-universe"
                  className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-90 transition-opacity"
                >
                  <Box className="w-5 h-5" />
                  Explore Math Universe
                </Link>
                <Link
                  href="/professional"
                  className="flex items-center gap-2 px-6 py-3 bg-card border border-border rounded-xl font-medium hover:border-primary/50 transition-colors"
                >
                  <Cpu className="w-5 h-5" />
                  Design Chips
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </div>
    </>
  );
}
