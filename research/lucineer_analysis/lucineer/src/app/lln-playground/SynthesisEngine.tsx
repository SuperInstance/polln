// ============================================================================
// LLN PLAYGROUND - SYNTHESIS ENGINE
// Mix & Match Teaching Methods to Create New Educational Tools
// Combination Tiles for Higher-Order Abstractions
// 12 Rounds of Creative Synthesis
// ============================================================================

import { motion } from "framer-motion";
import {
  GraduationCap,
  Users,
  Globe,
  MessageCircle,
  Sparkles,
  BookOpen,
  Brain,
  Lightbulb,
  CheckCircle,
  ArrowRight,
  Star,
  Trophy,
  Target,
  Clock,
  Languages,
  Zap,
  Layers,
  GitMerge,
  Atom,
  Palette,
  Music,
  Drama,
  Puzzle,
  Infinity,
  Heart,
  Compass,
  Microscope,
  PenTool,
  Video,
  Play,
  Shuffle,
  RefreshCw,
  Network,
  TreeDeciduous,
  Flame,
  Diamond,
  Hexagon,
} from "lucide-react";

// ============================================================================
// TEACHING METHOD INGREDIENTS (Base Components)
// ============================================================================

type BaseMethod = 
  | "socratic"           // Question-driven discovery
  | "project-based"      // Build real projects
  | "inquiry-based"      // Student-led investigation
  | "collaborative"      // Group problem-solving
  | "storytelling"       // Narrative-driven learning
  | "flipped-classroom"  // Students teach each other
  | "debate"             // Adversarial discourse
  | "apprenticeship"     // Master-student relationships
  | "montessori"         // Self-directed exploration
  | "gamification"       // Game mechanics in learning
  | "simulation"         // Immersive scenarios
  | "peer-teaching"      // Students teaching students
  | "case-study"         // Real-world analysis
  | "problem-based"      // Solve complex problems
  | "design-thinking";   // Human-centered design

interface MethodIngredient {
  id: BaseMethod;
  name: string;
  icon: string;
  strength: "discovery" | "creation" | "analysis" | "social" | "expression";
  energyLevel: "calm" | "moderate" | "high" | "intense";
  bestAgeGroup: string[];
  culturalAffinity: Record<string, number>; // culture -> compatibility score
  synergies: BaseMethod[]; // methods that work well combined
  conflicts: BaseMethod[]; // methods that don't mix well
}

// ============================================================================
// BASE METHOD DEFINITIONS
// ============================================================================

