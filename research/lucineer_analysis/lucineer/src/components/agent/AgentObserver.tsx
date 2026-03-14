"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Bot,
  Play,
  Pause,
  SkipForward,
  RotateCcw,
  Sparkles,
  Brain,
  MessageSquare,
  Settings,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  Target,
  Zap,
  Eye,
  Wand2,
  FastForward,
} from "lucide-react";

// Agent Types
export type AgentType = "explorer" | "optimizer" | "analyst" | "teacher" | "designer";

// Agent State
interface AgentState {
  status: "idle" | "thinking" | "acting" | "waiting" | "success" | "error";
  currentGoal: string;
  currentStep: number;
  totalSteps: number;
  thoughts: AgentThought[];
  actions: AgentAction[];
  direction: string | null;
  learning: string[];
}

interface AgentThought {
  id: string;
  content: string;
  type: "observation" | "analysis" | "decision" | "question";
  timestamp: number;
}

interface AgentAction {
  id: string;
  type: string;
  description: string;
  params: Record<string, unknown>;
  result?: string;
}

// Direction Presets
const directionPresets: Record<string, string[]> = {
  manufacturing: [
    "Maximize yield by adjusting defect density",
    "Find the bottleneck in the process flow",
    "Optimize for lowest cost per working die",
    "Design for the education market segment",
    "Minimize time to first silicon",
  ],
  economics: [
    "Maximize profit margin across all segments",
    "Find the optimal price point for DIY makers",
    "Analyze competitive threat response",
    "Calculate break-even for different scenarios",
    "Evaluate supply chain risk mitigation",
  ],
  rtl: [
    "Optimize timing for target clock frequency",
    "Minimize area while meeting constraints",
    "Reduce power consumption for edge deployment",
    "Fix setup time violations",
    "Improve clock tree balance",
  ],
  math: [
    "Explore gradient descent optimization",
    "Visualize attention mechanism weights",
    "Analyze information entropy in the system",
    "Understand mask-locked weight encoding",
    "Master tensor operations for ML",
  ],
};

// Agent Personalities
const agentPersonalities: Record<AgentType, { name: string; emoji: string; style: string }> = {
  explorer: { name: "Explorer Agent", emoji: "🧭", style: "Curious and thorough" },
  optimizer: { name: "Optimizer Agent", emoji: "⚡", style: "Efficiency-focused" },
  analyst: { name: "Analyst Agent", emoji: "📊", style: "Data-driven" },
  teacher: { name: "Teacher Agent", emoji: "🎓", style: "Patient and explanatory" },
  designer: { name: "Designer Agent", emoji: "🎨", style: "Creative and iterative" },
};

interface AgentObserverProps {
  domain: "manufacturing" | "economics" | "rtl" | "math" | "custom";
  customGoals?: string[];
  onAgentAction?: (action: AgentAction) => void;
  onAgentThought?: (thought: AgentThought) => void;
  children?: React.ReactNode;
}

