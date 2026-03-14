"use client";

import Link from "next/link";
import {
  Download, FileArchive, FileCode, FileText, Image, Box,
  ChevronRight, HardDrive, Clock, Check, ExternalLink,
  Package, Code, BookOpen, Layers
} from "lucide-react";

const downloadCategories = [
  {
    id: "complete",
    title: "Complete Package",
    icon: Package,
    description: "Everything you need to run Lucineer offline",
    items: [
      {
        name: "Lucineer Complete",
        size: "45 MB",
        version: "3.0.0",
        format: "ZIP",
        includes: ["All simulators", "All lessons", "Documentation", "Source code"],
      },
    ],
  },
  {
    id: "simulators",
    title: "Simulators",
    icon: Code,
    description: "Interactive timing simulations",
    items: [
      {
        name: "Traffic Light Simulator",
        size: "2.4 MB",
        version: "1.2.0",
        format: "HTML",
        includes: ["Standalone", "Works offline"],
      },
      {
        name: "Domino Chain Simulator",
        size: "1.8 MB",
        version: "1.1.0",
        format: "HTML",
        includes: ["Standalone", "Works offline"],
      },
      {
        name: "State Machine Designer",
        size: "3.2 MB",
        version: "2.0.0",
        format: "HTML",
        includes: ["Export Verilog", "Timing diagrams"],
      },
    ],
  },
  {
    id: "learning",
    title: "Learning Modules",
    icon: BookOpen,
    description: "Age-specific lessons and exercises",
    items: [
      {
        name: "Young Learners Pack",
        size: "12 MB",
        version: "1.0.0",
        format: "PDF + HTML",
        includes: ["Ages 4-10", "Parent guide", "Activity sheets"],
      },
      {
        name: "Middle School Pack",
        size: "15 MB",
        version: "1.0.0",
        format: "PDF + HTML",
        includes: ["Ages 11-14", "Projects", "Quizzes"],
      },
      {
        name: "Professional Pack",
        size: "20 MB",
        version: "1.0.0",
        format: "PDF + Code",
        includes: ["FPGA guides", "Timing analysis", "Real projects"],
      },
    ],
  },
  {
    id: "ternaryair",
    title: "TernaryAir",
    icon: Layers,
    description: "Chip design tools and templates",
    items: [
      {
        name: "TernaryAir Studio",
        size: "8 MB",
        version: "1.0.0",
        format: "Web App",
        includes: ["Voxel editor", "Schema generator", "Lucineer AI"],
      },
      {
        name: "Chip Templates",
        size: "2 MB",
        version: "1.0.0",
        format: "Verilog",
        includes: ["MCU core", "Memory array", "I/O blocks"],
      },
    ],
  },
];

export default function DownloadsPage() {
  return (
    <div className="animated-bg min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Download className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold">Download Center</h1>
              <p className="text-sm text-gray-500">Take everything offline</p>
            </div>
          </div>

          <p className="text-xl text-gray-300 max-w-3xl">
            Download the entire platform — simulators, lessons, documentation — and learn anywhere. 
            No internet required after download. Your progress saved locally.
          </p>
        </div>

        {/* Offline Benefits */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
          <div className="bg-dark-800/60 rounded-xl p-4 border border-dark-600">
            <HardDrive className="w-6 h-6 text-green-400 mb-3" />
            <h3 className="font-semibold mb-1">Works Offline</h3>
            <p className="text-sm text-gray-400">No internet needed after download. Learn anywhere, anytime.</p>
          </div>
          <div className="bg-dark-800/60 rounded-xl p-4 border border-dark-600">
            <Clock className="w-6 h-6 text-blue-400 mb-3" />
            <h3 className="font-semibold mb-1">Instant Access</h3>
            <p className="text-sm text-gray-400">Start learning immediately. No signup or installation required.</p>
          </div>
          <div className="bg-dark-800/60 rounded-xl p-4 border border-dark-600">
            <Check className="w-6 h-6 text-purple-400 mb-3" />
            <h3 className="font-semibold mb-1">Free Forever</h3>
            <p className="text-sm text-gray-400">MIT licensed. Use, modify, and share without limits.</p>
          </div>
        </div>

        {/* Download Categories */}
        <div className="space-y-8">
          {downloadCategories.map((category) => (
            <div key={category.id} className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden">
              <div className="p-4 border-b border-dark-600 bg-dark-700/50">
                <div className="flex items-center gap-3">
                  <category.icon className="w-5 h-5 text-green-400" />
                  <div>
                    <h2 className="font-semibold">{category.title}</h2>
                    <p className="text-xs text-gray-500">{category.description}</p>
                  </div>
                </div>
              </div>

              <div className="p-4">
                <div className="space-y-3">
                  {category.items.map((item) => (
                    <div
                      key={item.name}
                      className="flex items-center justify-between p-4 rounded-xl bg-dark-700/30 border border-dark-600 hover:border-green-500/30 transition-all"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <FileArchive className="w-5 h-5 text-gray-400" />
                          <h3 className="font-medium">{item.name}</h3>
                          <span className="text-xs px-2 py-0.5 rounded bg-dark-600 text-gray-400">
                            v{item.version}
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-2 text-xs text-gray-500">
                          <span>{item.size}</span>
                          <span>•</span>
                          <span>{item.format}</span>
                          {item.includes.map((inc) => (
                            <span key={inc} className="text-gray-600">• {inc}</span>
                          ))}
                        </div>
                      </div>
                      <button className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm font-medium transition-colors">
                        <Download className="w-4 h-4" />
                        Download
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Source Code */}
        <div className="mt-8 bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center">
                <Code className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="font-semibold">Source Code</h2>
                <p className="text-sm text-gray-500">Full repository on GitHub</p>
              </div>
            </div>
            <a
              href="https://github.com/lucineer/lucineer"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 hover:text-white text-sm transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
              View on GitHub
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