export const METHOD_INGREDIENTS: MethodIngredient[] = [
  {
    id: "socratic",
    name: "Socratic Questioning",
    icon: "🧙",
    strength: "discovery",
    energyLevel: "moderate",
    bestAgeGroup: ["teen", "university", "adult", "senior"],
    culturalAffinity: { JP: 0.7, US: 0.9, GH: 0.8, DE: 0.85, IN: 0.75 },
    synergies: ["debate", "inquiry-based", "case-study"],
    conflicts: ["gamification"]
  },
  {
    id: "project-based",
    name: "Project-Based Learning",
    icon: "🔨",
    strength: "creation",
    energyLevel: "high",
    bestAgeGroup: ["child", "teen", "university", "adult"],
    culturalAffinity: { JP: 0.85, US: 0.9, GH: 0.75, DE: 0.95, BR: 0.9 },
    synergies: ["design-thinking", "collaborative", "problem-based"],
    conflicts: []
  },
  {
    id: "inquiry-based",
    name: "Inquiry-Based Learning",
    icon: "🔬",
    strength: "discovery",
    energyLevel: "moderate",
    bestAgeGroup: ["child", "teen", "university"],
    culturalAffinity: { JP: 0.75, US: 0.85, GH: 0.7, DE: 0.9, IN: 0.8 },
    synergies: ["socratic", "problem-based", "case-study"],
    conflicts: ["apprenticeship"]
  },
  {
    id: "collaborative",
    name: "Collaborative Learning",
    icon: "👥",
    strength: "social",
    energyLevel: "high",
    bestAgeGroup: ["child", "teen", "university", "adult", "senior"],
    culturalAffinity: { JP: 0.9, US: 0.75, GH: 0.95, ZA: 0.95, CN: 0.85 },
    synergies: ["project-based", "peer-teaching", "design-thinking"],
    conflicts: ["apprenticeship"]
  },
  {
    id: "storytelling",
    name: "Narrative Learning",
    icon: "📖",
    strength: "expression",
    energyLevel: "calm",
    bestAgeGroup: ["child", "teen", "university", "adult", "senior"],
    culturalAffinity: { JP: 0.85, GH: 0.95, SN: 0.95, EG: 0.9, MX: 0.9 },
    synergies: ["case-study", "simulation", "montessori"],
    conflicts: ["debate"]
  },
  {
    id: "debate",
    name: "Debate & Discourse",
    icon: "⚔️",
    strength: "analysis",
    energyLevel: "intense",
    bestAgeGroup: ["teen", "university", "adult"],
    culturalAffinity: { US: 0.95, UK: 0.9, DE: 0.85, KR: 0.8, JP: 0.6 },
    synergies: ["socratic", "case-study", "peer-teaching"],
    conflicts: ["storytelling", "montessori"]
  },
  {
    id: "gamification",
    name: "Gamified Learning",
    icon: "🎮",
    strength: "creation",
    energyLevel: "high",
    bestAgeGroup: ["child", "teen"],
    culturalAffinity: { KR: 0.95, US: 0.9, BR: 0.85, JP: 0.8, DE: 0.7 },
    synergies: ["simulation", "project-based", "collaborative"],
    conflicts: ["socratic", "storytelling"]
  },
  {
    id: "simulation",
    name: "Immersive Simulation",
    icon: "🎭",
    strength: "creation",
    energyLevel: "high",
    bestAgeGroup: ["teen", "university", "adult"],
    culturalAffinity: { US: 0.85, JP: 0.8, DE: 0.85, KR: 0.85, BR: 0.8 },
    synergies: ["gamification", "case-study", "problem-based"],
    conflicts: []
  },
  {
    id: "design-thinking",
    name: "Design Thinking",
    icon: "🎨",
    strength: "creation",
    energyLevel: "high",
    bestAgeGroup: ["teen", "university", "adult"],
    culturalAffinity: { US: 0.9, DE: 0.85, BR: 0.9, JP: 0.8, KR: 0.75 },
    synergies: ["project-based", "collaborative", "problem-based"],
    conflicts: ["apprenticeship"]
  },
  {
    id: "apprenticeship",
    name: "Apprenticeship Model",
    icon: "🎓",
    strength: "social",
    energyLevel: "calm",
    bestAgeGroup: ["teen", "university", "adult", "senior"],
    culturalAffinity: { JP: 0.95, IN: 0.9, GH: 0.9, EG: 0.85, DE: 0.8 },
    synergies: ["storytelling", "montessori", "case-study"],
    conflicts: ["collaborative", "inquiry-based", "design-thinking"]
  },
  {
    id: "montessori",
    name: "Montessori Approach",
    icon: "🧩",
    strength: "discovery",
    energyLevel: "calm",
    bestAgeGroup: ["child", "teen"],
    culturalAffinity: { US: 0.8, DE: 0.85, IT: 0.9, NL: 0.85, BR: 0.75 },
    synergies: ["storytelling", "inquiry-based", "project-based"],
    conflicts: ["debate", "gamification"]
  },
  {
    id: "peer-teaching",
    name: "Peer Teaching",
    icon: "🔄",
    strength: "social",
    energyLevel: "moderate",
    bestAgeGroup: ["teen", "university", "adult"],
    culturalAffinity: { US: 0.85, JP: 0.7, DE: 0.8, BR: 0.85, IN: 0.75 },
    synergies: ["collaborative", "flipped-classroom", "debate"],
    conflicts: ["apprenticeship"]
  },
  {
    id: "case-study",
    name: "Case Study Method",
    icon: "📋",
    strength: "analysis",
    energyLevel: "moderate",
    bestAgeGroup: ["university", "adult", "senior"],
    culturalAffinity: { US: 0.95, UK: 0.9, DE: 0.85, JP: 0.8, IN: 0.8 },
    synergies: ["socratic", "storytelling", "simulation", "debate"],
    conflicts: []
  },
  {
    id: "problem-based",
    name: "Problem-Based Learning",
    icon: "🧩",
    strength: "analysis",
    energyLevel: "high",
    bestAgeGroup: ["teen", "university", "adult"],
    culturalAffinity: { US: 0.85, DE: 0.9, NL: 0.9, AU: 0.85, SG: 0.85 },
    synergies: ["project-based", "inquiry-based", "design-thinking", "collaborative"],
    conflicts: []
  },
  {
    id: "flipped-classroom",
    name: "Flipped Classroom",
    icon: "🔄",
    strength: "discovery",
    energyLevel: "moderate",
    bestAgeGroup: ["teen", "university", "adult"],
    culturalAffinity: { US: 0.85, UK: 0.8, AU: 0.85, DE: 0.75, KR: 0.7 },
    synergies: ["peer-teaching", "socratic", "collaborative"],
    conflicts: []
  }
];

