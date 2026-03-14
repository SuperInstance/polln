"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play,
  Pause,
  SkipForward,
  RotateCcw,
  Zap,
  Eye,
  Gamepad2,
  Brain,
  Sparkles,
  Trophy,
  Clock,
  Users,
  Target,
  ChevronRight,
  Volume2,
  VolumeX,
  Settings,
  Maximize2,
  Minimize2,
  FastForward,
  Rewind,
  Circle,
  CheckCircle2,
  Timer,
  Star,
  Heart,
  Flame,
  IceCrystal,
  Sun,
  Moon,
  CloudRain,
  Wind,
} from "lucide-react";

// ============================================================================
// REAL-TIME GAME ENGINE
// Makes games feel instant with WebSocket-like updates
// Easy switch between Game (play) and Simulation (watch) modes
// ============================================================================

type GameMode = "play" | "simulate" | "learn" | "challenge";
type GameSpeed = "slow" | "normal" | "fast" | "turbo";
type AgeGroup = "child" | "teen" | "adult";

interface GameState {
  mode: GameMode;
  speed: GameSpeed;
  isRunning: boolean;
  score: number;
  level: number;
  streak: number;
  timeElapsed: number;
  hintsUsed: number;
  hintsAvailable: number;
  correctAnswers: number;
  totalQuestions: number;
  multiplier: number;
  combo: number;
  particles: Particle[];
  notifications: Notification[];
}

interface Particle {
  id: string;
  x: number;
  y: number;
  color: string;
  size: number;
  velocity: { x: number; y: number };
  life: number;
}

interface Notification {
  id: string;
  message: string;
  type: "success" | "info" | "warning" | "achievement";
  timestamp: number;
}

interface GameQuestion {
  id: string;
  type: "pattern" | "sequence" | "match" | "predict" | "create";
  difficulty: number;
  prompt: string;
  options?: string[];
  correctAnswer: string | string[];
  hint: string;
  explanation: string;
  timeLimit: number;
  points: number;
  culturalVariant?: Record<string, string>;
}

