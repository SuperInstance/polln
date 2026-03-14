"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Rocket,
  Zap,
  ChevronRight,
  ChevronLeft,
  Play,
  Pause,
  SkipForward,
  RotateCcw,
  Sparkles,
  Brain,
  Target,
  Trophy,
  Star,
  Clock,
  CheckCircle2,
  XCircle,
  Gauge,
  Lightbulb,
  BookOpen,
  GraduationCap,
  Flame,
  Award,
  Timer,
  TrendingUp,
  Activity,
} from "lucide-react";

// ============================================================================
// SPEED LEARNING PATH
// Fast learners can pump through concepts quickly
// Adaptive difficulty that challenges without frustrating
// ============================================================================

type LearningPhase = "concept" | "practice" | "challenge" | "review";
type DifficultyLevel = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
type Subject = "ai-basics" | "neural-networks" | "machine-learning" | "deep-learning" | "nlp" | "computer-vision";

interface LearningConcept {
  id: string;
  title: string;
  summary: string;
  keyPoints: string[];
  difficulty: DifficultyLevel;
  estimatedTime: number; // seconds
  prerequisites: string[];
  relatedConcepts: string[];
}

interface SpeedChallenge {
  id: string;
  conceptId: string;
  type: "multiple-choice" | "fill-blank" | "sequence" | "match" | "apply";
  question: string;
  options?: string[];
  correctAnswer: string | string[];
  explanation: string;
  points: number;
  timeLimit: number; // seconds
}

interface LearningProgress {
  conceptsCompleted: string[];
  challengesSolved: string[];
  totalPoints: number;
  currentStreak: number;
  bestStreak: number;
  averageTime: number;
  masteryLevel: Record<string, number>; // conceptId -> mastery percentage
}

// Concept Library
const CONCEPTS: Record<Subject, LearningConcept[]> = {
  "ai-basics": [
    {
      id: "what-is-ai",
      title: "What is AI?",
      summary: "Artificial Intelligence is the simulation of human intelligence by machines, enabling them to learn, reason, and make decisions.",
      keyPoints: [
        "AI mimics human cognitive functions",
        "Machine Learning is a subset of AI",
        "AI can be narrow (specific tasks) or general (human-level)",
        "Training data is crucial for AI performance",
      ],
      difficulty: 1,
      estimatedTime: 30,
      prerequisites: [],
      relatedConcepts: ["machine-learning", "neural-networks"],
    },
    {
      id: "training-data",
      title: "Training Data",
      summary: "The examples and information used to teach AI systems. Quality data leads to quality AI.",
      keyPoints: [
        "More data generally means better AI",
        "Data quality matters more than quantity",
        "Bias in data leads to bias in AI",
        "Data must be labeled for supervised learning",
      ],
      difficulty: 2,
      estimatedTime: 45,
      prerequisites: ["what-is-ai"],
      relatedConcepts: ["machine-learning"],
    },
    {
      id: "patterns",
      title: "Pattern Recognition",
      summary: "AI's core ability to find patterns in data that humans might miss or take too long to identify.",
      keyPoints: [
        "Patterns can be visual, numerical, or behavioral",
        "AI finds patterns faster than humans",
        "Complex patterns require more training data",
        "False patterns can emerge from noise",
      ],
      difficulty: 2,
      estimatedTime: 40,
      prerequisites: ["what-is-ai"],
      relatedConcepts: ["machine-learning"],
    },
  ],
  "neural-networks": [
    {
      id: "neurons",
      title: "Artificial Neurons",
      summary: "The basic building blocks of neural networks, inspired by biological neurons in the brain.",
      keyPoints: [
        "Neurons receive inputs, apply weights, and produce outputs",
        "Activation functions determine neuron firing",
        "Weight adjustments enable learning",
        "Multiple neurons form layers",
      ],
      difficulty: 3,
      estimatedTime: 60,
      prerequisites: ["what-is-ai"],
      relatedConcepts: ["deep-learning"],
    },
    {
      id: "layers",
      title: "Network Layers",
      summary: "Neurons are organized into layers that transform data progressively toward the desired output.",
      keyPoints: [
        "Input layer receives raw data",
        "Hidden layers perform transformations",
        "Output layer produces predictions",
        "More layers = deeper network",
      ],
      difficulty: 4,
      estimatedTime: 45,
      prerequisites: ["neurons"],
      relatedConcepts: ["deep-learning"],
    },
  ],
  "machine-learning": [
    {
      id: "supervised-learning",
      title: "Supervised Learning",
      summary: "The most common ML approach where AI learns from labeled examples with known correct answers.",
      keyPoints: [
        "Requires labeled training data",
        "Learns to map inputs to outputs",
        "Used for classification and regression",
        "Performance measured on test data",
      ],
      difficulty: 3,
      estimatedTime: 50,
      prerequisites: ["training-data"],
      relatedConcepts: ["deep-learning"],
    },
    {
      id: "unsupervised-learning",
      title: "Unsupervised Learning",
      summary: "AI discovers patterns in unlabeled data, finding hidden structures without guidance.",
      keyPoints: [
        "No labeled data required",
        "Finds hidden patterns and groupings",
        "Clustering is a common technique",
        "Useful for data exploration",
      ],
      difficulty: 4,
      estimatedTime: 55,
      prerequisites: ["training-data"],
      relatedConcepts: ["deep-learning"],
    },
  ],
  "deep-learning": [],
  "nlp": [],
  "computer-vision": [],
};

