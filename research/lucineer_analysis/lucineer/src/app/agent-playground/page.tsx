"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Head from "next/head";
import Link from "next/link";
import AgentObserver from "@/components/agent/AgentObserver";
import {
  Bot,
  Factory,
  DollarSign,
  Code2,
  Box,
  Sparkles,
  Gamepad2,
  Brain,
  Target,
  Zap,
  Lightbulb,
  ArrowRight,
  Play,
  Eye,
  MessageSquare,
  Settings,
  Users,
  GraduationCap,
  Briefcase,
} from "lucide-react";

// Domain configurations
const domains = [
  {
    id: "manufacturing",
    name: "Manufacturing Agent",
    icon: Factory,
    color: "from-emerald-500 to-green-600",
    description: "Watch an agent optimize chip manufacturing yield",
    goals: [
      "Maximize yield at 28nm process node",
      "Reduce defect density below 0.3",
      "Optimize wafer utilization",
      "Minimize cycle time",
    ],
    ageRange: "Ages 10+",
    skillLevel: "Beginner",
  },
  {
    id: "economics",
    name: "Economics Agent",
    icon: DollarSign,
    color: "from-purple-500 to-indigo-600",
    description: "Agent analyzes market dynamics and pricing strategies",
    goals: [
      "Maximize profit margin",
      "Find optimal price point",
      "Analyze competitive threats",
      "Optimize supply chain costs",
    ],
    ageRange: "Ages 12+",
    skillLevel: "Intermediate",
  },
  {
    id: "rtl",
    name: "RTL Design Agent",
    icon: Code2,
    color: "from-blue-500 to-cyan-600",
    description: "Agent works through RTL to GDSII design flow",
    goals: [
      "Meet timing constraints",
      "Minimize chip area",
      "Reduce power consumption",
      "Fix design rule violations",
    ],
    ageRange: "Ages 14+",
    skillLevel: "Advanced",
  },
  {
    id: "math",
    name: "Math Explorer Agent",
    icon: Box,
    color: "from-amber-500 to-orange-600",
    description: "Agent explores mathematical concepts visually",
    goals: [
      "Understand gradient descent",
      "Explore attention mechanisms",
      "Master tensor operations",
      "Visualize optimization landscapes",
    ],
    ageRange: "Ages 8+",
    skillLevel: "All Levels",
  },
  {
    id: "mist",
    name: "MIST Game Agent",
    icon: Gamepad2,
    color: "from-pink-500 to-rose-600",
    description: "Watch an agent play the MIST sheepdog game",
    goals: [
      "Complete apprentice training",
      "Master the four seasons",
      "Learn progressive revelation",
      "Become a pack leader",
    ],
    ageRange: "Ages 5+",
    skillLevel: "Beginner",
  },
];

// Abstraction Levels
const abstractionLevels = [
  {
    level: 1,
    name: "Observer",
    description: "Just watch the agent work",
    icon: Eye,
  },
  {
    level: 2,
    name: "Director",
    description: "Give the agent directions",
    icon: Target,
  },
  {
    level: 3,
    name: "Manager",
    description: "Set goals and evaluate outcomes",
    icon: Users,
  },
  {
    level: 4,
    name: "Architect",
    description: "Design multi-agent workflows",
    icon: Settings,
  },
];

