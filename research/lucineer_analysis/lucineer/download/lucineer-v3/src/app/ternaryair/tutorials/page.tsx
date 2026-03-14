"use client";

import Link from "next/link";
import { useState } from "react";
import Image from "next/image";
import {
  Cpu, Layers, Box, Zap, ArrowRight, Play, ChevronRight,
  Lightbulb, Target, Clock, Binary, CircuitBoard, Gauge,
  GraduationCap, Wrench, Rocket, BookOpen, Video, Image as ImageIcon,
  Code, Download, ExternalLink, Check, Lock, Unlock
} from "lucide-react";

// Visual tutorial modules - teaching without words
const visualModules = [
  {
    id: "abstraction-layers",
    title: "From Idea to Silicon",
    subtitle: "Visual journey through design abstraction",
    visual: "/assets/chip-education/progressive-abstraction.png",
    duration: "5 min visual",
    concepts: 6,
    difficulty: "Beginner",
    description: "Watch how an idea transforms through layers of abstraction into physical silicon.",
    outcomes: ["Understand design flow", "Visualize abstraction", "See the complete path"],
  },
  {
    id: "chip-layers",
    title: "Inside a Chip",
    subtitle: "Cross-section exploration",
    visual: "/assets/chip-education/chip-layers.png",
    duration: "4 min visual",
    concepts: 5,
    difficulty: "Beginner",
    description: "Explore the microscopic layers that make up modern silicon chips.",
    outcomes: ["See metal interconnects", "Understand layering", "Grasp scale"],
  },
  {
    id: "state-machines",
    title: "Timing & States",
    subtitle: "Watch logic flow",
    visual: "/assets/chip-education/state-machine.png",
    duration: "6 min interactive",
    concepts: 8,
    difficulty: "Intermediate",
    description: "Interactive visualization of how chips move through states over time.",
    outcomes: ["Understand state machines", "See timing concepts", "Connect to code"],
  },
  {
    id: "ternary-computing",
    title: "Ternary Logic",
    subtitle: "Beyond binary thinking",
    visual: "/assets/chip-education/ternary-computing.png",
    duration: "8 min interactive",
    concepts: 10,
    difficulty: "Advanced",
    description: "Explore three-valued logic: -1, 0, +1. The foundation of efficient AI inference.",
    outcomes: ["Grasp ternary concepts", "See efficiency gains", "Connect to TernaryAir"],
  },
];

// Hands-on tutorials
const handsOnTutorials = [
  {
    id: "pcie-design",
    title: "PCIe AI Accelerator Card",
    icon: CircuitBoard,
    difficulty: "Intermediate",
    time: "2 hours",
    description: "Design a desktop AI accelerator card from concept to manufacturing-ready specs.",
    steps: ["Form factor selection", "Power budgeting", "Thermal simulation", "Interface design"],
    image: "/assets/chip-education/pcie-form-factor.png",
  },
  {
    id: "edge-device",
    title: "Edge AI Device Design",
    icon: Zap,
    difficulty: "Intermediate",
    time: "3 hours",
    description: "Create a complete edge device with AI inference capabilities.",
    steps: ["Use case definition", "Component selection", "Power optimization", "Packaging"],
    image: "/assets/chip-education/edge-deployments.png",
  },
  {
    id: "custom-asic",
    title: "Custom ASIC Flow",
    icon: Cpu,
    difficulty: "Advanced",
    time: "4 hours",
    description: "Full custom chip design flow from RTL to GDSII.",
    steps: ["Architecture", "RTL design", "Synthesis", "Place & route", "Verification"],
    image: "/assets/chip-education/voxel-to-chip.png",
  },
];

// Learning paths
const learningPaths = [
  {
    id: "hobbyist",
    title: "Hobbyist Path",
    description: "Start from zero, build your first AI device",
    duration: "10-15 hours",
    modules: 8,
    icon: Lightbulb,
    color: "#3b82f6",
    outcomes: ["Understand chip basics", "Design simple systems", "Prepare for manufacturing"],
  },
  {
    id: "engineer",
    title: "Engineer Path",
    description: "Deep dive into professional chip design",
    duration: "40-60 hours",
    modules: 20,
    icon: Wrench,
    color: "#8b5cf6",
    outcomes: ["Master design flow", "Use EDA tools", "Create production-ready designs"],
  },
  {
    id: "innovator",
    title: "Innovator Path",
    description: "Create novel AI chip architectures",
    duration: "100+ hours",
    modules: 35,
    icon: Rocket,
    color: "#22c55e",
    outcomes: ["Design custom architectures", "Optimize for specific use cases", "Prepare for tapeout"],
  },
];

