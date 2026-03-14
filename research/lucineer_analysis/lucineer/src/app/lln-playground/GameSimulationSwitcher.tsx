"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Gamepad2,
  Eye,
  BookOpen,
  Zap,
  Play,
  Pause,
  RotateCcw,
  ChevronRight,
  Layers,
  Brain,
  Sparkles,
  Target,
  Trophy,
  Clock,
  Star,
  Heart,
  Users,
  Settings,
  Volume2,
  VolumeX,
  Maximize2,
  Minimize2,
  Info,
  Lightbulb,
  Rocket,
  GraduationCap,
  Baby,
  Flame,
  Gauge,
  Timer,
  CheckCircle2,
  XCircle,
  SkipForward,
  Rewind,
} from "lucide-react";

// ============================================================================
// GAME/SIMULATION SWITCHER
// Easy toggle between Play (active) and Watch (simulation) modes
// Designed for all ages with intuitive controls
// ============================================================================

type ViewMode = "play" | "watch" | "learn" | "challenge";
type AgeGroup = "child" | "teen" | "adult";
type SimulationSpeed = "slow" | "normal" | "fast";

interface GameStep {
  id: string;
  type: "explanation" | "action" | "question" | "result" | "celebration";
  title: string;
  content: string;
  visual?: string;
  duration: number; // in milliseconds
}

interface LearningPath {
  id: string;
  name: string;
  description: string;
  icon: typeof Gamepad2;
  color: string;
  steps: GameStep[];
  ageAdaptation: Record<AgeGroup, { language: string; depth: string }>;
}

// Pre-defined learning paths
const LEARNING_PATHS: LearningPath[] = [
  {
    id: "pattern-recognition",
    name: "Pattern Recognition",
    description: "Learn how AI finds patterns in data",
    icon: Sparkles,
    color: "purple",
    steps: [
      {
        id: "intro",
        type: "explanation",
        title: "What are Patterns?",
        content: "Patterns are things that repeat in a predictable way. AI learns by finding these patterns!",
        visual: "🔢🔤🔣",
        duration: 3000,
      },
      {
        id: "example1",
        type: "action",
        title: "Look at This Pattern",
        content: "2, 4, 6, 8, 10... What comes next? The pattern is 'add 2'!",
        visual: "2️⃣→4️⃣→6️⃣→8️⃣→🔟→❓",
        duration: 4000,
      },
      {
        id: "question1",
        type: "question",
        title: "Your Turn!",
        content: "What comes next: 5, 10, 15, 20, ___?",
        visual: "5️⃣→🔟→1️⃣5️⃣→2️⃣0️⃣→❓",
        duration: 5000,
      },
      {
        id: "result1",
        type: "result",
        title: "Great Job!",
        content: "The answer is 25! The pattern is 'add 5'. AI finds patterns just like this!",
        duration: 3000,
      },
    ],
    ageAdaptation: {
      child: { language: "simple", depth: "basic" },
      teen: { language: "intermediate", depth: "detailed" },
      adult: { language: "technical", depth: "comprehensive" },
    },
  },
  {
    id: "neural-basics",
    name: "How Neural Networks Learn",
    description: "Discover the basics of how AI learns from examples",
    icon: Brain,
    color: "blue",
    steps: [
      {
        id: "intro",
        type: "explanation",
        title: "Neural Networks",
        content: "A neural network is like a brain that learns from examples. It gets smarter with practice!",
        visual: "🧠⚡🔮",
        duration: 3000,
      },
      {
        id: "example1",
        type: "action",
        title: "Learning from Examples",
        content: "Show a neural network many pictures of cats, and it learns what a cat looks like!",
        visual: "🐱📸🐱📸🐱📸",
        duration: 4000,
      },
      {
        id: "question1",
        type: "question",
        title: "Think About It",
        content: "If you showed a neural network 1000 pictures of dogs, what would it learn?",
        duration: 5000,
      },
      {
        id: "result1",
        type: "result",
        title: "Exactly Right!",
        content: "It would learn to recognize dogs! More examples = better learning!",
        duration: 3000,
      },
    ],
    ageAdaptation: {
      child: { language: "simple", depth: "basic" },
      teen: { language: "intermediate", depth: "detailed" },
      adult: { language: "technical", depth: "comprehensive" },
    },
  },
  {
    id: "training-data",
    name: "Training Data Matters",
    description: "Learn why the data we give AI is so important",
    icon: Target,
    color: "green",
    steps: [
      {
        id: "intro",
        type: "explanation",
        title: "Training Data",
        content: "AI learns from 'training data' - examples we give it. Good data = smart AI!",
        visual: "📊✨🎯",
        duration: 3000,
      },
      {
        id: "example1",
        type: "action",
        title: "Good vs Bad Data",
        content: "If we show only pictures of cats to learn about dogs, the AI will be confused!",
        visual: "🐱❌🐶 | 🐱✅🐶✅",
        duration: 4000,
      },
      {
        id: "question1",
        type: "question",
        title: "Your Choice",
        content: "What makes good training data for teaching AI about animals?",
        duration: 5000,
      },
      {
        id: "result1",
        type: "result",
        title: "Perfect!",
        content: "Diverse, accurate, and balanced data helps AI learn correctly!",
        duration: 3000,
      },
    ],
    ageAdaptation: {
      child: { language: "simple", depth: "basic" },
      teen: { language: "intermediate", depth: "detailed" },
      adult: { language: "technical", depth: "comprehensive" },
    },
  },
];

