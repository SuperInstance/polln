"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ChevronDown,
  Download,
  Shield,
  Cpu,
  Code,
  Users,
  BookOpen,
  Menu,
  X,
  Zap,
} from "lucide-react";

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

  const navItems = [
    {
      label: "Users",
      href: "/users",
      color: "user",
      icon: Users,
      description: "Non-technical guide to TernaryAir",
      subItems: [
        { label: "What is TernaryAir?", href: "/users#what-is" },
        { label: "Why It Matters", href: "/users#why-matters" },
        { label: "Use Cases", href: "/users#use-cases" },
        { label: "Getting Started", href: "/users#getting-started" },
      ],
    },
    {
      label: "Developers",
      href: "/developers",
      color: "developer",
      icon: Code,
      description: "SDK, API, and code examples",
      subItems: [
        { label: "Quick Start", href: "/developers#quick-start" },
        { label: "Python SDK", href: "/developers#sdk" },
        { label: "REST API", href: "/developers#api" },
        { label: "Examples", href: "/developers#examples" },
      ],
    },
    {
      label: "Engineers",
      href: "/engineers",
      color: "engineer",
      icon: Cpu,
      description: "RTL, FPGA, and silicon design",
      subItems: [
        { label: "Architecture", href: "/engineers#architecture" },
        { label: "RTL Source", href: "/engineers#rtl" },
        { label: "FPGA Prototyping", href: "/engineers#fpga" },
        { label: "Silicon Design", href: "/engineers#silicon" },
      ],
    },
  ];

  const getColorClasses = (color: string) => {
    switch (color) {
      case "user":
        return "text-blue-400 hover:text-blue-300";
      case "developer":
        return "text-purple-400 hover:text-purple-300";
      case "engineer":
        return "text-amber-400 hover:text-amber-300";
      default:
        return "text-green-400 hover:text-green-300";
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#050505]/95 backdrop-blur-lg border-b border-green-500/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center shadow-lg shadow-green-500/20">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-lg gradient-text">TernaryAir</span>
              <span className="text-[10px] text-green-500/60 -mt-1">by SuperInstance.AI</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <div
                key={item.label}
                className="relative"
                onMouseEnter={() => setActiveDropdown(item.label)}
                onMouseLeave={() => setActiveDropdown(null)}
              >
                <Link
                  href={item.href}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-lg transition-all ${getColorClasses(
                    item.color
                  )}`}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                  <ChevronDown className="w-3 h-3" />
                </Link>

                {/* Dropdown */}
                {activeDropdown === item.label && (
                  <div className="absolute top-full left-0 mt-1 w-56 bg-[#0a0a0a] rounded-xl shadow-2xl border border-green-500/20 overflow-hidden animate-slide-down">
                    <div className="p-3 border-b border-green-500/10">
                      <p className="text-xs text-gray-400">
                        {item.description}
                      </p>
                    </div>
                    <div className="py-1">
                      {item.subItems.map((subItem) => (
                        <Link
                          key={subItem.label}
                          href={subItem.href}
                          className="block px-4 py-2 text-sm text-gray-300 hover:bg-green-500/10 hover:text-white transition-colors"
                        >
                          {subItem.label}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            <div className="w-px h-6 bg-green-500/20 mx-2" />

            <Link
              href="/security"
              className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-300 hover:text-green-400 transition-colors"
            >
              <Shield className="w-4 h-4" />
              Security
            </Link>

            <Link
              href="/architecture"
              className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-300 hover:text-green-400 transition-colors"
            >
              <BookOpen className="w-4 h-4" />
              Architecture
            </Link>

            <Link
              href="/learning"
              className="flex items-center gap-1.5 px-3 py-2 text-sm text-gray-300 hover:text-green-400 transition-colors"
            >
              <Zap className="w-4 h-4" />
              Learning
            </Link>
          </div>

          {/* CTA Button */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white px-5 py-2.5 rounded-lg font-medium transition-all shadow-lg shadow-green-500/20 hover:shadow-green-500/30"
            >
              <Download className="w-4 h-4" />
              Download
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-gray-400 hover:text-green-400"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-[#0a0a0a] border-t border-green-500/20">
          <div className="px-4 py-4 space-y-2">
            {navItems.map((item) => (
              <div key={item.label}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-2 px-4 py-3 rounded-lg ${getColorClasses(
                    item.color
                  )} bg-green-500/5`}
                  onClick={() => setIsOpen(false)}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
                <div className="ml-8 mt-1 space-y-1">
                  {item.subItems.map((subItem) => (
                    <Link
                      key={subItem.label}
                      href={subItem.href}
                      className="block px-4 py-2 text-sm text-gray-400 hover:text-white"
                      onClick={() => setIsOpen(false)}
                    >
                      {subItem.label}
                    </Link>
                  ))}
                </div>
              </div>
            ))}

            <div className="border-t border-green-500/10 pt-4 mt-4 space-y-2">
              <Link
                href="/security"
                className="flex items-center gap-2 px-4 py-3 text-gray-300 hover:text-green-400"
                onClick={() => setIsOpen(false)}
              >
                <Shield className="w-5 h-5" />
                Security Model
              </Link>

              <Link
                href="/architecture"
                className="flex items-center gap-2 px-4 py-3 text-gray-300 hover:text-green-400"
                onClick={() => setIsOpen(false)}
              >
                <BookOpen className="w-5 h-5" />
                Architecture
              </Link>

              <Link
                href="/origin-story"
                className="flex items-center gap-2 px-4 py-3 text-gray-300 hover:text-green-400"
                onClick={() => setIsOpen(false)}
              >
                <BookOpen className="w-5 h-5" />
                Origin Story
              </Link>

              <Link
                href="/learning"
                className="flex items-center gap-2 px-4 py-3 text-gray-300 hover:text-green-400"
                onClick={() => setIsOpen(false)}
              >
                <Zap className="w-5 h-5" />
                Learning Center
              </Link>
            </div>

            <Link
              href="/download"
              className="flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-green-500 text-white px-4 py-3 rounded-lg font-medium mt-4 shadow-lg shadow-green-500/20"
              onClick={() => setIsOpen(false)}
            >
              <Download className="w-5 h-5" />
              Download Now
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
