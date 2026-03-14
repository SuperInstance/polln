"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import {
  Music,
  Play,
  Pause,
  Volume2,
  Piano,
  Disc3,
  Sparkles,
  Brain,
  Sliders,
  RefreshCw,
  Download,
  Zap,
  Layers,
  ArrowRight,
} from "lucide-react";

// Musical style presets
const stylePresets = [
  { id: "classical", name: "Classical", icon: "🎼", color: "text-amber-400", bgColor: "bg-amber-400/10" },
  { id: "jazz", name: "Jazz", icon: "🎷", color: "text-blue-400", bgColor: "bg-blue-400/10" },
  { id: "electronic", name: "Electronic", icon: "🎹", color: "text-purple-400", bgColor: "bg-purple-400/10" },
  { id: "ambient", name: "Ambient", icon: "🌙", color: "text-cyan-400", bgColor: "bg-cyan-400/10" },
  { id: "folk", name: "Folk", icon: "🎸", color: "text-green-400", bgColor: "bg-green-400/10" },
  { id: "minimal", name: "Minimal", icon: "▪", color: "text-gray-400", bgColor: "bg-gray-400/10" },
];

// Pattern constraints
const patternConstraints = [
  { id: "arpeggio", name: "Arpeggiated", description: "Notes played in sequence up/down" },
  { id: "chord", name: "Chord-Based", description: "Harmonic structures with voicing" },
  { id: "melodic", name: "Melodic", description: "Single-note melodic lines" },
  { id: "rhythmic", name: "Rhythmic", description: "Percussive and timing-focused" },
  { id: "counterpoint", name: "Counterpoint", description: "Multiple independent voices" },
  { id: "drone", name: "Drone", description: "Sustained harmonic foundation" },
];

