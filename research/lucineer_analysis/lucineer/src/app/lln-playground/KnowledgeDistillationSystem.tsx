"use client";

import { useState, useEffect, useCallback, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  Sparkles,
  Database,
  Zap,
  Target,
  TrendingUp,
  Layers,
  GitBranch,
  RefreshCw,
  Play,
  Pause,
  Download,
  Upload,
  Settings,
  ChevronRight,
  BarChart3,
  LineChart,
  PieChart,
  Activity,
  Cpu,
  HardDrive,
  Network,
  Atom,
  Crystal,
  Hexagon,
  Triangle,
  Square,
  Circle,
  Infinity,
  TreeDeciduous,
  Sprout,
  Sun,
  Wind,
  Droplet,
  Flame,
  Snowflake,
  Star,
  Award,
  Trophy,
  Medal,
  Crown,
  Gem,
  Diamond,
  Lightbulb,
  BookOpen,
  GraduationCap,
  Microscope,
  FlaskConical,
  TestTube,
  Beaker,
  Pill,
  Stethoscope,
  Heart,
  Shield,
  Sword,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  CheckCircle,
  XCircle,
  HelpCircle,
  Info,
  MessageCircle,
  MessageSquare,
  Send,
  Receive,
  Link,
  Unlink,
  Merge,
  Split,
  Copy,
  Clipboard,
  FileText,
  FileCode,
  FileJson,
  FileSpreadsheet,
  FolderOpen,
  Folder,
  Archive,
  Package,
  Box,
  Container,
  Server,
  Cloud,
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
  Bluetooth,
  Signal,
  Cable,
  Plug,
  Battery,
  BatteryCharging,
  BatteryFull,
  BatteryMedium,
  BatteryLow,
  Power,
  SwitchCamera,
  ToggleLeft,
  ToggleRight,
  Slider,
  Sliders,
  Gauge,
  Dashboard,
  PanelTop,
  PanelBottom,
  PanelLeft,
  PanelRight,
  Layout,
  LayoutDashboard,
  LayoutGrid,
  LayoutList,
  Columns,
  Rows,
  Table,
  Table2,
  Spreadsheet,
  Calculator,
  Sigma,
  Percent,
  Hash,
  AtSign,
  Key,
  Lock,
  Unlock,
  Eye,
  EyeOff,
  Visibility,
  VisibilityOff,
  Focus,
  Crosshair,
  Scan,
  Search,
  Filter,
  FilterX,
  SortAsc,
  SortDesc,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  ArrowDownRight,
  ArrowDownLeft,
  ArrowUpLeft,
  MoveUp,
  MoveDown,
  MoveLeft,
  MoveRight,
  RotateCcw,
  RotateCw,
  FlipHorizontal,
  FlipVertical,
  Move,
  Move3d,
  ZoomIn,
  ZoomOut,
  Maximize,
  Minimize,
  Expand,
  Shrink,
  FitScreen,
  FullScreen,
  SquareIcon,
  CircleDot,
  Octagon,
  DiamondIcon,
  Pentagon,
  HexagonIcon,
  Heptagon,
  OctagonIcon,
  StarIcon,
  SunIcon,
  MoonIcon,
  CloudIcon,
  CloudRain,
  CloudSnow,
  CloudLightning,
  CloudFog,
  CloudDrizzle,
  CloudHail,
  CloudMoon,
  CloudSun,
  Cloudy,
  Drizzle,
  Droplets,
  Thermometer,
  ThermometerSun,
  ThermometerSnowflake,
  ThermometerSunIcon,
  Umbrella,
  WindIcon,
  Tornado,
  Hurricane,
  Storm,
  Thunderstorm,
  Rainbow,
  Sunset,
  Sunrise,
  Horizon,
  HorizonRule,
  Sky,
  Mountain,
  MountainSnow,
  MountainIcon,
  TreePine,
  TreeDeciduousIcon,
  Tree,
  Trees,
  LeafIcon,
  LeafyGreen,
  Flower,
  Flower2,
  FlowerTulip,
  FlowerLotus,
  Daisy,
  Tulip,
  Lotus,
  Rose,
  Sunflower,
  Lavender,
  Hibiscus,
  Cactus,
  PalmTree,
  Ficus,
  Bonsai,
  Gardener,
  Shovel,
  Pickaxe,
  Axe,
  Saw,
  Hammer,
  Wrench,
  Screwdriver,
  Nut,
  Bolt,
  Cog,
  Cogs,
  SettingsIcon,
  Settings2,
  SettingsGear,
  Config,
  Preferences,
  Options,
  Customize,
  Personalize,
  Adjustments,
  ControlPanel,
  Tune,
  Dial,
  Knob,
  Dialpad,
  Keypad,
  Keyboard,
  Mouse,
  MousePointer,
  MousePointer2,
  MousePointerClick,
  Hand,
  HandMetal,
  HandFist,
  HandHeart,
  HandHelping,
  Handshake,
  ThumbsUp,
  ThumbsDown,
  Pointer,
  Point,
  FingerPrint,
  ScanFace,
  ScanLine,
  ScanEye,
  IdCard,
  Identification,
  Badge,
  BadgeCheck,
  BadgeAlert,
  BadgeDollarSign,
  BadgePercent,
  Ticket,
  TicketCheck,
  TicketX,
  Tag,
  Tags,
  Label,
  Bookmark,
  BookmarkCheck,
  BookmarkX,
  BookmarkPlus,
  BookmarkMinus,
  Flag,
  FlagOff,
  FlagTriangleLeft,
  FlagTriangleRight,
  FlagVariant,
  FlagIcon,
  Banner,
  Notice,
  Announcement,
  Billboard,
  Signpost,
  SignpostBig,
  Milestone,
  FlagPennant,
  FlagBanner,
  FlagWave,
} from "lucide-react";

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

