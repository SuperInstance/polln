"use client";

import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import {
  Cpu,
  Zap,
  Layers,
  Shield,
  Music,
  Sparkles,
  ArrowRight,
  Play,
  Gauge,
  Thermometer,
  Clock,
  Database,
  Code,
  Palette,
  Brain,
  Volume2,
  Puzzle,
  Gamepad2,
  GraduationCap,
  Lightbulb,
  Heart,
  Users,
  Rocket,
  BookOpen,
  Wand2,
  Baby,
  School,
  Briefcase,
  Building2,
  User,
  ShieldCheck,
} from "lucide-react";

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

// Education features - with parent-facing descriptions and learning outcomes
const educationFeatures = [
  {
    icon: Gamepad2,
    title: "MIST Game",
    tagline: "Learn AI Through Play",
    description: "A fun adventure where kids explore how machines learn — as a sheepdog puppy discovering the world",
    parentNote: "Ages 5-10 • No coding required • 15-min sessions",
    learningOutcomes: ["Pattern recognition", "Cause & effect thinking", "How AI learns from examples"],
    href: "/mist",
    color: "text-primary",
    bgColor: "bg-primary/10",
    borderColor: "border-primary/30",
  },
  {
    icon: Music,
    title: "Music Playground",
    tagline: "See AI Create",
    description: "Interactive MIDI playground showing how AI learns musical styles and patterns",
    parentNote: "All ages • Creative exploration • No signup needed",
    href: "/music",
    color: "text-cyan-400",
    bgColor: "bg-cyan-400/10",
    borderColor: "border-cyan-400/30",
  },
  {
    icon: Brain,
    title: "Tabula Rosa",
    tagline: "AI Personality Lab",
    description: "Research how blank-slate AI models become specialists — train your own AI personality",
    parentNote: "Advanced • Students & researchers • Open experiments",
    href: "/tabula-rosa",
    color: "text-purple-400",
    bgColor: "bg-purple-400/10",
    borderColor: "border-purple-400/30",
  },
  {
    icon: BookOpen,
    title: "Learning Hub",
    tagline: "Master the Fundamentals",
    description: "Interactive tutorials from timing basics to neural network architecture",
    parentNote: "All levels • Self-paced • Free access",
    href: "/learning",
    color: "text-amber-400",
    bgColor: "bg-amber-400/10",
    borderColor: "border-amber-400/30",
  },
];

// Design/Professional features
const designFeatures = [
  {
    icon: Cpu,
    title: "LUCI-1",
    params: "1B",
    power: "2W",
    speed: "15 tok/s",
    price: "$35",
    description: "Edge IoT & Wearables",
    color: "text-green-400",
    bgColor: "bg-green-400/10",
    borderColor: "border-green-400/30",
  },
  {
    icon: Cpu,
    title: "LUCI-3",
    params: "3B",
    power: "5W",
    speed: "25 tok/s",
    price: "$55",
    description: "Smart Home & Industrial",
    color: "text-blue-400",
    bgColor: "bg-blue-400/10",
    borderColor: "border-blue-400/30",
    featured: true,
  },
  {
    icon: Cpu,
    title: "LUCI-7",
    params: "7B",
    power: "10W",
    speed: "35 tok/s",
    price: "$89",
    description: "On-device AI Assistant",
    color: "text-purple-400",
    bgColor: "bg-purple-400/10",
    borderColor: "border-purple-400/30",
  },
  {
    icon: Wand2,
    title: "CUSTOM",
    params: "∞",
    power: "Custom",
    speed: "Variable",
    price: "Quote",
    description: "Your Architecture",
    color: "text-amber-400",
    bgColor: "bg-amber-400/10",
    borderColor: "border-amber-400/30",
  },
];

