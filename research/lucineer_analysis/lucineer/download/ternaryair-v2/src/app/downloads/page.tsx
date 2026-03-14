"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Download, Package, FileText, Code, HardDrive, Globe, 
  Check, ExternalLink, ChevronRight, Archive, Monitor,
  Smartphone, Server, BookOpen, Clock, Zap
} from "lucide-react";

const downloadCategories = [
  {
    id: "complete",
    title: "Complete Package",
    description: "Everything in one download",
    icon: Package,
    color: "green",
    items: [
      { name: "TernaryAir Complete", size: "45 MB", format: "ZIP", version: "v2.0.0" },
    ]
  },
  {
    id: "simulators",
    title: "Simulators",
    description: "Interactive timing tools",
    icon: Clock,
    color: "blue",
    items: [
      { name: "Traffic Light FSM", size: "2.4 MB", format: "HTML", version: "v1.2.0" },
      { name: "Domino Chain Simulator", size: "1.8 MB", format: "HTML", version: "v1.1.0" },
      { name: "Setup/Hold Visualizer", size: "1.2 MB", format: "HTML", version: "v1.0.0" },
      { name: "Pipeline Optimizer", size: "3.5 MB", format: "HTML", version: "v1.0.0" },
      { name: "CDC Analyzer", size: "2.1 MB", format: "HTML", version: "v1.0.0" },
    ]
  },
  {
    id: "learning",
    title: "Learning Modules",
    description: "Age-specific lessons",
    icon: BookOpen,
    color: "purple",
    items: [
      { name: "Young Learners Pack (4-10)", size: "12 MB", format: "HTML", version: "v2.0" },
      { name: "Middle School Pack (11-14)", size: "15 MB", format: "HTML", version: "v2.0" },
      { name: "High School Pack (15-18)", size: "18 MB", format: "HTML", version: "v2.0" },
      { name: "Professional Pack (18+)", size: "22 MB", format: "HTML", version: "v2.0" },
    ]
  },
  {
    id: "docs",
    title: "Documentation",
    description: "Guides and research",
    icon: FileText,
    color: "amber",
    items: [
      { name: "Design System", size: "1.2 MB", format: "PDF", version: "v2.0" },
      { name: "Timing Education Framework", size: "2.8 MB", format: "PDF", version: "v1.0" },
      { name: "API Integration Guide", size: "0.8 MB", format: "PDF", version: "v1.0" },
      { name: "Research Compendium", size: "8.5 MB", format: "PDF", version: "v1.0" },
    ]
  },
  {
    id: "source",
    title: "Source Code",
    description: "Full repository",
    icon: Code,
    color: "cyan",
    items: [
      { name: "Full Source (GitHub)", size: "~30 MB", format: "Git", version: "latest" },
      { name: "Source Archive", size: "28 MB", format: "ZIP", version: "v2.0.0" },
    ]
  },
  {
    id: "offline",
    title: "Offline Pack",
    description: "Minimal for offline use",
    icon: HardDrive,
    color: "red",
    items: [
      { name: "Core Simulators Only", size: "8 MB", format: "ZIP", version: "v2.0" },
      { name: "PWA Package", size: "10 MB", format: "ZIP", version: "v2.0" },
    ]
  },
];

