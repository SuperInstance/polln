"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Play,
  Pause,
  RotateCcw,
  Clock,
  ArrowRight,
  Zap,
  AlertTriangle,
  CheckCircle,
  Settings,
} from "lucide-react";

export default function TimingPlaygroundPage() {
  const [trafficState, setTrafficState] = useState<"red" | "green" | "yellow">("red");
  const [trafficTimer, setTrafficTimer] = useState(30);
  const [isPlaying, setIsPlaying] = useState(false);
  const [dominoCount, setDominoCount] = useState(5);
  const [dominoTriggered, setDominoTriggered] = useState<number[]>([]);

  // Traffic Light Timer
  useEffect(() => {
    if (!isPlaying) return;
    
    const interval = setInterval(() => {
      setTrafficTimer((prev) => {
        if (prev <= 1) {
          setTrafficState((state) => {
            if (state === "red") return "green";
            if (state === "green") return "yellow";
            return "red";
          });
          return trafficState === "red" ? 25 : trafficState === "green" ? 5 : 30;
        }
        return prev - 1;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [isPlaying, trafficState]);

  // Domino Effect
  useEffect(() => {
    if (dominoTriggered.length === 0 || dominoTriggered.length >= dominoCount) return;
    
    const timeout = setTimeout(() => {
      setDominoTriggered((prev) => [...prev, prev[prev.length - 1] + 1]);
    }, 300);

    return () => clearTimeout(timeout);
  }, [dominoTriggered, dominoCount]);

  const triggerDominoes = () => {
    setDominoTriggered([0]);
  };

  const resetDominoes = () => {
    setDominoTriggered([]);
  };

  return (
    <div className="animated-bg min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 mb-6">
            <Zap className="w-4 h-4 text-green-400" />
            <span className="text-green-400 text-sm font-medium">Interactive Simulators</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">Timing Playground</span>
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto text-lg">
            Interactive simulators to explore timing concepts hands-on. 
            Experiment, visualize, and learn by doing.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Traffic Light Simulator */}
          <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl border border-dark-600 overflow-hidden">
            <div className="p-6 border-b border-dark-600">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
                    <Clock className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold">Traffic Light State Machine</h2>
                    <p className="text-gray-500 text-sm">Learn FSM through traffic lights</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors"
                  >
                    {isPlaying ? (
                      <Pause className="w-5 h-5 text-amber-400" />
                    ) : (
                      <Play className="w-5 h-5 text-green-400" />
                    )}
                  </button>
                  <button
                    onClick={() => {
                      setTrafficState("red");
                      setTrafficTimer(30);
                      setIsPlaying(false);
                    }}
                    className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors"
                  >
                    <RotateCcw className="w-5 h-5 text-gray-400" />
                  </button>
                </div>
              </div>
            </div>

            <div className="p-6">
              {/* Traffic Light Visual */}
              <div className="flex justify-center mb-6">
                <div className="bg-dark-700 rounded-2xl p-4 space-y-3">
                  <div
                    className={`w-16 h-16 rounded-full transition-all duration-300 ${
                      trafficState === "red"
                        ? "bg-red-500 shadow-lg shadow-red-500/50"
                        : "bg-dark-600"
                    }`}
                  />
                  <div
                    className={`w-16 h-16 rounded-full transition-all duration-300 ${
                      trafficState === "yellow"
                        ? "bg-yellow-500 shadow-lg shadow-yellow-500/50"
                        : "bg-dark-600"
                    }`}
                  />
                  <div
                    className={`w-16 h-16 rounded-full transition-all duration-300 ${
                      trafficState === "green"
                        ? "bg-green-500 shadow-lg shadow-green-500/50"
                        : "bg-dark-600"
                    }`}
                  />
                </div>
              </div>

              {/* Timer Display */}
              <div className="text-center mb-6">
                <div className="text-4xl font-bold text-white mb-2">
                  {trafficTimer}s
                </div>
                <div className="text-gray-500 text-sm capitalize">
                  Current State: <span className={`font-medium ${
                    trafficState === "red" ? "text-red-400" :
                    trafficState === "yellow" ? "text-yellow-400" : "text-green-400"
                  }`}>{trafficState}</span>
                </div>
              </div>

              {/* State Transition Diagram */}
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <div className="text-center text-gray-300">
                    ┌─────┐  30s   ┌───────┐  25s   ┌───────┐  5s
                  </div>
                  <div className="text-center text-gray-300">
                    │ RED │ ─────▶ │ GREEN │ ─────▶ │YELLOW │ ───┐
                  </div>
                  <div className="text-center text-gray-300">
                    └─────┘        └───────┘        └───────┘    │
                  </div>
                  <div className="text-center text-gray-300">
                    ▲                                           │
                  </div>
                  <div className="text-center text-gray-300">
                    └───────────────────────────────────────────┘
                  </div>
                  <div className="mt-2 text-green-400 text-center">
                    // Same pattern: CPU pipelines!
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Domino Chain Simulator */}
          <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl border border-dark-600 overflow-hidden">
            <div className="p-6 border-b border-dark-600">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/10 flex items-center justify-center">
                    <Zap className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold">Domino Chain Reaction</h2>
                    <p className="text-gray-500 text-sm">Learn propagation delay</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={triggerDominoes}
                    disabled={dominoTriggered.length > 0}
                    className="px-4 py-2 rounded-lg bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 transition-colors disabled:opacity-50"
                  >
                    <Play className="w-5 h-5" />
                  </button>
                  <button
                    onClick={resetDominoes}
                    className="p-2 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors"
                  >
                    <RotateCcw className="w-5 h-5 text-gray-400" />
                  </button>
                </div>
              </div>
            </div>

            <div className="p-6">
              {/* Domino Controls */}
              <div className="flex items-center gap-4 mb-6">
                <span className="text-gray-400 text-sm">Dominoes:</span>
                <input
                  type="range"
                  min="3"
                  max="10"
                  value={dominoCount}
                  onChange={(e) => {
                    setDominoCount(parseInt(e.target.value));
                    setDominoTriggered([]);
                  }}
                  className="flex-1"
                />
                <span className="text-white font-medium">{dominoCount}</span>
              </div>

              {/* Domino Visual */}
              <div className="flex items-end justify-center gap-2 mb-6 h-24">
                {Array.from({ length: dominoCount }).map((_, i) => (
                  <div
                    key={i}
                    className={`w-6 h-16 rounded transition-all duration-300 ${
                      dominoTriggered.includes(i)
                        ? "bg-purple-500 transform rotate-90 origin-bottom"
                        : "bg-dark-600 hover:bg-dark-500"
                    }`}
                    style={{
                      transitionDelay: dominoTriggered.includes(i) ? "0ms" : `${i * 50}ms`,
                    }}
                  />
                ))}
              </div>

              {/* Timing Info */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-dark-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-purple-400">
                    {dominoTriggered.length}
                  </div>
                  <div className="text-gray-500 text-sm">Triggered</div>
                </div>
                <div className="bg-dark-700 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold text-white">
                    {(dominoTriggered.length * 300)}ms
                  </div>
                  <div className="text-gray-500 text-sm">Total Delay</div>
                </div>
              </div>

              {/* Code Explanation */}
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <div className="text-purple-400">// Propagation Delay:</div>
                  <div className="text-gray-300">Domino 1 → Domino 2 → ... → Domino N</div>
                  <div className="text-gray-300 mt-1">t=0ms    t=300ms         t=(N-1)*300ms</div>
                  <div className="mt-2 text-green-400">// Same as: Signal propagation in chips!</div>
                  <div className="text-green-400">// Each gate adds ~10-100ps delay</div>
                </div>
              </div>
            </div>
          </div>

          {/* Setup/Hold Time Visualizer */}
          <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl border border-dark-600 overflow-hidden lg:col-span-2">
            <div className="p-6 border-b border-dark-600">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-amber-400" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold">Setup & Hold Time Visualization</h2>
                  <p className="text-gray-500 text-sm">See what happens when timing goes wrong</p>
                </div>
              </div>
            </div>

            <div className="p-6">
              {/* Timing Diagram */}
              <div className="code-block mb-6">
                <div className="code-content font-mono text-sm overflow-x-auto">
                  <pre className="text-gray-300">{`
         Setup Time (tsu)
         ◀──────────────▶
                        │
    ──────┬─────────────┼────────────┬──────
          │             │            │
          │ Data stable │   Clock    │
          │             │    edge    │
          │             │            │
    ──────┴─────────────┼────────────┴──────
                        │
                        ◀──────────────▶
                        Hold Time (th)

    ✅ Data stable during setup+hold → Correct capture
    ❌ Data changes during setup OR hold → Metastability!
                  `}</pre>
                </div>
              </div>

              {/* Explanation Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="font-medium text-green-400">Setup Time</span>
                  </div>
                  <p className="text-gray-400 text-sm">
                    Data must be stable <em>before</em> the clock edge. Like getting 
                    ready to catch a ball before it arrives.
                  </p>
                </div>

                <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-blue-400" />
                    <span className="font-medium text-blue-400">Hold Time</span>
                  </div>
                  <p className="text-gray-400 text-sm">
                    Data must stay stable <em>after</em> the clock edge. Like holding 
                    onto the ball after catching it.
                  </p>
                </div>

                <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="w-5 h-5 text-red-400" />
                    <span className="font-medium text-red-400">Violation</span>
                  </div>
                  <p className="text-gray-400 text-sm">
                    When either time is violated, the flip-flop can enter an 
                    uncertain state (metastability) - like a coin spinning.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-12 flex justify-center gap-4">
          <Link
            href="/learning"
            className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-6 py-3 rounded-xl font-medium transition-colors"
          >
            ← Back to Learning
          </Link>
          <Link
            href="/professional"
            className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-6 py-3 rounded-xl font-medium transition-all"
          >
            Professional Tools <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
