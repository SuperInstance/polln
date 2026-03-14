"use client";

import Link from "next/link";
import { useState, useEffect, useRef } from "react";
import {
  Download, Shield, Zap, Cpu, Code, Users, ArrowRight,
  Github, Gamepad2, Clock, GraduationCap, Briefcase, Rocket,
  Sparkles, Play, ChevronRight, Star, Globe, Heart, BookOpen,
  Layers, Box, Microscope, Lightbulb, Wand2, Lock,
  Factory, CircuitBoard, Server, Settings, Bot, Coffee,
  Puzzle, Brain, MessageSquare, Turtle, Rabbit,
  AlertTriangle, Laugh, Flame, Gauge,
  Activity, Eye, Fingerprint, Key, CloudOff, WifiOff,
  ServerOff, CheckCircle, Timer, Package, Bell,
  Calendar, ArrowUpRight, Terminal, Microchip
} from "lucide-react";

// ============================================
// PRODUCT LINEUP - INFERENCE CHIPS
// ============================================
const chipProductLine = [
  {
    name: "LUCI-1",
    tagline: "Entry-Level Inference",
    params: "1B Parameters",
    power: "0.5W",
    throughput: "15 tok/s",
    formFactor: "USB-C",
    price: "$15",
    availability: "Q2 2026",
    status: "coming-soon" as const,
    gradient: "from-blue-500 to-cyan-500",
    features: ["Plug-and-play AI", "No drivers required", "Edge deployment ready"]
  },
  {
    name: "LUCI-3",
    tagline: "Performance Inference",
    params: "3B Parameters",
    power: "3W",
    throughput: "80 tok/s",
    formFactor: "M.2 / PCIe",
    price: "$45",
    availability: "Q3 2026",
    status: "coming-soon" as const,
    gradient: "from-green-500 to-emerald-500",
    features: ["BitNet optimized", "Local inference", "90% offline capable"]
  },
  {
    name: "LUCI-7",
    tagline: "Professional Series",
    params: "7B Parameters",
    power: "8W",
    throughput: "50 tok/s",
    formFactor: "PCIe x4",
    price: "$120",
    availability: "Q4 2026",
    status: "coming-soon" as const,
    gradient: "from-purple-500 to-pink-500",
    features: ["Enterprise deployment", "High accuracy", "Custom model support"]
  },
  {
    name: "LUCI-CUSTOM",
    tagline: "Your Design",
    params: "Any Size",
    power: "Custom",
    throughput: "Optimized",
    formFactor: "Any",
    price: "Contact Us",
    availability: "Now",
    status: "available" as const,
    gradient: "from-amber-500 to-orange-500",
    features: ["Full custom design", "Our tools → Your chip", "IP ownership"]
  }
];

// ============================================
// ANIMATED CHIP SHOWCASE
// ============================================
function ChipShowcase() {
  const [activeChip, setActiveChip] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveChip(prev => (prev + 1) % chipProductLine.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const chip = chipProductLine[activeChip];
  
  return (
    <div className="relative bg-dark-800/80 backdrop-blur-xl rounded-3xl border border-dark-600 overflow-hidden">
      {/* Animated glow */}
      <div className="absolute inset-0 opacity-30">
        <div className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full blur-3xl animate-pulse ${
          chip.gradient.includes('blue') ? 'bg-blue-500' :
          chip.gradient.includes('green') ? 'bg-green-500' :
          chip.gradient.includes('purple') ? 'bg-purple-500' :
          'bg-amber-500'
        }`} />
      </div>
      
      <div className="p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className={`text-4xl font-bold bg-gradient-to-r ${chip.gradient} bg-clip-text text-transparent`}>
              {chip.name}
            </div>
            <div className="text-lg text-gray-400 mt-1">{chip.tagline}</div>
          </div>
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${
            chip.status === 'coming-soon' 
              ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' 
              : 'bg-green-500/20 text-green-400 border border-green-500/30'
          }`}>
            {chip.status === 'coming-soon' ? `Coming ${chip.availability}` : 'Available Now'}
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          {[
            { label: "Parameters", value: chip.params },
            { label: "Power", value: chip.power },
            { label: "Speed", value: chip.throughput },
            { label: "Form Factor", value: chip.formFactor },
            { label: "Target Price", value: chip.price },
          ].map((spec) => (
            <div key={spec.label} className="bg-dark-700/50 rounded-lg p-3 text-center">
              <div className="text-xs text-gray-500 mb-1">{spec.label}</div>
              <div className="text-sm font-semibold text-white">{spec.value}</div>
            </div>
          ))}
        </div>
        
        <div className="space-y-2">
          {chip.features.map((feature) => (
            <div key={feature} className="flex items-center gap-2 text-sm text-gray-400">
              <CheckCircle className="w-4 h-4 text-green-400" />
              {feature}
            </div>
          ))}
        </div>
      </div>
      
      {/* Chip navigation */}
      <div className="flex justify-center gap-2 pb-4">
        {chipProductLine.map((c, i) => (
          <button
            key={c.name}
            onClick={() => setActiveChip(i)}
            className={`w-2 h-2 rounded-full transition-all ${
              activeChip === i ? 'bg-white scale-125' : 'bg-gray-600 hover:bg-gray-500'
            }`}
          />
        ))}
      </div>
    </div>
  );
}

