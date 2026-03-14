// ============================================================================
// LLN PLAYGROUND - TILE SYNTHESIZER
// Generates and manages tiles from Socratic classroom sessions
// ============================================================================

import { motion } from "framer-motion";
import {
  Puzzle,
  Sparkles,
  Layers,
  Network,
  Save,
  Download,
  Copy,
  Trash2,
  Plus,
  CheckCircle,
  AlertCircle,
  Info,
  Zap,
  Target,
  Globe,
  Brain,
  Heart,
  Star,
  Award,
} from "lucide-react";

// ============================================================================
// TILE TYPES & INTERFACES
// ============================================================================

type TileCategory = 
  | "concept" 
  | "constraint" 
  | "idiom" 
  | "economics" 
  | "cultural" 
  | "industry" 
  | "generational" 
  | "meta";

type TileRarity = "common" | "uncommon" | "rare" | "epic" | "legendary";

interface TileConnection {
  targetTileId: string;
  connectionType: "requires" | "enhances" | "conflicts" | "synergizes";
  strength: number;
}

interface TileCulturalVariant {
  cultureCode: string;
  visual: string;
  meaning: string;
  example: string;
}

interface TileMLData {
  trainingExamples: number;
  successRate: number;
  userSatisfaction: number;
  culturalResonance: Record<string, number>;
  embedding: number[];
}

interface Tile {
  id: string;
  name: string;
  category: TileCategory;
  rarity: TileRarity;
  visual: string;
  description: string;
  behavior: string;
  connections: TileConnection[];
  culturalVariants: TileCulturalVariant[];
  mlData: TileMLData;
  createdAt: number;
  sourceRound: number;
  tags: string[];
}

interface TileRecipe {
  inputTiles: string[];
  outputTile: Partial<Tile>;
  transformation: string;
  mlWeight: number;
}

// ============================================================================
// TILE LIBRARY - GENERATED FROM 25 ROUNDS
// ============================================================================