// ============================================================================
// GAME SIMULATION SWITCHER COMPONENT
// ============================================================================

interface GameSimulationSwitcherProps {
  ageGroup: AgeGroup;
  onComplete?: (pathId: string, score: number) => void;
  onProgress?: (stepId: string, progress: number) => void;
}

export function GameSimulationSwitcher({
  ageGroup,
  onComplete,
  onProgress,
}: GameSimulationSwitcherProps) {
  // State
  const [viewMode, setViewMode] = useState<ViewMode>("play");
  const [selectedPath, setSelectedPath] = useState<LearningPath | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [speed, setSpeed] = useState<SimulationSpeed>("normal");
  const [score, setScore] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [showControls, setShowControls] = useState(true);
  const [soundEnabled, setSoundEnabled] = useState(true);

  // Speed multipliers
  const speedMultipliers: Record<SimulationSpeed, number> = {
    slow: 1.5,
    normal: 1,
    fast: 0.5,
  };

  // Get current path and step
  const currentStep = selectedPath?.steps[currentStepIndex];

  // Start learning path
  const startPath = useCallback((path: LearningPath) => {
    setSelectedPath(path);
    setCurrentStepIndex(0);
    setScore(0);
    setAnswers({});
    setIsRunning(true);
  }, []);

  // Next step
  const nextStep = useCallback(() => {
    if (!selectedPath) return;

    if (currentStepIndex < selectedPath.steps.length - 1) {
      setCurrentStepIndex(prev => prev + 1);
    } else {
      // Path complete
      setIsRunning(false);
      onComplete?.(selectedPath.id, score);
    }
  }, [selectedPath, currentStepIndex, score, onComplete]);

  // Previous step
  const prevStep = useCallback(() => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1);
    }
  }, [currentStepIndex]);

  // Auto-play in watch mode
  const autoPlay = useCallback(() => {
    if (viewMode !== "watch" || !isRunning || !currentStep) return;

    const duration = currentStep.duration * speedMultipliers[speed];
    const timer = setTimeout(() => {
      nextStep();
    }, duration);

    return () => clearTimeout(timer);
  }, [viewMode, isRunning, currentStep, speed, nextStep, speedMultipliers]);

  // Handle answer
  const handleAnswer = useCallback((answer: string) => {
    if (!currentStep) return;

    setAnswers(prev => ({ ...prev, [currentStep.id]: answer }));
    setScore(prev => prev + 10);
    onProgress?.(currentStep.id, 100);

    // In play mode, wait for user to click next
    // In watch mode, auto-advance
    if (viewMode === "watch") {
      setTimeout(nextStep, 1000);
    }
  }, [currentStep, viewMode, nextStep, onProgress]);

  // Mode colors
  const modeColors: Record<ViewMode, string> = {
    play: "from-purple-500 to-pink-500",
    watch: "from-blue-500 to-cyan-500",
    learn: "from-green-500 to-emerald-500",
    challenge: "from-orange-500 to-red-500",
  };

  return (
    <div className="bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="bg-slate-800/50 px-4 py-3 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Layers className="w-5 h-5 text-purple-400" />
            <span className="font-bold text-white">Learning Experience</span>
          </div>

          {/* View Mode Switcher */}
          <div className="flex items-center gap-1 bg-slate-900/50 rounded-lg p-1">
            {[
              { id: "play" as ViewMode, label: "Play", icon: Gamepad2, desc: "Interactive - You control the pace" },
              { id: "watch" as ViewMode, label: "Watch", icon: Eye, desc: "Simulation - Watch AI learn" },
              { id: "learn" as ViewMode, label: "Learn", icon: BookOpen, desc: "Educational - Deep explanations" },
            ].map(mode => (
              <button
                key={mode.id}
                onClick={() => setViewMode(mode.id)}
                className={`group relative flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all ${
                  viewMode === mode.id
                    ? `bg-gradient-to-r ${modeColors[mode.id]} text-white`
                    : "text-slate-400 hover:text-white hover:bg-slate-700"
                }`}
              >
                <mode.icon className="w-4 h-4" />
                {mode.label}
                <span className="absolute -bottom-8 left-1/2 -translate-x-1/2 px-2 py-1 bg-slate-800 text-xs text-slate-300 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                  {mode.desc}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="p-6 min-h-[400px]">
        {!selectedPath ? (
          /* Path Selection */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <div className="text-center mb-6">
              <h3 className="text-xl font-bold text-white mb-2">
                Choose Your Learning Adventure
              </h3>
              <p className="text-slate-400">
                {ageGroup === "child" && "Pick a fun topic to explore! 🎮"}
                {ageGroup === "teen" && "Select a learning path to begin 🧠"}
                {ageGroup === "adult" && "Choose a topic for in-depth learning 📚"}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {LEARNING_PATHS.map((path, index) => (
                <motion.button
                  key={path.id}
                  onClick={() => startPath(path)}
                  className={`p-6 rounded-xl border-2 text-left transition-all ${
                    `border-${path.color}-500/30 bg-${path.color}-500/10 hover:border-${path.color}-500/50`
                  }`}
                  style={{
                    borderColor: path.color === "purple" ? "rgba(168, 85, 247, 0.3)" :
                                path.color === "blue" ? "rgba(59, 130, 246, 0.3)" :
                                "rgba(34, 197, 94, 0.3)",
                    backgroundColor: path.color === "purple" ? "rgba(168, 85, 247, 0.1)" :
                                    path.color === "blue" ? "rgba(59, 130, 246, 0.1)" :
                                    "rgba(34, 197, 94, 0.1)",
                  }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`p-2 rounded-lg bg-${path.color}-500/20`}>
                      <path.icon className={`w-5 h-5 text-${path.color}-400`} />
                    </div>
                    <div>
                      <h4 className="font-semibold text-white">{path.name}</h4>
                      <p className="text-xs text-slate-500">{path.steps.length} steps</p>
                    </div>
                  </div>
                  <p className="text-sm text-slate-400">{path.description}</p>
                </motion.button>
              ))}
            </div>
          </motion.div>
        ) : (
          /* Active Learning */
          <AnimatePresence mode="wait">
            {currentStep && (
              <motion.div
                key={currentStep.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                {/* Progress Bar */}
                <div className="flex items-center gap-4">
                  <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                      initial={{ width: 0 }}
                      animate={{ width: `${((currentStepIndex + 1) / selectedPath.steps.length) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm text-slate-400">
                    {currentStepIndex + 1}/{selectedPath.steps.length}
                  </span>
                </div>

                {/* Step Content */}
                <div className="text-center py-8">
                  {/* Visual */}
                  {currentStep.visual && (
                    <motion.div
                      className="text-4xl mb-6"
                      animate={{ scale: [1, 1.1, 1] }}
                      transition={{ duration: 1, repeat: Infinity }}
                    >
                      {currentStep.visual}
                    </motion.div>
                  )}

                  {/* Title */}
                  <h3 className="text-2xl font-bold text-white mb-4">
                    {currentStep.title}
                  </h3>

                  {/* Content */}
                  <p className="text-lg text-slate-300 max-w-2xl mx-auto">
                    {currentStep.content}
                  </p>

                  {/* Type-specific content */}
                  {currentStep.type === "question" && viewMode === "play" && (
                    <div className="mt-6 flex justify-center gap-4">
                      <motion.button
                        onClick={() => handleAnswer("correct")}
                        className="px-6 py-3 bg-green-500/20 border border-green-500/30 rounded-xl text-green-400 font-medium"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <CheckCircle2 className="w-5 h-5 inline mr-2" />
                        I Understand!
                      </motion.button>
                      <motion.button
                        onClick={() => handleAnswer("review")}
                        className="px-6 py-3 bg-blue-500/20 border border-blue-500/30 rounded-xl text-blue-400 font-medium"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <BookOpen className="w-5 h-5 inline mr-2" />
                        Explain Again
                      </motion.button>
                    </div>
                  )}

                  {currentStep.type === "result" && (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/20 rounded-full text-green-400 mt-4"
                    >
                      <Trophy className="w-5 h-5" />
                      +10 points!
                    </motion.div>
                  )}
                </div>

                {/* Controls */}
                <div className="flex items-center justify-center gap-4">
                  <motion.button
                    onClick={prevStep}
                    disabled={currentStepIndex === 0}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg text-slate-300 disabled:opacity-50"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Rewind className="w-4 h-4" />
                    Previous
                  </motion.button>

                  <motion.button
                    onClick={() => setIsRunning(!isRunning)}
                    className={`flex items-center gap-2 px-6 py-2 rounded-lg text-white font-medium bg-gradient-to-r ${modeColors[viewMode]}`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    {isRunning ? "Pause" : "Play"}
                  </motion.button>

                  <motion.button
                    onClick={nextStep}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg text-slate-300"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Next
                    <SkipForward className="w-4 h-4" />
                  </motion.button>
                </div>

                {/* Back to Paths */}
                <div className="text-center mt-4">
                  <button
                    onClick={() => setSelectedPath(null)}
                    className="text-sm text-slate-500 hover:text-slate-300 transition-colors"
                  >
                    ← Choose Different Topic
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </div>

      {/* Footer Stats */}
      {selectedPath && (
        <div className="bg-slate-800/30 px-4 py-3 border-t border-slate-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <Star className="w-4 h-4 text-yellow-400" />
                <span className="text-yellow-400 font-medium">{score} points</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-slate-400" />
                <span className="text-slate-400">Mode: {viewMode}</span>
              </div>
            </div>

            {/* Speed Control for Watch Mode */}
            {viewMode === "watch" && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">Speed:</span>
                {(["slow", "normal", "fast"] as SimulationSpeed[]).map(s => (
                  <button
                    key={s}
                    onClick={() => setSpeed(s)}
                    className={`px-2 py-1 rounded text-xs ${
                      speed === s ? "bg-blue-500/20 text-blue-400" : "text-slate-500 hover:text-slate-300"
                    }`}
                  >
                    {s === "slow" ? "🐢" : s === "normal" ? "🚶" : "🏃"}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default GameSimulationSwitcher;
