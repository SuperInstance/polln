"use client";

import Link from "next/link";
import { useState } from "react";
import {
  BookOpen, FileText, Download, ExternalLink, ChevronRight,
  Search, Filter, Calendar, Tag, Clock, Users
} from "lucide-react";

const researchDocuments = [
  {
    id: "kimi-swarm-v13",
    title: "Kimi Swarm Research Report v13",
    type: "Technical Report",
    date: "March 2026",
    pages: 47,
    tags: ["FPGA", "BitNet", "Edge AI", "Chip Design"],
    excerpt: "Comprehensive analysis of BitNet, Taalas, iFairy, and FPGA implementations for mask-locked inference chips.",
    category: "chip-design",
  },
  {
    id: "mask-locked-deep-dive",
    title: "Mask-Locked Inference Chip Deep Dive",
    type: "Technical Deep Dive",
    date: "March 2026",
    pages: 32,
    tags: ["Security", "Inference", "Hardware"],
    excerpt: "Exploring mask-locked chip architectures for secure AI inference at the edge.",
    category: "chip-design",
  },
  {
    id: "timing-education-framework",
    title: "Timing Education Framework",
    type: "Educational Research",
    date: "March 2026",
    pages: 28,
    tags: ["Education", "Timing", "Pedagogy"],
    excerpt: "Pedagogical framework for teaching timing concepts across age groups from 4 to adult.",
    category: "education",
  },
  {
    id: "edge-ai-market",
    title: "Edge AI Market Analysis",
    type: "Market Research",
    date: "February 2026",
    pages: 24,
    tags: ["Market", "Edge AI", "Analysis"],
    excerpt: "Current state and future trends in edge AI hardware and software ecosystems.",
    category: "market",
  },
  {
    id: "fpga-timing-closure",
    title: "FPGA Timing Closure Techniques",
    type: "Technical Guide",
    date: "January 2026",
    pages: 18,
    tags: ["FPGA", "Timing", "Optimization"],
    excerpt: "Best practices and advanced techniques for achieving timing closure in FPGA designs.",
    category: "technical",
  },
  {
    id: "ternary-computing",
    title: "Ternary Computing Fundamentals",
    type: "Technical Report",
    date: "January 2026",
    pages: 22,
    tags: ["Ternary", "Computing", "Architecture"],
    excerpt: "Introduction to ternary (base-3) computing and its potential applications in AI.",
    category: "technical",
  },
];

const categories = [
  { id: "all", name: "All Documents" },
  { id: "chip-design", name: "Chip Design" },
  { id: "education", name: "Education" },
  { id: "technical", name: "Technical Guides" },
  { id: "market", name: "Market Research" },
];

export default function ResearchPage() {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredDocuments = researchDocuments.filter((doc) => {
    const matchesCategory = selectedCategory === "all" || doc.category === selectedCategory;
    const matchesSearch = searchQuery === "" ||
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="animated-bg min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold">Research Hub</h1>
              <p className="text-sm text-gray-500">Technical docs, guides, and research</p>
            </div>
          </div>

          <p className="text-xl text-gray-300 max-w-3xl">
            Explore our research on chip design, AI education, and edge computing. 
            All documents are free to download and share.
          </p>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              placeholder="Search documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-dark-800 border border-dark-600 rounded-xl pl-10 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
            />
          </div>
          <div className="flex gap-2 overflow-x-auto pb-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                  selectedCategory === category.id
                    ? "bg-green-500/20 text-green-400 border border-green-500/30"
                    : "bg-dark-700/50 text-gray-400 hover:text-white"
                }`}
              >
                {category.name}
              </button>
            ))}
          </div>
        </div>

        {/* Document Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredDocuments.map((doc) => (
            <article
              key={doc.id}
              className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden hover:border-green-500/30 transition-all"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <span className="text-xs px-2 py-1 rounded-full bg-cyan-500/20 text-cyan-400">
                    {doc.type}
                  </span>
                  <div className="flex items-center gap-1 text-xs text-gray-500">
                    <Calendar className="w-3 h-3" />
                    {doc.date}
                  </div>
                </div>

                <h3 className="text-lg font-semibold mb-2">{doc.title}</h3>
                <p className="text-sm text-gray-400 mb-4">{doc.excerpt}</p>

                <div className="flex flex-wrap gap-2 mb-4">
                  {doc.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-xs px-2 py-0.5 rounded bg-dark-700/50 text-gray-400"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <FileText className="w-3 h-3" />
                      {doc.pages} pages
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {doc.date}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <button className="p-2 rounded-lg bg-dark-700/50 hover:bg-dark-600 transition-colors">
                      <ExternalLink className="w-4 h-4 text-gray-400" />
                    </button>
                    <button className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm transition-colors">
                      <Download className="w-4 h-4" />
                      PDF
                    </button>
                  </div>
                </div>
              </div>
            </article>
          ))}
        </div>

        {/* Empty State */}
        {filteredDocuments.length === 0 && (
          <div className="text-center py-12">
            <Search className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-400 mb-2">No documents found</h3>
            <p className="text-gray-500">Try adjusting your search or filters</p>
          </div>
        )}
      </div>
    </div>
  );
}
