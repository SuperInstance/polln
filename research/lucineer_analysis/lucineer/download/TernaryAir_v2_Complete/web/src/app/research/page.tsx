"use client";

import Link from "next/link";
import {
  BookOpen, FileText, Cpu, Clock, Zap, Users, Globe,
  Download, ExternalLink, ChevronRight, Calendar, Tag,
  Search, Filter, ArrowRight
} from "lucide-react";

const researchDocuments = [
  {
    id: "kimi-swarm-v13",
    type: "Technical Report",
    title: "Kimi Swarm Research Report v13",
    excerpt: "Comprehensive multi-agent research validating BitNet b1.58-2B-4T on HuggingFace with 16,010 monthly downloads. Confirms Taalas $169M funding and identifies iFairy from Peking University as breakthrough 2-bit complex-valued LLM.",
    date: "March 2026",
    pages: 47,
    tags: ["BitNet", "FPGA", "Edge AI", "Taalas", "iFairy"],
    category: "technical",
    featured: true,
  },
  {
    id: "timing-education-framework",
    type: "Education Framework",
    title: "Timing & Sequencing Education Framework",
    excerpt: "Complete pedagogical approach teaching timing concepts from playground games to professional chip design. Includes age-group specific content, cultural variations, and professional-to-playground concept bridges.",
    date: "March 2026",
    pages: 85,
    tags: ["Education", "Pedagogy", "Timing", "Age Groups"],
    category: "education",
    featured: true,
  },
  {
    id: "design-system-v2",
    type: "Design Document",
    title: "TernaryAir Design System v2.0",
    excerpt: "Comprehensive style guide covering brand philosophy, color systems, typography, components, animations, accessibility guidelines, and age-specific design patterns for the educational platform.",
    date: "March 2026",
    pages: 52,
    tags: ["Design", "UI/UX", "Components", "Accessibility"],
    category: "design",
    featured: false,
  },
  {
    id: "mask-locked-chip-deep-dive",
    type: "Technical Deep Dive",
    title: "Mask-Locked Inference Chip Architecture",
    excerpt: "Detailed analysis of mask-locked chip design principles, ROM-based weight storage, security implications, and manufacturing considerations for edge AI inference devices.",
    date: "March 2026",
    pages: 34,
    tags: ["Chip Design", "Security", "Edge AI", "Manufacturing"],
    category: "technical",
    featured: false,
  },
  {
    id: "fpga-timing-closure",
    type: "Technical Guide",
    title: "FPGA Timing Closure Techniques",
    excerpt: "Practical guide to achieving timing closure in FPGA designs. Covers static timing analysis, pipeline optimization, CDC handling, and common timing violation solutions.",
    date: "March 2026",
    pages: 28,
    tags: ["FPGA", "Timing", "CDC", "Pipeline"],
    category: "technical",
    featured: false,
  },
  {
    id: "ternary-logic-primer",
    type: "Educational",
    title: "Ternary Logic: A Visual Introduction",
    excerpt: "Accessible introduction to ternary logic systems (-1, 0, +1) with visual demonstrations. Explains why ternary computing is more efficient for neural network inference.",
    date: "March 2026",
    pages: 22,
    tags: ["Ternary", "Logic", "Neural Networks", "Education"],
    category: "education",
    featured: false,
  },
  {
    id: "competitive-analysis-2026",
    type: "Market Research",
    title: "Edge AI Chip Competitive Landscape 2026",
    excerpt: "Analysis of Taalas ($219M raised), Quadric ($72M), Axelera ($250M+), Hailo, and emerging players. Identifies 12-18 month window before edge competition intensifies.",
    date: "March 2026",
    pages: 45,
    tags: ["Market", "Competition", "Edge AI", "Investment"],
    category: "market",
    featured: true,
  },
  {
    id: "api-integration-guide",
    type: "Developer Guide",
    title: "Multi-Provider AI API Integration",
    excerpt: "Complete guide to connecting Groq, OpenAI, x.ai, DeepSeek, Kimi, and local Ollama instances. Includes code examples, error handling, and offline-first architecture patterns.",
    date: "March 2026",
    pages: 38,
    tags: ["API", "Integration", "Groq", "Ollama"],
    category: "developer",
    featured: false,
  },
];

const categories = [
  { id: "all", name: "All Documents", icon: BookOpen },
  { id: "technical", name: "Technical", icon: Cpu },
  { id: "education", name: "Education", icon: Users },
  { id: "design", name: "Design", icon: Zap },
  { id: "market", name: "Market Research", icon: Globe },
  { id: "developer", name: "Developer", icon: Clock },
];