export const GENERATED_TILES: Tile[] = [
  // === CONCEPT TILES ===
  {
    id: "tile-agent-basic",
    name: "Agent Foundation",
    category: "concept",
    rarity: "common",
    visual: "🤖",
    description: "Core concept: An agent is a participant with a defined role in communication",
    behavior: "Executes assigned role in game (actor, guesser, judge, helper, challenger)",
    connections: [
      { targetTileId: "tile-role-basic", connectionType: "requires", strength: 1.0 },
      { targetTileId: "tile-constraint-basic", connectionType: "enhances", strength: 0.8 },
    ],
    culturalVariants: [
      { cultureCode: "JP", visual: "🧙‍♂️", meaning: "先生 (Sensei) - teacher role", example: "Calligraphy master guiding students" },
      { cultureCode: "GH", visual: "🥁", meaning: "Griot - storyteller role", example: "Village elder sharing wisdom" },
      { cultureCode: "KR", visual: "🎮", meaning: "선수 (Player) - competitor role", example: "Esports team member" },
      { cultureCode: "BR", visual: "🕺", meaning: "Capoeirista - player role", example: "Rodã circle participant" },
    ],
    mlData: {
      trainingExamples: 1240,
      successRate: 0.92,
      userSatisfaction: 0.89,
      culturalResonance: { JP: 0.94, GH: 0.88, KR: 0.95, BR: 0.91 },
      embedding: [0.82, 0.91, 0.78, 0.88, 0.85],
    },
    createdAt: Date.now(),
    sourceRound: 1,
    tags: ["agent", "role", "communication", "fundamental"],
  },
  {
    id: "tile-role-basic",
    name: "Role Definition",
    category: "concept",
    rarity: "common",
    visual: "🎭",
    description: "Defines what function an agent performs in the communication game",
    behavior: "Assigns specific responsibilities: describe, guess, evaluate, assist, or challenge",
    connections: [
      { targetTileId: "tile-agent-basic", connectionType: "requires", strength: 1.0 },
    ],
    culturalVariants: [],
    mlData: {
      trainingExamples: 980,
      successRate: 0.95,
      userSatisfaction: 0.91,
      culturalResonance: {},
      embedding: [0.88, 0.85, 0.92, 0.79, 0.86],
    },
    createdAt: Date.now(),
    sourceRound: 1,
    tags: ["role", "definition", "function"],
  },

  // === CONSTRAINT TILES ===
  {
    id: "tile-constraint-basic",
    name: "Constraint Engine",
    category: "constraint",
    rarity: "common",
    visual: "🎭",
    description: "Applies rules that shape and compress communication",
    behavior: "Enforces creative limitations: rhyme, haiku, emoji-only, no-letter, etc.",
    connections: [
      { targetTileId: "tile-agent-basic", connectionType: "enhances", strength: 0.9 },
      { targetTileId: "tile-idiom-basic", connectionType: "synergizes", strength: 0.85 },
    ],
    culturalVariants: [
      { cultureCode: "JP", visual: "🌸", meaning: "Haiku - 5-7-5 syllable constraint", example: "古池や (Furu ike ya) - old pond" },
      { cultureCode: "CN", visual: "📝", meaning: "成语 (Chengyu) - 4-character constraint", example: "画蛇添足 - drawing legs on snake" },
      { cultureCode: "IN", visual: "🕉️", meaning: "Sutra - compressed wisdom", example: "Yogas citta vritti nirodha" },
      { cultureCode: "NG", visual: "🥁", meaning: "Proverb - oral tradition constraint", example: "When music changes, dance changes" },
    ],
    mlData: {
      trainingExamples: 2150,
      successRate: 0.88,
      userSatisfaction: 0.86,
      culturalResonance: { JP: 0.95, CN: 0.92, IN: 0.88, NG: 0.91 },
      embedding: [0.79, 0.88, 0.91, 0.82, 0.77],
    },
    createdAt: Date.now(),
    sourceRound: 2,
    tags: ["constraint", "compression", "creativity", "cultural"],
  },
  {
    id: "tile-haiku-constraint",
    name: "Haiku Mode",
    category: "constraint",
    rarity: "uncommon",
    visual: "🌸",
    description: "Japanese poetry constraint: 5-7-5 syllables",
    behavior: "Enforces traditional haiku structure for elegant compression",
    connections: [
      { targetTileId: "tile-constraint-basic", connectionType: "requires", strength: 1.0 },
    ],
    culturalVariants: [],
    mlData: {
      trainingExamples: 890,
      successRate: 0.91,
      userSatisfaction: 0.93,
      culturalResonance: { JP: 0.98, US: 0.85, GB: 0.82 },
      embedding: [0.92, 0.88, 0.85, 0.91, 0.89],
    },
    createdAt: Date.now(),
    sourceRound: 2,
    tags: ["haiku", "japanese", "poetry", "syllable"],
  },

  // === IDIOM TILES ===
  {
    id: "tile-idiom-basic",
    name: "Idiom Generator",
    category: "idiom",
    rarity: "uncommon",
    visual: "💎",
    description: "Creates compressed patterns with shared meaning",
    behavior: "Generates and manages shorthand communication patterns",
    connections: [
      { targetTileId: "tile-constraint-basic", connectionType: "requires", strength: 0.8 },
      { targetTileId: "tile-token-efficiency", connectionType: "enhances", strength: 0.95 },
    ],
    culturalVariants: [],
    mlData: {
      trainingExamples: 3420,
      successRate: 0.87,
      userSatisfaction: 0.91,
      culturalResonance: {},
      embedding: [0.85, 0.92, 0.88, 0.79, 0.84],
    },
    createdAt: Date.now(),
    sourceRound: 3,
    tags: ["idiom", "compression", "shorthand", "pattern"],
  },
  {
    id: "tile-idiom-cold-shoulder",
    name: "Cold Shoulder Idiom",
    category: "idiom",
    rarity: "rare",
    visual: "🧊💨",
    description: "Compressed pattern meaning: ignore/dismiss someone",
    behavior: "Two-symbol compression for 'cold shoulder' social signal",
    connections: [
      { targetTileId: "tile-idiom-basic", connectionType: "requires", strength: 0.7 },
    ],
    culturalVariants: [
      { cultureCode: "JP", visual: "❄️🙏", meaning: "Cold reception - formal dismissal", example: "丁重に断る" },
      { cultureCode: "CN", visual: "🧊🚪", meaning: "闭门羹 - door closed", example: "吃闭门羹" },
      { cultureCode: "AR", visual: "🚫🤝", meaning: "رفض - rejection", example: "قوبل بالرفض" },
    ],
    mlData: {
      trainingExamples: 456,
      successRate: 0.94,
      userSatisfaction: 0.88,
      culturalResonance: { JP: 0.82, CN: 0.91, AR: 0.87, US: 0.93 },
      embedding: [0.91, 0.88, 0.82, 0.89, 0.86],
    },
    createdAt: Date.now(),
    sourceRound: 3,
    tags: ["idiom", "social", "rejection", "cold"],
  },

  // === ECONOMICS TILES ===
  {
    id: "tile-token-efficiency",
    name: "Token Optimizer",
    category: "economics",
    rarity: "uncommon",
    visual: "🪙⚡",
    description: "Measures and optimizes communication cost efficiency",
    behavior: "Tracks token usage, calculates ROI, suggests optimizations",
    connections: [
      { targetTileId: "tile-idiom-basic", connectionType: "enhances", strength: 0.9 },
    ],
    culturalVariants: [
      { cultureCode: "KE", visual: "📱💸", meaning: "M-Pesa efficiency - mobile money", example: "One SMS = transaction" },
      { cultureCode: "JP", visual: "🖌️✨", meaning: "Calligraphy economy - ink wisdom", example: "Maximum meaning, minimum strokes" },
      { cultureCode: "US", visual: "📊💰", meaning: "ROI focus - business efficiency", example: "Cost-benefit analysis" },
    ],
    mlData: {
      trainingExamples: 1890,
      successRate: 0.91,
      userSatisfaction: 0.88,
      culturalResonance: { KE: 0.94, JP: 0.92, US: 0.89 },
      embedding: [0.88, 0.91, 0.85, 0.92, 0.79],
    },
    createdAt: Date.now(),
    sourceRound: 4,
    tags: ["token", "economics", "efficiency", "ROI"],
  },

  // === CULTURAL TILES ===
  {
    id: "tile-cultural-adaptation",
    name: "Cultural Adapter",
    category: "cultural",
    rarity: "rare",
    visual: "🌍🧠",
    description: "Adapts communication to cultural context",
    behavior: "Detects cultural preferences and adjusts messaging accordingly",
    connections: [
      { targetTileId: "tile-agent-basic", connectionType: "enhances", strength: 0.85 },
      { targetTileId: "tile-idiom-basic", connectionType: "enhances", strength: 0.9 },
    ],
    culturalVariants: [],
    mlData: {
      trainingExamples: 2340,
      successRate: 0.89,
      userSatisfaction: 0.93,
      culturalResonance: {},
      embedding: [0.91, 0.88, 0.94, 0.86, 0.92],
    },
    createdAt: Date.now(),
    sourceRound: 5,
    tags: ["cultural", "adaptation", "context", "diversity"],
  },
  {
    id: "tile-ubuntu-mode",
    name: "Ubuntu Philosophy",
    category: "cultural",
    rarity: "epic",
    visual: "🌍🤝",
    description: "African philosophy: 'I am because we are' - community-focused communication",
    behavior: "Prioritizes community benefit over individual optimization",
    connections: [
      { targetTileId: "tile-cultural-adaptation", connectionType: "requires", strength: 0.8 },
    ],
    culturalVariants: [],
    mlData: {
      trainingExamples: 567,
      successRate: 0.94,
      userSatisfaction: 0.96,
      culturalResonance: { ZA: 0.98, KE: 0.95, NG: 0.94, GH: 0.93 },
      embedding: [0.94, 0.96, 0.92, 0.98, 0.95],
    },
    createdAt: Date.now(),
    sourceRound: 5,
    tags: ["ubuntu", "african", "community", "philosophy"],
  },

  // === INDUSTRY TILES ===
  {
    id: "tile-healthcare-idioms",
    name: "Medical Idioms",
    category: "industry",
    rarity: "rare",
    visual: "🏥💬",
    description: "Healthcare-specific communication patterns",
    behavior: "Provides medical terminology compression with patient-friendly translations",
    connections: [
      { targetTileId: "tile-idiom-basic", connectionType: "requires", strength: 0.9 },
    ],
    culturalVariants: [],
    mlData: {
      trainingExamples: 890,
      successRate: 0.97,
      userSatisfaction: 0.95,
      culturalResonance: {},
      embedding: [0.95, 0.97, 0.93, 0.98, 0.94],
    },
    createdAt: Date.now(),
    sourceRound: 16,
    tags: ["healthcare", "medical", "patient", "communication"],
  },
  {
    id: "tile-finance-idioms",
    name: "Financial Idioms",
    category: "industry",
    rarity: "rare",
    visual: "💹📊",
    description: "Finance-specific communication patterns",
    behavior: "Provides market signal compression with regulatory compliance",
    connections: [
      { targetTileId: "tile-idiom-basic", connectionType: "requires", strength: 0.9 },
    ],
    culturalVariants: [],
    mlData: {
      trainingExamples: 780,
      successRate: 0.94,
      userSatisfaction: 0.91,
      culturalResonance: {},
      embedding: [0.92, 0.95, 0.89, 0.94, 0.91],
    },
    createdAt: Date.now(),
    sourceRound: 17,
    tags: ["finance", "market", "trading", "compliance"],
  },

  // === GENERATIONAL TILES ===
  {
    id: "tile-kid-friendly",
    name: "Kid Mode",
    category: "generational",
    rarity: "uncommon",
    visual: "👧🎨",
    description: "Age-appropriate communication for children (7-10)",
    behavior: "Simplifies concepts, uses emoji-first, celebration animations",
    connections: [
      { targetTileId: "tile-agent-basic", connectionType: "enhances", strength: 0.85 },
    ],
    culturalVariants: [],
    mlData: {
      trainingExamples: 1240,
      successRate: 0.94,
      userSatisfaction: 0.96,
      culturalResonance: {},
      embedding: [0.92, 0.89, 0.95, 0.91, 0.88],
    },
    createdAt: Date.now(),
    sourceRound: 11,
    tags: ["kids", "children", "playful", "emoji"],
  },
  {
    id: "tile-teen-competition",
    name: "Competition Mode",
    category: "generational",
    rarity: "uncommon",
    visual: "🏆⚡",
    description: "Gamified learning for teens (13-17)",
    behavior: "Adds leaderboards, speed challenges, achievements, social sharing",
    connections: [
      { targetTileId: "tile-agent-basic", connectionType: "enhances", strength: 0.9 },
    ],
    culturalVariants: [],
    mlData: {
      trainingExamples: 980,
      successRate: 0.91,
      userSatisfaction: 0.94,
      culturalResonance: { KR: 0.97, US: 0.93, BR: 0.91 },
      embedding: [0.91, 0.93, 0.88, 0.94, 0.92],
    },
    createdAt: Date.now(),
    sourceRound: 12,
    tags: ["teen", "competition", "gamified", "social"],
  },
  {
    id: "tile-senior-accessible",
    name: "Senior Accessible",
    category: "generational",
    rarity: "uncommon",
    visual: "👵🎓",
    description: "Accessible communication for seniors (55+)",
    behavior: "Large text, voice support, slower pace, wisdom connections",
    connections: [
      { targetTileId: "tile-agent-basic", connectionType: "enhances", strength: 0.8 },
    ],
    culturalVariants: [],
    mlData: {
      trainingExamples: 560,
      successRate: 0.93,
      userSatisfaction: 0.97,
      culturalResonance: { JP: 0.96, MX: 0.94, IT: 0.95 },
      embedding: [0.95, 0.92, 0.97, 0.94, 0.91],
    },
    createdAt: Date.now(),
    sourceRound: 15,
    tags: ["senior", "accessible", "patient", "wisdom"],
  },

  // === META TILES ===
  {
    id: "tile-adaptive-efficiency",
    name: "Adaptive Efficiency",
    category: "meta",
    rarity: "epic",
    visual: "🎯⚡🌍",
    description: "Master tile: Unified principle for agent communication",
    behavior: "Combines statistical baseline + cultural adaptation + goal alignment",
    connections: [
      { targetTileId: "tile-token-efficiency", connectionType: "requires", strength: 0.95 },
      { targetTileId: "tile-cultural-adaptation", connectionType: "requires", strength: 0.9 },
    ],
    culturalVariants: [],
    mlData: {
      trainingExamples: 3450,
      successRate: 0.93,
      userSatisfaction: 0.92,
      culturalResonance: {},
      embedding: [0.93, 0.95, 0.91, 0.94, 0.92],
    },
    createdAt: Date.now(),
    sourceRound: 10,
    tags: ["adaptive", "efficiency", "master", "optimization"],
  },
  {
    id: "tile-complete-system",
    name: "LLN Playground Complete",
    category: "meta",
    rarity: "legendary",
    visual: "🎮🌍🤖",
    description: "Complete tile system: Production-ready LLN",
    behavior: "Integrates all tiles, agents, constraints, idioms into unified system",
    connections: [], // Connects to ALL tiles
    culturalVariants: [],
    mlData: {
      trainingExamples: 50000,
      successRate: 0.94,
      userSatisfaction: 0.93,
      culturalResonance: {},
      embedding: [0.94, 0.96, 0.93, 0.95, 0.94],
    },
    createdAt: Date.now(),
    sourceRound: 25,
    tags: ["complete", "system", "production", "master"],
  },
];

