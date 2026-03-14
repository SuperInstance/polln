"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import {
  Download, Shield, Zap, Cpu, Code, Users, ArrowRight,
  Github, Gamepad2, Clock, GraduationCap, Briefcase, Rocket,
  Sparkles, Play, ChevronRight, Star, Globe, Heart, BookOpen,
  Layers, Box, Microscope
} from "lucide-react";

// Particle component for hero background
function Particles() {
  return (
    <div className="particle-field">
      {[...Array(20)].map((_, i) => (
        <div
          key={i}
          className="particle"
          style={{
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 20}s`,
            animationDuration: `${15 + Math.random() * 10}s`,
          }}
        />
      ))}
    </div>
  );
}

// Animated counter component
function AnimatedCounter({ end, suffix = "", duration = 2 }: { end: number; suffix?: string; duration?: number }) {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let startTime: number;
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / (duration * 1000), 1);
      setCount(Math.floor(progress * end));
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [end, duration]);
  
  return <span>{count}{suffix}</span>;
}

// Age group data
const ageGroups = [
  {
    id: "young",
    title: "Young Learners",
    age: "4-10",
    icon: Gamepad2,
    color: "blue",
    description: "Fun games teaching timing through traffic lights, musical chairs, and domino chains.",
    features: ["Traffic Light Games", "Musical Chairs Timing", "Domino Chains"],
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    id: "middle",
    title: "Middle School",
    age: "11-14",
    icon: Clock,
    color: "purple",
    description: "Animation timing, music beat programming, and traffic flow coordination.",
    features: ["Animation Frames", "Beat Programming", "Traffic Systems"],
    gradient: "from-purple-500 to-pink-500",
  },
  {
    id: "high",
    title: "High School",
    age: "15-18",
    icon: GraduationCap,
    color: "amber",
    description: "Sports replay analysis, assembly line optimization, digital logic timing.",
    features: ["Digital Logic Intro", "Timing Analysis", "System Design"],
    gradient: "from-amber-500 to-orange-500",
  },
  {
    id: "pro",
    title: "Professional",
    age: "18+",
    icon: Briefcase,
    color: "green",
    description: "FPGA timing closure, CDC analysis, pipeline optimization, real chip design.",
    features: ["FPGA Timing", "CDC Analysis", "Pipeline Design"],
    gradient: "from-green-500 to-emerald-500",
  },
];

// Main paths - NOW WITH THREE BUTTONS
const mainPaths = [
  {
    id: "learning",
    title: "Start Learning",
    subtitle: "All Ages",
    icon: BookOpen,
    color: "blue",
    description: "Interactive lessons for everyone from young learners to professionals",
    href: "/learning",
    gradient: "from-blue-600 to-cyan-600",
  },
  {
    id: "chip-design",
    title: "Chip Design & Technology",
    subtitle: "Build Real Hardware",
    icon: Cpu,
    color: "green",
    description: "Voxel playground for prototyping real chip designs with AI co-inventor Lucineer",
    href: "/chip-design",
    gradient: "from-green-600 to-emerald-600",
    featured: true,
  },
  {
    id: "playground",
    title: "Timing Playground",
    subtitle: "Simulate & Experiment",
    icon: Gamepad2,
    color: "purple",
    description: "Interactive timing simulators that work offline",
    href: "/timing-playground",
    gradient: "from-purple-600 to-pink-600",
  },
];

// Features
const features = [
  {
    icon: Gamepad2,
    title: "Game-Like Learning",
    description: "Master complex concepts through engaging games. Learning happens naturally.",
  },
  {
    icon: Users,
    title: "Cross-Generational",
    description: "Parents and children learn together, each at their own level.",
  },
  {
    icon: Globe,
    title: "Works Offline",
    description: "Download everything. Learn anywhere, anytime. No internet needed.",
  },
  {
    icon: Shield,
    title: "Open Source",
    description: "MIT licensed, fully free. Use, modify, and share without limits.",
  },
  {
    icon: Cpu,
    title: "Real Chip Design",
    description: "From voxel prototype to Cadence-ready schemas.",
  },
  {
    icon: Zap,
    title: "Instant Start",
    description: "No signup required. Works immediately on page load.",
  },
];

export default function Home() {
  const [activeDemo, setActiveDemo] = useState(0);

  // Cycle through demo states
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveDemo((prev) => (prev + 1) % 3);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="animated-bg min-h-screen overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative pt-28 md:pt-36 pb-16 md:pb-24 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Background Effects */}
        <Particles />
        <div className="absolute inset-0 grid-pattern opacity-30" />
        <div className="hero-orb hero-orb-green w-[600px] h-[600px] -top-40 -left-40" />
        <div className="hero-orb hero-orb-blue w-[500px] h-[500px] top-1/2 -right-20" />
        <div className="hero-orb hero-orb-purple w-[400px] h-[400px] bottom-0 left-1/3" />
        
        <div className="max-w-7xl mx-auto relative">
          {/* Pre-headline Badge */}
          <div className="flex justify-center mb-8">
            <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 pulse-glow">
              <Sparkles className="w-4 h-4 text-green-400" />
              <span className="text-green-400 text-sm font-medium">
                Free Forever • No Signup • Works Offline
              </span>
            </div>
          </div>

          {/* Main Headline */}
          <div className="text-center mb-10">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-bold mb-6 leading-tight">
              <span className="block text-white mb-2">Learn AI Through</span>
              <span className="gradient-text-animated">Timing & Play</span>
            </h1>
            
            <p className="text-xl sm:text-2xl text-gray-300 max-w-3xl mx-auto mb-8 leading-relaxed">
              From playground games to professional chip design. 
              <span className="text-green-400"> Master timing concepts that power AI</span> through 
              interactive simulations anyone can understand.
            </p>

            {/* THREE MAIN BUTTONS */}
            <div className="flex flex-col items-center gap-4 mb-12">
              {/* Center Featured Button - Chip Design */}
              <Link
                href="/chip-design"
                className="group relative w-full max-w-md"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
                <div className="relative flex items-center justify-center gap-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-8 py-5 rounded-2xl font-semibold text-lg transition-all shadow-xl">
                  <Cpu className="w-7 h-7" />
                  <div className="text-left">
                    <div className="text-xl font-bold">Chip Design & Technology</div>
                    <div className="text-sm text-green-100">Build real hardware with Lucineer AI</div>
                  </div>
                  <ArrowRight className="w-6 h-6 group-hover:translate-x-2 transition-transform" />
                </div>
              </Link>
              
              {/* Two Secondary Buttons */}
              <div className="flex flex-wrap justify-center gap-4 w-full max-w-2xl">
                <Link
                  href="/learning"
                  className="group flex-1 min-w-[200px] flex items-center justify-center gap-3 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-white px-6 py-4 rounded-xl font-semibold transition-all"
                >
                  <BookOpen className="w-5 h-5 text-blue-400" />
                  Start Learning
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>
                
                <Link
                  href="/timing-playground"
                  className="group flex-1 min-w-[200px] flex items-center justify-center gap-3 bg-purple-600/20 hover:bg-purple-600/30 border border-purple-500/30 text-white px-6 py-4 rounded-xl font-semibold transition-all"
                >
                  <Gamepad2 className="w-5 h-5 text-purple-400" />
                  Timing Playground
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto">
              {[
                { value: "4", label: "Age Groups", suffix: "" },
                { value: "100", label: "Interactive Lessons", suffix: "+" },
                { value: "0", label: "Cost (Free)", suffix: "$" },
                { value: "∞", label: "Offline Access", suffix: "" },
              ].map((stat) => (
                <div
                  key={stat.label}
                  className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-4 border border-dark-600 hover:border-green-500/30 transition-all"
                >
                  <div className="text-2xl font-bold text-green-400">
                    {stat.value === "∞" ? stat.value : <AnimatedCounter end={parseInt(stat.value)} suffix={stat.suffix} />}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Interactive Demo Preview */}
          <div className="max-w-4xl mx-auto">
            <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden shadow-2xl">
              {/* Demo Header */}
              <div className="flex items-center gap-2 px-4 py-3 bg-dark-700/50 border-b border-dark-600">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                </div>
                <span className="ml-2 text-sm text-gray-400">Live Preview — Traffic Light Simulator</span>
              </div>
              
              {/* Demo Content */}
              <div className="p-8 flex flex-col md:flex-row items-center gap-8">
                {/* Traffic Light */}
                <div className="flex flex-col items-center">
                  <div className="bg-dark-700 rounded-2xl p-4 space-y-3">
                    <div className={`w-14 h-14 rounded-full transition-all duration-500 ${
                      activeDemo === 0 ? "bg-red-500 shadow-lg shadow-red-500/50" : "bg-dark-600"
                    }`} />
                    <div className={`w-14 h-14 rounded-full transition-all duration-500 ${
                      activeDemo === 1 ? "bg-yellow-500 shadow-lg shadow-yellow-500/50" : "bg-dark-600"
                    }`} />
                    <div className={`w-14 h-14 rounded-full transition-all duration-500 ${
                      activeDemo === 2 ? "bg-green-500 shadow-lg shadow-green-500/50" : "bg-dark-600"
                    }`} />
                  </div>
                  <p className="mt-3 text-sm text-gray-500">
                    {activeDemo === 0 ? "RED — Wait" : activeDemo === 1 ? "YELLOW — Prepare" : "GREEN — Go!"}
                  </p>
                </div>
                
                {/* Code Preview */}
                <div className="flex-1 font-mono text-sm">
                  <div className="text-gray-500">// State Machine Example</div>
                  <div className="mt-2">
                    <span className="text-purple-400">states</span>: RED → GREEN → YELLOW
                  </div>
                  <div className="mt-1">
                    <span className="text-purple-400">current</span>: <span className="text-green-400">{activeDemo === 0 ? "RED" : activeDemo === 1 ? "YELLOW" : "GREEN"}</span>
                  </div>
                  <div className="mt-4 text-gray-500">
                    // Same pattern in CPUs: FETCH → DECODE → EXECUTE
                  </div>
                </div>
              </div>
              
              {/* Demo Footer */}
              <div className="px-6 py-4 bg-dark-700/30 border-t border-dark-600 flex items-center justify-between">
                <span className="text-sm text-gray-500">
                  This is a state machine — the foundation of all computing
                </span>
                <Link
                  href="/timing-playground"
                  className="flex items-center gap-2 text-green-400 hover:text-green-300 font-medium text-sm"
                >
                  Open Full Simulator <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Chip Design Feature Highlight */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-green-900/20 via-dark-900 to-emerald-900/20">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-4 py-2 mb-6">
                <Microscope className="w-4 h-4 text-green-400" />
                <span className="text-green-400 text-sm font-medium">New: Voxel Chip Design Studio</span>
              </div>
              
              <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                Design Real Chips in a <span className="gradient-text">Voxel Playground</span>
              </h2>
              
              <p className="text-gray-400 text-lg mb-6 leading-relaxed">
                Meet <strong className="text-green-400">Lucineer</strong>, your AI co-inventor. Start with a use case 
                (like a smart downrigger for Sitka fishing), and progressively iterate from high-level 
                vision to detailed chip schemas ready for Cadence and Synopsis.
              </p>
              
              <div className="space-y-4 mb-8">
                {[
                  { icon: Box, text: "3D voxel building for hardware prototyping" },
                  { icon: Globe, text: "Real-world data integration (maps, charts, terrain)" },
                  { icon: Layers, text: "Progressive abstraction: Vision → Chip Schema" },
                  { icon: Code, text: "Export to EDA tools (Cadence, Synopsis)" },
                ].map((item) => (
                  <div key={item.text} className="flex items-center gap-3 text-gray-300">
                    <div className="w-8 h-8 rounded-lg bg-green-500/10 flex items-center justify-center">
                      <item.icon className="w-4 h-4 text-green-400" />
                    </div>
                    <span>{item.text}</span>
                  </div>
                ))}
              </div>
              
              <Link
                href="/chip-design"
                className="inline-flex items-center gap-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-lg"
              >
                <Cpu className="w-5 h-5" />
                Open Chip Design Studio
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
            
            <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
              {/* Mock voxel editor preview */}
              <div className="p-4 border-b border-dark-600 bg-dark-700/50">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500" />
                  <div className="w-3 h-3 rounded-full bg-green-500" />
                  <span className="ml-3 text-sm text-gray-400">Lucineer Co-Inventor</span>
                </div>
              </div>
              
              <div className="p-6 font-mono text-xs">
                <div className="text-gray-500 mb-4">// Progressive Iteration Example</div>
                
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="text-amber-400">Layer 0</span>
                    <span className="text-gray-500">→</span>
                    <span className="text-gray-300">"Smart downrigger for Sitka fishing"</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-amber-400">Layer 1</span>
                    <span className="text-gray-500">→</span>
                    <span className="text-gray-300">"Depth sensor → MCU → Motor controller"</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-amber-400">Layer 2</span>
                    <span className="text-gray-500">→</span>
                    <span className="text-gray-300">"ESP32-C3 + MS5837 sensor"</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-amber-400">Layer 3</span>
                    <span className="text-gray-500">→</span>
                    <span className="text-gray-300">"Circular PCB, 50mm, IP68 housing"</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-amber-400">Layer 4</span>
                    <span className="text-gray-500">→</span>
                    <span className="text-gray-300">"BitNet 0.73B, Int4, 200KB"</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-amber-400">Layer 5</span>
                    <span className="text-gray-500">→</span>
                    <span className="text-green-400">"chip.v + constraints.sdc"</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Age Groups Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-dark-800/50 to-transparent" />
        
        <div className="max-w-7xl mx-auto relative">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
              One Platform, <span className="gradient-text">All Ages</span>
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              The same timing concepts taught through age-appropriate experiences.
              Everyone learns the fundamentals — just at different depths.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {ageGroups.map((group) => (
              <Link
                key={group.id}
                href={`/learning?age=${group.id}`}
                className="group relative bg-dark-800/60 backdrop-blur-sm rounded-2xl p-6 border border-dark-600 hover:border-green-500/30 transition-all duration-300 overflow-hidden"
              >
                {/* Gradient Overlay */}
                <div className={`absolute inset-0 bg-gradient-to-br ${group.gradient} opacity-0 group-hover:opacity-5 transition-opacity`} />
                
                {/* Icon */}
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${group.gradient} bg-opacity-10 flex items-center justify-center mb-4`}>
                  <group.icon className="w-7 h-7 text-white" />
                </div>
                
                {/* Content */}
                <div className="relative">
                  <h3 className="text-xl font-semibold text-white mb-1">{group.title}</h3>
                  <p className="text-sm text-gray-500 mb-4">Ages {group.age}</p>
                  <p className="text-sm text-gray-400 mb-4 leading-relaxed">{group.description}</p>
                  
                  <ul className="space-y-2">
                    {group.features.map((feature) => (
                      <li key={feature} className="flex items-center gap-2 text-sm text-gray-500">
                        <ChevronRight className="w-4 h-4 text-green-400" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Built for Everyone</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Accessible. Educational. Offline-capable. Open source.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <div 
                key={feature.title}
                className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-6 border border-dark-600 hover:border-green-500/30 transition-all"
              >
                <feature.icon className="w-8 h-8 text-green-400 mb-4" />
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Offline-First Banner */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-green-900/20 via-dark-900 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-green-500/10 mb-6">
            <Download className="w-8 h-8 text-green-400" />
          </div>
          
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Take It All Offline
          </h2>
          <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto leading-relaxed">
            Download the entire platform — simulators, lessons, documentation — and learn anywhere. 
            No internet required after download. Your progress saved locally.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/downloads"
              className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-lg"
            >
              <Download className="w-5 h-5" />
              Download Everything
            </Link>
            <Link
              href="/api-connect"
              className="flex items-center gap-2 bg-dark-700/80 hover:bg-dark-600 text-white px-8 py-4 rounded-xl font-semibold transition-all border border-dark-500"
            >
              <Zap className="w-5 h-5" />
              Connect AI APIs
            </Link>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-t border-dark-700">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">
            Ready to Start Learning?
          </h2>
          <p className="text-gray-400 text-lg mb-8">
            Jump right in — no signup, no credit card, no limits.
          </p>
          <Link
            href="/chip-design"
            className="inline-flex items-center gap-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-10 py-5 rounded-xl font-semibold text-lg transition-all shadow-lg hover:shadow-green-500/30"
          >
            <Rocket className="w-6 h-6" />
            Start Your Journey Now
          </Link>
        </div>
      </section>
    </div>
  );
}
