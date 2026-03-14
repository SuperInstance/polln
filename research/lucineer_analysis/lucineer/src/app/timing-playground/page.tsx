"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Clock,
  Circle,
  Puzzle,
  Layers,
  Play,
  Pause,
  RotateCcw,
  Settings,
  ArrowRight,
  Zap,
  Timer,
  Activity,
  Box,
} from "lucide-react";

type TrafficState = "red" | "yellow" | "green";

interface DominoBlock {
  id: number;
  angle: number;
  fallen: boolean;
  delay: number;
}

const playgrounds = [
  {
    id: "traffic",
    title: "Traffic Light Simulator",
    description: "Control timing sequences like a traffic engineer",
    icon: Circle,
    color: "text-red-400",
  },
  {
    id: "dominoes",
    title: "Domino Chain Builder",
    description: "Create cascading timing sequences",
    icon: Puzzle,
    color: "text-amber-400",
  },
  {
    id: "clocks",
    title: "Clock Domain Visualizer",
    description: "See how different clocks interact",
    icon: Clock,
    color: "text-blue-400",
  },
  {
    id: "signals",
    title: "Signal Timing Analysis",
    description: "Analyze setup and hold times",
    icon: Activity,
    color: "text-purple-400",
  },
];

// Traffic Light Simulator Component
function TrafficLightSimulator() {
  const [isRunning, setIsRunning] = useState(false);
  const [currentState, setCurrentState] = useState<TrafficState>("red");
  const [timings, setTimings] = useState({ red: 30, yellow: 5, green: 25 });
  const [timeLeft, setTimeLeft] = useState(timings.red);

  useEffect(() => {
    if (!isRunning) return;

    const interval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          // Switch state
          setCurrentState((current) => {
            const nextState = current === "red" ? "green" : current === "green" ? "yellow" : "red";
            setTimeLeft(timings[nextState]);
            return nextState;
          });
          return 0;
        }
        return prev - 1;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isRunning, timings]);

  const reset = () => {
    setIsRunning(false);
    setCurrentState("red");
    setTimeLeft(timings.red);
  };

  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-red-400/10 flex items-center justify-center">
            <div className="flex flex-col gap-0.5">
              <Circle className="w-2 h-2 text-red-400 fill-red-400" />
              <Circle className="w-2 h-2 text-yellow-400 fill-yellow-400 opacity-30" />
              <Circle className="w-2 h-2 text-green-400 fill-green-400 opacity-30" />
            </div>
          </div>
          <div>
            <h3 className="font-semibold">Traffic Light Controller</h3>
            <p className="text-sm text-muted-foreground">State machine timing simulation</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsRunning(!isRunning)}
            className={`p-2 rounded-lg transition-colors ${
              isRunning ? "bg-amber-400/10 text-amber-400" : "bg-primary/10 text-primary"
            }`}
          >
            {isRunning ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </button>
          <button
            onClick={reset}
            className="p-2 rounded-lg bg-muted text-muted-foreground hover:text-foreground transition-colors"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Traffic Light Visual */}
        <div className="flex flex-col items-center gap-6">
          <div className="bg-muted rounded-2xl p-4 flex flex-col gap-3">
            {(["red", "yellow", "green"] as TrafficState[]).map((color) => (
              <motion.div
                key={color}
                className={`w-16 h-16 rounded-full transition-all duration-300 ${
                  currentState === color
                    ? color === "red"
                      ? "bg-red-500 shadow-[0_0_30px_rgba(239,68,68,0.6)]"
                      : color === "yellow"
                      ? "bg-yellow-400 shadow-[0_0_30px_rgba(250,204,21,0.6)]"
                      : "bg-green-500 shadow-[0_0_30px_rgba(34,197,94,0.6)]"
                    : "bg-muted-foreground/20"
                }`}
                animate={currentState === color ? { scale: [1, 1.1, 1] } : { scale: 1 }}
                transition={{ duration: 0.5, repeat: currentState === color ? Infinity : 0, repeatDelay: 1 }}
              />
            ))}
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold font-mono text-primary">{timeLeft}s</div>
            <div className="text-sm text-muted-foreground capitalize">{currentState} light</div>
          </div>
        </div>

        {/* Timing Controls */}
        <div className="space-y-4">
          <h4 className="font-medium flex items-center gap-2">
            <Settings className="w-4 h-4" /> Timing Settings
          </h4>
          
          {(["red", "yellow", "green"] as TrafficState[]).map((color) => (
            <div key={color} className="flex items-center gap-4">
              <div className={`w-3 h-3 rounded-full ${
                color === "red" ? "bg-red-500" :
                color === "yellow" ? "bg-yellow-400" : "bg-green-500"
              }`} />
              <span className="text-sm capitalize w-16">{color}</span>
              <input
                type="range"
                min="1"
                max="60"
                value={timings[color]}
                onChange={(e) => setTimings({ ...timings, [color]: parseInt(e.target.value) })}
                className="flex-1"
              />
              <span className="text-sm font-mono w-8">{timings[color]}s</span>
            </div>
          ))}

          <div className="mt-6 p-4 bg-muted/50 rounded-xl">
            <div className="text-sm text-muted-foreground mb-2">Total Cycle Time</div>
            <div className="text-2xl font-bold text-primary">{timings.red + timings.yellow + timings.green}s</div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Domino Chain Simulator