// ============================================
// PARTICLE BACKGROUND
// ============================================
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

// ============================================
// MAIN COMPONENT
// ============================================
export default function Home() {
  const [email, setEmail] = useState("");
  const [waitlistJoined, setWaitlistJoined] = useState(false);
  
  return (
    <div className="animated-bg min-h-screen overflow-x-hidden">
      {/* ============================================ */}
      {/* HERO SECTION - CHIP DESIGN PLATFORM */}
      {/* ============================================ */}
      <section className="relative pt-20 md:pt-28 pb-12 md:pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <Particles />
        <div className="absolute inset-0 grid-pattern opacity-20" />
        <div className="hero-orb hero-orb-green w-[600px] h-[600px] -top-40 -left-40" />
        <div className="hero-orb hero-orb-blue w-[500px] h-[500px] top-1/2 -right-20" />
        <div className="hero-orb hero-orb-purple w-[400px] h-[400px] bottom-0 left-1/3" />
        
        <div className="max-w-7xl mx-auto relative">
          {/* Product Badge */}
          <div className="flex justify-center mb-6">
            <div className="inline-flex items-center gap-2 bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/30 rounded-full px-5 py-2 pulse-glow">
              <Microchip className="w-4 h-4 text-green-400" />
              <span className="text-green-400 text-sm font-medium">
                Inference Chips Coming 2026
              </span>
              <Bell className="w-3 h-3 text-green-400 animate-pulse" />
            </div>
          </div>

          {/* Main Headline */}
          <div className="text-center mb-8">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-bold mb-4 leading-tight tracking-tight">
              <span className="block text-white mb-2">Design Inference Chips.</span>
              <span className="gradient-text-animated">Ship Real AI Hardware.</span>
            </h1>
            
            <p className="text-xl sm:text-2xl text-gray-300 max-w-3xl mx-auto mb-4 leading-relaxed font-light">
              From voxel blocks to silicon chips. Our platform teaches you to design 
              <span className="text-green-400 font-medium">mask-locked inference hardware</span>—then helps you ship it.
            </p>
            
            <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-8">
              Education is how we get there. But <span className="text-amber-400">the destination is chips you can hold.</span>
            </p>

            {/* THREE MAIN CTAs */}
            <div className="flex flex-wrap justify-center gap-4 w-full max-w-4xl mx-auto mb-10">
              {/* PRIMARY: Design Chips */}
              <Link
                href="/professional"
                className="group relative flex-1 min-w-[280px]"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity" />
                <div className="relative flex items-center justify-center gap-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-6 py-5 rounded-2xl font-semibold transition-all shadow-xl">
                  <Microchip className="w-6 h-6" />
                  <div className="text-left">
                    <div className="text-lg font-bold">Design Chips</div>
                    <div className="text-xs text-green-100">Professional Tools</div>
                  </div>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
              
              {/* SECONDARY: Learn How */}
              <Link
                href="/learning"
                className="group relative flex-1 min-w-[280px]"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl blur-xl opacity-40 group-hover:opacity-60 transition-opacity" />
                <div className="relative flex items-center justify-center gap-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white px-6 py-5 rounded-2xl font-semibold transition-all shadow-xl">
                  <BookOpen className="w-6 h-6" />
                  <div className="text-left">
                    <div className="text-lg font-bold">Learn How</div>
                    <div className="text-xs text-blue-100">Free Education</div>
                  </div>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
              
              {/* TERTIARY: Playground */}
              <Link
                href="/ternaryair"
                className="group relative flex-1 min-w-[280px]"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur-xl opacity-40 group-hover:opacity-60 transition-opacity" />
                <div className="relative flex items-center justify-center gap-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-6 py-5 rounded-2xl font-semibold transition-all shadow-xl">
                  <Gamepad2 className="w-6 h-6" />
                  <div className="text-left">
                    <div className="text-lg font-bold">Playground</div>
                    <div className="text-xs text-purple-100">Voxel Design</div>
                  </div>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-3xl mx-auto">
              <div className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-4 border border-dark-600">
                <div className="text-2xl font-bold text-green-400">2026</div>
                <div className="text-xs text-gray-500">Chips Ship</div>
              </div>
              <div className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-4 border border-dark-600">
                <div className="text-2xl font-bold text-cyan-400">3W</div>
                <div className="text-xs text-gray-500">Power Target</div>
              </div>
              <div className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-4 border border-dark-600">
                <div className="text-2xl font-bold text-amber-400">$15</div>
                <div className="text-xs text-gray-500">Starting Price</div>
              </div>
              <div className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-4 border border-dark-600">
                <div className="text-2xl font-bold text-green-400">100%</div>
                <div className="text-xs text-gray-500">Local Inference</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* PRODUCT LINEUP - INFERENCE CHIPS */}
      {/* ============================================ */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 text-xs text-gray-500 uppercase tracking-widest mb-4">
              <Package className="w-3 h-3" />
              Product Lineup
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              <span className="text-white">LUCI Series</span> Inference Chips
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Mask-locked neural inference in silicon. From USB dongles to PCIe cards to your custom designs.
            </p>
          </div>
          
          <ChipShowcase />
          
          {/* Pre-order CTA */}
          <div className="mt-8 text-center">
            <div className="inline-flex flex-col sm:flex-row items-center gap-4 p-6 rounded-2xl bg-gradient-to-r from-green-900/20 via-dark-800 to-emerald-900/20 border border-green-500/20">
              <div className="text-left">
                <div className="text-lg font-semibold text-white">Be First in Line</div>
                <div className="text-sm text-gray-400">Join the waitlist for early access to inference chips</div>
              </div>
              <Link
                href="/professional"
                className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-500 px-6 py-3 rounded-xl font-medium transition-all"
              >
                <Bell className="w-4 h-4" />
                Join Waitlist
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* VALUE PROPOSITION */}
      {/* ============================================ */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-transparent via-dark-800/50 to-transparent">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Local */}
            <div className="text-center p-8 rounded-2xl bg-dark-800/60 border border-dark-600">
              <div className="w-16 h-16 rounded-2xl bg-green-500/10 flex items-center justify-center mx-auto mb-6 border border-green-500/20">
                <Lock className="w-8 h-8 text-green-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">100% Local</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Inference happens on your device. No cloud dependency. 
                No monthly fees. No data leaves your control.
              </p>
            </div>
            
            {/* Efficient */}
            <div className="text-center p-8 rounded-2xl bg-dark-800/60 border border-dark-600">
              <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 flex items-center justify-center mx-auto mb-6 border border-cyan-500/20">
                <Zap className="w-8 h-8 text-cyan-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">116× Efficient</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                3W for 3B parameters. GPUs need 350W for the same task.
                Run AI on battery for hours, not minutes.
              </p>
            </div>
            
            {/* Secure */}
            <div className="text-center p-8 rounded-2xl bg-dark-800/60 border border-dark-600">
              <div className="w-16 h-16 rounded-2xl bg-amber-500/10 flex items-center justify-center mx-auto mb-6 border border-amber-500/20">
                <Shield className="w-8 h-8 text-amber-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">Air-Gapped Security</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Weights become silicon. No network interfaces. 
                Cannot be hacked remotely. Security by physics.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* EDUCATION SECTION - SECONDARY */}
      {/* ============================================ */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 text-xs text-gray-500 uppercase tracking-widest mb-4">
              <BookOpen className="w-3 h-3" />
              How We Get You There
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              <span className="text-white">Education is the On-Ramp</span>
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Most people don't know they can design chips. Our learning platform changes that.
              Start with games, end with silicon.
            </p>
          </div>
          
          {/* Learning Pathways */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { age: "4-10", title: "Tiny Humans", icon: Gamepad2, color: "blue" },
              { age: "11-14", title: "Curious Minds", icon: Puzzle, color: "purple" },
              { age: "15-18", title: "Future Engineers", icon: Lightbulb, color: "amber" },
              { age: "18+", title: "Professionals", icon: Briefcase, color: "green" },
            ].map((group) => (
              <Link
                key={group.age}
                href={`/learning?age=${group.age}`}
                className="group p-6 rounded-xl bg-dark-800/60 border border-dark-600 hover:border-green-500/30 transition-all text-center"
              >
                <group.icon className={`w-10 h-10 mx-auto mb-3 text-${group.color}-400`} />
                <div className="font-semibold text-white mb-1">{group.title}</div>
                <div className="text-sm text-gray-500">Ages {group.age}</div>
                <ArrowRight className="w-4 h-4 mx-auto mt-3 text-gray-600 group-hover:text-green-400 transition-colors" />
              </Link>
            ))}
          </div>
          
          {/* Voxel Game Credit */}
          <div className="text-center p-6 rounded-xl bg-dark-800/40 border border-dark-700">
            <p className="text-gray-500 text-sm">
              <span className="text-gray-400">Voxel Game Concept</span> by{" "}
              <span className="text-gray-300 font-medium">Magnus & Casey DiGennaro</span>
              {" "}- designed by a father-son team who believe learning should feel like play.
            </p>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* PROFESSIONAL TOOLS TEASER */}
      {/* ============================================ */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-green-900/10 via-dark-900 to-emerald-900/10">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 text-xs text-green-400 uppercase tracking-widest mb-4">
                <Settings className="w-3 h-3" />
                Professional Tools
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                <span className="text-white">Design Real Chips.</span><br/>
                <span className="gradient-text">Export to Manufacturing.</span>
              </h2>
              <p className="text-gray-400 mb-6 leading-relaxed">
                Our Progressive Iteration Engine takes you from use case to manufacturing-ready files.
                Verilog RTL, timing constraints, GDSII layouts—everything you need to send to a foundry.
              </p>
              
              <div className="space-y-3 mb-8">
                {[
                  "6-layer design process from concept to silicon",
                  "Model selection with licensing guidance",
                  "Power calculator and throughput estimator",
                  "Export to Cadence, Synopsys, and foundry partners"
                ].map((item) => (
                  <div key={item} className="flex items-center gap-3 text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                    <span className="text-sm">{item}</span>
                  </div>
                ))}
              </div>
              
              <Link
                href="/professional"
                className="inline-flex items-center gap-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-lg"
              >
                <Microchip className="w-5 h-5" />
                Open Professional Tools
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
            
            <div className="bg-dark-800/60 rounded-2xl border border-dark-600 p-6">
              {/* Mini Progressive Iteration Preview */}
              <div className="flex items-center gap-2 mb-4">
                <div className="w-6 h-6 rounded bg-amber-500/20 flex items-center justify-center text-amber-400 text-xs">0</div>
                <div className="flex-1 h-1 bg-dark-600 rounded" />
                <div className="w-6 h-6 rounded bg-purple-500/20 flex items-center justify-center text-purple-400 text-xs">1</div>
                <div className="flex-1 h-1 bg-dark-600 rounded" />
                <div className="w-6 h-6 rounded bg-green-500/20 flex items-center justify-center text-green-400 text-xs">2</div>
              </div>
              
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-dark-700/30">
                  <Lightbulb className="w-4 h-4 text-amber-400" />
                  <span className="text-gray-400">Use Case Definition</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-dark-700/30">
                  <Bot className="w-4 h-4 text-purple-400" />
                  <span className="text-gray-400">Model Selection</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                  <Lock className="w-4 h-4 text-green-400" />
                  <span className="text-green-400">Mask-Locked Architecture</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-dark-700/30">
                  <CircuitBoard className="w-4 h-4 text-blue-400" />
                  <span className="text-gray-400">System Integration</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-dark-700/30">
                  <CheckCircle className="w-4 h-4 text-pink-400" />
                  <span className="text-gray-400">Validation & Test</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-dark-700/30">
                  <Factory className="w-4 h-4 text-emerald-400" />
                  <span className="text-gray-400">Manufacturing Export</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* FOOTER CTA */}
      {/* ============================================ */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-transparent to-dark-800">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Ready to Design Your First Inference Chip?
          </h2>
          <p className="text-gray-400 mb-8">
            Our LUCI chips ship in 2026. By then, you could be ready to design your own.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/professional"
              className="inline-flex items-center gap-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-lg"
            >
              <Microchip className="w-5 h-5" />
              Start Designing
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/learning"
              className="inline-flex items-center gap-3 bg-dark-700 hover:bg-dark-600 text-white px-8 py-4 rounded-xl font-semibold transition-all border border-dark-500"
            >
              <BookOpen className="w-5 h-5" />
              Start Learning
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