export default function ResearchPage() {
  return (
    <div className="animated-bg min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/30 rounded-full px-5 py-2 mb-6">
            <BookOpen className="w-4 h-4 text-blue-400" />
            <span className="text-blue-400 text-sm font-medium">Knowledge Base</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">Research Hub</span>
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto text-lg">
            Deep dive into the technology, pedagogy, and market research behind TernaryAir.
            All documents available for download.
          </p>
        </div>

        {/* Featured Documents */}
        <section className="mb-12">
          <h2 className="text-xl font-bold mb-6">Featured Research</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {researchDocuments.filter(d => d.featured).map((doc) => (
              <Link
                key={doc.id}
                href={`/research/${doc.id}`}
                className="group bg-dark-800/60 backdrop-blur-sm rounded-2xl border border-dark-600 p-6 hover:border-green-500/30 transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <span className="text-xs font-medium text-green-400 bg-green-500/10 px-3 py-1 rounded-full">
                    {doc.type}
                  </span>
                  <span className="text-xs text-gray-500">{doc.pages} pages</span>
                </div>
                
                <h3 className="text-lg font-semibold mb-2 group-hover:text-green-400 transition-colors">
                  {doc.title}
                </h3>
                
                <p className="text-sm text-gray-400 mb-4 leading-relaxed line-clamp-3">
                  {doc.excerpt}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-2">
                    {doc.tags.slice(0, 3).map((tag) => (
                      <span key={tag} className="text-xs text-gray-500 bg-dark-700 px-2 py-1 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-green-400 transition-colors" />
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Category Filter */}
        <section className="mb-8">
          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => (
              <button
                key={cat.id}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  cat.id === "all"
                    ? "bg-green-500/10 text-green-400 border border-green-500/30"
                    : "bg-dark-700/50 text-gray-400 hover:text-white hover:bg-dark-600"
                }`}
              >
                <cat.icon className="w-4 h-4" />
                {cat.name}
              </button>
            ))}
          </div>
        </section>

        {/* All Documents */}
        <section>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {researchDocuments.map((doc) => (
              <article
                key={doc.id}
                className="bg-dark-800/60 rounded-xl border border-dark-600 p-5 hover:border-green-500/30 transition-all"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-medium text-blue-400">{doc.type}</span>
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <Calendar className="w-3 h-3" />
                    {doc.date}
                  </div>
                </div>
                
                <h3 className="font-semibold mb-2 text-sm">{doc.title}</h3>
                <p className="text-xs text-gray-500 mb-3 line-clamp-2">{doc.excerpt}</p>
                
                <div className="flex items-center justify-between">
                  <div className="flex flex-wrap gap-1">
                    {doc.tags.slice(0, 2).map((tag) => (
                      <span key={tag} className="text-[10px] text-gray-500 bg-dark-700 px-1.5 py-0.5 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center gap-2">
                    <button className="p-1.5 text-gray-400 hover:text-green-400 transition-colors">
                      <Download className="w-4 h-4" />
                    </button>
                    <button className="p-1.5 text-gray-400 hover:text-white transition-colors">
                      <ExternalLink className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>

        {/* For Different Audiences */}
        <section className="mt-16">
          <h2 className="text-xl font-bold mb-6">Resources By Audience</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-6">
              <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="font-semibold mb-2">For Teachers</h3>
              <p className="text-sm text-gray-400 mb-4">
                Classroom guides, lesson plans, and curriculum integration resources for all age groups.
              </p>
              <ul className="space-y-2">
                <li>
                  <Link href="#" className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-2">
                    <ChevronRight className="w-4 h-4" /> Lesson Plan Templates
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-2">
                    <ChevronRight className="w-4 h-4" /> Assessment Rubrics
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-2">
                    <ChevronRight className="w-4 h-4" /> Offline Classroom Guide
                  </Link>
                </li>
              </ul>
            </div>
            
            <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-6">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-4">
                <Cpu className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="font-semibold mb-2">For Chip Designers</h3>
              <p className="text-sm text-gray-400 mb-4">
                Technical deep dives, architecture specifications, and FPGA implementation guides.
              </p>
              <ul className="space-y-2">
                <li>
                  <Link href="#" className="text-sm text-purple-400 hover:text-purple-300 flex items-center gap-2">
                    <ChevronRight className="w-4 h-4" /> RTL Architecture
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-sm text-purple-400 hover:text-purple-300 flex items-center gap-2">
                    <ChevronRight className="w-4 h-4" /> Timing Constraints
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-sm text-purple-400 hover:text-purple-300 flex items-center gap-2">
                    <ChevronRight className="w-4 h-4" /> FPGA Prototyping Guide
                  </Link>
                </li>
              </ul>
            </div>
            
            <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-6">
              <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center mb-4">
                <Globe className="w-6 h-6 text-green-400" />
              </div>
              <h3 className="font-semibold mb-2">For Contributors</h3>
              <p className="text-sm text-gray-400 mb-4">
                Contribution guidelines, design system docs, and development setup instructions.
              </p>
              <ul className="space-y-2">
                <li>
                  <Link href="#" className="text-sm text-green-400 hover:text-green-300 flex items-center gap-2">
                    <ChevronRight className="w-4 h-4" /> Contributing Guide
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-sm text-green-400 hover:text-green-300 flex items-center gap-2">
                    <ChevronRight className="w-4 h-4" /> Design System
                  </Link>
                </li>
                <li>
                  <Link href="#" className="text-sm text-green-400 hover:text-green-300 flex items-center gap-2">
                    <ChevronRight className="w-4 h-4" /> Development Setup
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Navigation */}
        <div className="flex justify-center gap-4 mt-12">
          <Link
            href="/downloads"
            className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-6 py-3 rounded-xl font-medium transition-colors"
          >
            ← Download Center
          </Link>
          <Link
            href="/community"
            className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-6 py-3 rounded-xl font-medium transition-all"
          >
            Community <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
