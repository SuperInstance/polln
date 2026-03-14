"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  TrendingUp,
  Target,
  Clock,
  Zap,
  Sparkles,
  BarChart3,
  Activity,
  Lightbulb,
  Trophy,
  Star,
  Heart,
  Users,
  Settings,
  RefreshCw,
  Download,
  Upload,
  Eye,
  LineChart,
  PieChart,
  TrendingDown,
  AlertCircle,
  CheckCircle2,
  Info,
  Gauge,
} from "lucide-react";

// ============================================================================
// ML USER ACTION TRACKER
// Learns from user actions to improve the system
// Provides insights and recommendations
// ============================================================================

type ActionType = 
  | "click"
  | "scroll"
  | "hover"
  | "answer"
  | "hint_used"
  | "mode_switch"
  | "pause"
  | "skip"
  | "replay"
  | "correct"
  | "incorrect"
  | "streak_achieved"
  | "level_up"
  | "achievement_unlocked"
  | "session_start"
  | "session_end"
  | "page_view"
  | "feature_used";

interface UserAction {
  id: string;
  type: ActionType;
  timestamp: number;
  context: Record<string, unknown>;
  sessionId: string;
  userId?: string;
  metadata?: Record<string, unknown>;
}

interface LearningPattern {
  id: string;
  pattern: string;
  confidence: number;
  occurrences: number;
  lastSeen: number;
  suggestions: string[];
  category: "engagement" | "difficulty" | "preference" | "timing" | "learning_style";
}

interface UserInsight {
  id: string;
  type: "strength" | "weakness" | "opportunity" | "recommendation";
  title: string;
  description: string;
  actionable: boolean;
  action?: string;
  priority: "low" | "medium" | "high";
  confidence: number;
}

interface SessionStats {
  startTime: number;
  totalActions: number;
  correctAnswers: number;
  incorrectAnswers: number;
  hintsUsed: number;
  averageResponseTime: number;
  streaksAchieved: number;
  levelUps: number;
  modePreferences: Record<string, number>;
  featureUsage: Record<string, number>;
  engagementScore: number;
  learningVelocity: number;
}

interface MLModelData {
  weights: Record<string, number>;
  biases: Record<string, number>;
  features: string[];
  lastUpdated: number;
  version: string;
}

// ============================================================================
// ML USER ACTION TRACKER COMPONENT
// ============================================================================

interface MLUserActionTrackerProps {
  onPatternDetected?: (pattern: LearningPattern) => void;
  onInsightGenerated?: (insight: UserInsight) => void;
  onModelUpdate?: (model: MLModelData) => void;
  enableRealTimeTracking?: boolean;
  debugMode?: boolean;
}

