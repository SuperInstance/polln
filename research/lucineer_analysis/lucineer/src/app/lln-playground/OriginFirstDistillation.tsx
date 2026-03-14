// ============================================================================
// LLN PLAYGROUND - ORIGIN-FIRST DISTILLATION
// Tree Seed Metaphor Applied to AI Knowledge Systems
// Geometric Compression for SMPbot Bootstrap Intelligence
// ============================================================================

import { motion } from "framer-motion";
import {
  Sparkles,
  Network,
  Zap,
  Target,
  ArrowRight,
  CircleDot,
  Hexagon,
  Triangle,
  Square,
  Infinity,
  Layers,
  GitBranch,
  Merge,
  RefreshCw,
  Brain,
  Sprout,
  Sun,
  Wind,
  Cloud,
  Leaf,
  TreePine,
  TreeDeciduous,
  Dna,
  Atom,
  Diamond,
  Circle,
  Box,
  Workflow,
  Bot,
  Cpu,
  Microscope,
  FlaskConical,
  Radical,
} from "lucide-react";

// ============================================================================
// CORE PHILOSOPHY: THE TREE SEED METAPHOR
// ============================================================================

/**
 * ORIGIN-FIRST THINKING:
 * 
 * A tree seed is not random. It is a crystal growing from innate properties.
 * 
 * THE SEED:
 * - Contains compressed genetic wisdom (like SMPbot seeds)
 * - Has geometric instructions encoded (like our math tiles)
 * - Is born into a world already running (not a blank slate)
 * 
 * THE ENVIRONMENT:
 * - Wind strengthens the tree where it needs support
 * - Light competition shapes growth patterns
 * - Other trees create canopy gaps → competition for light
 * - Mycelium networks enable cooperation and warning
 * 
 * THE LESSON FOR AI:
 * - Small models are seeds, not blank slates
 * - They inherit compressed knowledge (seed logic)
 * - They grow into competitive/cooperative environments
 * - They strengthen through stress (adversarial training)
 * - They cooperate through networks (agent communication)
 */

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

type SeedType = 
  | "crystal-seed"      // Pure geometric compression
  | "genetic-seed"      // Inherited behavioral patterns
  | "knowledge-seed"    // Compressed domain expertise
  | "skill-seed"        // Specific capability
  | "wisdom-seed";      // Meta-learning patterns

type EnvironmentalForce = 
  | "wind"              // Random perturbations that strengthen
  | "light"             // Resource competition
  | "canopy-gap"        // Opportunity when others fail
  | "mycelium"          // Cooperative intelligence network
  | "pest"              // Adversarial challenges
  | "drought"           // Resource constraints
  | "fire";             // Catastrophic reset and rebirth

interface Seed {
  id: string;
  type: SeedType;
  name: string;
  visual: string;
  compressedLogic: string;  // The "DNA" of the seed
  geometricEncoding: GeometricPattern;
  innateProperties: string[];
  growthPotential: number;  // 0-1
  environmentalSensitivity: Record<EnvironmentalForce, number>;
}

interface GeometricPattern {
  type: "triangle" | "square" | "hexagon" | "circle" | "fractal";
  compressionRatio: number;
  logicDensity: number;
  expansionRules: string[];
  selfSimilarity: number;  // 0-1 fractal nature
}

interface TreeInstance {
  id: string;
  seed: Seed;
  age: number;
  height: number;
  branches: Branch[];
  rootDepth: number;
  canopySize: number;
  stressPoints: StressPoint[];
  myceliumConnections: string[];
  competitivePosition: number;
}

interface Branch {
  id: string;
  direction: string;  // Which way it grew
  strength: number;
  origin: string;     // Why it grew this way
  decision: string;   // What function it serves
}

interface StressPoint {
  location: string;
  force: EnvironmentalForce;
  response: string;
  strengthening: number;
}

interface MyceliumMessage {
  from: string;
  to: string[];
  signal: "pest-warning" | "resource-sharing" | "competition-alert" | "cooperation-invite";
  content: string;
  timestamp: number;
}