// ============================================================================
// COMBINATION TILE DEFINITIONS (Higher-Order Abstractions)
// ============================================================================

type TileCategory = 
  | "meta-learning"      // Learning how to learn
  | "cognitive-tool"     // Thinking frameworks
  | "cultural-bridge"    // Cross-cultural understanding
  | "age-transcendent"   // Works across all ages
  | "domain-synthesis"   // Combines multiple domains
  | "creativity-engine"  // Generates new ideas
  | "wisdom-container"   // Stores compressed knowledge
  | "transformation";    // Changes learner state

interface CombinationTile {
  id: string;
  name: string;
  visual: string;
  description: string;
  componentMethods: BaseMethod[];
  category: TileCategory;
  synergyScore: number;
  ageAdaptation: Record<string, string>; // age group -> adaptation
  culturalVariants: Record<string, string>;
  behaviorFormula: string;
  powerLevel: number; // 1-10 abstraction level
  prerequisites: string[];
  outputs: string[];
}

export const COMBINATION_TILES: CombinationTile[] = [
  // META-LEARNING TILES
  {
    id: "tile-learning-to-learn",
    name: "Meta-Learning Engine",
    visual: "🧠🔄🌱",
    description: "Teaches learners how they learn best by combining reflection with practice",
    componentMethods: ["socratic", "peer-teaching", "flipped-classroom"],
    category: "meta-learning",
    synergyScore: 0.94,
    ageAdaptation: {
      child: "Simple reflection: 'What helped you learn today?'",
      teen: "Learning style discovery through experimentation",
      university: "Metacognitive strategies and self-regulation",
      adult: "Professional learning optimization",
      senior: "Wisdom transfer to younger generations"
    },
    culturalVariants: {
      JP: "守破離 (Shuhari) - Learn, Detach, Transcend",
      GH: "Sankofa - Learn from the past to build the future",
      DE: "Bildung - Self-cultivation through learning"
    },
    behaviorFormula: "reflection × practice × feedback = meta-competence",
    powerLevel: 9,
    prerequisites: ["basic-reflection", "growth-mindset"],
    outputs: ["personal-learning-strategy", "metacognitive-awareness"]
  },
  {
    id: "tile-wisdom-synthesis",
    name: "Wisdom Synthesis Engine",
    visual: "💎📚🔄",
    description: "Compresses complex learning into transferable wisdom patterns",
    componentMethods: ["storytelling", "case-study", "apprenticeship"],
    category: "wisdom-container",
    synergyScore: 0.91,
    ageAdaptation: {
      child: "Simple stories with clear lessons",
      teen: "Mentor stories with reflection questions",
      university: "Case analysis with pattern extraction",
      adult: "Experience synthesis for decision-making",
      senior: "Life wisdom crystallization and transfer"
    },
    culturalVariants: {
      JP: "伝承 (Denshō) - Tradition passing",
      GH: "Griot wisdom transmission",
      IN: "Guru-shishya parampara"
    },
    behaviorFormula: "story + case + mentor = compressed wisdom",
    powerLevel: 10,
    prerequisites: ["experience-bank", "reflection-practice"],
    outputs: ["wisdom-nuggets", "decision-patterns", "teaching-stories"]
  },

  // COGNITIVE TOOL TILES
  {
    id: "tile-mental-models",
    name: "Mental Model Toolkit",
    visual: "🧰🧠⚙️",
    description: "Collection of thinking tools from multiple disciplines",
    componentMethods: ["socratic", "case-study", "problem-based"],
    category: "cognitive-tool",
    synergyScore: 0.88,
    ageAdaptation: {
      child: "Simple thinking tools (compare/contrast)",
      teen: "Decision matrices and pros/cons",
      university: "First-principles thinking, systems thinking",
      adult: "Professional decision frameworks",
      senior: "Life-tested mental models"
    },
    culturalVariants: {
      US: "First principles, inversion, circles of competence",
      JP: "Kaizen, Ikigai, Wabi-sabi",
      IN: "Dharma, Karma, Purushartha"
    },
    behaviorFormula: "question × case × problem = mental model",
    powerLevel: 8,
    prerequisites: ["basic-logic", "critical-thinking"],
    outputs: ["decision-frameworks", "thinking-patterns"]
  },
  {
    id: "tile-creativity-catalyst",
    name: "Creativity Catalyst",
    visual: "✨🎨💡",
    description: "Provokes creative thinking through constraint and freedom interplay",
    componentMethods: ["design-thinking", "gamification", "problem-based"],
    category: "creativity-engine",
    synergyScore: 0.93,
    ageAdaptation: {
      child: "Play with constraints (build tallest tower with blocks)",
      teen: "Design challenges with gamified elements",
      university: "Innovation workshops with real constraints",
      adult: "Creative problem-solving for professional challenges",
      senior: "Creative expression and legacy projects"
    },
    culturalVariants: {
      BR: "Carnival creativity - joyful constraint",
      JP: "Haiku discipline - 17 syllables infinity",
      GH: "Adinkra symbols - visual wisdom compression"
    },
    behaviorFormula: "constraint + play + problem = creative breakthrough",
    powerLevel: 8,
    prerequisites: ["openness", "divergent-thinking"],
    outputs: ["creative-solutions", "innovations", "artifacts"]
  },

  // CULTURAL BRIDGE TILES
  {
    id: "tile-cultural-translator",
    name: "Cultural Intelligence Bridge",
    visual: "🌍🌉👥",
    description: "Translates concepts across cultural contexts for global understanding",
    componentMethods: ["storytelling", "collaborative", "peer-teaching"],
    category: "cultural-bridge",
    synergyScore: 0.89,
    ageAdaptation: {
      child: "Stories from around the world",
      teen: "Cultural exchange projects",
      university: "Cross-cultural case studies",
      adult: "Global team collaboration",
      senior: "Cultural heritage preservation"
    },
    culturalVariants: {
      ALL: "Universal human experiences as bridges",
      JP: "Omotenashi - anticipating needs",
      GH: "Ubuntu - I am because we are"
    },
    behaviorFormula: "story + collaboration + exchange = cultural intelligence",
    powerLevel: 7,
    prerequisites: ["cultural-awareness", "empathy"],
    outputs: ["cultural-understanding", "global-competence"]
  },
  {
    id: "tile-universal-patterns",
    name: "Universal Pattern Recognition",
    visual: "🌌🔮✨",
    description: "Identifies patterns that exist across all cultures and domains",
    componentMethods: ["inquiry-based", "case-study", "socratic"],
    category: "wisdom-container",
    synergyScore: 0.92,
    ageAdaptation: {
      child: "Find patterns in nature and stories",
      teen: "Cross-domain pattern hunting",
      university: "Meta-pattern research",
      adult: "Professional pattern recognition",
      senior: "Life pattern crystallization"
    },
    culturalVariants: {
      ALL: "Universal patterns: birth/growth/death, order/chaos, unity/separation"
    },
    behaviorFormula: "inquiry + cases + questioning = universal insight",
    powerLevel: 10,
    prerequisites: ["pattern-recognition", "abstract-thinking"],
    outputs: ["universal-principles", "cross-domain-insights"]
  },

  // AGE-TRANSCENDENT TILES
  {
    id: "tile-intergenerational-wisdom",
    name: "Intergenerational Wisdom Flow",
    visual: "👵👧🤝",
    description: "Creates learning exchanges between generations",
    componentMethods: ["apprenticeship", "storytelling", "collaborative"],
    category: "age-transcendent",
    synergyScore: 0.95,
    ageAdaptation: {
      child: "Learn from elders, teach elders technology",
      teen: "Mentor younger, apprentice to elders",
      university: "Research with elder wisdom keepers",
      adult: "Both mentor and apprentice roles",
      senior: "Teach wisdom, learn new technologies"
    },
    culturalVariants: {
      JP: "Respect for elders (敬語)",
      GH: "Griot tradition",
      MX: "Abuela wisdom",
      IN: "Joint family learning"
    },
    behaviorFormula: "elder_wisdom + youth_energy + exchange = living tradition",
    powerLevel: 9,
    prerequisites: ["respect", "openness"],
    outputs: ["preserved-wisdom", "innovated-traditions"]
  },
  {
    id: "tile-lifespan-learning",
    name: "Lifespan Learning Companion",
    visual: "🌱🌳🍂🔄",
    description: "Adapts any concept to any life stage",
    componentMethods: ["montessori", "socratic", "peer-teaching"],
    category: "age-transcendent",
    synergyScore: 0.91,
    ageAdaptation: {
      child: "Discovery through play and senses",
      teen: "Discovery through challenge and identity",
      university: "Discovery through depth and application",
      adult: "Discovery through professional integration",
      senior: "Discovery through reflection and legacy"
    },
    culturalVariants: {
      JP: "一生懸命 (Issho kenmei) - lifelong dedication",
      GH: "Learning never ends",
      DE: "Lebenslanges Lernen"
    },
    behaviorFormula: "adaptation × stage × method = lifelong learner",
    powerLevel: 10,
    prerequisites: ["growth-mindset"],
    outputs: ["lifelong-learner", "adaptive-expertise"]
  },

  // DOMAIN SYNTHESIS TILES
  {
    id: "tile-art-science-fusion",
    name: "Art-Science Fusion Engine",
    visual: "🎨🔬⚡",
    description: "Combines artistic and scientific thinking for innovation",
    componentMethods: ["design-thinking", "inquiry-based", "project-based"],
    category: "domain-synthesis",
    synergyScore: 0.94,
    ageAdaptation: {
      child: "Science experiments as art projects",
      teen: "STEAM challenges with creative output",
      university: "Research with creative methodology",
      adult: "Innovation at art-science intersection",
      senior: "Wisdom synthesis from multiple domains"
    },
    culturalVariants: {
      BR: "Carnival engineering meets art",
      JP: "Engineering aesthetics (monozukuri)",
      IT: "Renaissance polymath tradition"
    },
    behaviorFormula: "art × science × practice = innovation",
    powerLevel: 9,
    prerequisites: ["creative-confidence", "scientific-literacy"],
    outputs: ["innovations", "artifacts", "new-methods"]
  },
  {
    id: "tile-ethics-action-engine",
    name: "Ethics-in-Action Engine",
    visual: "⚖️💚🚀",
    description: "Integrates ethical reasoning with practical action",
    componentMethods: ["socratic", "case-study", "project-based"],
    category: "transformation",
    synergyScore: 0.96,
    ageAdaptation: {
      child: "Simple right/wrong with action",
      teen: "Ethical dilemmas with real projects",
      university: "Applied ethics in professional contexts",
      adult: "Ethical leadership in organizations",
      senior: "Ethical legacy and teaching"
    },
    culturalVariants: {
      JP: "和 (Wa) - Harmony as ethical foundation",
      GH: "Ubuntu ethics - community-centered",
      DE: "Pflichtethik - duty-based ethics"
    },
    behaviorFormula: "ethics + case + action = ethical practitioner",
    powerLevel: 10,
    prerequisites: ["moral-reasoning", "action-orientation"],
    outputs: ["ethical-decisions", "responsible-innovations"]
  },

  // TRANSFORMATION TILES
  {
    id: "tile-paradigm-shifter",
    name: "Paradigm Shift Catalyst",
    visual: "🔄💥🌱",
    description: "Designed to fundamentally change how learners see the world",
    componentMethods: ["debate", "socratic", "simulation"],
    category: "transformation",
    synergyScore: 0.88,
    ageAdaptation: {
      child: "Wonder and discovery moments",
      teen: "Challenge assumptions through debate",
      university: "Paradigm analysis and reconstruction",
      adult: "Professional transformation",
      senior: "Wisdom perspective shifts"
    },
    culturalVariants: {
      US: "Disruptive thinking",
      JP: "禅 (Zen) enlightenment moments",
      IN: "Viveka - discriminative wisdom"
    },
    behaviorFormula: "challenge × question × experience = paradigm shift",
    powerLevel: 10,
    prerequisites: ["cognitive-flexibility", "openness"],
    outputs: ["transformed-perspective", "new-worldview"]
  },
  {
    id: "tile-mastery-pathway",
    name: "Mastery Acceleration Pathway",
    visual: "🎯⚡🏆",
    description: "Combines deliberate practice with mentorship and reflection",
    componentMethods: ["apprenticeship", "gamification", "flipped-classroom"],
    category: "transformation",
    synergyScore: 0.93,
    ageAdaptation: {
      child: "Skill building with rewards and mentors",
      teen: "Level-up system with mentor guidance",
      university: "Expertise development with coaching",
      adult: "Professional mastery acceleration",
      senior: "Mastery crystallization and teaching"
    },
    culturalVariants: {
      JP: "Shuhari - obey, digest, transcend",
      KR: "Sunbi spirit - scholarly dedication",
      DE: "Meister - mastery through apprenticeship"
    },
    behaviorFormula: "mentor + practice + reflection = accelerated mastery",
    powerLevel: 9,
    prerequisites: ["growth-mindset", "dedication"],
    outputs: ["expertise", "mastery-artifacts", "teaching-ability"]
  }
];