// Learning Insights Panel
function LearningInsights() {
  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Lightbulb className="w-5 h-5 text-amber-400" />
        Why Watch Agents?
      </h3>
      
      <div className="space-y-4">
        <div className="p-4 bg-amber-500/10 rounded-xl border border-amber-500/20">
          <h4 className="font-medium text-amber-400 mb-2">Abstraction Training</h4>
          <p className="text-sm text-muted-foreground">
            When you direct an agent, you must first NAME what you're doing, then BREAK IT DOWN into steps.
            This externalizes your thinking and trains meta-cognitive skills.
          </p>
        </div>

        <div className="p-4 bg-indigo-500/10 rounded-xl border border-indigo-500/20">
          <h4 className="font-medium text-indigo-400 mb-2">Level-Up Your Thinking</h4>
          <p className="text-sm text-muted-foreground">
            Start as an Observer (just watch). Progress to Director (give directions), Manager (set goals),
            and Architect (design workflows). Each level trains higher-order thinking.
          </p>
        </div>

        <div className="p-4 bg-green-500/10 rounded-xl border border-green-500/20">
          <h4 className="font-medium text-green-400 mb-2">For All Ages</h4>
          <p className="text-sm text-muted-foreground">
            A 5-year-old watches MIST agent learn. A 15-year-old directs RTL optimization.
            A professional architect multi-agent workflows. Same platform, different depths.
          </p>
        </div>
      </div>
    </div>
  );
}

