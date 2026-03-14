// ============================================================================
// LLN PLAYGROUND - EXTENDED SYNTHESIS ROUNDS (12 MORE ROUNDS)
// Rounds 13-24: Advanced Method Combinations & Meta-Patterns
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
  Crystal,
  Hexagon,
  Crown,
  Diamond,
  Award,
  Medal,
  Rocket,
  Shield,
  Swords,
  Fingerprint,
  Scan,
  Radar,
  Eye,
  Focus,
  Crosshair,
  Sunrise,
  Sunset,
  Rainbow,
  Cloud,
  Droplet,
  Wind,
  Thermometer,
  Gauge,
  Activity,
  TrendingUp,
  BarChart3,
  PieChart,
  LineChart,
  Database,
  Server,
  Cpu,
  HardDrive,
  Wifi,
  Signal,
  Radio,
  Satellite,
  MapPin,
  Navigation,
  Anchor,
  Ship,
  Plane,
  Helicopter,
  Car,
  Train,
  Bike,
  Walk,
  Footprints,
  Home,
  Building,
  Building2,
  Factory,
  Warehouse,
  Store,
  ShoppingCart,
  CreditCard,
  Wallet,
  PiggyBank,
  Landmark,
  Banknote,
  Coins,
  DollarSign,
  Euro,
  PoundSterling,
  Yen,
  IndianRupee,
  Bitcoin,
} from "lucide-react";

// ============================================================================
// EXTENDED SYNTHESIS ROUND DEFINITIONS
// ============================================================================

export interface ExtendedSynthesisRound {
  id: string;
  roundNumber: number;
  name: string;
  description: string;
  type: "method-hybrid" | "meta-pattern" | "wisdom-engine" | "cultural-synthesis" | "age-bridge" | "domain-fusion" | "transformation" | "mastery-path" | "innovation-lab" | "research-deep" | "creative-forge" | "wisdom-crystallization";
  icon: string;
  color: string;
  inputMethods: string[];
  outputTile: string;
  synergyScore: number;
  mlTrainingExamples: number;
  duration: number; // minutes
  difficulty: "intermediate" | "advanced" | "expert";
  prerequisites: string[];
  outcomes: string[];
  culturalVariants: Record<string, string>;
  ageAdaptations: Record<string, string>;
  formula: string;
  powerLevel: number;
  relatedRounds: string[];
  discoveryDate: string;
}

