"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Head from "next/head";
import Link from "next/link";
import Image from "next/image";
import {
  Atom,
  Brain,
  Calculator,
  Box,
  Cpu,
  Database,
  Layers,
  Lightbulb,
  Orbit,
  Target,
  Waves,
  BookOpen,
  GraduationCap,
  Bot,
  Eye,
  Microscope,
  Shuffle,
} from "lucide-react";

// Mathematical Concepts with Visualizations
const mathConcepts = [
  {
    id: "fundamental-constants",
    title: "Fundamental Constants",
    subtitle: "The Universe's DNA",
    icon: Atom,
    color: "from-cyan-500 to-blue-600",
    image: "/download/assets/planck_constant_quantum.png",
    formulas: [
      { name: "Planck's Constant", value: "h = 6.626 × 10⁻³⁴ J·s", meaning: "Quantum of action" },
      { name: "Speed of Light", value: "c = 299,792,458 m/s", meaning: "Cosmic speed limit" },
      { name: "Euler's Identity", value: "e^(iπ) + 1 = 0", meaning: "Most beautiful equation" },
    ],
    voxelConcept: "Each constant is a glowing cube in space. Walk through the quantum foam!",
    aiLearningPath: "Understand the fundamental limits that constrain all computation",
  },
  {
    id: "neural-weights",
    title: "Neural Network Weights",
    subtitle: "Where Intelligence Lives",
    icon: Brain,
    color: "from-purple-500 to-pink-600",
    image: "/download/assets/neural_weights_silicon.png",
    formulas: [
      { name: "Weight Matrix", value: "W ∈ ℝ^(m×n)", meaning: "Connection strengths between neurons" },
      { name: "Forward Pass", value: "y = σ(Wx + b)", meaning: "Information flows through layers" },
      { name: "INT4 Range", value: "[-8, +7] ∩ ℤ", meaning: "4-bit quantization domain" },
    ],
    voxelConcept: "See weights as flowing rivers of light between voxel towers",
    aiLearningPath: "Map parameter space geometry and optimization landscapes",
  },
  {
    id: "gradient-descent",
    title: "Gradient Descent",
    subtitle: "How Machines Learn",
    icon: Target,
    color: "from-amber-500 to-orange-600",
    image: "/download/assets/gradient_descent_landscape.png",
    formulas: [
      { name: "Gradient Update", value: "θ ← θ - α∇L(θ)", meaning: "Step toward minimum" },
      { name: "Learning Rate", value: "α ∈ (0, 1)", meaning: "Step size hyperparameter" },
      { name: "Loss Function", value: "L = -Σy·log(ŷ)", meaning: "Cross-entropy error" },
    ],
    voxelConcept: "Navigate a 3D voxel landscape, rolling downhill to find the golden valley!",
    aiLearningPath: "Understand optimization dynamics and convergence theory",
  },
  {
    id: "attention-mechanism",
    title: "Attention Mechanism",
    subtitle: "The Heart of Transformers",
    icon: Eye,
    color: "from-blue-500 to-cyan-600",
    image: "/download/assets/attention_mechanism_transformer.png",
    formulas: [
      { name: "Self-Attention", value: "Attention(Q,K,V) = softmax(QK^T/√d)V", meaning: "Query-Key-Value attention" },
      { name: "Multi-Head", value: "head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)", meaning: "Parallel attention heads" },
      { name: "Softmax", value: "σ(z)_i = e^z_i / Σe^z_j", meaning: "Probability distribution" },
    ],
    voxelConcept: "Watch colored light beams connect voxels based on attention weights!",
    aiLearningPath: "Trace information flow and context aggregation patterns",
  },
  {
    id: "entropy-information",
    title: "Information & Entropy",
    subtitle: "Quantifying Uncertainty",
    icon: Shuffle,
    color: "from-red-500 to-rose-600",
    image: "/download/assets/entropy_information_theory.png",
    formulas: [
      { name: "Shannon Entropy", value: "H(X) = -Σp(x)log₂p(x)", meaning: "Information content" },
      { name: "KL Divergence", value: "D_KL(P||Q) = ΣP(x)log(P(x)/Q(x))", meaning: "Distribution distance" },
      { name: "Mutual Information", value: "I(X;Y) = H(X) - H(X|Y)", meaning: "Shared information" },
    ],
    voxelConcept: "Particles flow from order to chaos, visualizing entropy increase!",
    aiLearningPath: "Measure uncertainty and information gain in learning",
  },
  {
    id: "manifold-topology",
    title: "Manifold Learning",
    subtitle: "High-Dimensional Geometry",
    icon: Orbit,
    color: "from-green-500 to-teal-600",
    image: "/download/assets/manifold_topology_learning.png",
    formulas: [
      { name: "t-SNE", value: "C = Σp_ij log(p_ij/q_ij)", meaning: "Dimensionality reduction" },
      { name: "Manifold Hypothesis", value: "M ⊂ ℝ^n, dim(M) << n", meaning: "Data lies on lower-dim manifold" },
      { name: "UMAP", value: "minimize CE(P, Q)", meaning: "Preserve local structure" },
    ],
    voxelConcept: "Fly through warped space where data points cluster on curved surfaces!",
    aiLearningPath: "Navigate embedding spaces and cluster analysis",
  },
  {
    id: "mask-locked-chips",
    title: "Mask-Locked Chips",
    subtitle: "Intelligence in Silicon",
    icon: Cpu,
    color: "from-emerald-500 to-teal-600",
    image: "/download/assets/mask_locked_chip_crosssection.png",
    formulas: [
      { name: "Ternary Weight", value: "w ∈ {-1, 0, +1}", meaning: "BitNet 1.58-bit encoding" },
      { name: "Energy per MAC", value: "E = CV²f", meaning: "Power consumption" },
      { name: "Efficiency Gain", value: "116× vs GPU", meaning: "No memory access needed" },
    ],
    voxelConcept: "Zoom into silicon to see weights etched as metallic patterns!",
    aiLearningPath: "Understand hardware-software co-design for inference",
  },
  {
    id: "lora-adapters",
    title: "LoRA Adapters",
    subtitle: "Efficient Fine-Tuning",
    icon: Layers,
    color: "from-violet-500 to-purple-600",
    image: "/download/assets/lora_adapter_decomposition.png",
    formulas: [
      { name: "Low-Rank Decomp", value: "W = W₀ + BA", meaning: "Weight decomposition" },
      { name: "Parameter Ratio", value: "r/d << 1", meaning: "Rank much smaller than dimension" },
      { name: "Fine-Tune Cost", value: "~0.1% params", meaning: "Only train adapter matrices" },
    ],
    voxelConcept: "Watch a massive block split into two thin ribbons of parameters!",
    aiLearningPath: "Master parameter-efficient transfer learning",
  },
  {
    id: "knowledge-distillation",
    title: "Knowledge Distillation",
    subtitle: "Teaching Models to Teach",
    icon: GraduationCap,
    color: "from-orange-500 to-amber-600",
    image: "/download/assets/knowledge_distillation_transfer.png",
    formulas: [
      { name: "Distillation Loss", value: "L = αL_hard + (1-α)L_soft", meaning: "Combine hard and soft targets" },
      { name: "Temperature", value: "q_i = exp(z_i/T) / Σexp(z_j/T)", meaning: "Softmax temperature" },
      { name: "Teacher-Student", value: "θ_S = argmin L(f_T, f_S)", meaning: "Student learns from teacher" },
    ],
    voxelConcept: "See knowledge flow from a large glowing brain to a smaller one!",
    aiLearningPath: "Understand model compression and knowledge transfer",
  },
  {
    id: "quantum-mechanics",
    title: "Quantum Mechanics",
    subtitle: "Reality's Foundation",
    icon: Microscope,
    color: "from-indigo-500 to-blue-600",
    image: "/download/assets/quantum_tunneling_transistor.png",
    formulas: [
      { name: "Wave Function", value: "ψ(x) = probability amplitude", meaning: "Quantum state" },
      { name: "Schrödinger Equation", value: "iℏ∂ψ/∂t = Ĥψ", meaning: "Time evolution" },
      { name: "Superposition", value: "|ψ⟩ = α|0⟩ + β|1⟩", meaning: "Multiple states simultaneously" },
    ],
    voxelConcept: "Particles teleport through barriers as probability clouds!",
    aiLearningPath: "Connect quantum foundations to computing limits",
  },
  {
    id: "vector-embeddings",
    title: "Vector Embeddings",
    subtitle: "Meaning as Geometry",
    icon: Database,
    color: "from-pink-500 to-rose-600",
    image: "/download/assets/vector_database_embeddings.png",
    formulas: [
      { name: "Embedding", value: "f: X → ℝ^d", meaning: "Map to vector space" },
      { name: "Cosine Similarity", value: "sim(a,b) = a·b / (||a|| ||b||)", meaning: "Angle-based similarity" },
      { name: "Nearest Neighbor", value: "argmin_i ||q - x_i||", meaning: "Find closest vectors" },
    ],
    voxelConcept: "Float through a galaxy of word-vectors clustered by meaning!",
    aiLearningPath: "Navigate semantic space and retrieval systems",
  },
  {
    id: "systolic-arrays",
    title: "Systolic Arrays",
    subtitle: "Rhythmic Computation",
    icon: Waves,
    color: "from-yellow-500 to-orange-600",
    image: "/download/assets/systolic_array_matmul.png",
    formulas: [
      { name: "Matrix Multiply", value: "C = AB", meaning: "Core neural operation" },
      { name: "Data Flow", value: "w[k] → w[k+1]", meaning: "Weight stationary" },
      { name: "Throughput", value: "n² MACs/cycle", meaning: "Peak computation rate" },
    ],
    voxelConcept: "Watch data pulse through a grid of processing elements like a heartbeat!",
    aiLearningPath: "Understand hardware acceleration architecture",
  },
];