// Domain Card
function DomainCard({ domain, onSelect, isActive }: { 
  domain: typeof domains[0]; 
  onSelect: () => void;
  isActive: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      onClick={onSelect}
      className={`cursor-pointer group transition-all duration-300 ${
        isActive ? 'scale-105' : 'hover:scale-102'
      }`}
    >
      <div className={`bg-card rounded-2xl border-2 overflow-hidden transition-colors ${
        isActive ? 'border-indigo-500 shadow-lg shadow-indigo-500/20' : 'border-border hover:border-indigo-500/30'
      }`}>
        <div className={`h-2 bg-gradient-to-r ${domain.color}`} />
        <div className="p-5">
          <div className="flex items-center gap-3 mb-3">
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${domain.color} flex items-center justify-center`}>
              <domain.icon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold">{domain.name}</h3>
              <div className="flex gap-2 text-xs text-muted-foreground">
                <span>{domain.ageRange}</span>
                <span>•</span>
                <span>{domain.skillLevel}</span>
              </div>
            </div>
          </div>
          
          <p className="text-sm text-muted-foreground mb-3">{domain.description}</p>
          
          <div className="flex items-center justify-between">
            <div className="text-xs text-indigo-400">
              {domain.goals.length} goals available
            </div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground group-hover:text-indigo-400 transition-colors">
              <Play className="w-3 h-3" />
              Watch
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Abstraction Level Selector
function AbstractionLevelSelector({ level, onChange }: { level: number; onChange: (l: number) => void }) {
  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Brain className="w-5 h-5 text-purple-400" />
        Your Abstraction Level
      </h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {abstractionLevels.map((al) => (
          <button
            key={al.level}
            onClick={() => onChange(al.level)}
            className={`p-4 rounded-xl border-2 transition-all text-center ${
              level === al.level 
                ? 'border-indigo-500 bg-indigo-500/10' 
                : 'border-border hover:border-indigo-500/30'
            }`}
          >
            <al.icon className={`w-6 h-6 mx-auto mb-2 ${level === al.level ? 'text-indigo-400' : 'text-muted-foreground'}`} />
            <div className="font-medium text-sm">{al.name}</div>
            <div className="text-xs text-muted-foreground mt-1">Level {al.level}</div>
          </button>
        ))}
      </div>
      
      <p className="mt-4 text-sm text-muted-foreground text-center">
        {abstractionLevels[level - 1].description}
      </p>
    </div>
  );
}

export default function AgentPlaygroundPage() {
  const [activeDomain, setActiveDomain] = useState<string | null>(null);
  const [abstractionLevel, setAbstractionLevel] = useState(2);

  const currentDomain = domains.find(d => d.id === activeDomain);

  return (
    <>
      <Head>
        <title>Agent Playground | Lucineer - Watch & Direct AI Agents</title>
        <meta name="description" content="Watch AI agents play games, optimize designs, and explore concepts. Train your abstraction skills by directing agents through complex tasks." />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-background via-background to-indigo-500/5 pt-20">
        <section className="py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            {/* Hero */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-12"
            >
              <div className="inline-flex items-center gap-2 bg-indigo-500/10 border border-indigo-500/30 rounded-full px-4 py-2 mb-6">
                <Bot className="w-4 h-4 text-indigo-400" />
                <span className="text-indigo-400 text-sm font-medium">Agent Observation Deck</span>
              </div>

              <h1 className="text-4xl sm:text-5xl font-bold mb-4">
                <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Agent Playground
                </span>
              </h1>

              <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
                Watch agents play, optimize, and explore. Give them directions.
                Train your brain to think at higher levels of abstraction.
              </p>

              {/* Audience Tags */}
              <div className="flex flex-wrap justify-center gap-3">
                <span className="inline-flex items-center gap-2 px-4 py-2 bg-pink-500/10 rounded-full text-sm">
                  <Sparkles className="w-4 h-4 text-pink-400" />
                  <span className="text-pink-400">Kids 5-10</span>
                </span>
                <span className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 rounded-full text-sm">
                  <GraduationCap className="w-4 h-4 text-blue-400" />
                  <span className="text-blue-400">Students 11-17</span>
                </span>
                <span className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/10 rounded-full text-sm">
                  <Briefcase className="w-4 h-4 text-purple-400" />
                  <span className="text-purple-400">Professionals</span>
                </span>
              </div>
            </motion.div>

            {/* Abstraction Level Selector */}
            <div className="mb-8">
              <AbstractionLevelSelector 
                level={abstractionLevel} 
                onChange={setAbstractionLevel} 
              />
            </div>

            {/* Domain Selection */}
            <div className="mb-8">
              <h2 className="text-2xl font-bold mb-6 text-center">Choose an Agent Domain</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {domains.map((domain) => (
                  <DomainCard
                    key={domain.id}
                    domain={domain}
                    isActive={activeDomain === domain.id}
                    onSelect={() => setActiveDomain(domain.id)}
                  />
                ))}
              </div>
            </div>

            {/* Agent Observer */}
            {currentDomain && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-8"
              >
                <AgentObserver
                  domain={currentDomain.id as "manufacturing" | "economics" | "rtl" | "math"}
                  customGoals={currentDomain.goals}
                />
              </motion.div>
            )}

            {/* Learning Insights */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <LearningInsights />

              {/* Quick Stats */}
              <div className="bg-card rounded-2xl border border-border p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-cyan-400" />
                  How This Trains Your Brain
                </h3>

                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                      <span className="text-cyan-400 font-bold">1</span>
                    </div>
                    <div>
                      <h4 className="font-medium">Name It</h4>
                      <p className="text-sm text-muted-foreground">
                        To direct an agent, you must name what you want. This forces explicit knowledge.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                      <span className="text-purple-400 font-bold">2</span>
                    </div>
                    <div>
                      <h4 className="font-medium">Break It Down</h4>
                      <p className="text-sm text-muted-foreground">
                        Complex goals become sequences. You see the structure of problems.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0">
                      <span className="text-green-400 font-bold">3</span>
                    </div>
                    <div>
                      <h4 className="font-medium">Evaluate</h4>
                      <p className="text-sm text-muted-foreground">
                        Watch the agent's results. Reflect on your directions. Improve meta-cognition.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                      <span className="text-amber-400 font-bold">4</span>
                    </div>
                    <div>
                      <h4 className="font-medium">Level Up</h4>
                      <p className="text-sm text-muted-foreground">
                        Move from Observer → Director → Manager → Architect. Each level is harder thinking.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <div className="flex flex-wrap gap-4 justify-center">
              <Link
                href="/mist"
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-pink-500 to-rose-500 text-white font-medium"
              >
                <Gamepad2 className="w-5 h-5" />
                Play MIST Game
              </Link>
              <Link
                href="/math-universe"
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-card border border-border hover:border-indigo-500/50 transition-colors"
              >
                <Box className="w-5 h-5 text-amber-400" />
                Math Universe
              </Link>
              <Link
                href="/manufacturing"
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-card border border-border hover:border-emerald-500/50 transition-colors"
              >
                <Factory className="w-5 h-5 text-emerald-400" />
                Manufacturing
              </Link>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