export function MLUserActionTracker({
  onPatternDetected,
  onInsightGenerated,
  onModelUpdate,
  enableRealTimeTracking = true,
  debugMode = false,
}: MLUserActionTrackerProps) {
  // State
  const [actions, setActions] = useState<UserAction[]>([]);
  const [patterns, setPatterns] = useState<LearningPattern[]>([]);
  const [insights, setInsights] = useState<UserInsight[]>([]);
  const [sessionStats, setSessionStats] = useState<SessionStats>({
    startTime: Date.now(),
    totalActions: 0,
    correctAnswers: 0,
    incorrectAnswers: 0,
    hintsUsed: 0,
    averageResponseTime: 0,
    streaksAchieved: 0,
    levelUps: 0,
    modePreferences: {},
    featureUsage: {},
    engagementScore: 0,
    learningVelocity: 0,
  });
  const [modelData, setModelData] = useState<MLModelData>({
    weights: {},
    biases: {},
    features: [],
    lastUpdated: Date.now(),
    version: "1.0.0",
  });
  const [isTracking, setIsTracking] = useState(enableRealTimeTracking);

  // Refs for timing
  const lastActionTimeRef = useRef<number>(Date.now());
  const responseTimesRef = useRef<number[]>([]);

  // Session ID
  const sessionId = useRef(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  // ============================================================================
  // ACTION TRACKING
  // ============================================================================

  const trackAction = useCallback((type: ActionType, context: Record<string, unknown> = {}) => {
    if (!isTracking) return;

    const now = Date.now();
    const responseTime = now - lastActionTimeRef.current;
    lastActionTimeRef.current = now;

    const action: UserAction = {
      id: `action_${now}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      timestamp: now,
      context,
      sessionId: sessionId.current,
    };

    // Track response times for answers
    if (type === "correct" || type === "incorrect") {
      responseTimesRef.current.push(responseTime);
    }

    setActions(prev => [...prev, action]);
    setSessionStats(prev => {
      const newStats = { ...prev, totalActions: prev.totalActions + 1 };

      // Update specific counters
      if (type === "correct") newStats.correctAnswers = prev.correctAnswers + 1;
      if (type === "incorrect") newStats.incorrectAnswers = prev.incorrectAnswers + 1;
      if (type === "hint_used") newStats.hintsUsed = prev.hintsUsed + 1;
      if (type === "streak_achieved") newStats.streaksAchieved = prev.streaksAchieved + 1;
      if (type === "level_up") newStats.levelUps = prev.levelUps + 1;

      // Track mode preferences
      if (type === "mode_switch" && context.mode) {
        newStats.modePreferences = {
          ...prev.modePreferences,
          [context.mode as string]: (prev.modePreferences[context.mode as string] || 0) + 1,
        };
      }

      // Track feature usage
      if (type === "feature_used" && context.feature) {
        newStats.featureUsage = {
          ...prev.featureUsage,
          [context.feature as string]: (prev.featureUsage[context.feature as string] || 0) + 1,
        };
      }

      // Calculate engagement score
      newStats.engagementScore = calculateEngagementScore(newStats, actions);

      // Calculate learning velocity
      newStats.learningVelocity = calculateLearningVelocity(newStats, responseTimesRef.current);

      // Calculate average response time
      if (responseTimesRef.current.length > 0) {
        newStats.averageResponseTime = responseTimesRef.current.reduce((a, b) => a + b, 0) / responseTimesRef.current.length;
      }

      return newStats;
    });

    // Analyze for patterns
    analyzePatterns(action);

    return action;
  }, [isTracking, actions]);

  // ============================================================================
  // PATTERN ANALYSIS
  // ============================================================================

  const analyzePatterns = useCallback((newAction: UserAction) => {
    const recentActions = actions.slice(-50);
    const allActions = [...recentActions, newAction];

    // Pattern: Quick correct answers indicate mastery
    if (newAction.type === "correct") {
      const recentCorrect = allActions.filter(a => 
        a.type === "correct" && 
        a.timestamp > newAction.timestamp - 60000
      );
      if (recentCorrect.length >= 3) {
        const pattern: LearningPattern = {
          id: "pattern_mastery",
          pattern: "rapid_correct_sequence",
          confidence: 0.85,
          occurrences: recentCorrect.length,
          lastSeen: newAction.timestamp,
          suggestions: ["Consider increasing difficulty", "Introduce advanced concepts"],
          category: "learning_style",
        };
        addPattern(pattern);
      }
    }

    // Pattern: Hint usage indicates struggle
    if (newAction.type === "hint_used") {
      const recentHints = allActions.filter(a => 
        a.type === "hint_used" && 
        a.timestamp > newAction.timestamp - 120000
      );
      if (recentHints.length >= 2) {
        const pattern: LearningPattern = {
          id: "pattern_struggle",
          pattern: "frequent_hint_usage",
          confidence: 0.75,
          occurrences: recentHints.length,
          lastSeen: newAction.timestamp,
          suggestions: ["Provide more foundational content", "Offer simpler examples"],
          category: "difficulty",
        };
        addPattern(pattern);
      }
    }

    // Pattern: Mode switching indicates exploration
    if (newAction.type === "mode_switch") {
      const recentSwitches = allActions.filter(a => 
        a.type === "mode_switch" && 
        a.timestamp > newAction.timestamp - 300000
      );
      if (recentSwitches.length >= 3) {
        const pattern: LearningPattern = {
          id: "pattern_exploration",
          pattern: "frequent_mode_switching",
          confidence: 0.70,
          occurrences: recentSwitches.length,
          lastSeen: newAction.timestamp,
          suggestions: ["User is exploring - provide variety", "Consider personalized learning path"],
          category: "engagement",
        };
        addPattern(pattern);
      }
    }

    // Pattern: Streak achievement indicates engagement
    if (newAction.type === "streak_achieved") {
      const pattern: LearningPattern = {
        id: "pattern_engaged",
        pattern: "streak_achievement",
        confidence: 0.90,
        occurrences: sessionStats.streaksAchieved,
        lastSeen: newAction.timestamp,
        suggestions: ["User is highly engaged", "Maintain momentum with challenges"],
        category: "engagement",
      };
      addPattern(pattern);
    }

    // Generate insights based on patterns
    generateInsights();
  }, [actions, sessionStats.streaksAchieved]);

  // ============================================================================
  // INSIGHT GENERATION
  // ============================================================================

  const generateInsights = useCallback(() => {
    const newInsights: UserInsight[] = [];

    // Engagement insight
    if (sessionStats.engagementScore > 80) {
      newInsights.push({
        id: "insight_high_engagement",
        type: "strength",
        title: "High Engagement Detected",
        description: "User is highly engaged with the content. Consider offering advanced challenges.",
        actionable: true,
        action: "Increase difficulty level",
        priority: "medium",
        confidence: 0.85,
      });
    }

    // Learning velocity insight
    if (sessionStats.learningVelocity > 0.8) {
      newInsights.push({
        id: "insight_fast_learner",
        type: "strength",
        title: "Fast Learner",
        description: "User is learning quickly! They may benefit from accelerated content.",
        actionable: true,
        action: "Offer skip-ahead options",
        priority: "high",
        confidence: 0.80,
      });
    }

    // Hint overuse insight
    if (sessionStats.hintsUsed > sessionStats.correctAnswers * 0.5) {
      newInsights.push({
        id: "insight_hint_dependency",
        type: "weakness",
        title: "Hint Dependency",
        description: "User relies heavily on hints. Consider providing more foundational support.",
        actionable: true,
        action: "Show introductory content",
        priority: "high",
        confidence: 0.75,
      });
    }

    // Response time insight
    if (sessionStats.averageResponseTime > 30000) {
      newInsights.push({
        id: "insight_slow_responses",
        type: "opportunity",
        title: "Extended Thinking Time",
        description: "User takes time to respond. This may indicate deep thinking or confusion.",
        actionable: true,
        action: "Offer optional hints earlier",
        priority: "medium",
        confidence: 0.70,
      });
    }

    // Mode preference insight
    const preferredMode = Object.entries(sessionStats.modePreferences)
      .sort((a, b) => b[1] - a[1])[0];
    if (preferredMode && preferredMode[1] > 5) {
      newInsights.push({
        id: "insight_mode_preference",
        type: "preference",
        title: `Prefers ${preferredMode[0]} Mode`,
        description: `User frequently uses ${preferredMode[0]} mode. Consider personalizing experience.`,
        actionable: true,
        action: `Set ${preferredMode[0]} as default`,
        priority: "low",
        confidence: 0.85,
      });
    }

    setInsights(newInsights);
    newInsights.forEach(insight => onInsightGenerated?.(insight));
  }, [sessionStats, onInsightGenerated]);

  // ============================================================================
  // ML MODEL UPDATES
  // ============================================================================

  const updateModel = useCallback(() => {
    // Simple model update based on user behavior
    const newWeights = { ...modelData.weights };
    const newBiases = { ...modelData.biases };

    // Update weights based on patterns
    patterns.forEach(pattern => {
      const featureName = `pattern_${pattern.pattern}`;
      if (!newWeights[featureName]) {
        newWeights[featureName] = 0.5;
      }
      // Adjust weight based on confidence and occurrences
      newWeights[featureName] = newWeights[featureName] * 0.9 + pattern.confidence * 0.1;
    });

    // Update biases based on session stats
    newBiases["engagement_bias"] = sessionStats.engagementScore / 100;
    newBiases["velocity_bias"] = sessionStats.learningVelocity;
    newBiases["accuracy_bias"] = sessionStats.correctAnswers / Math.max(1, sessionStats.correctAnswers + sessionStats.incorrectAnswers);

    const newModel: MLModelData = {
      weights: newWeights,
      biases: newBiases,
      features: [...new Set([...modelData.features, ...Object.keys(newWeights)])],
      lastUpdated: Date.now(),
      version: modelData.version,
    };

    setModelData(newModel);
    onModelUpdate?.(newModel);
  }, [modelData, patterns, sessionStats, onModelUpdate]);

  // ============================================================================
  // HELPER FUNCTIONS
  // ============================================================================

  const addPattern = (pattern: LearningPattern) => {
    setPatterns(prev => {
      const existing = prev.find(p => p.id === pattern.id);
      if (existing) {
        return prev.map(p => p.id === pattern.id ? { ...pattern, occurrences: p.occurrences + 1 } : p);
      }
      return [...prev, pattern];
    });
    onPatternDetected?.(pattern);
  };

  const calculateEngagementScore = (stats: SessionStats, historicalActions: UserAction[]): number => {
    const accuracy = stats.correctAnswers / Math.max(1, stats.correctAnswers + stats.incorrectAnswers);
    const hintPenalty = stats.hintsUsed * 5;
    const streakBonus = stats.streaksAchieved * 10;
    const actionBonus = Math.min(stats.totalActions * 0.5, 20);

    let score = (accuracy * 50) + streakBonus + actionBonus - hintPenalty;
    return Math.max(0, Math.min(100, score));
  };

  const calculateLearningVelocity = (stats: SessionStats, responseTimes: number[]): number => {
    if (stats.correctAnswers === 0) return 0;
    
    const avgTime = responseTimes.length > 0 
      ? responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length 
      : 30000;
    
    const accuracy = stats.correctAnswers / Math.max(1, stats.correctAnswers + stats.incorrectAnswers);
    const speedFactor = Math.max(0, 1 - (avgTime / 60000)); // Normalize to 0-1 based on 1 min max
    
    return accuracy * 0.6 + speedFactor * 0.4;
  };

  // ============================================================================
  // EFFECTS
  // ============================================================================

  // Periodic model update
  useEffect(() => {
    const interval = setInterval(updateModel, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [updateModel]);

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="bg-gradient-to-br from-slate-900 via-indigo-900/20 to-slate-900 rounded-2xl border border-indigo-500/30 overflow-hidden">
      {/* Header */}
      <div className="bg-slate-800/50 px-4 py-3 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Brain className="w-5 h-5 text-indigo-400" />
            <span className="font-bold text-white">ML Learning Engine</span>
            <div className={`px-2 py-0.5 rounded-full text-xs ${
              isTracking ? "bg-green-500/20 text-green-400" : "bg-slate-600 text-slate-400"
            }`}>
              {isTracking ? "Learning" : "Paused"}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsTracking(!isTracking)}
              className="p-2 text-slate-400 hover:text-white transition-colors"
            >
              {isTracking ? <Eye className="w-4 h-4" /> : <Activity className="w-4 h-4" />}
            </button>
            <button
              onClick={updateModel}
              className="p-2 text-slate-400 hover:text-white transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-800/50 rounded-xl p-3">
          <div className="flex items-center gap-2 text-slate-400 mb-1">
            <Activity className="w-4 h-4" />
            <span className="text-xs">Total Actions</span>
          </div>
          <div className="text-2xl font-bold text-white">{sessionStats.totalActions}</div>
        </div>

        <div className="bg-slate-800/50 rounded-xl p-3">
          <div className="flex items-center gap-2 text-slate-400 mb-1">
            <Target className="w-4 h-4" />
            <span className="text-xs">Accuracy</span>
          </div>
          <div className="text-2xl font-bold text-green-400">
            {Math.round((sessionStats.correctAnswers / Math.max(1, sessionStats.correctAnswers + sessionStats.incorrectAnswers)) * 100)}%
          </div>
        </div>

        <div className="bg-slate-800/50 rounded-xl p-3">
          <div className="flex items-center gap-2 text-slate-400 mb-1">
            <Zap className="w-4 h-4" />
            <span className="text-xs">Engagement</span>
          </div>
          <div className="text-2xl font-bold text-purple-400">{Math.round(sessionStats.engagementScore)}</div>
        </div>

        <div className="bg-slate-800/50 rounded-xl p-3">
          <div className="flex items-center gap-2 text-slate-400 mb-1">
            <Gauge className="w-4 h-4" />
            <span className="text-xs">Velocity</span>
          </div>
          <div className="text-2xl font-bold text-cyan-400">{sessionStats.learningVelocity.toFixed(2)}</div>
        </div>
      </div>

      {/* Detected Patterns */}
      <div className="px-4 pb-4">
        <div className="bg-slate-800/30 rounded-xl p-4">
          <h4 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
            <Lightbulb className="w-4 h-4 text-yellow-400" />
            Detected Patterns ({patterns.length})
          </h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            <AnimatePresence>
              {patterns.map(pattern => (
                <motion.div
                  key={pattern.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center justify-between p-2 bg-slate-900/50 rounded-lg"
                >
                  <div>
                    <span className="text-sm text-white">{pattern.pattern}</span>
                    <span className="text-xs text-slate-500 ml-2">({pattern.category})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-xs text-indigo-400">{(pattern.confidence * 100).toFixed(0)}%</div>
                    <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-indigo-500" 
                        style={{ width: `${pattern.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
            {patterns.length === 0 && (
              <div className="text-center py-4 text-slate-500 text-sm">
                Interact with the game to detect patterns...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="px-4 pb-4">
        <div className="bg-slate-800/30 rounded-xl p-4">
          <h4 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-400" />
            AI Insights ({insights.length})
          </h4>
          <div className="space-y-2">
            {insights.map(insight => (
              <motion.div
                key={insight.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-3 rounded-lg border ${
                  insight.type === "strength" ? "border-green-500/30 bg-green-500/10" :
                  insight.type === "weakness" ? "border-red-500/30 bg-red-500/10" :
                  insight.type === "opportunity" ? "border-yellow-500/30 bg-yellow-500/10" :
                  "border-blue-500/30 bg-blue-500/10"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-white">{insight.title}</span>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    insight.priority === "high" ? "bg-red-500/20 text-red-400" :
                    insight.priority === "medium" ? "bg-yellow-500/20 text-yellow-400" :
                    "bg-slate-600 text-slate-400"
                  }`}>
                    {insight.priority}
                  </span>
                </div>
                <p className="text-xs text-slate-400">{insight.description}</p>
                {insight.actionable && insight.action && (
                  <button className="mt-2 text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
                    → {insight.action}
                  </button>
                )}
              </motion.div>
            ))}
            {insights.length === 0 && (
              <div className="text-center py-4 text-slate-500 text-sm">
                Play more to generate insights...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Debug Panel */}
      {debugMode && (
        <div className="px-4 pb-4">
          <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
            <h4 className="text-sm font-medium text-slate-300 mb-3">Debug: Model Weights</h4>
            <pre className="text-xs text-slate-400 overflow-auto max-h-32">
              {JSON.stringify(modelData, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {/* Export Actions */}
      <div className="px-4 pb-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              const data = JSON.stringify({ actions, patterns, insights, sessionStats, modelData }, null, 2);
              const blob = new Blob([data], { type: "application/json" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `ml_data_${Date.now()}.json`;
              a.click();
            }}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg text-slate-300 text-sm"
          >
            <Download className="w-4 h-4" />
            Export Data
          </button>
          <button
            onClick={trackAction.bind(null, "session_start", { source: "ml_tracker" })}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-500/20 rounded-lg text-indigo-400 text-sm"
          >
            <Upload className="w-4 h-4" />
            Test Action
          </button>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// EXPORT HOOK FOR EXTERNAL USE
// ============================================================================

export function useMLTracker() {
  const [tracker] = useState(() => new MLUserActionTracker({}));

  return {
    trackAction: tracker.trackAction,
    getStats: () => tracker.sessionStats,
    getPatterns: () => tracker.patterns,
    getInsights: () => tracker.insights,
  };
}

export default MLUserActionTracker;