export default function DownloadsPage() {
  const [downloading, setDownloading] = useState<string | null>(null);

  const handleDownload = (itemName: string) => {
    setDownloading(itemName);
    // Simulate download
    setTimeout(() => setDownloading(null), 2000);
  };

  return (
    <div className="animated-bg min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 mb-6">
            <HardDrive className="w-4 h-4 text-green-400" />
            <span className="text-green-400 text-sm font-medium">Offline First</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">Download Center</span>
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto text-lg">
            Take everything offline. Learn anywhere, anytime. No internet required after download.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <div className="bg-dark-800/60 rounded-xl p-5 border border-dark-600 text-center">
            <div className="text-3xl font-bold text-green-400 mb-1">45 MB</div>
            <div className="text-sm text-gray-500">Complete Package</div>
          </div>
          <div className="bg-dark-800/60 rounded-xl p-5 border border-dark-600 text-center">
            <div className="text-3xl font-bold text-blue-400 mb-1">100%</div>
            <div className="text-sm text-gray-500">Works Offline</div>
          </div>
          <div className="bg-dark-800/60 rounded-xl p-5 border border-dark-600 text-center">
            <div className="text-3xl font-bold text-purple-400 mb-1">MIT</div>
            <div className="text-sm text-gray-500">Open License</div>
          </div>
          <div className="bg-dark-800/60 rounded-xl p-5 border border-dark-600 text-center">
            <div className="text-3xl font-bold text-amber-400 mb-1">v2.0</div>
            <div className="text-sm text-gray-500">Latest Version</div>
          </div>
        </div>

        {/* Download Categories */}
        <div className="space-y-12">
          {downloadCategories.map((category) => (
            <section key={category.id} id={category.id}>
              <div className="flex items-center gap-3 mb-6">
                <div className={`w-10 h-10 rounded-lg bg-${category.color}-500/10 flex items-center justify-center`}>
                  <category.icon className={`w-5 h-5 text-${category.color}-400`} />
                </div>
                <div>
                  <h2 className="text-xl font-bold">{category.title}</h2>
                  <p className="text-gray-500 text-sm">{category.description}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {category.items.map((item) => (
                  <div
                    key={item.name}
                    className="bg-dark-800/60 rounded-xl border border-dark-600 p-5 hover:border-green-500/30 transition-all"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-semibold text-white">{item.name}</h3>
                        <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                          <span>{item.size}</span>
                          <span>•</span>
                          <span>{item.format}</span>
                          <span>•</span>
                          <span>{item.version}</span>
                        </div>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => handleDownload(item.name)}
                      disabled={downloading === item.name}
                      className={`w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                        downloading === item.name
                          ? "bg-green-500/20 text-green-400"
                          : "bg-green-500/10 text-green-400 hover:bg-green-500/20"
                      }`}
                    >
                      {downloading === item.name ? (
                        <>
                          <div className="w-4 h-4 border-2 border-green-400 border-t-transparent rounded-full animate-spin" />
                          Downloading...
                        </>
                      ) : (
                        <>
                          <Download className="w-4 h-4" />
                          Download
                        </>
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>

        {/* Platform Specific */}
        <section className="mt-16">
          <h2 className="text-xl font-bold mb-6">Platform-Specific Packages</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-5">
              <Monitor className="w-8 h-8 text-blue-400 mb-4" />
              <h3 className="font-semibold mb-2">Desktop App</h3>
              <p className="text-sm text-gray-500 mb-4">Windows, macOS, Linux</p>
              <div className="space-y-2">
                <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600">
                  <Download className="w-4 h-4" /> Windows (.exe)
                </button>
                <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600">
                  <Download className="w-4 h-4" /> macOS (.dmg)
                </button>
                <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600">
                  <Download className="w-4 h-4" /> Linux (.AppImage)
                </button>
              </div>
            </div>
            
            <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-5">
              <Smartphone className="w-8 h-8 text-purple-400 mb-4" />
              <h3 className="font-semibold mb-2">Mobile App</h3>
              <p className="text-sm text-gray-500 mb-4">iOS and Android PWA</p>
              <div className="space-y-2">
                <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600">
                  <Download className="w-4 h-4" /> iOS (PWA)
                </button>
                <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600">
                  <Download className="w-4 h-4" /> Android (APK)
                </button>
              </div>
            </div>
            
            <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-5">
              <Server className="w-8 h-8 text-amber-400 mb-4" />
              <h3 className="font-semibold mb-2">Self-Host</h3>
              <p className="text-sm text-gray-500 mb-4">Docker and bare metal</p>
              <div className="space-y-2">
                <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600">
                  <Download className="w-4 h-4" /> Docker Image
                </button>
                <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600">
                  <Download className="w-4 h-4" /> Docker Compose
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Usage Note */}
        <div className="mt-12 bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
          <h3 className="font-semibold text-blue-400 mb-3">Offline Usage</h3>
          <p className="text-gray-400 text-sm leading-relaxed mb-4">
            All downloads work completely offline after the initial download. 
            Your progress is saved locally in your browser using IndexedDB. 
            For cross-device sync, optionally connect to Cloudflare.
          </p>
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Check className="w-4 h-4 text-green-400" />
              <span>No account required</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Check className="w-4 h-4 text-green-400" />
              <span>No tracking</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Check className="w-4 h-4 text-green-400" />
              <span>Fully private</span>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-center gap-4 mt-12">
          <Link
            href="/api-connect"
            className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-6 py-3 rounded-xl font-medium transition-colors"
          >
            ← API Connections
          </Link>
          <Link
            href="/research"
            className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-6 py-3 rounded-xl font-medium transition-all"
          >
            Research Hub <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
