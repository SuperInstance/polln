"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  BookOpen,
  Clock,
  Puzzle,
  CircuitBoard,
  Network,
  ArrowRight,
  Play,
  CheckCircle,
  Sparkles,
  GraduationCap,
  Briefcase,
  Timer,
  Layers,
  Zap,
  Lightbulb,
  Target,
} from "lucide-react";

const ageGroups = [
  { id: "young", label: "Young Learners", icon: Sparkles, color: "text-green-400", age: "Ages 5-10" },
  { id: "middle", label: "Middle School", icon: GraduationCap, color: "text-blue-400", age: "Ages 11-14" },
  { id: "high", label: "High School", icon: BookOpen, color: "text-amber-400", age: "Ages 15-18" },
  { id: "professional", label: "Professional", icon: Briefcase, color: "text-purple-400", age: "18+" },
];

const learningModules = {
  timing: [
    {
      id: "timing-basics",
      title: "Timing Basics",
      description: "Learn how clocks and timing signals work in digital systems",
      duration: "15 min",
      lessons: 5,
      difficulty: "Beginner",
      icon: Timer,
      topics: ["What is a Clock?", "Frequency & Period", "Timing Diagrams", "Rising & Falling Edges"],
    },
    {
      id: "clock-domains",
      title: "Clock Domains",
      description: "Understanding how different clock speeds interact",
      duration: "20 min",
      lessons: 6,
      difficulty: "Intermediate",
      icon: Layers,
      topics: ["Single Clock Domain", "Multiple Clocks", "CDC Basics", "Metastability"],
    },
    {
      id: "setup-hold",
      title: "Setup & Hold Times",
      description: "Critical timing constraints for reliable circuits",
      duration: "25 min",
      lessons: 7,
      difficulty: "Intermediate",
      icon: Target,
      topics: ["Setup Time", "Hold Time", "Timing Violations", "Slack Analysis"],
    },
  ],
  sequencing: [
    {
      id: "cause-effect",
      title: "Cause & Effect",
      description: "Understanding sequencing through visual examples",
      duration: "10 min",
      lessons: 4,
      difficulty: "Beginner",
      icon: Lightbulb,
      topics: ["Sequential Logic", "State Machines", "Order Matters", "Dependencies"],
    },
    {
      id: "pipelines",
      title: "Pipeline Concepts",
      description: "How computers process instructions step by step",
      duration: "20 min",
      lessons: 5,
      difficulty: "Intermediate",
      icon: Zap,
      topics: ["Pipeline Stages", "Throughput", "Latency", "Hazards"],
    },
    {
      id: "synchronization",
      title: "Synchronization",
      description: "Coordinating multiple signals and processes",
      duration: "30 min",
      lessons: 8,
      difficulty: "Advanced",
      icon: Network,
      topics: ["Synchronizers", "Handshaking", "FIFOs", "Clock Crossing"],
    },
  ],
  applications: [
    {
      id: "traffic-lights",
      title: "Traffic Light Controllers",
      description: "Real-world timing in action",
      duration: "15 min",
      lessons: 5,
      difficulty: "Beginner",
      icon: CircuitBoard,
      topics: ["State Machines", "Timing Circuits", "Sensor Inputs", "Safety Logic"],
    },
    {
      id: "cpu-timing",
      title: "CPU Timing",
      description: "How processors execute billions of operations per second",
      duration: "25 min",
      lessons: 6,
      difficulty: "Intermediate",
      icon: CircuitBoard,
      topics: ["Clock Cycles", "Instruction Timing", "Branch Prediction", "Cache Timing"],
    },
    {
      id: "memory-timing",
      title: "Memory Timing",
      description: "Understanding RAM and memory access patterns",
      duration: "20 min",
      lessons: 5,
      difficulty: "Intermediate",
      icon: Puzzle,
      topics: ["Access Times", "CAS Latency", "Refresh Cycles", "Bandwidth"],
    },
  ],
};