type DistillationPhase = 
  | "seed-extraction"     // Extract compressed knowledge
  | "pattern-recognition" // Identify patterns in data
  | "logic-compression"   // Compress logic into seeds
  | "cultural-adaptation" // Adapt for different cultures
  | "age-calibration"     // Calibrate for age groups
  | "validation"          // Validate distillation quality
  | "deployment";         // Deploy to SMPbot

type KnowledgeType = 
  | "constraint-logic"    // How constraints work
  | "idiom-wisdom"        // Compressed communication
  | "agent-decision"      // Decision-making patterns
  | "cultural-pattern"    // Cross-cultural understanding
  | "teaching-method"     // Educational approaches
  | "synthesis-pattern";  // Method combination

interface DistillationJob {
  id: string;
  name: string;
  type: KnowledgeType;
  phase: DistillationPhase;
  progress: number;
  inputTokens: number;
  outputTokens: number;
  compressionRatio: number;
  qualityScore: number;
  culturalVariants: number;
  ageAdaptations: number;
  timestamp: number;
  status: "queued" | "running" | "completed" | "failed";
}

interface TrainingExample {
  id: string;
  input: string;
  output: string;
  tokens: number;
  quality: number;
  culturalContext: string;
  ageGroup: string;
  tags: string[];
}

interface MLPipeline {
  name: string;
  stages: PipelineStage[];
  accuracy: number;
  throughput: number;
  latency: number;
}

interface PipelineStage {
  name: string;
  description: string;
  inputSize: number;
  outputSize: number;
  processingTime: number;
  accuracy: number;
}

// ============================================================================
// DISTILLATION TEMPLATES
// ============================================================================

