"use client";

import { useState, useMemo, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import {
  Search,
  Filter,
  SortAsc,
  SortDesc,
  Grid,
  GraduationCap,
  Users,
  Gamepad2,
  Microscope,
  Wrench,
  Code2,
  List,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Star,
  StarOff,
  Heart,
  Bookmark,
  BookmarkCheck,
  Eye,
  EyeOff,
  Clock,
  Calendar,
  Tag,
  Tags,
  Folder,
  FolderOpen,
  File,
  FileText,
  FileCode,
  FileJson,
  FileSpreadsheet,
  Image,
  Video,
  Music,
  Archive,
  Package,
  Box,
  Layers,
  Layout,
  LayoutGrid,
  LayoutList,
  Columns,
  Rows,
  Table,
  Table2,
  Hash,
  AtSign,
  Link as LinkIcon,
  ExternalLink,
  Download,
  Upload,
  Share,
  Share2,
  Copy,
  Clipboard,
  Printer,
  Mail,
  MessageCircle,
  MessageSquare,
  Send,
  Globe,
  Map,
  MapPin,
  Compass,
  Navigation,
  Route,
  Waypoints,
  Anchor,
  Ship,
  Plane,
  Rocket,
  Satellite,
  Radar,
  Radio,
  Wifi,
  Signal,
  Zap,
  Battery,
  BatteryCharging,
  Power,
  Gauge,
  Dashboard,
  PanelTop,
  Activity,
  TrendingUp,
  TrendingDown,
  BarChart3,
  LineChart,
  PieChart,
  ScatterChart,
  AreaChart,
  RadarChart,
  Target,
  Crosshair,
  Focus,
  Scan,
  Cross,
  Plus,
  Minus,
  X,
  Check,
  CheckCircle,
  XCircle,
  HelpCircle,
  Info,
  AlertCircle,
  AlertTriangle,
  Shield,
  ShieldCheck,
  ShieldAlert,
  Lock,
  Unlock,
  Key,
  KeyRound,
  Fingerprint,
  IdCard,
  Badge,
  BadgeCheck,
  BadgeAlert,
  Award,
  Trophy,
  Medal,
  Crown,
  Gem,
  Sparkles,
  Flame,
  Snowflake,
  Sun,
  Moon,
  Cloud,
  CloudRain,
  CloudSnow,
  CloudLightning,
  Wind,
  Droplet,
  Droplets,
  Thermometer,
  Umbrella,
  Rainbow,
  Sunrise,
  Sunset,
  Horizon,
  Sky,
  Mountain,
  MountainSnow,
  TreePine,
  TreeDeciduous,
  Tree,
  Trees,
  Leaf,
  LeafyGreen,
  Flower,
  Flower2,
  Dna,
  Atom,
  Diamond,
  Hexagon,
  Triangle,
  Square,
  Circle,
  CircleDot,
  Octagon,
  Pentagon,
  Heptagon,
  Infinity,
  Brain,
  Cpu,
  Microchip,
  HardDrive,
  Database,
  Server,
  CloudServer,
  Network,
  GitBranch,
  GitMerge,
  GitCommit,
  GitPullRequest,
  Merge,
  Split,
  Bot,
  BotMessageSquare,
  BotOff,
  Cog,
  Cogs,
  Settings,
  Settings2,
  SettingsGear,
  Slider,
  Sliders,
  ToggleLeft,
  ToggleRight,
  SwitchCamera,
  Hammer,
  Screwdriver,
  Nut,
  Bolt,
  Construction,
  HammerIcon,
  Paintbrush,
  Paintbrush2,
  Palette,
  Pencil,
  Pen,
  PenTool,
  PencilRuler,
  Ruler,
  Scissors,
  Eraser,
  Move,
  Move3d,
  MoveHorizontal,
  MoveVertical,
  ZoomIn,
  ZoomOut,
  Maximize,
  Minimize,
  Expand,
  Shrink,
  RotateCcw,
  RotateCw,
  FlipHorizontal,
  FlipVertical,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  AlignStartVertical,
  AlignCenterVertical,
  AlignEndVertical,
  AlignStartHorizontal,
  AlignCenterHorizontal,
  AlignEndHorizontal,
  Space,
  Spacing,
  Indent,
  Outdent,
  TextCursor,
  Type,
  FontSize,
  FontBold,
  FontItalic,
  FontUnderline,
  FontStrikethrough,
  FontFamily,
  LetterText,
  CaseSensitive,
  CaseLower,
  CaseUpper,
  CaseCapital,
  Quote,
  Superscript,
  Subscript,
  ListOrdered,
  ListUnordered,
  ListChecks,
  ListTodo,
  ListPlus,
  ListMinus,
  ListX,
  TreeStructure,
  TreeDeciduousIcon,
  TreePineIcon,
  Branch,
  GitFork,
  Combine,
  Group,
  Ungroup,
  LayersIcon,
  Stack,
  Stack2,
  Boxes,
  BoxIcon,
  Container,
  ContainerIcon,
  PackageIcon,
  Package2,
  ArchiveIcon,
  ArchiveRestore,
  FileArchive,
  FileBox,
  FolderArchive,
  FolderSync,
  FolderSyncIcon,
  FolderCog,
  FolderSearch,
  FolderLock,
  FolderKey,
  FolderHeart,
  FolderStar,
  FolderX,
  FolderPlus,
  FolderMinus,
  FolderCheck,
  FolderEdit,
  FolderInput,
  FolderOutput,
  FolderUp,
  FolderDown,
  FolderOpenIcon,
  FolderClosed,
  Folders,
  Directory,
  DirectoryOpen,
  DirectoryClosed,
  Book,
  BookOpen,
  BookOpenCheck,
  BookOpenText,
  BookOpenIcon,
  BookMarked,
  BookCopy,
  BookKey,
  BookLock,
  BookHeart,
  BookMinus,
  BookPlus,
  BookTemplate,
  BookType,
  BookUser,
  BookX,
  Notebook,
  NotebookPen,
  NotebookTabs,
  NotebookText,
  NotepadText,
  NotepadTextDashed,
  StickyNote,
  Note,
  ClipboardList,
  ClipboardCheck,
  ClipboardEdit,
  ClipboardPaste,
  ClipboardSignature,
  ClipboardType,
  ClipboardX,
  ClipboardIcon,
  ListChecksIcon,
  ListChecksFilled,
  CheckSquare,
  CheckSquare2,
  SquareCheck,
  SquareCheckIcon,
  SquareX,
  SquareMinus,
  SquarePlus,
  SquareIcon,
  CircleCheck,
  CircleX,
  CircleMinus,
  CirclePlus,
  CircleIcon,
  CircleDotIcon,
  CircleSlash,
  CircleSlash2,
  CircleAlert,
  CircleHelp,
  CircleArrowLeft,
  CircleArrowRight,
  CircleArrowUp,
  CircleArrowDown,
  ArrowLeftCircle,
  ArrowRightCircle,
  ArrowUpCircle,
  ArrowDownCircle,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  ArrowDown,
  ArrowUpLeft,
  ArrowUpRight,
  ArrowDownLeft,
  ArrowDownRight,
  MoveUpLeft,
  MoveUpRight,
  MoveDownLeft,
  MoveDownRight,
  CornerUpLeft,
  CornerUpRight,
  CornerDownLeft,
  CornerDownRight,
} from "lucide-react";

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

type ContentCategory = 
  | "documentation" 
  | "simulation" 
  | "teaching" 
  | "synthesis" 
  | "debate" 
  | "research" 
  | "tool"
  | "game"
  | "api"
  | "component";

type ContentDifficulty = "beginner" | "intermediate" | "advanced" | "expert";

type LearningPath = 
  | "explorer"     // New to AI/ML
  | "developer"    // Building with AI
  | "researcher"   // Deep research
  | "educator";    // Teaching others

interface ContentItem {
  id: string;
  title: string;
  description: string;
  category: ContentCategory;
  difficulty: ContentDifficulty;
  tags: string[];
  path: string;
  icon: React.ElementType;
  estimatedTime: number; // minutes
  prerequisites: string[];
  outcomes: string[];
  relatedContent: string[];
  featured: boolean;
  new: boolean;
  popular: boolean;
  completionRate: number;
  rating: number;
  reviews: number;
}

interface ExplorerFilter {
  categories: ContentCategory[];
  difficulties: ContentDifficulty[];
  paths: LearningPath[];
  search: string;
  tags: string[];
  sortBy: "relevance" | "title" | "difficulty" | "rating" | "popular";
  sortOrder: "asc" | "desc";
}

interface ExplorerStats {
  totalContent: number;
  categoriesCount: Record<ContentCategory, number>;
  averageRating: number;
  totalReviews: number;
  featuredCount: number;
  newCount: number;
}

// ============================================================================
// CONTENT LIBRARY
// ============================================================================

const CONTENT_LIBRARY: ContentItem[] = [
  // DOCUMENTATION
  {
    id: "doc-overview",
    title: "LLN Playground Overview",
    description: "Complete introduction to Large Language Networks - how agents learn through constrained gameplay to create idioms and SMPbots.",
    category: "documentation",
    difficulty: "beginner",
    tags: ["introduction", "getting-started", "concepts"],
    path: "/lln-playground",
    icon: BookOpen,
    estimatedTime: 15,
    prerequisites: [],
    outcomes: ["Understand LLN concepts", "Navigate the playground", "Start your first game"],
    relatedContent: ["doc-constraints", "doc-agents"],
    featured: true,
    new: false,
    popular: true,
    completionRate: 0.89,
    rating: 4.8,
    reviews: 234
  },
  {
    id: "doc-constraints",
    title: "Constraint System Deep Dive",
    description: "Learn how constraints shape communication and creativity. From rhyme challenges to negative-space descriptions.",
    category: "documentation",
    difficulty: "intermediate",
    tags: ["constraints", "creativity", "communication"],
    path: "/lln-playground#constraints",
    icon: Lock,
    estimatedTime: 25,
    prerequisites: ["doc-overview"],
    outcomes: ["Design custom constraints", "Understand constraint interactions", "Measure constraint impact"],
    relatedContent: ["doc-idioms", "sim-constraint-lab"],
    featured: false,
    new: false,
    popular: true,
    completionRate: 0.76,
    rating: 4.6,
    reviews: 189
  },
  {
    id: "doc-agents",
    title: "Agent Architecture Guide",
    description: "How AI agents are designed, trained, and deployed in the LLN ecosystem. From Riddler to Oracle to Sage.",
    category: "documentation",
    difficulty: "intermediate",
    tags: ["agents", "AI", "architecture"],
    path: "/lln-playground#agents",
    icon: Bot,
    estimatedTime: 30,
    prerequisites: ["doc-overview"],
    outcomes: ["Design agent personalities", "Configure agent roles", "Optimize agent performance"],
    relatedContent: ["doc-idioms", "sim-agent-training"],
    featured: false,
    new: true,
    popular: false,
    completionRate: 0.68,
    rating: 4.7,
    reviews: 156
  },
  {
    id: "doc-idioms",
    title: "Idiom Creation & Management",
    description: "Master the art of creating compressed communication patterns. From emoji sequences to cultural adaptations.",
    category: "documentation",
    difficulty: "advanced",
    tags: ["idioms", "compression", "communication"],
    path: "/lln-playground#idioms",
    icon: MessageSquare,
    estimatedTime: 35,
    prerequisites: ["doc-constraints", "doc-agents"],
    outcomes: ["Create effective idioms", "Lock idioms to seeds", "Measure idiom efficiency"],
    relatedContent: ["doc-smpbots", "sim-idiom-lab"],
    featured: true,
    new: false,
    popular: true,
    completionRate: 0.62,
    rating: 4.9,
    reviews: 312
  },
  {
    id: "doc-smpbots",
    title: "SMPbot Development Guide",
    description: "Build Single Mastery Point bots with deterministic seeds. The foundation of LLN intelligence.",
    category: "documentation",
    difficulty: "expert",
    tags: ["smpbots", "deterministic", "seeds"],
    path: "/lln-playground#smpbots",
    icon: Cpu,
    estimatedTime: 45,
    prerequisites: ["doc-idioms"],
    outcomes: ["Design SMPbot architectures", "Create deterministic seeds", "Deploy SMPbots at scale"],
    relatedContent: ["doc-distillation", "sim-smpbot-builder"],
    featured: false,
    new: true,
    popular: false,
    completionRate: 0.45,
    rating: 4.8,
    reviews: 98
  },

  // SIMULATIONS
  {
    id: "sim-socratic",
    title: "Socratic Classroom Simulation",
    description: "Experience 25 rounds of Socratic teaching simulations. Watch agents learn through questioning.",
    category: "simulation",
    difficulty: "intermediate",
    tags: ["socratic", "teaching", "simulation"],
    path: "/lln-playground?socratic",
    icon: GraduationCap,
    estimatedTime: 60,
    prerequisites: ["doc-overview"],
    outcomes: ["Run Socratic simulations", "Analyze question patterns", "Generate training data"],
    relatedContent: ["sim-multi-method", "doc-agents"],
    featured: true,
    new: false,
    popular: true,
    completionRate: 0.72,
    rating: 4.7,
    reviews: 178
  },
  {
    id: "sim-multi-method",
    title: "Multi-Method Teaching Lab",
    description: "50 rounds of multi-method teaching simulations. Compare Socratic, Project-Based, Inquiry-Based approaches.",
    category: "simulation",
    difficulty: "advanced",
    tags: ["multi-method", "teaching", "comparison"],
    path: "/lln-playground?multi-method",
    icon: Layers,
    estimatedTime: 90,
    prerequisites: ["sim-socratic"],
    outcomes: ["Compare teaching methods", "Synthesize approaches", "Optimize learning outcomes"],
    relatedContent: ["sim-synthesis", "doc-constraints"],
    featured: false,
    new: false,
    popular: true,
    completionRate: 0.58,
    rating: 4.6,
    reviews: 134
  },
  {
    id: "sim-debate",
    title: "Debate Simulation Arena",
    description: "25 rounds of structured debates. Oxford, Parliamentary, Socratic, and more formats.",
    category: "simulation",
    difficulty: "advanced",
    tags: ["debate", "argumentation", "reasoning"],
    path: "/lln-playground?debate",
    icon: MessageCircle,
    estimatedTime: 75,
    prerequisites: ["doc-overview"],
    outcomes: ["Run debate simulations", "Score arguments", "Analyze persuasion patterns"],
    relatedContent: ["sim-synthesis", "doc-agents"],
    featured: true,
    new: false,
    popular: false,
    completionRate: 0.65,
    rating: 4.5,
    reviews: 112
  },
  {
    id: "sim-synthesis",
    title: "Creative Synthesis Engine",
    description: "12 rounds of method synthesis. Discover new teaching tools by combining approaches.",
    category: "synthesis",
    difficulty: "expert",
    tags: ["synthesis", "creativity", "methods"],
    path: "/lln-playground?synthesis",
    icon: Sparkles,
    estimatedTime: 45,
    prerequisites: ["sim-multi-method"],
    outcomes: ["Create method combinations", "Discover synergy patterns", "Generate combination tiles"],
    relatedContent: ["sim-socratic", "doc-distillation"],
    featured: true,
    new: true,
    popular: true,
    completionRate: 0.52,
    rating: 4.9,
    reviews: 89
  },
  {
    id: "sim-mycelium",
    title: "Mycelium Network Simulation",
    description: "Visualize cooperative intelligence networks. Pest warnings, resource sharing, competition dynamics.",
    category: "simulation",
    difficulty: "intermediate",
    tags: ["mycelium", "cooperation", "networks"],
    path: "/lln-playground?mycelium",
    icon: TreeDeciduous,
    estimatedTime: 40,
    prerequisites: ["doc-overview"],
    outcomes: ["Simulate agent networks", "Analyze cooperation patterns", "Design warning systems"],
    relatedContent: ["doc-agents", "sim-smpbot-builder"],
    featured: false,
    new: true,
    popular: false,
    completionRate: 0.71,
    rating: 4.4,
    reviews: 67
  },

  // RESEARCH
  {
    id: "research-origin-first",
    title: "Origin-First Distillation Research",
    description: "Deep dive into tree seed metaphor for AI knowledge systems. Compressed wisdom, geometric encoding.",
    category: "research",
    difficulty: "expert",
    tags: ["research", "distillation", "origin-first"],
    path: "/lln-playground?origin-first",
    icon: TreeDeciduous,
    estimatedTime: 60,
    prerequisites: ["doc-smpbots"],
    outcomes: ["Understand seed metaphor", "Design distillation pipelines", "Compress knowledge"],
    relatedContent: ["doc-distillation", "sim-smpbot-builder"],
    featured: true,
    new: true,
    popular: false,
    completionRate: 0.38,
    rating: 4.8,
    reviews: 45
  },
  {
    id: "research-cultural",
    title: "Cultural Adaptation Framework",
    description: "How LLN adapts across 14+ cultures and 12+ languages. Cultural bridges and pattern recognition.",
    category: "research",
    difficulty: "advanced",
    tags: ["cultural", "adaptation", "globalization"],
    path: "/lln-playground?cultural",
    icon: Globe,
    estimatedTime: 50,
    prerequisites: ["doc-idioms"],
    outcomes: ["Design cultural adaptations", "Bridge cultural patterns", "Measure cultural fit"],
    relatedContent: ["doc-constraints", "sim-synthesis"],
    featured: false,
    new: false,
    popular: true,
    completionRate: 0.55,
    rating: 4.6,
    reviews: 123
  },
  {
    id: "research-age-adaptive",
    title: "Age-Adaptive Learning Systems",
    description: "Universal patterns that work from age 5 to 95. Lifespan learning companions.",
    category: "research",
    difficulty: "advanced",
    tags: ["age-adaptive", "lifespan", "universal"],
    path: "/lln-playground?age-adaptive",
    icon: Users,
    estimatedTime: 45,
    prerequisites: ["doc-overview"],
    outcomes: ["Design age-adaptive content", "Create lifespan companions", "Measure age fit"],
    relatedContent: ["research-cultural", "sim-synthesis"],
    featured: false,
    new: false,
    popular: false,
    completionRate: 0.61,
    rating: 4.5,
    reviews: 87
  },

  // TOOLS
  {
    id: "tool-tile-editor",
    title: "Tile Intelligence Editor",
    description: "Visual tile-based programming for LLN. Create, edit, and combine knowledge tiles.",
    category: "tool",
    difficulty: "intermediate",
    tags: ["tiles", "visual", "programming"],
    path: "/lln-tiles",
    icon: Box,
    estimatedTime: 30,
    prerequisites: ["doc-overview"],
    outcomes: ["Create knowledge tiles", "Combine tiles", "Export tile sets"],
    relatedContent: ["tool-synthesis-engine", "doc-idioms"],
    featured: true,
    new: false,
    popular: true,
    completionRate: 0.74,
    rating: 4.7,
    reviews: 203
  },
  {
    id: "tool-synthesis-engine",
    title: "Synthesis Engine Studio",
    description: "Mix and match teaching methods to discover new educational tools. Real-time synergy calculation.",
    category: "tool",
    difficulty: "advanced",
    tags: ["synthesis", "methods", "discovery"],
    path: "/lln-playground?synthesis-engine",
    icon: Merge,
    estimatedTime: 40,
    prerequisites: ["doc-overview"],
    outcomes: ["Combine methods", "Calculate synergy scores", "Generate combination tiles"],
    relatedContent: ["tool-tile-editor", "sim-synthesis"],
    featured: false,
    new: true,
    popular: false,
    completionRate: 0.58,
    rating: 4.6,
    reviews: 78
  },
  {
    id: "tool-distillation",
    title: "Knowledge Distillation Lab",
    description: "ML training data generation and compression. Origin-first distillation pipelines.",
    category: "tool",
    difficulty: "expert",
    tags: ["distillation", "ML", "compression"],
    path: "/lln-playground?distillation",
    icon: Brain,
    estimatedTime: 55,
    prerequisites: ["doc-smpbots"],
    outcomes: ["Create distillation jobs", "Generate training data", "Compress knowledge"],
    relatedContent: ["research-origin-first", "doc-distillation"],
    featured: true,
    new: true,
    popular: false,
    completionRate: 0.42,
    rating: 4.8,
    reviews: 56
  },

  // GAMES
  {
    id: "game-charades",
    title: "AI Charades Arena",
    description: "Classic guessing game with AI agents. Describe without saying the word, under constraints.",
    category: "game",
    difficulty: "beginner",
    tags: ["charades", "game", "fun"],
    path: "/lln-playground?game=charades",
    icon: Gamepad2,
    estimatedTime: 15,
    prerequisites: [],
    outcomes: ["Learn LLN basics", "Create first idioms", "Have fun!"],
    relatedContent: ["game-word-chain", "doc-overview"],
    featured: true,
    new: false,
    popular: true,
    completionRate: 0.92,
    rating: 4.9,
    reviews: 456
  },
  {
    id: "game-debate",
    title: "AI Debate Tournament",
    description: "Structured debates with AI judges. Win arguments, score points, climb leaderboards.",
    category: "game",
    difficulty: "intermediate",
    tags: ["debate", "competition", "leaderboard"],
    path: "/lln-playground?game=debate",
    icon: Trophy,
    estimatedTime: 25,
    prerequisites: ["game-charades"],
    outcomes: ["Master debate formats", "Score high in tournaments", "Earn achievements"],
    relatedContent: ["sim-debate", "game-charades"],
    featured: false,
    new: false,
    popular: true,
    completionRate: 0.78,
    rating: 4.6,
    reviews: 289
  },

  // API
  {
    id: "api-overview",
    title: "LLN API Documentation",
    description: "Complete API reference for integrating LLN into your applications. REST and WebSocket endpoints.",
    category: "api",
    difficulty: "advanced",
    tags: ["api", "integration", "developers"],
    path: "/lln-playground?api",
    icon: Code2,
    estimatedTime: 45,
    prerequisites: ["doc-overview"],
    outcomes: ["Integrate LLN APIs", "Build custom agents", "Deploy at scale"],
    relatedContent: ["tool-tile-editor", "doc-smpbots"],
    featured: false,
    new: false,
    popular: false,
    completionRate: 0.54,
    rating: 4.5,
    reviews: 67
  }
];

// ============================================================================
// EXPLORER HUB COMPONENT
// ============================================================================

export function ExplorerHub() {
  const [filter, setFilter] = useState<ExplorerFilter>({
    categories: [],
    difficulties: [],
    paths: [],
    search: "",
    tags: [],
    sortBy: "relevance",
    sortOrder: "desc"
  });
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [selectedItem, setSelectedItem] = useState<ContentItem | null>(null);
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const [bookmarks, setBookmarks] = useState<Set<string>>(new Set());

  // Calculate stats
  const stats: ExplorerStats = useMemo(() => {
    const categoriesCount: Record<ContentCategory, number> = {
      documentation: 0, simulation: 0, teaching: 0, synthesis: 0,
      debate: 0, research: 0, tool: 0, game: 0, api: 0, component: 0
    };
    
    CONTENT_LIBRARY.forEach(item => {
      categoriesCount[item.category]++;
    });

    return {
      totalContent: CONTENT_LIBRARY.length,
      categoriesCount,
      averageRating: CONTENT_LIBRARY.reduce((sum, item) => sum + item.rating, 0) / CONTENT_LIBRARY.length,
      totalReviews: CONTENT_LIBRARY.reduce((sum, item) => sum + item.reviews, 0),
      featuredCount: CONTENT_LIBRARY.filter(item => item.featured).length,
      newCount: CONTENT_LIBRARY.filter(item => item.new).length
    };
  }, []);

  // Filter and sort content
  const filteredContent = useMemo(() => {
    let results = [...CONTENT_LIBRARY];

    // Category filter
    if (filter.categories.length > 0) {
      results = results.filter(item => filter.categories.includes(item.category));
    }

    // Difficulty filter
    if (filter.difficulties.length > 0) {
      results = results.filter(item => filter.difficulties.includes(item.difficulty));
    }

    // Search filter
    if (filter.search) {
      const searchLower = filter.search.toLowerCase();
      results = results.filter(item =>
        item.title.toLowerCase().includes(searchLower) ||
        item.description.toLowerCase().includes(searchLower) ||
        item.tags.some(tag => tag.toLowerCase().includes(searchLower))
      );
    }

    // Tags filter
    if (filter.tags.length > 0) {
      results = results.filter(item =>
        filter.tags.some(tag => item.tags.includes(tag))
      );
    }

    // Sort
    results.sort((a, b) => {
      switch (filter.sortBy) {
        case "title":
          return a.title.localeCompare(b.title);
        case "difficulty":
          const diffOrder = { beginner: 1, intermediate: 2, advanced: 3, expert: 4 };
          return diffOrder[a.difficulty] - diffOrder[b.difficulty];
        case "rating":
          return b.rating - a.rating;
        case "popular":
          return b.reviews - a.reviews;
        default: // relevance
          const aScore = (a.featured ? 10 : 0) + (a.popular ? 5 : 0) + (a.new ? 3 : 0);
          const bScore = (b.featured ? 10 : 0) + (b.popular ? 5 : 0) + (b.new ? 3 : 0);
          return bScore - aScore;
      }
    });

    if (filter.sortOrder === "asc") {
      results.reverse();
    }

    return results;
  }, [filter]);

  // Get all unique tags
  const allTags = useMemo(() => {
    const tags = new Set<string>();
    CONTENT_LIBRARY.forEach(item => item.tags.forEach(tag => tags.add(tag)));
    return Array.from(tags).sort();
  }, []);

  // Toggle handlers
  const toggleFavorite = useCallback((id: string) => {
    setFavorites(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const toggleBookmark = useCallback((id: string) => {
    setBookmarks(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  const toggleCategory = useCallback((category: ContentCategory) => {
    setFilter(prev => ({
      ...prev,
      categories: prev.categories.includes(category)
        ? prev.categories.filter(c => c !== category)
        : [...prev.categories, category]
    }));
  }, []);

  const toggleDifficulty = useCallback((difficulty: ContentDifficulty) => {
    setFilter(prev => ({
      ...prev,
      difficulties: prev.difficulties.includes(difficulty)
        ? prev.difficulties.filter(d => d !== difficulty)
        : [...prev.difficulties, difficulty]
    }));
  }, []);

  const toggleTag = useCallback((tag: string) => {
    setFilter(prev => ({
      ...prev,
      tags: prev.tags.includes(tag)
        ? prev.tags.filter(t => t !== tag)
        : [...prev.tags, tag]
    }));
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-emerald-900/30 via-cyan-900/20 to-purple-900/30 rounded-2xl p-6 border border-emerald-500/30">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500/30 to-cyan-500/30 flex items-center justify-center">
              <Compass className="w-8 h-8 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Explorer Hub</h2>
              <p className="text-emerald-300">Discover Everything in the LLN Ecosystem</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-white">{stats.totalContent}</div>
            <div className="text-xs text-slate-500">Resources Available</div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
          {[
            { label: "Featured", value: stats.featuredCount, icon: Star, color: "amber" },
            { label: "New", value: stats.newCount, icon: Sparkles, color: "emerald" },
            { label: "Docs", value: stats.categoriesCount.documentation, icon: BookOpen, color: "blue" },
            { label: "Simulations", value: stats.categoriesCount.simulation + stats.categoriesCount.synthesis, icon: FlaskConical, color: "purple" },
            { label: "Tools", value: stats.categoriesCount.tool, icon: Wrench, color: "cyan" },
            { label: "Games", value: stats.categoriesCount.game, icon: Trophy, color: "rose" },
            { label: "Research", value: stats.categoriesCount.research, icon: Microscope, color: "orange" },
            { label: "API", value: stats.categoriesCount.api, icon: Code2, color: "violet" }
          ].map((stat, idx) => (
            <motion.div
              key={stat.label}
              className="p-3 bg-slate-900/50 rounded-xl border border-slate-700 text-center cursor-pointer hover:border-slate-600 transition-colors"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              onClick={() => {
                if (stat.label === "Featured" || stat.label === "New") return;
                const categoryMap: Record<string, ContentCategory> = {
                  "Docs": "documentation",
                  "Simulations": "simulation",
                  "Tools": "tool",
                  "Games": "game",
                  "Research": "research",
                  "API": "api"
                };
                toggleCategory(categoryMap[stat.label]);
              }}
            >
              <stat.icon className={`w-4 h-4 mx-auto mb-1 text-${stat.color}-400`} />
              <div className="text-lg font-bold text-white">{stat.value}</div>
              <div className="text-xs text-slate-500">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Search & Filters */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
        {/* Search Bar */}
        <div className="flex items-center gap-4 mb-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input
              type="text"
              value={filter.search}
              onChange={(e) => setFilter(prev => ({ ...prev, search: e.target.value }))}
              placeholder="Search documentation, simulations, tools..."
              className="w-full pl-12 pr-4 py-3 rounded-xl bg-slate-900/50 border border-slate-600 text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <div className="flex items-center gap-2">
            <motion.button
              onClick={() => setViewMode("grid")}
              className={`p-2 rounded-lg ${viewMode === "grid" ? "bg-emerald-500/20 text-emerald-400" : "text-slate-500"}`}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <Grid className="w-5 h-5" />
            </motion.button>
            <motion.button
              onClick={() => setViewMode("list")}
              className={`p-2 rounded-lg ${viewMode === "list" ? "bg-emerald-500/20 text-emerald-400" : "text-slate-500"}`}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
            >
              <List className="w-5 h-5" />
            </motion.button>
          </div>
        </div>

        {/* Filter Categories */}
        <div className="flex flex-wrap gap-2 mb-4">
          {(["documentation", "simulation", "synthesis", "research", "tool", "game", "api"] as ContentCategory[]).map((category) => (
            <motion.button
              key={category}
              onClick={() => toggleCategory(category)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-all ${
                filter.categories.includes(category)
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "bg-slate-900/50 text-slate-400 border border-slate-600 hover:border-slate-500"
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {category}
            </motion.button>
          ))}
        </div>

        {/* Filter Difficulties */}
        <div className="flex flex-wrap gap-2 mb-4">
          {(["beginner", "intermediate", "advanced", "expert"] as ContentDifficulty[]).map((difficulty) => (
            <motion.button
              key={difficulty}
              onClick={() => toggleDifficulty(difficulty)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-all ${
                filter.difficulties.includes(difficulty)
                  ? difficulty === "beginner" ? "bg-green-500/20 text-green-400 border border-green-500/30" :
                    difficulty === "intermediate" ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30" :
                    difficulty === "advanced" ? "bg-orange-500/20 text-orange-400 border border-orange-500/30" :
                    "bg-red-500/20 text-red-400 border border-red-500/30"
                  : "bg-slate-900/50 text-slate-400 border border-slate-600 hover:border-slate-500"
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {difficulty}
            </motion.button>
          ))}
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-2">
          {allTags.slice(0, 15).map((tag) => (
            <motion.button
              key={tag}
              onClick={() => toggleTag(tag)}
              className={`px-2 py-1 rounded text-xs transition-all ${
                filter.tags.includes(tag)
                  ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                  : "bg-slate-900/50 text-slate-500 border border-slate-700 hover:border-slate-600"
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              #{tag}
            </motion.button>
          ))}
        </div>

        {/* Results Count */}
        <div className="mt-4 text-sm text-slate-500">
          Showing {filteredContent.length} of {CONTENT_LIBRARY.length} resources
        </div>
      </div>

      {/* Content Grid/List */}
      {viewMode === "grid" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredContent.map((item, idx) => (
            <motion.div
              key={item.id}
              className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700 hover:border-slate-600 transition-all cursor-pointer"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.03 }}
              whileHover={{ scale: 1.02, y: -4 }}
              onClick={() => setSelectedItem(item)}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    item.category === "documentation" ? "bg-blue-500/20" :
                    item.category === "simulation" || item.category === "synthesis" ? "bg-purple-500/20" :
                    item.category === "tool" ? "bg-cyan-500/20" :
                    item.category === "game" ? "bg-rose-500/20" :
                    item.category === "research" ? "bg-orange-500/20" :
                    "bg-violet-500/20"
                  }`}>
                    <item.icon className={`w-5 h-5 ${
                      item.category === "documentation" ? "text-blue-400" :
                      item.category === "simulation" || item.category === "synthesis" ? "text-purple-400" :
                      item.category === "tool" ? "text-cyan-400" :
                      item.category === "game" ? "text-rose-400" :
                      item.category === "research" ? "text-orange-400" :
                      "text-violet-400"
                    }`} />
                  </div>
                  <div>
                    <h4 className="text-white font-medium">{item.title}</h4>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-1.5 py-0.5 rounded ${
                        item.difficulty === "beginner" ? "bg-green-500/20 text-green-400" :
                        item.difficulty === "intermediate" ? "bg-yellow-500/20 text-yellow-400" :
                        item.difficulty === "advanced" ? "bg-orange-500/20 text-orange-400" :
                        "bg-red-500/20 text-red-400"
                      }`}>
                        {item.difficulty}
                      </span>
                      <span className="text-xs text-slate-500">{item.estimatedTime} min</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-1">
                  {item.featured && <Star className="w-4 h-4 text-amber-400 fill-amber-400" />}
                  {item.new && <Sparkles className="w-4 h-4 text-emerald-400" />}
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-slate-400 mb-3 line-clamp-2">{item.description}</p>

              {/* Tags */}
              <div className="flex flex-wrap gap-1 mb-3">
                {item.tags.slice(0, 3).map((tag) => (
                  <span key={tag} className="text-xs px-1.5 py-0.5 rounded bg-slate-700 text-slate-400">
                    #{tag}
                  </span>
                ))}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                  <span className="text-sm text-white">{item.rating}</span>
                  <span className="text-xs text-slate-500">({item.reviews})</span>
                </div>
                <div className="flex items-center gap-2">
                  <motion.button
                    onClick={(e) => { e.stopPropagation(); toggleFavorite(item.id); }}
                    className={`p-1.5 rounded-lg ${favorites.has(item.id) ? "text-rose-400" : "text-slate-500"}`}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <Heart className={`w-4 h-4 ${favorites.has(item.id) ? "fill-rose-400" : ""}`} />
                  </motion.button>
                  <motion.button
                    onClick={(e) => { e.stopPropagation(); toggleBookmark(item.id); }}
                    className={`p-1.5 rounded-lg ${bookmarks.has(item.id) ? "text-cyan-400" : "text-slate-500"}`}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <Bookmark className={`w-4 h-4 ${bookmarks.has(item.id) ? "fill-cyan-400" : ""}`} />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredContent.map((item, idx) => (
            <motion.div
              key={item.id}
              className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 hover:border-slate-600 transition-all cursor-pointer flex items-center gap-4"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.02 }}
              whileHover={{ scale: 1.01 }}
              onClick={() => setSelectedItem(item)}
            >
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                item.category === "documentation" ? "bg-blue-500/20" :
                item.category === "simulation" || item.category === "synthesis" ? "bg-purple-500/20" :
                item.category === "tool" ? "bg-cyan-500/20" :
                item.category === "game" ? "bg-rose-500/20" :
                item.category === "research" ? "bg-orange-500/20" :
                "bg-violet-500/20"
              }`}>
                <item.icon className={`w-6 h-6 ${
                  item.category === "documentation" ? "text-blue-400" :
                  item.category === "simulation" || item.category === "synthesis" ? "text-purple-400" :
                  item.category === "tool" ? "text-cyan-400" :
                  item.category === "game" ? "text-rose-400" :
                  item.category === "research" ? "text-orange-400" :
                  "text-violet-400"
                }`} />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="text-white font-medium">{item.title}</h4>
                  {item.featured && <Star className="w-4 h-4 text-amber-400 fill-amber-400" />}
                  {item.new && <Sparkles className="w-4 h-4 text-emerald-400" />}
                </div>
                <p className="text-sm text-slate-400 line-clamp-1">{item.description}</p>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-1 mb-1">
                  <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                  <span className="text-sm text-white">{item.rating}</span>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded ${
                  item.difficulty === "beginner" ? "bg-green-500/20 text-green-400" :
                  item.difficulty === "intermediate" ? "bg-yellow-500/20 text-yellow-400" :
                  item.difficulty === "advanced" ? "bg-orange-500/20 text-orange-400" :
                  "bg-red-500/20 text-red-400"
                }`}>
                  {item.difficulty}
                </span>
              </div>
              <ChevronRight className="w-5 h-5 text-slate-500" />
            </motion.div>
          ))}
        </div>
      )}

      {/* Selected Item Modal */}
      <AnimatePresence>
        {selectedItem && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedItem(null)}
          >
            <motion.div
              className="bg-slate-900 rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Modal Header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className={`w-16 h-16 rounded-2xl flex items-center justify-center ${
                    selectedItem.category === "documentation" ? "bg-blue-500/20" :
                    selectedItem.category === "simulation" || selectedItem.category === "synthesis" ? "bg-purple-500/20" :
                    selectedItem.category === "tool" ? "bg-cyan-500/20" :
                    selectedItem.category === "game" ? "bg-rose-500/20" :
                    selectedItem.category === "research" ? "bg-orange-500/20" :
                    "bg-violet-500/20"
                  }`}>
                    <selectedItem.icon className={`w-8 h-8 ${
                      selectedItem.category === "documentation" ? "text-blue-400" :
                      selectedItem.category === "simulation" || selectedItem.category === "synthesis" ? "text-purple-400" :
                      selectedItem.category === "tool" ? "text-cyan-400" :
                      selectedItem.category === "game" ? "text-rose-400" :
                      selectedItem.category === "research" ? "text-orange-400" :
                      "text-violet-400"
                    }`} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-xl font-bold text-white">{selectedItem.title}</h3>
                      {selectedItem.featured && <Star className="w-5 h-5 text-amber-400 fill-amber-400" />}
                      {selectedItem.new && <Sparkles className="w-5 h-5 text-emerald-400" />}
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`text-sm px-2 py-0.5 rounded ${
                        selectedItem.difficulty === "beginner" ? "bg-green-500/20 text-green-400" :
                        selectedItem.difficulty === "intermediate" ? "bg-yellow-500/20 text-yellow-400" :
                        selectedItem.difficulty === "advanced" ? "bg-orange-500/20 text-orange-400" :
                        "bg-red-500/20 text-red-400"
                      }`}>
                        {selectedItem.difficulty}
                      </span>
                      <span className="text-sm text-slate-500">{selectedItem.estimatedTime} minutes</span>
                      <span className="text-sm text-slate-500 capitalize">{selectedItem.category}</span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedItem(null)}
                  className="p-2 text-slate-500 hover:text-white"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Description */}
              <p className="text-slate-300 mb-6">{selectedItem.description}</p>

              {/* Outcomes */}
              <div className="mb-6">
                <h4 className="text-white font-medium mb-2">What You&apos;ll Learn</h4>
                <ul className="space-y-1">
                  {selectedItem.outcomes.map((outcome, idx) => (
                    <li key={idx} className="flex items-center gap-2 text-sm text-slate-400">
                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                      {outcome}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Prerequisites */}
              {selectedItem.prerequisites.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-white font-medium mb-2">Prerequisites</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedItem.prerequisites.map((prereq) => (
                      <span key={prereq} className="px-3 py-1 rounded-lg bg-slate-800 text-slate-300 text-sm">
                        {prereq}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Tags */}
              <div className="mb-6">
                <h4 className="text-white font-medium mb-2">Tags</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedItem.tags.map((tag) => (
                    <span key={tag} className="px-2 py-1 rounded bg-purple-500/20 text-purple-300 text-sm">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="p-4 bg-slate-800/50 rounded-xl text-center">
                  <div className="text-2xl font-bold text-amber-400">{selectedItem.rating}</div>
                  <div className="text-xs text-slate-500">Rating ({selectedItem.reviews} reviews)</div>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-xl text-center">
                  <div className="text-2xl font-bold text-emerald-400">{(selectedItem.completionRate * 100).toFixed(0)}%</div>
                  <div className="text-xs text-slate-500">Completion Rate</div>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-xl text-center">
                  <div className="text-2xl font-bold text-cyan-400">{selectedItem.estimatedTime}</div>
                  <div className="text-xs text-slate-500">Minutes</div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-4">
                <Link
                  href={selectedItem.path}
                  className="flex-1 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-medium text-center"
                >
                  Open Resource
                </Link>
                <motion.button
                  onClick={() => toggleFavorite(selectedItem.id)}
                  className={`p-3 rounded-xl ${favorites.has(selectedItem.id) ? "bg-rose-500/20 text-rose-400" : "bg-slate-800 text-slate-400"}`}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <Heart className={`w-5 h-5 ${favorites.has(selectedItem.id) ? "fill-rose-400" : ""}`} />
                </motion.button>
                <motion.button
                  onClick={() => toggleBookmark(selectedItem.id)}
                  className={`p-3 rounded-xl ${bookmarks.has(selectedItem.id) ? "bg-cyan-500/20 text-cyan-400" : "bg-slate-800 text-slate-400"}`}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <Bookmark className={`w-5 h-5 ${bookmarks.has(selectedItem.id) ? "fill-cyan-400" : ""}`} />
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  ExplorerHub,
  CONTENT_LIBRARY
};