export default function TutorialsPage() {
  const [activePath, setActivePath] = useState("hobbyist");
  const [completedModules, setCompletedModules] = useState<string[]>([]);

  const markComplete = (moduleId: string) => {
    if (!completedModules.includes(moduleId)) {
      setCompletedModules([...completedModules, moduleId]);
    }
  };

  return (
    <div className="animated-bg min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold">
                <span className="gradient-text">Chip Design Academy</span>
              </h1>
              <p className="text-sm text-gray-500">Visual learning • Hands-on projects • Real manufacturing</p>
            </div>
          </div>

          <p className="text-xl text-gray-300 max-w-3xl">
            Learn chip design through interactive visualizations and hands-on projects. 
            Start as a hobbyist, graduate with the skills to design real silicon.
          </p>
        </div>

        {/* Learning Paths */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Target className="w-6 h-6 text-green-400" />
            Choose Your Path
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {learningPaths.map((path) => (
              <button
                key={path.id}
                onClick={() => setActivePath(path.id)}
                className={`text-left p-6 rounded-2xl border transition-all ${
                  activePath === path.id
                    ? "bg-gradient-to-br from-green-900/30 to-dark-800 border-green-500/50 shadow-lg shadow-green-500/10"
                    : "bg-dark-800/60 border-dark-600 hover:border-dark-500"
                }`}
              >
                <div className="flex items-center gap-4 mb-4">
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center"
                    style={{ background: `${path.color}30` }}
                  >
                    <path.icon className="w-6 h-6" style={{ color: path.color }} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{path.title}</h3>
                    <p className="text-sm text-gray-500">{path.duration}</p>
                  </div>
                </div>
                <p className="text-gray-400 text-sm mb-4">{path.description}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>{path.modules} modules</span>
                  <span>•</span>
                  <span>{path.outcomes.length} key outcomes</span>
                </div>
                <div className="mt-4 space-y-1">
                  {path.outcomes.map((outcome) => (
                    <div key={outcome} className="flex items-center gap-2 text-xs text-gray-400">
                      <Check className="w-3 h-3 text-green-400" />
                      {outcome}
                    </div>
                  ))}
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* Visual Learning Modules */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <ImageIcon className="w-6 h-6 text-blue-400" />
            Visual Learning Modules
          </h2>
          <p className="text-gray-400 mb-6">
            Learn through pictures and interaction. Minimal reading, maximum understanding.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {visualModules.map((module) => (
              <div
                key={module.id}
                className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden group hover:border-green-500/30 transition-all"
              >
                {/* Visual Preview */}
                <div className="relative h-48 bg-dark-700 overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-purple-500/10" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-32 h-32 rounded-2xl bg-gradient-to-br from-green-500/20 to-purple-500/20 flex items-center justify-center">
                      <Box className="w-12 h-12 text-green-400" />
                    </div>
                  </div>
                  <div className="absolute bottom-2 right-2 flex items-center gap-2">
                    <span className="px-2 py-1 rounded-full bg-dark-800/80 text-xs text-gray-400">
                      {module.duration}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      module.difficulty === "Beginner" ? "bg-green-500/20 text-green-400" :
                      module.difficulty === "Intermediate" ? "bg-amber-500/20 text-amber-400" :
                      "bg-red-500/20 text-red-400"
                    }`}>
                      {module.difficulty}
                    </span>
                  </div>
                  {completedModules.includes(module.id) && (
                    <div className="absolute top-2 right-2 w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
                      <Check className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="p-5">
                  <h3 className="font-semibold text-lg mb-1">{module.title}</h3>
                  <p className="text-sm text-gray-500 mb-3">{module.subtitle}</p>
                  <p className="text-sm text-gray-400 mb-4">{module.description}</p>

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">{module.concepts} core concepts</span>
                    <Link
                      href={`/ternaryair/tutorials/${module.id}`}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm transition-colors"
                    >
                      <Play className="w-4 h-4" />
                      Start
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Hands-on Tutorials */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Wrench className="w-6 h-6 text-purple-400" />
            Hands-on Projects
          </h2>
          <p className="text-gray-400 mb-6">
            Real projects that teach you to design manufacturable hardware.
          </p>

          <div className="space-y-4">
            {handsOnTutorials.map((tutorial, index) => (
              <div
                key={tutorial.id}
                className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden hover:border-green-500/30 transition-all"
              >
                <div className="flex flex-col md:flex-row">
                  {/* Preview */}
                  <div className="w-full md:w-64 h-40 md:h-auto bg-dark-700 relative">
                    <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-blue-500/10" />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <tutorial.icon className="w-12 h-12 text-purple-400" />
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-semibold text-lg">{tutorial.title}</h3>
                        <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                          <span className={`px-2 py-0.5 rounded-full ${
                            tutorial.difficulty === "Beginner" ? "bg-green-500/20 text-green-400" :
                            tutorial.difficulty === "Intermediate" ? "bg-amber-500/20 text-amber-400" :
                            "bg-red-500/20 text-red-400"
                          }`}>
                            {tutorial.difficulty}
                          </span>
                          <span>{tutorial.time}</span>
                        </div>
                      </div>
                      <span className="text-2xl font-bold text-dark-600">{String(index + 1).padStart(2, '0')}</span>
                    </div>

                    <p className="text-sm text-gray-400 mb-4">{tutorial.description}</p>

                    <div className="flex flex-wrap gap-2 mb-4">
                      {tutorial.steps.map((step) => (
                        <span
                          key={step}
                          className="px-3 py-1 rounded-full bg-dark-700/50 text-xs text-gray-400 border border-dark-600"
                        >
                          {step}
                        </span>
                      ))}
                    </div>

                    <Link
                      href={`/ternaryair/tutorials/${tutorial.id}`}
                      className="flex items-center gap-2 text-green-400 hover:text-green-300 text-sm font-medium"
                    >
                      Start Project <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Manufacturing Pathway */}
        <section className="mb-16">
          <div className="bg-gradient-to-r from-green-900/30 via-dark-800 to-emerald-900/30 rounded-2xl p-8 border border-green-500/20">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center">
                <Rocket className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Ready for Manufacturing?</h2>
                <p className="text-gray-400">Take your design from simulation to silicon</p>
              </div>
            </div>

            <p className="text-gray-300 mb-6 max-w-2xl">
              Complete the tutorials and hands-on projects, then submit your design for manufacturing review. 
              We connect hobbyists with MPW (Multi-Project Wafer) services and small-batch production.
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-dark-800/50 rounded-xl p-4 border border-dark-600">
                <div className="text-2xl font-bold text-green-400 mb-1">TinyTapeout</div>
                <p className="text-sm text-gray-400">$100-500 for prototype</p>
              </div>
              <div className="bg-dark-800/50 rounded-xl p-4 border border-dark-600">
                <div className="text-2xl font-bold text-blue-400 mb-1">MPW Shuttle</div>
                <p className="text-sm text-gray-400">$5K-50K for small batch</p>
              </div>
              <div className="bg-dark-800/50 rounded-xl p-4 border border-dark-600">
                <div className="text-2xl font-bold text-purple-400 mb-1">Full Tapeout</div>
                <p className="text-sm text-gray-400">$100K+ for production</p>
              </div>
            </div>

            <Link
              href="/ternaryair/manufacturing"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-green-600 hover:bg-green-500 text-white font-medium transition-colors"
            >
              Explore Manufacturing Options <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </section>

        {/* Progress Tracker */}
        <section className="bg-dark-800/60 rounded-2xl p-6 border border-dark-600">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <Gauge className="w-5 h-5 text-green-400" />
            Your Progress
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-dark-700/50 rounded-xl p-4">
              <div className="text-3xl font-bold text-green-400">{completedModules.length}</div>
              <div className="text-sm text-gray-500">Modules Completed</div>
            </div>
            <div className="bg-dark-700/50 rounded-xl p-4">
              <div className="text-3xl font-bold text-blue-400">0</div>
              <div className="text-sm text-gray-500">Projects Started</div>
            </div>
            <div className="bg-dark-700/50 rounded-xl p-4">
              <div className="text-3xl font-bold text-purple-400">0h</div>
              <div className="text-sm text-gray-500">Learning Time</div>
            </div>
            <div className="bg-dark-700/50 rounded-xl p-4">
              <div className="text-3xl font-bold text-amber-400">0</div>
              <div className="text-sm text-gray-500">Designs Created</div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