const DISTILLATION_TEMPLATES: Record<KnowledgeType, {
  name: string;
  description: string;
  icon: React.ElementType;
  color: string;
  avgCompression: number;
  phases: DistillationPhase[];
}> = {
  "constraint-logic": {
    name: "Constraint Logic Distillation",
    description: "Extract how constraints shape creativity and communication",
    icon: Lock,
    color: "from-purple-500 to-pink-500",
    avgCompression: 0.85,
    phases: ["seed-extraction", "pattern-recognition", "logic-compression", "validation"]
  },
  "idiom-wisdom": {
    name: "Idiom Wisdom Distillation",
    description: "Compress cultural communication patterns into idioms",
    icon: MessageSquare,
    color: "from-amber-500 to-orange-500",
    avgCompression: 0.92,
    phases: ["seed-extraction", "cultural-adaptation", "logic-compression", "validation"]
  },
  "agent-decision": {
    name: "Agent Decision Distillation",
    description: "Extract decision-making patterns from agent behavior",
    icon: Brain,
    color: "from-cyan-500 to-blue-500",
    avgCompression: 0.78,
    phases: ["pattern-recognition", "logic-compression", "age-calibration", "validation"]
  },
  "cultural-pattern": {
    name: "Cultural Pattern Distillation",
    description: "Identify and compress cross-cultural understanding",
    icon: Globe,
    color: "from-emerald-500 to-teal-500",
    avgCompression: 0.88,
    phases: ["seed-extraction", "cultural-adaptation", "validation", "deployment"]
  },
  "teaching-method": {
    name: "Teaching Method Distillation",
    description: "Compress educational approaches into reusable patterns",
    icon: GraduationCap,
    color: "from-rose-500 to-red-500",
    avgCompression: 0.82,
    phases: ["pattern-recognition", "age-calibration", "logic-compression", "validation"]
  },
  "synthesis-pattern": {
    name: "Synthesis Pattern Distillation",
    description: "Extract patterns for combining teaching methods",
    icon: Merge,
    color: "from-violet-500 to-purple-500",
    avgCompression: 0.90,
    phases: ["seed-extraction", "pattern-recognition", "logic-compression", "validation", "deployment"]
  }
};

// ============================================================================
// ORIGIN-FIRST DISTILLATION ENGINE
// ============================================================================

export class OriginFirstDistillationEngine {
  private jobs: Map<string, DistillationJob>;
  private trainingData: TrainingExample[];
  private pipelines: MLPipeline[];

  constructor() {
    this.jobs = new Map();
    this.trainingData = [];
    this.pipelines = this.initializePipelines();
    this.initializeSampleData();
  }

  private initializePipelines(): MLPipeline[] {
    return [
      {
        name: "Constraint Crystallizer",
        stages: [
          { name: "Input Parsing", description: "Parse constraint definitions", inputSize: 1024, outputSize: 512, processingTime: 45, accuracy: 0.98 },
          { name: "Pattern Matching", description: "Match against known patterns", inputSize: 512, outputSize: 256, processingTime: 78, accuracy: 0.95 },
          { name: "Logic Compression", description: "Compress into seed format", inputSize: 256, outputSize: 64, processingTime: 120, accuracy: 0.92 },
          { name: "Validation", description: "Validate compression quality", inputSize: 64, outputSize: 64, processingTime: 30, accuracy: 0.99 }
        ],
        accuracy: 0.94,
        throughput: 850,
        latency: 273
      },
      {
        name: "Idiom Sage",
        stages: [
          { name: "Context Analysis", description: "Analyze usage context", inputSize: 2048, outputSize: 1024, processingTime: 65, accuracy: 0.97 },
          { name: "Cultural Mapping", description: "Map to cultural patterns", inputSize: 1024, outputSize: 512, processingTime: 90, accuracy: 0.94 },
          { name: "Meaning Extraction", description: "Extract core meaning", inputSize: 512, outputSize: 128, processingTime: 110, accuracy: 0.91 },
          { name: "Emoji Encoding", description: "Encode as emoji sequence", inputSize: 128, outputSize: 32, processingTime: 45, accuracy: 0.96 }
        ],
        accuracy: 0.92,
        throughput: 720,
        latency: 310
      },
      {
        name: "Decision Agent Trainer",
        stages: [
          { name: "Behavior Logging", description: "Log agent decisions", inputSize: 4096, outputSize: 2048, processingTime: 55, accuracy: 0.99 },
          { name: "Outcome Analysis", description: "Analyze decision outcomes", inputSize: 2048, outputSize: 1024, processingTime: 85, accuracy: 0.93 },
          { name: "Pattern Extraction", description: "Extract decision patterns", inputSize: 1024, outputSize: 256, processingTime: 140, accuracy: 0.88 },
          { name: "Seed Generation", description: "Generate decision seeds", inputSize: 256, outputSize: 64, processingTime: 75, accuracy: 0.90 }
        ],
        accuracy: 0.89,
        throughput: 620,
        latency: 355
      }
    ];
  }

