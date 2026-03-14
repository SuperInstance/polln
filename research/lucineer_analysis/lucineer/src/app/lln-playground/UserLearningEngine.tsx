"use client";

import { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  Sparkles,
  Target,
  TrendingUp,
  Activity,
  Zap,
  Eye,
  EyeOff,
  Settings,
  BarChart3,
  LineChart,
  PieChart,
  Clock,
  User,
  Users,
  Heart,
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
  Cpu,
  Network,
  Database,
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
  Rocket,
  Satellite,
  Radar,
  Radio,
  Wifi,
  Signal,
  Battery,
  BatteryCharging,
  Power,
  Gauge,
  Dashboard,
  PanelTop,
  Layout,
  LayoutDashboard,
  LayoutGrid,
  LayoutList,
  Columns,
  Rows,
  Table,
  Table2,
  Calculator,
  Sigma,
  Hash,
  Key,
  Lock,
  Unlock,
  Focus,
  Scan,
  Search,
  Filter,
  SortAsc,
  SortDesc,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Play,
  Pause,
  Download,
  Upload,
  Copy,
  Clipboard,
  FileText,
  FileJson,
  FolderOpen,
  Folder,
  Archive,
  Package,
  Box,
  Container,
  Layers,
  GitBranch,
  GitMerge,
  GitCommit,
  GitPullRequest,
  Merge,
  Split,
  TreeDeciduous,
  Sprout,
  Sun,
  Wind,
  Droplet,
  Flame,
  Snowflake,
  SunIcon,
  MoonIcon,
  CloudIcon,
  CloudRain,
  Thermometer,
  Leaf,
  Flower2,
  TreePine,
  Dna,
  Atom,
  Hexagon,
  Triangle,
  Square,
  Circle,
  Infinity,
  Bot,
  MessageCircle,
  MessageSquare,
  AlertTriangle,
  Shield,
  CheckCircle,
  XCircle,
  HelpCircle,
  Info,
  Send,
  Receive,
  Link,
  Unlink,
  Move,
  Move3d,
  ZoomIn,
  ZoomOut,
  Maximize,
  Minimize,
  Expand,
  Shrink,
  FullScreen,
  CircleDot,
  Octagon,
  Pentagon,
  Heptagon,
  StarIcon,
  Sunrise,
  Sunset,
  Horizon,
  Mountain,
  Cactus,
  PalmTree,
  Shovel,
  Pickaxe,
  Hammer,
  Wrench,
  Screwdriver,
  Nut,
  Bolt,
  Cog,
  Cogs,
  Settings2,
  Adjustments,
  Tune,
  Dial,
  Keyboard,
  Mouse,
  MousePointer,
  Hand,
  Handshake,
  ThumbsUp,
  ThumbsDown,
  Pointer,
  FingerPrint,
  ScanFace,
  IdCard,
  Badge,
  BadgeCheck,
  BadgeAlert,
  Ticket,
  Tag,
  Label,
  Bookmark,
  BookmarkCheck,
  Flag,
  FlagOff,
  Banner,
  Signpost,
  Milestone,
} from "lucide-react";

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

type ActionType = 
  | "click"           // User clicked something
  | "hover"           // User hovered over something
  | "scroll"          // User scrolled
  | "input"           // User typed something
  | "select"          // User selected an option
  | "play"            // User started a game/simulation
  | "complete"        // User completed something
  | "share"           // User shared something
  | "save"            // User saved something
  | "create"          // User created something
  | "learn"           // User learned something
  | "teach"           // User taught something
  | "explore"         // User explored
  | "synthesize";     // User synthesized something

type LearningDomain = 
  | "gameplay"        // Game interactions
  | "navigation"      // How user navigates
  | "preferences"     // User preferences
  | "performance"     // User performance patterns
  | "social"          // Social interactions
  | "creative"        // Creative actions
  | "learning"        // Learning patterns
  | "teaching";       // Teaching patterns

type AdaptationType = 
  | "difficulty"      // Adjust difficulty
  | "pacing"          // Adjust pacing
  | "content"         // Adjust content
  | "interface"       // Adjust interface
  | "feedback"        // Adjust feedback style
  | "challenge"       // Adjust challenge level
  | "reward"          // Adjust reward system
  | "social";         // Adjust social features