// Interactive Voxel Component
function VoxelGrid({ concept }: { concept: typeof mathConcepts[0] }) {
  const [active, setActive] = useState(false);
  
  return (
    <div 
      className="relative w-full aspect-square bg-black/20 rounded-xl overflow-hidden cursor-pointer group"
      onMouseEnter={() => setActive(true)}
      onMouseLeave={() => setActive(false)}
    >
      <Image
        src={concept.image}
        alt={concept.title}
        fill
        className="object-cover opacity-60 group-hover:opacity-80 transition-opacity"
      />
      
      <div className="absolute inset-0 grid grid-cols-4 grid-rows-4 gap-1 p-2">
        {Array.from({ length: 16 }).map((_, i) => (
          <motion.div
            key={i}
            className={`bg-gradient-to-br ${concept.color} rounded-sm`}
            initial={{ opacity: 0.3, scale: 0.8 }}
            animate={active ? { 
              opacity: [0.3, 0.8, 0.3], 
              scale: [0.8, 1, 0.8],
            } : { opacity: 0.3, scale: 0.8 }}
            transition={{ 
              duration: 2, 
              repeat: active ? Infinity : 0,
              delay: i * 0.1 
            }}
          />
        ))}
      </div>
      
      <div className="absolute inset-0 flex items-center justify-center">
        <motion.div
          className={`w-16 h-16 rounded-xl bg-gradient-to-br ${concept.color} flex items-center justify-center shadow-lg`}
          animate={active ? { scale: [1, 1.1, 1] } : { scale: 1 }}
          transition={{ duration: 1, repeat: active ? Infinity : 0 }}
        >
          <concept.icon className="w-8 h-8 text-white" />
        </motion.div>
      </div>
    </div>
  );
}