  private initializeSampleData() {
    // Generate sample training examples
    const cultures = ["JP", "US", "GH", "DE", "IN", "BR", "CN", "KR", "UK", "FR"];
    const ageGroups = ["child", "teen", "university", "adult", "senior"];
    
    for (let i = 0; i < 100; i++) {
      this.trainingData.push({
        id: `example_${i}`,
        input: this.generateSampleInput(),
        output: this.generateSampleOutput(),
        tokens: Math.floor(Math.random() * 500) + 50,
        quality: 0.7 + Math.random() * 0.3,
        culturalContext: cultures[Math.floor(Math.random() * cultures.length)],
        ageGroup: ageGroups[Math.floor(Math.random() * ageGroups.length)],
        tags: this.generateTags()
      });
    }
  }

  private generateSampleInput(): string {
    const inputs = [
      "Agent describes 'elephant' without using the letter 'E'",
      "Student asks 'Why do constraints improve creativity?'",
      "Cultural translation needed for idiom 'cold shoulder'",
      "Age-adaptive explanation for 'patience' concept",
      "Method synthesis: Socratic + Storytelling"
    ];
    return inputs[Math.floor(Math.random() * inputs.length)];
  }

  private generateSampleOutput(): string {
    const outputs = [
      "Large gray friend with trunk! Never forgets!",
      "Constraints create focus. Without limits, we wander. With limits, we create.",
      "🧊💨 = Cold shoulder - ignore/dismiss",
      "Child: Drawing with one color. Adult: Budget limits.",
      "Wisdom Synthesis Engine: Story + Question + Reflection"
    ];
    return outputs[Math.floor(Math.random() * outputs.length)];
  }

  private generateTags(): string[] {
    const allTags = ["constraint", "idiom", "cultural", "age-adaptive", "synthesis", "teaching", "pattern"];
    const count = Math.floor(Math.random() * 3) + 1;
    const shuffled = allTags.sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
  }