export const EXTENDED_SYNTHESIS_ROUNDS: ExtendedSynthesisRound[] = [
  // ROUND 13: Meta-Cognition Catalyst
  {
    id: "round-13-meta-cognition",
    roundNumber: 13,
    name: "Meta-Cognition Catalyst",
    description: "Combines Socratic questioning with peer-teaching to create learners who understand HOW they learn, not just WHAT they learn.",
    type: "meta-pattern",
    icon: "🧠🔄💡",
    color: "from-purple-500 to-pink-500",
    inputMethods: ["socratic", "peer-teaching", "flipped-classroom"],
    outputTile: "Meta-Learning Engine",
    synergyScore: 0.95,
    mlTrainingExamples: 12500,
    duration: 45,
    difficulty: "advanced",
    prerequisites: ["basic-socratic", "peer-interaction"],
    outcomes: [
      "Learners develop metacognitive awareness",
      "Self-regulation skills improve 3x",
      "Learning transfer increases 2.5x",
      "Retention improves by 45%"
    ],
    culturalVariants: {
      JP: "守破離 (Shuhari) - Learn, Detach, Transcend through teaching",
      US: "Think-aloud protocols combined with peer explanation",
      GH: "Wisdom circles where elders learn from youth explanations",
      IN: "Guru-shishya with role reversal for metacognition"
    },
    ageAdaptations: {
      child: "Think-pair-share: 'What helped you learn this?'",
      teen: "Learning style discovery through peer teaching experiments",
      university: "Metacognitive strategy development with research",
      adult: "Professional learning optimization through reflection",
      senior: "Wisdom crystallization through teaching younger generations"
    },
    formula: "question × explain × reflect = metacognition",
    powerLevel: 9,
    relatedRounds: ["round-1-wisdom-synthesis", "round-10-meta-learning"],
    discoveryDate: "2024-03-15"
  },

  // ROUND 14: Emotional Intelligence Forge
  {
    id: "round-14-emotional-intelligence",
    roundNumber: 14,
    name: "Emotional Intelligence Forge",
    description: "Synthesizes storytelling, collaborative learning, and drama simulation to build emotional understanding across cultures.",
    type: "wisdom-engine",
    icon: "❤️🎭🌍",
    color: "from-rose-500 to-orange-500",
    inputMethods: ["storytelling", "collaborative", "simulation"],
    outputTile: "EQ Development Engine",
    synergyScore: 0.92,
    mlTrainingExamples: 15200,
    duration: 60,
    difficulty: "advanced",
    prerequisites: ["storytelling-basics", "collaborative-experience"],
    outcomes: [
      "Emotional vocabulary expands 4x",
      "Cross-cultural empathy improves",
      "Conflict resolution skills develop",
      "Social awareness increases"
    ],
    culturalVariants: {
      JP: "Mono no aware (物の哀れ) - Pathos of things through shared stories",
      US: "Empathy mapping with collaborative scenarios",
      GH: "Ubuntu storytelling circles for collective EQ",
      BR: "Carnival emotion exploration through drama"
    },
    ageAdaptations: {
      child: "Feeling puppets and emotion stories",
      teen: "Role-playing complex social scenarios",
      university: "Emotional intelligence research projects",
      adult: "Workplace EQ development simulations",
      senior: "Life wisdom sharing for emotional legacy"
    },
    formula: "story + collaborate + experience = emotional wisdom",
    powerLevel: 10,
    relatedRounds: ["round-4-intergenerational", "round-8-healing-learning"],
    discoveryDate: "2024-03-18"
  },

  // ROUND 15: Constraint Innovation Lab
  {
    id: "round-15-constraint-innovation",
    roundNumber: 15,
    name: "Constraint Innovation Lab",
    description: "Deep exploration of how constraints drive creativity. Combines gamification, problem-based learning, and design thinking.",
    type: "innovation-lab",
    icon: "🔐🎨🚀",
    color: "from-amber-500 to-red-500",
    inputMethods: ["gamification", "problem-based", "design-thinking"],
    outputTile: "Innovation Constraint Engine",
    synergyScore: 0.94,
    mlTrainingExamples: 18700,
    duration: 75,
    difficulty: "expert",
    prerequisites: ["constraint-basics", "design-thinking-intro"],
    outcomes: [
      "Creative output quality improves 2x under constraints",
      "Problem-solving speed increases",
      "Innovation metrics improve",
      "Stress-response creativity develops"
    ],
    culturalVariants: {
      JP: "Haiku discipline - 17 syllables containing infinity",
      US: "Shark Tank pitch constraints driving innovation",
      GH: "Proverb constraints compressing wisdom",
      DE: "Engineering constraints creating Bauhaus beauty"
    },
    ageAdaptations: {
      child: "One-color drawing challenges",
      teen: "280-character explanation challenges",
      university: "Thesis constraints driving depth",
      adult: "Budget and time constraints as innovation fuel",
      senior: "Life constraints crystallized into wisdom"
    },
    formula: "constraint × problem × design = innovation",
    powerLevel: 9,
    relatedRounds: ["round-2-design-tournament", "round-7-art-science"],
    discoveryDate: "2024-03-21"
  },

  // ROUND 16: Cultural Bridge Builder
  {
    id: "round-16-cultural-bridge",
    roundNumber: 16,
    name: "Cultural Bridge Builder",
    description: "Creates deep cross-cultural understanding through collaborative inquiry, storytelling, and debate across cultural contexts.",
    type: "cultural-synthesis",
    icon: "🌉🌍🤝",
    color: "from-emerald-500 to-teal-500",
    inputMethods: ["collaborative", "storytelling", "debate"],
    outputTile: "Cultural Intelligence Bridge",
    synergyScore: 0.91,
    mlTrainingExamples: 22000,
    duration: 90,
    difficulty: "expert",
    prerequisites: ["cultural-basics", "debate-experience"],
    outcomes: [
      "Cultural intelligence (CQ) improves 3x",
      "Cross-cultural communication effectiveness doubles",
      "Global team collaboration improves",
      "Cultural conflict resolution develops"
    ],
    culturalVariants: {
      JP: "Wa (和) - Harmony through understanding differences",
      US: "Diversity dialogue and cultural perspective-taking",
      GH: "Ubuntu bridges - I am because we are across cultures",
      IN: "Vasudhaiva Kutumbakam - World as one family exploration"
    },
    ageAdaptations: {
      child: "Stories from around the world with shared themes",
      teen: "Virtual cultural exchange projects",
      university: "Cross-cultural research collaborations",
      adult: "Global team leadership development",
      senior: "Heritage preservation and sharing across cultures"
    },
    formula: "collaborate + story + debate = cultural bridge",
    powerLevel: 10,
    relatedRounds: ["round-3-research-collective", "round-14-emotional-intelligence"],
    discoveryDate: "2024-03-24"
  },

  // ROUND 17: Mastery Acceleration Pathway
  {
    id: "round-17-mastery-pathway",
    roundNumber: 17,
    name: "Mastery Acceleration Pathway",
    description: "Combines apprenticeship, gamification, and flipped-classroom to create accelerated paths to expertise in any domain.",
    type: "mastery-path",
    icon: "🎯⚡🏆",
    color: "from-cyan-500 to-blue-500",
    inputMethods: ["apprenticeship", "gamification", "flipped-classroom"],
    outputTile: "Mastery Acceleration Engine",
    synergyScore: 0.96,
    mlTrainingExamples: 25000,
    duration: 120,
    difficulty: "expert",
    prerequisites: ["apprenticeship-basics", "gamification-design"],
    outcomes: [
      "Time to mastery reduces by 40%",
      "Skill retention improves 3x",
      "Expertise development accelerates",
      "Teaching ability develops alongside learning"
    ],
    culturalVariants: {
      JP: "Shuhari (守破離) - Obey, Digest, Transcend with game elements",
      DE: "Meister system with gamified progression",
      IN: "Gurukul meets modern gamification",
      US: "Gamified mentorship programs"
    },
    ageAdaptations: {
      child: "Level-up skill games with mentor support",
      teen: "Gamified practice with expert coaching",
      university: "Accelerated expertise development programs",
      adult: "Professional mastery acceleration systems",
      senior: "Wisdom mastery crystallization and teaching"
    },
    formula: "mentor + game + flip = accelerated mastery",
    powerLevel: 10,
    relatedRounds: ["round-11-paradigm-shift", "round-13-meta-cognition"],
    discoveryDate: "2024-03-27"
  },

  // ROUND 18: Research Synthesis Engine
  {
    id: "round-18-research-synthesis",
    roundNumber: 18,
    name: "Research Synthesis Engine",
    description: "Combines inquiry-based learning, case study, and socratic method to create research-savvy learners who can synthesize across domains.",
    type: "research-deep",
    icon: "🔬📚🔍",
    color: "from-violet-500 to-purple-500",
    inputMethods: ["inquiry-based", "case-study", "socratic"],
    outputTile: "Research Synthesis Tile",
    synergyScore: 0.93,
    mlTrainingExamples: 19800,
    duration: 100,
    difficulty: "expert",
    prerequisites: ["research-basics", "critical-thinking"],
    outcomes: [
      "Research methodology mastery",
      "Cross-domain synthesis capability",
      "Critical analysis skills",
      "Knowledge contribution readiness"
    ],
    culturalVariants: {
      JP: "Kenkyū (研究) - Deep investigation with case analysis",
      DE: "Bildung through research - self-cultivation through inquiry",
      UK: "Oxford tutorial meets case study method",
      US: "Research apprenticeship with Socratic guidance"
    },
    ageAdaptations: {
      child: "Discovery experiments with question journals",
      teen: "Research projects with mentor guidance",
      university: "Full research methodology training",
      adult: "Professional research skill development",
      senior: "Life research crystallization"
    },
    formula: "inquire + case + question = research synthesis",
    powerLevel: 9,
    relatedRounds: ["round-3-research-collective", "round-13-meta-cognition"],
    discoveryDate: "2024-03-30"
  },

  // ROUND 19: Creative Confidence Builder
  {
    id: "round-19-creative-confidence",
    roundNumber: 19,
    name: "Creative Confidence Builder",
    description: "Combines design-thinking, montessori, and project-based learning to build unshakeable creative confidence in learners.",
    type: "transformation",
    icon: "✨🎨💪",
    color: "from-pink-500 to-rose-500",
    inputMethods: ["design-thinking", "montessori", "project-based"],
    outputTile: "Creative Confidence Engine",
    synergyScore: 0.89,
    mlTrainingExamples: 14500,
    duration: 80,
    difficulty: "intermediate",
    prerequisites: ["creative-basics", "self-direction"],
    outcomes: [
      "Creative confidence increases 4x",
      "Fear of failure decreases significantly",
      "Innovation attempts increase",
      "Creative identity solidifies"
    ],
    culturalVariants: {
      JP: "Wabi-sabi acceptance - beauty in imperfection builds confidence",
      US: "Design thinking with Montessori freedom",
      BR: "Carnival creativity without judgment",
      IT: "Renaissance workshop meets modern design"
    },
    ageAdaptations: {
      child: "Open-ended creation stations with celebration",
      teen: "Design challenges with process over product focus",
      university: "Creative thesis projects with support",
      adult: "Professional creativity workshops",
      senior: "Life creativity celebration and sharing"
    },
    formula: "design + freedom + create = creative confidence",
    powerLevel: 8,
    relatedRounds: ["round-7-art-science", "round-15-constraint-innovation"],
    discoveryDate: "2024-04-02"
  },

  // ROUND 20: Systems Thinking Catalyst
  {
    id: "round-20-systems-thinking",
    roundNumber: 20,
    name: "Systems Thinking Catalyst",
    description: "Combines problem-based learning, simulation, and case study to develop systems thinking capabilities across domains.",
    type: "meta-pattern",
    icon: "🔄🌐🎯",
    color: "from-teal-500 to-emerald-500",
    inputMethods: ["problem-based", "simulation", "case-study"],
    outputTile: "Systems Thinking Tile",
    synergyScore: 0.94,
    mlTrainingExamples: 21000,
    duration: 90,
    difficulty: "advanced",
    prerequisites: ["systems-intro", "simulation-experience"],
    outcomes: [
      "Systems thinking capability develops",
      "Problem complexity handling improves",
      "Feedback loop recognition emerges",
      "Strategic thinking expands"
    ],
    culturalVariants: {
      JP: "Zen garden - understanding interconnection through microcosms",
      US: "Business simulation meets systems dynamics",
      GH: "Ecosystem understanding through community problems",
      DE: "Systems engineering meets case analysis"
    },
    ageAdaptations: {
      child: "Ecosystem games and connected puzzles",
      teen: "Complex system simulations with mentorship",
      university: "Systems dynamics research and modeling",
      adult: "Organizational systems thinking development",
      senior: "Life systems wisdom crystallization"
    },
    formula: "problem × simulate × analyze = systems thinking",
    powerLevel: 9,
    relatedRounds: ["round-18-research-synthesis", "round-3-research-collective"],
    discoveryDate: "2024-04-05"
  },

  // ROUND 21: Wisdom Crystallization Engine
  {
    id: "round-21-wisdom-crystallization",
    roundNumber: 21,
    name: "Wisdom Crystallization Engine",
    description: "Combines apprenticeship, storytelling, and case study to crystallize lifetime wisdom into transferable knowledge seeds.",
    type: "wisdom-crystallization",
    icon: "💎📚🌱",
    color: "from-amber-500 to-yellow-500",
    inputMethods: ["apprenticeship", "storytelling", "case-study"],
    outputTile: "Wisdom Crystallization Tile",
    synergyScore: 0.97,
    mlTrainingExamples: 30000,
    duration: 180,
    difficulty: "expert",
    prerequisites: ["wisdom-experience", "teaching-experience"],
    outcomes: [
      "Wisdom crystallization capability",
      "Knowledge seed generation",
      "Legacy documentation skills",
      "Intergenerational transfer mastery"
    ],
    culturalVariants: {
      JP: "Iemoto system - wisdom transmission through art forms",
      GH: "Griot tradition with case crystallization",
      IN: "Guru-shishya parampara with story preservation",
      IL: "Talmudic case method meets modern storytelling"
    },
    ageAdaptations: {
      child: "Learn from elders, teach through stories",
      teen: "Mentor younger, crystallize learning",
      university: "Research crystallization and legacy building",
      adult: "Professional wisdom documentation",
      senior: "Life wisdom crystallization and transmission"
    },
    formula: "mentor + story + case = crystallized wisdom",
    powerLevel: 10,
    relatedRounds: ["round-4-intergenerational", "round-17-mastery-pathway"],
    discoveryDate: "2024-04-08"
  },

  // ROUND 22: Adaptive Learning Engine
  {
    id: "round-22-adaptive-learning",
    roundNumber: 22,
    name: "Adaptive Learning Engine",
    description: "Combines simulation, montessori, and peer-teaching to create adaptive learning systems that respond to learner needs.",
    type: "mastery-path",
    icon: "🔄🎯🤖",
    color: "from-indigo-500 to-violet-500",
    inputMethods: ["simulation", "montessori", "peer-teaching"],
    outputTile: "Adaptive Learning Tile",
    synergyScore: 0.91,
    mlTrainingExamples: 23000,
    duration: 100,
    difficulty: "advanced",
    prerequisites: ["adaptive-basics", "simulation-design"],
    outcomes: [
      "Adaptive system design capability",
      "Learner response recognition",
      "Personalization methodology",
      "Continuous improvement mindset"
    ],
    culturalVariants: {
      JP: "Kaizen learning - continuous small improvements",
      US: "AI-powered adaptive learning with human teaching",
      FI: "Finnish education meets adaptive systems",
      SG: "Singapore math meets personalization"
    },
    ageAdaptations: {
      child: "Adaptive games that learn from play",
      teen: "Personalized challenge systems",
      university: "Adaptive learning research",
      adult: "Professional adaptive skill development",
      senior: "Wisdom-adaptive sharing systems"
    },
    formula: "simulate + adapt + teach = adaptive learning",
    powerLevel: 9,
    relatedRounds: ["round-17-mastery-pathway", "round-20-systems-thinking"],
    discoveryDate: "2024-04-11"
  },

  // ROUND 23: Innovation Ecosystem Builder
  {
    id: "round-23-innovation-ecosystem",
    roundNumber: 23,
    name: "Innovation Ecosystem Builder",
    description: "Combines design-thinking, collaborative, and project-based learning to build entire innovation ecosystems within organizations.",
    type: "domain-fusion",
    icon: "🌐💡🚀",
    color: "from-orange-500 to-red-500",
    inputMethods: ["design-thinking", "collaborative", "project-based"],
    outputTile: "Innovation Ecosystem Tile",
    synergyScore: 0.88,
    mlTrainingExamples: 17500,
    duration: 150,
    difficulty: "expert",
    prerequisites: ["innovation-basics", "collaboration-leadership"],
    outcomes: [
      "Innovation ecosystem design capability",
      "Team innovation facilitation",
      "Innovation culture development",
      "Sustainable innovation systems"
    ],
    culturalVariants: {
      JP: "Monozukuri ecosystem - craftsmanship culture",
      US: "Silicon Valley innovation system design",
      IL: "Startup nation methodology",
      DE: "Mittelstand innovation ecosystem"
    },
    ageAdaptations: {
      child: "Classroom invention studios",
      teen: "School innovation labs",
      university: "Campus innovation ecosystems",
      adult: "Organizational innovation design",
      senior: "Wisdom ecosystem curation"
    },
    formula: "design + collaborate + build = innovation ecosystem",
    powerLevel: 9,
    relatedRounds: ["round-15-constraint-innovation", "round-16-cultural-bridge"],
    discoveryDate: "2024-04-14"
  },

  // ROUND 24: Universal Wisdom Synthesis
  {
    id: "round-24-universal-wisdom",
    roundNumber: 24,
    name: "Universal Wisdom Synthesis",
    description: "The ultimate synthesis round combining all methods to create universal wisdom patterns that transcend culture, age, and domain.",
    type: "wisdom-crystallization",
    icon: "🌟🌍💎",
    color: "from-gradient-500 via-purple-500 to-amber-500",
    inputMethods: ["socratic", "storytelling", "collaborative", "apprenticeship", "design-thinking"],
    outputTile: "Universal Wisdom Tile",
    synergyScore: 0.99,
    mlTrainingExamples: 50000,
    duration: 240,
    difficulty: "expert",
    prerequisites: ["all-previous-rounds"],
    outcomes: [
      "Universal pattern recognition",
      "Cross-domain wisdom transfer",
      "Meta-teaching capability",
      "Wisdom architecture design"
    ],
    culturalVariants: {
      ALL: "Universal patterns that work across all cultures",
      JP: "Zen meets Shinto meets modern learning",
      US: "Democratized wisdom systems",
      GH: "Ubuntu universalized - humanity's collective wisdom",
      IN: "Sanatana Dharma - eternal wisdom patterns"
    },
    ageAdaptations: {
      child: "Universal wonder and discovery",
      teen: "Universal identity formation",
      university: "Universal research and contribution",
      adult: "Universal professional wisdom",
      senior: "Universal legacy crystallization"
    },
    formula: "question + story + collaborate + mentor + design = universal wisdom",
    powerLevel: 10,
    relatedRounds: ["round-21-wisdom-crystallization", "round-13-meta-cognition", "round-17-mastery-pathway"],
    discoveryDate: "2024-04-17"
  }
];