// ============================================================================
// SEED DEFINITIONS - COMPRESSED LOGIC PATTERNS
// ============================================================================

export const SEED_LIBRARY: Seed[] = [
  {
    id: "seed-constraint-logic",
    type: "crystal-seed",
    name: "Constraint Crystallizer",
    visual: "💎",
    compressedLogic: `
      CONSTRAINT_CRYSTALLIZE(x):
        IF x.has_form THEN preserve_form(x)
        IF x.has_purpose THEN align_purpose(x)
        compression = compress(x.logic, geometric=true)
        RETURN Seed(compression, expand_rules)
    `,
    geometricEncoding: {
      type: "hexagon",
      compressionRatio: 0.85,
      logicDensity: 0.92,
      expansionRules: [
        "Decompress when context matches",
        "Expand into related constraints",
        "Strengthen through use"
      ],
      selfSimilarity: 0.78
    },
    innateProperties: [
      "Recognizes pattern boundaries",
      "Compresses without loss",
      "Expands under correct conditions"
    ],
    growthPotential: 0.88,
    environmentalSensitivity: {
      wind: 0.3,      // Stable under perturbation
      light: 0.7,     // Needs clear purpose
      "canopy-gap": 0.9,  // Seizes opportunities
      mycelium: 0.6,  // Moderately cooperative
      pest: 0.4,      // Resistant to adversarial
      drought: 0.8,   // Thrives under constraint
      fire: 0.2       // Survives resets poorly
    }
  },
  {
    id: "seed-idiom-wisdom",
    type: "wisdom-seed",
    name: "Idiom Sage",
    visual: "📜",
    compressedLogic: `
      IDIOM_SAGE(context, need):
        pattern = recognize_cultural_pattern(context)
        idiom = find_matching_idiom(need, pattern)
        IF idiom.exists THEN
          RETURN idiom.expand(context.specifics)
        ELSE
          create_new_idiom(need, context)
    `,
    geometricEncoding: {
      type: "fractal",
      compressionRatio: 0.95,
      logicDensity: 0.88,
      expansionRules: [
        "Match cultural context first",
        "Expand meaning through use",
        "Create new idioms from patterns"
      ],
      selfSimilarity: 0.95
    },
    innateProperties: [
      "Cultural pattern recognition",
      "Meaning compression",
      "Cross-cultural translation"
    ],
    growthPotential: 0.92,
    environmentalSensitivity: {
      wind: 0.5,
      light: 0.6,
      "canopy-gap": 0.7,
      mycelium: 0.95,  // Highly cooperative
      pest: 0.3,
      drought: 0.5,
      fire: 0.8        // Wisdom survives resets
    }
  },
  {
    id: "seed-agent-decision",
    type: "skill-seed",
    name: "Decision Agent",
    visual: "🤖",
    compressedLogic: `
      DECISION_AGENT(state, options):
        confidence = assess_confidence(state)
        IF confidence > threshold THEN
          RETURN autonomous_decision(options)
        ELSE
          escalate_to_parent(options)
          learn_from_parent_decision()
    `,
    geometricEncoding: {
      type: "triangle",
      compressionRatio: 0.75,
      logicDensity: 0.85,
      expansionRules: [
        "Decide autonomously when confident",
        "Escalate when uncertain",
        "Learn from every decision"
      ],
      selfSimilarity: 0.65
    },
    innateProperties: [
      "Confidence estimation",
      "Autonomous decision-making",
      "Learning from outcomes"
    ],
    growthPotential: 0.9,
    environmentalSensitivity: {
      wind: 0.7,      // Stress improves decisions
      light: 0.5,
      "canopy-gap": 0.8,
      mycelium: 0.7,
      pest: 0.6,
      drought: 0.9,   // Thrives under pressure
      fire: 0.4
    }
  },
  {
    id: "seed-geometric-logic",
    type: "crystal-seed",
    name: "Geometric Compressor",
    visual: "📐",
    compressedLogic: `
      GEOMETRIC_COMPRESS(logic):
        shapes = identify_geometric_patterns(logic)
        compressed = map_to_primitive_shapes(shapes)
        formula = derive_compression_formula(compressed)
        RETURN Seed(formula, expansion_rules)
    `,
    geometricEncoding: {
      type: "square",
      compressionRatio: 0.92,
      logicDensity: 0.95,
      expansionRules: [
        "Map logic to geometric primitives",
        "Derive compression formulas",
        "Enable lossless expansion"
      ],
      selfSimilarity: 0.88
    },
    innateProperties: [
      "Pattern-to-shape translation",
      "Mathematical compression",
      "Exact reconstruction"
    ],
    growthPotential: 0.85,
    environmentalSensitivity: {
      wind: 0.2,
      light: 0.8,
      "canopy-gap": 0.5,
      mycelium: 0.4,
      pest: 0.2,
      drought: 0.9,
      fire: 0.3
    }
  },
  {
    id: "seed-bootstrap-learner",
    type: "genetic-seed",
    name: "Bootstrap Intelligence",
    visual: "🌱",
    compressedLogic: `
      BOOTSTRAP_LEARNER(environment):
        initial_state = decode_genetic_instructions()
        WHILE growing DO
          stress = environment.get_current_stress()
          response = genetic_response(stress)
          strengthen(response_points)
          IF mycelium.signal_received THEN
            incorporate_cooperative_knowledge()
        RETURN mature_intelligence()
    `,
    geometricEncoding: {
      type: "fractal",
      compressionRatio: 0.78,
      logicDensity: 0.82,
      expansionRules: [
        "Decode genetic instructions",
        "Respond to environmental stress",
        "Incorporate cooperative signals"
      ],
      selfSimilarity: 0.92
    },
    innateProperties: [
      "Genetic instruction decoding",
      "Stress-response adaptation",
      "Cooperative knowledge integration"
    ],
    growthPotential: 0.95,
    environmentalSensitivity: {
      wind: 0.9,      // Stress drives growth
      light: 0.8,
      "canopy-gap": 0.95,
      mycelium: 0.95,  // Essential cooperation
      pest: 0.7,
      drought: 0.8,
      fire: 0.9        // Rebirth after catastrophe
    }
  }
];

