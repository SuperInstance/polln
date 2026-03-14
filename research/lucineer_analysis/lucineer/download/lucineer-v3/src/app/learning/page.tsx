"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  BookOpen, Gamepad2, Clock, GraduationCap, Briefcase,
  ChevronRight, ArrowRight, Play, Star, Lock, Unlock,
  Zap, Target, Award, TrendingUp, Users, Lightbulb,
  Puzzle, Sparkles, Layers, Box, Rocket, Cpu, Heart,
  Eye, Wand2, GitBranch, Flame, CircleDot, Timer,
  Trophy, Medal, Crown, Diamond
} from "lucide-react";

// ============================================
// RESEARCH-BACKED LEARNING PRINCIPLES
// Based on Csikszentmihalyi's Flow Theory,
// KiwiCo's hands-on model, and Minecraft's creative autonomy
// ============================================

const learningPrinciples = [
  {
    icon: Zap,
    title: "Flow State Learning",
    description: "Challenge matches skill level. Clear goals. Immediate feedback. Time flies when you're learning.",
    researcher: "Csikszentmihalyi",
    color: "text-amber-400",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
  },
  {
    icon: Layers,
    title: "Progressive Difficulty",
    description: "Start simple. Scaffold complexity. Each level builds on the last. No frustrating jumps.",
    researcher: "Vygotsky (ZPD)",
    color: "text-blue-400",
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
  },
  {
    icon: Box,
    title: "Hands-on Tangibility",
    description: "Abstract concepts become physical objects you can manipulate. Like KiwiCo crates for your mind.",
    researcher: "Montessori",
    color: "text-green-400",
    bg: "bg-green-500/10",
    border: "border-green-500/20",
  },
  {
    icon: Wand2,
    title: "Creative Autonomy",
    description: "Sandbox freedom within guided objectives. Build your own solutions. Like Minecraft for chip design.",
    researcher: "Minecraft Model",
    color: "text-purple-400",
    bg: "bg-purple-500/10",
    border: "border-purple-500/20",
  },
  {
    icon: Eye,
    title: "Visual Feedback",
    description: "Every action has visible consequences. Watch your chip come alive. See timing in real-time.",
    researcher: "Papert (Constructionism)",
    color: "text-cyan-400",
    bg: "bg-cyan-500/10",
    border: "border-cyan-500/20",
  },
  {
    icon: Target,
    title: "Meaningful Context",
    description: "Learning serves a purpose you care about. Build something real. Solve problems that matter.",
    researcher: "Project-Based Learning",
    color: "text-pink-400",
    bg: "bg-pink-500/10",
    border: "border-pink-500/20",
  },
];