// ============================================================================
// METHOD COMBINATION ENGINE
// ============================================================================

interface MethodCombination {
  methods: BaseMethod[];
  combinationName: string;
  synergyScore: number;
  description: string;
  strengths: string[];
  weaknesses: string[];
  bestUseCase: string;
  ageRecommendation: string[];
  culturalRecommendation: string[];
  generatedTile?: CombinationTile;
}

export function calculateSynergy(method1: MethodIngredient, method2: MethodIngredient): number {
  let score = 0.5; // base

  // Synergy bonus
  if (method1.synergies.includes(method2.id)) score += 0.3;
  if (method2.synergies.includes(method1.id)) score += 0.2;

  // Conflict penalty
  if (method1.conflicts.includes(method2.id)) score -= 0.3;
  if (method2.conflicts.includes(method1.id)) score -= 0.3;

  // Strength complementarity
  if (method1.strength !== method2.strength) score += 0.15;

  // Energy level balance
  const energyLevels = ["calm", "moderate", "high", "intense"];
  const energyDiff = Math.abs(energyLevels.indexOf(method1.energyLevel) - energyLevels.indexOf(method2.energyLevel));
  if (energyDiff === 1) score += 0.1; // Adjacent energy levels work well
  if (energyDiff >= 3) score -= 0.1; // Extreme differences can be jarring

  return Math.max(0, Math.min(1, score));
}