interface UserAction {
  id: string;
  type: ActionType;
  domain: LearningDomain;
  target: string;
  context: Record<string, unknown>;
  timestamp: number;
  sessionId: string;
  duration?: number;
  outcome?: "success" | "failure" | "neutral";
  value?: number;
}

interface UserPattern {
  id: string;
  name: string;
  description: string;
  frequency: number;
  confidence: number;
  lastSeen: number;
  actions: string[];
  adaptations: AdaptationType[];
  mlFeatures: Record<string, number>;
}

interface UserPreference {
  id: string;
  category: string;
  key: string;
  value: unknown;
  confidence: number;
  learned: boolean;
  lastUpdated: number;
}

interface LearningModel {
  name: string;
  accuracy: number;
  trainingExamples: number;
  features: number;
  lastTrained: number;
  version: string;
}

interface AdaptationSuggestion {
  id: string;
  type: AdaptationType;
  reason: string;
  confidence: number;
  impact: "positive" | "neutral" | "negative";
  implemented: boolean;
  userFeedback?: "accepted" | "rejected" | "ignored";
}

interface NNLayer {
  name: string;
  neurons: number;
  activation: string;
  weights: number[][];
  biases: number[];
}

// ============================================================================
// USER LEARNING ENGINE CLASS
// ============================================================================

export class UserLearningEngine {
  private actions: UserAction[];
  private patterns: Map<string, UserPattern>;
  private preferences: Map<string, UserPreference>;
  private models: LearningModel[];
  private suggestions: AdaptationSuggestion[];
  private nnLayers: NNLayer[];
  private sessionId: string;

  constructor() {
    this.actions = [];
    this.patterns = new Map();
    this.preferences = new Map();
    this.models = this.initializeModels();
    this.suggestions = [];
    this.nnLayers = this.initializeNN();
    this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.initializeDefaultPreferences();
    this.initializePatterns();
  }

  private initializeModels(): LearningModel[] {
    return [
      {
        name: "Preference Predictor",
        accuracy: 0.87,
        trainingExamples: 12500,
        features: 128,
        lastTrained: Date.now() - 3600000,
        version: "2.3.1"
      },
      {
        name: "Difficulty Calibrator",
        accuracy: 0.92,
        trainingExamples: 8700,
        features: 64,
        lastTrained: Date.now() - 7200000,
        version: "1.8.4"
      },
      {
        name: "Engagement Forecaster",
        accuracy: 0.81,
        trainingExamples: 15000,
        features: 256,
        lastTrained: Date.now() - 1800000,
        version: "3.1.0"
      },
      {
        name: "Learning Style Detector",
        accuracy: 0.89,
        trainingExamples: 6200,
        features: 96,
        lastTrained: Date.now() - 5400000,
        version: "2.0.2"
      }
    ];
  }

  private initializeNN(): NNLayer[] {
    return [
      { name: "Input Layer", neurons: 128, activation: "relu", weights: [], biases: [] },
      { name: "Hidden Layer 1", neurons: 256, activation: "relu", weights: [], biases: [] },
      { name: "Hidden Layer 2", neurons: 128, activation: "relu", weights: [], biases: [] },
      { name: "Hidden Layer 3", neurons: 64, activation: "relu", weights: [], biases: [] },
      { name: "Output Layer", neurons: 16, activation: "softmax", weights: [], biases: [] }
    ];
  }

  private initializeDefaultPreferences() {
    const defaults: Array<{category: string; key: string; value: unknown; confidence: number}> = [
      { category: "interface", key: "theme", value: "dark", confidence: 0.6 },
      { category: "interface", key: "animations", value: true, confidence: 0.7 },
      { category: "gameplay", key: "difficulty", value: "adaptive", confidence: 0.8 },
      { category: "gameplay", key: "hints", value: "progressive", confidence: 0.7 },
      { category: "learning", key: "pace", value: "self-directed", confidence: 0.6 },
      { category: "learning", key: "style", value: "visual", confidence: 0.5 },
      { category: "social", key: "leaderboards", value: true, confidence: 0.6 },
      { category: "social", key: "sharing", value: "selective", confidence: 0.5 }
    ];

    defaults.forEach(pref => {
      this.preferences.set(`${pref.category}.${pref.key}`, {
        id: `pref_${pref.category}_${pref.key}`,
        ...pref,
        learned: false,
        lastUpdated: Date.now()
      });
    });
  }