// Challenge Bank
const CHALLENGES: SpeedChallenge[] = [
  {
    id: "ch1",
    conceptId: "what-is-ai",
    type: "multiple-choice",
    question: "What does AI stand for?",
    options: ["Automated Intelligence", "Artificial Intelligence", "Advanced Interface", "Analog Integration"],
    correctAnswer: "Artificial Intelligence",
    explanation: "AI stands for Artificial Intelligence - the simulation of human intelligence by machines.",
    points: 100,
    timeLimit: 15,
  },
  {
    id: "ch2",
    conceptId: "what-is-ai",
    type: "multiple-choice",
    question: "Which is a subset of AI?",
    options: ["Python", "Machine Learning", "Database", "Web Development"],
    correctAnswer: "Machine Learning",
    explanation: "Machine Learning is a subset of AI that enables systems to learn from data without being explicitly programmed.",
    points: 100,
    timeLimit: 15,
  },
  {
    id: "ch3",
    conceptId: "training-data",
    type: "multiple-choice",
    question: "What happens if training data has bias?",
    options: ["AI becomes faster", "AI becomes biased", "AI stops working", "No effect on AI"],
    correctAnswer: "AI becomes biased",
    explanation: "AI learns from its training data. If that data contains bias, the AI will reflect and potentially amplify those biases.",
    points: 150,
    timeLimit: 20,
  },
  {
    id: "ch4",
    conceptId: "patterns",
    type: "multiple-choice",
    question: "Why is pattern recognition important for AI?",
    options: ["It makes AI look cool", "It enables AI to make predictions", "It's required by law", "It reduces file sizes"],
    correctAnswer: "It enables AI to make predictions",
    explanation: "Pattern recognition allows AI to identify trends and relationships in data, enabling it to make predictions on new, unseen data.",
    points: 150,
    timeLimit: 20,
  },
  {
    id: "ch5",
    conceptId: "neurons",
    type: "multiple-choice",
    question: "What does an artificial neuron do?",
    options: ["Stores files", "Receives inputs and produces outputs", "Creates websites", "Sends emails"],
    correctAnswer: "Receives inputs and produces outputs",
    explanation: "An artificial neuron receives input signals, applies weights, processes them through an activation function, and produces an output signal.",
    points: 200,
    timeLimit: 25,
  },
];

// ============================================================================
// SPEED LEARNING PATH COMPONENT
// ============================================================================

interface SpeedLearningPathProps {
  subject?: Subject;
  startDifficulty?: DifficultyLevel;
  onProgress?: (progress: LearningProgress) => void;
  onConceptMastered?: (conceptId: string) => void;
  onChallengeComplete?: (challengeId: string, correct: boolean) => void;
}