// Age groups with detailed pathways
const ageGroups = [
  {
    id: "young",
    title: "Young Explorers",
    age: "4-10",
    icon: Gamepad2,
    color: "#3b82f6",
    gradient: "from-blue-500 to-cyan-500",
    tagline: "Play games that secretly teach",
    description: "Timing concepts through traffic lights, domino chains, and musical chairs. Kids don't realize they're learning—they're just having fun.",
    modules: [
      { 
        name: "Traffic Light Timing", 
        lessons: 8, 
        difficulty: "Easy", 
        icon: "🚦",
        description: "Control intersection lights. Learn sequencing and timing windows.",
        skills: ["Sequencing", "Timing Windows", "Cause & Effect"]
      },
      { 
        name: "Musical Chairs Fun", 
        lessons: 6, 
        difficulty: "Easy", 
        icon: "🎵",
        description: "Match beats and rhythms. Feel timing through music.",
        skills: ["Rhythm", "Pattern Recognition", "Memory"]
      },
      { 
        name: "Domino Chain Reactions", 
        lessons: 10, 
        difficulty: "Easy", 
        icon: "🎲",
        description: "Build cascading timing chains. Watch effects propagate.",
        skills: ["Cascading Logic", "Propagation Delay", "Planning"]
      },
      { 
        name: "Baking Timer Games", 
        lessons: 5, 
        difficulty: "Easy", 
        icon: "🍪",
        description: "Perfect timing in the kitchen. Real-world applications.",
        skills: ["Countdown", "Precision", "Patience"]
      },
    ],
    minecraftParallel: "Like Minecraft's Redstone, but designed for timing first. Kids who love building contraptions will feel right at home.",
    kiwiCoParallel: "Hands-on experiments you can touch and feel. Every lesson has a physical-world analogy.",
  },
  {
    id: "middle",
    title: "Curious Minds",
    age: "11-14",
    icon: Puzzle,
    color: "#8b5cf6",
    gradient: "from-purple-500 to-pink-500",
    tagline: "Understand how things actually work",
    description: "Animation timing, music beat programming, and traffic systems. Build small systems, break them, learn why they broke.",
    modules: [
      { 
        name: "Animation Frame Timing", 
        lessons: 12, 
        difficulty: "Medium", 
        icon: "🎬",
        description: "Create smooth animations by mastering frame timing.",
        skills: ["Frame Rates", "Interpolation", "Smooth Motion"]
      },
      { 
        name: "Beat Programming", 
        lessons: 8, 
        difficulty: "Medium", 
        icon: "🥁",
        description: "Program drum machines and sequencers. Feel the timing.",
        skills: ["Sequencers", "Clocks", "Synchronization"]
      },
      { 
        name: "Traffic Flow Systems", 
        lessons: 10, 
        difficulty: "Medium", 
        icon: "🚗",
        description: "Design traffic light systems. Optimize flow.",
        skills: ["State Machines", "Optimization", "Systems Thinking"]
      },
      { 
        name: "Sports Replay Analysis", 
        lessons: 6, 
        difficulty: "Medium", 
        icon: "⚽",
        description: "Analyze timing in sports. Frame-by-frame precision.",
        skills: ["Analysis", "Precision Timing", "Data Interpretation"]
      },
    ],
    minecraftParallel: "Like building complex Redstone computers, but with visual tools that show you what each component does.",
    kiwiCoParallel: "Tinker Crate level complexity. Projects that demonstrate real engineering principles.",
  },
  {
    id: "high",
    title: "Future Engineers",
    age: "15-18",
    icon: Lightbulb,
    color: "#f59e0b",
    gradient: "from-amber-500 to-orange-500",
    tagline: "Design real systems",
    description: "Digital logic timing, assembly line optimization, system design. Prepare for engineering careers or just understand the world better.",
    modules: [
      { 
        name: "Digital Logic Intro", 
        lessons: 15, 
        difficulty: "Advanced", 
        icon: "⚡",
        description: "How computers make decisions. Gates, flip-flops, timing.",
        skills: ["Logic Gates", "Flip-Flops", "Propagation"]
      },
      { 
        name: "Timing Analysis", 
        lessons: 12, 
        difficulty: "Advanced", 
        icon: "📊",
        description: "Analyze and optimize timing in digital systems.",
        skills: ["Setup/Hold Times", "Critical Paths", "Analysis"]
      },
      { 
        name: "System Design Basics", 
        lessons: 10, 
        difficulty: "Advanced", 
        icon: "🔧",
        description: "Design complete systems. Think like an architect.",
        skills: ["Architecture", "Tradeoffs", "Integration"]
      },
      { 
        name: "CPU State Machines", 
        lessons: 8, 
        difficulty: "Advanced", 
        icon: "💻",
        description: "How processors actually work. Step by step.",
        skills: ["State Machines", "Control Logic", "Execution"]
      },
    ],
    minecraftParallel: "Like designing a working computer in Minecraft, but with professional-grade tools and concepts.",
    kiwiCoParallel: "Eureka Crate complexity. Projects that could be prototypes for real products.",
  },
  {
    id: "pro",
    title: "Professionals",
    age: "18+",
    icon: Briefcase,
    color: "#22c55e",
    gradient: "from-green-500 to-emerald-500",
    tagline: "Build production systems",
    description: "FPGA timing closure, CDC analysis, pipeline optimization, real chip design. For engineers who need to ship products.",
    modules: [
      { 
        name: "FPGA Timing Closure", 
        lessons: 20, 
        difficulty: "Expert", 
        icon: "🔬",
        description: "Meet timing constraints. Debug violations. Ship silicon.",
        skills: ["Static Timing Analysis", "Constraints", "Optimization"]
      },
      { 
        name: "CDC Analysis", 
        lessons: 15, 
        difficulty: "Expert", 
        icon: "📈",
        description: "Cross clock domain design. Avoid metastability.",
        skills: ["Clock Domains", "Synchronizers", "Metastability"]
      },
      { 
        name: "Pipeline Optimization", 
        lessons: 12, 
        difficulty: "Expert", 
        icon: "⚙️",
        description: "Maximize throughput. Balance stages perfectly.",
        skills: ["Pipeline Design", "Throughput", "Latency Tradeoffs"]
      },
      { 
        name: "Real Chip Design", 
        lessons: 25, 
        difficulty: "Expert", 
        icon: "🧠",
        description: "Complete chip design flow. From concept to tapeout.",
        skills: ["Full Flow", "Verification", "Tapeout"]
      },
    ],
    minecraftParallel: "Professional tools with Minecraft-level accessibility. Power without the learning cliff.",
    kiwiCoParallel: "The tools are real. The concepts are production-ready. Build things that ship.",
  },
];