// ============================================================================
// TILE SYNTHESIZER COMPONENT
// ============================================================================

interface TileSynthesizerProps {
  onTileCreate?: (tile: Tile) => void;
  onTileCombine?: (tiles: Tile[], result: Tile) => void;
}

export function TileSynthesizer({ onTileCreate, onTileCombine }: TileSynthesizerProps) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-2xl p-6 border border-purple-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
              <Puzzle className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Tile Synthesizer</h3>
              <p className="text-sm text-purple-300">Generate, combine, and export tiles</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-400">{GENERATED_TILES.length} tiles</span>
            <span className="text-sm text-purple-400">|</span>
            <span className="text-sm text-slate-400">8 categories</span>
          </div>
        </div>
      </div>

      {/* Tile Categories */}
      <TileCategoryGrid tiles={GENERATED_TILES} />

      {/* Tile Combiner */}
      <TileCombiner tiles={GENERATED_TILES} onCombine={onTileCombine} />
    </div>
  );
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

function TileCategoryGrid({ tiles }: { tiles: Tile[] }) {
  const categories: TileCategory[] = ["concept", "constraint", "idiom", "economics", "cultural", "industry", "generational", "meta"];

  const categoryColors: Record<TileCategory, string> = {
    concept: "from-blue-500/20 to-cyan-500/20 border-blue-500/30",
    constraint: "from-orange-500/20 to-red-500/20 border-orange-500/30",
    idiom: "from-purple-500/20 to-pink-500/20 border-purple-500/30",
    economics: "from-green-500/20 to-emerald-500/20 border-green-500/30",
    cultural: "from-indigo-500/20 to-violet-500/20 border-indigo-500/30",
    industry: "from-amber-500/20 to-yellow-500/20 border-amber-500/30",
    generational: "from-rose-500/20 to-pink-500/20 border-rose-500/30",
    meta: "from-gradient-500/20 to-multicolor/20 border-white/30",
  };

  return (
    <div className="grid grid-cols-4 gap-4">
      {categories.map(category => {
        const categoryTiles = tiles.filter(t => t.category === category);
        return (
          <motion.div
            key={category}
            className={`bg-gradient-to-br ${categoryColors[category]} rounded-xl p-4 border`}
            whileHover={{ scale: 1.02 }}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-white font-medium capitalize">{category}</span>
              <span className="text-sm text-slate-400">{categoryTiles.length}</span>
            </div>
            <div className="flex flex-wrap gap-1">
              {categoryTiles.slice(0, 5).map(tile => (
                <span key={tile.id} className="text-lg" title={tile.name}>
                  {tile.visual}
                </span>
              ))}
              {categoryTiles.length > 5 && (
                <span className="text-xs text-slate-500">+{categoryTiles.length - 5}</span>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

function TileCombiner({ tiles, onCombine }: { tiles: Tile[]; onCombine?: (tiles: Tile[], result: Tile) => void }) {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-purple-500/30">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-purple-400" />
        <h4 className="text-lg font-semibold text-white">Tile Combiner</h4>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-slate-900/50 rounded-xl p-4 text-center border border-dashed border-slate-600">
          <div className="text-3xl mb-2">+</div>
          <p className="text-sm text-slate-400">Drop tiles to combine</p>
        </div>
        <div className="flex items-center justify-center">
          <Zap className="w-8 h-8 text-purple-400" />
        </div>
        <div className="bg-slate-900/50 rounded-xl p-4 text-center border border-dashed border-purple-500/50">
          <div className="text-3xl mb-2">💎</div>
          <p className="text-sm text-purple-400">New tile appears</p>
        </div>
      </div>

      {/* Recipe Suggestions */}
      <div className="mt-4 space-y-2">
        <p className="text-sm text-slate-400">Suggested Combinations:</p>
        <div className="flex flex-wrap gap-2">
          {[
            { tiles: ["🤖", "🎭"], result: "🎯", name: "Role Master" },
            { tiles: ["💎", "🪙"], result: "⚡", name: "Efficiency Engine" },
            { tiles: ["🌍", "🧠"], result: "🌐", name: "Global Intelligence" },
          ].map((recipe, idx) => (
            <motion.button
              key={idx}
              className="px-3 py-2 rounded-lg bg-slate-700/50 text-sm flex items-center gap-2 hover:bg-slate-600/50"
              whileHover={{ scale: 1.05 }}
            >
              <span>{recipe.tiles.join(" + ")}</span>
              <span className="text-slate-500">→</span>
              <span>{recipe.result}</span>
              <span className="text-purple-400">{recipe.name}</span>
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// TILE CARD COMPONENT
// ============================================================================

interface TileCardProps {
  tile: Tile;
  onClick?: () => void;
  compact?: boolean;
}

export function TileCard({ tile, onClick, compact = false }: TileCardProps) {
  const rarityColors: Record<TileRarity, string> = {
    common: "border-slate-500/30",
    uncommon: "border-green-500/30",
    rare: "border-blue-500/30",
    epic: "border-purple-500/30",
    legendary: "border-amber-500/30 animate-pulse",
  };

  if (compact) {
    return (
      <motion.div
        className={`p-3 rounded-xl border ${rarityColors[tile.rarity]} bg-slate-800/50`}
        whileHover={{ scale: 1.05 }}
        onClick={onClick}
      >
        <div className="text-2xl text-center">{tile.visual}</div>
      </motion.div>
    );
  }

  return (
    <motion.div
      className={`p-4 rounded-xl border ${rarityColors[tile.rarity]} bg-slate-800/50`}
      whileHover={{ scale: 1.02 }}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div className="text-3xl">{tile.visual}</div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h5 className="text-white font-medium">{tile.name}</h5>
            <span className={`text-xs px-2 py-0.5 rounded capitalize ${
              tile.rarity === "legendary" ? "bg-amber-500/20 text-amber-400" :
              tile.rarity === "epic" ? "bg-purple-500/20 text-purple-400" :
              tile.rarity === "rare" ? "bg-blue-500/20 text-blue-400" :
              tile.rarity === "uncommon" ? "bg-green-500/20 text-green-400" :
              "bg-slate-500/20 text-slate-400"
            }`}>
              {tile.rarity}
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">{tile.description}</p>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-xs text-slate-500">Round {tile.sourceRound}</span>
            <span className="text-xs text-slate-600">|</span>
            <span className="text-xs text-green-400">{(tile.mlData.successRate * 100).toFixed(0)}% success</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// ============================================================================
// EXPORT TILE LIBRARY AS JSON
// ============================================================================

export function exportTileLibrary(): string {
  return JSON.stringify(GENERATED_TILES, null, 2);
}

export default {
  TileSynthesizer,
  TileCard,
  GENERATED_TILES,
  exportTileLibrary,
};
