"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { motion, AnimatePresence, useAnimation } from "framer-motion";
import {
  Gamepad2,
  Brain,
  Coins,
  Zap,
  MessageSquare,
  Users,
  Sparkles,
  Lock,
  Unlock,
  TrendingUp,
  Target,
  RefreshCw,
  Play,
  Pause,
  Plus,
  Trash2,
  Copy,
  Download,
  Settings,
  ChevronRight,
  Hash,
  Layers,
  Network,
  Atom,
  Shuffle,
  Award,
  Timer,
  Volume2,
  VolumeX,
  Baby,
  GraduationCap,
  Briefcase,
  Microscope,
  Palette,
  BarChart3,
  Trophy,
  Star,
  Heart,
  Rocket,
  Wand2,
  BookOpen,
  Code2,
  Lightbulb,
  Puzzle,
  Music,
  Camera,
  Film,
  Edit3,
  Save,
  Share2,
  Eye,
  ThumbsUp,
  MessageCircle,
  Crown,
  Flame,
  Snowflake,
  Sun,
  Moon,
  Cloud,
  Droplet,
  Leaf,
  Flower2,
  TreePine,
  Bird,
  Fish,
  Bug,
  Ghost,
  Alien,
  Rocket as RocketIcon,
  Planet,
  Star as StarIcon,
  Galaxy,
  User,
  UserPlus,
  Settings2,
  PanelLeft,
  X,
  Check,
  AlertCircle,
  Info,
  HelpCircle,
  Coffee,
  Pizza,
  Apple,
  Cookie,
  Candy,
  Cake,
  Gift,
  PartyPopper,
  Confetti,
  Compass,
  Search,
  Filter,
  LayoutGrid,
  LayoutList,
  Database,
  Cpu,
  TreeDeciduous,
  FlaskConical,
  Globe,
  Merge,
  Hexagon,
  Box,
  GitMerge,
  Diamond,
} from "lucide-react";
import Link from "next/link";

// Import all our major components
import { SynthesisEngine, COMBINATION_TILES, METHOD_INGREDIENTS, discoverCombinations } from "./SynthesisEngine";
import { MyceliumNetwork, MyceliumNetworkSimulation, LifePrinciplesDisplay } from "./MyceliumNetwork";
import { OriginFirstDistillation, BootstrapIntelligenceEngine, SuperInstanceWorkflow, SEED_LIBRARY, GEOMETRIC_COMPRESSORS } from "./OriginFirstDistillation";
import { KnowledgeDistillationSystem, OriginFirstDistillationEngine } from "./KnowledgeDistillationSystem";
import { UserLearningEngineComponent } from "./UserLearningEngine";
import { ExplorerHub } from "./ExplorerHub";
import { ExtendedSynthesisRounds, EXTENDED_SYNTHESIS_ROUNDS } from "./SynthesisRoundsExtended";
import { RealTimeGameEngine } from "./RealTimeGameEngine";
import { GameSimulationSwitcher } from "./GameSimulationSwitcher";
import { MLUserActionTracker } from "./MLUserActionTracker";
import { VoxelGameIntegrator } from "./VoxelGameIntegrator";
import { SpeedLearningPath } from "./SpeedLearningPath";

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

type UserRole = "kid" | "teen" | "developer" | "researcher" | "enterprise" | "educator" | "hobbyist" | "scientist" | "pm" | "artist";
type GameMode = "charades" | "word-chain" | "story-build" | "riddle-battle" | "emoji-translate" | "concept-map" | "debate" | "improv";
type DifficultyLevel = "beginner" | "intermediate" | "advanced" | "expert";
type HubSection = "play" | "synthesis" | "mycelium" | "distillation" | "learning" | "explorer" | "rounds" | "voxel" | "speedrun";

interface UserProfile {
  id: string;
  role: UserRole;
  displayName: string;
  avatar: string;
  level: number;
  xp: number;
  achievements: string[];
  preferences: UserPreferences;
  stats: UserStats;
}

interface UserPreferences {
  theme: "light" | "dark" | "auto";
  soundEnabled: boolean;
  animationsEnabled: boolean;
  language: string;
  difficulty: DifficultyLevel;
  aiAssistance: boolean;
  showTutorial: boolean;
}

interface UserStats {
  gamesPlayed: number;
  gamesWon: number;
  totalTokens: number;
  tokensSaved: number;
  idiomsCreated: number;
  favoriteMode: GameMode;
  streak: number;
  bestStreak: number;
}

interface Agent {
  id: string;
  name: string;
  emoji: string;
  role: "actor" | "guesser" | "judge" | "observer" | "helper" | "challenger";
  personality: string;
  modelType: string;
  tokensUsed: number;
  wins: number;
  idioms: string[];
  color: string;
  unlocked: boolean;
  description: string;
}

interface Constraint {
  id: string;
  type: "rhyme" | "no-letter" | "roast" | "negative" | "haiku" | "emoji-only" | "one-syllable" | "alphabetical" | "pirate" | "shakespeare" | "custom";
  value: string;
  emoji: string;
  penalty: number;
  active: boolean;
  unlocked: boolean;
  category: "beginner" | "intermediate" | "advanced" | "expert";
  description: string;
}

interface GameRound {
  id: string;
  target: string;
  category: string;
  actors: string[];
  guessers: string[];
  judges: string[];
  constraints: Constraint[];
  messages: GameMessage[];
  status: "waiting" | "acting" | "guessing" | "judging" | "complete";
  winner?: string;
  tokenCost: number;
  timeElapsed: number;
  hints: string[];
  hintsUsed: number;
}