// Achievement levels for gamification
const achievementLevels = [
  { name: "Novice", icon: Star, description: "Just starting out", lessons: 0 },
  { name: "Apprentice", icon: Flame, description: "Building fundamentals", lessons: 10 },
  { name: "Journeyer", icon: Trophy, description: "Solid understanding", lessons: 30 },
  { name: "Expert", icon: Medal, description: "Deep knowledge", lessons: 60 },
  { name: "Master", icon: Crown, description: "Ready to teach", lessons: 100 },
  { name: "Lucineer", icon: Diamond, description: "Elite level", lessons: 150 },
];

// ============================================
// HOW LEARNING WORKS SECTION
// ============================================
function HowLearningWorks() {
  return (
    <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl border border-dark-600 p-6 md:p-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
          <BookOpen className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-2xl font-bold">How Our Learning Works</h2>
          <p className="text-sm text-gray-500">Research-backed principles, hacker/maker spirit</p>
        </div>
      </div>

      <p className="text-gray-300 mb-8 leading-relaxed">
        We didn't just build another tutorial site. We studied how people actually learn complex technical concepts.
        <span className="text-green-400"> Flow theory</span>, 
        <span className="text-blue-400"> progressive difficulty</span>, 
        <span className="text-purple-400"> hands-on tangibility</span> — 
        these aren't buzzwords. They're the foundation of everything we build.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {learningPrinciples.map((principle) => (
          <div 
            key={principle.title}
            className={`p-4 rounded-xl ${principle.bg} border ${principle.border} hover:scale-[1.02] transition-transform`}
          >
            <principle.icon className={`w-6 h-6 ${principle.color} mb-3`} />
            <h3 className="font-semibold text-white mb-2">{principle.title}</h3>
            <p className="text-sm text-gray-400 mb-2">{principle.description}</p>
            <span className="text-xs text-gray-500">Based on: {principle.researcher}</span>
          </div>
        ))}
      </div>

      <div className="mt-8 p-4 rounded-xl bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20">
        <div className="flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-purple-400 mt-0.5" />
          <div>
            <h4 className="font-semibold text-purple-300 mb-1">The Voxel Game Philosophy</h4>
            <p className="text-sm text-gray-400 leading-relaxed">
              Magnus (age 10) and Casey DiGennaro designed a gamified voxel-based "Incredible Machines" style game 
              over several weeks. It teaches timing through play. Kids don't sit through lectures — 
              they <span className="text-white">build things</span>, watch them work (or break), 
              and iterate. That's the model for all our learning experiences.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================
// PROGRESS PATHWAY VISUALIZATION
// ============================================
function ProgressPathway({ selectedAge }: { selectedAge: string }) {
  const activeGroup = ageGroups.find((g) => g.id === selectedAge) || ageGroups[0];
  const totalLessons = activeGroup.modules.reduce((acc, m) => acc + m.lessons, 0);
  
  return (
    <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl border border-dark-600 p-6">
      <div className="flex items-center gap-3 mb-6">
        <GitBranch className="w-5 h-5 text-green-400" />
        <h3 className="font-semibold">Your Progress Pathway</h3>
      </div>
      
      <div className="flex items-center gap-2 overflow-x-auto pb-4">
        {achievementLevels.map((level, index) => (
          <div key={level.name} className="flex items-center">
            <div className="flex flex-col items-center min-w-[80px]">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                index === 0 
                  ? 'bg-gradient-to-br from-amber-500 to-orange-500' 
                  : 'bg-dark-700 border border-dark-500'
              }`}>
                <level.icon className={`w-6 h-6 ${index === 0 ? 'text-white' : 'text-gray-500'}`} />
              </div>
              <span className={`text-xs mt-2 ${index === 0 ? 'text-amber-400 font-medium' : 'text-gray-500'}`}>
                {level.name}
              </span>
              <span className="text-xs text-gray-600">{level.lessons}+ lessons</span>
            </div>
            {index < achievementLevels.length - 1 && (
              <ArrowRight className="w-4 h-4 text-gray-600 mx-2" />
            )}
          </div>
        ))}
      </div>
      
      <div className="mt-4 p-3 rounded-lg bg-dark-700/50">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-400">Total lessons available</span>
          <span className="text-sm font-medium text-white">{totalLessons} lessons</span>
        </div>
        <div className="h-2 bg-dark-600 rounded-full overflow-hidden">
          <div 
            className={`h-full bg-gradient-to-r ${activeGroup.gradient} rounded-full`}
            style={{ width: '0%' }}
          />
        </div>
      </div>
    </div>
  );
}

// ============================================
// MAIN LEARNING PAGE
// ============================================
export default function LearningPage() {
  const searchParams = useSearchParams();
  const selectedAge = searchParams.get("age") || "young";

  const activeGroup = ageGroups.find((g) => g.id === selectedAge) || ageGroups[0];

  return (
    <div className="animated-bg min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold">Learning Center</h1>
              <p className="text-sm text-gray-500">Research-backed education for curious minds</p>
            </div>
          </div>

          <p className="text-xl text-gray-300 max-w-3xl">
            Master the timing concepts that power AI through interactive modules. 
            Same fundamentals, different depths for every age group. 
            <span className="text-green-400"> Play first, understand later.</span>
          </p>
        </div>

        {/* How Learning Works Section */}
        <div className="mb-12">
          <HowLearningWorks />
        </div>

        {/* Age Group Selector */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Users className="w-5 h-5 text-green-400" />
            Choose Your Pathway
          </h2>
          <div className="flex flex-wrap gap-3">
            {ageGroups.map((group) => (
              <Link
                key={group.id}
                href={`/learning?age=${group.id}`}
                className={`flex items-center gap-2 px-4 py-3 rounded-xl font-medium transition-all ${
                  selectedAge === group.id
                    ? `bg-gradient-to-r ${group.gradient} text-white`
                    : "bg-dark-700/50 text-gray-400 hover:text-white border border-dark-600"
                }`}
              >
                <group.icon className="w-5 h-5" />
                <div>
                  <div className="text-sm font-semibold">{group.title}</div>
                  <div className="text-xs opacity-75">Ages {group.age}</div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Active Group Content */}
        <div className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden mb-8">
          <div className={`p-6 bg-gradient-to-r ${activeGroup.gradient} bg-opacity-10`}>
            <div className="flex items-center gap-4 mb-4">
              <div
                className="w-16 h-16 rounded-2xl flex items-center justify-center"
                style={{ background: `linear-gradient(135deg, ${activeGroup.color}40 0%, ${activeGroup.color}20 100%)` }}
              >
                <activeGroup.icon className="w-8 h-8" style={{ color: activeGroup.color }} />
              </div>
              <div>
                <h2 className="text-2xl font-bold">{activeGroup.title}</h2>
                <p className="text-gray-400">
                  Ages {activeGroup.age} • {activeGroup.modules.reduce((acc, m) => acc + m.lessons, 0)} lessons
                </p>
              </div>
            </div>
            <p className="text-lg text-gray-300 mb-2">{activeGroup.tagline}</p>
            <p className="text-gray-400">{activeGroup.description}</p>
          </div>

          {/* Minecraft/KiwiCo Parallels */}
          <div className="p-6 border-b border-dark-600">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-purple-500/5 border border-purple-500/20">
                <div className="flex items-center gap-2 mb-2">
                  <Box className="w-4 h-4 text-purple-400" />
                  <span className="text-sm font-medium text-purple-400">Minecraft Parallel</span>
                </div>
                <p className="text-sm text-gray-400">{activeGroup.minecraftParallel}</p>
              </div>
              <div className="p-4 rounded-xl bg-green-500/5 border border-green-500/20">
                <div className="flex items-center gap-2 mb-2">
                  <Wand2 className="w-4 h-4 text-green-400" />
                  <span className="text-sm font-medium text-green-400">KiwiCo Parallel</span>
                </div>
                <p className="text-sm text-gray-400">{activeGroup.kiwiCoParallel}</p>
              </div>
            </div>
          </div>

          {/* Module Grid */}
          <div className="p-6">
            <h3 className="font-semibold mb-4 flex items-center gap-2">
              <Layers className="w-4 h-4 text-green-400" />
              Learning Modules
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {activeGroup.modules.map((module) => (
                <div
                  key={module.name}
                  className="p-5 rounded-xl bg-dark-700/30 border border-dark-600 hover:border-green-500/30 transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <span className="text-3xl">{module.icon}</span>
                      <div>
                        <h4 className="font-semibold group-hover:text-green-400 transition-colors">
                          {module.name}
                        </h4>
                        <p className="text-xs text-gray-500">{module.lessons} lessons</p>
                      </div>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      module.difficulty === "Easy" ? "bg-green-500/20 text-green-400" :
                      module.difficulty === "Medium" ? "bg-amber-500/20 text-amber-400" :
                      module.difficulty === "Advanced" ? "bg-orange-500/20 text-orange-400" :
                      "bg-red-500/20 text-red-400"
                    }`}>
                      {module.difficulty}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-400 mb-3">{module.description}</p>
                  
                  {/* Skills Tags */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {module.skills.map((skill) => (
                      <span 
                        key={skill}
                        className="text-xs px-2 py-1 rounded bg-dark-600/50 text-gray-400"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3 h-3 ${i < 3 ? "text-yellow-500 fill-yellow-500" : "text-gray-600"}`}
                        />
                      ))}
                    </div>
                    <button className="flex items-center gap-1 text-green-400 text-sm font-medium group-hover:gap-2 transition-all">
                      Start <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Progress Pathway */}
        <div className="mb-8">
          <ProgressPathway selectedAge={selectedAge} />
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-dark-800/60 rounded-xl p-4 border border-dark-600">
            <div className="flex items-center gap-3">
              <Target className="w-5 h-5 text-blue-400" />
              <div>
                <div className="text-2xl font-bold">100+</div>
                <div className="text-xs text-gray-500">Lessons</div>
              </div>
            </div>
          </div>
          <div className="bg-dark-800/60 rounded-xl p-4 border border-dark-600">
            <div className="flex items-center gap-3">
              <Award className="w-5 h-5 text-amber-400" />
              <div>
                <div className="text-2xl font-bold">4</div>
                <div className="text-xs text-gray-500">Age Pathways</div>
              </div>
            </div>
          </div>
          <div className="bg-dark-800/60 rounded-xl p-4 border border-dark-600">
            <div className="flex items-center gap-3">
              <TrendingUp className="w-5 h-5 text-green-400" />
              <div>
                <div className="text-2xl font-bold">6</div>
                <div className="text-xs text-gray-500">Achievement Levels</div>
              </div>
            </div>
          </div>
          <div className="bg-dark-800/60 rounded-xl p-4 border border-dark-600">
            <div className="flex items-center gap-3">
              <Rocket className="w-5 h-5 text-purple-400" />
              <div>
                <div className="text-2xl font-bold">$0</div>
                <div className="text-xs text-gray-500">Cost (Free)</div>
              </div>
            </div>
          </div>
        </div>

        {/* DiGennaro Credit Footer */}
        <div className="text-center pt-8 border-t border-dark-700">
          <div className="flex items-center justify-center gap-2 text-gray-500">
            <Cpu className="w-4 h-4 text-purple-400" />
            <span className="text-sm">
              Voxel Game Concept by{" "}
              <span className="text-gray-400 font-medium">Magnus & Casey DiGennaro</span>
            </span>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            Built with curiosity for learners everywhere
          </p>
        </div>
      </div>
    </div>
  );
}