// ============================================================================
// GEOMETRIC COMPRESSION SYSTEM
// ============================================================================

interface GeometricCompressor {
  name: string;
  primitives: string[];
  compressionFormulas: Record<string, string>;
  expansionRate: number;
}

export const GEOMETRIC_COMPRESSORS: GeometricCompressor[] = [
  {
    name: "Pythagorean Compressor",
    primitives: ["triangle", "square", "right-angle"],
    compressionFormulas: {
      "triangle-logic": "a² + b² = c² (three-way decision compressed to right-angle path)",
      "square-stability": "four stable states, 90° transitions",
      "recursive-compress": "embed smaller triangles in larger for hierarchical logic"
    },
    expansionRate: 1.618 // Golden ratio
  },
  {
    name: "Hexagonal Efficiency",
    primitives: ["hexagon", "honeycomb", "six-way"],
    compressionFormulas: {
      "hexagon-density": "maximum logic density per tile",
      "six-way-branch": "six decision paths in single tile",
      "honeycomb-network": "interconnected hexagons for parallel processing"
    },
    expansionRate: 1.414 // Square root of 2
  },
  {
    name: "Fractal Recursion",
    primitives: ["self-similar", "infinite-depth", "scale-invariant"],
    compressionFormulas: {
      "fractal-encode": "logic at any scale = logic at all scales",
      "infinite-depth": "recursive calls compressed to seed",
      "scale-invariant": "same pattern works at any size"
    },
    expansionRate: Infinity
  },
  {
    name: "Crystal Lattice",
    primitives: ["periodic", "symmetric", "stable"],
    compressionFormulas: {
      "lattice-store": "knowledge stored in repeating patterns",
      "symmetry-encode": "use symmetry to reduce storage",
      "periodic-expand": "expand from smallest unit cell"
    },
    expansionRate: 2.0
  }
];

