"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Play, Pause, RotateCcw, SkipForward, Settings, Maximize2,
  Clock, Zap, Layers, Box, ChevronRight, ArrowRight
} from "lucide-react";

// Traffic Light Simulator
function TrafficLightSimulator() {
  const [state, setState] = useState(0); // 0: RED, 1: YELLOW, 2: GREEN
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState([3000, 1500, 4000]); // RED, YELLOW, GREEN durations

  useEffect(() => {
    if (isPlaying) {
      const timer = setTimeout(() => {
        setState((prev) => (prev + 1) % 3);
      }, duration[state]);
      return () => clearTimeout(timer);
    }
  }, [state, isPlaying, duration]);

  const colors = [
    { name: "RED", color: "#ef4444", meaning: "Stop" },
    { name: "YELLOW", color: "#f59e0b", meaning: "Prepare" },
    { name: "GREEN", color: "#22c55e", meaning: "Go" },
  ];

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="ml-2 font-semibold">Traffic Light Simulator</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 rounded-lg bg-green-600 hover:bg-green-500 transition-colors"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={() => { setState(0); setIsPlaying(false); }}
            className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="p-8 flex flex-col md:flex-row items-center gap-8">
        {/* Traffic Light Visual */}
        <div className="flex flex-col items-center">
          <div className="bg-dark-700 rounded-2xl p-4 space-y-3">
            {colors.map((color, index) => (
              <div
                key={color.name}
                className={`w-16 h-16 rounded-full transition-all duration-500 ${
                  state === index
                    ? `shadow-lg`
                    : "bg-dark-600"
                }`}
                style={{
                  backgroundColor: state === index ? color.color : undefined,
                  boxShadow: state === index ? `0 0 30px ${color.color}50` : undefined,
                }}
              />
            ))}
          </div>
          <p className="mt-4 text-center">
            <span className="text-lg font-semibold" style={{ color: colors[state].color }}>
              {colors[state].name}
            </span>
            <span className="text-gray-500 text-sm block">{colors[state].meaning}</span>
          </p>
        </div>

        {/* State Diagram */}
        <div className="flex-1 font-mono text-sm">
          <div className="text-gray-500 mb-4">// State Machine Definition</div>
          <div className="bg-dark-700/50 rounded-lg p-4 space-y-2">
            <div>
              <span className="text-purple-400">states</span>: [RED, YELLOW, GREEN]
            </div>
            <div>
              <span className="text-purple-400">current</span>: <span style={{ color: colors[state].color }}>{colors[state].name}</span>
            </div>
            <div className="mt-4 pt-4 border-t border-dark-600">
              <span className="text-gray-500">// Transitions</span>
              <div className="mt-2 text-xs">
                RED ({duration[0]}ms) → GREEN ({duration[2]}ms) → YELLOW ({duration[1]}ms) → RED
              </div>
            </div>
          </div>
          <div className="mt-4 text-gray-500">
            // Same pattern in CPUs: FETCH → DECODE → EXECUTE
          </div>
        </div>
      </div>

      {/* Duration Controls */}
      <div className="px-8 pb-6">
        <div className="grid grid-cols-3 gap-4">
          {colors.map((color, index) => (
            <div key={color.name} className="text-center">
              <label className="text-xs text-gray-500 block mb-2">{color.name} Duration (ms)</label>
              <input
                type="range"
                min="500"
                max="10000"
                step="500"
                value={duration[index]}
                onChange={(e) => {
                  const newDuration = [...duration];
                  newDuration[index] = parseInt(e.target.value);
                  setDuration(newDuration);
                }}
                className="w-full accent-green-500"
              />
              <span className="text-sm text-gray-400">{duration[index]}ms</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Domino Chain Simulator
function DominoSimulator() {
  const [dominoes, setDominoes] = useState(Array(10).fill(false));
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (isPlaying) {
      const currentDomino = dominoes.findIndex((d) => !d);
      if (currentDomino === -1) {
        setIsPlaying(false);
        return;
      }
      const timer = setTimeout(() => {
        const newDominoes = [...dominoes];
        newDominoes[currentDomino] = true;
        setDominoes(newDominoes);
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [dominoes, isPlaying]);

  const reset = () => {
    setDominoes(Array(10).fill(false));
    setIsPlaying(false);
  };

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Box className="w-5 h-5 text-purple-400" />
          <span className="font-semibold">Domino Chain Simulator</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => isPlaying ? setIsPlaying(false) : setIsPlaying(true)}
            className="p-2 rounded-lg bg-purple-600 hover:bg-purple-500 transition-colors"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={reset}
            className="p-2 rounded-lg bg-dark-600 hover:bg-dark-500 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="p-8">
        <div className="flex items-end justify-center gap-2 mb-6">
          {dominoes.map((fallen, index) => (
            <div
              key={index}
              className={`w-8 h-16 rounded transition-all duration-300 ${
                fallen
                  ? "bg-purple-500 rotate-90 origin-bottom"
                  : "bg-dark-600 hover:bg-purple-600 cursor-pointer"
              }`}
              onClick={() => {
                if (!isPlaying) {
                  const newDominoes = [...dominoes];
                  newDominoes[index] = !newDominoes[index];
                  setDominoes(newDominoes);
                }
              }}
            />
          ))}
        </div>
        <div className="text-center text-gray-500 text-sm">
          Click a domino to toggle, or press Play to watch the chain reaction
        </div>
      </div>
    </div>
  );
}

export default function TimingPlaygroundPage() {
  const [activeSim, setActiveSim] = useState("traffic");

  return (
    <div className="animated-bg min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-pink-500 to-rose-500 flex items-center justify-center">
              <Clock className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold">Timing Playground</h1>
              <p className="text-sm text-gray-500">Interactive timing simulations</p>
            </div>
          </div>

          <p className="text-xl text-gray-300 max-w-3xl">
            Explore timing concepts through interactive simulations. 
            These work completely offline — no internet required.
          </p>
        </div>

        {/* Simulator Tabs */}
        <div className="flex gap-3 mb-8">
          <button
            onClick={() => setActiveSim("traffic")}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              activeSim === "traffic"
                ? "bg-green-500/20 text-green-400 border border-green-500/30"
                : "bg-dark-700/50 text-gray-400 hover:text-white"
            }`}
          >
            Traffic Light
          </button>
          <button
            onClick={() => setActiveSim("domino")}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              activeSim === "domino"
                ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                : "bg-dark-700/50 text-gray-400 hover:text-white"
            }`}
          >
            Domino Chain
          </button>
        </div>

        {/* Active Simulator */}
        {activeSim === "traffic" && <TrafficLightSimulator />}
        {activeSim === "domino" && <DominoSimulator />}

        {/* Learning Connection */}
        <div className="mt-8 bg-gradient-to-r from-green-900/20 via-dark-800 to-emerald-900/20 rounded-2xl p-6 border border-green-500/20">
          <div className="flex items-center gap-4">
            <Zap className="w-8 h-8 text-green-400" />
            <div className="flex-1">
              <h3 className="font-semibold mb-1">Ready to Learn More?</h3>
              <p className="text-sm text-gray-400">
                These simulators teach the same timing concepts used in CPU design, 
                FPGA programming, and AI chip architecture.
              </p>
            </div>
            <Link
              href="/learning"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white transition-colors"
            >
              Start Learning
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