// Parallel Journey Paths - Explorer (Education) and Builder (Professional)
const explorerPath = [
  { stage: "Play", desc: "Interactive games teach core AI concepts", icon: Gamepad2, color: "text-primary" },
  { stage: "Experiment", desc: "Hands-on tools reveal how machines learn", icon: Puzzle, color: "text-cyan-400" },
  { stage: "Understand", desc: "Deep dives into neural architecture", icon: Brain, color: "text-purple-400" },
  { stage: "Innovate", desc: "Create your own AI experiments", icon: Sparkles, color: "text-amber-400" },
];

const builderPath = [
  { stage: "Design", desc: "Configure your inference chip architecture", icon: Palette, color: "text-primary" },
  { stage: "Simulate", desc: "Test performance before manufacturing", icon: Gauge, color: "text-blue-400" },
  { stage: "Validate", desc: "Verify weights lock correctly in silicon", icon: Shield, color: "text-purple-400" },
  { stage: "Deploy", desc: "Ship your custom inference hardware", icon: Rocket, color: "text-amber-400" },
];

// Value propositions
const valueProps = [
  {
    icon: Shield,
    title: "Air-Gapped Security",
    value: "100%",
    description: "Weights embedded in silicon metal layers - impossible to extract",
  },
  {
    icon: Zap,
    title: "Power Efficiency",
    value: "116x",
    description: "vs GPU inference - 3W instead of 350W for equivalent inference",
  },
  {
    icon: Clock,
    title: "No Loading",
    value: "0ms",
    description: "Weights are the hardware - no memory transfers ever",
  },
  {
    icon: Database,
    title: "Open Source",
    value: "MIT",
    description: "Based on BitNet b1.58-2B-4T - fully open architecture",
  },
];

// Performance comparison data
const performanceData = [
  { name: "NVIDIA H100", energy: 3500, color: "bg-green-500" },
  { name: "NVIDIA A100", energy: 2800, color: "bg-green-400" },
  { name: "Jetson Orin", energy: 1500, color: "bg-blue-400" },
  { name: "Hailo-10H", energy: 800, color: "bg-blue-300" },
  { name: "LUCI-7", energy: 30, color: "bg-primary", highlight: true },
];

// Testimonials
const testimonials = [
  {
    quote: "My daughter asks to 'play the dog game' every day. She's learning what neural networks are without realizing it.",
    author: "Parent of 7-year-old",
    role: "Early Access Tester",
    type: "parent",
  },
  {
    quote: "Finally, a way to prototype custom inference without waiting for GPU allocations.",
    author: "Senior Hardware Engineer",
    role: "Startup Founder",
    type: "professional",
  },
];