export default function LearningPage() {
  const [selectedAge, setSelectedAge] = useState<string | null>(null);

  return (
    <div className="animated-gradient-bg min-h-screen">
      {/* Hero Section */}
      <section className="hero-gradient pt-20 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2 mb-6">
              <BookOpen className="w-4 h-4 text-primary" />
              <span className="text-primary text-sm font-medium">Interactive Learning Hub</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="gradient-text">Master Timing</span>
              <br />
              <span className="text-foreground">& Sequencing Concepts</span>
            </h1>

            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Interactive lessons that make complex digital timing concepts easy to understand
              through visualizations and hands-on experiments.
            </p>
          </motion.div>

          {/* Age Group Selector */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="flex flex-wrap justify-center gap-3 mb-12"
          >
            {ageGroups.map((group) => (
              <button
                key={group.id}
                onClick={() => setSelectedAge(selectedAge === group.id ? null : group.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl border transition-all duration-200 ${
                  selectedAge === group.id
                    ? `${group.color} bg-current/10 border-current`
                    : "border-border text-muted-foreground hover:border-foreground/30"
                }`}
              >
                <group.icon className="w-4 h-4" />
                <span className="font-medium">{group.label}</span>
                <span className="text-xs opacity-70">({group.age})</span>
              </button>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Learning Paths */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Timing Fundamentals */}
          <div id="timing-basics" className="mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="flex items-center gap-3 mb-8"
            >
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                <Clock className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Timing Fundamentals</h2>
                <p className="text-muted-foreground">Master the basics of digital timing</p>
              </div>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {learningModules.timing.map((module, index) => (
                <motion.div
                  key={module.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="group bg-card rounded-2xl border border-border p-6 card-hover"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                      <module.icon className="w-6 h-6 text-primary" />
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      module.difficulty === "Beginner" ? "bg-green-400/10 text-green-400" :
                      module.difficulty === "Intermediate" ? "bg-amber-400/10 text-amber-400" :
                      "bg-purple-400/10 text-purple-400"
                    }`}>
                      {module.difficulty}
                    </span>
                  </div>

                  <h3 className="text-lg font-semibold mb-2">{module.title}</h3>
                  <p className="text-muted-foreground text-sm mb-4">{module.description}</p>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
                    <span>{module.duration}</span>
                    <span>•</span>
                    <span>{module.lessons} lessons</span>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {module.topics.slice(0, 3).map((topic) => (
                      <span key={topic} className="text-xs px-2 py-1 rounded-md bg-muted">
                        {topic}
                      </span>
                    ))}
                    {module.topics.length > 3 && (
                      <span className="text-xs px-2 py-1 rounded-md bg-muted text-muted-foreground">
                        +{module.topics.length - 3} more
                      </span>
                    )}
                  </div>

                  <Link
                    href={`/timing-playground#${module.id}`}
                    className="flex items-center gap-2 text-primary font-medium text-sm group-hover:gap-3 transition-all"
                  >
                    Start Learning <ArrowRight className="w-4 h-4" />
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Sequencing Logic */}
          <div id="sequencing" className="mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="flex items-center gap-3 mb-8"
            >
              <div className="w-12 h-12 rounded-xl bg-blue-400/10 flex items-center justify-center">
                <Puzzle className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Sequencing Logic</h2>
                <p className="text-muted-foreground">Understand cause and effect in digital circuits</p>
              </div>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {learningModules.sequencing.map((module, index) => (
                <motion.div
                  key={module.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="group bg-card rounded-2xl border border-border p-6 card-hover"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-blue-400/10 flex items-center justify-center">
                      <module.icon className="w-6 h-6 text-blue-400" />
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      module.difficulty === "Beginner" ? "bg-green-400/10 text-green-400" :
                      module.difficulty === "Intermediate" ? "bg-amber-400/10 text-amber-400" :
                      "bg-purple-400/10 text-purple-400"
                    }`}>
                      {module.difficulty}
                    </span>
                  </div>

                  <h3 className="text-lg font-semibold mb-2">{module.title}</h3>
                  <p className="text-muted-foreground text-sm mb-4">{module.description}</p>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
                    <span>{module.duration}</span>
                    <span>•</span>
                    <span>{module.lessons} lessons</span>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {module.topics.slice(0, 3).map((topic) => (
                      <span key={topic} className="text-xs px-2 py-1 rounded-md bg-muted">
                        {topic}
                      </span>
                    ))}
                    {module.topics.length > 3 && (
                      <span className="text-xs px-2 py-1 rounded-md bg-muted text-muted-foreground">
                        +{module.topics.length - 3} more
                      </span>
                    )}
                  </div>

                  <Link
                    href={`/timing-playground#${module.id}`}
                    className="flex items-center gap-2 text-blue-400 font-medium text-sm group-hover:gap-3 transition-all"
                  >
                    Start Learning <ArrowRight className="w-4 h-4" />
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Real-World Applications */}
          <div id="examples" className="mb-16">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="flex items-center gap-3 mb-8"
            >
              <div className="w-12 h-12 rounded-xl bg-amber-400/10 flex items-center justify-center">
                <Network className="w-6 h-6 text-amber-400" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Real-World Applications</h2>
                <p className="text-muted-foreground">See timing concepts in action</p>
              </div>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {learningModules.applications.map((module, index) => (
                <motion.div
                  key={module.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1 }}
                  className="group bg-card rounded-2xl border border-border p-6 card-hover"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-amber-400/10 flex items-center justify-center">
                      <module.icon className="w-6 h-6 text-amber-400" />
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      module.difficulty === "Beginner" ? "bg-green-400/10 text-green-400" :
                      module.difficulty === "Intermediate" ? "bg-amber-400/10 text-amber-400" :
                      "bg-purple-400/10 text-purple-400"
                    }`}>
                      {module.difficulty}
                    </span>
                  </div>

                  <h3 className="text-lg font-semibold mb-2">{module.title}</h3>
                  <p className="text-muted-foreground text-sm mb-4">{module.description}</p>

                  <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
                    <span>{module.duration}</span>
                    <span>•</span>
                    <span>{module.lessons} lessons</span>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {module.topics.slice(0, 3).map((topic) => (
                      <span key={topic} className="text-xs px-2 py-1 rounded-md bg-muted">
                        {topic}
                      </span>
                    ))}
                    {module.topics.length > 3 && (
                      <span className="text-xs px-2 py-1 rounded-md bg-muted text-muted-foreground">
                        +{module.topics.length - 3} more
                      </span>
                    )}
                  </div>

                  <Link
                    href={`/timing-playground#${module.id}`}
                    className="flex items-center gap-2 text-amber-400 font-medium text-sm group-hover:gap-3 transition-all"
                  >
                    Start Learning <ArrowRight className="w-4 h-4" />
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Interactive Code Block */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-card rounded-2xl border border-border overflow-hidden"
          >
            <div className="p-6 border-b border-border bg-muted/30">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <Play className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold">Quick Example: Clock Signal</h3>
                    <p className="text-sm text-muted-foreground">See how a clock signal works</p>
                  </div>
                </div>
                <Link
                  href="/timing-playground"
                  className="flex items-center gap-2 text-primary text-sm font-medium hover:underline"
                >
                  Try in Playground <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>

            <div className="p-6">
              <div className="code-block">
                <div className="code-header">
                  <div className="code-dot bg-red-500" />
                  <div className="code-dot bg-yellow-500" />
                  <div className="code-dot bg-green-500" />
                  <span className="ml-2 text-muted-foreground text-sm">clock_signal.py</span>
                </div>
                <div className="code-content">
                  <div className="text-muted-foreground text-sm"># A clock signal alternates between 0 and 1</div>
                  <br />
                  <div><span className="text-blue-400">class</span> <span className="text-amber-400">Clock</span>:</div>
                  <div>  <span className="text-blue-400">def</span> <span className="text-green-400">__init__</span>(self, frequency_hz):</div>
                  <div>    self.period = <span className="text-purple-400">1.0</span> / frequency_hz  <span className="text-muted-foreground"># Time for one cycle</span></div>
                  <div>    self.state = <span className="text-purple-400">0</span></div>
                  <br />
                  <div>  <span className="text-blue-400">def</span> <span className="text-green-400">tick</span>(self, elapsed_time):</div>
                  <div>    <span className="text-muted-foreground"># Toggle state every half period</span></div>
                  <div>    <span className="text-blue-400">if</span> (elapsed_time % self.period) &gt;= (self.period / <span className="text-purple-400">2</span>):</div>
                  <div>      self.state = <span className="text-purple-400">1</span>  <span className="text-muted-foreground"># High</span></div>
                  <div>    <span className="text-blue-400">else</span>:</div>
                  <div>      self.state = <span className="text-purple-400">0</span>  <span className="text-muted-foreground"># Low</span></div>
                </div>
              </div>

              {/* Visual Clock Display */}
              <div className="mt-6 p-4 bg-muted/30 rounded-xl">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-sm text-muted-foreground">Clock Visualization</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary">1 Hz</span>
                </div>
                <div className="flex items-end gap-1 h-16">
                  {Array.from({ length: 20 }).map((_, i) => (
                    <motion.div
                      key={i}
                      className="flex-1 bg-primary"
                      initial={{ height: i % 2 === 0 ? "100%" : "20%" }}
                      animate={{ 
                        height: [
                          i % 2 === 0 ? "100%" : "20%",
                          i % 2 === 0 ? "20%" : "100%",
                          i % 2 === 0 ? "100%" : "20%"
                        ]
                      }}
                      transition={{
                        duration: 1,
                        repeat: Infinity,
                        ease: "steps(1)",
                        delay: i * 0.05
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Progress Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="bg-card rounded-2xl border border-border p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-green-400/10 flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                </div>
                <span className="font-semibold">Track Your Progress</span>
              </div>
              <p className="text-muted-foreground text-sm">
                Complete lessons and track your understanding with quizzes and interactive challenges.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="bg-card rounded-2xl border border-border p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-blue-400/10 flex items-center justify-center">
                  <CircuitBoard className="w-5 h-5 text-blue-400" />
                </div>
                <span className="font-semibold">Hands-On Labs</span>
              </div>
              <p className="text-muted-foreground text-sm">
                Apply what you learn in interactive simulations and real-world design challenges.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="bg-card rounded-2xl border border-border p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-amber-400/10 flex items-center justify-center">
                  <Target className="w-5 h-5 text-amber-400" />
                </div>
                <span className="font-semibold">Earn Achievements</span>
              </div>
              <p className="text-muted-foreground text-sm">
                Complete challenges and earn badges as you master timing and sequencing concepts.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl font-bold mb-4">Ready to Dive Deeper?</h2>
            <p className="text-muted-foreground mb-8">
              Put your knowledge into practice with interactive timing simulations
            </p>
            <Link
              href="/timing-playground"
              className="btn-primary inline-flex items-center gap-2 px-8 py-4 text-lg"
            >
              <Play className="w-5 h-5" />
              Open Timing Playground
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