export function generateCombinationName(method1: MethodIngredient, method2: MethodIngredient): string {
  const prefixes: Record<string, string> = {
    socratic: "Inquiry-Driven",
    "project-based": "Experiential",
    "inquiry-based": "Discovery-Based",
    collaborative: "Collective",
    storytelling: "Narrative-Enhanced",
    debate: "Dialectical",
    gamification: "Game-Infused",
    simulation: "Immersive",
    "design-thinking": "Human-Centered",
    apprenticeship: "Mentored",
    montessori: "Self-Directed",
    "peer-teaching": "Reciprocal",
    "case-study": "Case-Anchored",
    "problem-based": "Challenge-Centered",
    "flipped-classroom": "Flipped"
  };

  const primary = method1.synergies.includes(method2.id) ? method1 : method2;
  const secondary = primary === method1 ? method2 : method1;

  return `${prefixes[primary.id]} ${secondary.name}`;
}

export function discoverCombinations(): MethodCombination[] {
  const combinations: MethodCombination[] = [];

  for (let i = 0; i < METHOD_INGREDIENTS.length; i++) {
    for (let j = i + 1; j < METHOD_INGREDIENTS.length; j++) {
      const method1 = METHOD_INGREDIENTS[i];
      const method2 = METHOD_INGREDIENTS[j];

      const synergy = calculateSynergy(method1, method2);

      if (synergy >= 0.7) { // Only include promising combinations
        const combination: MethodCombination = {
          methods: [method1.id, method2.id],
          combinationName: generateCombinationName(method1, method2),
          synergyScore: synergy,
          description: `Combines ${method1.name} with ${method2.name} for enhanced learning outcomes`,
          strengths: [
            `${method1.strength} discovery`,
            `${method2.strength} development`,
            `Balanced ${method1.energyLevel}/${method2.energyLevel} energy`
          ],
          weaknesses: synergy < 0.8 ? ["May require careful sequencing"] : [],
          bestUseCase: determineBestUseCase(method1, method2),
          ageRecommendation: findCommonAgeGroups(method1.bestAgeGroup, method2.bestAgeGroup),
          culturalRecommendation: findBestCultures(method1.culturalAffinity, method2.culturalAffinity),
          generatedTile: findMatchingTile([method1.id, method2.id])
        };
        combinations.push(combination);
      }
    }
  }

  return combinations.sort((a, b) => b.synergyScore - a.synergyScore);
}