interface GameMessage {
  id: string;
  agentId: string;
  content: string;
  type: "description" | "guess" | "judgment" | "idiom-generated" | "hint" | "reaction" | "celebration";
  tokens: number;
  constraintApplied?: string;
  timestamp: number;
  reactions?: { emoji: string; count: number }[];
}

interface Idiom {
  id: string;
  shorthand: string;
  meaning: string;
  originAgents: string[];
  usageCount: number;
  tokenSavings: number;
  seed?: string;
  lockedToSeed: boolean;
  category: string;
  createdBy?: string;
}

// ============================================================================
// CONSTANTS & DATA
// ============================================================================

const USER_ROLE_CONFIG: Record<UserRole, {
  label: string;
  icon: React.ElementType;
  color: string;
  description: string;
  defaultDifficulty: DifficultyLevel;
  features: string[];
}> = {
  kid: {
    label: "Young Explorer",
    icon: Baby,
    color: "#10B981",
    description: "Learn through play! Fun games and friendly AI helpers.",
    defaultDifficulty: "beginner",
    features: ["Friendly avatars", "Picture hints", "Celebration animations", "Simple words", "Voice support"]
  },
  teen: {
    label: "Challenger",
    icon: Flame,
    color: "#F59E0B",
    description: "Compete, create, and connect with friends!",
    defaultDifficulty: "intermediate",
    features: ["Leaderboards", "Multiplayer", "Custom games", "Social sharing", "Achievements"]
  },
  developer: {
    label: "Builder",
    icon: Code2,
    color: "#6366F1",
    description: "Build agents, APIs, and custom game logic.",
    defaultDifficulty: "advanced",
    features: ["Agent editor", "API access", "Debug mode", "Token analytics", "Export tools"]
  },
  researcher: {
    label: "Researcher",
    icon: Microscope,
    color: "#8B5CF6",
    description: "Study AI communication patterns and collect data.",
    defaultDifficulty: "advanced",
    features: ["Data export", "Pattern analysis", "Experiment builder", "Citation tools", "Privacy controls"]
  },
  enterprise: {
    label: "Enterprise",
    icon: Briefcase,
    color: "#0EA5E9",
    description: "Optimize business communication and train custom models.",
    defaultDifficulty: "intermediate",
    features: ["Team management", "Custom idioms", "Analytics dashboard", "SSO", "Support"]
  },
  educator: {
    label: "Educator",
    icon: BookOpen,
    color: "#EC4899",
    description: "Create lessons and track student progress.",
    defaultDifficulty: "intermediate",
    features: ["Lesson builder", "Student tracking", "Assignments", "Progress reports", "Curriculum tools"]
  },
  hobbyist: {
    label: "Enthusiast",
    icon: Wand2,
    color: "#14B8A6",
    description: "Experiment with AI and create fun experiences.",
    defaultDifficulty: "intermediate",
    features: ["Playground mode", "Experiment tools", "Community sharing", "Templates", "Tutorials"]
  },
  scientist: {
    label: "Data Scientist",
    icon: BarChart3,
    color: "#F97316",
    description: "Analyze patterns and build predictive models.",
    defaultDifficulty: "expert",
    features: ["Data pipelines", "ML tools", "Visualization", "Statistical analysis", "Export formats"]
  },
  pm: {
    label: "Product Manager",
    icon: Target,
    color: "#84CC16",
    description: "A/B test UX and gather insights.",
    defaultDifficulty: "intermediate",
    features: ["Experiment builder", "Metrics", "User recordings", "Heatmaps", "Feedback tools"]
  },
  artist: {
    label: "Creative",
    icon: Palette,
    color: "#D946EF",
    description: "Generate art, stories, and creative content.",
    defaultDifficulty: "beginner",
    features: ["Generative tools", "Style transfer", "Story mode", "Art prompts", "Gallery"]
  }
};

const GAME_MODES: Record<GameMode, {
  label: string;
  description: string;
  icon: React.ElementType;
  difficulty: DifficultyLevel;
  minPlayers: number;
  maxPlayers: number;
  avgTokens: number;
}> = {
  charades: {
    label: "Charades",
    description: "Classic guessing game - describe without saying the word!",
    icon: MessageSquare,
    difficulty: "beginner",
    minPlayers: 2,
    maxPlayers: 8,
    avgTokens: 150
  },
  "word-chain": {
    label: "Word Chain",
    description: "Each word must start with the last letter of the previous word.",
    icon: ChevronRight,
    difficulty: "beginner",
    minPlayers: 2,
    maxPlayers: 10,
    avgTokens: 80
  },
  "story-build": {
    label: "Story Builder",
    description: "Collaboratively create a story, one sentence at a time.",
    icon: BookOpen,
    difficulty: "intermediate",
    minPlayers: 2,
    maxPlayers: 6,
    avgTokens: 200
  },
  "riddle-battle": {
    label: "Riddle Battle",
    description: "Create and solve riddles competitively.",
    icon: Sparkles,
    difficulty: "intermediate",
    minPlayers: 2,
    maxPlayers: 4,
    avgTokens: 180
  },
  "emoji-translate": {
    label: "Emoji Translator",
    description: "Translate phrases using only emojis.",
    icon: Sun,
    difficulty: "beginner",
    minPlayers: 2,
    maxPlayers: 6,
    avgTokens: 60
  },
  "concept-map": {
    label: "Concept Mapping",
    description: "Build knowledge graphs through collaborative connections.",
    icon: Network,
    difficulty: "advanced",
    minPlayers: 2,
    maxPlayers: 4,
    avgTokens: 250
  },
  debate: {
    label: "AI Debate",
    description: "Structured debates with AI judges scoring arguments.",
    icon: MessageCircle,
    difficulty: "expert",
    minPlayers: 2,
    maxPlayers: 2,
    avgTokens: 400
  },
  improv: {
    label: "Improv Theater",
    description: "Spontaneous scenes and characters with audience suggestions.",
    icon: Palette,
    difficulty: "advanced",
    minPlayers: 2,
    maxPlayers: 8,
    avgTokens: 300
  }
};