  private initializePatterns() {
    const defaultPatterns: UserPattern[] = [
      {
        id: "pattern_explorer",
        name: "Explorer Pattern",
        description: "User likes to explore all options before committing",
        frequency: 0,
        confidence: 0.5,
        lastSeen: 0,
        actions: ["hover", "scroll", "click"],
        adaptations: ["content", "interface"],
        mlFeatures: { exploration_rate: 0, time_per_option: 0 }
      },
      {
        id: "pattern_completer",
        name: "Completer Pattern",
        description: "User focuses on finishing tasks before exploring",
        frequency: 0,
        confidence: 0.5,
        lastSeen: 0,
        actions: ["play", "complete"],
        adaptations: ["pacing", "reward"],
        mlFeatures: { completion_rate: 0, skip_rate: 0 }
      },
      {
        id: "pattern_socializer",
        name: "Socializer Pattern",
        description: "User engages heavily with social features",
        frequency: 0,
        confidence: 0.5,
        lastSeen: 0,
        actions: ["share", "teach"],
        adaptations: ["social", "feedback"],
        mlFeatures: { share_rate: 0, teach_rate: 0 }
      },
      {
        id: "pattern_creator",
        name: "Creator Pattern",
        description: "User loves to create and synthesize new things",
        frequency: 0,
        confidence: 0.5,
        lastSeen: 0,
        actions: ["create", "synthesize"],
        adaptations: ["content", "challenge"],
        mlFeatures: { creation_rate: 0, synthesis_complexity: 0 }
      }
    ];

    defaultPatterns.forEach(pattern => {
      this.patterns.set(pattern.id, pattern);
    });
  }