  // Create a new distillation job
  createJob(name: string, type: KnowledgeType): DistillationJob {
    const template = DISTILLATION_TEMPLATES[type];
    const job: DistillationJob = {
      id: `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name,
      type,
      phase: template.phases[0],
      progress: 0,
      inputTokens: Math.floor(Math.random() * 50000) + 10000,
      outputTokens: 0,
      compressionRatio: 0,
      qualityScore: 0,
      culturalVariants: 0,
      ageAdaptations: 0,
      timestamp: Date.now(),
      status: "queued"
    };
    this.jobs.set(job.id, job);
    return job;
  }

  // Run distillation simulation
  async runDistillation(jobId: string, onProgress: (job: DistillationJob) => void): Promise<DistillationJob> {
    const job = this.jobs.get(jobId);
    if (!job) throw new Error("Job not found");

    const template = DISTILLATION_TEMPLATES[job.type];
    job.status = "running";

    for (let phaseIndex = 0; phaseIndex < template.phases.length; phaseIndex++) {
      job.phase = template.phases[phaseIndex];
      
      // Simulate phase progress
      for (let progress = 0; progress <= 100; progress += 5) {
        await new Promise(resolve => setTimeout(resolve, 100));
        job.progress = ((phaseIndex * 100) + progress) / template.phases.length;
        onProgress({ ...job });
      }

      // Update job stats based on phase
      switch (job.phase) {
        case "seed-extraction":
          job.outputTokens = Math.floor(job.inputTokens * 0.5);
          break;
        case "pattern-recognition":
          job.qualityScore = 0.85 + Math.random() * 0.1;
          break;
        case "logic-compression":
          job.compressionRatio = template.avgCompression + (Math.random() * 0.1 - 0.05);
          job.outputTokens = Math.floor(job.inputTokens * (1 - job.compressionRatio));
          break;
        case "cultural-adaptation":
          job.culturalVariants = Math.floor(Math.random() * 8) + 4;
          break;
        case "age-calibration":
          job.ageAdaptations = 5;
          break;
        case "validation":
          job.qualityScore = Math.min(1, job.qualityScore + 0.05);
          break;
      }
    }

    job.progress = 100;
    job.status = "completed";
    onProgress({ ...job });
    return job;
  }

  // Get training data for ML
  getTrainingData(filters?: {
    culturalContext?: string;
    ageGroup?: string;
    minQuality?: number;
    tags?: string[];
  }): TrainingExample[] {
    let data = [...this.trainingData];

    if (filters) {
      if (filters.culturalContext) {
        data = data.filter(d => d.culturalContext === filters.culturalContext);
      }
      if (filters.ageGroup) {
        data = data.filter(d => d.ageGroup === filters.ageGroup);
      }
      if (filters.minQuality) {
        data = data.filter(d => d.quality >= filters.minQuality!);
      }
      if (filters.tags && filters.tags.length > 0) {
        data = data.filter(d => filters.tags!.some(tag => d.tags.includes(tag)));
      }
    }

    return data;
  }

  // Get pipelines
  getPipelines(): MLPipeline[] {
    return this.pipelines;
  }

  // Get all jobs
  getJobs(): DistillationJob[] {
    return Array.from(this.jobs.values()).sort((a, b) => b.timestamp - a.timestamp);
  }

  // Calculate ML training metrics
  getTrainingMetrics() {
    const data = this.trainingData;
    const jobs = this.getJobs();

    return {
      totalExamples: data.length,
      avgQuality: data.reduce((sum, d) => sum + d.quality, 0) / data.length,
      totalTokens: data.reduce((sum, d) => sum + d.tokens, 0),
      culturalCoverage: new Set(data.map(d => d.culturalContext)).size,
      ageCoverage: new Set(data.map(d => d.ageGroup)).size,
      jobsCompleted: jobs.filter(j => j.status === "completed").length,
      jobsRunning: jobs.filter(j => j.status === "running").length,
      avgCompressionRatio: jobs.length > 0 
        ? jobs.reduce((sum, j) => sum + j.compressionRatio, 0) / jobs.length 
        : 0,
      pipelineThroughput: this.pipelines.reduce((sum, p) => sum + p.throughput, 0),
      avgLatency: this.pipelines.reduce((sum, p) => sum + p.latency, 0) / this.pipelines.length
    };
  }
}

// ============================================================================
// KNOWLEDGE DISTILLATION COMPONENT
// ============================================================================

interface KnowledgeDistillationSystemProps {
  onJobComplete?: (job: DistillationJob) => void;
}

export function KnowledgeDistillationSystem({ onJobComplete }: KnowledgeDistillationSystemProps) {
  const [engine] = useState(() => new OriginFirstDistillationEngine());
  const [jobs, setJobs] = useState<DistillationJob[]>([]);
  const [selectedType, setSelectedType] = useState<KnowledgeType>("constraint-logic");
  const [jobName, setJobName] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [trainingData, setTrainingData] = useState<TrainingExample[]>([]);
  const [metrics, setMetrics] = useState(engine.getTrainingMetrics());
  const [activeTab, setActiveTab] = useState<"distillation" | "training" | "pipelines">("distillation");

  const handleCreateJob = useCallback(() => {
    if (!jobName.trim()) return;
    const job = engine.createJob(jobName, selectedType);
    setJobs(engine.getJobs());
    setJobName("");
    
    // Auto-run the job
    setIsRunning(true);
    engine.runDistillation(job.id, (updatedJob) => {
      setJobs(engine.getJobs());
      if (updatedJob.status === "completed") {
        setIsRunning(false);
        setMetrics(engine.getTrainingMetrics());
        onJobComplete?.(updatedJob);
      }
    });
  }, [engine, jobName, selectedType, onJobComplete]);

  const handleLoadTrainingData = useCallback((filters?: {
    culturalContext?: string;
    ageGroup?: string;
    minQuality?: number;
  }) => {
    setTrainingData(engine.getTrainingData(filters));
  }, [engine]);

  useEffect(() => {
    handleLoadTrainingData();
  }, [handleLoadTrainingData]);

  const pipelines = engine.getPipelines();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-cyan-900/30 via-purple-900/20 to-amber-900/30 rounded-2xl p-6 border border-cyan-500/30">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500/30 to-purple-500/30 flex items-center justify-center">
              <Brain className="w-8 h-8 text-cyan-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Knowledge Distillation System</h2>
              <p className="text-cyan-300">Origin-First ML Training Data Generation</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-white">{metrics.totalExamples}</div>
            <div className="text-xs text-slate-500">Training Examples</div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
          {[
            { label: "Examples", value: metrics.totalExamples, icon: Database, color: "cyan" },
            { label: "Quality", value: `${(metrics.avgQuality * 100).toFixed(0)}%`, icon: Star, color: "amber" },
            { label: "Tokens", value: `${(metrics.totalTokens / 1000).toFixed(1)}K`, icon: Zap, color: "purple" },
            { label: "Cultures", value: metrics.culturalCoverage, icon: Globe, color: "emerald" },
            { label: "Age Groups", value: metrics.ageCoverage, icon: Users, color: "rose" },
            { label: "Jobs Done", value: metrics.jobsCompleted, icon: CheckCircle, color: "green" },
            { label: "Throughput", value: `${metrics.pipelineThroughput}/s`, icon: Activity, color: "blue" },
            { label: "Latency", value: `${metrics.avgLatency.toFixed(0)}ms`, icon: Clock, color: "orange" }
          ].map((stat, idx) => (
            <motion.div
              key={stat.label}
              className="p-3 bg-slate-900/50 rounded-xl border border-slate-700 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
            >
              <stat.icon className={`w-4 h-4 mx-auto mb-1 text-${stat.color}-400`} />
              <div className="text-lg font-bold text-white">{stat.value}</div>
              <div className="text-xs text-slate-500">{stat.label}</div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: "distillation", label: "Distillation Jobs", icon: FlaskConical },
          { id: "training", label: "Training Data", icon: Database },
          { id: "pipelines", label: "ML Pipelines", icon: GitBranch }
        ].map((tab) => (
          <motion.button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as typeof activeTab)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all ${
              activeTab === tab.id
                ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                : "bg-slate-800/50 text-slate-400 border border-slate-700 hover:border-slate-600"
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </motion.button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === "distillation" && (
          <motion.div
            key="distillation"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* New Job Form */}
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-400" />
                Create Distillation Job
              </h3>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="text-sm text-slate-400 mb-1 block">Job Name</label>
                  <input
                    type="text"
                    value={jobName}
                    onChange={(e) => setJobName(e.target.value)}
                    placeholder="e.g., Constraint Logic v2.0"
                    className="w-full px-4 py-2 rounded-xl bg-slate-900/50 border border-slate-600 text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="text-sm text-slate-400 mb-1 block">Knowledge Type</label>
                  <select
                    value={selectedType}
                    onChange={(e) => setSelectedType(e.target.value as KnowledgeType)}
                    className="w-full px-4 py-2 rounded-xl bg-slate-900/50 border border-slate-600 text-white focus:border-cyan-500 focus:outline-none"
                  >
                    {Object.entries(DISTILLATION_TEMPLATES).map(([type, template]) => (
                      <option key={type} value={type}>{template.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Template Preview */}
              <div className={`p-4 rounded-xl bg-gradient-to-r ${DISTILLATION_TEMPLATES[selectedType].color} bg-opacity-20 border border-slate-600 mb-4`}>
                <div className="flex items-center gap-3 mb-2">
                  {(() => {
                    const Icon = DISTILLATION_TEMPLATES[selectedType].icon;
                    return <Icon className="w-5 h-5 text-white" />;
                  })()}
                  <span className="text-white font-medium">{DISTILLATION_TEMPLATES[selectedType].name}</span>
                </div>
                <p className="text-sm text-slate-300">{DISTILLATION_TEMPLATES[selectedType].description}</p>
                <div className="flex items-center gap-4 mt-2 text-xs text-slate-400">
                  <span>Avg Compression: {((1 - DISTILLATION_TEMPLATES[selectedType].avgCompression) * 100).toFixed(0)}%</span>
                  <span>Phases: {DISTILLATION_TEMPLATES[selectedType].phases.length}</span>
                </div>
              </div>

              <motion.button
                onClick={handleCreateJob}
                disabled={isRunning || !jobName.trim()}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-medium flex items-center justify-center gap-2 disabled:opacity-50"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {isRunning ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Running Distillation...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Start Distillation
                  </>
                )}
              </motion.button>
            </div>

            {/* Jobs List */}
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-cyan-400" />
                Distillation Jobs
              </h3>

              {jobs.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  <FlaskConical className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No distillation jobs yet. Create one above!</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {jobs.map((job) => (
                    <motion.div
                      key={job.id}
                      className="p-4 bg-slate-900/50 rounded-xl border border-slate-600"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          {(() => {
                            const Icon = DISTILLATION_TEMPLATES[job.type].icon;
                            return <Icon className="w-5 h-5 text-cyan-400" />;
                          })()}
                          <span className="text-white font-medium">{job.name}</span>
                        </div>
                        <div className={`px-2 py-0.5 rounded text-xs ${
                          job.status === "completed" ? "bg-green-500/20 text-green-400" :
                          job.status === "running" ? "bg-cyan-500/20 text-cyan-400" :
                          job.status === "failed" ? "bg-red-500/20 text-red-400" :
                          "bg-slate-500/20 text-slate-400"
                        }`}>
                          {job.status}
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="mb-2">
                        <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                          <span>{job.phase}</span>
                          <span>{(job.progress * 100).toFixed(0)}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <motion.div
                            className="h-full bg-gradient-to-r from-cyan-500 to-purple-500"
                            initial={{ width: 0 }}
                            animate={{ width: `${job.progress * 100}%` }}
                          />
                        </div>
                      </div>

                      {/* Job Stats */}
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span>In: {(job.inputTokens / 1000).toFixed(1)}K tokens</span>
                        <span>Out: {(job.outputTokens / 1000).toFixed(1)}K tokens</span>
                        <span>Compression: {((1 - job.compressionRatio) * 100).toFixed(0)}%</span>
                        <span>Quality: {(job.qualityScore * 100).toFixed(0)}%</span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        )}

        {activeTab === "training" && (
          <motion.div
            key="training"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Database className="w-5 h-5 text-purple-400" />
              Training Data ({trainingData.length} examples)
            </h3>

            <div className="space-y-2 max-h-96 overflow-y-auto">
              {trainingData.slice(0, 20).map((example) => (
                <motion.div
                  key={example.id}
                  className="p-3 bg-slate-900/50 rounded-lg border border-slate-600"
                  whileHover={{ scale: 1.01 }}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-1">
                      <div className="text-sm text-white mb-1">{example.input}</div>
                      <div className="text-sm text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">
                        → {example.output}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-slate-500">{example.tokens} tokens</div>
                      <div className="text-xs text-amber-400">{(example.quality * 100).toFixed(0)}% quality</div>
                      <div className="text-xs text-purple-400">{example.culturalContext}</div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === "pipelines" && (
          <motion.div
            key="pipelines"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {pipelines.map((pipeline, idx) => (
              <div key={pipeline.name} className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/30 to-purple-500/30 flex items-center justify-center">
                      <GitBranch className="w-5 h-5 text-cyan-400" />
                    </div>
                    <div>
                      <h4 className="text-white font-medium">{pipeline.name}</h4>
                      <div className="text-xs text-slate-500">
                        {pipeline.throughput} examples/s • {pipeline.latency}ms latency
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-emerald-400">{(pipeline.accuracy * 100).toFixed(0)}%</div>
                    <div className="text-xs text-slate-500">Accuracy</div>
                  </div>
                </div>

                {/* Pipeline Stages */}
                <div className="flex items-center gap-2 overflow-x-auto pb-2">
                  {pipeline.stages.map((stage, stageIdx) => (
                    <div key={stage.name} className="flex items-center">
                      <motion.div
                        className="p-3 bg-slate-900/50 rounded-lg border border-slate-600 min-w-[150px]"
                        whileHover={{ scale: 1.02 }}
                      >
                        <div className="text-xs text-white font-medium mb-1">{stage.name}</div>
                        <div className="text-xs text-slate-500 mb-2">{stage.description}</div>
                        <div className="flex items-center gap-2 text-xs">
                          <span className="text-cyan-400">{stage.inputSize}→{stage.outputSize}</span>
                          <span className="text-amber-400">{(stage.accuracy * 100).toFixed(0)}%</span>
                        </div>
                      </motion.div>
                      {stageIdx < pipeline.stages.length - 1 && (
                        <ChevronRight className="w-4 h-4 text-slate-600 mx-1" />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Download Section */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">Export Training Data</h3>
            <p className="text-sm text-slate-500">Download ML training examples for your models</p>
          </div>
          <motion.button
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-medium"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Download className="w-4 h-4" />
            Export JSON
          </motion.button>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  KnowledgeDistillationSystem,
  OriginFirstDistillationEngine,
  DISTILLATION_TEMPLATES
};