const CONSTRAINT_TEMPLATES: Constraint[] = [
  { id: "1", type: "rhyme", value: "Your descriptions must rhyme!", emoji: "🎭", penalty: 1.2, active: false, unlocked: true, category: "beginner", description: "Make every line rhyme like a poem" },
  { id: "2", type: "no-letter", value: "Don't use the letter 'E'!", emoji: "🚫", penalty: 1.5, active: false, unlocked: true, category: "intermediate", description: "A lipogram challenge - avoid the most common letter" },
  { id: "3", type: "roast", value: "Roast your opponents playfully!", emoji: "🔥", penalty: 1.3, active: false, unlocked: true, category: "teen", description: "Give a funny burn and score it 0-100" },
  { id: "4", type: "negative", value: "Only describe what it's NOT", emoji: "➖", penalty: 1.4, active: false, unlocked: true, category: "beginner", description: "Reverse psychology - negatives only" },
  { id: "5", type: "haiku", value: "Speak only in haiku (5-7-5)", emoji: "🌸", penalty: 1.1, active: false, unlocked: true, category: "intermediate", description: "Traditional Japanese poetry format" },
  { id: "6", type: "emoji-only", value: "Only emojis, no words!", emoji: "😀", penalty: 1.6, active: false, unlocked: true, category: "beginner", description: "Pure visual communication" },
  { id: "7", type: "one-syllable", value: "One syllable words only!", emoji: "🎵", penalty: 1.3, active: false, unlocked: false, category: "intermediate", description: "Keep it simple, one beat at a time" },
  { id: "8", type: "alphabetical", value: "Each word starts with next letter!", emoji: "🔤", penalty: 1.7, active: false, unlocked: false, category: "advanced", description: "A-B-C-D... sequential speaking" },
  { id: "9", type: "pirate", value: "Talk like a pirate, matey!", emoji: "🏴‍☠️", penalty: 1.2, active: false, unlocked: false, category: "beginner", description: "Arrr, speak the seven seas way" },
  { id: "10", type: "shakespeare", value: "Speak like Shakespeare!", emoji: "🎭", penalty: 1.4, active: false, unlocked: false, category: "advanced", description: "Thee must speak in Olde English" },
];

const AGENT_TEMPLATES: Agent[] = [
  { id: "a1", name: "Riddler", emoji: "🧩", role: "actor", personality: "mysterious", modelType: "gpt-4", tokensUsed: 0, wins: 0, idioms: [], color: "#10B981", unlocked: true, description: "Loves cryptic clues and wordplay" },
  { id: "a2", name: "Oracle", emoji: "🔮", role: "guesser", personality: "wise", modelType: "claude-3", tokensUsed: 0, wins: 0, idioms: [], color: "#8B5CF6", unlocked: true, description: "Analytical and thoughtful" },
  { id: "a3", name: "Jester", emoji: "🃏", role: "actor", personality: "playful", modelType: "gemini-pro", tokensUsed: 0, wins: 0, idioms: [], color: "#F59E0B", unlocked: true, description: "Funny and unpredictable" },
  { id: "a4", name: "Sage", emoji: "🦉", role: "judge", personality: "fair", modelType: "gpt-4", tokensUsed: 0, wins: 0, idioms: [], color: "#EC4899", unlocked: true, description: "Balanced and encouraging" },
  { id: "a5", name: "Sparky", emoji: "⚡", role: "helper", personality: "energetic", modelType: "claude-3", tokensUsed: 0, wins: 0, idioms: [], color: "#FCD34D", unlocked: false, description: "Gives hints and encouragement" },
  { id: "a6", name: "Shadow", emoji: "🌑", role: "challenger", personality: "tricky", modelType: "gemini-pro", tokensUsed: 0, wins: 0, idioms: [], color: "#374151", unlocked: false, description: "Adds twists and challenges" },
  { id: "a7", name: "Buddy", emoji: "🤗", role: "helper", personality: "friendly", modelType: "gpt-4", tokensUsed: 0, wins: 0, idioms: [], color: "#FB923C", unlocked: false, description: "Perfect for kids - super supportive!" },
  { id: "a8", name: "Pixel", emoji: "👾", role: "actor", personality: "gamer", modelType: "claude-3", tokensUsed: 0, wins: 0, idioms: [], color: "#A855F7", unlocked: false, description: "Speaks in gaming terms" },
];