function determineBestUseCase(method1: MethodIngredient, method2: MethodIngredient): string {
  const strengthPairs = [
    { pair: ["discovery", "creation"], use: "Research projects with tangible outputs" },
    { pair: ["analysis", "social"], use: "Team-based problem analysis and solution design" },
    { pair: ["expression", "creation"], use: "Creative projects with narrative depth" },
    { pair: ["social", "discovery"], use: "Collaborative exploration and peer learning" },
    { pair: ["analysis", "creation"], use: "Design thinking with rigorous evaluation" },
    { pair: ["discovery", "expression"], use: "Inquiry-based creative expression" }
  ];

  for (const { pair, use } of strengthPairs) {
    if ((method1.strength === pair[0] && method2.strength === pair[1]) ||
        (method1.strength === pair[1] && method2.strength === pair[0])) {
      return use;
    }
  }

  return `Deep learning through ${method1.strength} and ${method2.strength} integration`;
}

function findCommonAgeGroups(ages1: string[], ages2: string[]): string[] {
  return ages1.filter(age => ages2.includes(age));
}

function findBestCultures(cultures1: Record<string, number>, cultures2: Record<string, number>): string[] {
  const combined: Record<string, number> = {};
  const allCultures = new Set([...Object.keys(cultures1), ...Object.keys(cultures2)]);

  for (const culture of allCultures) {
    const score1 = cultures1[culture] || 0;
    const score2 = cultures2[culture] || 0;
    combined[culture] = (score1 + score2) / 2;
  }

  return Object.entries(combined)
    .filter(([_, score]) => score >= 0.8)
    .sort((a, b) => b[1] - a[1])
    .map(([culture]) => culture);
}