export default function AgentObserver({
  domain,
  customGoals,
  onAgentAction,
  onAgentThought,
  children,
}: AgentObserverProps) {
  const [agentType, setAgentType] = useState<AgentType>("explorer");
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState<1 | 2 | 5 | 10>(1);
  const [showThoughts, setShowThoughts] = useState(true);
  const [showLearning, setShowLearning] = useState(true);
  const [direction, setDirection] = useState<string>("");
  const [state, setState] = useState<AgentState>({
    status: "idle",
    currentGoal: "",
    currentStep: 0,
    totalSteps: 10,
    thoughts: [],
    actions: [],
    direction: null,
    learning: [],
  });

  const goals = customGoals || directionPresets[domain] || directionPresets.math;

  // Generate agent thoughts based on domain
  const generateThought = useCallback((goal: string, step: number): AgentThought => {
    const thoughtTypes: AgentThought["type"][] = ["observation", "analysis", "decision", "question"];
    const type = thoughtTypes[Math.floor(Math.random() * thoughtTypes.length)];

    const thoughtTemplates: Record<AgentThought["type"], string[]> = {
      observation: [
        `I notice the parameter at step ${step} has interesting properties...`,
        `Looking at the data pattern here, I see a trend...`,
        `The visualization shows a correlation between variables...`,
        `This reminds me of similar optimization problems...`,
        `The constraint boundary is closer than expected...`,
      ],
      analysis: [
        `Let me calculate the optimal value for this parameter...`,
        `Comparing with previous results suggests...`,
        `The gradient points toward a local minimum here...`,
        `This trade-off between speed and quality is key...`,
        `I should explore the parameter space more thoroughly...`,
      ],
      decision: [
        `I'll adjust the value to explore this region...`,
        `Next, I'll verify this hypothesis experimentally...`,
        `Let me try a different approach here...`,
        `I'm choosing to focus on this critical path...`,
        `Time to check if this assumption holds...`,
      ],
      question: [
        `What if I tried the opposite approach?`,
        `Could there be a hidden constraint I'm missing?`,
        `Is this the global optimum or a local one?`,
        `How would this change with different parameters?`,
        `What does the theory predict for this case?`,
      ],
    };

    const templates = thoughtTemplates[type];
    const content = templates[Math.floor(Math.random() * templates.length)];

    return {
      id: `thought-${Date.now()}-${step}`,
      content,
      type,
      timestamp: Date.now(),
    };
  }, []);

  // Generate agent actions
  const generateAction = useCallback((goal: string, step: number): AgentAction => {
    const actionTypes = [
      { type: "adjust", desc: "Adjusting parameter" },
      { type: "measure", desc: "Measuring outcome" },
      { type: "compare", desc: "Comparing results" },
      { type: "iterate", desc: "Iterating approach" },
      { type: "verify", desc: "Verifying hypothesis" },
    ];

    const action = actionTypes[Math.floor(Math.random() * actionTypes.length)];

    return {
      id: `action-${Date.now()}-${step}`,
      type: action.type,
      description: `${action.desc} for step ${step} of "${goal}"`,
      params: { step, goal, timestamp: Date.now() },
      result: step % 3 === 0 ? "Success - found improvement" : undefined,
    };
  }, []);

  // Agent simulation loop
  useEffect(() => {
    if (!isPlaying || state.status === "success") return;

    const interval = setInterval(() => {
      setState((prev) => {
        if (prev.currentStep >= prev.totalSteps) {
          return { ...prev, status: "success" };
        }

        const newStep = prev.currentStep + 1;
        const thought = generateThought(prev.currentGoal || goals[0], newStep);
        const action = generateAction(prev.currentGoal || goals[0], newStep);

        // Notify parent components
        onAgentThought?.(thought);
        onAgentAction?.(action);

        // Generate learning insights
        const learningInsight = newStep % 3 === 0 ? 
          `Learned: Optimal strategy depends on ${["constraint boundaries", "parameter sensitivity", "initial conditions"][Math.floor(Math.random() * 3)]}` : 
          undefined;

        return {
          ...prev,
          status: newStep < prev.totalSteps ? "acting" : "success",
          currentStep: newStep,
          thoughts: [...prev.thoughts.slice(-9), thought],
          actions: [...prev.actions.slice(-4), action],
          learning: learningInsight ? [...prev.learning.slice(-4), learningInsight] : prev.learning,
        };
      });
    }, 1000 / speed);

    return () => clearInterval(interval);
  }, [isPlaying, speed, state.status, goals, generateThought, generateAction, onAgentThought, onAgentAction]);

  // Start agent with a goal
  const startAgent = (goal: string) => {
    setState({
      status: "thinking",
      currentGoal: goal,
      currentStep: 0,
      totalSteps: 10,
      thoughts: [{
        id: "init",
        content: `Starting to work on: "${goal}"`,
        type: "observation",
        timestamp: Date.now(),
      }],
      actions: [],
      direction: direction || null,
      learning: [],
    });
    setIsPlaying(true);
  };

  // Reset agent
  const resetAgent = () => {
    setIsPlaying(false);
    setState({
      status: "idle",
      currentGoal: "",
      currentStep: 0,
      totalSteps: 10,
      thoughts: [],
      actions: [],
      direction: null,
      learning: [],
    });
  };

  // Skip to end
  const skipToEnd = () => {
    setState((prev) => ({
      ...prev,
      currentStep: prev.totalSteps,
      status: "success",
    }));
  };

  const personality = agentPersonalities[agentType];

  return (
    <div className="bg-card rounded-2xl border border-border overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <motion.div
              animate={isPlaying ? { scale: [1, 1.1, 1] } : {}}
              transition={{ repeat: Infinity, duration: 2 }}
              className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center"
            >
              <span className="text-2xl">{personality.emoji}</span>
            </motion.div>
            <div>
              <h3 className="font-semibold">{personality.name}</h3>
              <p className="text-xs text-muted-foreground">{personality.style}</p>
            </div>
          </div>

          {/* Speed Control */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Speed:</span>
            {[1, 2, 5, 10].map((s) => (
              <button
                key={s}
                onClick={() => setSpeed(s as typeof speed)}
                className={`px-2 py-1 rounded text-xs ${speed === s ? "bg-indigo-500 text-white" : "bg-muted"}`}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>

        {/* Progress Bar */}
        {state.currentGoal && (
          <div className="mt-4">
            <div className="flex justify-between text-xs text-muted-foreground mb-1">
              <span className="truncate">{state.currentGoal}</span>
              <span>{state.currentStep}/{state.totalSteps}</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                initial={{ width: 0 }}
                animate={{ width: `${(state.currentStep / state.totalSteps) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Direction Input */}
      <div className="p-4 border-b border-border bg-muted/30">
        <label className="text-xs font-medium text-muted-foreground mb-2 block">
          💡 Give the agent a direction (abstraction training):
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={direction}
            onChange={(e) => setDirection(e.target.value)}
            placeholder="e.g., 'Focus on minimizing power consumption'"
            className="flex-1 bg-background rounded-lg px-3 py-2 text-sm border border-border focus:border-indigo-500 outline-none"
          />
          <select
            value={agentType}
            onChange={(e) => setAgentType(e.target.value as AgentType)}
            className="bg-background rounded-lg px-3 py-2 text-sm border border-border"
          >
            <option value="explorer">🧭 Explorer</option>
            <option value="optimizer">⚡ Optimizer</option>
            <option value="analyst">📊 Analyst</option>
            <option value="teacher">🎓 Teacher</option>
            <option value="designer">🎨 Designer</option>
          </select>
        </div>
      </div>

      {/* Goal Selection */}
      {!isPlaying && state.status === "idle" && (
        <div className="p-4 border-b border-border">
          <label className="text-xs font-medium text-muted-foreground mb-2 block">
            🎯 Select a goal for the agent:
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {goals.map((goal, i) => (
              <button
                key={i}
                onClick={() => startAgent(goal)}
                className="text-left px-3 py-2 rounded-lg bg-muted hover:bg-indigo-500/10 hover:border-indigo-500/50 border border-border text-sm transition-colors"
              >
                <Target className="w-3 h-3 inline mr-2 text-indigo-400" />
                {goal}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Playback Controls */}
      {state.currentGoal && (
        <div className="p-4 border-b border-border flex justify-center gap-3">
          <button
            onClick={resetAgent}
            className="p-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
            title="Reset"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className={`p-3 rounded-lg ${isPlaying ? "bg-amber-500" : "bg-indigo-500"} text-white transition-colors`}
            title={isPlaying ? "Pause" : "Play"}
          >
            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </button>
          <button
            onClick={() => setIsPlaying(true)}
            className="p-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
            title="Step Forward"
          >
            <SkipForward className="w-5 h-5" />
          </button>
          <button
            onClick={skipToEnd}
            className="p-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
            title="Skip to End"
          >
            <FastForward className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 divide-y lg:divide-y-0 lg:divide-x divide-border">
        {/* Thoughts Panel */}
        <div className={`p-4 ${showThoughts ? "" : "hidden lg:block"}`}>
          <button
            onClick={() => setShowThoughts(!showThoughts)}
            className="flex items-center gap-2 text-sm font-medium mb-3 lg:cursor-default"
          >
            <Brain className="w-4 h-4 text-purple-400" />
            Agent Thoughts
            <ChevronDown className={`w-4 h-4 lg:hidden transition-transform ${showThoughts ? "rotate-180" : ""}`} />
          </button>
          
          <div className="space-y-2 max-h-60 overflow-y-auto">
            <AnimatePresence>
              {state.thoughts.map((thought) => (
                <motion.div
                  key={thought.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`p-2 rounded-lg text-xs ${
                    thought.type === "observation" ? "bg-blue-500/10 border-l-2 border-blue-400" :
                    thought.type === "analysis" ? "bg-purple-500/10 border-l-2 border-purple-400" :
                    thought.type === "decision" ? "bg-green-500/10 border-l-2 border-green-400" :
                    "bg-amber-500/10 border-l-2 border-amber-400"
                  }`}
                >
                  <span className="text-muted-foreground capitalize">{thought.type}:</span>{" "}
                  {thought.content}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>

        {/* Actions Panel */}
        <div className="p-4">
          <div className="flex items-center gap-2 text-sm font-medium mb-3">
            <Wand2 className="w-4 h-4 text-indigo-400" />
            Actions Taken
          </div>
          
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {state.actions.length === 0 ? (
              <p className="text-xs text-muted-foreground">Actions will appear here...</p>
            ) : (
              state.actions.map((action) => (
                <div
                  key={action.id}
                  className="p-2 rounded-lg bg-muted text-xs"
                >
                  <span className="font-medium text-indigo-400">{action.type}:</span>{" "}
                  {action.description}
                  {action.result && (
                    <span className="ml-1 text-green-400">✓ {action.result}</span>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Learning Panel */}
        <div className={`p-4 ${showLearning ? "" : "hidden lg:block"}`}>
          <button
            onClick={() => setShowLearning(!showLearning)}
            className="flex items-center gap-2 text-sm font-medium mb-3 lg:cursor-default"
          >
            <Lightbulb className="w-4 h-4 text-amber-400" />
            Learning Insights
            <ChevronDown className={`w-4 h-4 lg:hidden transition-transform ${showLearning ? "rotate-180" : ""}`} />
          </button>
          
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {state.learning.length === 0 ? (
              <p className="text-xs text-muted-foreground">Insights will appear as the agent learns...</p>
            ) : (
              state.learning.map((insight, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/20 text-xs"
                >
                  <Sparkles className="w-3 h-3 inline mr-1 text-amber-400" />
                  {insight}
                </motion.div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Success State */}
      {state.status === "success" && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-t border-green-500/20 text-center"
        >
          <div className="text-4xl mb-2">🎉</div>
          <h4 className="font-semibold text-lg text-green-400">Goal Completed!</h4>
          <p className="text-sm text-muted-foreground mt-1">
            The agent explored "{state.currentGoal}" over {state.totalSteps} steps.
          </p>
          <div className="mt-4 flex justify-center gap-3">
            <button
              onClick={resetAgent}
              className="px-4 py-2 rounded-lg bg-green-500/20 text-green-400 text-sm font-medium"
            >
              Try Another Goal
            </button>
            <button
              onClick={() => setDirection("")}
              className="px-4 py-2 rounded-lg bg-muted text-sm font-medium"
            >
              Change Direction
            </button>
          </div>
        </motion.div>
      )}

      {/* Abstraction Training Note */}
      <div className="p-4 bg-muted/30 border-t border-border">
        <div className="flex items-start gap-2">
          <Eye className="w-4 h-4 text-indigo-400 mt-0.5" />
          <div className="text-xs text-muted-foreground">
            <strong className="text-foreground">Abstraction Training:</strong> Watching an agent work 
            helps you see the structure of problems. Try giving different directions and observe how 
            the agent's approach changes. This trains your ability to break down complex tasks.
          </div>
        </div>
      </div>

      {/* Custom Content */}
      {children}
    </div>
  );
}
