"use client";

import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import {
  Brain,
  Sparkles,
  Zap,
  Layers,
  Database,
  ArrowRight,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Code,
  Cpu,
  Music,
  BookOpen,
  Target,
} from "lucide-react";

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

// Concept validation results
const validationResults = [
  { 
    claim: "Artistically dumb but artistically skilled", 
    verdict: "refined",
    icon: AlertTriangle,
    finding: "Models CAN be technically capable with minimal style bias, but never truly 'blank'",
    color: "text-amber-400",
  },
  { 
    claim: "Training on specific material for specialization", 
    verdict: "validated",
    icon: CheckCircle,
    finding: "Standard domain adaptation approach; LoRA is optimal implementation",
    color: "text-green-400",
  },
  { 
    claim: "Distilling vector databases into personalities", 
    verdict: "validated",
    icon: CheckCircle,
    finding: "Embeddings capture style; distillation feasible but quality bounded by base model",
    color: "text-green-400",
  },
  { 
    claim: "Model starts blank and learns ONLY from training data", 
    verdict: "falsified",
    icon: XCircle,
    finding: "No model is truly blank; pure narrow training produces brittle specialists",
    color: "text-red-400",
  },
];

// Implementation layers
const implementationLayers = [
  {
    name: "Layer 1: Silicon (Immutable)",
    description: "Base model frozen in hardware",
    details: [
      "100M ternary parameters",
      "Diverse chip design training",
      "Neutral, professional style",
      "3W power, 25 tok/s",
    ],
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    name: "Layer 2: SRAM (Configurable)",
    description: "Hot-swap personality adapters",
    details: [
      "3 adapter slots × 100KB each",
      "Industry, Style, Language slots",
      "<1 second swap time",
      "Runtime personality change",
    ],
    color: "text-blue-400",
    bgColor: "bg-blue-400/10",
  },
  {
    name: "Layer 3: Cloud (Extensible)",
    description: "Continuous learning pipeline",
    details: [
      "Adapter marketplace",
      "Style distillation pipeline",
      "Vector database embeddings",
      "Community sharing",
    ],
    color: "text-purple-400",
    bgColor: "bg-purple-400/10",
  },
];

// Key research papers
const keyPapers = [
  { name: "LoRA", authors: "Hu et al., 2021", contribution: "Parameter-efficient adaptation foundation" },
  { name: "Platonic Representation Hypothesis", authors: "Huh et al., 2024", contribution: "Refutes true blank slate possibility" },
  { name: "Neural Style Transfer", authors: "Gatys, 2015-2016", contribution: "Proves style is mathematically separable" },
  { name: "MusicLM/MusicGen", authors: "Google/Meta, 2023", contribution: "Demonstrates controllable music generation" },
  { name: "Constitutional AI", authors: "Anthropic, 2022", contribution: "Personality layering onto base capabilities" },
];

// Failure modes and mitigations
const failureModes = [
  {
    mode: "Mode Collapse",
    description: "Model outputs become repetitive and lose diversity",
    mitigation: "Use diverse training data; implement diversity sampling",
    severity: "high",
  },
  {
    mode: "Overfitting",
    description: "Model memorizes training data instead of learning patterns",
    mitigation: "Regularization, early stopping, data augmentation",
    severity: "high",
  },
  {
    mode: "Catastrophic Forgetting",
    description: "New training erases previously learned capabilities",
    mitigation: "Use LoRA adapters; avoid full fine-tuning",
    severity: "medium",
  },
  {
    mode: "Distribution Shift",
    description: "Training distribution doesn't match real-world use",
    mitigation: "Curated training sets; synthetic data generation",
    severity: "medium",
  },
];