function DominoSimulator() {
  const [dominoes, setDominoes] = useState<DominoBlock[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [fallSpeed, setFallSpeed] = useState(100);

  const addDomino = () => {
    const newId = dominoes.length;
    setDominoes([
      ...dominoes,
      { id: newId, angle: 0, fallen: false, delay: newId * 0.1 }
    ]);
  };

  const startChain = () => {
    if (dominoes.length === 0) return;
    setIsRunning(true);
    
    dominoes.forEach((_, index) => {
      setTimeout(() => {
        setDominoes((prev) =>
          prev.map((d, i) =>
            i === index ? { ...d, fallen: true, angle: 85 } : d
          )
        );
      }, index * fallSpeed);
    });

    setTimeout(() => setIsRunning(false), dominoes.length * fallSpeed + 500);
  };

  const reset = () => {
    setIsRunning(false);
    setDominoes(dominoes.map((d) => ({ ...d, fallen: false, angle: 0 })));
  };

  const clearAll = () => {
    setIsRunning(false);
    setDominoes([]);
  };

  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-amber-400/10 flex items-center justify-center">
            <Puzzle className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h3 className="font-semibold">Domino Chain Builder</h3>
            <p className="text-sm text-muted-foreground">Cascading timing sequence</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={addDomino}
            disabled={isRunning}
            className="px-3 py-2 rounded-lg bg-primary/10 text-primary text-sm font-medium disabled:opacity-50"
          >
            Add Domino
          </button>
          <button
            onClick={startChain}
            disabled={isRunning || dominoes.length === 0}
            className="p-2 rounded-lg bg-primary/10 text-primary disabled:opacity-50"
          >
            <Play className="w-5 h-5" />
          </button>
          <button
            onClick={reset}
            className="p-2 rounded-lg bg-muted text-muted-foreground hover:text-foreground"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
          <button
            onClick={clearAll}
            className="p-2 rounded-lg bg-muted text-muted-foreground hover:text-foreground"
          >
            <Box className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Domino Visualization */}
      <div className="bg-muted/30 rounded-xl p-8 mb-6 min-h-[200px] flex items-end gap-2 justify-center overflow-hidden">
        {dominoes.length === 0 ? (
          <div className="text-muted-foreground text-center">
            <Puzzle className="w-12 h-12 mx-auto mb-2 opacity-30" />
            <p>Click &quot;Add Domino&quot; to start building</p>
          </div>
        ) : (
          dominoes.map((domino) => (
            <motion.div
              key={domino.id}
              className="w-6 h-24 bg-gradient-to-t from-amber-600 to-amber-400 rounded-t-sm origin-bottom"
              animate={{
                rotateX: domino.angle,
              }}
              transition={{
                duration: 0.3,
                ease: "easeOut",
              }}
              style={{
                transformStyle: "preserve-3d",
              }}
            />
          ))
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4">
        <span className="text-sm text-muted-foreground">Fall Speed:</span>
        <input
          type="range"
          min="50"
          max="300"
          value={fallSpeed}
          onChange={(e) => setFallSpeed(parseInt(e.target.value))}
          className="flex-1 max-w-xs"
        />
        <span className="text-sm font-mono">{fallSpeed}ms</span>
        <span className="text-sm text-muted-foreground ml-4">
          Total delay: <span className="text-primary font-mono">{dominoes.length * fallSpeed}ms</span>
        </span>
      </div>
    </div>
  );
}

// Clock Domain Visualizer
function ClockDomainVisualizer() {
  const [isRunning, setIsRunning] = useState(true);
  const [clockA, setClockA] = useState({ freq: 100, phase: 0 });
  const [clockB, setClockB] = useState({ freq: 66, phase: 0 });
  const [time, setTime] = useState(0);

  useEffect(() => {
    if (!isRunning) return;
    
    const interval = setInterval(() => {
      setTime((t) => (t + 1) % 100);
    }, 50);

    return () => clearInterval(interval);
  }, [isRunning]);

  const getSignal = (freq: number, phase: number) => {
    const period = 100 / freq;
    return Math.floor((time + phase) / (period / 2)) % 2 === 0;
  };

  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-400/10 flex items-center justify-center">
            <Clock className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="font-semibold">Clock Domain Visualizer</h3>
            <p className="text-sm text-muted-foreground">See how different clock frequencies interact</p>
          </div>
        </div>
        <button
          onClick={() => setIsRunning(!isRunning)}
          className={`p-2 rounded-lg transition-colors ${
            isRunning ? "bg-amber-400/10 text-amber-400" : "bg-primary/10 text-primary"
          }`}
        >
          {isRunning ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
        </button>
      </div>

      <div className="space-y-6">
        {/* Clock A */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-primary">Clock Domain A</span>
            <span className="text-sm font-mono">{clockA.freq} MHz</span>
          </div>
          <div className="h-12 bg-muted/30 rounded-lg overflow-hidden flex">
            {Array.from({ length: 50 }).map((_, i) => (
              <motion.div
                key={i}
                className={`flex-1 ${getSignal(clockA.freq, clockA.phase) ? "bg-primary" : "bg-primary/20"}`}
                animate={{
                  backgroundColor: getSignal(clockA.freq, clockA.phase) 
                    ? "oklch(0.72 0.19 145)" 
                    : "oklch(0.72 0.19 145 / 0.2)"
                }}
                transition={{ duration: 0.05 }}
              />
            ))}
          </div>
          <input
            type="range"
            min="20"
            max="200"
            value={clockA.freq}
            onChange={(e) => setClockA({ ...clockA, freq: parseInt(e.target.value) })}
            className="w-full"
          />
        </div>

        {/* Clock B */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-blue-400">Clock Domain B</span>
            <span className="text-sm font-mono">{clockB.freq} MHz</span>
          </div>
          <div className="h-12 bg-muted/30 rounded-lg overflow-hidden flex">
            {Array.from({ length: 50 }).map((_, i) => (
              <motion.div
                key={i}
                className="flex-1"
                animate={{
                  backgroundColor: getSignal(clockB.freq, clockB.phase) 
                    ? "oklch(0.65 0.18 230)" 
                    : "oklch(0.65 0.18 230 / 0.2)"
                }}
                transition={{ duration: 0.05 }}
              />
            ))}
          </div>
          <input
            type="range"
            min="20"
            max="200"
            value={clockB.freq}
            onChange={(e) => setClockB({ ...clockB, freq: parseInt(e.target.value) })}
            className="w-full"
          />
        </div>

        {/* CDC Warning */}
        <div className="p-4 bg-amber-400/10 border border-amber-400/30 rounded-xl">
          <div className="flex items-center gap-2 text-amber-400 font-medium mb-2">
            <Zap className="w-4 h-4" />
            Clock Domain Crossing (CDC)
          </div>
          <p className="text-sm text-muted-foreground">
            When signals cross between clock domains with different frequencies, special care must be taken 
            to avoid metastability. The ratio of {clockA.freq}:{clockB.freq} MHz creates potential timing hazards.
          </p>
        </div>
      </div>
    </div>
  );
}

// Signal Timing Analysis
function SignalTimingAnalysis() {
  const [setupTime, setSetupTime] = useState(2);
  const [holdTime, setHoldTime] = useState(1);
  const [clockPeriod, setClockPeriod] = useState(10);

  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-400/10 flex items-center justify-center">
            <Activity className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h3 className="font-semibold">Signal Timing Analysis</h3>
            <p className="text-sm text-muted-foreground">Setup and hold time visualization</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Timing Diagram */}
        <div className="space-y-4">
          {/* Clock */}
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Clock</span>
            <div className="h-8 bg-muted/30 rounded flex">
              {Array.from({ length: 20 }).map((_, i) => (
                <div
                  key={i}
                  className={`flex-1 ${i % 2 === 0 ? "bg-primary" : "bg-muted"}`}
                />
              ))}
            </div>
          </div>

          {/* Data Signal */}
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground">Data Signal</span>
            <div className="h-8 bg-muted/30 rounded relative overflow-hidden">
              <div className="absolute inset-0 flex">
                {Array.from({ length: 20 }).map((_, i) => (
                  <div
                    key={i}
                    className={`flex-1 ${i < 5 ? "bg-blue-400" : i < 10 ? "bg-muted" : i < 15 ? "bg-blue-400" : "bg-muted"}`}
                  />
                ))}
              </div>
              {/* Setup Window */}
              <div 
                className="absolute top-0 right-0 h-full bg-green-400/30 border-r-2 border-green-400"
                style={{ width: `${(setupTime / clockPeriod) * 100}%` }}
              />
              {/* Hold Window */}
              <div 
                className="absolute top-0 left-0 h-full bg-red-400/30 border-l-2 border-red-400"
                style={{ width: `${(holdTime / clockPeriod) * 100}%` }}
              />
            </div>
          </div>

          {/* Legend */}
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-400/30 border border-green-400" />
              <span className="text-muted-foreground">Setup Time</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-red-400/30 border border-red-400" />
              <span className="text-muted-foreground">Hold Time</span>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="space-y-4">
          <h4 className="font-medium flex items-center gap-2">
            <Timer className="w-4 h-4" /> Timing Parameters
          </h4>

          <div className="space-y-3">
            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-muted-foreground">Setup Time</span>
                <span className="font-mono text-green-400">{setupTime}ns</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="5"
                step="0.5"
                value={setupTime}
                onChange={(e) => setSetupTime(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-muted-foreground">Hold Time</span>
                <span className="font-mono text-red-400">{holdTime}ns</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="5"
                step="0.5"
                value={holdTime}
                onChange={(e) => setHoldTime(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="text-muted-foreground">Clock Period</span>
                <span className="font-mono text-primary">{clockPeriod}ns</span>
              </div>
              <input
                type="range"
                min="5"
                max="20"
                value={clockPeriod}
                onChange={(e) => setClockPeriod(parseInt(e.target.value))}
                className="w-full"
              />
            </div>
          </div>

          {/* Timing Summary */}
          <div className="p-4 bg-muted/30 rounded-xl space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Max Frequency</span>
              <span className="font-mono text-primary">{(1000 / clockPeriod).toFixed(0)} MHz</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Timing Margin</span>
              <span className="font-mono text-green-400">{clockPeriod - setupTime - holdTime}ns</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function TimingPlaygroundPage() {
  const [activePlayground, setActivePlayground] = useState("traffic");

  const renderPlayground = useCallback(() => {
    switch (activePlayground) {
      case "traffic":
        return <TrafficLightSimulator />;
      case "dominoes":
        return <DominoSimulator />;
      case "clocks":
        return <ClockDomainVisualizer />;
      case "signals":
        return <SignalTimingAnalysis />;
      default:
        return <TrafficLightSimulator />;
    }
  }, [activePlayground]);

  return (
    <div className="animated-gradient-bg min-h-screen">
      {/* Hero Section */}
      <section className="hero-gradient pt-20 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2 mb-6">
              <Clock className="w-4 h-4 text-primary" />
              <span className="text-primary text-sm font-medium">Interactive Timing Playground</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="gradient-text">Hands-On Timing</span>
              <br />
              <span className="text-foreground">Simulations</span>
            </h1>

            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Interactive experiments that make timing concepts click. 
              Build, simulate, and understand how digital timing really works.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Playground Selector */}
      <section className="px-4 sm:px-6 lg:px-8 pb-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-wrap justify-center gap-3">
            {playgrounds.map((playground) => (
              <button
                key={playground.id}
                onClick={() => setActivePlayground(playground.id)}
                className={`flex items-center gap-2 px-4 py-3 rounded-xl border transition-all duration-200 ${
                  activePlayground === playground.id
                    ? `${playground.color} bg-current/10 border-current`
                    : "border-border text-muted-foreground hover:border-foreground/30 hover:bg-muted/30"
                }`}
              >
                <playground.icon className="w-5 h-5" />
                <span className="font-medium">{playground.title}</span>
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Active Playground */}
      <section className="px-4 sm:px-6 lg:px-8 pb-12">
        <div className="max-w-5xl mx-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={activePlayground}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderPlayground()}
            </motion.div>
          </AnimatePresence>
        </div>
      </section>

      {/* Learning Resources */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-2xl font-bold mb-4">Continue Learning</h2>
            <p className="text-muted-foreground">Deepen your understanding with structured lessons</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="bg-card rounded-2xl border border-border p-6 card-hover group"
            >
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
                <Layers className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">Clock Domain Crossing</h3>
              <p className="text-muted-foreground text-sm mb-4">
                Learn how to safely transfer data between different clock domains.
              </p>
              <Link
                href="/learning#clock-domains"
                className="flex items-center gap-2 text-primary text-sm font-medium group-hover:gap-3 transition-all"
              >
                Start Lesson <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="bg-card rounded-2xl border border-border p-6 card-hover group"
            >
              <div className="w-12 h-12 rounded-xl bg-blue-400/10 flex items-center justify-center mb-4">
                <Timer className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="font-semibold mb-2">Setup & Hold Analysis</h3>
              <p className="text-muted-foreground text-sm mb-4">
                Master timing constraints for reliable digital design.
              </p>
              <Link
                href="/learning#timing-basics"
                className="flex items-center gap-2 text-blue-400 text-sm font-medium group-hover:gap-3 transition-all"
              >
                Start Lesson <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="bg-card rounded-2xl border border-border p-6 card-hover group"
            >
              <div className="w-12 h-12 rounded-xl bg-amber-400/10 flex items-center justify-center mb-4">
                <Zap className="w-6 h-6 text-amber-400" />
              </div>
              <h3 className="font-semibold mb-2">Pipeline Design</h3>
              <p className="text-muted-foreground text-sm mb-4">
                Build efficient pipelines for maximum throughput.
              </p>
              <Link
                href="/professional#pipeline"
                className="flex items-center gap-2 text-amber-400 text-sm font-medium group-hover:gap-3 transition-all"
              >
                Explore Tools <ArrowRight className="w-4 h-4" />
              </Link>
            </motion.div>
          </div>
        </div>
      </section>
    </div>
  );
}