// ============================================================================
// SYNTHESIS ROUNDS VISUALIZATION COMPONENT
// ============================================================================

interface ExtendedSynthesisRoundsProps {
  onRoundSelect?: (round: ExtendedSynthesisRound) => void;
  completedRounds?: string[];
}

export function ExtendedSynthesisRounds({ onRoundSelect, completedRounds = [] }: ExtendedSynthesisRoundsProps) {
  const totalRounds = EXTENDED_SYNTHESIS_ROUNDS.length;
  const totalExamples = EXTENDED_SYNTHESIS_ROUNDS.reduce((sum, r) => sum + r.mlTrainingExamples, 0);
  const avgSynergy = EXTENDED_SYNTHESIS_ROUNDS.reduce((sum, r) => sum + r.synergyScore, 0) / totalRounds;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-amber-900/30 via-purple-900/20 to-cyan-900/30 rounded-2xl p-6 border border-amber-500/30">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500/30 to-purple-500/30 flex items-center justify-center">
              <Rocket className="w-8 h-8 text-amber-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Extended Synthesis Rounds</h2>
              <p className="text-amber-300">12 More Rounds of Creative Discovery</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-white">{totalRounds}</div>
            <div className="text-xs text-slate-500">Advanced Rounds</div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-4">
          <div className="p-4 bg-slate-900/50 rounded-xl text-center border border-slate-700">
            <div className="text-2xl font-bold text-amber-400">{totalRounds}</div>
            <div className="text-xs text-slate-500">Total Rounds</div>
          </div>
          <div className="p-4 bg-slate-900/50 rounded-xl text-center border border-slate-700">
            <div className="text-2xl font-bold text-purple-400">{(totalExamples / 1000).toFixed(0)}K</div>
            <div className="text-xs text-slate-500">ML Examples</div>
          </div>
          <div className="p-4 bg-slate-900/50 rounded-xl text-center border border-slate-700">
            <div className="text-2xl font-bold text-cyan-400">{(avgSynergy * 100).toFixed(0)}%</div>
            <div className="text-xs text-slate-500">Avg Synergy</div>
          </div>
          <div className="p-4 bg-slate-900/50 rounded-xl text-center border border-slate-700">
            <div className="text-2xl font-bold text-emerald-400">{completedRounds.length}</div>
            <div className="text-xs text-slate-500">Completed</div>
          </div>
        </div>
      </div>

      {/* Rounds Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {EXTENDED_SYNTHESIS_ROUNDS.map((round, idx) => (
          <motion.div
            key={round.id}
            className={`p-5 rounded-2xl border cursor-pointer transition-all ${
              completedRounds.includes(round.id)
                ? "bg-emerald-500/10 border-emerald-500/30"
                : "bg-slate-800/50 border-slate-700 hover:border-slate-600"
            }`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
            whileHover={{ scale: 1.02, y: -2 }}
            onClick={() => onRoundSelect?.(round)}
          >
            {/* Round Number Badge */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center bg-gradient-to-br ${round.color} bg-opacity-20`}>
                  <span className="text-white text-sm font-bold">{round.roundNumber}</span>
                </div>
                <span className="text-xs text-slate-500 capitalize">{round.type.replace("-", " ")}</span>
              </div>
              {completedRounds.includes(round.id) && (
                <CheckCircle className="w-5 h-5 text-emerald-400" />
              )}
            </div>

            {/* Icon and Title */}
            <div className="flex items-center gap-3 mb-3">
              <div className="text-3xl">{round.icon}</div>
              <div>
                <h4 className="text-white font-medium">{round.name}</h4>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    round.difficulty === "intermediate" ? "bg-yellow-500/20 text-yellow-400" :
                    round.difficulty === "advanced" ? "bg-orange-500/20 text-orange-400" :
                    "bg-red-500/20 text-red-400"
                  }`}>
                    {round.difficulty}
                  </span>
                  <span className="text-xs text-slate-500">{round.duration} min</span>
                </div>
              </div>
            </div>

            {/* Description */}
            <p className="text-sm text-slate-400 mb-3 line-clamp-2">{round.description}</p>

            {/* Synergy Bar */}
            <div className="mb-3">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-slate-500">Synergy</span>
                <span className="text-purple-400">{(round.synergyScore * 100).toFixed(0)}%</span>
              </div>
              <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className={`h-full bg-gradient-to-r ${round.color}`}
                  style={{ width: `${round.synergyScore * 100}%` }}
                />
              </div>
            </div>

            {/* ML Examples and Power Level */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1">
                <Database className="w-3 h-3 text-cyan-400" />
                <span className="text-xs text-cyan-400">{(round.mlTrainingExamples / 1000).toFixed(1)}K ML</span>
              </div>
              <div className="flex items-center gap-1">
                <Star className="w-3 h-3 text-amber-400" />
                <span className="text-xs text-amber-400">Level {round.powerLevel}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Round Dependencies Visualization */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Network className="w-5 h-5 text-purple-400" />
          Round Dependencies & Connections
        </h3>

        <div className="relative h-64 bg-slate-900/50 rounded-xl overflow-hidden">
          {/* Simple dependency visualization */}
          <svg className="absolute inset-0 w-full h-full">
            {EXTENDED_SYNTHESIS_ROUNDS.slice(0, 8).map((round, idx) => {
              const x = 50 + (idx % 4) * 25;
              const y = 30 + Math.floor(idx / 4) * 40;
              return (
                <g key={round.id}>
                  <motion.circle
                    cx={`${x}%`}
                    cy={`${y}%`}
                    r="12"
                    fill="rgba(168, 85, 247, 0.3)"
                    stroke="rgba(168, 85, 247, 0.5)"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: idx * 0.1 }}
                  />
                  <text
                    x={`${x}%`}
                    y={`${y}%`}
                    fill="white"
                    fontSize="10"
                    textAnchor="middle"
                    dominantBaseline="middle"
                  >
                    {round.roundNumber}
                  </text>
                </g>
              );
            })}
            {/* Connection lines */}
            {EXTENDED_SYNTHESIS_ROUNDS.slice(0, 6).map((round, idx) => {
              if (round.relatedRounds.length === 0) return null;
              const relatedIdx = EXTENDED_SYNTHESIS_ROUNDS.findIndex(r => r.id === round.relatedRounds[0]);
              if (relatedIdx === -1 || relatedIdx >= 8) return null;
              
              const x1 = 50 + (idx % 4) * 25;
              const y1 = 30 + Math.floor(idx / 4) * 40;
              const x2 = 50 + (relatedIdx % 4) * 25;
              const y2 = 30 + Math.floor(relatedIdx / 4) * 40;
              
              return (
                <motion.line
                  key={`line-${round.id}`}
                  x1={`${x1}%`}
                  y1={`${y1}%`}
                  x2={`${x2}%`}
                  y2={`${y2}%`}
                  stroke="rgba(168, 85, 247, 0.2)"
                  strokeWidth="1"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ delay: 0.5 + idx * 0.1, duration: 1 }}
                />
              );
            })}
          </svg>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="bg-gradient-to-r from-amber-500/10 via-purple-500/10 to-cyan-500/10 rounded-2xl p-6 border border-purple-500/30">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Trophy className="w-5 h-5 text-amber-400" />
          Complete System Statistics
        </h3>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-white">{totalRounds + 12}</div>
            <div className="text-sm text-slate-400">Total Synthesis Rounds</div>
            <div className="text-xs text-slate-500">(Original + Extended)</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400">{((127000 + totalExamples) / 1000).toFixed(0)}K</div>
            <div className="text-sm text-slate-400">Total ML Examples</div>
            <div className="text-xs text-slate-500">Training Data</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-cyan-400">15+</div>
            <div className="text-sm text-slate-400">Base Methods</div>
            <div className="text-xs text-slate-500">Combinable</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-emerald-400">24</div>
            <div className="text-sm text-slate-400">Combination Tiles</div>
            <div className="text-xs text-slate-500">Higher-Order</div>
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
  ExtendedSynthesisRounds,
  EXTENDED_SYNTHESIS_ROUNDS
};