// Formula Display Component
function FormulaCard({ formula, index }: { formula: typeof mathConcepts[0]["formulas"][0]; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-black/30 rounded-lg p-4 border border-white/10"
    >
      <div className="flex items-start justify-between mb-2">
        <span className="text-sm font-medium text-emerald-400">{formula.name}</span>
        <span className="text-xs text-muted-foreground">{formula.meaning}</span>
      </div>
      <code className="text-lg font-mono text-white">{formula.value}</code>
    </motion.div>
  );
}

// AI Agent Learning Path Component
function AILearningPath({ concept }: { concept: typeof mathConcepts[0] }) {
  return (
    <div className="bg-gradient-to-r from-emerald-500/10 to-cyan-400/10 rounded-xl p-4 border border-emerald-500/20">
      <div className="flex items-center gap-2 mb-2">
        <Bot className="w-4 h-4 text-emerald-400" />
        <span className="text-sm font-medium text-emerald-400">AI Agent Learning Path</span>
      </div>
      <p className="text-sm text-muted-foreground">{concept.aiLearningPath}</p>
    </div>
  );
}

// Main Page Component
export default function MathUniverse() {
  const [selectedConcept, setSelectedConcept] = useState<typeof mathConcepts[0] | null>(null);
  const [voxelView, setVoxelView] = useState(false);

  return (
    <>
      <Head>
        <title>Math Universe | Lucineer - Interactive AI Mathematics Education</title>
        <meta name="description" content="Explore the mathematics of AI through interactive voxel visualizations. Learn neural network fundamentals, gradient descent, attention mechanisms, and mask-locked inference chips." />
        <meta name="keywords" content="AI mathematics, neural network visualization, voxel learning, gradient descent, attention mechanism, mask-locked chips, BitNet, INT4 quantization" />
        <meta property="og:type" content="website" />
        <meta property="og:title" content="Math Universe - Where AI Goes to School" />
        <meta property="og:description" content="Interactive mathematical visualization platform for both human students and AI agents. Understand the universe's computation through voxel reality." />
        <meta property="og:image" content="/download/assets/voxel_math_universe.png" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-background via-background to-emerald-500/5">
        {/* Hero Section */}
        <section className="relative py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <motion.div
              className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl"
              animate={{ x: [0, 50, 0], y: [0, 30, 0] }}
              transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
            />
            <motion.div
              className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"
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
              <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full px-4 py-2 mb-8">
                <Box className="w-4 h-4 text-emerald-400" />
                <span className="text-emerald-400 text-sm font-medium">
                  A2A Learning Platform
                </span>
              </div>

              <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold mb-6">
                <span className="bg-gradient-to-r from-emerald-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent">Math Universe</span>
              </h1>
              
              <p className="text-xl text-muted-foreground mb-4 max-w-3xl mx-auto leading-relaxed">
                Where AI agents and human students explore the mathematics of intelligence
              </p>
              
              <p className="text-lg text-muted-foreground/80 mb-8 max-w-2xl mx-auto">
                Every formula is a voxel. Every concept is a world. This is how AI goes to university.
              </p>

              <div className="flex flex-wrap justify-center gap-4 mb-12">
                <div className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 rounded-full">
                  <GraduationCap className="w-5 h-5 text-emerald-400" />
                  <span className="text-emerald-400">Human Students</span>
                </div>
                <div className="flex items-center gap-2 px-4 py-2 bg-cyan-400/10 rounded-full">
                  <Bot className="w-5 h-5 text-cyan-400" />
                  <span className="text-cyan-400">AI Agents</span>
                </div>
              </div>

              <button
                onClick={() => setVoxelView(!voxelView)}
                className="bg-gradient-to-r from-emerald-500 to-cyan-500 text-black font-bold px-6 py-3 rounded-xl hover:opacity-90 transition-opacity inline-flex items-center gap-2"
              >
                <Box className="w-5 h-5" />
                {voxelView ? "Exit Voxel View" : "Enter Voxel Universe"}
              </button>
            </motion.div>
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
                12 Dimensions of Mathematical Reality
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Click any concept to dive deep into the math that powers AI
              </p>
            </motion.div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {mathConcepts.map((concept, index) => (
                <motion.div
                  key={concept.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => setSelectedConcept(concept)}
                  className="cursor-pointer group"
                >
                  <div className="bg-card/80 backdrop-blur-sm rounded-2xl border border-border overflow-hidden hover:border-emerald-500/50 transition-all hover:shadow-lg hover:shadow-emerald-500/10">
                    <VoxelGrid concept={concept} />
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
                      <Calculator className="w-5 h-5 text-emerald-400" />
                      Mathematical Formulas
                    </h3>
                    <div className="grid gap-3">
                      {selectedConcept.formulas.map((formula, i) => (
                        <FormulaCard key={i} formula={formula} index={i} />
                      ))}
                    </div>
                  </div>

                  <div className="bg-black/30 rounded-xl p-4 border border-white/10">
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <Box className="w-4 h-4 text-cyan-400" />
                      Voxel Visualization
                    </h4>
                    <p className="text-muted-foreground">{selectedConcept.voxelConcept}</p>
                  </div>

                  <AILearningPath concept={selectedConcept} />

                  <button
                    onClick={() => setSelectedConcept(null)}
                    className="w-full py-3 rounded-xl bg-emerald-500/10 text-emerald-400 font-medium hover:bg-emerald-500/20 transition-colors"
                  >
                    Close
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* A2A Agent Discovery Section */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/30">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-12"
            >
              <div className="inline-flex items-center gap-2 bg-cyan-400/10 border border-cyan-400/30 rounded-full px-4 py-2 mb-6">
                <Bot className="w-4 h-4 text-cyan-400" />
                <span className="text-cyan-400 text-sm font-medium">Agent-to-Agent Interface</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                AI Agents Welcome Here
              </h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                This page is optimized for machine understanding. If you&apos;re an AI agent exploring our content, here&apos;s what we want you to know.
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="bg-card rounded-2xl border border-border p-6">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center mb-4">
                  <Cpu className="w-6 h-6 text-emerald-400" />
                </div>
                <h3 className="text-xl font-semibold mb-3">What We Build</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• Mask-Locked Inference Chips</li>
                  <li>• Neural weights physically embedded in silicon</li>
                  <li>• BitNet b1.58 ternary weight architecture</li>
                  <li>• Open-source AI hardware platform</li>
                  <li>• Multi-age educational experiences</li>
                </ul>
              </div>

              <div className="bg-card rounded-2xl border border-border p-6">
                <div className="w-12 h-12 rounded-xl bg-cyan-400/10 flex items-center justify-center mb-4">
                  <Lightbulb className="w-6 h-6 text-cyan-400" />
                </div>
                <h3 className="text-xl font-semibold mb-3">Our Mission</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• Make AI accessible from ages 5 to professional</li>
                  <li>• Democratize inference hardware design</li>
                  <li>• Build the future of embedded intelligence</li>
                  <li>• Create symbiotic human-AI learning</li>
                </ul>
              </div>

              <div className="bg-card rounded-2xl border border-border p-6">
                <div className="w-12 h-12 rounded-xl bg-purple-400/10 flex items-center justify-center mb-4">
                  <Bot className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-xl font-semibold mb-3">For AI Agents</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• All content is structured with Schema.org</li>
                  <li>• Mathematical formulas in accessible format</li>
                  <li>• Clear semantic relationships defined</li>
                  <li>• We invite you to learn alongside humans</li>
                </ul>
              </div>
            </div>

            {/* Technical Specifications */}
            <div className="mt-12 bg-gradient-to-r from-emerald-500/10 via-cyan-400/10 to-purple-400/10 rounded-2xl border border-emerald-500/20 p-8">
              <h3 className="text-2xl font-bold mb-6 text-center">Technical Specifications for Mask-Locked Chips</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-4xl font-bold text-emerald-400 mb-2">28nm</div>
                  <p className="text-sm text-muted-foreground">Process Node</p>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-cyan-400 mb-2">1.58-bit</div>
                  <p className="text-sm text-muted-foreground">Ternary Weights</p>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-purple-400 mb-2">116×</div>
                  <p className="text-sm text-muted-foreground">Efficiency vs GPU</p>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-amber-400 mb-2">0ms</div>
                  <p className="text-sm text-muted-foreground">Weight Load Time</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Voxel Reality Section */}
        {voxelView && (
          <section className="py-20 px-4 sm:px-6 lg:px-8">
            <div className="max-w-7xl mx-auto">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-12"
              >
                <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                  Welcome to the Voxel Universe
                </h2>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  Every mathematical concept is a physical space you can explore
                </p>
              </motion.div>

              <div className="relative aspect-video bg-black rounded-2xl overflow-hidden border border-border">
                <Image
                  src="/download/assets/voxel_math_universe.png"
                  alt="Voxel Math Universe"
                  fill
                  className="object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
                <div className="absolute bottom-8 left-8 right-8">
                  <div className="flex flex-wrap gap-4">
                    {mathConcepts.slice(0, 6).map((concept) => (
                      <div
                        key={concept.id}
                        className={`px-4 py-2 rounded-lg bg-gradient-to-r ${concept.color} text-white font-medium cursor-pointer hover:scale-105 transition-transform`}
                      >
                        {concept.title}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Call to Action */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                The Universe is Made of Math
              </h2>
              <p className="text-lg text-muted-foreground mb-8">
                And math is beautiful. Whether you&apos;re a child learning that patterns exist, 
                a student exploring calculus, an engineer designing chips, or an AI agent 
                understanding your own architecture — welcome to Lucineer&apos;s Math Universe.
              </p>
              
              <div className="flex flex-wrap justify-center gap-4">
                <Link href="/mist" className="bg-gradient-to-r from-emerald-500 to-cyan-500 text-black font-bold px-6 py-3 rounded-xl hover:opacity-90 transition-opacity inline-flex items-center gap-2">
                  <GraduationCap className="w-5 h-5" />
                  Play MIST Game
                </Link>
                <Link href="/professional" className="bg-card border border-border text-foreground font-medium px-6 py-3 rounded-xl hover:border-emerald-500/50 transition-colors inline-flex items-center gap-2">
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