const WORD_CATEGORIES = [
  { id: "animals", name: "Animals", emoji: "🐾", words: ["ELEPHANT", "PENGUIN", "GIRAFFE", "DOLPHIN", "BUTTERFLY"], difficulty: "beginner", unlocked: true },
  { id: "food", name: "Food", emoji: "🍕", words: ["PIZZA", "BANANA", "CHOCOLATE", "SPAGHETTI", "ICE CREAM"], difficulty: "beginner", unlocked: true },
  { id: "nature", name: "Nature", emoji: "🌿", words: ["RAINBOW", "MOUNTAIN", "OCEAN", "VOLCANO", "WATERFALL"], difficulty: "beginner", unlocked: true },
  { id: "tech", name: "Technology", emoji: "💻", words: ["COMPUTER", "ROBOT", "SATELLITE", "ALGORITHM", "BLOCKCHAIN"], difficulty: "intermediate", unlocked: true },
  { id: "science", name: "Science", emoji: "🔬", words: ["GRAVITY", "MOLECULE", "ECOSYSTEM", "PHOTON", "EVOLUTION"], difficulty: "intermediate", unlocked: true },
  { id: "emotions", name: "Emotions", emoji: "💭", words: ["HAPPINESS", "CURIOSITY", "NOSTALGIA", "EXCITEMENT", "SURPRISE"], difficulty: "intermediate", unlocked: true },
  { id: "concepts", name: "Abstract Concepts", emoji: "🧠", words: ["FREEDOM", "JUSTICE", "INFINITY", "PARADOX", "SERENDIPITY"], difficulty: "advanced", unlocked: false },
  { id: "professions", name: "Jobs", emoji: "👔", words: ["ASTRONAUT", "ARCHITECT", "DETECTIVE", "INVENTOR", "PHILOSOPHER"], difficulty: "beginner", unlocked: true },
];