export default function Home() {
  return (
    <div className="animated-gradient-bg min-h-screen">
      {/* HERO SECTION - Balanced Dual Path */}
      <section className="relative hero-gradient pt-16 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <motion.div
            className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl"
            animate={{ x: [0, 50, 0], y: [0, 30, 0] }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div
            className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl"
            animate={{ x: [0, -30, 0], y: [0, -50, 0] }}
            transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
          />
          {/* Central glow - the "coin" center */}
          <motion.div
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-primary/10 via-transparent to-transparent rounded-full"
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
          />
        </div>

        <div className="max-w-7xl mx-auto relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            {/* Unified Badge */}
            <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2 mb-8">
              <Lightbulb className="w-4 h-4 text-primary" />
              <span className="text-primary text-sm font-medium">
                Where AI Becomes Intuitive
              </span>
            </div>

            {/* NEW Headline - Equal Weight */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4 text-shadow">
              <span className="text-foreground">For Explorers </span>
              <span className="text-muted-foreground">and </span>
              <span className="gradient-text">Engineers</span>
            </h1>

            <p className="text-xl text-muted-foreground mb-2 max-w-3xl mx-auto leading-relaxed">
              Games that teach kids how machines learn.
            </p>
            <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
              Tools that help engineers build what comes next.
            </p>
            
            {/* Audience clarity */}
            <div className="flex flex-wrap justify-center gap-3 mb-12">
              <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-full text-sm">
                <Baby className="w-4 h-4 text-primary" />
                <span className="text-primary">Ages 5-10</span>
              </span>
              <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-cyan-400/10 rounded-full text-sm">
                <School className="w-4 h-4 text-cyan-400" />
                <span className="text-cyan-400">Students</span>
              </span>
              <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-purple-400/10 rounded-full text-sm">
                <Briefcase className="w-4 h-4 text-purple-400" />
                <span className="text-purple-400">Engineers</span>
              </span>
              <span className="inline-flex items-center gap-2 px-3 py-1.5 bg-amber-400/10 rounded-full text-sm">
                <Building2 className="w-4 h-4 text-amber-400" />
                <span className="text-amber-400">Enterprise</span>
              </span>
            </div>

            {/* DUAL CTA SECTION - Equal Visual Weight */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-5xl mx-auto mb-12">
              {/* LEARN PATH - Brand Color Emphasis */}
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-primary/10 to-cyan-400/10 rounded-3xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity" />
                <div className="relative bg-card/80 backdrop-blur-sm border-2 border-primary/40 rounded-3xl p-8 h-full hover:border-primary/60 transition-colors">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center">
                      <GraduationCap className="w-7 h-7 text-primary" />
                    </div>
                    <div className="text-left">
                      <h2 className="text-2xl font-bold text-primary">LEARN</h2>
                      <p className="text-sm text-muted-foreground">Discovery Mode</p>
                    </div>
                  </div>
                  
                  <p className="text-foreground mb-4 text-left text-lg">
                    Interactive games where kids teach machines to see, hear, and think.
                  </p>
                  
                  {/* Parent-facing microcopy */}
                  <div className="flex items-center gap-2 mb-6 p-3 bg-primary/5 rounded-xl border border-primary/20">
                    <ShieldCheck className="w-4 h-4 text-primary flex-shrink-0" />
                    <p className="text-sm text-muted-foreground text-left">
                      <span className="text-primary font-medium">For parents:</span> Screen time that builds real STEM skills. No coding required.
                    </p>
                  </div>
                  
                  {/* Parent Promise - Trust Section */}
                  <div className="mb-4 p-3 bg-green-400/5 rounded-xl border border-green-400/20">
                    <div className="flex items-center gap-2 mb-2">
                      <ShieldCheck className="w-4 h-4 text-green-400" />
                      <span className="text-sm font-medium text-green-400">Parent Promise</span>
                    </div>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>✓ No account required to play</li>
                      <li>✓ No ads, no in-app purchases</li>
                      <li>✓ We don&apos;t collect children&apos;s data</li>
                    </ul>
                  </div>
                  
                  <Link
                    href="/mist"
                    className="flex items-center justify-center gap-2 w-full py-4 rounded-xl bg-gradient-to-r from-primary to-cyan-400 text-black font-bold text-lg hover:opacity-90 transition-opacity"
                  >
                    <Gamepad2 className="w-5 h-5" />
                    Start Playing Free
                  </Link>
                </div>
              </motion.div>

              {/* DESIGN PATH - Equal Brand Color Emphasis */}
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="relative group"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 via-purple-400/10 to-blue-400/10 rounded-3xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity" />
                <div className="relative bg-card/80 backdrop-blur-sm border-2 border-primary/40 rounded-3xl p-8 h-full hover:border-primary/60 transition-colors">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary/20 to-purple-400/20 flex items-center justify-center">
                      <Cpu className="w-7 h-7 text-primary" />
                    </div>
                    <div className="text-left">
                      <h2 className="text-2xl font-bold text-primary">DESIGN</h2>
                      <p className="text-sm text-muted-foreground">Creation Mode</p>
                    </div>
                  </div>
                  
                  <p className="text-foreground mb-4 text-left text-lg">
                    Professional chip design studio for building custom inference hardware.
                  </p>
                  
                  {/* Engineer-facing microcopy */}
                  <div className="flex items-center gap-2 mb-4 p-3 bg-primary/5 rounded-xl border border-primary/20">
                    <Zap className="w-4 h-4 text-primary flex-shrink-0" />
                    <p className="text-sm text-muted-foreground text-left">
                      <span className="text-primary font-medium">For engineers:</span> From trained model to mask-locked silicon in 4 steps.
                    </p>
                  </div>
                  
                  {/* Technical Credibility */}
                  <div className="mb-4 p-3 bg-purple-400/5 rounded-xl border border-purple-400/20">
                    <div className="flex items-center gap-2 mb-2">
                      <Database className="w-4 h-4 text-purple-400" />
                      <span className="text-xs font-medium text-purple-400">Technical Specs</span>
                    </div>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>• 28nm process node • Open-source toolchain</li>
                      <li>• BitNet b1.58 ternary weights</li>
                      <li>• FPGA prototype validation available</li>
                    </ul>
                  </div>
                  
                  <Link
                    href="/professional"
                    className="flex items-center justify-center gap-2 w-full py-4 rounded-xl bg-gradient-to-r from-primary to-purple-400 text-black font-bold text-lg hover:opacity-90 transition-opacity"
                  >
                    <Layers className="w-5 h-5" />
                    Start Designing
                  </Link>
                </div>
              </motion.div>
            </div>

            {/* Coin Visual Metaphor - More Prominent */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="flex items-center justify-center gap-4 text-muted-foreground mb-4"
            >
              <div className="relative w-20 h-20">
                {/* Coin visual */}
                <div className="absolute inset-0 rounded-full bg-gradient-to-r from-primary via-purple-400 to-primary animate-spin-slow opacity-30" />
                <div className="absolute inset-1 rounded-full bg-card flex items-center justify-center">
                  <div className="text-center">
                    <Sparkles className="w-5 h-5 text-primary mx-auto" />
                    <span className="text-[10px] font-bold text-primary">ONE</span>
                  </div>
                </div>
              </div>
            </motion.div>
            
            <p className="text-sm text-muted-foreground max-w-md mx-auto">
              The same AI principles that fascinate a 5-year-old are what engineers optimize for in silicon.
            </p>
          </motion.div>
        </div>
      </section>

      {/* PARALLEL JOURNEYS - Two Paths, Equal Weight */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/30">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Two Paths, Same Destination
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Understanding AI — whether through play or engineering
            </p>
          </motion.div>

          {/* Parallel Journey Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* EXPLORER PATH */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <div className="text-center mb-8">
                <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2">
                  <GraduationCap className="w-4 h-4 text-primary" />
                  <span className="text-primary text-sm font-medium">The Explorer Path</span>
                </div>
              </div>
              
              <div className="space-y-4">
                {explorerPath.map((step, index) => (
                  <motion.div
                    key={step.stage}
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-4 p-4 rounded-xl bg-card border border-border hover:border-primary/30 transition-colors"
                  >
                    <div className={`w-10 h-10 rounded-lg ${step.color.replace('text-', 'bg-')}/10 flex items-center justify-center flex-shrink-0`}>
                      <step.icon className={`w-5 h-5 ${step.color}`} />
                    </div>
                    <div>
                      <h3 className="font-semibold">{step.stage}</h3>
                      <p className="text-sm text-muted-foreground">{step.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* BUILDER PATH */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <div className="text-center mb-8">
                <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2">
                  <Cpu className="w-4 h-4 text-primary" />
                  <span className="text-primary text-sm font-medium">The Builder Path</span>
                </div>
              </div>
              
              <div className="space-y-4">
                {builderPath.map((step, index) => (
                  <motion.div
                    key={step.stage}
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-start gap-4 p-4 rounded-xl bg-card border border-border hover:border-primary/30 transition-colors"
                  >
                    <div className={`w-10 h-10 rounded-lg ${step.color.replace('text-', 'bg-')}/10 flex items-center justify-center flex-shrink-0`}>
                      <step.icon className={`w-5 h-5 ${step.color}`} />
                    </div>
                    <div>
                      <h3 className="font-semibold">{step.stage}</h3>
                      <p className="text-sm text-muted-foreground">{step.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* FOR LEARNERS SECTION */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2 mb-6">
              <GraduationCap className="w-4 h-4 text-primary" />
              <span className="text-primary text-sm font-medium">For Learners</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Discover How Machines Think
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Interactive experiences that make AI concepts tangible and fun
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {educationFeatures.map((feature) => (
              <motion.div
                key={feature.title}
                variants={fadeInUp}
              >
                <Link
                  href={feature.href}
                  className={`block group p-6 rounded-2xl bg-card border-2 ${feature.borderColor} card-hover h-full`}
                >
                  <div className={`w-14 h-14 rounded-xl ${feature.bgColor} flex items-center justify-center mb-4`}>
                    <feature.icon className={`w-7 h-7 ${feature.color}`} />
                  </div>
                  <h3 className="text-xl font-semibold mb-1">{feature.title}</h3>
                  <p className="text-sm text-primary font-medium mb-2">{feature.tagline}</p>
                  <p className="text-sm text-muted-foreground mb-4">{feature.description}</p>
                  <div className="mt-auto">
                    <p className="text-xs text-muted-foreground/70 mb-2">{feature.parentNote}</p>
                    {feature.learningOutcomes && (
                      <div className="mb-3">
                        <p className="text-xs font-medium text-green-400 mb-1">What they&apos;ll learn:</p>
                        <ul className="text-xs text-muted-foreground space-y-0.5">
                          {feature.learningOutcomes.map((outcome, i) => (
                            <li key={i}>• {outcome}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-sm font-medium text-primary">
                      <span>Explore</span>
                      <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* TESTIMONIALS - Social Proof */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <h2 className="text-2xl font-bold mb-4">
              Hear From Our Community
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className={`p-6 rounded-2xl bg-card border ${
                  testimonial.type === 'parent' ? 'border-primary/30' : 'border-purple-400/30'
                }`}
              >
                <p className="text-foreground mb-4 italic">&ldquo;{testimonial.quote}&rdquo;</p>
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    testimonial.type === 'parent' ? 'bg-primary/10' : 'bg-purple-400/10'
                  }`}>
                    {testimonial.type === 'parent' ? (
                      <User className="w-5 h-5 text-primary" />
                    ) : (
                      <Briefcase className="w-5 h-5 text-purple-400" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{testimonial.author}</p>
                    <p className="text-xs text-muted-foreground">{testimonial.role}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FOR BUILDERS SECTION */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/30 rounded-full px-4 py-2 mb-6">
              <Cpu className="w-4 h-4 text-primary" />
              <span className="text-primary text-sm font-medium">For Builders</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Design Inference Chips That Ship
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              The LUCI series — from prototype to production
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {designFeatures.map((chip) => (
              <motion.div
                key={chip.name}
                variants={fadeInUp}
                className={`relative group p-6 rounded-2xl bg-card border ${chip.borderColor} card-hover ${
                  chip.featured ? "ring-2 ring-primary" : ""
                }`}
              >
                {chip.featured && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-primary-foreground text-xs font-bold px-3 py-1 rounded-full">
                    POPULAR
                  </div>
                )}
                <div className={`w-16 h-16 rounded-xl ${chip.bgColor} flex items-center justify-center mb-4 mx-auto`}>
                  <chip.icon className={`w-8 h-8 ${chip.color}`} />
                </div>
                <h3 className={`text-2xl font-bold text-center mb-2 ${chip.color}`}>{chip.title}</h3>
                <p className="text-sm text-muted-foreground text-center mb-4">{chip.description}</p>
                
                <div className="space-y-2 mb-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Parameters</span>
                    <span className="font-mono">{chip.params}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Power</span>
                    <span className="font-mono">{chip.power}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Speed</span>
                    <span className="font-mono">{chip.speed}</span>
                  </div>
                </div>

                <div className="text-center">
                  <div className={`text-3xl font-bold mb-4 ${chip.color}`}>{chip.price}</div>
                  <Link
                    href="/professional"
                    className={`block w-full py-2 rounded-lg text-center text-sm font-medium transition-colors ${
                      chip.featured
                        ? "bg-primary text-primary-foreground hover:bg-primary/90"
                        : `${chip.bgColor} ${chip.color} hover:bg-current/20`
                    }`}
                  >
                    Design Now
                  </Link>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* EDUCATIONAL INSIGHT - Connecting Both Worlds */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <div className="inline-flex items-center gap-2 bg-purple-400/10 border border-purple-400/30 rounded-full px-4 py-2 mb-6">
                <Brain className="w-4 h-4 text-purple-400" />
                <span className="text-purple-400 text-sm font-medium">The Connection</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                What Teaching Machines Teaches Us
              </h2>
              <p className="text-lg text-muted-foreground mb-6">
                The fundamentals of AI — pattern recognition, learning from examples, 
                making predictions — are the same whether you&apos;re 7 or 70.
              </p>
              
              <div className="space-y-4 mb-8">
                <div className="p-4 bg-primary/5 rounded-xl border border-primary/20">
                  <h3 className="font-medium text-primary mb-2">For Kids</h3>
                  <p className="text-sm text-muted-foreground">
                    Learn that machines learn from examples — just like they do. 
                    Discover how training data shapes what AI can do.
                  </p>
                </div>
                <div className="p-4 bg-purple-400/5 rounded-xl border border-purple-400/20">
                  <h3 className="font-medium text-purple-400 mb-2">For Engineers</h3>
                  <p className="text-sm text-muted-foreground">
                    Apply that same understanding to optimize inference chips. 
                    The training pipeline becomes the silicon pipeline.
                  </p>
                </div>
              </div>

              <Link
                href="/tabula-rosa"
                className="btn-secondary inline-flex items-center gap-2"
              >
                <Brain className="w-4 h-4" />
                Explore the Research
              </Link>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="bg-card rounded-2xl border border-border overflow-hidden">
                <Image
                  src="/download/assets/tabula_rosa_concept.png"
                  alt="AI Learning Concepts"
                  width={1344}
                  height={768}
                  className="w-full h-auto"
                />
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* WHY MASK-LOCKED - Shared Value */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Why Mask-Locked Inference?
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Neural weights embedded in silicon metal layers — immutable, efficient, secure
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {valueProps.map((prop) => (
              <motion.div
                key={prop.title}
                variants={fadeInUp}
                className="p-6 rounded-2xl bg-card border border-border text-center"
              >
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                  <prop.icon className="w-6 h-6 text-primary" />
                </div>
                <div className="text-4xl font-bold text-primary mb-2">{prop.value}</div>
                <h3 className="text-lg font-semibold mb-2">{prop.title}</h3>
                <p className="text-sm text-muted-foreground">{prop.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ENERGY COMPARISON */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Energy Efficiency Comparison
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Energy consumption per 1M tokens (7B parameter model)
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="bg-card rounded-2xl border border-border p-8"
          >
            <div className="space-y-6">
              {performanceData.map((item, index) => (
                <div key={item.name} className="flex items-center gap-4">
                  <div className={`w-32 text-sm ${item.highlight ? 'font-bold text-primary' : 'text-muted-foreground'}`}>
                    {item.name}
                  </div>
                  <div className="flex-1 h-8 bg-muted rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: `${(item.energy / 3500) * 100}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 1, delay: index * 0.1 }}
                      className={`h-full ${item.color} ${item.highlight ? 'shadow-[0_0_20px_rgba(0,212,170,0.5)]' : ''}`}
                    />
                  </div>
                  <div className={`w-20 text-right text-sm font-mono ${item.highlight ? 'text-primary font-bold' : 'text-muted-foreground'}`}>
                    {item.energy} Wh
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-8 p-4 bg-primary/10 rounded-xl border border-primary/20">
              <p className="text-center text-primary font-medium">
                LUCI-7 uses 116x less energy than NVIDIA H100 for equivalent inference
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* HOW IT WORKS - Design Flow */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              From Model to Silicon in 4 Steps
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Design inference chips from your trained neural networks
            </p>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-4 gap-6"
          >
            {[
              { step: "1", title: "Train", icon: Brain, desc: "Train your model with PyTorch, TensorFlow, or ONNX" },
              { step: "2", title: "Export", icon: Code, desc: "Export to ternary weights (-1, 0, +1)" },
              { step: "3", title: "Design", icon: Palette, desc: "Lucineer converts to mask layout (GDSII)" },
              { step: "4", title: "Ship", icon: Layers, desc: "Receive your custom inference chip" },
            ].map((item, index) => (
              <motion.div
                key={item.step}
                variants={fadeInUp}
                className="relative"
              >
                <div className="p-6 rounded-2xl bg-card border border-border text-center h-full">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4 border-2 border-primary">
                    <span className="text-2xl font-bold text-primary">{item.step}</span>
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-muted-foreground">{item.desc}</p>
                </div>
                {index < 3 && (
                  <ArrowRight className="hidden md:block absolute top-1/2 -right-3 w-6 h-6 text-muted-foreground" />
                )}
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* DUAL SHOWCASE - Both Paths Visual */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-card/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Learning Showcase */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative group"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-cyan-400/20 rounded-2xl blur-xl opacity-30 group-hover:opacity-50 transition-opacity" />
              <div className="relative bg-card rounded-2xl border-2 border-primary/40 overflow-hidden">
                <Image
                  src="/download/assets/voxel_puppy_hero.png"
                  alt="MIST Game - Learning AI Concepts"
                  width={1344}
                  height={768}
                  className="w-full h-auto"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-transparent to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Gamepad2 className="w-5 h-5 text-primary" />
                    <span className="text-primary font-semibold">MIST: A Sheepdog&apos;s Journey</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    A voxel adventure where kids discover how machines learn — through play
                  </p>
                </div>
              </div>
            </motion.div>

            {/* Design Showcase */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative group"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-purple-400/20 rounded-2xl blur-xl opacity-30 group-hover:opacity-50 transition-opacity" />
              <div className="relative bg-card rounded-2xl border-2 border-primary/40 overflow-hidden">
                <Image
                  src="/download/assets/inference_chip_hero.png"
                  alt="Lucineer Inference Chip"
                  width={1344}
                  height={768}
                  className="w-full h-auto"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-background/90 via-transparent to-transparent" />
                <div className="absolute bottom-0 left-0 right-0 p-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Cpu className="w-5 h-5 text-primary" />
                    <span className="text-primary font-semibold">LUCI Chip Series</span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Mask-locked inference chips designed from your trained neural networks
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* FINAL CTA - Dual Path */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-purple-400/5" />
        <div className="max-w-5xl mx-auto text-center relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Ready to Start Your Journey?
            </h2>
            <p className="text-lg text-muted-foreground mb-10 max-w-2xl mx-auto">
              Whether you&apos;re here to play, learn, or build — welcome to Lucineer.
            </p>

            <div className="flex flex-wrap justify-center gap-4">
              <Link
                href="/mist"
                className="btn-primary flex items-center gap-2 px-8 py-4 text-lg"
              >
                <Gamepad2 className="w-5 h-5" />
                Start Playing Free
              </Link>
              <Link
                href="/professional"
                className="btn-secondary flex items-center gap-2 px-8 py-4 text-lg"
              >
                <Cpu className="w-5 h-5" />
                Start Designing
              </Link>
            </div>

            <p className="text-sm text-muted-foreground mt-8">
              Expected ship date: Q4 2026 • LUCI-1 starting at $35
            </p>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