// Simplified piano roll visualization
function PianoRoll({ notes, currentStep }: { notes: number[]; currentStep: number }) {
  const rows = 12; // One octave
  const cols = 16; // 16 steps
  
  return (
    <div className="bg-card rounded-xl border border-border p-4 overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold flex items-center gap-2">
          <Piano className="w-4 h-4" /> Piano Roll
        </h3>
        <span className="text-sm text-muted-foreground">Step {currentStep + 1}/16</span>
      </div>
      <div className="space-y-0.5">
        {Array.from({ length: rows }).map((_, row) => {
          const noteIndex = rows - 1 - row;
          const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
          const noteName = noteNames[noteIndex % 12];
          const isBlackKey = noteName.includes('#');
          
          return (
            <div key={row} className="flex items-center gap-1">
              <div className={`w-8 text-xs text-right ${isBlackKey ? 'text-gray-500' : 'text-muted-foreground'}`}>
                {noteName}
              </div>
              <div className="flex gap-0.5 flex-1">
                {Array.from({ length: cols }).map((_, col) => {
                  const isActive = notes.includes(noteIndex) && col === currentStep;
                  const isHighlight = col % 4 === 0;
                  
                  return (
                    <div
                      key={col}
                      className={`flex-1 h-4 rounded-sm transition-all duration-100 ${
                        isActive
                          ? 'bg-primary shadow-[0_0_10px_rgba(0,212,170,0.5)]'
                          : isHighlight
                          ? isBlackKey ? 'bg-gray-800' : 'bg-gray-700'
                          : isBlackKey ? 'bg-gray-900' : 'bg-gray-800'
                      }`}
                    />
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// Parameter slider component
function ParamSlider({ label, value, onChange, min = 0, max = 100, unit = "" }: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  unit?: string;
}) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-mono text-primary">{value}{unit}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 bg-muted rounded-full appearance-none cursor-pointer"
      />
    </div>
  );
}

// Model constraint visualization
function ModelConstraintViz({ style, constraint }: { style: string; constraint: string }) {
  return (
    <div className="bg-card rounded-xl border border-border p-6">
      <h3 className="font-semibold mb-4 flex items-center gap-2">
        <Brain className="w-4 h-4" /> Model Constraint Space
      </h3>
      
      <div className="relative h-48 bg-muted/30 rounded-lg overflow-hidden">
        <svg className="w-full h-full" viewBox="0 0 400 200">
          {/* Background grid */}
          {Array.from({ length: 20 }).map((_, i) => (
            <line key={`v-${i}`} x1={i * 20} y1={0} x2={i * 20} y2={200} stroke="rgba(255,255,255,0.05)" />
          ))}
          {Array.from({ length: 10 }).map((_, i) => (
            <line key={`h-${i}`} x1={0} y1={i * 20} x2={400} y2={i * 20} stroke="rgba(255,255,255,0.05)" />
          ))}
          
          {/* Constrained area */}
          <motion.ellipse
            cx={200}
            cy={100}
            rx={120}
            ry={60}
            fill="rgba(0, 212, 170, 0.1)"
            stroke="rgba(0, 212, 170, 0.5)"
            strokeWidth={2}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.5 }}
          />
          
          {/* Style marker */}
          <motion.circle
            cx={200}
            cy={100}
            r={10}
            fill="#00D4AA"
            initial={{ scale: 0 }}
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          
          {/* Labels */}
          <text x={200} y={170} textAnchor="middle" fill="rgba(255,255,255,0.5)" fontSize={12}>
            Style: {style || 'None'}
          </text>
          <text x={200} y={185} textAnchor="middle" fill="rgba(255,255,255,0.5)" fontSize={10}>
            Pattern: {constraint || 'None'}
          </text>
        </svg>
      </div>
      
      <p className="text-sm text-muted-foreground mt-4">
        The model is constrained to operate within the highlighted region, producing only outputs
        that match the selected style and pattern.
      </p>
    </div>
  );
}

export default function MusicPage() {
  const [selectedStyle, setSelectedStyle] = useState("classical");
  const [selectedPattern, setSelectedPattern] = useState("arpeggio");
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [tempo, setTempo] = useState(120);
  const [complexity, setComplexity] = useState(50);
  const [randomness, setRandomness] = useState(20);
  
  // Generate random notes for visualization
  const [activeNotes, setActiveNotes] = useState<number[]>([0, 4, 7]);
  
  // Simulate playback
  useEffect(() => {
    if (!isPlaying) return;
    
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % 16);
      // Randomly update notes for demo
      if (Math.random() > 0.7) {
        setActiveNotes([
          Math.floor(Math.random() * 12),
          Math.floor(Math.random() * 12),
          Math.floor(Math.random() * 12),
        ]);
      }
    }, 60000 / tempo / 4);
    
    return () => clearInterval(interval);
  }, [isPlaying, tempo]);

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
            <div className="inline-flex items-center gap-2 bg-cyan-400/10 border border-cyan-400/30 rounded-full px-4 py-2 mb-6">
              <Music className="w-4 h-4 text-cyan-400" />
              <span className="text-cyan-400 text-sm font-medium">Generative Music Playground</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="gradient-text">Constrain Creativity</span>
            </h1>

            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Explore how neural networks can be constrained into specific styles and patterns.
              Like training a musician to play only one genre perfectly.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Main Interface */}
      <section className="px-4 sm:px-6 lg:px-8 pb-12">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left Panel: Style Selection */}
            <div className="space-y-6">
              <div className="bg-card rounded-2xl border border-border p-6">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                  <Disc3 className="w-4 h-4" /> Musical Style
                </h3>
                <div className="grid grid-cols-2 gap-3">
                  {stylePresets.map((style) => (
                    <button
                      key={style.id}
                      onClick={() => setSelectedStyle(style.id)}
                      className={`p-3 rounded-xl border transition-all text-left ${
                        selectedStyle === style.id
                          ? `${style.bgColor} border-current ${style.color}`
                          : 'border-border hover:border-muted'
                      }`}
                    >
                      <div className="text-2xl mb-1">{style.icon}</div>
                      <div className="text-sm font-medium">{style.name}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="bg-card rounded-2xl border border-border p-6">
                <h3 className="font-semibold mb-4 flex items-center gap-2">
                  <Layers className="w-4 h-4" /> Pattern Constraint
                </h3>
                <div className="space-y-2">
                  {patternConstraints.map((pattern) => (
                    <button
                      key={pattern.id}
                      onClick={() => setSelectedPattern(pattern.id)}
                      className={`w-full p-3 rounded-lg border text-left transition-all ${
                        selectedPattern === pattern.id
                          ? 'bg-primary/10 border-primary text-primary'
                          : 'border-border hover:border-muted'
                      }`}
                    >
                      <div className="font-medium text-sm">{pattern.name}</div>
                      <div className="text-xs text-muted-foreground">{pattern.description}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Center Panel: Piano Roll & Controls */}
            <div className="lg:col-span-2 space-y-6">
              <PianoRoll notes={activeNotes} currentStep={currentStep} />
              
              {/* Transport Controls */}
              <div className="bg-card rounded-xl border border-border p-6">
                <div className="flex items-center justify-center gap-4 mb-6">
                  <button
                    onClick={() => setCurrentStep(0)}
                    className="p-3 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
                  >
                    <RefreshCw className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className={`p-4 rounded-full transition-all ${
                      isPlaying
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-primary/10 text-primary hover:bg-primary hover:text-primary-foreground'
                    }`}
                  >
                    {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
                  </button>
                  <button className="p-3 rounded-lg bg-muted hover:bg-muted/80 transition-colors">
                    <Download className="w-5 h-5" />
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <ParamSlider
                    label="Tempo"
                    value={tempo}
                    onChange={setTempo}
                    min={40}
                    max={200}
                    unit=" BPM"
                  />
                  <ParamSlider
                    label="Complexity"
                    value={complexity}
                    onChange={setComplexity}
                    unit="%"
                  />
                  <ParamSlider
                    label="Randomness"
                    value={randomness}
                    onChange={setRandomness}
                    unit="%"
                  />
                </div>
              </div>

              <ModelConstraintViz style={selectedStyle} constraint={selectedPattern} />
            </div>
          </div>
        </div>
      </section>

      {/* Tabula Rosa Connection */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <div className="inline-flex items-center gap-2 bg-purple-400/10 border border-purple-400/30 rounded-full px-4 py-2 mb-6">
              <Brain className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 text-sm font-medium">Connected Concept</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              This is Tabula Rosa in Action
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Imagine a model that starts blank - capable of playing any music but with no style.
              Train it on only classical music, and it becomes a classical specialist.
              Train it on jazz, it becomes a jazz specialist.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-card rounded-2xl border border-border p-6">
              <div className="w-12 h-12 rounded-xl bg-purple-400/10 flex items-center justify-center mb-4">
                <Sparkles className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Blank Slate</h3>
              <p className="text-muted-foreground text-sm">
                Start with a neutral model that has technical capability but no inherent style preferences.
              </p>
            </div>
            <div className="bg-card rounded-2xl border border-border p-6">
              <div className="w-12 h-12 rounded-xl bg-purple-400/10 flex items-center justify-center mb-4">
                <Sliders className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Constrain</h3>
              <p className="text-muted-foreground text-sm">
                Apply style and pattern constraints through targeted training on specific material.
              </p>
            </div>
            <div className="bg-card rounded-2xl border border-border p-6">
              <div className="w-12 h-12 rounded-xl bg-purple-400/10 flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Specialist</h3>
              <p className="text-muted-foreground text-sm">
                Result: A model that excels at one thing, trained from a blank canvas.
              </p>
            </div>
          </div>

          <div className="text-center mt-8">
            <Link
              href="/tabula-rosa"
              className="btn-primary inline-flex items-center gap-2"
            >
              <Brain className="w-4 h-4" />
              Learn More About Tabula Rosa
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Technical Explanation */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                How Constraint Works
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                Neural networks learn patterns from data. By carefully selecting training data,
                we can constrain what patterns the model learns - effectively &quot;training in&quot;
                specific behaviors while &quot;training out&quot; others.
              </p>
              
              <div className="space-y-4">
                <div className="p-4 bg-muted/30 rounded-xl">
                  <h3 className="font-medium mb-2">Vector Space Constraints</h3>
                  <p className="text-sm text-muted-foreground">
                    Each style occupies a region in embedding space. Training narrows the model&apos;s
                    output distribution to stay within that region.
                  </p>
                </div>
                <div className="p-4 bg-muted/30 rounded-xl">
                  <h3 className="font-medium mb-2">LoRA Adapters</h3>
                  <p className="text-sm text-muted-foreground">
                    Low-Rank Adaptation allows us to swap personalities in/out of a base model
                    with just 0.1% of the parameters - like changing a music style preset.
                  </p>
                </div>
                <div className="p-4 bg-muted/30 rounded-xl">
                  <h3 className="font-medium mb-2">From Music to Chips</h3>
                  <p className="text-sm text-muted-foreground">
                    The same principles apply to inference chips: a neutral substrate model
                    can be specialized for specific tasks through mask-locked weights.
                  </p>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="bg-card rounded-2xl border border-border overflow-hidden">
                <Image
                  src="/download/assets/music_neural_network.png"
                  alt="Music Neural Network"
                  width={1024}
                  height={1024}
                  className="w-full h-auto"
                />
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Ready to Go Deeper?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Explore the full platform - from music playground to chip design studio.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/professional"
              className="btn-primary flex items-center gap-2 px-8 py-4"
            >
              <Zap className="w-5 h-5" />
              Chip Design Studio
            </Link>
            <Link
              href="/tabula-rosa"
              className="btn-secondary flex items-center gap-2 px-8 py-4"
            >
              <Brain className="w-5 h-5" />
              Tabula Rosa Research
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