function findMatchingTile(methods: BaseMethod[]): CombinationTile | undefined {
  return COMBINATION_TILES.find(tile => 
    methods.every(m => tile.componentMethods.includes(m))
  );
}

// ============================================================================
// SYNTHESIS ENGINE COMPONENT
// ============================================================================

interface SynthesisEngineProps {
  onCombinationSelect: (combination: MethodCombination) => void;
}

export function SynthesisEngine({ onCombinationSelect }: SynthesisEngineProps) {
  const combinations = discoverCombinations();

  return (
    <div className="space-y-6">
      {/* Engine Header */}
      <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-2xl p-6 border border-purple-500/30">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
            <GitMerge className="w-6 h-6 text-purple-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Method Synthesis Engine</h3>
            <p className="text-sm text-purple-300">Discover new teaching tools by mixing methods</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">{METHOD_INGREDIENTS.length}</div>
            <div className="text-xs text-slate-500">Base Methods</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-pink-400">{combinations.length}</div>
            <div className="text-xs text-slate-500">Valid Combinations</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">{COMBINATION_TILES.length}</div>
            <div className="text-xs text-slate-500">Combination Tiles</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">
              {combinations.filter(c => c.synergyScore >= 0.9).length}
            </div>
            <div className="text-xs text-slate-500">High Synergy</div>
          </div>
        </div>
      </div>

      {/* Method Ingredients Palette */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
        <h4 className="text-white font-medium mb-4 flex items-center gap-2">
          <Layers className="w-4 h-4 text-amber-400" />
          Method Ingredients
        </h4>
        <div className="flex flex-wrap gap-2">
          {METHOD_INGREDIENTS.map((method) => (
            <motion.div
              key={method.id}
              className="px-3 py-2 rounded-lg bg-slate-900/50 border border-slate-600 hover:border-purple-500/50 cursor-pointer transition-colors"
              whileHover={{ scale: 1.05 }}
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">{method.icon}</span>
                <span className="text-sm text-slate-300">{method.name}</span>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-slate-500 capitalize">{method.strength}</span>
                <span className="text-xs text-slate-600">•</span>
                <span className="text-xs text-slate-500 capitalize">{method.energyLevel}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Top Combinations */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
        <h4 className="text-white font-medium mb-4 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-yellow-400" />
          Top Synergy Combinations
        </h4>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {combinations.slice(0, 10).map((combo, idx) => (
            <motion.div
              key={combo.combinationName}
              className="p-4 bg-slate-900/50 rounded-xl border border-slate-600 hover:border-purple-500/50 cursor-pointer transition-colors"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              onClick={() => onCombinationSelect(combo)}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="text-lg font-medium text-white">{combo.combinationName}</div>
                  {combo.generatedTile && (
                    <span className="px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-xs">
                      Tile: {combo.generatedTile.name}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-purple-500 to-pink-500" 
                      style={{ width: `${combo.synergyScore * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-purple-400">{(combo.synergyScore * 100).toFixed(0)}%</span>
                </div>
              </div>
              <p className="text-sm text-slate-400">{combo.description}</p>
              <div className="flex flex-wrap gap-2 mt-2">
                {combo.ageRecommendation.map(age => (
                  <span key={age} className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-300">
                    {age}
                  </span>
                ))}
                {combo.culturalRecommendation.slice(0, 3).map(culture => (
                  <span key={culture} className="text-xs px-2 py-0.5 rounded bg-green-500/20 text-green-300">
                    {culture}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Combination Tiles Grid */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
        <h4 className="text-white font-medium mb-4 flex items-center gap-2">
          <Diamond className="w-4 h-4 text-cyan-400" />
          Combination Tiles (Higher-Order Abstractions)
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {COMBINATION_TILES.map((tile) => (
            <motion.div
              key={tile.id}
              className="p-4 bg-gradient-to-br from-slate-900/80 to-slate-800/50 rounded-xl border border-slate-600 hover:border-cyan-500/50 cursor-pointer transition-all"
              whileHover={{ scale: 1.02, y: -2 }}
            >
              <div className="text-3xl mb-2">{tile.visual}</div>
              <div className="text-white font-medium text-sm">{tile.name}</div>
              <div className="text-xs text-slate-500 mt-1 capitalize">{tile.category}</div>
              <div className="flex items-center gap-1 mt-2">
                <span className="text-xs text-cyan-400">Power Level:</span>
                <div className="flex gap-0.5">
                  {Array.from({ length: 10 }).map((_, i) => (
                    <div
                      key={i}
                      className={`w-2 h-2 rounded-full ${i < tile.powerLevel ? "bg-cyan-400" : "bg-slate-700"}`}
                    />
                  ))}
                </div>
              </div>
              <div className="mt-2 flex flex-wrap gap-1">
                {tile.componentMethods.map(method => (
                  <span key={method} className="text-xs px-1.5 py-0.5 rounded bg-slate-700 text-slate-400">
                    {method}
                  </span>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// CREATIVE SYNTHESIS ROUNDS COMPONENT
// ============================================================================

interface CreativeSynthesisRoundProps {
  roundNumber: number;
  roundType: "method-hybrid" | "age-adaptive" | "domain-synthesis" | "master-synthesis";
  onComplete: (results: SynthesisRoundResult) => void;
}

interface SynthesisRoundResult {
  round: number;
  type: string;
  discoveries: string[];
  tilesCreated: CombinationTile[];
  insights: string[];
  culturalAdaptations: Record<string, string>;
  mlFeatures: Record<string, number>;
}

export function CreativeSynthesisRound({ roundNumber, roundType, onComplete }: CreativeSynthesisRoundProps) {
  const roundConfigs = {
    "method-hybrid": {
      title: "Method Hybrid Discovery",
      description: "Discover new teaching tools by combining methods",
      icon: "🔀",
      color: "from-purple-500/20 to-pink-500/20"
    },
    "age-adaptive": {
      title: "Age-Adaptive Synthesis",
      description: "Create learning tools that work across generations",
      icon: "👶👵",
      color: "from-blue-500/20 to-green-500/20"
    },
    "domain-synthesis": {
      title: "Domain Synthesis",
      description: "Combine domain expertise with learning methods",
      icon: "🎨🔬",
      color: "from-amber-500/20 to-red-500/20"
    },
    "master-synthesis": {
      title: "Master Synthesis",
      description: "Create universal meta-learning patterns",
      icon: "🌟",
      color: "from-cyan-500/20 to-purple-500/20"
    }
  };

  const config = roundConfigs[roundType];

  return (
    <div className={`bg-gradient-to-br ${config.color} rounded-2xl p-6 border border-slate-700`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="text-3xl">{config.icon}</div>
          <div>
            <h3 className="text-lg font-semibold text-white">Round {roundNumber}: {config.title}</h3>
            <p className="text-sm text-slate-400">{config.description}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-sm text-slate-500">Synthesis Round</div>
          <div className="text-2xl font-bold text-white">{roundNumber}/12</div>
        </div>
      </div>

      {/* Synthesis Visualization */}
      <div className="bg-slate-900/50 rounded-xl p-4 mb-4">
        <div className="flex items-center justify-center gap-8">
          <MethodNode name="Socratic" icon="🧙" />
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            <Zap className="w-8 h-8 text-yellow-400" />
          </motion.div>
          <MethodNode name="Storytelling" icon="📖" />
          <ArrowRight className="w-6 h-6 text-green-400" />
          <div className="p-4 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-xl border border-purple-500/50">
            <div className="text-2xl">💎</div>
            <div className="text-sm text-white mt-1">Wisdom Tile</div>
          </div>
        </div>
      </div>

      {/* Action Button */}
      <motion.button
        className="w-full py-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium flex items-center justify-center gap-2"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => {
          onComplete({
            round: roundNumber,
            type: roundType,
            discoveries: [
              "Story-Socratic fusion creates reflection loops",
              "Age-adaptive questioning patterns discovered",
              "Cultural wisdom compression achieved"
            ],
            tilesCreated: COMBINATION_TILES.slice(0, 2),
            insights: [
              "Questions embedded in stories create memorable learning",
              "Cultural context amplifies question impact"
            ],
            culturalAdaptations: {
              JP: "Zen koan tradition merges naturally with Socratic questioning",
              GH: "Griot stories become vessels for Socratic inquiry"
            },
            mlFeatures: {
              synthesis_quality: 0.92,
              cultural_adaptation: 0.89,
              age_flexibility: 0.95,
              creativity_index: 0.94
            }
          });
        }}
      >
        <RefreshCw className="w-4 h-4" />
        Execute Creative Synthesis
      </motion.button>
    </div>
  );
}

function MethodNode({ name, icon }: { name: string; icon: string }) {
  return (
    <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-600 text-center">
      <div className="text-2xl mb-1">{icon}</div>
      <div className="text-sm text-white">{name}</div>
    </div>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  METHOD_INGREDIENTS,
  COMBINATION_TILES,
  SynthesisEngine,
  CreativeSynthesisRound,
  discoverCombinations,
  calculateSynergy,
  generateCombinationName
};