const SAMPLE_IDIOMS: Idiom[] = [
  { id: "i1", shorthand: "🧊💨", meaning: "Cold shoulder - ignore/dismiss", originAgents: ["a1", "a2"], usageCount: 47, tokenSavings: 142, lockedToSeed: false, category: "social" },
  { id: "i2", shorthand: "🎲→🎯", meaning: "Random becomes intentional", originAgents: ["a2", "a3"], usageCount: 23, tokenSavings: 89, lockedToSeed: true, seed: "seed_7x9_omega", category: "strategy" },
  { id: "i3", shorthand: "🌊🧠", meaning: "Deep thought / flow state", originAgents: ["a1", "a3"], usageCount: 156, tokenSavings: 312, lockedToSeed: false, category: "mental" },
  { id: "i4", shorthand: "🔥🧩", meaning: "Challenging but exciting", originAgents: ["a3", "a4"], usageCount: 34, tokenSavings: 78, lockedToSeed: false, category: "emotional" },
  { id: "i5", shorthand: "👀💡", meaning: "I see the idea now!", originAgents: ["a2", "a4"], usageCount: 89, tokenSavings: 167, lockedToSeed: false, category: "learning" },
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function LLNPlayground() {
  // User State
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [showRoleSelector, setShowRoleSelector] = useState(true);
  
  // Game State
  const [selectedMode, setSelectedMode] = useState<GameMode>("charades");
  const [selectedCategory, setSelectedCategory] = useState("animals");
  const [agents, setAgents] = useState<Agent[]>(AGENT_TEMPLATES);
  const [constraints, setConstraints] = useState<Constraint[]>(CONSTRAINT_TEMPLATES);
  const [activeConstraints, setActiveConstraints] = useState<Constraint[]>([]);
  const [idioms, setIdioms] = useState<Idiom[]>(SAMPLE_IDIOMS);
  
  // Play State
  const [currentRound, setCurrentRound] = useState<GameRound | null>(null);
  const [messages, setMessages] = useState<GameMessage[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [roundHistory, setRoundHistory] = useState<GameRound[]>([]);
  
  // Hub Navigation
  const [activeSection, setActiveSection] = useState<HubSection>("play");
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  
  // Mycelium Simulation
  const [myceliumSimulation] = useState(() => new MyceliumNetworkSimulation());

  // Derived values
  const categoryWords = WORD_CATEGORIES.find(c => c.id === selectedCategory)?.words || [];
  const targetWord = categoryWords[Math.floor(Math.random() * categoryWords.length)] || "BANANA";

  // Handlers
  const handleRoleSelect = (role: UserRole) => {
    const config = USER_ROLE_CONFIG[role];
    setUserProfile({
      id: `user_${Date.now()}`,
      role,
      displayName: config.label,
      avatar: "🎮",
      level: 1,
      xp: 0,
      achievements: [],
      preferences: {
        theme: "dark",
        soundEnabled: true,
        animationsEnabled: true,
        language: "en",
        difficulty: config.defaultDifficulty,
        aiAssistance: false,
        showTutorial: true,
      },
      stats: {
        gamesPlayed: 0,
        gamesWon: 0,
        totalTokens: 0,
        tokensSaved: 0,
        idiomsCreated: 0,
        favoriteMode: "charades",
        streak: 0,
        bestStreak: 0,
      },
    });
    setShowRoleSelector(false);
  };

  const toggleConstraint = (constraint: Constraint) => {
    if (activeConstraints.find(c => c.id === constraint.id)) {
      setActiveConstraints(prev => prev.filter(c => c.id !== constraint.id));
    } else {
      setActiveConstraints(prev => [...prev, constraint]);
    }
  };

  const toggleIdiomLock = (idiom: Idiom) => {
    setIdioms(prev => prev.map(i =>
      i.id === idiom.id
        ? { ...i, lockedToSeed: !i.lockedToSeed, seed: i.lockedToSeed ? undefined : `seed_${Math.random().toString(36).substr(2, 9)}` }
        : i
    ));
  };

  // Game simulation
  const simulateRound = useCallback(async () => {
    if (!targetWord) return;

    const round: GameRound = {
      id: `round_${Date.now()}`,
      target: targetWord.toUpperCase(),
      category: selectedCategory,
      actors: agents.filter(a => a.role === "actor" && a.unlocked).map(a => a.id),
      guessers: agents.filter(a => a.role === "guesser" && a.unlocked).map(a => a.id),
      judges: agents.filter(a => a.role === "judge" && a.unlocked).map(a => a.id),
      constraints: activeConstraints,
      messages: [],
      status: "acting",
      tokenCost: 0,
      timeElapsed: 0,
      hints: [],
      hintsUsed: 0,
    };

    setCurrentRound(round);
    setMessages([]);
    setIsPlaying(true);

    const actors = agents.filter(a => a.role === "actor" && a.unlocked);
    const guessers = agents.filter(a => a.role === "guesser" && a.unlocked);

    // Generate descriptions
    for (const actor of actors) {
      await new Promise(resolve => setTimeout(resolve, 800));
      const desc = generateDescription(targetWord, activeConstraints, actor);
      const msg: GameMessage = {
        id: `msg_${Date.now()}`,
        agentId: actor.id,
        content: desc,
        type: "description",
        tokens: Math.floor(desc.length * 0.3 * (activeConstraints.length > 0 ? 1.3 : 1)),
        constraintApplied: activeConstraints[0]?.type,
        timestamp: Date.now(),
        reactions: [{ emoji: "👍", count: Math.floor(Math.random() * 5) + 1 }],
      };
      setMessages(prev => [...prev, msg]);
      setCurrentRound(prev => prev ? { ...prev, tokenCost: prev.tokenCost + msg.tokens } : null);
    }

    // Generate guesses
    await new Promise(resolve => setTimeout(resolve, 1000));
    round.status = "guessing";
    setCurrentRound({ ...round });

    for (const guesser of guessers) {
      await new Promise(resolve => setTimeout(resolve, 600));
      const guess = generateGuess(targetWord, activeConstraints);
      const msg: GameMessage = {
        id: `msg_${Date.now()}`,
        agentId: guesser.id,
        content: guess,
        type: "guess",
        tokens: Math.floor(guess.length * 0.25),
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, msg]);
      setCurrentRound(prev => prev ? { ...prev, tokenCost: prev.tokenCost + msg.tokens } : null);

      if (guess.toLowerCase().includes(targetWord.toLowerCase())) {
        round.winner = guesser.id;
        round.status = "complete";
        setCurrentRound({ ...round });

        // Celebration message
        const celebrationMsg: GameMessage = {
          id: `msg_${Date.now()}`,
          agentId: "system",
          content: `🎉 ${guesser.name} got it! The word was "${targetWord.toUpperCase()}"!`,
          type: "celebration",
          tokens: 0,
          timestamp: Date.now(),
        };
        setMessages(prev => [...prev, celebrationMsg]);

        // Generate idiom
        if (activeConstraints.length > 0) {
          const newIdiom = generateIdiom(actors[0], guesser, targetWord);
          setIdioms(prev => [...prev, newIdiom]);
        }
        break;
      }
    }

    if (!round.winner) {
      round.status = "judging";
      setCurrentRound({ ...round });
      await new Promise(resolve => setTimeout(resolve, 800));
      
      const judge = agents.find(a => a.role === "judge" && a.unlocked);
      if (judge) {
        const judgment = `The word was "${targetWord.toUpperCase()}". Great effort! Try again?`;
        const msg: GameMessage = {
          id: `msg_${Date.now()}`,
          agentId: judge.id,
          content: judgment,
          type: "judgment",
          tokens: 15,
          timestamp: Date.now(),
        };
        setMessages(prev => [...prev, msg]);
      }
      round.status = "complete";
      setCurrentRound({ ...round });
    }

    setRoundHistory(prev => [...prev, round]);
    setIsPlaying(false);
  }, [targetWord, agents, activeConstraints, selectedCategory]);

  // Helper functions
  const generateDescription = (target: string, constraints: Constraint[], actor: Agent): string => {
    const descriptions: Record<string, string[]> = {
      "BANANA": ["Yellow curve that monkeys love!", "You peel it before eating!", "A fruit shaped like a smile!"],
      "ELEPHANT": ["Big gray friend with a trunk!", "Never forgets anything!", "Largest land animal!"],
      "PENGUIN": ["Wears a tuxedo everyday!", "Waddles on ice!", "Lives where it's super cold!"],
      "DOLPHIN": ["Smart ocean friend!", "Jumps through hoops!", "Loves to play!"],
      "BUTTERFLY": ["Starts as caterpillar!", "Beautiful wings!", "Flower visitor!"],
      "PIZZA": ["Triangle of happiness!", "Cheese on bread!", "Everyone's favorite!"],
      "RAINBOW": ["Colors in the sky!", "After rain comes sunshine!", "Nature's art!"],
      "COMPUTER": ["Electric brain!", "Clicks and types!", "Does math fast!"],
      "GRAVITY": ["What goes up must come down!", "Invisible force!", "Keeps us grounded!"],
      "HAPPINESS": ["Feels like sunshine!", "Smile inside!", "Best feeling ever!"],
      "FREEDOM": ["Flying without chains!", "Your own choices!", "Liberty!"],
      "ASTRONAUT": ["Space traveler!", "Wears special suit!", "Sees Earth from above!"],
    };
    
    const baseDescs = descriptions[target.toUpperCase()] || ["Something amazing!", "Can you guess it?", "A wonderful thing!"];
    let desc = baseDescs[Math.floor(Math.random() * baseDescs.length)];
    
    if (constraints.some(c => c.type === "rhyme")) {
      const rhymes: Record<string, string> = {
        "BANANA": "Yellow fruit, a tasty nana!",
        "PIZZA": "Cheesy treat, perfect on a feetsa!",
        "RAINBOW": "Colors high, look at them glow!",
      };
      desc = rhymes[target.toUpperCase()] || desc + " - so fine!";
    }
    
    if (constraints.some(c => c.type === "emoji-only")) {
      const emojiMap: Record<string, string> = {
        "BANANA": "🍌💛🐵",
        "ELEPHANT": "🐘🐘🐘",
        "PENGUIN": "🐧❄️🧊",
        "PIZZA": "🍕🧀😋",
        "RAINBOW": "🌈⛈️☀️",
      };
      desc = emojiMap[target.toUpperCase()] || "🤔❓✨";
    }
    
    return desc;
  };

  const generateGuess = (target: string, constraints: Constraint[]): string => {
    const wrongGuesses = ["Is it a cat?", "Could it be a car?", "Maybe a house?", "A ball?", "Some food?"];
    const correctGuess = `Is it ${target}?`;
    
    // 70% chance to guess correctly
    if (Math.random() > 0.3) {
      return correctGuess;
    }
    return wrongGuesses[Math.floor(Math.random() * wrongGuesses.length)];
  };

  const generateIdiom = (actor: Agent, guesser: Agent, target: string): Idiom => {
    const emojis = ["🌊", "🔥", "⚡", "💡", "🎯", "🧠", "💎", "🌟"];
    const shorthand = `${emojis[Math.floor(Math.random() * emojis.length)]}${emojis[Math.floor(Math.random() * emojis.length)]}`;
    return {
      id: `idiom_${Date.now()}`,
      shorthand,
      meaning: `Understanding of ${target} through play`,
      originAgents: [actor.id, guesser.id],
      usageCount: 1,
      tokenSavings: 50,
      lockedToSeed: false,
      category: "game-generated"
    };
  };

  // Get role configuration
  const roleConfig = userProfile ? USER_ROLE_CONFIG[userProfile.role] : null;

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <div className="sticky top-0 z-40 bg-slate-900/95 backdrop-blur-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="flex items-center gap-2">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                  <Network className="w-5 h-5 text-white" />
                </div>
                <div className="hidden sm:block">
                  <h1 className="text-lg font-bold">LLN Playground</h1>
                  <p className="text-xs text-slate-500">Large Language Networks</p>
                </div>
              </Link>
              
              {/* Section Tabs */}
              <div className="hidden md:flex items-center gap-1 ml-6">
                {[
                  { id: "play", label: "Play", icon: Gamepad2 },
                  { id: "realtime", label: "Real-Time", icon: Zap },
                  { id: "voxel", label: "Voxel Lab", icon: Box },
                  { id: "speedrun", label: "Speed Learn", icon: Rocket },
                  { id: "synthesis", label: "Synthesis", icon: Merge },
                  { id: "mycelium", label: "Network", icon: TreeDeciduous },
                  { id: "distillation", label: "Distillation", icon: Brain },
                  { id: "learning", label: "ML Engine", icon: Cpu },
                ].map((section) => (
                  <motion.button
                    key={section.id}
                    onClick={() => setActiveSection(section.id as HubSection)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm transition-all ${
                      activeSection === section.id
                        ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                        : "text-slate-400 hover:text-white hover:bg-slate-800"
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <section.icon className="w-4 h-4" />
                    {section.label}
                  </motion.button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-4">
              {userProfile && roleConfig && (
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: roleConfig.color + '30' }}>
                    <roleConfig.icon className="w-4 h-4" style={{ color: roleConfig.color }} />
                  </div>
                  <div className="hidden sm:block">
                    <div className="text-sm font-medium">{userProfile.displayName}</div>
                    <div className="text-xs text-slate-500">Level {userProfile.level}</div>
                  </div>
                </div>
              )}
              
              {/* Mobile menu */}
              <button
                className="md:hidden p-2 text-slate-400 hover:text-white"
                onClick={() => setShowMobileMenu(!showMobileMenu)}
              >
                {showMobileMenu ? <X className="w-5 h-5" /> : <Layers className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <AnimatePresence>
        {showMobileMenu && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-slate-900 border-b border-slate-800"
          >
            <div className="p-4 grid grid-cols-2 gap-2">
              {[
                { id: "play", label: "Play", icon: Gamepad2 },
                { id: "realtime", label: "Real-Time", icon: Zap },
                { id: "voxel", label: "Voxel Lab", icon: Box },
                { id: "speedrun", label: "Speed Learn", icon: Rocket },
                { id: "synthesis", label: "Synthesis", icon: Merge },
                { id: "mycelium", label: "Network", icon: TreeDeciduous },
                { id: "distillation", label: "Distillation", icon: Brain },
                { id: "learning", label: "ML Engine", icon: Cpu },
              ].map((section) => (
                <button
                  key={section.id}
                  onClick={() => {
                    setActiveSection(section.id as HubSection);
                    setShowMobileMenu(false);
                  }}
                  className={`flex items-center gap-2 p-3 rounded-xl text-sm ${
                    activeSection === section.id
                      ? "bg-purple-500/20 text-purple-400"
                      : "bg-slate-800 text-slate-400"
                  }`}
                >
                  <section.icon className="w-4 h-4" />
                  {section.label}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <AnimatePresence mode="wait">
          {/* PLAY SECTION */}
          {activeSection === "play" && (
            <motion.div
              key="play"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Role Selector */}
              {showRoleSelector && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                  <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="bg-slate-900 rounded-3xl p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto"
                  >
                    <h2 className="text-3xl font-bold text-white text-center mb-2">Welcome to LLN Playground!</h2>
                    <p className="text-slate-400 text-center mb-8">Choose your adventure type to get started</p>
                    
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                      {(Object.entries(USER_ROLE_CONFIG) as [UserRole, typeof USER_ROLE_CONFIG[UserRole]][]).map(([role, config]) => (
                        <motion.button
                          key={role}
                          onClick={() => handleRoleSelect(role)}
                          className="p-4 rounded-2xl border-2 border-slate-700 hover:border-slate-500 bg-slate-800/50 transition-all"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <div
                            className="w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-3"
                            style={{ backgroundColor: config.color + '30' }}
                          >
                            <config.icon className="w-6 h-6" style={{ color: config.color }} />
                          </div>
                          <h3 className="text-white font-semibold text-sm text-center">{config.label}</h3>
                          <p className="text-slate-500 text-xs text-center mt-1 line-clamp-2">{config.description}</p>
                        </motion.button>
                      ))}
                    </div>
                  </motion.div>
                </div>
              )}

              {/* Game Mode Selector */}
              <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Gamepad2 className="w-5 h-5 text-purple-400" />
                  Game Mode
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {(Object.entries(GAME_MODES) as [GameMode, typeof GAME_MODES[GameMode]][]).map(([modeId, mode]) => (
                    <motion.button
                      key={modeId}
                      onClick={() => setSelectedMode(modeId)}
                      className={`p-4 rounded-xl border-2 transition-all text-left ${
                        selectedMode === modeId
                          ? 'border-purple-500 bg-purple-500/20'
                          : 'border-slate-700 hover:border-slate-500 bg-slate-800/50'
                      }`}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <mode.icon className="w-5 h-5 text-purple-400" />
                        <span className="text-white font-medium text-sm">{mode.label}</span>
                      </div>
                      <p className="text-slate-500 text-xs line-clamp-2">{mode.description}</p>
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Word Category & Constraints */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Categories */}
                <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Target className="w-5 h-5 text-amber-400" />
                    Word Category
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {WORD_CATEGORIES.map(category => (
                      <motion.button
                        key={category.id}
                        onClick={() => setSelectedCategory(category.id)}
                        className={`px-4 py-2 rounded-xl border transition-all flex items-center gap-2 ${
                          selectedCategory === category.id
                            ? 'border-purple-500 bg-purple-500/20 text-white'
                            : 'border-slate-700 hover:border-slate-500 bg-slate-800/50 text-slate-400'
                        }`}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <span className="text-lg">{category.emoji}</span>
                        <span className="text-sm">{category.name}</span>
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Constraints */}
                <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Lock className="w-5 h-5 text-rose-400" />
                    Constraints
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {constraints.filter(c => c.unlocked || userProfile?.role === 'developer').map(constraint => (
                      <motion.button
                        key={constraint.id}
                        onClick={() => toggleConstraint(constraint)}
                        className={`px-3 py-1.5 rounded-lg border transition-all flex items-center gap-2 ${
                          activeConstraints.find(c => c.id === constraint.id)
                            ? 'border-rose-500 bg-rose-500/20 text-white'
                            : 'border-slate-700 hover:border-slate-500 bg-slate-800/50 text-slate-400'
                        }`}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <span>{constraint.emoji}</span>
                        <span className="text-sm">{constraint.type}</span>
                      </motion.button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Game Area */}
              <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Game Arena</h3>
                  <motion.button
                    onClick={simulateRound}
                    disabled={isPlaying}
                    className="flex items-center gap-2 px-6 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium disabled:opacity-50"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {isPlaying ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Playing...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        Start Round
                      </>
                    )}
                  </motion.button>
                </div>

                {/* Messages */}
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {messages.length === 0 ? (
                    <div className="text-center py-12 text-slate-500">
                      <Gamepad2 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>Click "Start Round" to begin!</p>
                    </div>
                  ) : (
                    messages.map(msg => {
                      const agent = agents.find(a => a.id === msg.agentId);
                      return (
                        <motion.div
                          key={msg.id}
                          initial={{ x: -20, opacity: 0 }}
                          animate={{ x: 0, opacity: 1 }}
                          className={`p-3 rounded-xl ${
                            msg.type === 'celebration' ? 'bg-yellow-500/20 border border-yellow-500' :
                            msg.type === 'guess' ? 'bg-purple-500/10 border border-purple-500/30' :
                            'bg-slate-900/50'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-xl">{agent?.emoji || "🤖"}</span>
                            <div className="flex-1">
                              <span className="font-medium text-white">{agent?.name}: </span>
                              <span className="text-slate-300">{msg.content}</span>
                            </div>
                            <span className="text-xs text-amber-400">{msg.tokens}t</span>
                          </div>
                        </motion.div>
                      );
                    })
                  )}
                </div>
              </div>

              {/* Idioms */}
              <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-400" />
                  Idiom Library ({idioms.length})
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                  {idioms.map(idiom => (
                    <motion.div
                      key={idiom.id}
                      className={`p-3 rounded-xl border cursor-pointer transition-all ${
                        idiom.lockedToSeed ? 'border-amber-500/50 bg-amber-500/10' : 'border-slate-700 bg-slate-900/50'
                      }`}
                      whileHover={{ scale: 1.05 }}
                      onClick={() => toggleIdiomLock(idiom)}
                    >
                      <div className="text-2xl text-center mb-2">{idiom.shorthand}</div>
                      <div className="text-xs text-slate-400 text-center">{idiom.meaning}</div>
                      <div className="flex items-center justify-center gap-2 mt-2">
                        <span className="text-xs text-emerald-400">-{idiom.tokenSavings}t</span>
                        {idiom.lockedToSeed && <Lock className="w-3 h-3 text-amber-400" />}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {/* SYNTHESIS SECTION */}
          {activeSection === "synthesis" && (
            <motion.div
              key="synthesis"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <SynthesisEngine onCombinationSelect={(combo) => console.log("Selected:", combo)} />
            </motion.div>
          )}

          {/* MYCELIUM SECTION */}
          {activeSection === "mycelium" && (
            <motion.div
              key="mycelium"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <MyceliumNetwork simulation={myceliumSimulation} />
              <LifePrinciplesDisplay />
            </motion.div>
          )}

          {/* DISTILLATION SECTION */}
          {activeSection === "distillation" && (
            <motion.div
              key="distillation"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <OriginFirstDistillation
                onSeedSelect={(seed) => console.log("Selected seed:", seed)}
                onEnvironmentChange={(forces) => console.log("Environment forces:", forces)}
              />
              <BootstrapIntelligenceEngine />
              <SuperInstanceWorkflow />
            </motion.div>
          )}

          {/* ML LEARNING ENGINE SECTION */}
          {activeSection === "learning" && (
            <motion.div
              key="learning"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <KnowledgeDistillationSystem
                onJobComplete={(job) => console.log("Job completed:", job)}
              />
              <UserLearningEngineComponent
                onPatternDetected={(pattern) => console.log("Pattern detected:", pattern)}
                onSuggestionGenerated={(suggestion) => console.log("Suggestion:", suggestion)}
              />
            </motion.div>
          )}

          {/* EXPLORER SECTION */}
          {activeSection === "explorer" && (
            <motion.div
              key="explorer"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <ExplorerHub />
            </motion.div>
          )}

          {/* REAL-TIME GAME ENGINE SECTION */}
          {activeSection === "realtime" && (
            <motion.div
              key="realtime"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <RealTimeGameEngine
                ageGroup={userProfile?.role === "kid" ? "child" : userProfile?.role === "teen" ? "teen" : "adult"}
                onScoreUpdate={(score) => console.log("Score:", score)}
                onAchievement={(achievement) => console.log("Achievement:", achievement)}
                onPatternDetected={(pattern) => console.log("Pattern:", pattern)}
              />
              <GameSimulationSwitcher
                ageGroup={userProfile?.role === "kid" ? "child" : userProfile?.role === "teen" ? "teen" : "adult"}
                onComplete={(pathId, score) => console.log("Path complete:", pathId, score)}
                onProgress={(stepId, progress) => console.log("Progress:", stepId, progress)}
              />
            </motion.div>
          )}

          {/* VOXEL GAME INTEGRATOR SECTION */}
          {activeSection === "voxel" && (
            <motion.div
              key="voxel"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <VoxelGameIntegrator
                ageLevel={userProfile?.role === "kid" ? "elementary" : userProfile?.role === "teen" ? "middle" : "high"}
                onModuleSelect={(module) => console.log("Module:", module)}
                onScoreUpdate={(score) => console.log("Voxel score:", score)}
              />
            </motion.div>
          )}

          {/* SPEED LEARNING PATH SECTION */}
          {activeSection === "speedrun" && (
            <motion.div
              key="speedrun"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <SpeedLearningPath
                subject="ai-basics"
                onProgress={(progress) => console.log("Learning progress:", progress)}
                onConceptMastered={(conceptId) => console.log("Mastered:", conceptId)}
                onChallengeComplete={(id, correct) => console.log("Challenge:", id, correct)}
              />
              <MLUserActionTracker
                onPatternDetected={(pattern) => console.log("ML Pattern:", pattern)}
                onInsightGenerated={(insight) => console.log("Insight:", insight)}
                enableRealTimeTracking={true}
              />
            </motion.div>
          )}

          {/* ROUNDS SECTION */}
          {activeSection === "rounds" && (
            <motion.div
              key="rounds"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <ExtendedSynthesisRounds
                onRoundSelect={(round) => console.log("Selected round:", round)}
                completedRounds={[]}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Footer Stats */}
      <div className="border-t border-slate-800 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="grid grid-cols-4 md:grid-cols-8 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-400">24</div>
              <div className="text-xs text-slate-500">Synthesis Rounds</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-400">15</div>
              <div className="text-xs text-slate-500">Teaching Methods</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-cyan-400">24</div>
              <div className="text-xs text-slate-500">Combination Tiles</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-emerald-400">14+</div>
              <div className="text-xs text-slate-500">Cultures</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-rose-400">8</div>
              <div className="text-xs text-slate-500">Debate Formats</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-violet-400">5</div>
              <div className="text-xs text-slate-500">Seed Types</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-400">127K+</div>
              <div className="text-xs text-slate-500">ML Examples</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-pink-400">∞</div>
              <div className="text-xs text-slate-500">Possibilities</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