export default function TabulaRosaPage() {
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
            <div className="inline-flex items-center gap-2 bg-purple-400/10 border border-purple-400/30 rounded-full px-4 py-2 mb-6">
              <Brain className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 text-sm font-medium">Research Concept</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="gradient-text">Tabula Rosa</span>
            </h1>

            <p className="text-xl text-muted-foreground mb-4 max-w-2xl mx-auto">
              The Blank Slate Model
            </p>
            <p className="text-lg text-muted-foreground mb-8 max-w-3xl mx-auto">
              Train a model that&apos;s technically capable but style-neutral.
              Then specialize it to do one thing perfectly through targeted training.
            </p>

            <div className="flex flex-wrap justify-center gap-4">
              <Link
                href="/music"
                className="btn-primary flex items-center gap-2 px-8 py-4"
              >
                <Music className="w-5 h-5" />
                Try Music Playground
              </Link>
              <Link
                href="#concept"
                className="btn-secondary flex items-center gap-2 px-8 py-4"
              >
                <BookOpen className="w-5 h-5" />
                Read the Research
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Concept Overview */}
      <section id="concept" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                The Core Concept
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                What if you could train a neural network that starts as a blank canvas?
                A model with technical capability but no inherent style or personality?
              </p>
              
              <div className="space-y-4">
                <div className="p-4 bg-purple-400/5 rounded-xl border border-purple-400/20">
                  <h3 className="font-medium text-purple-400 mb-2 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" /> Neutral Substrate
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Start with a model trained for technical competence across diverse domains,
                    but carefully curated to minimize style bias and personality imprint.
                  </p>
                </div>
                <div className="p-4 bg-purple-400/5 rounded-xl border border-purple-400/20">
                  <h3 className="font-medium text-purple-400 mb-2 flex items-center gap-2">
                    <Target className="w-4 h-4" /> Targeted Specialization
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Fine-tune on narrowly curated data to create specialists that excel
                    at one specific task or style - a jazz pianist, a classical composer, 
                    a technical writer.
                  </p>
                </div>
                <div className="p-4 bg-purple-400/5 rounded-xl border border-purple-400/20">
                  <h3 className="font-medium text-purple-400 mb-2 flex items-center gap-2">
                    <Layers className="w-4 h-4" /> Adapter Architecture
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Use LoRA adapters to swap personalities in and out of the base model,
                    enabling one chip to become many specialists.
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
                  src="/download/assets/tabula_rosa_concept.png"
                  alt="Tabula Rosa Concept"
                  width={1344}
                  height={768}
                  className="w-full h-auto"
                />
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Validation Results */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Concept Validation
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              We tested the core claims against current research and simulation
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {validationResults.map((result) => (
              <motion.div
                key={result.claim}
                variants={fadeInUp}
                className="bg-card rounded-2xl border border-border p-6"
              >
                <div className="flex items-start gap-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    result.verdict === 'validated' ? 'bg-green-400/10' :
                    result.verdict === 'falsified' ? 'bg-red-400/10' : 'bg-amber-400/10'
                  }`}>
                    <result.icon className={`w-5 h-5 ${result.color}`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold">{result.claim}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        result.verdict === 'validated' ? 'bg-green-400/10 text-green-400' :
                        result.verdict === 'falsified' ? 'bg-red-400/10 text-red-400' : 
                        'bg-amber-400/10 text-amber-400'
                      }`}>
                        {result.verdict.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">{result.finding}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Implementation Architecture */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Implementation Architecture
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Three-layer architecture for specialized inference chips
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="space-y-6"
          >
            {implementationLayers.map((layer, index) => (
              <motion.div
                key={layer.name}
                variants={fadeInUp}
                className="bg-card rounded-2xl border border-border p-6"
              >
                <div className="flex flex-col md:flex-row gap-6">
                  <div className="flex-shrink-0">
                    <div className={`w-16 h-16 rounded-xl ${layer.bgColor} flex items-center justify-center`}>
                      <span className={`text-2xl font-bold ${layer.color}`}>{index + 1}</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold mb-2">{layer.name}</h3>
                    <p className="text-muted-foreground mb-4">{layer.description}</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {layer.details.map((detail) => (
                        <div key={detail} className="text-sm bg-muted/30 rounded-lg px-3 py-2">
                          {detail}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Vector DB Distillation */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="order-2 lg:order-1"
            >
              <div className="bg-card rounded-2xl border border-border overflow-hidden">
                <Image
                  src="/download/assets/vector_db_distillation.png"
                  alt="Vector Database Distillation"
                  width={1344}
                  height={768}
                  className="w-full h-auto"
                />
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="order-1 lg:order-2"
            >
              <div className="inline-flex items-center gap-2 bg-cyan-400/10 border border-cyan-400/30 rounded-full px-4 py-2 mb-6">
                <Database className="w-4 h-4 text-cyan-400" />
                <span className="text-cyan-400 text-sm font-medium">Data Architecture</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Vector DB Distillation
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                Extract specific artistic personalities from large embedded collections.
                Vector embeddings capture style, and distillation extracts those patterns
                into portable, swappable adapters.
              </p>
              
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-cyan-400/10 flex items-center justify-center text-sm font-bold text-cyan-400">1</div>
                  <p className="text-sm">Encode artistic corpus into vector embeddings</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-cyan-400/10 flex items-center justify-center text-sm font-bold text-cyan-400">2</div>
                  <p className="text-sm">Cluster embeddings by style/similarity</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-cyan-400/10 flex items-center justify-center text-sm font-bold text-cyan-400">3</div>
                  <p className="text-sm">Train LoRA adapter on cluster subset</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-cyan-400/10 flex items-center justify-center text-sm font-bold text-cyan-400">4</div>
                  <p className="text-sm">Deploy as swappable personality module</p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Failure Modes */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Failure Modes & Mitigations
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Understanding how specialization can go wrong
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            {failureModes.map((mode) => (
              <motion.div
                key={mode.mode}
                variants={fadeInUp}
                className="bg-card rounded-2xl border border-border p-6"
              >
                <div className="flex items-center gap-2 mb-3">
                  <h3 className="font-semibold">{mode.mode}</h3>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    mode.severity === 'high' 
                      ? 'bg-red-400/10 text-red-400' 
                      : 'bg-amber-400/10 text-amber-400'
                  }`}>
                    {mode.severity.toUpperCase()} RISK
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mb-3">{mode.description}</p>
                <div className="p-3 bg-green-400/5 rounded-lg border border-green-400/20">
                  <p className="text-sm text-green-400">
                    <strong>Mitigation:</strong> {mode.mitigation}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Key Research */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Key Research Foundations
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Papers that inform and validate this approach
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="space-y-4"
          >
            {keyPapers.map((paper) => (
              <motion.div
                key={paper.name}
                variants={fadeInUp}
                className="bg-card rounded-xl border border-border p-4 flex flex-col md:flex-row md:items-center gap-4"
              >
                <div className="flex-1">
                  <h3 className="font-semibold">{paper.name}</h3>
                  <p className="text-sm text-muted-foreground">{paper.authors}</p>
                </div>
                <div className="md:text-right">
                  <p className="text-sm">{paper.contribution}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Connection to Chips */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2 mb-6">
                <Cpu className="w-4 h-4 text-primary" />
                <span className="text-primary text-sm font-medium">Hardware Application</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                From Tabula Rosa to Inference Chips
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                The same principles apply to mask-locked inference chips. 
                A neutral substrate model can be specialized for specific tasks
                through immutable weights burned into silicon.
              </p>
              
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5" />
                  <div>
                    <h3 className="font-medium">Immutable Specialization</h3>
                    <p className="text-sm text-muted-foreground">
                      Weights frozen in metal layers - the ultimate committed specialist
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5" />
                  <div>
                    <h3 className="font-medium">Adapter Slots</h3>
                    <p className="text-sm text-muted-foreground">
                      SRAM-based adapters for runtime personality swaps
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-primary mt-0.5" />
                  <div>
                    <h3 className="font-medium">Security by Design</h3>
                    <p className="text-sm text-muted-foreground">
                      Cannot extract or modify weights - the model IS the hardware
                    </p>
                  </div>
                </div>
              </div>

              <Link
                href="/professional"
                className="btn-primary inline-flex items-center gap-2 mt-8"
              >
                <Cpu className="w-4 h-4" />
                Explore Chip Design Studio
                <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="bg-card rounded-2xl border border-border overflow-hidden">
                <Image
                  src="/download/assets/silicon_wafer_closeup.png"
                  alt="Silicon Wafer"
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
            Explore the Platform
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            See Tabula Rosa in action across our tools
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/music"
              className="btn-primary flex items-center gap-2 px-8 py-4"
            >
              <Music className="w-5 h-5" />
              Music Playground
            </Link>
            <Link
              href="/professional"
              className="btn-secondary flex items-center gap-2 px-8 py-4"
            >
              <Cpu className="w-5 h-5" />
              Chip Design Studio
            </Link>
            <Link
              href="/learning"
              className="btn-secondary flex items-center gap-2 px-8 py-4"
            >
              <BookOpen className="w-5 h-5" />
              Learning Hub
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
