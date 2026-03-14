"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Head from "next/head";
import Link from "next/link";
import Image from "next/image";
import {
  Box,
  Layers,
  GitBranch,
  Zap,
  Eye,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Play,
  Plus,
  ArrowRight,
  Database,
  Terminal,
  BookOpen,
  Sparkles,
  ChevronRight,
  TrendingUp,
  Activity,
} from "lucide-react";

// Tile Types
interface Tile {
  id: string;
  name: string;
  type: "input" | "process" | "output";
  confidence: number;
}

// Confidence Zone Colors
const getZoneInfo = (confidence: number) => {
  if (confidence >= 0.9) return { zone: "GREEN", color: "emerald", text: "text-emerald-400", bg: "bg-emerald-500/20" };
  if (confidence >= 0.75) return { zone: "YELLOW", color: "amber", text: "text-amber-400", bg: "bg-amber-500/20" };
  return { zone: "RED", color: "red", text: "text-red-400", bg: "bg-red-500/20" };
};

// Tile Intelligence Concepts
const tileConcepts = [
  {
    id: "tile-interface",
    title: "The Tile Interface",
    subtitle: "I, O, f, c, τ",
    icon: Box,
    color: "from-cyan-500 to-blue-600",
    image: "/download/assets/round1_tiles/tile_interface_diagram.png",
    description: "Every tile has five core operations: Input, Output, discriminate, confidence, and trace.",
    formulas: [
      { name: "Input", value: "I: any", meaning: "Data entering the tile" },
      { name: "Output", value: "O: any", meaning: "Processed result" },
      { name: "Discriminate", value: "f: I → O", meaning: "Core transformation" },
      { name: "Confidence", value: "c: I → [0,1]", meaning: "How sure is this tile?" },
      { name: "Trace", value: "τ: I → string", meaning: "Why did this happen?" },
    ],
    learnMore: "Tiles are the LEGO blocks of AI. Each tile does one thing well and can be inspected independently.",
  },
  {
    id: "sequential-composition",
    title: "Sequential Composition",
    subtitle: "Confidence Multiplies",
    icon: ArrowRight,
    color: "from-purple-500 to-pink-600",
    image: "/download/assets/round1_tiles/sequential_multiplication.png",
    description: "When tiles are composed sequentially, their confidences multiply.",
    formulas: [
      { name: "Compose", value: "A.compose(B)", meaning: "Connect A to B" },
      { name: "Confidence Flow", value: "c_total = c_A × c_B", meaning: "Uncertainty compounds" },
      { name: "Example", value: "0.90 × 0.80 = 0.72", meaning: "RED zone!" },
    ],
    learnMore: "Two 90% confident tiles become 81% together. Three become 72.9%.",
  },
  {
    id: "parallel-composition",
    title: "Parallel Composition",
    subtitle: "Confidence Averages",
    icon: Layers,
    color: "from-emerald-500 to-teal-600",
    image: "/download/assets/round1_tiles/parallel_averaging.png",
    description: "When tiles run in parallel, their confidences average for reliability.",
    formulas: [
      { name: "Parallel", value: "A.parallel(B)", meaning: "Run both simultaneously" },
      { name: "Confidence Mix", value: "c_total = (c_A + c_B) / 2", meaning: "Average uncertainty" },
      { name: "Example", value: "(0.90 + 0.70) / 2 = 0.80", meaning: "YELLOW zone" },
    ],
    learnMore: "Parallel composition is like getting a second opinion. It prevents single points of failure.",
  },
  {
    id: "confidence-zones",
    title: "Three-Zone Model",
    subtitle: "GREEN, YELLOW, RED",
    icon: Activity,
    color: "from-amber-500 to-orange-600",
    image: "/download/assets/round1_tiles/confidence_cascade_zones.png",
    description: "Tiles are classified into zones based on confidence level.",
    formulas: [
      { name: "GREEN Zone", value: "c ≥ 0.90", meaning: "Auto-proceed" },
      { name: "YELLOW Zone", value: "0.75 ≤ c < 0.90", meaning: "Review suggested" },
      { name: "RED Zone", value: "c < 0.75", meaning: "Stop, investigate" },
    ],
    learnMore: "RED tiles require intervention before proceeding. This guards against low-confidence decisions.",
  },
  {
    id: "tile-registry",
    title: "Tile Registry",
    subtitle: "Discovery & Dependencies",
    icon: Database,
    color: "from-blue-500 to-indigo-600",
    image: "/download/assets/round1_tiles/tile_registry_hub.png",
    description: "A central hub for discovering tiles and managing dependencies.",
    formulas: [
      { name: "Register", value: "registry.register(tile)", meaning: "Add to catalog" },
      { name: "Discover", value: "registry.find(I, O)", meaning: "Find by type signature" },
      { name: "Resolve", value: "registry.deps(tile)", meaning: "Get dependencies" },
    ],
    learnMore: "The registry enables a thriving ecosystem of reusable AI components.",
  },
  {
    id: "tile-chains",
    title: "Tile Chains",
    subtitle: "Pipeline Intelligence",
    icon: GitBranch,
    color: "from-rose-500 to-pink-600",
    image: "/download/assets/round1_tiles/tile_chain_flow.png",
    description: "Complex AI emerges from simple tile chains. Every step is visible.",
    formulas: [
      { name: "Chain", value: "tile1.chain(tile2, ...)", meaning: "Build pipeline" },
      { name: "Branch", value: "chain.branch(cond, alt)", meaning: "Conditional exec" },
      { name: "Trace", value: "chain.trace(input)", meaning: "See every decision" },
    ],
    learnMore: "Unlike black-box neural networks, tile chains let you see every intermediate result.",
  },
];