export function SpeedLearningPath({
  subject = "ai-basics",
  startDifficulty = 1,
  onProgress,
  onConceptMastered,
  onChallengeComplete,
}: SpeedLearningPathProps) {
  // State
  const [currentPhase, setCurrentPhase] = useState<LearningPhase>("concept");
  const [currentConceptIndex, setCurrentConceptIndex] = useState(0);
  const [currentChallengeIndex, setCurrentChallengeIndex] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const [difficulty, setDifficulty] = useState(startDifficulty);
  
  const [progress, setProgress] = useState<LearningProgress>({
    conceptsCompleted: [],
    challengesSolved: [],
    totalPoints: 0,
    currentStreak: 0,
    bestStreak: 0,
    averageTime: 0,
    masteryLevel: {},
  });

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const startTimeRef = useRef<number>(Date.now());

  // Get current content
  const concepts = CONCEPTS[subject] || [];
  const currentConcept = concepts[currentConceptIndex];
  const relevantChallenges = CHALLENGES.filter(c => c.conceptId === currentConcept?.id);
  const currentChallenge = relevantChallenges[currentChallengeIndex];

  // Start timer for challenge
  const startTimer = useCallback((seconds: number) => {
    setTimeRemaining(seconds);
    if (timerRef.current) clearInterval(timerRef.current);
    
    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev === null || prev <= 0) {
          handleTimeout();
          return null;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  // Handle timeout
  const handleTimeout = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    setShowExplanation(true);
    setProgress(prev => ({
      ...prev,
      currentStreak: 0,
    }));
    
    setTimeout(() => nextChallenge(), 2000);
  }, []);

  // Next concept
  const nextConcept = useCallback(() => {
    if (currentConceptIndex < concepts.length - 1) {
      setCurrentConceptIndex(prev => prev + 1);
      setCurrentChallengeIndex(0);
      setCurrentPhase("concept");
      setShowExplanation(false);
      setSelectedAnswer(null);
    }
  }, [currentConceptIndex, concepts.length]);

  // Next challenge
  const nextChallenge = useCallback(() => {
    if (currentChallengeIndex < relevantChallenges.length - 1) {
      setCurrentChallengeIndex(prev => prev + 1);
      setShowExplanation(false);
      setSelectedAnswer(null);
    } else {
      // All challenges done for this concept
      if (currentConcept) {
        setProgress(prev => ({
          ...prev,
          conceptsCompleted: [...prev.conceptsCompleted, currentConcept.id],
          masteryLevel: {
            ...prev.masteryLevel,
            [currentConcept.id]: 100,
          },
        }));
        onConceptMastered?.(currentConcept.id);
      }
      nextConcept();
    }
  }, [currentChallengeIndex, relevantChallenges.length, currentConcept, nextConcept, onConceptMastered]);

  // Handle answer
  const handleAnswer = useCallback((answer: string) => {
    if (!currentChallenge || selectedAnswer !== null) return;

    setSelectedAnswer(answer);
    if (timerRef.current) clearInterval(timerRef.current);

    const isCorrect = answer === currentChallenge.correctAnswer;

    if (isCorrect) {
      const timeBonus = Math.floor((timeRemaining || 0) * 10);
      const points = currentChallenge.points + timeBonus;

      setProgress(prev => ({
        ...prev,
        challengesSolved: [...prev.challengesSolved, currentChallenge.id],
        totalPoints: prev.totalPoints + points,
        currentStreak: prev.currentStreak + 1,
        bestStreak: Math.max(prev.bestStreak, prev.currentStreak + 1),
      }));

      onChallengeComplete?.(currentChallenge.id, true);
    } else {
      setProgress(prev => ({
        ...prev,
        currentStreak: 0,
      }));
      onChallengeComplete?.(currentChallenge.id, false);
    }

    setShowExplanation(true);
    onProgress?.(progress);

    // Auto-advance after explanation
    setTimeout(nextChallenge, 1500);
  }, [currentChallenge, selectedAnswer, timeRemaining, progress, nextChallenge, onChallengeComplete, onProgress]);

  // Start learning session
  const startSession = useCallback(() => {
    setIsRunning(true);
    startTimeRef.current = Date.now();
    setCurrentPhase("concept");
  }, []);

  // Skip to challenge
  const skipToChallenge = useCallback(() => {
    setCurrentPhase("challenge");
    if (currentChallenge) {
      startTimer(currentChallenge.timeLimit);
    }
  }, [currentChallenge, startTimer]);

  // Calculate speed score
  const speedScore = progress.currentStreak >= 5 ? 2 : progress.currentStreak >= 3 ? 1.5 : 1;

  return (
    <div className="bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900 rounded-2xl border border-purple-500/30 overflow-hidden">
      {/* Header */}
      <div className="bg-slate-800/50 px-4 py-3 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Rocket className="w-5 h-5 text-purple-400" />
            <span className="font-bold text-white">Speed Learning Path</span>
            <div className="px-2 py-0.5 bg-purple-500/20 rounded-full text-purple-400 text-xs">
              {subject.replace("-", " ").toUpperCase()}
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Star className="w-4 h-4 text-yellow-400" />
              <span className="font-bold text-yellow-400">{progress.totalPoints}</span>
            </div>
            <div className="flex items-center gap-2">
              <Flame className="w-4 h-4 text-orange-400" />
              <span className="text-orange-400">{progress.currentStreak} streak</span>
            </div>
            <div className="flex items-center gap-2">
              <Gauge className="w-4 h-4 text-cyan-400" />
              <span className="text-cyan-400">{speedScore}x speed</span>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-slate-800/30 px-4 py-2 border-b border-slate-700/50">
        <div className="flex items-center gap-4">
          <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500"
              animate={{ width: `${(progress.conceptsCompleted.length / Math.max(1, concepts.length)) * 100}%` }}
            />
          </div>
          <span className="text-xs text-slate-400">
            {progress.conceptsCompleted.length}/{concepts.length} concepts
          </span>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-4 min-h-[300px]">
        {!isRunning ? (
          /* Start Screen */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-8"
          >
            <Rocket className="w-16 h-16 text-purple-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Fast Track Learning</h2>
            <p className="text-slate-400 mb-6">
              Zoom through concepts at your own pace. Skip what you know, dive deep on challenges.
            </p>
            
            <div className="flex items-center justify-center gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">{concepts.length}</div>
                <div className="text-xs text-slate-500">Concepts</div>
              </div>
              <div className="w-px h-8 bg-slate-700" />
              <div className="text-center">
                <div className="text-2xl font-bold text-pink-400">{CHALLENGES.filter(c => concepts.some(con => con.id === c.conceptId)).length}</div>
                <div className="text-xs text-slate-500">Challenges</div>
              </div>
              <div className="w-px h-8 bg-slate-700" />
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-400">~{concepts.reduce((sum, c) => sum + c.estimatedTime, 0) / 60}min</div>
                <div className="text-xs text-slate-500">Est. Time</div>
              </div>
            </div>

            <motion.button
              onClick={startSession}
              className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white font-bold text-lg"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Zap className="w-5 h-5 inline mr-2" />
              Start Speed Run
            </motion.button>
          </motion.div>
        ) : currentConcept ? (
          <AnimatePresence mode="wait">
            {currentPhase === "concept" && (
              /* Concept Phase */
              <motion.div
                key="concept"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-purple-400" />
                    <h3 className="text-xl font-bold text-white">{currentConcept.title}</h3>
                  </div>
                  <div className="flex items-center gap-2 text-slate-400">
                    <Clock className="w-4 h-4" />
                    <span className="text-sm">~{currentConcept.estimatedTime}s</span>
                  </div>
                </div>

                <p className="text-slate-300 text-lg">{currentConcept.summary}</p>

                <div className="space-y-2">
                  {currentConcept.keyPoints.map((point, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start gap-2 p-2 bg-slate-800/30 rounded-lg"
                    >
                      <CheckCircle2 className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-slate-300">{point}</span>
                    </motion.div>
                  ))}
                </div>

                <div className="flex items-center justify-center gap-4 pt-4">
                  <motion.button
                    onClick={skipToChallenge}
                    className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg text-white font-medium"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Got it! Next
                    <ChevronRight className="w-4 h-4" />
                  </motion.button>
                  <button
                    onClick={nextConcept}
                    className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-lg text-slate-300"
                  >
                    <SkipForward className="w-4 h-4" />
                    Skip
                  </button>
                </div>
              </motion.div>
            )}

            {currentPhase === "challenge" && currentChallenge && (
              /* Challenge Phase */
              <motion.div
                key="challenge"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-4"
              >
                {/* Timer */}
                {timeRemaining !== null && (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Timer className="w-4 h-4 text-slate-400" />
                      <span className={`font-mono text-lg ${
                        timeRemaining <= 5 ? "text-red-400" : "text-slate-300"
                      }`}>
                        {timeRemaining}s
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Target className="w-4 h-4 text-amber-400" />
                      <span className="text-amber-400">{currentChallenge.points} pts</span>
                    </div>
                  </div>
                )}

                {/* Question */}
                <div className="bg-slate-800/50 rounded-xl p-4">
                  <p className="text-lg text-white font-medium">{currentChallenge.question}</p>
                </div>

                {/* Options */}
                {currentChallenge.options && (
                  <div className="grid grid-cols-2 gap-3">
                    {currentChallenge.options.map((option, index) => {
                      const isSelected = selectedAnswer === option;
                      const isCorrect = option === currentChallenge.correctAnswer;
                      const showResult = selectedAnswer !== null;

                      return (
                        <motion.button
                          key={index}
                          onClick={() => handleAnswer(option)}
                          disabled={selectedAnswer !== null}
                          className={`p-3 rounded-xl border-2 text-left transition-all ${
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
                    className="bg-slate-800/30 rounded-xl p-4 border border-slate-700"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <Lightbulb className="w-4 h-4 text-yellow-400" />
                      <span className="font-medium text-white">Explanation</span>
                    </div>
                    <p className="text-sm text-slate-300">{currentChallenge.explanation}</p>
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        ) : (
          /* Complete */
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-8"
          >
            <Trophy className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Speed Run Complete! 🎉</h2>
            <p className="text-slate-400 mb-4">
              You mastered {progress.conceptsCompleted.length} concepts!
            </p>
            <div className="flex items-center justify-center gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-400">{progress.totalPoints}</div>
                <div className="text-xs text-slate-500">Total Points</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-400">{progress.bestStreak}</div>
                <div className="text-xs text-slate-500">Best Streak</div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

export default SpeedLearningPath;