  // Record a user action
  recordAction(
    type: ActionType,
    domain: LearningDomain,
    target: string,
    context: Record<string, unknown> = {},
    outcome?: "success" | "failure" | "neutral",
    value?: number
  ): UserAction {
    const action: UserAction = {
      id: `action_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      domain,
      target,
      context,
      timestamp: Date.now(),
      sessionId: this.sessionId,
      outcome,
      value
    };

    this.actions.push(action);
    this.analyzeAction(action);
    return action;
  }

  // Analyze an action and update patterns/preferences
  private analyzeAction(action: UserAction) {
    // Update patterns based on action
    this.patterns.forEach((pattern, id) => {
      if (pattern.actions.includes(action.type)) {
        pattern.frequency++;
        pattern.lastSeen = action.timestamp;
        pattern.confidence = Math.min(1, pattern.confidence + 0.05);
        
        // Update ML features
        if (action.type === "hover") {
          pattern.mlFeatures.exploration_rate = (pattern.mlFeatures.exploration_rate || 0) + 1;
        }
        if (action.type === "complete") {
          pattern.mlFeatures.completion_rate = (pattern.mlFeatures.completion_rate || 0) + 1;
        }
        if (action.type === "share") {
          pattern.mlFeatures.share_rate = (pattern.mlFeatures.share_rate || 0) + 1;
        }
        if (action.type === "create") {
          pattern.mlFeatures.creation_rate = (pattern.mlFeatures.creation_rate || 0) + 1;
        }

        this.patterns.set(id, pattern);
      }
    });

    // Generate adaptation suggestions
    this.generateSuggestions(action);
  }

  // Generate adaptation suggestions
  private generateSuggestions(action: UserAction) {
    // Only generate suggestions occasionally to avoid noise
    if (Math.random() > 0.2) return;

    const suggestions: AdaptationSuggestion[] = [];

    // Check for difficulty adjustment needs
    if (action.domain === "gameplay" && action.outcome === "failure") {
      suggestions.push({
        id: `suggest_${Date.now()}_difficulty`,
        type: "difficulty",
        reason: "User struggled with recent challenge",
        confidence: 0.75,
        impact: "positive",
        implemented: false
      });
    }

    // Check for engagement patterns
    if (action.domain === "navigation" && action.type === "scroll") {
      suggestions.push({
        id: `suggest_${Date.now()}_pacing`,
        type: "pacing",
        reason: "User is exploring content thoroughly",
        confidence: 0.68,
        impact: "positive",
        implemented: false
      });
    }

    // Check for creative patterns
    if (action.domain === "creative" && action.type === "create") {
      suggestions.push({
        id: `suggest_${Date.now()}_challenge`,
        type: "challenge",
        reason: "User is actively creating, could handle more challenge",
        confidence: 0.82,
        impact: "positive",
        implemented: false
      });
    }

    this.suggestions.push(...suggestions);
  }

  // Get user's dominant pattern
  getDominantPattern(): UserPattern | null {
    let dominant: UserPattern | null = null;
    let maxConfidence = 0;

    this.patterns.forEach(pattern => {
      if (pattern.frequency > 0 && pattern.confidence > maxConfidence) {
        maxConfidence = pattern.confidence;
        dominant = pattern;
      }
    });

    return dominant;
  }

  // Get all patterns
  getPatterns(): UserPattern[] {
    return Array.from(this.patterns.values()).sort((a, b) => b.confidence - a.confidence);
  }

  // Get preferences
  getPreferences(): UserPreference[] {
    return Array.from(this.preferences.values());
  }

  // Update a preference
  updatePreference(category: string, key: string, value: unknown): UserPreference {
    const id = `${category}.${key}`;
    const existing = this.preferences.get(id);
    
    const preference: UserPreference = {
      id: `pref_${category}_${key}`,
      category,
      key,
      value,
      confidence: existing ? Math.min(1, existing.confidence + 0.1) : 0.7,
      learned: true,
      lastUpdated: Date.now()
    };

    this.preferences.set(id, preference);
    return preference;
  }

  // Get recent actions
  getRecentActions(count: number = 50): UserAction[] {
    return this.actions.slice(-count);
  }

  // Get models
  getModels(): LearningModel[] {
    return this.models;
  }

  // Get suggestions
  getSuggestions(): AdaptationSuggestion[] {
    return this.suggestions.slice(-20);
  }

  // Get NN layers
  getNNLayers(): NNLayer[] {
    return this.nnLayers;
  }

  // Simulate training on collected data
  async trainModels(onProgress: (model: LearningModel, progress: number) => void): Promise<void> {
    for (const model of this.models) {
      for (let progress = 0; progress <= 100; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 50));
        onProgress(model, progress);
      }
      model.trainingExamples += this.actions.length;
      model.lastTrained = Date.now();
      model.accuracy = Math.min(0.99, model.accuracy + 0.01);
    }
  }

  // Get session stats
  getSessionStats() {
    const sessionActions = this.actions.filter(a => a.sessionId === this.sessionId);
    
    return {
      sessionId: this.sessionId,
      duration: sessionActions.length > 0 
        ? Date.now() - sessionActions[0].timestamp 
        : 0,
      totalActions: this.actions.length,
      sessionActions: sessionActions.length,
      actionsByType: this.countByType(sessionActions),
      actionsByDomain: this.countByDomain(sessionActions),
      successRate: this.calculateSuccessRate(sessionActions),
      engagement: this.calculateEngagement(sessionActions),
      dominantPattern: this.getDominantPattern()?.name || "Unknown",
      learnedPreferences: Array.from(this.preferences.values()).filter(p => p.learned).length,
      pendingSuggestions: this.suggestions.filter(s => !s.implemented).length
    };
  }

  private countByType(actions: UserAction[]): Record<ActionType, number> {
    const counts: Record<string, number> = {};
    actions.forEach(a => {
      counts[a.type] = (counts[a.type] || 0) + 1;
    });
    return counts as Record<ActionType, number>;
  }

  private countByDomain(actions: UserAction[]): Record<LearningDomain, number> {
    const counts: Record<string, number> = {};
    actions.forEach(a => {
      counts[a.domain] = (counts[a.domain] || 0) + 1;
    });
    return counts as Record<LearningDomain, number>;
  }

  private calculateSuccessRate(actions: UserAction[]): number {
    const withOutcome = actions.filter(a => a.outcome);
    if (withOutcome.length === 0) return 0;
    const successes = withOutcome.filter(a => a.outcome === "success").length;
    return successes / withOutcome.length;
  }

  private calculateEngagement(actions: UserAction[]): number {
    // Simple engagement score based on action frequency and variety
    const recentActions = actions.slice(-20);
    const uniqueTypes = new Set(recentActions.map(a => a.type)).size;
    const actionRate = recentActions.length / Math.max(1, recentActions.length);
    return (uniqueTypes / 14 + actionRate) / 2;
  }
}

// ============================================================================
// USER LEARNING ENGINE COMPONENT
// ============================================================================

interface UserLearningEngineComponentProps {
  onPatternDetected?: (pattern: UserPattern) => void;
  onSuggestionGenerated?: (suggestion: AdaptationSuggestion) => void;
}

export function UserLearningEngineComponent({ 
  onPatternDetected, 
  onSuggestionGenerated 
}: UserLearningEngineComponentProps) {
  const [engine] = useState(() => new UserLearningEngine());
  const [patterns, setPatterns] = useState<UserPattern[]>([]);
  const [preferences, setPreferences] = useState<UserPreference[]>([]);
  const [suggestions, setSuggestions] = useState<AdaptationSuggestion[]>([]);
  const [models, setModels] = useState<LearningModel[]>([]);
  const [stats, setStats] = useState(engine.getSessionStats());
  const [isTraining, setIsTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState<Record<string, number>>({});
  const [activeTab, setActiveTab] = useState<"patterns" | "preferences" | "suggestions" | "models">("patterns");
  const [isRecording, setIsRecording] = useState(true);

  // Simulate user actions
  const simulateUserActions = useCallback(() => {
    const actionTypes: ActionType[] = ["click", "hover", "play", "complete", "create", "explore", "learn"];
    const domains: LearningDomain[] = ["gameplay", "navigation", "creative", "learning", "social"];
    const targets = ["tile_1", "game_mode", "constraint", "idiom", "agent", "synthesis"];

    for (let i = 0; i < 5; i++) {
      engine.recordAction(
        actionTypes[Math.floor(Math.random() * actionTypes.length)],
        domains[Math.floor(Math.random() * domains.length)],
        targets[Math.floor(Math.random() * targets.length)],
        {},
        Math.random() > 0.3 ? "success" : "failure"
      );
    }

    setPatterns(engine.getPatterns());
    setPreferences(engine.getPreferences());
    setSuggestions(engine.getSuggestions());
    setStats(engine.getSessionStats());
  }, [engine]);

  useEffect(() => {
    setPatterns(engine.getPatterns());
    setPreferences(engine.getPreferences());
    setSuggestions(engine.getSuggestions());
    setModels(engine.getModels());

    // Simulate some user actions on mount
    if (isRecording) {
      const interval = setInterval(simulateUserActions, 3000);
      return () => clearInterval(interval);
    }
  }, [engine, isRecording, simulateUserActions]);

  const handleTrainModels = useCallback(async () => {
    setIsTraining(true);
    await engine.trainModels((model, progress) => {
      setTrainingProgress(prev => ({ ...prev, [model.name]: progress }));
    });
    setModels(engine.getModels());
    setIsTraining(false);
  }, [engine]);

  const handleImplementSuggestion = useCallback((suggestionId: string) => {
    setSuggestions(prev => prev.map(s => 
      s.id === suggestionId ? { ...s, implemented: true } : s
    ));
  }, []);

  const dominantPattern = engine.getDominantPattern();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-purple-900/30 via-amber-900/20 to-emerald-900/30 rounded-2xl p-6 border border-purple-500/30">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/30 to-amber-500/30 flex items-center justify-center">
              <Brain className="w-8 h-8 text-purple-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">User Learning Engine</h2>
              <p className="text-purple-300">ML System That Learns From User Actions</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <motion.button
              onClick={() => setIsRecording(!isRecording)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl border transition-all ${
                isRecording 
                  ? "bg-red-500/20 border-red-500/30 text-red-400" 
                  : "bg-slate-800/50 border-slate-700 text-slate-400"
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isRecording ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
              {isRecording ? "Recording" : "Paused"}
            </motion.button>
            <motion.button
              onClick={handleTrainModels}
              disabled={isTraining}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-amber-500 text-white font-medium disabled:opacity-50"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isTraining ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              {isTraining ? "Training..." : "Train Models"}
            </motion.button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
          {[
            { label: "Actions", value: stats.totalActions, icon: Activity, color: "purple" },
            { label: "Patterns", value: patterns.length, icon: Target, color: "amber" },
            { label: "Prefs", value: preferences.length, icon: Settings, color: "cyan" },
            { label: "Suggestions", value: stats.pendingSuggestions, icon: Lightbulb, color: "emerald" },
            { label: "Success", value: `${(stats.successRate * 100).toFixed(0)}%`, icon: CheckCircle, color: "green" },
            { label: "Engagement", value: `${(stats.engagement * 100).toFixed(0)}%`, icon: Heart, color: "rose" },
            { label: "Learned", value: stats.learnedPreferences, icon: GraduationCap, color: "blue" },
            { label: "Pattern", value: stats.dominantPattern.split(" ")[0], icon: User, color: "orange" }
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

      {/* Dominant Pattern Display */}
      {dominantPattern && (
        <motion.div
          className="bg-gradient-to-r from-purple-500/10 to-amber-500/10 rounded-2xl p-6 border border-purple-500/30"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/30 to-amber-500/30 flex items-center justify-center">
              <Crown className="w-8 h-8 text-amber-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-white">{dominantPattern.name}</h3>
              <p className="text-slate-400">{dominantPattern.description}</p>
              <div className="flex items-center gap-4 mt-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-500">Confidence:</span>
                  <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-purple-500 to-amber-500"
                      style={{ width: `${dominantPattern.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-amber-400">{(dominantPattern.confidence * 100).toFixed(0)}%</span>
                </div>
                <span className="text-xs text-slate-500">Frequency: {dominantPattern.frequency}</span>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {[
          { id: "patterns", label: "User Patterns", icon: Target },
          { id: "preferences", label: "Preferences", icon: Settings },
          { id: "suggestions", label: "Suggestions", icon: Lightbulb },
          { id: "models", label: "ML Models", icon: Brain }
        ].map((tab) => (
          <motion.button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as typeof activeTab)}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all whitespace-nowrap ${
              activeTab === tab.id
                ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
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
        {activeTab === "patterns" && (
          <motion.div
            key="patterns"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-amber-400" />
              Detected User Patterns
            </h3>

            <div className="grid grid-cols-2 gap-4">
              {patterns.map((pattern) => (
                <motion.div
                  key={pattern.id}
                  className={`p-4 rounded-xl border ${
                    pattern === dominantPattern
                      ? "bg-purple-500/10 border-purple-500/30"
                      : "bg-slate-900/50 border-slate-600"
                  }`}
                  whileHover={{ scale: 1.02 }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">{pattern.name}</span>
                    <span className="text-xs text-amber-400">{(pattern.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <p className="text-sm text-slate-400 mb-3">{pattern.description}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500">Actions:</span>
                    {pattern.actions.map(action => (
                      <span key={action} className="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-300">
                        {action}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs text-slate-500">Adaptations:</span>
                    {pattern.adaptations.map(adj => (
                      <span key={adj} className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300">
                        {adj}
                      </span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === "preferences" && (
          <motion.div
            key="preferences"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-cyan-400" />
              Learned Preferences
            </h3>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {preferences.map((pref) => (
                <motion.div
                  key={pref.id}
                  className="p-3 bg-slate-900/50 rounded-lg border border-slate-600 flex items-center justify-between"
                  whileHover={{ scale: 1.01 }}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      pref.learned ? "bg-emerald-500/20" : "bg-slate-700"
                    }`}>
                      {pref.learned ? (
                        <GraduationCap className="w-4 h-4 text-emerald-400" />
                      ) : (
                        <Settings className="w-4 h-4 text-slate-400" />
                      )}
                    </div>
                    <div>
                      <div className="text-white text-sm">{pref.category}.{pref.key}</div>
                      <div className="text-xs text-slate-500">
                        {typeof pref.value === "boolean" ? (pref.value ? "Yes" : "No") : String(pref.value)}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-amber-400">{(pref.confidence * 100).toFixed(0)}%</span>
                    {pref.learned && (
                      <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300">Learned</span>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {activeTab === "suggestions" && (
          <motion.div
            key="suggestions"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700"
          >
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-amber-400" />
              Adaptation Suggestions
            </h3>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {suggestions.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  <Lightbulb className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No suggestions yet. Keep using the system!</p>
                </div>
              ) : (
                suggestions.map((suggestion) => (
                  <motion.div
                    key={suggestion.id}
                    className={`p-3 rounded-lg border flex items-center justify-between ${
                      suggestion.implemented
                        ? "bg-emerald-500/10 border-emerald-500/30"
                        : "bg-slate-900/50 border-slate-600"
                    }`}
                    whileHover={{ scale: 1.01 }}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        suggestion.impact === "positive" ? "bg-green-500/20" : "bg-amber-500/20"
                      }`}>
                        {suggestion.implemented ? (
                          <CheckCircle className="w-4 h-4 text-emerald-400" />
                        ) : (
                          <Lightbulb className="w-4 h-4 text-amber-400" />
                        )}
                      </div>
                      <div>
                        <div className="text-white text-sm capitalize">{suggestion.type}</div>
                        <div className="text-xs text-slate-500">{suggestion.reason}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-amber-400">{(suggestion.confidence * 100).toFixed(0)}%</span>
                      {!suggestion.implemented && (
                        <motion.button
                          onClick={() => handleImplementSuggestion(suggestion.id)}
                          className="text-xs px-2 py-1 rounded bg-emerald-500/20 text-emerald-300"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          Apply
                        </motion.button>
                      )}
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        )}

        {activeTab === "models" && (
          <motion.div
            key="models"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-4"
          >
            {models.map((model) => (
              <motion.div
                key={model.name}
                className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700"
                whileHover={{ scale: 1.01 }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500/30 to-cyan-500/30 flex items-center justify-center">
                      <Brain className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <h4 className="text-white font-medium">{model.name}</h4>
                      <div className="text-xs text-slate-500">v{model.version}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-emerald-400">{(model.accuracy * 100).toFixed(1)}%</div>
                    <div className="text-xs text-slate-500">Accuracy</div>
                  </div>
                </div>

                {/* Training Progress */}
                {isTraining && trainingProgress[model.name] !== undefined && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                      <span>Training...</span>
                      <span>{trainingProgress[model.name]}%</span>
                    </div>
                    <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-gradient-to-r from-purple-500 to-cyan-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${trainingProgress[model.name]}%` }}
                      />
                    </div>
                  </div>
                )}

                <div className="flex items-center gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <Database className="w-4 h-4 text-cyan-400" />
                    <span className="text-slate-400">{model.trainingExamples.toLocaleString()} examples</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-purple-400" />
                    <span className="text-slate-400">{model.features} features</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-amber-400" />
                    <span className="text-slate-400">
                      Last: {new Date(model.lastTrained).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}

            {/* Neural Network Visualization */}
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
              <h4 className="text-white font-medium mb-4 flex items-center gap-2">
                <Network className="w-5 h-5 text-purple-400" />
                Neural Network Architecture
              </h4>

              <div className="flex items-center justify-between gap-4">
                {engine.getNNLayers().map((layer, idx) => (
                  <div key={layer.name} className="flex items-center">
                    <motion.div
                      className="p-4 bg-slate-900/50 rounded-xl border border-slate-600 text-center min-w-[100px]"
                      whileHover={{ scale: 1.05 }}
                    >
                      <div className="text-2xl font-bold text-cyan-400">{layer.neurons}</div>
                      <div className="text-xs text-white">{layer.name}</div>
                      <div className="text-xs text-slate-500 mt-1">{layer.activation}</div>
                    </motion.div>
                    {idx < engine.getNNLayers().length - 1 && (
                      <div className="flex flex-col items-center mx-2">
                        {Array.from({ length: 3 }).map((_, i) => (
                          <motion.div
                            key={i}
                            className="w-8 h-0.5 bg-purple-500/30 my-1"
                            initial={{ scaleX: 0 }}
                            animate={{ scaleX: 1 }}
                            transition={{ delay: idx * 0.1 + i * 0.05 }}
                          />
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Session Info */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">Current Session</h3>
            <p className="text-sm text-slate-500 font-mono">{stats.sessionId}</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-400">
              Duration: {Math.floor(stats.duration / 60000)}m {Math.floor((stats.duration % 60000) / 1000)}s
            </div>
            <div className="text-sm text-slate-400">
              Actions: {stats.sessionActions} this session
            </div>
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
  UserLearningEngine,
  UserLearningEngineComponent
};