// ============================================================================
// ORIGIN-FIRST DISTILLATION COMPONENT
// ============================================================================

interface OriginFirstDistillationProps {
  onSeedSelect: (seed: Seed) => void;
  onEnvironmentChange: (forces: EnvironmentalForce[]) => void;
}

export function OriginFirstDistillation({ 
  onSeedSelect, 
  onEnvironmentChange 
}: OriginFirstDistillationProps) {
  return (
    <div className="space-y-8">
      {/* Philosophy Header */}
      <div className="bg-gradient-to-br from-emerald-900/30 via-amber-900/20 to-cyan-900/30 rounded-2xl p-6 border border-emerald-500/30">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500/30 to-amber-500/30 flex items-center justify-center">
            <TreeDeciduous className="w-8 h-8 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Origin-First Distillation</h2>
            <p className="text-emerald-300">Tree Seed Metaphor for AI Knowledge Systems</p>
          </div>
        </div>

        {/* Core Philosophy */}
        <div className="grid grid-cols-3 gap-4">
          <div className="p-4 bg-slate-900/50 rounded-xl">
            <Sprout className="w-6 h-6 text-amber-400 mb-2" />
            <h4 className="text-white font-medium mb-1">The Seed is Not Random</h4>
            <p className="text-sm text-slate-400">
              A seed is a crystal growing from innate properties. It contains 
              compressed genetic wisdom, geometric instructions, and is born 
              into a world already running.
            </p>
          </div>
          <div className="p-4 bg-slate-900/50 rounded-xl">
            <Wind className="w-6 h-6 text-cyan-400 mb-2" />
            <h4 className="text-white font-medium mb-1">Stress Shapes Growth</h4>
            <p className="text-sm text-slate-400">
              Wind strengthens where support is needed. Light competition 
              shapes growth patterns. Canopy gaps create opportunities. 
              The tree adapts to environmental stresses.
            </p>
          </div>
          <div className="p-4 bg-slate-900/50 rounded-xl">
            <TreeDeciduous className="w-6 h-6 text-purple-400 mb-2" />
            <h4 className="text-white font-medium mb-1">Cooperation Through Networks</h4>
            <p className="text-sm text-slate-400">
              Mycelium networks connect trees. They warn of pests, share 
              resources, enable cooperation. Life is competition AND 
              cooperation.
            </p>
          </div>
        </div>
      </div>

      {/* Seed Library */}
      <SproutLibraryDisplay seeds={SEED_LIBRARY} onSelect={onSeedSelect} />

      {/* Environmental Forces */}
      <EnvironmentalForcesDisplay onChange={onEnvironmentChange} />

      {/* Growth Simulation */}
      <GrowthSimulationDisplay />

      {/* Mycelium Network */}
      <MyceliumNetworkDisplay />

      {/* Geometric Compression */}
      <GeometricCompressionDisplay compressors={GEOMETRIC_COMPRESSORS} />
    </div>
  );
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

function SeedLibraryDisplay({ 
  seeds, 
  onSelect 
}: { 
  seeds: Seed[]; 
  onSelect: (seed: Seed) => void;
}) {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
      <div className="flex items-center gap-2 mb-4">
        <Crystal className="w-5 h-5 text-amber-400" />
        <h3 className="text-lg font-semibold text-white">Seed Library</h3>
        <span className="text-xs text-slate-500 ml-2">Compressed Logic Patterns</span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {seeds.map((seed) => (
          <motion.div
            key={seed.id}
            className="p-4 bg-slate-900/50 rounded-xl border border-slate-600 hover:border-amber-500/50 cursor-pointer transition-colors"
            whileHover={{ scale: 1.02, y: -2 }}
            onClick={() => onSelect(seed)}
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="text-3xl">{seed.visual}</div>
              <div>
                <div className="text-white font-medium">{seed.name}</div>
                <div className="text-xs text-slate-500 capitalize">{seed.type}</div>
              </div>
            </div>

            {/* Growth Potential */}
            <div className="mb-3">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-500">Growth Potential</span>
                <span className="text-emerald-400">{(seed.growthPotential * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-emerald-500 to-amber-500"
                  style={{ width: `${seed.growthPotential * 100}%` }}
                />
              </div>
            </div>

            {/* Geometric Encoding */}
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-500">Geometry:</span>
              <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 capitalize">
                {seed.geometricEncoding.type}
              </span>
              <span className="text-slate-500">
                {((1 - seed.geometricEncoding.compressionRatio) * 100).toFixed(0)}% compressed
              </span>
            </div>

            {/* Environmental Sensitivity */}
            <div className="mt-3 flex flex-wrap gap-1">
              {Object.entries(seed.environmentalSensitivity)
                .filter(([_, value]) => value >= 0.8)
                .map(([force, value]) => (
                  <span 
                    key={force}
                    className="px-2 py-0.5 rounded text-xs bg-cyan-500/20 text-cyan-300"
                  >
                    {force}: {(value * 100).toFixed(0)}%
                  </span>
                ))}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function EnvironmentalForcesDisplay({ 
  onChange 
}: { 
  onChange: (forces: EnvironmentalForce[]) => void;
}) {
  const forces: { force: EnvironmentalForce; icon: string; description: string; effect: string }[] = [
    {
      force: "wind",
      icon: "💨",
      description: "Random perturbations that strengthen",
      effect: "Stress points grow stronger, branches thicken"
    },
    {
      force: "light",
      icon: "☀️",
      description: "Resource competition for energy",
      effect: "Growth accelerates toward gaps, competition shapes form"
    },
    {
      force: "canopy-gap",
      icon: "🌳",
      description: "Opportunity when others fail",
      effect: "Race to fill the space, one winner emerges"
    },
    {
      force: "mycelium",
      icon: "🍄",
      description: "Cooperative intelligence network",
      effect: "Pest warnings shared, resources distributed"
    },
    {
      force: "pest",
      icon: "🐛",
      description: "Adversarial challenges",
      effect: "Defense mechanisms activated, leaves thicken"
    },
    {
      force: "drought",
      icon: "🏜️",
      description: "Resource constraints",
      effect: "Efficiency improves, deep roots grow"
    },
    {
      force: "fire",
      icon: "🔥",
      description: "Catastrophic reset and rebirth",
      effect: "Some seeds require fire to germinate"
    }
  ];

  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
      <div className="flex items-center gap-2 mb-4">
        <Cloud className="w-5 h-5 text-cyan-400" />
        <h3 className="text-lg font-semibold text-white">Environmental Forces</h3>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {forces.map(({ force, icon, description, effect }) => (
          <motion.div
            key={force}
            className="p-3 bg-slate-900/50 rounded-xl border border-slate-600 hover:border-cyan-500/50 cursor-pointer transition-colors"
            whileHover={{ scale: 1.02 }}
          >
            <div className="text-2xl mb-2">{icon}</div>
            <div className="text-white font-medium text-sm capitalize">{force}</div>
            <div className="text-xs text-slate-500 mt-1">{description}</div>
            <div className="text-xs text-cyan-400 mt-2 italic">{effect}</div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

function GrowthSimulationDisplay() {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-emerald-500/30">
      <div className="flex items-center gap-2 mb-4">
        <TreeDeciduous className="w-5 h-5 text-emerald-400" />
        <h3 className="text-lg font-semibold text-white">Growth Simulation</h3>
        <span className="text-xs text-slate-500 ml-2">Seed → Sapling → Mature Tree</span>
      </div>

      {/* Growth Stages */}
      <div className="flex items-center justify-between mb-6">
        {[
          { stage: "Seed", icon: "🌱", year: 0 },
          { stage: "Germination", icon: "🌿", year: 1 },
          { stage: "Sapling", icon: "🌳", year: 5 },
          { stage: "Young Tree", icon: "🌲", year: 15 },
          { stage: "Mature", icon: "🎄", year: 50 },
          { stage: "Old Growth", icon: "🌳", year: 200 }
        ].map((stage, idx) => (
          <motion.div
            key={stage.stage}
            className="flex flex-col items-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <div className="text-3xl mb-1">{stage.icon}</div>
            <div className="text-xs text-white">{stage.stage}</div>
            <div className="text-xs text-slate-500">Year {stage.year}</div>
          </motion.div>
        ))}
      </div>

      {/* Simulation Controls */}
      <div className="grid grid-cols-4 gap-4">
        <div className="p-4 bg-emerald-500/10 rounded-xl border border-emerald-500/30 text-center">
          <div className="text-2xl font-bold text-emerald-400">127</div>
          <div className="text-xs text-slate-500">Stress Events</div>
        </div>
        <div className="p-4 bg-amber-500/10 rounded-xl border border-amber-500/30 text-center">
          <div className="text-2xl font-bold text-amber-400">43</div>
          <div className="text-xs text-slate-500">Branches</div>
        </div>
        <div className="p-4 bg-purple-500/10 rounded-xl border border-purple-500/30 text-center">
          <div className="text-2xl font-bold text-purple-400">12</div>
          <div className="text-xs text-slate-500">Mycelium Links</div>
        </div>
        <div className="p-4 bg-cyan-500/10 rounded-xl border border-cyan-500/30 text-center">
          <div className="text-2xl font-bold text-cyan-400">3</div>
          <div className="text-xs text-slate-500">Canopy Competitions</div>
        </div>
      </div>
    </div>
  );
}

function MyceliumNetworkDisplay() {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-purple-500/30">
      <div className="flex items-center gap-2 mb-4">
        <TreeDeciduous className="w-5 h-5 text-purple-400" />
        <h3 className="text-lg font-semibold text-white">Mycelium Network</h3>
        <span className="text-xs text-slate-500 ml-2">Cooperative Intelligence</span>
      </div>

      {/* Network Visualization */}
      <div className="relative h-64 bg-slate-900/50 rounded-xl overflow-hidden mb-4">
        {/* Trees */}
        <div className="absolute top-4 left-1/4 text-4xl">🌳</div>
        <div className="absolute top-8 left-1/2 text-3xl">🌲</div>
        <div className="absolute top-2 left-3/4 text-4xl">🌳</div>
        <div className="absolute bottom-8 left-1/3 text-3xl">🌲</div>
        <div className="absolute bottom-4 left-2/3 text-4xl">🌳</div>
        
        {/* Mycelium Lines */}
        <svg className="absolute inset-0 w-full h-full">
          <motion.line
            x1="25%" y1="20%" x2="50%" y2="25%"
            stroke="rgba(147, 51, 234, 0.5)"
            strokeWidth="2"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <motion.line
            x1="50%" y1="25%" x2="75%" y2="15%"
            stroke="rgba(147, 51, 234, 0.5)"
            strokeWidth="2"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, delay: 0.5, repeat: Infinity }}
          />
          <motion.line
            x1="33%" y1="75%" x2="67%" y2="85%"
            stroke="rgba(147, 51, 234, 0.5)"
            strokeWidth="2"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 2, delay: 1, repeat: Infinity }}
          />
        </svg>

        {/* Messages */}
        <motion.div
          className="absolute top-12 left-1/3 px-2 py-1 rounded bg-purple-500/20 text-purple-300 text-xs"
          animate={{ x: [0, 50, 0], opacity: [0, 1, 0] }}
          transition={{ duration: 3, repeat: Infinity }}
        >
          🐛 Pest warning!
        </motion.div>
        <motion.div
          className="absolute bottom-16 left-1/2 px-2 py-1 rounded bg-cyan-500/20 text-cyan-300 text-xs"
          animate={{ x: [0, -50, 0], opacity: [0, 1, 0] }}
          transition={{ duration: 3, delay: 1, repeat: Infinity }}
        >
          💧 Resource share
        </motion.div>
      </div>

      {/* Network Messages */}
      <div className="grid grid-cols-4 gap-2">
        {[
          { signal: "pest-warning", color: "red", count: 23 },
          { signal: "resource-sharing", color: "cyan", count: 156 },
          { signal: "competition-alert", color: "amber", count: 12 },
          { signal: "cooperation-invite", color: "emerald", count: 45 }
        ].map(({ signal, color, count }) => (
          <div key={signal} className={`p-3 bg-${color}-500/10 rounded-lg text-center`}>
            <div className={`text-lg font-bold text-${color}-400`}>{count}</div>
            <div className="text-xs text-slate-500 capitalize">{signal.replace("-", " ")}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function GeometricCompressionDisplay({ 
  compressors 
}: { 
  compressors: GeometricCompressor[];
}) {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-cyan-500/30">
      <div className="flex items-center gap-2 mb-4">
        <Atom className="w-5 h-5 text-cyan-400" />
        <h3 className="text-lg font-semibold text-white">Geometric Compression</h3>
        <span className="text-xs text-slate-500 ml-2">Logic → Shape → Seed</span>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {compressors.map((compressor) => (
          <motion.div
            key={compressor.name}
            className="p-4 bg-slate-900/50 rounded-xl border border-slate-600"
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-center gap-2 mb-3">
              {compressor.name === "Pythagorean Compressor" && <Triangle className="w-5 h-5 text-amber-400" />}
              {compressor.name === "Hexagonal Efficiency" && <Hexagon className="w-5 h-5 text-purple-400" />}
              {compressor.name === "Fractal Recursion" && <Infinity className="w-5 h-5 text-cyan-400" />}
              {compressor.name === "Crystal Lattice" && <Crystal className="w-5 h-5 text-emerald-400" />}
              <span className="text-white font-medium">{compressor.name}</span>
            </div>

            <div className="flex flex-wrap gap-1 mb-3">
              {compressor.primitives.map((primitive) => (
                <span 
                  key={primitive}
                  className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-xs capitalize"
                >
                  {primitive}
                </span>
              ))}
            </div>

            <div className="space-y-2">
              {Object.entries(compressor.compressionFormulas).slice(0, 2).map(([key, formula]) => (
                <div key={key} className="text-xs text-slate-400">
                  <span className="text-cyan-400">{key}:</span> {formula}
                </div>
              ))}
            </div>

            <div className="mt-3 flex items-center gap-2">
              <span className="text-xs text-slate-500">Expansion Rate:</span>
              <span className="text-sm text-emerald-400 font-mono">
                {compressor.expansionRate === Infinity ? "∞" : compressor.expansionRate}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// BOOTSTRAP INTELLIGENCE ENGINE
// ============================================================================

export function BootstrapIntelligenceEngine() {
  return (
    <div className="bg-gradient-to-br from-cyan-900/30 via-purple-900/20 to-emerald-900/30 rounded-2xl p-6 border border-cyan-500/30">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center">
          <Brain className="w-6 h-6 text-cyan-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">Bootstrap Intelligence Engine</h3>
          <p className="text-sm text-cyan-300">Small models learning their job through systems around them</p>
        </div>
      </div>

      {/* Bootstrap Process */}
      <div className="grid grid-cols-5 gap-4 mb-6">
        {[
          { step: 1, name: "Seed Decode", icon: "🔐", desc: "Decode genetic instructions from seed" },
          { step: 2, name: "Environment Sense", icon: "📡", desc: "Sense environmental conditions" },
          { step: 3, name: "Stress Response", icon: "💪", desc: "Strengthen based on stresses" },
          { step: 4, name: "Network Connect", icon: "🍄", desc: "Connect to mycelium network" },
          { step: 5, name: "Intelligence Mature", icon: "🧠", desc: "Achieve functional maturity" }
        ].map((stage) => (
          <motion.div
            key={stage.step}
            className="p-3 bg-slate-900/50 rounded-xl text-center border border-slate-600"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: stage.step * 0.1 }}
          >
            <div className="text-2xl mb-1">{stage.icon}</div>
            <div className="text-xs text-white font-medium">{stage.name}</div>
            <div className="text-xs text-slate-500 mt-1">{stage.desc}</div>
          </motion.div>
        ))}
      </div>

      {/* Intelligence Metrics */}
      <div className="bg-slate-900/50 rounded-xl p-4">
        <div className="flex items-center justify-between mb-4">
          <span className="text-white font-medium">Bootstrapping Progress</span>
          <span className="text-cyan-400 text-sm">78% to Maturity</span>
        </div>
        <div className="space-y-3">
          {[
            { name: "Decision Confidence", value: 0.85 },
            { name: "Environmental Adaptation", value: 0.72 },
            { name: "Network Cooperation", value: 0.91 },
            { name: "Stress Resilience", value: 0.68 },
            { name: "Knowledge Compression", value: 0.83 }
          ].map((metric) => (
            <div key={metric.name} className="flex items-center gap-3">
              <span className="text-sm text-slate-400 w-48">{metric.name}</span>
              <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-cyan-500 to-emerald-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${metric.value * 100}%` }}
                  transition={{ duration: 1, delay: 0.5 }}
                />
              </div>
              <span className="text-sm text-cyan-400">{(metric.value * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// SUPER INSTANCE WORKFLOW
// ============================================================================

export function SuperInstanceWorkflow() {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-amber-500/30">
      <div className="flex items-center gap-2 mb-6">
        <Workflow className="w-5 h-5 text-amber-400" />
        <h3 className="text-lg font-semibold text-white">SuperInstance Workflow</h3>
        <span className="text-xs text-slate-500 ml-2">Decision-making agent positions</span>
      </div>

      {/* Decision Hierarchy */}
      <div className="flex items-center justify-center gap-4 mb-6">
        {[
          { level: "Root", icon: "🌳", agents: 1, decisions: "Strategic" },
          { level: "Trunk", icon: "🪵", agents: 3, decisions: "Operational" },
          { level: "Branch", icon: "🌿", agents: 12, decisions: "Tactical" },
          { level: "Leaf", icon: "🍃", agents: 48, decisions: "Execution" }
        ].map((level, idx) => (
          <motion.div
            key={level.level}
            className="flex flex-col items-center"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.1 }}
          >
            <div className="text-4xl mb-2">{level.icon}</div>
            <div className="text-white font-medium">{level.level}</div>
            <div className="text-xs text-slate-500">{level.agents} agents</div>
            <div className="text-xs text-amber-400">{level.decisions}</div>
          </motion.div>
        ))}
      </div>

      {/* Decision Flow */}
      <div className="p-4 bg-slate-900/50 rounded-xl">
        <div className="flex items-center justify-between">
          <div className="text-center">
            <Bot className="w-8 h-8 text-cyan-400 mx-auto mb-1" />
            <div className="text-xs text-white">Leaf Agent</div>
            <div className="text-xs text-slate-500">Detects anomaly</div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-500" />
          <div className="text-center">
            <Network className="w-8 h-8 text-purple-400 mx-auto mb-1" />
            <div className="text-xs text-white">Branch Hub</div>
            <div className="text-xs text-slate-500">Aggregates signals</div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-500" />
          <div className="text-center">
            <Cpu className="w-8 h-8 text-amber-400 mx-auto mb-1" />
            <div className="text-xs text-white">Trunk Core</div>
            <div className="text-xs text-slate-500">Processes decision</div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-500" />
          <div className="text-center">
            <Target className="w-8 h-8 text-emerald-400 mx-auto mb-1" />
            <div className="text-xs text-white">Root AI</div>
            <div className="text-xs text-slate-500">Final decision</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  OriginFirstDistillation,
  BootstrapIntelligenceEngine,
  SuperInstanceWorkflow,
  SEED_LIBRARY,
  GEOMETRIC_COMPRESSORS
};