// Pre-defined questions for different age groups
const QUESTION_BANK: Record<AgeGroup, GameQuestion[]> = {
  child: [
    {
      id: "c1",
      type: "pattern",
      difficulty: 1,
      prompt: "What comes next? 🌞🌙🌞🌙🌞🌙___",
      options: ["🌞", "🌙", "⭐", "🌈"],
      correctAnswer: "🌙",
      hint: "Look at the pattern - sun, moon, sun, moon...",
      explanation: "The pattern repeats: sun, moon, sun, moon, sun, moon, then MOON!",
      timeLimit: 30,
      points: 100,
      culturalVariant: {
        JP: "日、月、日、月の次は？",
        ES: "Sol, luna, sol, luna..."
      }
    },
    {
      id: "c2",
      type: "match",
      difficulty: 1,
      prompt: "Which animal says 'woof'?",
      options: ["🐱 Cat", "🐶 Dog", "🐮 Cow", "🐷 Pig"],
      correctAnswer: "🐶 Dog",
      hint: "Think about what sound each animal makes!",
      explanation: "Dogs say 'woof' or 'bark'! Cats say 'meow', cows say 'moo', and pigs say 'oink'.",
      timeLimit: 20,
      points: 100,
    },
    {
      id: "c3",
      type: "sequence",
      difficulty: 2,
      prompt: "Complete the sequence: 2, 4, 6, 8, ___",
      options: ["9", "10", "12", "14"],
      correctAnswer: "10",
      hint: "Count by 2s! 2, 4, 6, 8...",
      explanation: "This is counting by 2s! 2, 4, 6, 8, 10!",
      timeLimit: 25,
      points: 150,
    },
    {
      id: "c4",
      type: "predict",
      difficulty: 2,
      prompt: "If you drop a ball, what will it do?",
      options: ["Float up", "Fall down", "Stay still", "Disappear"],
      correctAnswer: "Fall down",
      hint: "Think about gravity - what goes up must come down!",
      explanation: "Gravity pulls things down toward the Earth. That's why balls fall when you drop them!",
      timeLimit: 20,
      points: 150,
    },
    {
      id: "c5",
      type: "create",
      difficulty: 3,
      prompt: "Draw a pattern using: ⭐🌙✨",
      correctAnswer: ["⭐🌙✨", "🌙⭐✨", "✨🌙⭐"],
      hint: "Create any pattern you like with these symbols!",
      explanation: "Great pattern! You can make many different patterns with these symbols.",
      timeLimit: 60,
      points: 200,
    }
  ],
  teen: [
    {
      id: "t1",
      type: "pattern",
      difficulty: 3,
      prompt: "What's the next number: 1, 1, 2, 3, 5, 8, 13, ___?",
      options: ["18", "20", "21", "26"],
      correctAnswer: "21",
      hint: "Add the last two numbers together...",
      explanation: "This is the Fibonacci sequence! Each number is the sum of the two before it: 5+8=13, 8+13=21",
      timeLimit: 45,
      points: 200,
    },
    {
      id: "t2",
      type: "predict",
      difficulty: 3,
      prompt: "A neural network is trained on cat photos. What will it learn to recognize?",
      options: ["Dogs", "Cats", "Cars", "Nothing"],
      correctAnswer: "Cats",
      hint: "AI learns from the data it's given!",
      explanation: "Neural networks learn patterns from training data. Given cat photos, it learns to recognize cats!",
      timeLimit: 30,
      points: 200,
    },
    {
      id: "t3",
      type: "sequence",
      difficulty: 4,
      prompt: "Complete: 2³, 3³, 4³, 5³, ___",
      options: ["125", "150", "216", "256"],
      correctAnswer: "216",
      hint: "Calculate 6³...",
      explanation: "These are perfect cubes! 2³=8, 3³=27, 4³=64, 5³=125, 6³=216",
      timeLimit: 40,
      points: 250,
    },
    {
      id: "t4",
      type: "match",
      difficulty: 4,
      prompt: "Which algorithm would you use to group similar items?",
      options: ["Linear Search", "K-Means Clustering", "Binary Search", "Quick Sort"],
      correctAnswer: "K-Means Clustering",
      hint: "Think about 'clustering' things together...",
      explanation: "K-Means Clustering is an unsupervised learning algorithm that groups similar data points together!",
      timeLimit: 45,
      points: 300,
    }
  ],
  adult: [
    {
      id: "a1",
      type: "pattern",
      difficulty: 5,
      prompt: "In gradient descent, if the learning rate is too high, what happens?",
      options: ["Slow convergence", "Overshooting/divergence", "No change", "Faster convergence"],
      correctAnswer: "Overshooting/divergence",
      hint: "Think about taking steps that are too big...",
      explanation: "A high learning rate can cause the optimizer to overshoot the minimum and diverge instead of converging.",
      timeLimit: 60,
      points: 400,
    },
    {
      id: "a2",
      type: "predict",
      difficulty: 5,
      prompt: "What happens to a model's variance as you increase model complexity?",
      options: ["Decreases", "Stays same", "Increases", "Becomes zero"],
      correctAnswer: "Increases",
      hint: "Think about the bias-variance tradeoff...",
      explanation: "Higher model complexity leads to higher variance (overfitting risk) but lower bias. This is the classic bias-variance tradeoff.",
      timeLimit: 45,
      points: 400,
    },
    {
      id: "a3",
      type: "match",
      difficulty: 6,
      prompt: "Which activation function helps with vanishing gradients in deep networks?",
      options: ["Sigmoid", "Tanh", "ReLU", "Linear"],
      correctAnswer: "ReLU",
      hint: "Think about which function doesn't squash values to a small range...",
      explanation: "ReLU (Rectified Linear Unit) helps with vanishing gradients because it doesn't squash values like sigmoid or tanh, allowing gradients to flow better in deep networks.",
      timeLimit: 60,
      points: 500,
    }
  ]
};

// ============================================================================
// REAL-TIME GAME ENGINE COMPONENT
// ============================================================================

interface RealTimeGameEngineProps {
  ageGroup: AgeGroup;
  onScoreUpdate?: (score: number) => void;
  onAchievement?: (achievement: string) => void;
  onPatternDetected?: (pattern: string) => void;
}