// Interactive Tile Builder Component
function TileBuilder() {
  const [tiles, setTiles] = useState<Tile[]>([]);
  const [compositionType, setCompositionType] = useState<"sequential" | "parallel">("sequential");

  const addTile = useCallback(() => {
    const newTile: Tile = {
      id: `tile-${Date.now()}`,
      name: `Tile ${tiles.length + 1}`,
      type: tiles.length === 0 ? "input" : tiles.length === 5 ? "output" : "process",
      confidence: 0.7 + Math.random() * 0.3,
    };
    setTiles([...tiles, newTile]);
  }, [tiles]);

  const resetTiles = useCallback(() => {
    setTiles([]);
  }, []);

  const calculateTotalConfidence = () => {
    if (tiles.length === 0) return 0;
    if (compositionType === "sequential") {
      return tiles.reduce((acc, tile) => acc * tile.confidence, 1);
    }
    return tiles.reduce((acc, tile) => acc + tile.confidence, 0) / tiles.length;
  };

  const totalConfidence = calculateTotalConfidence();
  const zoneInfo = getZoneInfo(totalConfidence);

  return (
    <div className="bg-card/80 backdrop-blur-sm rounded-2xl border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold flex items-center gap-2">
          <Box className="w-5 h-5 text-purple-400" />
          Interactive Tile Composer
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCompositionType("sequential")}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              compositionType === "sequential"
                ? "bg-purple-500/20 text-purple-400 border border-purple-500/50"
                : "bg-muted text-muted-foreground"
            }`}
          >
            Sequential
          </button>
          <button
            onClick={() => setCompositionType("parallel")}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
              compositionType === "parallel"
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/50"
                : "bg-muted text-muted-foreground"
            }`}
          >
            Parallel
          </button>
        </div>
      </div>

      {/* Tile Visualization */}
      <div className="relative min-h-[120px] bg-black/30 rounded-xl p-4 mb-4 overflow-x-auto">
        <div className="flex items-center gap-4 min-w-max">
          {tiles.length === 0 ? (
            <div className="text-center w-full text-muted-foreground py-8">
              Click &quot;Add Tile&quot; to start building
            </div>
          ) : (
            tiles.map((tile, index) => {
              const tileZone = getZoneInfo(tile.confidence);
              return (
                <motion.div
                  key={tile.id}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="flex items-center gap-3"
                >
                  <div className={`flex flex-col items-center p-3 rounded-xl ${tileZone.bg} border border-white/10 min-w-[80px]`}>
                    <span className="text-xs text-muted-foreground">{tile.type}</span>
                    <span className="font-medium">{tile.name}</span>
                    <span className={`text-sm font-mono ${tileZone.text}`}>
                      {(tile.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                  {index < tiles.length - 1 && (
                    <span className="text-xl text-muted-foreground">
                      {compositionType === "sequential" ? "→" : "∥"}
                    </span>
                  )}
                </motion.div>
              );
            })
          )}
        </div>
      </div>

      {/* Total Confidence Display */}
      {tiles.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-4 rounded-xl ${zoneInfo.bg} border border-white/10 mb-4`}
        >
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              Total Confidence ({compositionType === "sequential" ? "multiplied" : "averaged"}):
            </span>
            <div className="flex items-center gap-2">
              <span className={`text-2xl font-bold font-mono ${zoneInfo.text}`}>
                {(totalConfidence * 100).toFixed(1)}%
              </span>
              <span className={`text-xs px-2 py-1 rounded ${zoneInfo.bg} ${zoneInfo.text} font-medium`}>
                {zoneInfo.zone}
              </span>
            </div>
          </div>
          <div className="mt-2 text-xs text-muted-foreground">
            {compositionType === "sequential" 
              ? tiles.map(t => (t.confidence * 100).toFixed(0)).join(" × ") + " = " + (totalConfidence * 100).toFixed(1)
              : `(${tiles.map(t => (t.confidence * 100).toFixed(0)).join(" + ")}) / ${tiles.length} = ${(totalConfidence * 100).toFixed(1)}`
            }
          </div>
        </motion.div>
      )}

      {/* Controls */}
      <div className="flex gap-3">
        <button
          onClick={addTile}
          className="flex-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium px-4 py-2 rounded-xl hover:opacity-90 transition-opacity inline-flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Tile
        </button>
        <button
          onClick={resetTiles}
          className="bg-muted text-muted-foreground px-4 py-2 rounded-xl hover:bg-muted/80 transition-colors"
        >
          Reset
        </button>
      </div>
    </div>
  );
}

// Zone Legend Component
function ZoneLegend() {
  return (
    <div className="flex flex-wrap items-center justify-center gap-6 py-4">
      <div className="flex items-center gap-2">
        <CheckCircle className="w-5 h-5 text-emerald-400" />
        <span className="text-sm">GREEN (≥90%) - Auto-proceed</span>
      </div>
      <div className="flex items-center gap-2">
        <AlertTriangle className="w-5 h-5 text-amber-400" />
        <span className="text-sm">YELLOW (75-89%) - Review</span>
      </div>
      <div className="flex items-center gap-2">
        <XCircle className="w-5 h-5 text-red-400" />
        <span className="text-sm">RED (&lt;75%) - Stop</span>
      </div>
    </div>
  );
}

// Main Page Component
export default function TileIntelligence() {
  const [selectedConcept, setSelectedConcept] = useState<typeof tileConcepts[0] | null>(null);

  return (
    <>
      <Head>
        <title>Tile Intelligence | Lucineer - POLLN Educational Platform</title>
        <meta name="description" content="Learn Tile Intelligence from POLLN - AI decomposed into inspectable, composable tiles. Interactive confidence cascade visualization." />
        <meta name="keywords" content="tile intelligence, POLLN, AI tiles, confidence cascade, inspectable AI, glass box AI" />
        <meta property="og:type" content="website" />
        <meta property="og:title" content="Tile Intelligence - Where AI Becomes LEGO" />
        <meta property="og:description" content="Interactive educational platform for understanding AI tiles. Build, compose, and debug AI like never before." />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "LearningResource",
              "name": "Tile Intelligence Visualizer",
              "description": "Educational platform for understanding POLLN tile architecture",
              "educationalLevel": "Beginner to Advanced",
              "learningResourceType": "Interactive Simulation",
              "about": ["Artificial Intelligence", "Neural Networks", "Software Architecture"],
            }),
          }}
        />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-background via-background to-purple-500/5">
        {/* Hero Section */}
        <section className="relative py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <motion.div
              className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"
              animate={{ x: [0, 50, 0], y: [0, 30, 0] }}
              transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
            />
            <motion.div
              className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl"
              animate={{ x: [0, -30, 0], y: [0, -50, 0] }}
              transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
            />
          </div>

          <div className="max-w-7xl mx-auto relative">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-center"
            >
              <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/30 rounded-full px-4 py-2 mb-8">
                <Box className="w-4 h-4 text-purple-400" />
                <span className="text-purple-400 text-sm font-medium">
                  From POLLN Project
                </span>
              </div>

              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6">
                <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">Tile Intelligence</span>
              </h1>
              
              <p className="text-xl text-muted-foreground mb-4 max-w-3xl mx-auto leading-relaxed">
                AI Decomposed into Inspectable, Composable LEGO Blocks
              </p>
              
              <p className="text-lg text-muted-foreground/80 mb-8 max-w-2xl mx-auto">
                From black boxes to glass boxes. Every decision visible. Every step debuggable.
              </p>

              <div className="flex flex-wrap justify-center gap-4 mb-8">
                <div className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 rounded-full">
                  <Eye className="w-5 h-5 text-emerald-400" />
                  <span className="text-emerald-400">Inspectable</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-cyan-400/10 rounded-full">
                  <Layers className="w-5 h-5 text-cyan-400" />
                  <span className="text-cyan-400">Composable</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-purple-400/10 rounded-full">
                  <Zap className="w-5 h-5 text-purple-400" />
                  <span className="text-purple-400">Debuggable</span>
                </div>
              </div>

              <ZoneLegend />
            </motion.div>
          </div>
        </section>

        {/* Interactive Tile Builder */}
        <section className="py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-8"
            >
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Try It Yourself
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Add tiles and watch how confidence flows through the composition
              </p>
            </motion.div>

            <TileBuilder />
          </div>
        </section>

        {/* Concept Grid */}
        <section className="py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                6 Core Concepts
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Click any concept to dive deep into the math that powers tile intelligence
              </p>
            </motion.div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {tileConcepts.map((concept, index) => (
                <motion.div
                  key={concept.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => setSelectedConcept(concept)}
                  className="cursor-pointer group"
                >
                  <div className="bg-card/80 backdrop-blur-sm rounded-2xl border border-border overflow-hidden hover:border-purple-500/50 transition-all hover:shadow-lg hover:shadow-purple-500/10">
                    <div className="relative h-48">
                      <Image
                        src={concept.image}
                        alt={concept.title}
                        fill
                        className="object-cover opacity-60 group-hover:opacity-80 transition-opacity"
                      />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${concept.color} flex items-center justify-center shadow-lg`}>
                          <concept.icon className="w-8 h-8 text-white" />
                        </div>
                      </div>
                    </div>
                    <div className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${concept.color} flex items-center justify-center`}>
                          <concept.icon className="w-4 h-4 text-white" />
                        </div>
                        <div>
                          <h3 className="font-semibold">{concept.title}</h3>
                          <p className="text-xs text-muted-foreground">{concept.subtitle}</p>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">{concept.description}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Selected Concept Detail Modal */}
        <AnimatePresence>
          {selectedConcept && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
              onClick={() => setSelectedConcept(null)}
            >
              <motion.div
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.9, y: 20 }}
                className="bg-card rounded-3xl border border-border max-w-4xl w-full max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="relative h-64">
                  <Image
                    src={selectedConcept.image}
                    alt={selectedConcept.title}
                    fill
                    className="object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-card to-transparent" />
                  <div className="absolute bottom-4 left-4 right-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${selectedConcept.color} flex items-center justify-center`}>
                        <selectedConcept.icon className="w-6 h-6 text-white" />
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold">{selectedConcept.title}</h2>
                        <p className="text-muted-foreground">{selectedConcept.subtitle}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="p-6 space-y-6">
                  <div>
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                      <Terminal className="w-5 h-5 text-purple-400" />
                      Key Formulas
                    </h3>
                    <div className="grid gap-3">
                      {selectedConcept.formulas.map((formula, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.1 }}
                          className="bg-black/30 rounded-lg p-4 border border-white/10"
                        >
                          <div className="flex items-start justify-between mb-2">
                            <span className="text-sm font-medium text-purple-400">{formula.name}</span>
                            <span className="text-xs text-muted-foreground">{formula.meaning}</span>
                          </div>
                          <code className="text-lg font-mono text-white">{formula.value}</code>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gradient-to-r from-purple-500/10 to-cyan-400/10 rounded-xl p-4 border border-purple-500/20">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-4 h-4 text-purple-400" />
                      <span className="text-sm font-medium text-purple-400">Learn More</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{selectedConcept.learnMore}</p>
                  </div>

                  <button
                    onClick={() => setSelectedConcept(null)}
                    className="w-full py-3 rounded-xl bg-purple-500/10 text-purple-400 font-medium hover:bg-purple-500/20 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* POLLN Integration Section */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/30">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                From POLLN Project
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Tile Intelligence is the core innovation of POLLN - a distributed AI system 
                built on inspectable, composable agents.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-card rounded-2xl border border-border p-6 text-center">
                <div className="text-4xl font-bold text-purple-400 mb-2">5</div>
                <p className="text-sm text-muted-foreground">Core Operations per Tile</p>
              </div>
              <div className="bg-card rounded-2xl border border-border p-6 text-center">
                <div className="text-4xl font-bold text-cyan-400 mb-2">3</div>
                <p className="text-sm text-muted-foreground">Confidence Zones</p>
              </div>
              <div className="bg-card rounded-2xl border border-border p-6 text-center">
                <div className="text-4xl font-bold text-emerald-400 mb-2">2</div>
                <p className="text-sm text-muted-foreground">Composition Types</p>
              </div>
              <div className="bg-card rounded-2xl border border-border p-6 text-center">
                <div className="text-4xl font-bold text-pink-400 mb-2">∞</div>
                <p className="text-sm text-muted-foreground">Possible Combinations</p>
              </div>
            </div>

            <div className="mt-12 text-center">
              <a
                href="https://github.com/SuperInstance/polln"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold px-6 py-3 rounded-xl hover:opacity-90 transition-opacity"
              >
                <BookOpen className="w-5 h-5" />
                View POLLN on GitHub
                <ChevronRight className="w-4 h-4" />
              </a>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                Build AI You Can Trust
              </h2>
              <p className="text-lg text-muted-foreground mb-8">
                Tile Intelligence transforms AI from black boxes to glass boxes. 
                See every decision. Debug every step. Improve every tile.
              </p>
              
              <div className="flex flex-wrap justify-center gap-4">
                <Link href="/math-universe" className="bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold px-6 py-3 rounded-xl hover:opacity-90 transition-opacity inline-flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Explore Math Universe
                </Link>
                <Link href="/mist" className="bg-card border border-border text-foreground font-medium px-6 py-3 rounded-xl hover:border-purple-500/50 transition-colors inline-flex items-center gap-2">
                  <Play className="w-5 h-5" />
                  Play MIST Game
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </div>
    </>
  );
}