export function RealTimeGameEngine({
  ageGroup,
  onScoreUpdate,
  onAchievement,
  onPatternDetected,
}: RealTimeGameEngineProps) {
  // Game state
  const [gameState, setGameState] = useState<GameState>({
    mode: "play",
    speed: "normal",
    isRunning: false,
    score: 0,
    level: 1,
    streak: 0,
    timeElapsed: 0,
    hintsUsed: 0,
    hintsAvailable: 3,
    correctAnswers: 0,
    totalQuestions: 0,
    multiplier: 1,
    combo: 0,
    particles: [],
    notifications: [],
  });

  const [currentQuestion, setCurrentQuestion] = useState<GameQuestion | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showHint, setShowHint] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);

  const questionTimerRef = useRef<NodeJS.Timeout | null>(null);
  const gameTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Get questions for current age group
  const questions = QUESTION_BANK[ageGroup];

  // Speed multipliers
  const speedMultipliers: Record<GameSpeed, number> = {
    slow: 2,
    normal: 1,
    fast: 0.5,
    turbo: 0.25,
  };

  // Start a new question
  const nextQuestion = useCallback(() => {
    const availableQuestions = questions.filter(q => q.difficulty <= gameState.level + 2);
    const question = availableQuestions[Math.floor(Math.random() * availableQuestions.length)];
    setCurrentQuestion(question);
    setSelectedAnswer(null);
    setShowHint(false);
    setShowExplanation(false);
    setTimeRemaining(question.timeLimit);
    setGameState(prev => ({ ...prev, totalQuestions: prev.totalQuestions + 1 }));

    // Start question timer
    if (questionTimerRef.current) clearInterval(questionTimerRef.current);
    questionTimerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev === null || prev <= 0) {
          // Time's up!
          handleTimeout();
          return null;
        }
        return prev - 1;
      });
    }, 1000 * speedMultipliers[gameState.speed]);
  }, [questions, gameState.level, gameState.speed]);

  // Handle timeout
  const handleTimeout = useCallback(() => {
    if (questionTimerRef.current) clearInterval(questionTimerRef.current);
    setGameState(prev => ({
      ...prev,
      streak: 0,
      combo: 0,
      multiplier: 1,
    }));
    setShowExplanation(true);
    
    // In simulate mode, auto-proceed
    if (gameState.mode === "simulate") {
      setTimeout(nextQuestion, 2000);
    }
  }, [gameState.mode, nextQuestion]);

  // Handle answer selection
  const handleAnswer = useCallback((answer: string) => {
    if (!currentQuestion || selectedAnswer !== null) return;

    setSelectedAnswer(answer);
    if (questionTimerRef.current) clearInterval(questionTimerRef.current);

    const isCorrect = Array.isArray(currentQuestion.correctAnswer)
      ? currentQuestion.correctAnswer.includes(answer)
      : answer === currentQuestion.correctAnswer;

    if (isCorrect) {
      const timeBonus = Math.floor((timeRemaining || 0) * 10);
      const streakBonus = Math.min(gameState.streak * 50, 500);
      const points = (currentQuestion.points + timeBonus + streakBonus) * gameState.multiplier;

      setGameState(prev => ({
        ...prev,
        score: prev.score + points,
        streak: prev.streak + 1,
        combo: prev.combo + 1,
        multiplier: Math.min(1 + prev.combo * 0.1, 3),
        correctAnswers: prev.correctAnswers + 1,
        level: Math.floor((prev.correctAnswers + 1) / 5) + 1,
      }));

      // Spawn celebration particles
      spawnParticles(10);

      // Add notification
      addNotification(`+${points} points! 🎉`, "success");

      // Check for achievements
      if (gameState.streak === 4) {
        onAchievement?.("5 Streak! 🔥");
        addNotification("Achievement: 5 Streak! 🔥", "achievement");
      }

      // Pattern detection for ML
      onPatternDetected?.(`correct_streak_${gameState.streak}`);

      onScoreUpdate?.(gameState.score + points);
    } else {
      setGameState(prev => ({
        ...prev,
        streak: 0,
        combo: 0,
        multiplier: 1,
      }));
      addNotification("Try again! 💪", "info");
    }

    setShowExplanation(true);

    // Auto-proceed in simulate mode or after delay
    const proceedDelay = gameState.mode === "simulate" ? 1500 : gameState.mode === "play" ? 2000 : 3000;
    setTimeout(nextQuestion, proceedDelay);
  }, [currentQuestion, selectedAnswer, timeRemaining, gameState, nextQuestion, onScoreUpdate, onAchievement, onPatternDetected]);

  // Spawn particles
  const spawnParticles = useCallback((count: number) => {
    const colors = ["#FFD700", "#FF6B6B", "#4ECDC4", "#45B7D1", "#96E6A1"];
    const newParticles: Particle[] = Array.from({ length: count }, (_, i) => ({
      id: `particle_${Date.now()}_${i}`,
      x: 50 + (Math.random() - 0.5) * 30,
      y: 50,
      color: colors[Math.floor(Math.random() * colors.length)],
      size: 4 + Math.random() * 8,
      velocity: {
        x: (Math.random() - 0.5) * 20,
        y: -10 - Math.random() * 15,
      },
      life: 1,
    }));

    setGameState(prev => ({
      ...prev,
      particles: [...prev.particles, ...newParticles],
    }));
  }, []);

  // Add notification
  const addNotification = useCallback((message: string, type: Notification["type"]) => {
    const notification: Notification = {
      id: `notif_${Date.now()}`,
      message,
      type,
      timestamp: Date.now(),
    };
    setGameState(prev => ({
      ...prev,
      notifications: [...prev.notifications.slice(-4), notification],
    }));
  }, []);

  // Use hint
  const useHint = useCallback(() => {
    if (gameState.hintsUsed >= gameState.hintsAvailable || showHint) return;
    setShowHint(true);
    setGameState(prev => ({
      ...prev,
      hintsUsed: prev.hintsUsed + 1,
    }));
    addNotification("Hint revealed! 💡", "info");
  }, [gameState.hintsUsed, gameState.hintsAvailable, showHint, addNotification]);

  // Start game
  const startGame = useCallback(() => {
    setGameState(prev => ({ ...prev, isRunning: true, score: 0, streak: 0, level: 1 }));
    nextQuestion();

    // Start game timer
    gameTimerRef.current = setInterval(() => {
      setGameState(prev => ({ ...prev, timeElapsed: prev.timeElapsed + 1 }));
    }, 1000);
  }, [nextQuestion]);

  // Pause game
  const pauseGame = useCallback(() => {
    setGameState(prev => ({ ...prev, isRunning: false }));
    if (questionTimerRef.current) clearInterval(questionTimerRef.current);
    if (gameTimerRef.current) clearInterval(gameTimerRef.current);
  }, []);

  // Resume game
  const resumeGame = useCallback(() => {
    setGameState(prev => ({ ...prev, isRunning: true }));
  }, []);

  // Change mode
  const changeMode = useCallback((mode: GameMode) => {
    setGameState(prev => ({ ...prev, mode }));
    if (mode === "simulate" && currentQuestion) {
      // Auto-answer in simulation mode
      setTimeout(() => {
        const randomAnswer = currentQuestion.options?.[Math.floor(Math.random() * (currentQuestion.options?.length || 4))];
        if (randomAnswer) handleAnswer(randomAnswer);
      }, 1500);
    }
  }, [currentQuestion, handleAnswer]);

  // Clean up timers
  useEffect(() => {
    return () => {
      if (questionTimerRef.current) clearInterval(questionTimerRef.current);
      if (gameTimerRef.current) clearInterval(gameTimerRef.current);
    };
  }, []);

  // Update particles
  useEffect(() => {
    const particleInterval = setInterval(() => {
      setGameState(prev => ({
        ...prev,
        particles: prev.particles
          .map(p => ({
            ...p,
            y: p.y + p.velocity.y * 0.1,
            x: p.x + p.velocity.x * 0.1,
            velocity: { ...p.velocity, y: p.velocity.y + 0.5 },
            life: p.life - 0.02,
          }))
          .filter(p => p.life > 0),
      }));
    }, 16);
    return () => clearInterval(particleInterval);
  }, []);

  return (
    <div className="bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 rounded-2xl border border-purple-500/30 overflow-hidden">
      {/* Header */}
      <div className="bg-slate-800/50 px-4 py-3 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              <span className="font-bold text-lg text-white">Real-Time Engine</span>
            </div>

            {/* Mode Switcher */}
            <div className="flex items-center gap-1 bg-slate-900/50 rounded-lg p-1">
              {[
                { id: "play" as GameMode, label: "Play", icon: Gamepad2 },
                { id: "simulate" as GameMode, label: "Watch", icon: Eye },
                { id: "learn" as GameMode, label: "Learn", icon: Brain },
                { id: "challenge" as GameMode, label: "Challenge", icon: Target },
              ].map(mode => (
                <button
                  key={mode.id}
                  onClick={() => changeMode(mode.id)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-all ${
                    gameState.mode === mode.id
                      ? "bg-purple-500 text-white"
                      : "text-slate-400 hover:text-white hover:bg-slate-700"
                  }`}
                >
                  <mode.icon className="w-4 h-4" />
                  {mode.label}
                </button>
              ))}
            </div>
          </div>

          {/* Speed Control */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Speed:</span>
            <select
              value={gameState.speed}
              onChange={(e) => setGameState(prev => ({ ...prev, speed: e.target.value as GameSpeed }))}
              className="bg-slate-900 text-white text-sm rounded px-2 py-1 border border-slate-700"
            >
              <option value="slow">🐢 Slow</option>
              <option value="normal">🚶 Normal</option>
              <option value="fast">🏃 Fast</option>
              <option value="turbo">⚡ Turbo</option>
            </select>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="bg-slate-800/30 px-4 py-2 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-yellow-400" />
              <span className="font-bold text-yellow-400">{gameState.score.toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <Flame className="w-4 h-4 text-orange-400" />
              <span className="text-orange-400">{gameState.streak} streak</span>
            </div>
            <div className="flex items-center gap-2">
              <Trophy className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400">Level {gameState.level}</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-cyan-400" />
              <span className="text-cyan-400">{gameState.multiplier.toFixed(1)}x multiplier</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Timer className="w-4 h-4 text-slate-400" />
              <span className="text-slate-400 font-mono">
                {Math.floor(gameState.timeElapsed / 60)}:{(gameState.timeElapsed % 60).toString().padStart(2, "0")}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-green-400" />
              <span className="text-slate-400">
                {gameState.correctAnswers}/{gameState.totalQuestions}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Game Area */}
      <div className="p-6 min-h-[400px] relative overflow-hidden">
        {/* Particles */}
        <AnimatePresence>
          {gameState.particles.map(particle => (
            <motion.div
              key={particle.id}
              className="absolute rounded-full pointer-events-none"
              style={{
                left: `${particle.x}%`,
                top: `${particle.y}%`,
                width: particle.size,
                height: particle.size,
                backgroundColor: particle.color,
                opacity: particle.life,
              }}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              exit={{ opacity: 0 }}
            />
          ))}
        </AnimatePresence>

        {/* Notifications */}
        <div className="absolute top-4 right-4 space-y-2 z-10">
          <AnimatePresence>
            {gameState.notifications.map(notif => (
              <motion.div
                key={notif.id}
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 50 }}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  notif.type === "success" ? "bg-green-500/20 text-green-400" :
                  notif.type === "achievement" ? "bg-yellow-500/20 text-yellow-400" :
                  notif.type === "warning" ? "bg-orange-500/20 text-orange-400" :
                  "bg-blue-500/20 text-blue-400"
                }`}
              >
                {notif.message}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {!gameState.isRunning ? (
          /* Start Screen */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <div className="text-6xl mb-4">
              {ageGroup === "child" ? "🎮" : ageGroup === "teen" ? "🧠" : "🔬"}
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">
              {ageGroup === "child" ? "Let's Play!" : ageGroup === "teen" ? "Challenge Mode" : "Expert Mode"}
            </h2>
            <p className="text-slate-400 mb-6">
              {gameState.mode === "play" && "Answer questions as fast as you can!"}
              {gameState.mode === "simulate" && "Watch how AI learns from examples"}
              {gameState.mode === "learn" && "Learn at your own pace with explanations"}
              {gameState.mode === "challenge" && "Compete for the highest score!"}
            </p>
            <motion.button
              onClick={startGame}
              className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white font-bold text-lg flex items-center gap-2 mx-auto"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Play className="w-5 h-5" />
              Start Game
            </motion.button>
          </motion.div>
        ) : currentQuestion ? (
          /* Question Display */
          <motion.div
            key={currentQuestion.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Timer Bar */}
            {timeRemaining !== null && (
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500"
                  animate={{ width: `${(timeRemaining / currentQuestion.timeLimit) * 100}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            )}

            {/* Question */}
            <div className="text-center">
              <div className="inline-block px-3 py-1 bg-purple-500/20 rounded-full text-purple-400 text-sm mb-4">
                Question {gameState.totalQuestions} • {currentQuestion.points} pts
              </div>
              <h3 className="text-xl md:text-2xl font-bold text-white mb-2">
                {currentQuestion.prompt}
              </h3>
              <p className="text-slate-500 text-sm">
                {currentQuestion.type === "pattern" && "🧩 Find the pattern"}
                {currentQuestion.type === "sequence" && "🔢 Complete the sequence"}
                {currentQuestion.type === "match" && "🎯 Match the correct answer"}
                {currentQuestion.type === "predict" && "🔮 Predict the outcome"}
                {currentQuestion.type === "create" && "✨ Create your answer"}
              </p>
            </div>

            {/* Hint */}
            {showHint && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4"
              >
                <div className="flex items-center gap-2 text-yellow-400">
                  <Sparkles className="w-4 h-4" />
                  <span className="font-medium">Hint: {currentQuestion.hint}</span>
                </div>
              </motion.div>
            )}

            {/* Options */}
            {currentQuestion.options && (
              <div className="grid grid-cols-2 gap-3">
                {currentQuestion.options.map((option, index) => {
                  const isSelected = selectedAnswer === option;
                  const isCorrect = Array.isArray(currentQuestion.correctAnswer)
                    ? currentQuestion.correctAnswer.includes(option)
                    : option === currentQuestion.correctAnswer;
                  const showResult = selectedAnswer !== null;

                  return (
                    <motion.button
                      key={`option-${index}`}
                      onClick={() => handleAnswer(option)}
                      disabled={selectedAnswer !== null}
                      className={`p-4 rounded-xl border-2 text-left transition-all ${
                        showResult && isCorrect
                          ? "border-green-500 bg-green-500/20"
                          : showResult && isSelected && !isCorrect
                          ? "border-red-500 bg-red-500/20"
                          : isSelected
                          ? "border-purple-500 bg-purple-500/20"
                          : "border-slate-700 bg-slate-800/50 hover:border-slate-500"
                      }`}
                      whileHover={!selectedAnswer ? { scale: 1.02 } : {}}
                      whileTap={!selectedAnswer ? { scale: 0.98 } : {}}
                    >
                      <span className="text-white">{option}</span>
                      {showResult && isCorrect && <CheckCircle2 className="w-5 h-5 text-green-400 ml-2 inline" />}
                    </motion.button>
                  );
                })}
              </div>
            )}

            {/* Explanation */}
            {showExplanation && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-800/50 rounded-xl p-4 border border-slate-700"
              >
                <h4 className="font-medium text-white mb-2">📚 Explanation</h4>
                <p className="text-slate-300">{currentQuestion.explanation}</p>
              </motion.div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-center gap-4">
              {!showHint && gameState.hintsUsed < gameState.hintsAvailable && (
                <motion.button
                  onClick={useHint}
                  className="flex items-center gap-2 px-4 py-2 bg-yellow-500/20 rounded-lg text-yellow-400"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Sparkles className="w-4 h-4" />
                  Use Hint ({gameState.hintsAvailable - gameState.hintsUsed} left)
                </motion.button>
              )}
              <motion.button
                onClick={pauseGame}
                className="flex items-center gap-2 px-4 py-2 bg-slate-700 rounded-lg text-slate-300"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Pause className="w-4 h-4" />
                Pause
              </motion.button>
            </div>
          </motion.div>
        ) : null}
      </div>

      {/* Mode-Specific Info */}
      {gameState.mode === "simulate" && gameState.isRunning && (
        <div className="bg-blue-500/10 border-t border-blue-500/30 px-4 py-2">
          <div className="flex items-center gap-2 text-blue-400 text-sm">
            <Eye className="w-4 h-4" />
            <span>Simulation Mode: Watching AI learn from patterns...</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default RealTimeGameEngine;
